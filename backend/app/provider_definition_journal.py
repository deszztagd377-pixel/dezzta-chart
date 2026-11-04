"""Durable append-only journal for provider instrument-definition events.

The journal records the provider's original event before canonical resolution.
It is deliberately separate from the in-memory catalog and from the atomic
mapping/metadata transition repository.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping


class ProviderDefinitionJournalError(RuntimeError):
    """Base error for durable provider definition journal operations."""


class ProviderDefinitionJournalConflict(ProviderDefinitionJournalError):
    """An event key was replayed with different contents or state."""


@dataclass(frozen=True, slots=True)
class ProviderDefinitionJournalRecord:
    event_id: str
    provider: str
    dataset: str
    publisher_id: int
    instrument_id: int
    source_event_ts_ns: int
    source_order: int
    action: str
    raw_symbol: str
    payload_sha256: str
    payload: dict[str, Any]
    received_at_utc: str
    processing_status: str
    canonical_id: str | None
    error_code: str | None


class SQLiteProviderDefinitionJournal:
    """Persist and replay provider events using a file-backed SQLite database.

    The registry must be initialized first so the schema-v5 journal table and
    canonical-instrument foreign key exist. Source order is explicit because
    providers may deliver multiple records with the same event timestamp.
    """

    def __init__(self, database_path: str, *, busy_timeout_ms: int = 10_000) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("database_path is required.")
        if database_path == ":memory:":
            raise ValueError("A file-backed database is required.")
        if (
            not isinstance(busy_timeout_ms, int)
            or isinstance(busy_timeout_ms, bool)
            or busy_timeout_ms < 1
        ):
            raise ValueError("busy_timeout_ms must be a positive integer.")
        self.database_path = str(Path(database_path).expanduser())
        self.busy_timeout_ms = busy_timeout_ms

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=self.busy_timeout_ms / 1000,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
        return connection

    @staticmethod
    def _record(row: sqlite3.Row) -> ProviderDefinitionJournalRecord:
        return ProviderDefinitionJournalRecord(
            event_id=row["event_id"],
            provider=row["provider"],
            dataset=row["dataset"],
            publisher_id=row["publisher_id"],
            instrument_id=row["instrument_id"],
            source_event_ts_ns=row["source_event_ts_ns"],
            source_order=row["source_order"],
            action=row["action"],
            raw_symbol=row["raw_symbol"],
            payload_sha256=row["payload_sha256"],
            payload=json.loads(row["payload_json"]),
            received_at_utc=row["received_at_utc"],
            processing_status=row["processing_status"],
            canonical_id=row["canonical_id"],
            error_code=row["error_code"],
        )

    def append_event(
        self,
        *,
        provider: str,
        dataset: str,
        publisher_id: int,
        instrument_id: int,
        source_event_ts_ns: int,
        source_order: int,
        action: str,
        raw_symbol: str,
        payload: Mapping[str, Any],
    ) -> tuple[ProviderDefinitionJournalRecord, bool]:
        """Append one source event; exact replays are idempotent.

        The unique source key includes source_order, preserving stable order
        when multiple provider events share the same nanosecond timestamp.
        """
        text_fields = {
            "provider": provider,
            "dataset": dataset,
            "action": action,
            "raw_symbol": raw_symbol,
        }
        for field, value in text_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} is required.")
        for field, value in {
            "publisher_id": publisher_id,
            "instrument_id": instrument_id,
            "source_event_ts_ns": source_event_ts_ns,
            "source_order": source_order,
        }.items():
            minimum = 1 if field in {"publisher_id", "instrument_id"} else 0
            if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
                raise ValueError(f"{field} must be an integer >= {minimum}.")
        normalized_action = action.strip().upper()
        if normalized_action not in {"A", "M", "D"}:
            raise ValueError("action must be Add (A), Modify (M), or Delete (D).")
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be a mapping.")
        try:
            payload_json = json.dumps(
                dict(payload), sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False,
            )
        except (TypeError, ValueError):
            raise ValueError("payload must contain finite JSON-compatible values.") from None
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        normalized_provider = provider.strip().lower()
        normalized_dataset = dataset.strip().upper()
        normalized_symbol = raw_symbol.strip().upper()
        source_key = (
            normalized_provider, normalized_dataset, publisher_id, instrument_id,
            source_event_ts_ns, source_order,
        )
        event_id = hashlib.sha256(
            ("\x1f".join(map(str, source_key)) + "\x1f" + payload_hash).encode("utf-8")
        ).hexdigest()

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                """
                SELECT * FROM provider_definition_events
                WHERE provider = ? AND dataset = ? AND publisher_id = ?
                  AND instrument_id = ? AND source_event_ts_ns = ? AND source_order = ?
                """,
                source_key,
            ).fetchone()
            if existing is not None:
                if (
                    existing["payload_sha256"] != payload_hash
                    or existing["action"] != normalized_action
                    or existing["raw_symbol"] != normalized_symbol
                ):
                    raise ProviderDefinitionJournalConflict(
                        "The same provider source-order key was replayed with different event contents."
                    )
                connection.commit()
                return self._record(existing), False

            connection.execute(
                """
                INSERT INTO provider_definition_events (
                    event_id, provider, dataset, publisher_id, instrument_id,
                    source_event_ts_ns, source_order, action, raw_symbol,
                    payload_sha256, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id, normalized_provider, normalized_dataset,
                    publisher_id, instrument_id, source_event_ts_ns, source_order,
                    normalized_action, normalized_symbol, payload_hash, payload_json,
                ),
            )
            row = connection.execute(
                "SELECT * FROM provider_definition_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            connection.commit()
            assert row is not None
            return self._record(row), True
        except sqlite3.IntegrityError as exc:
            if connection.in_transaction:
                connection.rollback()
            raise ProviderDefinitionJournalConflict(
                "Provider event could not be appended without violating journal integrity."
            ) from exc
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def mark_applied(self, event_id: str, canonical_id: str) -> bool:
        """Mark a pending event applied after its registry transaction succeeds."""
        if not isinstance(event_id, str) or len(event_id) != 64:
            raise ValueError("event_id must be a SHA-256 hex digest.")
        if not isinstance(canonical_id, str) or not canonical_id.strip():
            raise ValueError("canonical_id is required.")
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM provider_definition_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            if row is None:
                raise KeyError(event_id)
            if row["processing_status"] == "applied":
                if row["canonical_id"] == canonical_id:
                    connection.commit()
                    return False
                raise ProviderDefinitionJournalConflict("Event was already applied to another canonical ID.")
            if row["processing_status"] != "pending":
                raise ProviderDefinitionJournalConflict("A quarantined event cannot be marked applied.")
            connection.execute(
                """
                UPDATE provider_definition_events
                SET processing_status = 'applied', canonical_id = ?
                WHERE event_id = ? AND processing_status = 'pending'
                """,
                (canonical_id, event_id),
            )
            connection.commit()
            return True
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def mark_quarantined(self, event_id: str, error_code: str) -> bool:
        """Quarantine an unresolved/ambiguous event without discarding its payload."""
        if not isinstance(event_id, str) or len(event_id) != 64:
            raise ValueError("event_id must be a SHA-256 hex digest.")
        if not isinstance(error_code, str) or not error_code.strip():
            raise ValueError("error_code is required.")
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM provider_definition_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            if row is None:
                raise KeyError(event_id)
            if row["processing_status"] == "quarantined":
                if row["error_code"] == error_code.strip():
                    connection.commit()
                    return False
                raise ProviderDefinitionJournalConflict("Event was quarantined with a different error code.")
            if row["processing_status"] != "pending":
                raise ProviderDefinitionJournalConflict("An applied event cannot be quarantined.")
            connection.execute(
                """
                UPDATE provider_definition_events
                SET processing_status = 'quarantined', error_code = ?
                WHERE event_id = ? AND processing_status = 'pending'
                """,
                (error_code.strip(), event_id),
            )
            connection.commit()
            return True
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def list_pending(self, *, limit: int = 100) -> list[ProviderDefinitionJournalRecord]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000.")
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT * FROM provider_definition_events
                WHERE processing_status = 'pending'
                ORDER BY source_event_ts_ns, source_order, provider, dataset,
                         publisher_id, instrument_id
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [self._record(row) for row in rows]
        finally:
            connection.close()

    def get_event(self, event_id: str) -> ProviderDefinitionJournalRecord | None:
        if not isinstance(event_id, str) or len(event_id) != 64:
            raise ValueError("event_id must be a SHA-256 hex digest.")
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT * FROM provider_definition_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            return None if row is None else self._record(row)
        finally:
            connection.close()
