import sqlite3

import pytest

from app.schema_migrations import (
    SchemaMigrationConflict,
    SchemaMigrationOrderError,
    SQLiteSchemaMigrationLedger,
    schema_fingerprint,
    sha256_migration,
)


def test_baseline_is_adopted_once_and_idempotently(tmp_path):
    ledger = SQLiteSchemaMigrationLedger(str(tmp_path / "shared.sqlite3"))
    checksum = sha256_migration("legacy schema snapshot v1")

    assert ledger.record_baseline(
        component="alerts",
        version=1,
        migration_id="baseline-legacy-alerts-v1",
        checksum_sha256=checksum,
    ) is True
    assert ledger.record_baseline(
        component="alerts",
        version=1,
        migration_id="baseline-legacy-alerts-v1",
        checksum_sha256=checksum,
    ) is False
    assert ledger.current_version("alerts") == 1


def test_baseline_refuses_to_overwrite_existing_component_history(tmp_path):
    ledger = SQLiteSchemaMigrationLedger(str(tmp_path / "shared.sqlite3"))
    ledger.record_baseline(
        component="alerts",
        version=1,
        migration_id="baseline-alerts-v1",
        checksum_sha256=sha256_migration("schema"),
    )
    with pytest.raises(SchemaMigrationConflict):
        ledger.record_baseline(
            component="alerts",
            version=1,
            migration_id="different-baseline",
            checksum_sha256=sha256_migration("different schema"),
        )


def test_migrations_are_sequential_and_atomic_with_schema_changes(tmp_path):
    path = str(tmp_path / "shared.sqlite3")
    ledger = SQLiteSchemaMigrationLedger(path)
    ledger.record_baseline(
        component="ohlcv",
        version=1,
        migration_id="baseline-ohlcv-v1",
        checksum_sha256=sha256_migration("ohlcv v1"),
    )

    def add_column(connection):
        connection.execute("CREATE TABLE migration_probe (value TEXT NOT NULL)")

    checksum = sha256_migration("CREATE TABLE migration_probe (value TEXT NOT NULL)")
    assert ledger.apply_migration(
        component="ohlcv",
        version=2,
        migration_id="ohlcv-v2-probe",
        checksum_sha256=checksum,
        apply=add_column,
    ) is True
    assert ledger.current_version("ohlcv") == 2
    assert ledger.apply_migration(
        component="ohlcv",
        version=2,
        migration_id="ohlcv-v2-probe",
        checksum_sha256=checksum,
        apply=add_column,
    ) is False

    connection = sqlite3.connect(path)
    try:
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='migration_probe'"
        ).fetchone()[0] == "migration_probe"
    finally:
        connection.close()


def test_migration_failure_rolls_back_schema_and_history(tmp_path):
    ledger = SQLiteSchemaMigrationLedger(str(tmp_path / "shared.sqlite3"))
    ledger.record_baseline(
        component="registry",
        version=1,
        migration_id="baseline-registry-v1",
        checksum_sha256=sha256_migration("registry v1"),
    )

    def fail_after_ddl(connection):
        connection.execute("CREATE TABLE should_rollback (value TEXT)")
        raise RuntimeError("migration failure")

    with pytest.raises(RuntimeError, match="migration failure"):
        ledger.apply_migration(
            component="registry",
            version=2,
            migration_id="registry-v2-failure",
            checksum_sha256=sha256_migration("failing migration"),
            apply=fail_after_ddl,
        )
    assert ledger.current_version("registry") == 1

    connection = sqlite3.connect(ledger.database_path)
    try:
        assert connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='should_rollback'"
        ).fetchone() is None
    finally:
        connection.close()


def test_migration_refuses_skipped_versions_and_checksum_changes(tmp_path):
    ledger = SQLiteSchemaMigrationLedger(str(tmp_path / "shared.sqlite3"))
    ledger.record_baseline(
        component="entitlements",
        version=1,
        migration_id="baseline-entitlements-v1",
        checksum_sha256=sha256_migration("entitlements v1"),
    )
    with pytest.raises(SchemaMigrationOrderError):
        ledger.apply_migration(
            component="entitlements",
            version=3,
            migration_id="entitlements-v3",
            checksum_sha256=sha256_migration("entitlements v3"),
            apply=lambda connection: None,
        )
    with pytest.raises(SchemaMigrationConflict):
        ledger.apply_migration(
            component="entitlements",
            version=1,
            migration_id="baseline-entitlements-v1",
            checksum_sha256=sha256_migration("tampered baseline"),
            apply=lambda connection: None,
        )


def test_migration_history_cannot_be_updated_or_deleted(tmp_path):
    path = str(tmp_path / "shared.sqlite3")
    ledger = SQLiteSchemaMigrationLedger(path)
    ledger.record_baseline(
        component="devices",
        version=1,
        migration_id="baseline-devices-v1",
        checksum_sha256=sha256_migration("devices v1"),
    )
    connection = sqlite3.connect(path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="schema_migration_history_is_append_only"):
            connection.execute(
                "UPDATE application_schema_migrations SET migration_id='rewritten' "
                "WHERE component='devices'"
            )
        with pytest.raises(sqlite3.IntegrityError, match="schema_migration_history_is_append_only"):
            connection.execute(
                "DELETE FROM application_schema_migrations WHERE component='devices'"
            )
    finally:
        connection.close()


def test_schema_ledger_rejects_invalid_identifiers_and_memory_database(tmp_path):
    with pytest.raises(ValueError):
        SQLiteSchemaMigrationLedger(":memory:")
    ledger = SQLiteSchemaMigrationLedger(str(tmp_path / "shared.sqlite3"))
    with pytest.raises(ValueError):
        ledger.record_baseline(
            component="Bad Name",
            version=1,
            migration_id="baseline-v1",
            checksum_sha256=sha256_migration("schema"),
        )


def test_schema_fingerprint_is_stable_and_changes_when_schema_changes(tmp_path):
    path = str(tmp_path / "fingerprint.sqlite3")
    ledger = SQLiteSchemaMigrationLedger(path)
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE sample_data (id INTEGER PRIMARY KEY, value TEXT)")
        first = schema_fingerprint(connection, ["sample_data"])
        second = schema_fingerprint(connection, ["sample_data"])
        assert first == second
        connection.execute("CREATE INDEX idx_sample_value ON sample_data(value)")
        changed = schema_fingerprint(connection, ["sample_data"])
        assert changed != first
    finally:
        connection.close()


def test_schema_fingerprint_rejects_missing_tables_and_unsafe_identifiers(tmp_path):
    path = str(tmp_path / "fingerprint.sqlite3")
    SQLiteSchemaMigrationLedger(path)
    connection = sqlite3.connect(path)
    try:
        with pytest.raises(Exception, match="missing schema tables"):
            schema_fingerprint(connection, ["missing_table"])
        with pytest.raises(ValueError, match="unique lowercase SQLite identifiers"):
            schema_fingerprint(connection, ["sample; DROP TABLE users"])
    finally:
        connection.close()
