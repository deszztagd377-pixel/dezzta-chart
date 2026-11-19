"""Durable SQLite checkpoint and lease for the OHLCV Redis publisher.

This module is deliberately transport-agnostic: Batch 62H-1 persists publisher
ownership and progress, while Redis append/read-back is implemented separately.
The authoritative OHLCV outbox remains the source of truth.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from app.ohlcv_store import SQLiteOhlcvStore

_PUBLISHER_SCHEMA_VERSION = 1
_DEFAULT_BUSY_TIMEOUT_MS = 10_000
_MAX_LEASE_TTL_MS = 300_000


class SQLiteOhlcvPublisherCheckpoint:
    """Fenced, durable publisher cursor stored beside the source outbox.

    A checkpoint can advance only one cursor at a time and only while the
    caller holds the current, unexpired lease epoch. Call
    record_confirmed_append() only after Redis XADD is confirmed or an exact
    deterministic-ID read-back has verified the existing entry.
    """

    def __init__(
        self,
        source_store: SQLiteOhlcvStore,
        *,
        stream_key: str = "dezzta:market-data:ohlcv:v1",
        busy_timeout_ms: int = _DEFAULT_BUSY_TIMEOUT_MS,
    ) -> None:
        if not isinstance(source_store, SQLiteOhlcvStore):
            raise TypeError("source_store must be a SQLiteOhlcvStore.")
        if not isinstance(stream_key, str) or not stream_key.strip() or len(stream_key) > 256:
            raise ValueError("stream_key must be a non-empty string of at most 256 characters.")
        if not isinstance(busy_timeout_ms, int) or isinstance(busy_timeout_ms, bool) or busy_timeout_ms < 1:
            raise ValueError("busy_timeout_ms must be a positive integer.")
        self.source_store = source_store
        self.database_path = str(Path(source_store.database_path).expanduser())
        self.stream_key = stream_key
        self.busy_timeout_ms = busy_timeout_ms
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(
            self.database_path,
            timeout=self.busy_timeout_ms / 1000,
            isolation_level=None,
        )
        db.row_factory = sqlite3.Row
        db.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
        db.execute("PRAGMA foreign_keys = ON")
        return db

    def _initialize(self) -> None:
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                """CREATE TABLE IF NOT EXISTS ohlcv_relay_publisher_checkpoint (
                    source_id TEXT PRIMARY KEY NOT NULL,
                    stream_key TEXT NOT NULL UNIQUE,
                    published_cursor INTEGER NOT NULL CHECK(published_cursor >= 0),
                    last_event_id TEXT,
                    last_stream_id TEXT NOT NULL,
                    lease_owner TEXT,
                    lease_epoch INTEGER NOT NULL CHECK(lease_epoch >= 0),
                    lease_expires_ms INTEGER NOT NULL CHECK(lease_expires_ms >= 0),
                    updated_at_ms INTEGER NOT NULL CHECK(updated_at_ms >= 0),
                    schema_version INTEGER NOT NULL
                )"""
            )
            columns = {
                row["name"]
                for row in db.execute(
                    "PRAGMA table_info(ohlcv_relay_publisher_checkpoint)"
                )
            }
            required = {
                "source_id", "stream_key", "published_cursor", "last_event_id",
                "last_stream_id", "lease_owner", "lease_epoch",
                "lease_expires_ms", "updated_at_ms", "schema_version",
            }
            if columns != required:
                raise RuntimeError(
                    "Publisher checkpoint schema is incompatible; refusing an implicit migration."
                )
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def initialize_from_snapshot(self, snapshot_cursor: int, *, now_ms: int) -> dict[str, Any]:
        """Create the publisher cursor at a successfully installed snapshot watermark."""
        if type(snapshot_cursor) is not int or snapshot_cursor < 0:
            raise ValueError("snapshot_cursor must be a non-negative integer.")
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError("now_ms must be a non-negative integer.")

        source_id = self.source_store.source_id()
        source_window = self.source_store.read_outbox_batch(
            after_cursor=snapshot_cursor, limit=1,
        )
        if snapshot_cursor > int(source_window["high_water"]):
            raise ValueError("Snapshot cursor is ahead of the authoritative outbox.")
        if source_window.get("status") != "ok":
            raise RuntimeError(
                "Snapshot watermark is outside the retained source outbox; install a fresh snapshot."
            )

        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT * FROM ohlcv_relay_publisher_checkpoint WHERE source_id=?",
                (source_id,),
            ).fetchone()
            if existing is not None:
                if (
                    str(existing["stream_key"]) != self.stream_key
                    or int(existing["schema_version"]) != _PUBLISHER_SCHEMA_VERSION
                ):
                    raise RuntimeError("Existing publisher checkpoint has a different stream or schema.")
                db.execute("COMMIT")
                return self._row_dict(existing)
            try:
                db.execute(
                    """INSERT INTO ohlcv_relay_publisher_checkpoint(
                        source_id,stream_key,published_cursor,last_event_id,
                        last_stream_id,lease_owner,lease_epoch,lease_expires_ms,
                        updated_at_ms,schema_version
                    ) VALUES (?,?,?,?,?,NULL,0,0,?,?)""",
                    (
                        source_id, self.stream_key, snapshot_cursor, None,
                        f"{snapshot_cursor}-0", now_ms, _PUBLISHER_SCHEMA_VERSION,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise RuntimeError(
                    "The configured Redis stream is already assigned to another source."
                ) from exc
            row = db.execute(
                "SELECT * FROM ohlcv_relay_publisher_checkpoint WHERE source_id=?",
                (source_id,),
            ).fetchone()
            db.execute("COMMIT")
            return self._row_dict(row)
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    @staticmethod
    def _row_dict(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "source_id": str(row["source_id"]),
            "stream_key": str(row["stream_key"]),
            "published_cursor": int(row["published_cursor"]),
            "last_event_id": None if row["last_event_id"] is None else str(row["last_event_id"]),
            "last_stream_id": str(row["last_stream_id"]),
            "lease_owner": None if row["lease_owner"] is None else str(row["lease_owner"]),
            "lease_epoch": int(row["lease_epoch"]),
            "lease_expires_ms": int(row["lease_expires_ms"]),
            "updated_at_ms": int(row["updated_at_ms"]),
            "schema_version": int(row["schema_version"]),
        }

    def state(self) -> dict[str, Any] | None:
        source_id = self.source_store.source_id()
        db = self._connect()
        try:
            row = db.execute(
                "SELECT * FROM ohlcv_relay_publisher_checkpoint WHERE source_id=?",
                (source_id,),
            ).fetchone()
            if row is None:
                return None
            state = self._row_dict(row)
            if state["schema_version"] != _PUBLISHER_SCHEMA_VERSION:
                raise RuntimeError("Publisher checkpoint schema version is unsupported.")
            if state["stream_key"] != self.stream_key:
                raise RuntimeError("Publisher stream key does not match its durable checkpoint.")
            return state
        finally:
            db.close()

    def acquire_lease(
        self,
        owner: str,
        *,
        now_ms: int,
        ttl_ms: int = 30_000,
    ) -> dict[str, Any] | None:
        """Acquire or renew a source-local lease; epoch fences stale publishers."""
        if not isinstance(owner, str) or not owner.strip() or len(owner) > 128:
            raise ValueError("owner must be a non-empty string of at most 128 characters.")
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError("now_ms must be a non-negative integer.")
        if type(ttl_ms) is not int or not 1 <= ttl_ms <= _MAX_LEASE_TTL_MS:
            raise ValueError(f"ttl_ms must be between 1 and {_MAX_LEASE_TTL_MS}.")
        source_id = self.source_store.source_id()
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT * FROM ohlcv_relay_publisher_checkpoint WHERE source_id=?",
                (source_id,),
            ).fetchone()
            if row is None:
                raise RuntimeError("Initialize the publisher checkpoint from a snapshot first.")
            if int(row["schema_version"]) != _PUBLISHER_SCHEMA_VERSION:
                raise RuntimeError("Publisher checkpoint schema version is unsupported.")
            current_owner = row["lease_owner"]
            current_expiry = int(row["lease_expires_ms"])
            if current_owner is not None and current_expiry > now_ms and str(current_owner) != owner:
                db.execute("ROLLBACK")
                return None

            same_live_owner = current_owner is not None and str(current_owner) == owner and current_expiry > now_ms
            epoch = int(row["lease_epoch"]) if same_live_owner else int(row["lease_epoch"]) + 1
            expires = now_ms + ttl_ms
            db.execute(
                """UPDATE ohlcv_relay_publisher_checkpoint
                SET lease_owner=?,lease_epoch=?,lease_expires_ms=?,updated_at_ms=?
                WHERE source_id=?""",
                (owner, epoch, expires, now_ms, source_id),
            )
            updated = db.execute(
                "SELECT * FROM ohlcv_relay_publisher_checkpoint WHERE source_id=?",
                (source_id,),
            ).fetchone()
            db.execute("COMMIT")
            return self._row_dict(updated)
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def release_lease(self, owner: str, *, epoch: int, now_ms: int) -> bool:
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("owner must be a non-empty string.")
        if type(epoch) is not int or epoch < 1 or type(now_ms) is not int or now_ms < 0:
            raise ValueError("epoch and now_ms must be valid non-negative integers.")
        source_id = self.source_store.source_id()
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            updated = db.execute(
                """UPDATE ohlcv_relay_publisher_checkpoint
                SET lease_owner=NULL,lease_expires_ms=0,updated_at_ms=?
                WHERE source_id=? AND lease_owner=? AND lease_epoch=?""",
                (now_ms, source_id, owner, epoch),
            )
            db.execute("COMMIT")
            return updated.rowcount == 1
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def record_confirmed_append(
        self,
        owner: str,
        *,
        epoch: int,
        expected_cursor: int,
        event: dict[str, Any],
        stream_id: str,
        now_ms: int,
    ) -> dict[str, Any]:
        """Advance exactly one cursor after the caller confirms its Redis entry."""
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("owner must be a non-empty string.")
        if type(epoch) is not int or epoch < 1:
            raise ValueError("epoch must be a positive integer.")
        if type(expected_cursor) is not int or expected_cursor < 0:
            raise ValueError("expected_cursor must be a non-negative integer.")
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError("now_ms must be a non-negative integer.")
        if not isinstance(event, dict):
            raise TypeError("event must be the canonical outbox event object.")
        cursor = event.get("cursor")
        event_id = event.get("eventId")
        if type(cursor) is not int or cursor != expected_cursor + 1:
            raise ValueError("Publisher checkpoint must advance by exactly one contiguous cursor.")
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("event must contain a stable non-empty eventId.")
        expected_stream_id = f"{cursor}-0"
        if stream_id != expected_stream_id:
            raise ValueError("Redis Stream ID must equal the deterministic cursor ID.")

        source_page = self.source_store.read_outbox_batch(
            after_cursor=expected_cursor, limit=1,
        )
        if (
            source_page.get("status") != "ok"
            or not source_page.get("events")
            or source_page["events"][0] != event
        ):
            raise RuntimeError(
                "Confirmed event does not match the next retained authoritative outbox record."
            )

        source_id = self.source_store.source_id()
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT * FROM ohlcv_relay_publisher_checkpoint WHERE source_id=?",
                (source_id,),
            ).fetchone()
            if row is None:
                raise RuntimeError("Publisher checkpoint is not initialized.")
            if (
                int(row["schema_version"]) != _PUBLISHER_SCHEMA_VERSION
                or str(row["stream_key"]) != self.stream_key
            ):
                raise RuntimeError("Publisher checkpoint schema or stream key mismatch.")
            if (
                row["lease_owner"] is None
                or str(row["lease_owner"]) != owner
                or int(row["lease_epoch"]) != epoch
                or int(row["lease_expires_ms"]) <= now_ms
            ):
                raise RuntimeError("Publisher lease is absent, expired or fenced by a newer owner.")
            if int(row["published_cursor"]) != expected_cursor:
                raise RuntimeError("Publisher checkpoint compare-and-swap failed.")
            db.execute(
                """UPDATE ohlcv_relay_publisher_checkpoint
                SET published_cursor=?,last_event_id=?,last_stream_id=?,updated_at_ms=?
                WHERE source_id=? AND published_cursor=? AND lease_owner=?
                    AND lease_epoch=? AND lease_expires_ms>?""",
                (
                    cursor, event_id, stream_id, now_ms, source_id,
                    expected_cursor, owner, epoch, now_ms,
                ),
            )
            updated = db.execute(
                "SELECT * FROM ohlcv_relay_publisher_checkpoint WHERE source_id=?",
                (source_id,),
            ).fetchone()
            if int(updated["published_cursor"]) != cursor:
                raise RuntimeError("Publisher checkpoint failed its fenced cursor update.")
            db.execute("COMMIT")
            return self._row_dict(updated)
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()
