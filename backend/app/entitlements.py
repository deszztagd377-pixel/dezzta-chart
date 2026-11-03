"""Durable, deny-by-default per-account canonical-instrument entitlements.

This adapter shares the instrument registry SQLite database. Grants are
internal administrative operations only; no client-facing grant endpoint is
provided. Every authorization decision is scoped to a verified account subject
and an immutable canonical instrument UUID.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
from uuid import UUID


class EntitlementValidationError(ValueError):
    """An account or canonical instrument identifier is invalid."""


class EntitlementUnknownInstrument(ValueError):
    """The requested canonical instrument is not registered."""


@dataclass(frozen=True, slots=True)
class InstrumentEntitlement:
    subject: str
    canonical_instrument_id: str
    status: str
    granted_at_utc: str
    revoked_at_utc: str | None


class SQLiteInstrumentEntitlementStore:
    """SQLite persistence for explicit user-to-instrument access grants."""

    def __init__(self, database_path: str, *, busy_timeout_ms: int = 10_000) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("database_path is required.")
        if database_path == ":memory:":
            raise ValueError("A file-backed database is required for durable entitlements.")
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
                CREATE TABLE IF NOT EXISTS user_instrument_entitlements (
                    subject TEXT NOT NULL CHECK (length(trim(subject)) BETWEEN 1 AND 256),
                    canonical_instrument_id TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('active', 'revoked')),
                    granted_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    revoked_at_utc TEXT,
                    PRIMARY KEY (subject, canonical_instrument_id),
                    FOREIGN KEY (canonical_instrument_id)
                        REFERENCES canonical_instruments(canonical_id)
                        ON UPDATE RESTRICT ON DELETE RESTRICT,
                    CHECK (
                        (status = 'active' AND revoked_at_utc IS NULL)
                        OR (status = 'revoked' AND revoked_at_utc IS NOT NULL)
                    )
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_entitlements_subject_status
                ON user_instrument_entitlements(subject, status, canonical_instrument_id)
                """
            )
        finally:
            connection.close()

    @staticmethod
    def _normalize_subject(subject: str) -> str:
        if not isinstance(subject, str) or not subject.strip() or len(subject.strip()) > 256:
            raise EntitlementValidationError("A verified account subject is required.")
        return subject.strip()

    @staticmethod
    def _normalize_canonical_id(canonical_instrument_id: str) -> str:
        try:
            return str(UUID(canonical_instrument_id))
        except (ValueError, TypeError, AttributeError):
            raise EntitlementValidationError("canonical_instrument_id must be a valid UUID.") from None

    @staticmethod
    def _from_row(row: sqlite3.Row) -> InstrumentEntitlement:
        return InstrumentEntitlement(
            subject=row["subject"],
            canonical_instrument_id=row["canonical_instrument_id"],
            status=row["status"],
            granted_at_utc=row["granted_at_utc"],
            revoked_at_utc=row["revoked_at_utc"],
        )

    def grant(self, *, subject: str, canonical_instrument_id: str) -> InstrumentEntitlement:
        """Grant one canonical instrument; intended for trusted admin workflows."""
        normalized_subject = self._normalize_subject(subject)
        canonical_id = self._normalize_canonical_id(canonical_instrument_id)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            exists = connection.execute(
                "SELECT 1 FROM canonical_instruments WHERE canonical_id = ?",
                (canonical_id,),
            ).fetchone()
            if exists is None:
                raise EntitlementUnknownInstrument("The canonical instrument is not registered.")
            connection.execute(
                """
                INSERT INTO user_instrument_entitlements (
                    subject, canonical_instrument_id, status, granted_at_utc, revoked_at_utc
                ) VALUES (?, ?, 'active', CURRENT_TIMESTAMP, NULL)
                ON CONFLICT(subject, canonical_instrument_id) DO UPDATE SET
                    status = 'active',
                    granted_at_utc = CURRENT_TIMESTAMP,
                    revoked_at_utc = NULL
                """,
                (normalized_subject, canonical_id),
            )
            row = connection.execute(
                """
                SELECT * FROM user_instrument_entitlements
                WHERE subject = ? AND canonical_instrument_id = ?
                """,
                (normalized_subject, canonical_id),
            ).fetchone()
            connection.commit()
            return self._from_row(row)
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def revoke(self, *, subject: str, canonical_instrument_id: str) -> bool:
        normalized_subject = self._normalize_subject(subject)
        canonical_id = self._normalize_canonical_id(canonical_instrument_id)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE user_instrument_entitlements
                SET status = 'revoked', revoked_at_utc = CURRENT_TIMESTAMP
                WHERE subject = ? AND canonical_instrument_id = ? AND status = 'active'
                """,
                (normalized_subject, canonical_id),
            )
            connection.commit()
            return cursor.rowcount == 1
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def has_access(self, *, subject: str, canonical_instrument_id: str) -> bool:
        normalized_subject = self._normalize_subject(subject)
        canonical_id = self._normalize_canonical_id(canonical_instrument_id)
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT 1 FROM user_instrument_entitlements
                WHERE subject = ? AND canonical_instrument_id = ? AND status = 'active'
                """,
                (normalized_subject, canonical_id),
            ).fetchone()
            return row is not None
        finally:
            connection.close()

    def list_for_subject(self, *, subject: str, include_revoked: bool = False) -> list[InstrumentEntitlement]:
        normalized_subject = self._normalize_subject(subject)
        if not isinstance(include_revoked, bool):
            raise ValueError("include_revoked must be a boolean.")
        status_filter = "" if include_revoked else "AND status = 'active'"
        connection = self._connect()
        try:
            rows = connection.execute(
                f"""
                SELECT * FROM user_instrument_entitlements
                WHERE subject = ? {status_filter}
                ORDER BY canonical_instrument_id
                """,
                (normalized_subject,),
            ).fetchall()
            return [self._from_row(row) for row in rows]
        finally:
            connection.close()
