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
class PriceAlertTriggerEvent:
    event_id: str
    zone_id: str
    owner_id: str
    canonical_instrument_id: str
    trigger_price: Decimal
    provider_event_id: str
    source_timestamp_ns: int
    delivery_status: str


class AlertMarketEventRejected(ValueError):
    """A market event is stale, out of order, or invalid for alert evaluation."""


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
                CREATE TABLE IF NOT EXISTS price_alert_evaluation_state (
                    zone_id TEXT PRIMARY KEY NOT NULL,
                    is_inside INTEGER NOT NULL CHECK (is_inside IN (0, 1)),
                    last_source_timestamp_ns INTEGER NOT NULL,
                    FOREIGN KEY (zone_id) REFERENCES price_alert_zones(zone_id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS price_alert_market_cursor (
                    canonical_instrument_id TEXT PRIMARY KEY NOT NULL,
                    last_source_timestamp_ns INTEGER NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS price_alert_processed_events (
                    canonical_instrument_id TEXT NOT NULL,
                    provider_event_id TEXT NOT NULL,
                    source_timestamp_ns INTEGER NOT NULL,
                    PRIMARY KEY (canonical_instrument_id, provider_event_id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS price_alert_trigger_events (
                    event_id TEXT PRIMARY KEY NOT NULL,
                    zone_id TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    canonical_instrument_id TEXT NOT NULL,
                    trigger_price TEXT NOT NULL,
                    provider_event_id TEXT NOT NULL,
                    source_timestamp_ns INTEGER NOT NULL,
                    delivery_status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (delivery_status IN ('pending', 'delivered', 'failed')),
                    created_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (zone_id, provider_event_id),
                    FOREIGN KEY (zone_id) REFERENCES price_alert_zones(zone_id)
                        ON DELETE RESTRICT
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_price_alert_delivery_pending
                ON price_alert_trigger_events(delivery_status, created_at_utc)
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

    def evaluate_market_price(
        self,
        *,
        canonical_instrument_id: str,
        price: Decimal | str | int | float,
        provider_event_id: str,
        source_timestamp_ns: int,
        now_ns: int,
        max_age_ns: int = 5_000_000_000,
        future_skew_ns: int = 1_000_000_000,
    ) -> list[PriceAlertTriggerEvent]:
        """Persist one trusted provider price event and emit entry events once.

        This internal method must only be called after the ingestion layer has
        authenticated provider provenance and resolved the canonical instrument.
        It is deliberately not exposed as an HTTP endpoint. Delivery remains a
        separate pending outbox responsibility.
        """
        canonical_id = self._normalize_canonical_id(canonical_instrument_id)
        try:
            parsed_price = Decimal(str(price))
        except (ArithmeticError, TypeError, ValueError):
            raise AlertMarketEventRejected("Market price must be a valid decimal.") from None
        if not parsed_price.is_finite():
            raise AlertMarketEventRejected("Market price must be finite.")
        if (
            not isinstance(provider_event_id, str)
            or not provider_event_id.strip()
            or len(provider_event_id) > 256
        ):
            raise AlertMarketEventRejected("provider_event_id is invalid.")
        numeric_values = (source_timestamp_ns, now_ns, max_age_ns, future_skew_ns)
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in numeric_values
        ) or source_timestamp_ns == 0 or max_age_ns == 0:
            raise AlertMarketEventRejected("Market event timestamps and age limits are invalid.")
        age_ns = now_ns - source_timestamp_ns
        if age_ns > max_age_ns or age_ns < -future_skew_ns:
            raise AlertMarketEventRejected("Market event is stale or from the future.")

        connection = self._connect()
        triggered: list[PriceAlertTriggerEvent] = []
        try:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                SELECT last_source_timestamp_ns
                FROM price_alert_market_cursor
                WHERE canonical_instrument_id = ?
                """,
                (canonical_id,),
            ).fetchone()
            if cursor is not None and source_timestamp_ns < cursor["last_source_timestamp_ns"]:
                raise AlertMarketEventRejected("Out-of-order market event was rejected.")

            inserted = connection.execute(
                """
                INSERT OR IGNORE INTO price_alert_processed_events (
                    canonical_instrument_id, provider_event_id, source_timestamp_ns
                ) VALUES (?, ?, ?)
                """,
                (canonical_id, provider_event_id.strip(), source_timestamp_ns),
            )
            if inserted.rowcount == 0:
                connection.commit()
                return []

            connection.execute(
                """
                INSERT INTO price_alert_market_cursor (
                    canonical_instrument_id, last_source_timestamp_ns
                ) VALUES (?, ?)
                ON CONFLICT(canonical_instrument_id) DO UPDATE SET
                    last_source_timestamp_ns = MAX(
                        price_alert_market_cursor.last_source_timestamp_ns,
                        excluded.last_source_timestamp_ns
                    )
                """,
                (canonical_id, source_timestamp_ns),
            )
            zones = connection.execute(
                """
                SELECT * FROM price_alert_zones
                WHERE canonical_instrument_id = ?
                  AND deleted_at_utc IS NULL
                  AND status IN ('active', 'triggered', 'paused')
                ORDER BY created_at_utc, zone_id
                """,
                (canonical_id,),
            ).fetchall()
            for zone in zones:
                is_inside = (
                    Decimal(zone["lower_price"])
                    <= parsed_price
                    <= Decimal(zone["upper_price"])
                )
                previous = connection.execute(
                    """
                    SELECT is_inside FROM price_alert_evaluation_state
                    WHERE zone_id = ?
                    """,
                    (zone["zone_id"],),
                ).fetchone()
                has_baseline = previous is not None
                was_inside = bool(previous["is_inside"]) if has_baseline else False

                # The first observation establishes a baseline; it is not
                # evidence that the market entered the zone.
                if is_inside and has_baseline and not was_inside and zone["status"] != "paused":
                    event_id = str(uuid4())
                    connection.execute(
                        """
                        INSERT INTO price_alert_trigger_events (
                            event_id, zone_id, owner_id, canonical_instrument_id,
                            trigger_price, provider_event_id, source_timestamp_ns
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            event_id, zone["zone_id"], zone["owner_id"], canonical_id,
                            format(parsed_price, "f"), provider_event_id.strip(),
                            source_timestamp_ns,
                        ),
                    )
                    connection.execute(
                        "UPDATE price_alert_zones SET status = 'triggered' WHERE zone_id = ?",
                        (zone["zone_id"],),
                    )
                    triggered.append(
                        PriceAlertTriggerEvent(
                            event_id=event_id,
                            zone_id=zone["zone_id"],
                            owner_id=zone["owner_id"],
                            canonical_instrument_id=canonical_id,
                            trigger_price=parsed_price,
                            provider_event_id=provider_event_id.strip(),
                            source_timestamp_ns=source_timestamp_ns,
                            delivery_status="pending",
                        )
                    )
                elif not is_inside and was_inside:
                    connection.execute(
                        "UPDATE price_alert_zones SET status = 'active' WHERE zone_id = ?",
                        (zone["zone_id"],),
                    )

                connection.execute(
                    """
                    INSERT INTO price_alert_evaluation_state (
                        zone_id, is_inside, last_source_timestamp_ns
                    ) VALUES (?, ?, ?)
                    ON CONFLICT(zone_id) DO UPDATE SET
                        is_inside = excluded.is_inside,
                        last_source_timestamp_ns = excluded.last_source_timestamp_ns
                    """,
                    (zone["zone_id"], int(is_inside), source_timestamp_ns),
                )
            connection.commit()
            return triggered
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def list_pending_trigger_events(self, *, limit: int = 100) -> list[PriceAlertTriggerEvent]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000.")
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT * FROM price_alert_trigger_events
                WHERE delivery_status = 'pending'
                ORDER BY created_at_utc, event_id
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [
                PriceAlertTriggerEvent(
                    event_id=row["event_id"],
                    zone_id=row["zone_id"],
                    owner_id=row["owner_id"],
                    canonical_instrument_id=row["canonical_instrument_id"],
                    trigger_price=Decimal(row["trigger_price"]),
                    provider_event_id=row["provider_event_id"],
                    source_timestamp_ns=row["source_timestamp_ns"],
                    delivery_status=row["delivery_status"],
                )
                for row in rows
            ]
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
