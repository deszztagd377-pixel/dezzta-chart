"""Atomic provider-definition events spanning mapping and metadata timelines.

A provider definition event is accepted only when its mapping and metadata
claims can be committed together in one SQLite transaction. This prevents
readers from observing a new provider identity mapping without its matching
versioned instrument definition (or vice versa).
"""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping

from app.instrument_metadata import (
    InstrumentMetadataRevision,
    MetadataRevisionConflict,
    UnknownMetadataInstrument,
)
from app.instrument_metadata import _timestamp
from app.instrument_registry import (
    InstrumentMappingConflict,
    ProviderInstrumentMapping,
    UnknownCanonicalInstrument,
    _normalize_mapping,
)


class ProviderDefinitionEventConflict(RuntimeError):
    """A provider event is stale, conflicting, or only partially replayed."""


class SQLiteProviderDefinitionEventRepository:
    """Coordinates provider mapping and metadata revisions in one DB transaction.

    The database must already be initialized by SQLiteInstrumentRegistry.
    Each event creates an open mapping and an open metadata revision at the
    mapping's effective timestamp; the prior open rows are closed atomically.
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
    def _mapping_record(row: sqlite3.Row) -> ProviderInstrumentMapping:
        return ProviderInstrumentMapping(
            provider=row["provider"],
            dataset=row["dataset"],
            publisher_id=row["publisher_id"],
            instrument_id=row["instrument_id"],
            raw_symbol=row["raw_symbol"],
            valid_from_ns=row["valid_from_ns"],
            valid_to_ns=row["valid_to_ns"],
            canonical_id=row["canonical_id"],
            series_type=row["series_type"],
        )

    @staticmethod
    def _metadata_record(row: sqlite3.Row) -> InstrumentMetadataRevision:
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

    def apply_event(
        self,
        mapping: ProviderInstrumentMapping,
        *,
        metadata: Mapping[str, Any],
        source_event_ts_ns: int | None = None,
        payload_schema_version: int = 1,
    ) -> tuple[ProviderInstrumentMapping, InstrumentMetadataRevision, bool]:
        """Apply a provider mapping + metadata definition as one atomic event.

        Mapping transitions are keyed by provider/dataset/publisher/instrument.
        Metadata provenance is derived from the normalized provider and dataset.
        Exact historical event replays are idempotent even after supersession.
        """
        normalized = _normalize_mapping(mapping)
        if normalized.valid_to_ns is not None:
            raise ValueError("A provider definition transition must start as an open mapping.")
        _timestamp(source_event_ts_ns, "source_event_ts_ns")
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
            key = (
                normalized.provider, normalized.dataset, normalized.publisher_id,
                normalized.instrument_id,
            )
            exact_mapping = connection.execute(
                """
                SELECT * FROM provider_instrument_mappings
                WHERE provider = ? AND dataset = ? AND publisher_id = ?
                  AND instrument_id = ? AND valid_from_ns = ?
                  AND canonical_id = ? AND raw_symbol = ? AND series_type = ?
                ORDER BY rowid LIMIT 1
                """,
                (*key, normalized.valid_from_ns, normalized.canonical_id,
                 normalized.raw_symbol, normalized.series_type),
            ).fetchone()
            exact_metadata = connection.execute(
                """
                SELECT * FROM instrument_metadata_revisions
                WHERE canonical_id = ? AND source_kind = 'provider'
                  AND source_name = ? AND source_dataset = ?
                  AND source_event_ts_ns IS ? AND effective_from_ns = ?
                  AND validity_status = 'known' AND payload_schema_version = ?
                  AND metadata_json = ?
                ORDER BY revision_id LIMIT 1
                """,
                (
                    normalized.canonical_id, normalized.provider, normalized.dataset,
                    source_event_ts_ns, normalized.valid_from_ns,
                    payload_schema_version, metadata_json,
                ),
            ).fetchone()

            if exact_mapping is not None or exact_metadata is not None:
                if exact_mapping is None or exact_metadata is None:
                    raise ProviderDefinitionEventConflict(
                        "Partial event replay detected; mapping and metadata must both exist."
                    )
                connection.commit()
                return (
                    self._mapping_record(exact_mapping),
                    self._metadata_record(exact_metadata),
                    False,
                )

            instrument_exists = connection.execute(
                "SELECT 1 FROM canonical_instruments WHERE canonical_id = ?",
                (normalized.canonical_id,),
            ).fetchone()
            if instrument_exists is None:
                raise UnknownCanonicalInstrument(
                    "Provider mapping references an unregistered canonical instrument."
                )

            latest_mapping = connection.execute(
                """
                SELECT rowid AS mapping_rowid, * FROM provider_instrument_mappings
                WHERE provider = ? AND dataset = ? AND publisher_id = ?
                  AND instrument_id = ?
                ORDER BY valid_from_ns DESC LIMIT 1
                """,
                key,
            ).fetchone()
            if (
                latest_mapping is not None
                and normalized.valid_from_ns <= latest_mapping["valid_from_ns"]
            ):
                raise ProviderDefinitionEventConflict(
                    "Out-of-order or conflicting provider mapping event."
                )

            latest_metadata = connection.execute(
                """
                SELECT * FROM instrument_metadata_revisions
                WHERE canonical_id = ? AND source_kind = 'provider'
                  AND source_name = ? AND source_dataset IS ?
                  AND validity_status = 'known'
                ORDER BY effective_from_ns DESC, revision_id DESC LIMIT 1
                """,
                (normalized.canonical_id, normalized.provider, normalized.dataset),
            ).fetchone()
            if (
                latest_metadata is not None
                and normalized.valid_from_ns <= latest_metadata["effective_from_ns"]
            ):
                raise MetadataRevisionConflict(
                    "Out-of-order or conflicting provider metadata event."
                )

            if latest_mapping is not None and latest_mapping["valid_to_ns"] is None:
                connection.execute(
                    """
                    UPDATE provider_instrument_mappings SET valid_to_ns = ?
                    WHERE rowid = ? AND valid_to_ns IS NULL
                    """,
                    (normalized.valid_from_ns, latest_mapping["mapping_rowid"]),
                )
            if latest_metadata is not None and latest_metadata["effective_to_ns"] is None:
                connection.execute(
                    """
                    UPDATE instrument_metadata_revisions SET effective_to_ns = ?
                    WHERE revision_id = ? AND effective_to_ns IS NULL
                    """,
                    (normalized.valid_from_ns, latest_metadata["revision_id"]),
                )

            try:
                connection.execute(
                    """
                    INSERT INTO provider_instrument_mappings (
                        provider, dataset, publisher_id, instrument_id, raw_symbol,
                        valid_from_ns, valid_to_ns, canonical_id, series_type
                    ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)
                    """,
                    (
                        normalized.provider, normalized.dataset, normalized.publisher_id,
                        normalized.instrument_id, normalized.raw_symbol,
                        normalized.valid_from_ns, normalized.canonical_id,
                        normalized.series_type,
                    ),
                )
                cursor = connection.execute(
                    """
                    INSERT INTO instrument_metadata_revisions (
                        canonical_id, source_kind, source_name, source_dataset,
                        source_event_ts_ns, effective_from_ns, effective_to_ns,
                        validity_status, payload_schema_version, metadata_json
                    ) VALUES (?, 'provider', ?, ?, ?, ?, NULL, 'known', ?, ?)
                    """,
                    (
                        normalized.canonical_id, normalized.provider, normalized.dataset,
                        source_event_ts_ns, normalized.valid_from_ns,
                        payload_schema_version, metadata_json,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                message = str(exc)
                if "overlapping_provider_mapping" in message or "UNIQUE constraint" in message:
                    raise InstrumentMappingConflict(
                        "Provider instrument mapping overlaps an existing validity window."
                    ) from exc
                if "overlapping_metadata_revision" in message:
                    raise MetadataRevisionConflict(
                        "Provider metadata revision overlaps an existing source claim."
                    ) from exc
                if "FOREIGN KEY" in message:
                    raise UnknownMetadataInstrument(
                        "Provider metadata references an unregistered canonical instrument."
                    ) from exc
                raise

            mapping_row = connection.execute(
                """
                SELECT * FROM provider_instrument_mappings
                WHERE provider = ? AND dataset = ? AND publisher_id = ?
                  AND instrument_id = ? AND valid_from_ns = ?
                """,
                (*key, normalized.valid_from_ns),
            ).fetchone()
            metadata_row = connection.execute(
                "SELECT * FROM instrument_metadata_revisions WHERE revision_id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            connection.commit()
            assert mapping_row is not None and metadata_row is not None
            return (
                self._mapping_record(mapping_row),
                self._metadata_record(metadata_row),
                True,
            )
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()
