"""Durable, monotonic receipts for authenticated OHLCV WebSocket consumers.

This store is a persistence primitive only. Callers MUST validate that an ACK
matches an event actually sent on the authenticated socket and enforce their
consumer-lease/fencing policy before committing a receipt. It deliberately does
not advertise or activate the WebSocket ACK protocol by itself.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import time
from pathlib import Path
from typing import Any

MAX_SQLITE_INTEGER = (1 << 63) - 1
MAX_CONSUMER_ID_LENGTH = 128
MAX_ACCOUNT_SUBJECT_LENGTH = 256
MAX_STREAM_ID_LENGTH = 128
MAX_EVENT_ID_LENGTH = 128
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ID_RE = re.compile(r"^[A-Za-z0-9._:-]+$")


class OhlcvConsumerReceiptError(ValueError):
    """Base class for invalid or conflicting durable consumer receipts."""


class OhlcvConsumerReceiptStale(OhlcvConsumerReceiptError):
    """The ACK cursor is older than the committed receipt."""


class OhlcvConsumerReceiptConflict(OhlcvConsumerReceiptError):
    """The same cursor was presented with a different event identity."""


class SQLiteOhlcvConsumerReceiptStore:
    """File-backed SQLite receipt store with serialized monotonic commits.

    The primary key scopes a receipt to one authenticated account, one stable
    client instance, and one canonical OHLCV series digest. SQLite
    BEGIN IMMEDIATE serializes competing writers; duplicate ACKs are
    idempotent, lower cursors are rejected, and same-cursor digest conflicts
    fail closed.
    """

    def __init__(
        self,
        database_path: str,
        *,
        busy_timeout_ms: int = 10_000,
        clock_ns=time.time_ns,
    ) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("database_path is required.")
        if database_path == ":memory:":
            raise ValueError("A file-backed database is required for durable receipts.")
        if type(busy_timeout_ms) is not int or busy_timeout_ms < 1:
            raise ValueError("busy_timeout_ms must be a positive integer.")
        if not callable(clock_ns):
            raise ValueError("clock_ns must be callable.")
        self.database_path = str(Path(database_path).expanduser())
        self.busy_timeout_ms = busy_timeout_ms
        self._clock_ns = clock_ns
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
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
            db.execute("PRAGMA journal_mode = WAL")
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                """CREATE TABLE IF NOT EXISTS ohlcv_consumer_receipts (
                    account_subject TEXT NOT NULL,
                    consumer_id TEXT NOT NULL,
                    series_key TEXT NOT NULL,
                    committed_cursor INTEGER NOT NULL CHECK(committed_cursor > 0),
                    event_id TEXT NOT NULL,
                    event_digest TEXT NOT NULL CHECK(length(event_digest) = 64),
                    stream_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL CHECK(sequence > 0),
                    receipt_version INTEGER NOT NULL CHECK(receipt_version > 0),
                    fencing_token INTEGER NOT NULL CHECK(fencing_token > 0),
                    updated_at_ns INTEGER NOT NULL CHECK(updated_at_ns >= 0),
                    PRIMARY KEY(account_subject, consumer_id, series_key)
                )"""
            )
            columns = {
                str(row["name"])
                for row in db.execute("PRAGMA table_info(ohlcv_consumer_receipts)")
            }
            if "fencing_token" not in columns:
                # Existing receipts predate owner fencing. Zero marks them as
                # legacy until a current lease holder safely advances them.
                db.execute(
                    """ALTER TABLE ohlcv_consumer_receipts
                    ADD COLUMN fencing_token INTEGER NOT NULL DEFAULT 0
                    CHECK(fencing_token >= 0)"""
                )
            db.execute(
                """CREATE INDEX IF NOT EXISTS idx_ohlcv_consumer_receipts_updated
                ON ohlcv_consumer_receipts(updated_at_ns)"""
            )
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    @staticmethod
    def _validate_text(value: Any, name: str, maximum: int) -> str:
        if (
            not isinstance(value, str)
            or not value
            or value != value.strip()
            or len(value) > maximum
            or not value.isascii()
            or not _ID_RE.fullmatch(value)
        ):
            raise OhlcvConsumerReceiptError(f"{name} is invalid.")
        return value

    @staticmethod
    def series_key_for(identity: dict[str, Any]) -> str:
        """Hash a canonical exact-series identity without storing raw metadata."""
        if not isinstance(identity, dict) or not identity:
            raise OhlcvConsumerReceiptError("series identity is required.")
        try:
            import json
            canonical = json.dumps(
                identity,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise OhlcvConsumerReceiptError("series identity is not canonicalizable.") from exc
        return hashlib.sha256(canonical).hexdigest()

    def commit_receipt(
        self,
        *,
        account_subject: str,
        consumer_id: str,
        series_key: str,
        cursor: int,
        event_id: str,
        event_digest: str,
        stream_id: str,
        sequence: int,
        fencing_token: int,
    ) -> dict[str, object]:
        account_subject = self._validate_text(
            account_subject, "account_subject", MAX_ACCOUNT_SUBJECT_LENGTH,
        )
        consumer_id = self._validate_text(
            consumer_id, "consumer_id", MAX_CONSUMER_ID_LENGTH,
        )
        series_key = self._validate_text(series_key, "series_key", 64)
        if not _SHA256_RE.fullmatch(series_key):
            raise OhlcvConsumerReceiptError("series_key must be a lowercase SHA-256 digest.")
        event_id = self._validate_text(event_id, "event_id", MAX_EVENT_ID_LENGTH)
        stream_id = self._validate_text(stream_id, "stream_id", MAX_STREAM_ID_LENGTH)
        if not isinstance(event_digest, str) or not _SHA256_RE.fullmatch(event_digest):
            raise OhlcvConsumerReceiptError("event_digest must be lowercase SHA-256 hex.")
        if type(cursor) is not int or not 1 <= cursor <= MAX_SQLITE_INTEGER:
            raise OhlcvConsumerReceiptError("cursor must be a positive SQLite-safe integer.")
        if type(sequence) is not int or not 1 <= sequence <= (1 << 53) - 1:
            raise OhlcvConsumerReceiptError("sequence must be a positive JavaScript-safe integer.")
        if type(fencing_token) is not int or not 1 <= fencing_token <= MAX_SQLITE_INTEGER:
            raise OhlcvConsumerReceiptError("fencing_token must be a positive SQLite-safe integer.")
        updated_at_ns = self._clock_ns()
        if type(updated_at_ns) is not int or not 0 <= updated_at_ns <= MAX_SQLITE_INTEGER:
            raise OhlcvConsumerReceiptError("clock_ns returned an invalid timestamp.")

        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                """SELECT committed_cursor,event_id,event_digest,receipt_version,fencing_token
                FROM ohlcv_consumer_receipts
                WHERE account_subject=? AND consumer_id=? AND series_key=?""",
                (account_subject, consumer_id, series_key),
            ).fetchone()
            if row is None:
                receipt_version = 1
                db.execute(
                    """INSERT INTO ohlcv_consumer_receipts(
                        account_subject,consumer_id,series_key,committed_cursor,
                        event_id,event_digest,stream_id,sequence,receipt_version,
                        fencing_token,updated_at_ns
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        account_subject, consumer_id, series_key, cursor,
                        event_id, event_digest, stream_id, sequence,
                        receipt_version, fencing_token, updated_at_ns,
                    ),
                )
                duplicate = False
            else:
                previous_cursor = int(row["committed_cursor"])
                previous_fence = int(row["fencing_token"])
                receipt_version = int(row["receipt_version"])
                if fencing_token < previous_fence:
                    raise OhlcvConsumerReceiptStale("ACK fencing token is older than the committed owner.")
                if cursor < previous_cursor:
                    raise OhlcvConsumerReceiptStale("ACK cursor is older than the committed receipt.")
                if cursor == previous_cursor:
                    if row["event_id"] != event_id or row["event_digest"] != event_digest:
                        raise OhlcvConsumerReceiptConflict(
                            "ACK cursor conflicts with the committed event identity."
                        )
                    duplicate = True
                    fence_advanced = fencing_token > previous_fence
                    if fence_advanced:
                        receipt_version += 1
                    db.execute(
                        """UPDATE ohlcv_consumer_receipts
                        SET stream_id=?,sequence=?,fencing_token=?,receipt_version=?,updated_at_ns=?
                        WHERE account_subject=? AND consumer_id=? AND series_key=?""",
                        (
                            stream_id, sequence, fencing_token, receipt_version, updated_at_ns,
                            account_subject, consumer_id, series_key,
                        ),
                    )
                else:
                    receipt_version += 1
                    duplicate = False
                    db.execute(
                        """UPDATE ohlcv_consumer_receipts SET
                            committed_cursor=?,event_id=?,event_digest=?,
                            stream_id=?,sequence=?,fencing_token=?,receipt_version=?,updated_at_ns=?
                        WHERE account_subject=? AND consumer_id=? AND series_key=?""",
                        (
                            cursor, event_id, event_digest, stream_id, sequence,
                            fencing_token, receipt_version, updated_at_ns,
                            account_subject, consumer_id, series_key,
                        ),
                    )
            db.execute("COMMIT")
            return {
                "accepted": True,
                "duplicate": duplicate,
                "committed_cursor": str(cursor),
                "receipt_version": receipt_version,
                "fencing_token": fencing_token,
            }
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def get_receipt(
        self, *, account_subject: str, consumer_id: str, series_key: str,
    ) -> dict[str, object] | None:
        account_subject = self._validate_text(
            account_subject, "account_subject", MAX_ACCOUNT_SUBJECT_LENGTH,
        )
        consumer_id = self._validate_text(
            consumer_id, "consumer_id", MAX_CONSUMER_ID_LENGTH,
        )
        series_key = self._validate_text(series_key, "series_key", 64)
        if not _SHA256_RE.fullmatch(series_key):
            raise OhlcvConsumerReceiptError("series_key must be a lowercase SHA-256 digest.")
        db = self._connect()
        try:
            row = db.execute(
                """SELECT committed_cursor,event_id,event_digest,stream_id,
                    sequence,receipt_version,fencing_token,updated_at_ns
                FROM ohlcv_consumer_receipts
                WHERE account_subject=? AND consumer_id=? AND series_key=?""",
                (account_subject, consumer_id, series_key),
            ).fetchone()
            if row is None:
                return None
            return {
                "committed_cursor": str(row["committed_cursor"]),
                "event_id": str(row["event_id"]),
                "event_digest": str(row["event_digest"]),
                "stream_id": str(row["stream_id"]),
                "sequence": int(row["sequence"]),
                "receipt_version": int(row["receipt_version"]),
                "fencing_token": int(row["fencing_token"]),
                "updated_at_ns": int(row["updated_at_ns"]),
            }
        finally:
            db.close()
