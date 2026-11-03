"""Durable SQLite storage for account-wide price-alert zones.

The store is intentionally not exposed through HTTP routes until verified
Firebase identity and instrument entitlements are enforced by the API layer.
The account quota is enforced by a SQLite trigger as well as by the repository
transaction, so direct SQL inserts cannot bypass the five-zone limit.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import sqlite3
from uuid import UUID, uuid4

from app.alerts import (
    AlertZoneQuotaExceeded,
    AlertZoneValidationError,
    validate_zone_creation,
)

_ALLOWED_STATUSES = frozenset({"active", "paused", "triggered", "delivery_failed"})


class AlertZoneUnknownInstrument(ValueError):
    """The canonical instrument does not exist in the instrument registry."""


@dataclass(frozen=True, slots=True)
class StoredPriceAlertZone:
    zone_id: str
    owner_id: str
    canonical_instrument_id: str
    lower_price: Decimal
    upper_price: Decimal
    status: str
    created_at_utc: str
    deleted_at_utc: str | None


class SQLitePriceAlertStore:
    """File-backed, transaction-safe alert-zone repository.

    Use the same database path as SQLiteInstrumentRegistry so foreign keys
    can bind every alert to a registered canonical instrument. SQLite
    BEGIN IMMEDIATE serializes quota checks and inserts across writers.
    """

    def __init__(self, database_path: str, *, busy_timeout_ms: int = 10_000) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("database_path is required.")
        if database_path == ":memory:":
            raise ValueError("A file-backed database is required for durable alerts.")
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS price_alert_zones (
                    zone_id TEXT PRIMARY KEY NOT NULL,
                    owner_id TEXT NOT NULL CHECK (length(trim(owner_id)) > 0),
                    canonical_instrument_id TEXT NOT NULL,
                    lower_price TEXT NOT NULL,
                    upper_price TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('active', 'paused', 'triggered', 'delivery_failed')
                    ),
                    created_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    deleted_at_utc TEXT,
                    FOREIGN KEY (canonical_instrument_id)
                        REFERENCES canonical_instruments(canonical_id)
                        ON UPDATE RESTRICT ON DELETE RESTRICT
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_price_alert_owner_saved
                ON price_alert_zones(owner_id, deleted_at_utc, created_at_utc)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_price_alert_instrument_active
                ON price_alert_zones(canonical_instrument_id, status, deleted_at_utc)
                """
            )
            connection.execute(
                """
                CREATE TRIGGER IF NOT EXISTS enforce_price_alert_account_quota
                BEFORE INSERT ON price_alert_zones
                WHEN (
                    SELECT COUNT(*) FROM price_alert_zones
                    WHERE owner_id = NEW.owner_id AND deleted_at_utc IS NULL
                ) >= 5
                BEGIN
                    SELECT RAISE(ABORT, 'alert_zone_account_quota_exceeded');
                END
                """
            )
        finally:
            connection.close()

    @staticmethod
    def _normalize_owner(owner_id: str) -> str:
        if not isinstance(owner_id, str) or not owner_id.strip():
            raise AlertZoneValidationError("owner_id is required.")
        return owner_id.strip()

    @staticmethod
    def _normalize_canonical_id(canonical_instrument_id: str) -> str:
        try:
            return str(UUID(canonical_instrument_id))
        except (ValueError, TypeError, AttributeError):
            raise AlertZoneValidationError(
                "canonical_instrument_id must be a valid UUID."
            ) from None

    @staticmethod
    def _zone_from_row(row: sqlite3.Row) -> StoredPriceAlertZone:
        return StoredPriceAlertZone(
            zone_id=row["zone_id"],
            owner_id=row["owner_id"],
            canonical_instrument_id=row["canonical_instrument_id"],
            lower_price=Decimal(row["lower_price"]),
            upper_price=Decimal(row["upper_price"]),
            status=row["status"],
            created_at_utc=row["created_at_utc"],
            deleted_at_utc=row["deleted_at_utc"],
        )

    def create_zone(
        self,
        *,
        owner_id: str,
        canonical_instrument_id: str,
        lower_price: Decimal | str | int | float,
        upper_price: Decimal | str | int | float,
    ) -> StoredPriceAlertZone:
        """Create a zone, atomically enforcing five saved zones account-wide."""
        owner = self._normalize_owner(owner_id)
        canonical_id = self._normalize_canonical_id(canonical_instrument_id)
        candidate = validate_zone_creation(
            owner_id=owner,
            canonical_instrument_id=canonical_id,
            lower_price=lower_price,
            upper_price=upper_price,
            existing_zones=(),
        )
        zone_id = str(uuid4())
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            saved_count = connection.execute(
                """
                SELECT COUNT(*) FROM price_alert_zones
                WHERE owner_id = ? AND deleted_at_utc IS NULL
                """,
                (owner,),
            ).fetchone()[0]
            if saved_count >= 5:
                raise AlertZoneQuotaExceeded(
                    "An account can have at most 5 saved alert zones across all instruments."
                )
            try:
                connection.execute(
                    """
                    INSERT INTO price_alert_zones (
                        zone_id, owner_id, canonical_instrument_id,
                        lower_price, upper_price, status
                    ) VALUES (?, ?, ?, ?, ?, 'active')
                    """,
                    (
                        zone_id, owner, canonical_id,
                        format(candidate.lower_price, "f"),
                        format(candidate.upper_price, "f"),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                message = str(exc)
                if "alert_zone_account_quota_exceeded" in message:
                    raise AlertZoneQuotaExceeded(
                        "An account can have at most 5 saved alert zones across all instruments."
                    ) from exc
                if "FOREIGN KEY" in message:
                    raise AlertZoneUnknownInstrument(
                        "The canonical instrument is not registered."
                    ) from exc
                raise
            row = connection.execute(
                "SELECT * FROM price_alert_zones WHERE zone_id = ?", (zone_id,)
            ).fetchone()
            connection.commit()
            return self._zone_from_row(row)
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def list_zones(
        self, *, owner_id: str, include_deleted: bool = False
    ) -> list[StoredPriceAlertZone]:
        owner = self._normalize_owner(owner_id)
        if not isinstance(include_deleted, bool):
            raise ValueError("include_deleted must be a boolean.")
        where = "" if include_deleted else "AND deleted_at_utc IS NULL"
        connection = self._connect()
        try:
            rows = connection.execute(
                f"""
                SELECT * FROM price_alert_zones
                WHERE owner_id = ? {where}
                ORDER BY created_at_utc, zone_id
                """,
                (owner,),
            ).fetchall()
            return [self._zone_from_row(row) for row in rows]
        finally:
            connection.close()

    def set_status(self, *, owner_id: str, zone_id: str, status: str) -> bool:
        owner = self._normalize_owner(owner_id)
        if status not in _ALLOWED_STATUSES:
            raise ValueError("Unsupported alert-zone status.")
        try:
            normalized_zone_id = str(UUID(zone_id))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("zone_id must be a valid UUID.") from None
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE price_alert_zones SET status = ?
                WHERE zone_id = ? AND owner_id = ? AND deleted_at_utc IS NULL
                """,
                (status, normalized_zone_id, owner),
            )
            connection.commit()
            return cursor.rowcount == 1
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def delete_zone(self, *, owner_id: str, zone_id: str) -> bool:
        """Soft-delete a zone; only this explicit action releases its quota slot."""
        owner = self._normalize_owner(owner_id)
        try:
            normalized_zone_id = str(UUID(zone_id))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("zone_id must be a valid UUID.") from None
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE price_alert_zones SET deleted_at_utc = CURRENT_TIMESTAMP
                WHERE zone_id = ? AND owner_id = ? AND deleted_at_utc IS NULL
                """,
                (normalized_zone_id, owner),
            )
            connection.commit()
            return cursor.rowcount == 1
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()
