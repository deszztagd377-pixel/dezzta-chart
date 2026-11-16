"""Append-only, per-domain SQLite schema migration ledger.

This ledger is a foundation primitive. Existing stores must be adopted one by
one with an explicit baseline before the ledger can govern their migrations.
"""
from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
import re
from pathlib import Path
import sqlite3

_COMPONENT = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
_MIGRATION_ID = re.compile(r"^[a-z0-9][a-z0-9_.-]{1,127}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class SchemaMigrationError(RuntimeError):
    """Base error for schema migration ledger failures."""


class SchemaMigrationConflict(SchemaMigrationError):
    """A migration identity or checksum conflicts with its recorded history."""


class SchemaMigrationOrderError(SchemaMigrationError):
    """A migration would skip, reverse, or downgrade a component schema."""


def sha256_migration(source: str | bytes) -> str:
    """Return the stable SHA-256 checksum for a migration source artifact."""
    if isinstance(source, str):
        source = source.encode("utf-8")
    if not isinstance(source, bytes) or not source:
        raise ValueError("migration source must be non-empty text or bytes.")
    return hashlib.sha256(source).hexdigest()


def schema_fingerprint(
    connection: sqlite3.Connection, table_names: tuple[str, ...] | list[str]
) -> str:
    """Fingerprint selected SQLite tables plus their indexes and triggers."""
    if not isinstance(connection, sqlite3.Connection):
        raise ValueError("connection must be an active SQLite connection.")
    if (
        not isinstance(table_names, (tuple, list))
        or not table_names
        or any(
            not isinstance(name, str)
            or not re.fullmatch(r"[a-z][a-z0-9_]{0,127}", name)
            for name in table_names
        )
        or len(set(table_names)) != len(table_names)
    ):
        raise ValueError("table_names must be unique lowercase SQLite identifiers.")
    placeholders = ",".join("?" for _ in table_names)
    objects = connection.execute(
        f"""
        SELECT type, name, tbl_name, COALESCE(sql, '')
        FROM sqlite_master
        WHERE type IN ('table', 'index', 'trigger')
          AND tbl_name IN ({placeholders})
          AND name NOT LIKE 'sqlite_%'
        ORDER BY type, name
        """,
        tuple(table_names),
    ).fetchall()
    found_tables = {row[2] for row in objects if row[0] == "table"}
    if found_tables != set(table_names):
        missing = sorted(set(table_names) - found_tables)
        raise SchemaMigrationError(
            "Cannot fingerprint missing schema tables: " + ", ".join(missing)
        )
    columns = {}
    for table_name in sorted(table_names):
        # Identifier interpolation is safe after the strict allow-list above.
        columns[table_name] = [
            tuple(row)
            for row in connection.execute(
                f'PRAGMA table_xinfo("{table_name}")'
            ).fetchall()
        ]
    payload = {
        "objects": [tuple(row) for row in objects],
        "columns": columns,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class SQLiteSchemaMigrationLedger:
    """Append-only migration history shared by all domains in one SQLite file.

    Migration callbacks run inside the same BEGIN IMMEDIATE transaction as
    their ledger insert. Callbacks must use connection.execute/executemany and
    must not call executescript(), commit(), or open a second connection.
    """

    def __init__(self, database_path: str, *, busy_timeout_ms: int = 10_000) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("database_path is required.")
        if database_path == ":memory:":
            raise ValueError("A file-backed database is required for durable schema history.")
        if (
            not isinstance(busy_timeout_ms, int)
            or isinstance(busy_timeout_ms, bool)
            or busy_timeout_ms < 1
        ):
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
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS application_schema_migrations (
                    component TEXT NOT NULL,
                    version INTEGER NOT NULL CHECK(version >= 1),
                    migration_id TEXT NOT NULL,
                    checksum_sha256 TEXT NOT NULL CHECK(length(checksum_sha256) = 64),
                    applied_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(component, version),
                    UNIQUE(component, migration_id)
                )
                """
            )
            connection.execute(
                """
                CREATE TRIGGER IF NOT EXISTS application_schema_migrations_no_update
                BEFORE UPDATE ON application_schema_migrations
                BEGIN
                    SELECT RAISE(ABORT, 'schema_migration_history_is_append_only');
                END
                """
            )
            connection.execute(
                """
                CREATE TRIGGER IF NOT EXISTS application_schema_migrations_no_delete
                BEFORE DELETE ON application_schema_migrations
                BEGIN
                    SELECT RAISE(ABORT, 'schema_migration_history_is_append_only');
                END
                """
            )
            connection.commit()
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _validate_identity(
        component: str, version: int, migration_id: str, checksum_sha256: str
    ) -> tuple[str, int, str, str]:
        if not isinstance(component, str) or not _COMPONENT.fullmatch(component):
            raise ValueError("component must be a lowercase stable identifier.")
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            raise ValueError("version must be a positive integer.")
        if not isinstance(migration_id, str) or not _MIGRATION_ID.fullmatch(migration_id):
            raise ValueError("migration_id must be a stable lowercase identifier.")
        if not isinstance(checksum_sha256, str) or not _SHA256.fullmatch(checksum_sha256):
            raise ValueError("checksum_sha256 must be a lowercase SHA-256 hex digest.")
        return component, version, migration_id, checksum_sha256

    def current_version(self, component: str) -> int:
        if not isinstance(component, str) or not _COMPONENT.fullmatch(component):
            raise ValueError("component must be a lowercase stable identifier.")
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT MAX(version) AS version
                FROM application_schema_migrations WHERE component = ?
                """,
                (component,),
            ).fetchone()
            return 0 if row["version"] is None else int(row["version"])
        finally:
            connection.close()

    def record_baseline(
        self, *, component: str, version: int, migration_id: str,
        checksum_sha256: str,
    ) -> bool:
        """Adopt an already-existing schema without claiming its older history."""
        component, version, migration_id, checksum_sha256 = self._validate_identity(
            component, version, migration_id, checksum_sha256
        )
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                """
                SELECT version, migration_id, checksum_sha256
                FROM application_schema_migrations
                WHERE component = ? ORDER BY version
                """,
                (component,),
            ).fetchall()
            if rows:
                if (
                    len(rows) == 1
                    and int(rows[0]["version"]) == version
                    and rows[0]["migration_id"] == migration_id
                    and rows[0]["checksum_sha256"] == checksum_sha256
                ):
                    connection.commit()
                    return False
                raise SchemaMigrationConflict(
                    f"Component {component} already has migration history; baseline adoption is not allowed."
                )
            if version != 1:
                raise SchemaMigrationOrderError(
                    "A new ledger component must start with a baseline at version 1. "
                    "Legacy schema versions require an explicit adoption plan."
                )
            connection.execute(
                """
                INSERT INTO application_schema_migrations
                    (component, version, migration_id, checksum_sha256)
                VALUES (?, ?, ?, ?)
                """,
                (component, version, migration_id, checksum_sha256),
            )
            connection.commit()
            return True
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def apply_migration(
        self, *, component: str, version: int, migration_id: str,
        checksum_sha256: str, apply: Callable[[sqlite3.Connection], None],
    ) -> bool:
        """Apply exactly the next migration and record it atomically."""
        component, version, migration_id, checksum_sha256 = self._validate_identity(
            component, version, migration_id, checksum_sha256
        )
        if not callable(apply):
            raise ValueError("apply must be a migration callback.")
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                """
                SELECT version, migration_id, checksum_sha256
                FROM application_schema_migrations
                WHERE component = ? ORDER BY version
                """,
                (component,),
            ).fetchall()
            current = 0 if not rows else int(rows[-1]["version"])
            if version <= current:
                existing = next((row for row in rows if int(row["version"]) == version), None)
                if (
                    existing is not None
                    and existing["migration_id"] == migration_id
                    and existing["checksum_sha256"] == checksum_sha256
                ):
                    connection.commit()
                    return False
                raise SchemaMigrationConflict(
                    f"Component {component} version {version} conflicts with recorded history."
                )
            if version != current + 1:
                raise SchemaMigrationOrderError(
                    f"Component {component} must migrate from {current} to {current + 1}, not {version}."
                )
            apply(connection)
            connection.execute(
                """
                INSERT INTO application_schema_migrations
                    (component, version, migration_id, checksum_sha256)
                VALUES (?, ?, ?, ?)
                """,
                (component, version, migration_id, checksum_sha256),
            )
            connection.commit()
            return True
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()
