"""Typed repository API for versioned instrument metadata revisions.

This module deliberately does not ingest provider feeds or choose between
conflicting sources. It persists source-attributed claims and fails closed
when an as-of lookup is ambiguous.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping
from uuid import UUID

_SQLITE_MAX_INTEGER = 9_223_372_036_854_775_807
_SOURCE_KINDS = frozenset({"provider", "operator"})


class MetadataRevisionError(RuntimeError):
    """Base error for metadata revision repository operations."""


class MetadataRevisionConflict(MetadataRevisionError):
    """A revision overlaps another claim or resolution is ambiguous."""


class UnknownMetadataInstrument(MetadataRevisionError):
    """A metadata revision references an unregistered canonical instrument."""


@dataclass(frozen=True, slots=True)
class InstrumentMetadataRevision:
    revision_id: int
    canonical_id: str
    source_kind: str
    source_name: str
    source_dataset: str | None
    source_event_ts_ns: int | None
    received_at_utc: str
    effective_from_ns: int | None
    effective_to_ns: int | None
    validity_status: str
    payload_schema_version: int
    metadata: dict[str, Any]


def _timestamp(value: int | None, field_name: str, *, required: bool = False) -> None:
    if value is None:
        if required:
            raise ValueError(f"{field_name} is required.")
        return
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > _SQLITE_MAX_INTEGER
    ):
        raise ValueError(f"{field_name} must be a non-negative SQLite-range integer.")


def _canonical_id(value: str) -> str:
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("canonical_id must be a valid UUID.") from None


class SQLiteInstrumentMetadataRepository:
    """Persistence API over the v2 metadata revision table.

    The database must already be initialized by SQLiteInstrumentRegistry.
    Each method owns its connection; writes are serialized with BEGIN IMMEDIATE.
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
    def _record(row: sqlite3.Row | None) -> InstrumentMetadataRevision | None:
        if row is None:
            return None
        return InstrumentMetadataRevision(
            revision_id=row["revision_id"],
            canonical_id=row["canonical_id"],
            source_kind=row["source_kind"],
            source_name=row["source_name"],
            source_dataset=row["source_dataset"],
            source_event_ts_ns=row["source_event_ts_ns"],
            received_at_utc=row["received_at_utc"],
            effective_from_ns=row["effective_from_ns"],
            effective_to_ns=row["effective_to_ns"],
            validity_status=row["validity_status"],
            payload_schema_version=row["payload_schema_version"],
            metadata=json.loads(row["metadata_json"]),
        )

    def append_revision(
        self,
        *,
        canonical_id: str,
        source_kind: str,
        source_name: str,
        metadata: Mapping[str, Any],
        effective_from_ns: int,
        effective_to_ns: int | None = None,
        source_dataset: str | None = None,
        source_event_ts_ns: int | None = None,
        payload_schema_version: int = 1,
    ) -> tuple[InstrumentMetadataRevision, bool]:
        """Append a known-validity revision; return (record, created).

        Exact retries are idempotent. Historical-unknown records are migration
        artifacts and cannot be created through this provider/operator API.
        """
        normalized_id = _canonical_id(canonical_id)
        if source_kind not in _SOURCE_KINDS:
            raise ValueError("source_kind must be 'provider' or 'operator'.")
        if not isinstance(source_name, str) or not source_name.strip():
            raise ValueError("source_name is required.")
        normalized_source = source_name.strip().lower()
        if source_dataset is not None:
            if not isinstance(source_dataset, str) or not source_dataset.strip():
                raise ValueError("source_dataset must be non-empty when supplied.")
            normalized_dataset = source_dataset.strip().upper()
        else:
            normalized_dataset = None
        _timestamp(source_event_ts_ns, "source_event_ts_ns")
        _timestamp(effective_from_ns, "effective_from_ns", required=True)
        _timestamp(effective_to_ns, "effective_to_ns")
        if effective_to_ns is not None and effective_to_ns <= effective_from_ns:
            raise ValueError("effective_to_ns must be greater than effective_from_ns.")
        if (
            not isinstance(payload_schema_version, int)
            or isinstance(payload_schema_version, bool)
            or payload_schema_version < 1
        ):
            raise ValueError("payload_schema_version must be a positive integer.")
        if not isinstance(metadata, Mapping):
            raise ValueError("metadata must be a JSON object.")
        try:
            metadata_json = json.dumps(
                dict(metadata), sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False,
            )
        except (TypeError, ValueError):
            raise ValueError("metadata must contain finite JSON-compatible values.") from None
        if not isinstance(json.loads(metadata_json), dict):
            raise ValueError("metadata must serialize to a JSON object.")

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            exact = connection.execute(
                """
                SELECT * FROM instrument_metadata_revisions
                WHERE canonical_id = ? AND source_kind = ? AND source_name = ?
                  AND source_dataset IS ? AND source_event_ts_ns IS ?
                  AND effective_from_ns = ? AND effective_to_ns IS ?
                  AND validity_status = 'known' AND payload_schema_version = ?
                  AND metadata_json = ?
                ORDER BY revision_id LIMIT 1
                """,
                (
                    normalized_id, source_kind, normalized_source,
                    normalized_dataset, source_event_ts_ns, effective_from_ns,
                    effective_to_ns, payload_schema_version, metadata_json,
                ),
            ).fetchone()
            if exact is not None:
                connection.commit()
                record = self._record(exact)
                assert record is not None
                return record, False

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO instrument_metadata_revisions (
                        canonical_id, source_kind, source_name, source_dataset,
                        source_event_ts_ns, effective_from_ns, effective_to_ns,
                        validity_status, payload_schema_version, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'known', ?, ?)
                    """,
                    (
                        normalized_id, source_kind, normalized_source,
                        normalized_dataset, source_event_ts_ns, effective_from_ns,
                        effective_to_ns, payload_schema_version, metadata_json,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                message = str(exc)
                if "overlapping_metadata_revision" in message:
                    raise MetadataRevisionConflict(
                        "Metadata revision overlaps an existing claim from the same source."
                    ) from exc
                if "FOREIGN KEY" in message:
                    raise UnknownMetadataInstrument(
                        "Metadata revision references an unregistered canonical instrument."
                    ) from exc
                raise
            row = connection.execute(
                "SELECT * FROM instrument_metadata_revisions WHERE revision_id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            connection.commit()
            record = self._record(row)
            assert record is not None
            return record, True
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def append_revision_transition(
        self,
        *,
        canonical_id: str,
        source_kind: str,
        source_name: str,
        metadata: Mapping[str, Any],
        effective_from_ns: int,
        source_dataset: str | None = None,
        source_event_ts_ns: int | None = None,
        payload_schema_version: int = 1,
    ) -> tuple[InstrumentMetadataRevision, bool]:
        """Atomically supersede the open revision with a strictly newer claim.

        This is the ordered-event path for one canonical instrument and one
        source identity. Exact retries are idempotent. Older or same-effective-
        time conflicting events are rejected without changing the current row.
        The prior interval is closed and the new revision inserted in one
        SQLite transaction.
        """
        normalized_id = _canonical_id(canonical_id)
        if source_kind not in _SOURCE_KINDS:
            raise ValueError("source_kind must be 'provider' or 'operator'.")
        if not isinstance(source_name, str) or not source_name.strip():
            raise ValueError("source_name is required.")
        normalized_source = source_name.strip().lower()
        if source_dataset is not None:
            if not isinstance(source_dataset, str) or not source_dataset.strip():
                raise ValueError("source_dataset must be non-empty when supplied.")
            normalized_dataset = source_dataset.strip().upper()
        else:
            normalized_dataset = None
        _timestamp(source_event_ts_ns, "source_event_ts_ns")
        _timestamp(effective_from_ns, "effective_from_ns", required=True)
        if (
            not isinstance(payload_schema_version, int)
            or isinstance(payload_schema_version, bool)
            or payload_schema_version < 1
        ):
            raise ValueError("payload_schema_version must be a positive integer.")
        if not isinstance(metadata, Mapping):
            raise ValueError("metadata must be a JSON object.")
        try:
            metadata_json = json.dumps(
                dict(metadata), sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False,
            )
        except (TypeError, ValueError):
            raise ValueError("metadata must contain finite JSON-compatible values.") from None
        if not isinstance(json.loads(metadata_json), dict):
            raise ValueError("metadata must serialize to a JSON object.")

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            identity_parameters = (
                normalized_id, source_kind, normalized_source, normalized_dataset,
            )
            exact = connection.execute(
                """
                SELECT * FROM instrument_metadata_revisions
                WHERE canonical_id = ? AND source_kind = ? AND source_name = ?
                  AND source_dataset IS ? AND source_event_ts_ns IS ?
                  AND effective_from_ns = ? AND effective_to_ns IS NULL
                  AND validity_status = 'known' AND payload_schema_version = ?
                  AND metadata_json = ?
                ORDER BY revision_id LIMIT 1
                """,
                (
                    *identity_parameters, source_event_ts_ns, effective_from_ns,
                    payload_schema_version, metadata_json,
                ),
            ).fetchone()
            if exact is not None:
                connection.commit()
                record = self._record(exact)
                assert record is not None
                return record, False

            instrument_exists = connection.execute(
                "SELECT 1 FROM canonical_instruments WHERE canonical_id = ?",
                (normalized_id,),
            ).fetchone()
            if instrument_exists is None:
                raise UnknownMetadataInstrument(
                    "Metadata revision references an unregistered canonical instrument."
                )

            latest = connection.execute(
                """
                SELECT * FROM instrument_metadata_revisions
                WHERE canonical_id = ? AND source_kind = ? AND source_name = ?
                  AND source_dataset IS ? AND validity_status = 'known'
                ORDER BY effective_from_ns DESC, revision_id DESC LIMIT 1
                """,
                identity_parameters,
            ).fetchone()
            if latest is not None and effective_from_ns <= latest["effective_from_ns"]:
                raise MetadataRevisionConflict(
                    "Out-of-order or conflicting metadata event; effective time must increase."
                )

            if latest is not None and latest["effective_to_ns"] is None:
                connection.execute(
                    """
                    UPDATE instrument_metadata_revisions
                    SET effective_to_ns = ?
                    WHERE revision_id = ? AND effective_to_ns IS NULL
                    """,
                    (effective_from_ns, latest["revision_id"]),
                )

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO instrument_metadata_revisions (
                        canonical_id, source_kind, source_name, source_dataset,
                        source_event_ts_ns, effective_from_ns, effective_to_ns,
                        validity_status, payload_schema_version, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, NULL, 'known', ?, ?)
                    """,
                    (
                        normalized_id, source_kind, normalized_source,
                        normalized_dataset, source_event_ts_ns, effective_from_ns,
                        payload_schema_version, metadata_json,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                message = str(exc)
                if "overlapping_metadata_revision" in message:
                    raise MetadataRevisionConflict(
                        "Metadata revision overlaps an existing claim from the same source."
                    ) from exc
                if "FOREIGN KEY" in message:
                    raise UnknownMetadataInstrument(
                        "Metadata revision references an unregistered canonical instrument."
                    ) from exc
                raise
            row = connection.execute(
                "SELECT * FROM instrument_metadata_revisions WHERE revision_id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            connection.commit()
            record = self._record(row)
            assert record is not None
            return record, True
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def close_open_revision(self, revision_id: int, effective_to_ns: int) -> InstrumentMetadataRevision:
        """Close an open known revision without changing its immutable payload."""
        if (
            not isinstance(revision_id, int)
            or isinstance(revision_id, bool)
            or revision_id <= 0
        ):
            raise ValueError("revision_id must be a positive integer.")
        _timestamp(effective_to_ns, "effective_to_ns", required=True)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM instrument_metadata_revisions WHERE revision_id = ?",
                (revision_id,),
            ).fetchone()
            if row is None:
                raise ValueError("revision_id does not exist.")
            if row["validity_status"] != "known" or row["effective_to_ns"] is not None:
                raise ValueError("Only an open known revision can be closed.")
            if effective_to_ns <= row["effective_from_ns"]:
                raise ValueError("effective_to_ns must be greater than effective_from_ns.")
            try:
                connection.execute(
                    """
                    UPDATE instrument_metadata_revisions
                    SET effective_to_ns = ?
                    WHERE revision_id = ? AND effective_to_ns IS NULL
                    """,
                    (effective_to_ns, revision_id),
                )
            except sqlite3.IntegrityError as exc:
                if "overlapping_metadata_revision" in str(exc):
                    raise MetadataRevisionConflict(
                        "Closing this revision would overlap another source revision."
                    ) from exc
                raise
            updated = connection.execute(
                "SELECT * FROM instrument_metadata_revisions WHERE revision_id = ?",
                (revision_id,),
            ).fetchone()
            connection.commit()
            record = self._record(updated)
            assert record is not None
            return record
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def list_revisions(
        self,
        canonical_id: str,
        *,
        source_kind: str | None = None,
        source_name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InstrumentMetadataRevision]:
        normalized_id = _canonical_id(canonical_id)
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000.")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise ValueError("offset must be a non-negative integer.")
        clauses = ["canonical_id = ?"]
        parameters: list[Any] = [normalized_id]
        if source_kind is not None:
            if source_kind not in _SOURCE_KINDS:
                raise ValueError("source_kind must be 'provider' or 'operator'.")
            clauses.append("source_kind = ?")
            parameters.append(source_kind)
        if source_name is not None:
            if not isinstance(source_name, str) or not source_name.strip():
                raise ValueError("source_name must be non-empty when supplied.")
            clauses.append("source_name = ?")
            parameters.append(source_name.strip().lower())
        connection = self._connect()
        try:
            rows = connection.execute(
                f"""
                SELECT * FROM instrument_metadata_revisions
                WHERE {' AND '.join(clauses)}
                ORDER BY effective_from_ns, revision_id
                LIMIT ? OFFSET ?
                """,
                (*parameters, limit, offset),
            ).fetchall()
            return [record for row in rows if (record := self._record(row)) is not None]
        finally:
            connection.close()

    def resolve_as_of(
        self,
        canonical_id: str,
        timestamp_ns: int,
        *,
        source_kind: str | None = None,
        source_name: str | None = None,
        source_dataset: str | None = None,
    ) -> InstrumentMetadataRevision | None:
        """Resolve one source claim at a timestamp, never silently pick a source."""
        normalized_id = _canonical_id(canonical_id)
        _timestamp(timestamp_ns, "timestamp_ns", required=True)
        clauses = [
            "canonical_id = ?", "validity_status = 'known'",
            "effective_from_ns <= ?",
            "(effective_to_ns IS NULL OR ? < effective_to_ns)",
        ]
        parameters: list[Any] = [normalized_id, timestamp_ns, timestamp_ns]
        if source_kind is not None:
            if source_kind not in _SOURCE_KINDS:
                raise ValueError("source_kind must be 'provider' or 'operator'.")
            clauses.append("source_kind = ?")
            parameters.append(source_kind)
        if source_name is not None:
            if not isinstance(source_name, str) or not source_name.strip():
                raise ValueError("source_name must be non-empty when supplied.")
            clauses.append("source_name = ?")
            parameters.append(source_name.strip().lower())
        if source_dataset is not None:
            if not isinstance(source_dataset, str) or not source_dataset.strip():
                raise ValueError("source_dataset must be non-empty when supplied.")
            clauses.append("source_dataset = ?")
            parameters.append(source_dataset.strip().upper())

        connection = self._connect()
        try:
            rows = connection.execute(
                f"""
                SELECT * FROM instrument_metadata_revisions
                WHERE {' AND '.join(clauses)}
                ORDER BY revision_id LIMIT 2
                """,
                parameters,
            ).fetchall()
            if len(rows) > 1:
                raise MetadataRevisionConflict(
                    "Multiple source claims resolve at this timestamp; specify source provenance."
                )
            return self._record(rows[0] if rows else None)
        finally:
            connection.close()
