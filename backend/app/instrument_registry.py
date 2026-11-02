"""Durable SQLite registry for canonical instruments and provider mappings.

SQLite is the initial single-backend persistence adapter. Use a persistent
volume for restart durability. Do not expose write operations publicly until
user authentication and per-instrument entitlements are enforced.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any
from uuid import UUID

from app.instrument_identity import CanonicalInstrument

_SCHEMA_VERSION = 1
_SQLITE_MAX_INTEGER = 9_223_372_036_854_775_807


class InstrumentRegistryError(RuntimeError):
    """Base error for durable instrument registry operations."""


class InstrumentRegistryConflict(InstrumentRegistryError):
    """An immutable canonical ID already exists with different metadata."""


class InstrumentMappingConflict(InstrumentRegistryError):
    """A provider instrument ID has an overlapping validity mapping."""


class UnknownCanonicalInstrument(InstrumentRegistryError):
    """A provider mapping references an unknown canonical instrument."""


class UnsupportedRegistrySchema(InstrumentRegistryError):
    """The database schema is newer than this backend understands."""


@dataclass(frozen=True, slots=True)
class ProviderInstrumentMapping:
    provider: str
    dataset: str
    publisher_id: int
    instrument_id: int
    raw_symbol: str
    valid_from_ns: int
    valid_to_ns: int | None
    canonical_id: str
    series_type: str = "contract"


def _normalize_mapping(
    mapping: ProviderInstrumentMapping,
) -> ProviderInstrumentMapping:
    for name in ("provider", "dataset", "raw_symbol", "series_type", "canonical_id"):
        value = getattr(mapping, name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} is required.")
    for name in ("publisher_id", "instrument_id", "valid_from_ns"):
        value = getattr(mapping, name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer.")
    if mapping.valid_to_ns is not None and (
        not isinstance(mapping.valid_to_ns, int)
        or isinstance(mapping.valid_to_ns, bool)
        or mapping.valid_to_ns <= mapping.valid_from_ns
    ):
        raise ValueError("valid_to_ns must be greater than valid_from_ns.")
    if mapping.valid_from_ns >= _SQLITE_MAX_INTEGER:
        raise ValueError("valid_from_ns exceeds the supported SQLite integer range.")
    if mapping.valid_to_ns is not None and mapping.valid_to_ns > _SQLITE_MAX_INTEGER:
        raise ValueError("valid_to_ns exceeds the supported SQLite integer range.")
    try:
        canonical_id = str(UUID(mapping.canonical_id.strip()))
    except (ValueError, AttributeError):
        raise ValueError("canonical_id must be a valid UUID.") from None
    return ProviderInstrumentMapping(
        provider=mapping.provider.strip().lower(),
        dataset=mapping.dataset.strip().upper(),
        publisher_id=mapping.publisher_id,
        instrument_id=mapping.instrument_id,
        raw_symbol=mapping.raw_symbol.strip().upper(),
        valid_from_ns=mapping.valid_from_ns,
        valid_to_ns=mapping.valid_to_ns,
        canonical_id=canonical_id,
        series_type=mapping.series_type.strip().lower(),
    )


class SQLiteInstrumentRegistry:
    """Thread-safe, transaction-guarded persistent registry.

    Every operation owns its SQLite connection. Writes use BEGIN IMMEDIATE so
    overlap checks and inserts are serialized across concurrent writers.
    Canonical instrument rows are immutable; create a new canonical identity
    for a genuinely different instrument rather than mutating an old identity.
    """

    def __init__(self, database_path: str, *, busy_timeout_ms: int = 10_000) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("database_path is required.")
        if database_path == ":memory:":
            raise ValueError("A file-backed database is required for durable registry storage.")
        if not isinstance(busy_timeout_ms, int) or isinstance(busy_timeout_ms, bool) or busy_timeout_ms < 1:
            raise ValueError("busy_timeout_ms must be a positive integer.")

        self.database_path = str(Path(database_path).expanduser())
        self.busy_timeout_ms = busy_timeout_ms
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

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

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            connection.execute("PRAGMA journal_mode = WAL")
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if version > _SCHEMA_VERSION:
                raise UnsupportedRegistrySchema(
                    f"Database schema {version} is newer than supported schema {_SCHEMA_VERSION}."
                )
            if version == 0:
                connection.executescript(
                    """
                    BEGIN IMMEDIATE;

                    CREATE TABLE canonical_instruments (
                        canonical_id TEXT PRIMARY KEY NOT NULL,
                        asset_class TEXT NOT NULL CHECK (
                            asset_class IN ('equity', 'etf', 'crypto', 'future', 'option', 'fx', 'index')
                        ),
                        instrument_type TEXT NOT NULL CHECK (
                            instrument_type IN ('stock', 'etf', 'spot', 'perpetual', 'future', 'option', 'fx_pair', 'index')
                        ),
                        symbol TEXT NOT NULL CHECK (length(symbol) BETWEEN 1 AND 64),
                        venue TEXT NOT NULL CHECK (length(venue) BETWEEN 1 AND 64),
                        is_active INTEGER NOT NULL CHECK (is_active IN (0, 1)),
                        payload_json TEXT NOT NULL,
                        created_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        CHECK (
                            (asset_class = 'equity' AND instrument_type = 'stock') OR
                            (asset_class = 'etf' AND instrument_type = 'etf') OR
                            (asset_class = 'crypto' AND instrument_type IN ('spot', 'perpetual')) OR
                            (asset_class = 'future' AND instrument_type = 'future') OR
                            (asset_class = 'option' AND instrument_type = 'option') OR
                            (asset_class = 'fx' AND instrument_type = 'fx_pair') OR
                            (asset_class = 'index' AND instrument_type = 'index')
                        )
                    );

                    CREATE INDEX idx_canonical_asset_venue_symbol
                    ON canonical_instruments(asset_class, venue, symbol);

                    CREATE INDEX idx_canonical_active_asset
                    ON canonical_instruments(is_active, asset_class);

                    CREATE TABLE provider_instrument_mappings (
                        provider TEXT NOT NULL CHECK (length(provider) > 0),
                        dataset TEXT NOT NULL CHECK (length(dataset) > 0),
                        publisher_id INTEGER NOT NULL CHECK (publisher_id >= 0),
                        instrument_id INTEGER NOT NULL CHECK (instrument_id >= 0),
                        raw_symbol TEXT NOT NULL CHECK (length(raw_symbol) > 0),
                        valid_from_ns INTEGER NOT NULL CHECK (valid_from_ns >= 0),
                        valid_to_ns INTEGER,
                        canonical_id TEXT NOT NULL,
                        series_type TEXT NOT NULL CHECK (length(series_type) > 0),
                        PRIMARY KEY (provider, dataset, publisher_id, instrument_id, valid_from_ns),
                        FOREIGN KEY (canonical_id) REFERENCES canonical_instruments(canonical_id)
                            ON UPDATE RESTRICT ON DELETE RESTRICT,
                        CHECK (valid_to_ns IS NULL OR valid_to_ns > valid_from_ns)
                    );

                    CREATE INDEX idx_provider_mapping_canonical
                    ON provider_instrument_mappings(canonical_id);

                    CREATE INDEX idx_provider_mapping_symbol
                    ON provider_instrument_mappings(provider, dataset, raw_symbol);

                    CREATE TRIGGER prevent_provider_mapping_overlap_insert
                    BEFORE INSERT ON provider_instrument_mappings
                    WHEN EXISTS (
                        SELECT 1
                        FROM provider_instrument_mappings AS existing
                        WHERE existing.provider = NEW.provider
                          AND existing.dataset = NEW.dataset
                          AND existing.publisher_id = NEW.publisher_id
                          AND existing.instrument_id = NEW.instrument_id
                          AND NEW.valid_from_ns < COALESCE(existing.valid_to_ns, 9223372036854775807)
                          AND COALESCE(NEW.valid_to_ns, 9223372036854775807) > existing.valid_from_ns
                    )
                    BEGIN
                        SELECT RAISE(ABORT, 'overlapping_provider_mapping');
                    END;

                    CREATE TRIGGER prevent_provider_mapping_overlap_update
                    BEFORE UPDATE ON provider_instrument_mappings
                    WHEN EXISTS (
                        SELECT 1
                        FROM provider_instrument_mappings AS existing
                        WHERE existing.rowid != OLD.rowid
                          AND existing.provider = NEW.provider
                          AND existing.dataset = NEW.dataset
                          AND existing.publisher_id = NEW.publisher_id
                          AND existing.instrument_id = NEW.instrument_id
                          AND NEW.valid_from_ns < COALESCE(existing.valid_to_ns, 9223372036854775807)
                          AND COALESCE(NEW.valid_to_ns, 9223372036854775807) > existing.valid_from_ns
                    )
                    BEGIN
                        SELECT RAISE(ABORT, 'overlapping_provider_mapping');
                    END;

                    CREATE TRIGGER canonical_instruments_are_immutable
                    BEFORE UPDATE ON canonical_instruments
                    BEGIN
                        SELECT RAISE(ABORT, 'canonical_instrument_is_immutable');
                    END;

                    PRAGMA user_version = 1;
                    COMMIT;
                    """
                )
        finally:
            connection.close()

    def register_instrument(self, instrument: CanonicalInstrument) -> bool:
        """Insert an immutable instrument. Identical repeats are idempotent."""
        if not isinstance(instrument, CanonicalInstrument):
            raise TypeError("instrument must be a CanonicalInstrument.")
        payload = json.dumps(
            instrument.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT payload_json FROM canonical_instruments WHERE canonical_id = ?",
                (instrument.canonical_id,),
            ).fetchone()
            if existing is not None:
                if existing["payload_json"] != payload:
                    raise InstrumentRegistryConflict(
                        "Canonical ID already exists with different immutable metadata."
                    )
                connection.commit()
                return False

            connection.execute(
                """
                INSERT INTO canonical_instruments (
                    canonical_id, asset_class, instrument_type, symbol, venue,
                    is_active, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    instrument.canonical_id,
                    instrument.asset_class,
                    instrument.instrument_type,
                    instrument.symbol,
                    instrument.venue,
                    int(instrument.is_active),
                    payload,
                ),
            )
            connection.commit()
            return True
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _instrument_from_row(row: sqlite3.Row | None) -> CanonicalInstrument | None:
        if row is None:
            return None
        return CanonicalInstrument(**json.loads(row["payload_json"]))

    def get_instrument(self, canonical_id: str) -> CanonicalInstrument | None:
        try:
            normalized_id = str(UUID(canonical_id))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("canonical_id must be a valid UUID.") from None
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT payload_json FROM canonical_instruments WHERE canonical_id = ?",
                (normalized_id,),
            ).fetchone()
            return self._instrument_from_row(row)
        finally:
            connection.close()

    def list_instruments(
        self,
        *,
        asset_class: str | None = None,
        venue: str | None = None,
        symbol: str | None = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CanonicalInstrument]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000.")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise ValueError("offset must be a non-negative integer.")
        if not isinstance(active_only, bool):
            raise ValueError("active_only must be a boolean.")

        clauses: list[str] = []
        parameters: list[Any] = []
        if active_only:
            clauses.append("is_active = 1")
        if asset_class is not None:
            if not isinstance(asset_class, str) or not asset_class.strip():
                raise ValueError("asset_class must be non-empty when supplied.")
            clauses.append("asset_class = ?")
            parameters.append(asset_class.strip().lower())
        if venue is not None:
            if not isinstance(venue, str) or not venue.strip():
                raise ValueError("venue must be non-empty when supplied.")
            clauses.append("venue = ?")
            parameters.append(venue.strip().upper())
        if symbol is not None:
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError("symbol must be non-empty when supplied.")
            clauses.append("symbol = ?")
            parameters.append(symbol.strip().upper())

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        connection = self._connect()
        try:
            rows = connection.execute(
                f"""
                SELECT payload_json FROM canonical_instruments
                {where}
                ORDER BY asset_class, venue, symbol, canonical_id
                LIMIT ? OFFSET ?
                """,
                (*parameters, limit, offset),
            ).fetchall()
            return [
                instrument
                for row in rows
                if (instrument := self._instrument_from_row(row)) is not None
            ]
        finally:
            connection.close()

    def add_provider_mapping(self, mapping: ProviderInstrumentMapping) -> bool:
        """Add a point-in-time provider mapping; exact repeats are idempotent.

        Validity is [valid_from_ns, valid_to_ns). Any overlap for the same
        provider/dataset/publisher/instrument key is rejected, even if the
        symbol text happens to match. Adjacent windows are allowed.
        """
        normalized = _normalize_mapping(mapping)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            exact = connection.execute(
                """
                SELECT 1 FROM provider_instrument_mappings
                WHERE provider = ? AND dataset = ? AND publisher_id = ?
                  AND instrument_id = ? AND valid_from_ns = ?
                  AND valid_to_ns IS ? AND canonical_id = ?
                  AND raw_symbol = ? AND series_type = ?
                """,
                (
                    normalized.provider, normalized.dataset, normalized.publisher_id,
                    normalized.instrument_id, normalized.valid_from_ns,
                    normalized.valid_to_ns, normalized.canonical_id,
                    normalized.raw_symbol, normalized.series_type,
                ),
            ).fetchone()
            if exact is not None:
                connection.commit()
                return False

            try:
                connection.execute(
                    """
                    INSERT INTO provider_instrument_mappings (
                        provider, dataset, publisher_id, instrument_id, raw_symbol,
                        valid_from_ns, valid_to_ns, canonical_id, series_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        normalized.provider, normalized.dataset, normalized.publisher_id,
                        normalized.instrument_id, normalized.raw_symbol,
                        normalized.valid_from_ns, normalized.valid_to_ns,
                        normalized.canonical_id, normalized.series_type,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                message = str(exc)
                if "FOREIGN KEY" in message:
                    raise UnknownCanonicalInstrument(
                        "Provider mapping references an unregistered canonical instrument."
                    ) from exc
                if "overlapping_provider_mapping" in message or "UNIQUE constraint" in message:
                    raise InstrumentMappingConflict(
                        "Provider instrument mapping overlaps an existing validity window."
                    ) from exc
                raise
            connection.commit()
            return True
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _mapping_from_row(row: sqlite3.Row | None) -> ProviderInstrumentMapping | None:
        if row is None:
            return None
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

    def resolve_provider_mapping(
        self,
        *,
        provider: str,
        dataset: str,
        publisher_id: int,
        instrument_id: int,
        timestamp_ns: int,
    ) -> ProviderInstrumentMapping | None:
        if not isinstance(timestamp_ns, int) or isinstance(timestamp_ns, bool) or timestamp_ns < 0:
            raise ValueError("timestamp_ns must be a non-negative integer.")
        if not isinstance(provider, str) or not provider.strip():
            raise ValueError("provider is required.")
        if not isinstance(dataset, str) or not dataset.strip():
            raise ValueError("dataset is required.")
        for name, value in (("publisher_id", publisher_id), ("instrument_id", instrument_id)):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer.")

        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT * FROM provider_instrument_mappings
                WHERE provider = ? AND dataset = ? AND publisher_id = ?
                  AND instrument_id = ? AND valid_from_ns <= ?
                  AND (valid_to_ns IS NULL OR ? < valid_to_ns)
                ORDER BY valid_from_ns DESC LIMIT 2
                """,
                (
                    provider.strip().lower(), dataset.strip().upper(),
                    publisher_id, instrument_id, timestamp_ns, timestamp_ns,
                ),
            ).fetchall()
            if len(rows) > 1:
                raise InstrumentRegistryError(
                    "Registry invariant violated: multiple provider mappings resolve at one timestamp."
                )
            return self._mapping_from_row(rows[0] if rows else None)
        finally:
            connection.close()

    def list_provider_mappings(
        self, canonical_id: str
    ) -> list[ProviderInstrumentMapping]:
        try:
            normalized_id = str(UUID(canonical_id))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("canonical_id must be a valid UUID.") from None
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT * FROM provider_instrument_mappings
                WHERE canonical_id = ?
                ORDER BY provider, dataset, publisher_id, instrument_id, valid_from_ns
                """,
                (normalized_id,),
            ).fetchall()
            return [
                mapping
                for row in rows
                if (mapping := self._mapping_from_row(row)) is not None
            ]
        finally:
            connection.close()
