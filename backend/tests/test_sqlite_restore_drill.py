import json
import shutil
import sqlite3
import pytest

from app.sqlite_restore_drill import _inventory, run_restore_drill

def _build_database(path):
    from decimal import Decimal
    from app.alert_store import SQLitePriceAlertStore
    from app.coverage_store import SQLiteCoverageTracker
    from app.entitlements import SQLiteInstrumentEntitlementStore
    from app.instrument_identity import CanonicalInstrument
    from app.instrument_registry import SQLiteInstrumentRegistry
    from app.ohlcv import OhlcvBar
    from app.ohlcv_store import SQLiteOhlcvStore

    canonical_id = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
    instrument = CanonicalInstrument(
        canonical_id=canonical_id, asset_class="equity", instrument_type="stock",
        symbol="MSFT", venue="XNAS", quote_currency="USD", tick_size="0.01",
    )
    SQLiteInstrumentRegistry(str(path)).register_instrument(instrument)
    SQLiteInstrumentEntitlementStore(str(path)).grant(
        subject="drill-test-subject", canonical_instrument_id=canonical_id,
    )
    SQLitePriceAlertStore(str(path)).create_zone(
        owner_id="drill-test-subject", canonical_instrument_id=canonical_id,
        lower_price="100.25", upper_price="110.75",
    )
    scope = ("test-provider", "TEST.DATA", 1, 9001, "contract", "MSFT")
    coverage = SQLiteCoverageTracker(str(path))
    coverage.add_covered(scope, 1000, 2000)
    coverage.add_gap(scope, 1400, 1600)
    bar = OhlcvBar(
        provider="test-provider", dataset="TEST.DATA", publisher_id=1,
        instrument_id=9001, raw_symbol="MSFT", series_type="contract",
        timeframe="1m", ts_start_ns=60_000_000_000,
        open=Decimal("100"), high=Decimal("103"), low=Decimal("99"),
        close=Decimal("101.000000000000000001"),
        volume=Decimal("12.500000000000000009"),
        ts_event_ns=1_790_000_000_123_456_789,
        ts_received_ns=1_790_000_000_123_456_799,
        sequence=1, sequence_origin="local", origin="provider", completeness="unknown",
    )
    assert SQLiteOhlcvStore(str(path)).apply(bar) == "inserted"

def test_restore_probe_reads_committed_write_from_a_fresh_read_only_connection(
    tmp_path, monkeypatch
):
    from app import sqlite_restore_drill

    restored = tmp_path / "restored.sqlite3"
    _build_database(restored)
    original_ro = sqlite_restore_drill._ro
    observed_probe_rows = []

    def inspect_committed_probe(path):
        connection = original_ro(path)
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            ("__dezzta_restore_drill_probe",),
        ).fetchone()
        if exists:
            row = connection.execute(
                "SELECT probe_id, checked_at_utc "
                "FROM __dezzta_restore_drill_probe"
            ).fetchone()
            observed_probe_rows.append(row is not None and bool(row["probe_id"]))
        else:
            observed_probe_rows.append(False)
        return connection

    monkeypatch.setattr(sqlite_restore_drill, "_ro", inspect_committed_probe)
    sqlite_restore_drill._write_probe(restored)

    assert observed_probe_rows == [True, False]
    with sqlite3.connect(restored) as db:
        assert db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            ("__dezzta_restore_drill_probe",),
        ).fetchone() is None


def test_restore_probe_cleans_committed_probe_if_readback_fails(tmp_path, monkeypatch):
    from app import sqlite_restore_drill

    restored = tmp_path / "restored.sqlite3"
    _build_database(restored)

    def fail_readback(_path):
        raise sqlite3.DatabaseError("injected committed readback failure")

    monkeypatch.setattr(sqlite_restore_drill, "_ro", fail_readback)
    with pytest.raises(
        sqlite3.DatabaseError, match="injected committed readback failure"
    ):
        sqlite_restore_drill._write_probe(restored)

    with sqlite3.connect(restored) as db:
        assert db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            ("__dezzta_restore_drill_probe",),
        ).fetchone() is None


def test_owner_device_restore_drill_checks_application_domains_and_redacts_paths(tmp_path):
    source = tmp_path / "live" / "application.sqlite3"
    backup = tmp_path / "backup" / "application-backup.sqlite3"
    restored = tmp_path / "fresh" / "application-restored.sqlite3"
    source.parent.mkdir()
    _build_database(source)
    source_before = source.read_bytes()

    report = run_restore_drill(source, backup, restored)

    assert report["status"] == "passed"
    assert report["integrity_check"] == "ok"
    assert report["foreign_key_errors"] == 0
    assert report["table_row_counts_match"] is True
    assert report["table_content_match"] is True
    assert report["schema_match"] is True
    assert len(report["application_content_sha256"]) == 64
    assert report["post_restore_write_read_cleanup"] == "passed"
    assert report["failed_checks"] == []
    report_without_hash = dict(report)
    report_hash = report_without_hash.pop("report_sha256")
    canonical = json.dumps(report_without_hash, sort_keys=True, separators=(",", ":"))
    import hashlib
    assert report_hash == hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert report["application_domain_readback"] == {
        "canonical_instruments": 1, "provider_mappings": 0,
        "entitlements": 1, "alert_zones": 1, "coverage_scopes": 1,
        "coverage_intervals": 2, "coverage_gaps": 1,
        "ohlcv_bars": 1, "ohlcv_series": 1, "outbox_high_water": 1,
    }
    assert source.read_bytes() == source_before
    assert backup.is_file() and restored.is_file()
    with sqlite3.connect(restored) as db:
        assert db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            ("__dezzta_restore_drill_probe",),
        ).fetchone() is None
    assert str(tmp_path) not in json.dumps(report)
    assert source.name not in json.dumps(report)
    assert backup.name not in json.dumps(report)
    assert restored.name not in json.dumps(report)
    assert report["source_role"] == "source"
    assert report["backup_role"] == "backup"
    assert report["restore_role"] == "restored_copy"
    assert "drill-test-subject" not in json.dumps(report)

@pytest.mark.parametrize("failing_publication", ["backup", "restore"])
def test_restore_drill_cleans_output_when_directory_fsync_fails_after_publish(
    tmp_path, monkeypatch, failing_publication
):
    from app import sqlite_backup

    source = tmp_path / "live.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    _build_database(source)
    source_before = source.read_bytes()
    original_fsync = sqlite_backup._fsync_directory
    calls = 0
    fail_on = 1 if failing_publication == "backup" else 2

    def fail_selected_directory_fsync(directory):
        nonlocal calls
        calls += 1
        if calls == fail_on:
            raise OSError("injected directory fsync failure")
        return original_fsync(directory)

    monkeypatch.setattr(
        sqlite_backup, "_fsync_directory", fail_selected_directory_fsync
    )

    with pytest.raises(OSError, match="injected directory fsync failure"):
        run_restore_drill(source, backup, restored)

    assert source.read_bytes() == source_before
    assert not backup.exists()
    assert not restored.exists()
    for output in (backup, restored):
        for suffix in ("-journal", "-wal", "-shm"):
            assert not (tmp_path / f"{output.name}{suffix}").exists()


def test_failed_restore_verification_removes_only_drill_created_outputs(tmp_path, monkeypatch):
    source = tmp_path / "live.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    _build_database(source)

    from app import sqlite_restore_drill
    original_inventory = sqlite_restore_drill._inventory
    calls = 0

    def fail_restored_inventory(path):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise sqlite3.DatabaseError("injected restore verification failure")
        return original_inventory(path)

    monkeypatch.setattr(sqlite_restore_drill, "_inventory", fail_restored_inventory)

    with pytest.raises(sqlite3.DatabaseError, match="injected restore verification failure"):
        run_restore_drill(source, backup, restored)

    assert source.is_file()
    assert not backup.exists()
    assert not restored.exists()
    for output in (backup, restored):
        for suffix in ("-journal", "-wal", "-shm"):
            assert not (tmp_path / f"{output.name}{suffix}").exists()


def test_restore_drill_refuses_existing_output_paths_without_overwriting(tmp_path):
    source = tmp_path / "live.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    _build_database(source)
    backup.write_bytes(b"keep-backup")
    restored.write_bytes(b"keep-restore")
    with pytest.raises(FileExistsError):
        run_restore_drill(source, backup, restored)
    assert backup.read_bytes() == b"keep-backup"
    assert restored.read_bytes() == b"keep-restore"



@pytest.mark.parametrize("symlink_role", ["backup", "restore"])
def test_restore_drill_refuses_dangling_symlink_output_paths(tmp_path, symlink_role):
    source = tmp_path / "live.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    target_dir = tmp_path / "outside"
    target_dir.mkdir()
    target = target_dir / "redirected.sqlite3"
    _build_database(source)
    source_before = source.read_bytes()

    symlink = backup if symlink_role == "backup" else restored
    symlink.symlink_to(target)

    with pytest.raises(ValueError, match="destination must not be a symbolic link"):
        run_restore_drill(source, backup, restored)

    assert symlink.is_symlink()
    assert not target.exists()
    assert source.read_bytes() == source_before
    assert not backup.is_file()
    assert not restored.is_file()


def test_restore_inventory_detects_same_count_row_content_changes(tmp_path):
    source = tmp_path / "source.sqlite3"
    altered = tmp_path / "altered.sqlite3"
    _build_database(source)
    shutil.copyfile(source, altered)

    with sqlite3.connect(altered) as db:
        db.execute("UPDATE price_alert_zones SET lower_price = '100.26'")

    source_inventory = _inventory(source)
    altered_inventory = _inventory(altered)

    assert source_inventory["counts"] == altered_inventory["counts"]
    assert source_inventory["row_sha256"] != altered_inventory["row_sha256"]
    assert source_inventory["content_sha256"] != altered_inventory["content_sha256"]


def test_restore_inventory_detects_schema_changes(tmp_path):
    source = tmp_path / "source.sqlite3"
    altered = tmp_path / "altered.sqlite3"
    _build_database(source)
    shutil.copyfile(source, altered)

    with sqlite3.connect(altered) as db:
        db.execute(
            "CREATE INDEX idx_restore_drill_test_owner "
            "ON price_alert_zones(owner_id)"
        )

    source_inventory = _inventory(source)
    altered_inventory = _inventory(altered)

    assert source_inventory["counts"] == altered_inventory["counts"]
    assert source_inventory["row_sha256"] == altered_inventory["row_sha256"]
    assert source_inventory["schema_sha256"] != altered_inventory["schema_sha256"]
    assert source_inventory["content_sha256"] != altered_inventory["content_sha256"]


@pytest.mark.parametrize(
    "missing_table",
    [
        "price_alert_evaluation_state",
        "price_alert_market_cursor",
        "price_alert_processed_events",
        "price_alert_trigger_events",
    ],
)
def test_restore_inventory_requires_all_alert_runtime_tables(tmp_path, missing_table):
    source = tmp_path / "source.sqlite3"
    _build_database(source)

    with sqlite3.connect(source) as db:
        db.execute(f'DROP TABLE "{missing_table}"')

    with pytest.raises(
        sqlite3.DatabaseError,
        match="required application tables are missing",
    ):
        _inventory(source)

def test_encrypted_application_backup_round_trip_feeds_full_restore_drill(tmp_path):
    """Exercise SQLite snapshot -> authenticated encryption -> decrypt -> domain restore.

    This isolated CI test does not claim off-host storage, owner key custody,
    retention, or a restore on the production target.
    """
    import hashlib

    from app.backup_encryption import decrypt_backup_file, encrypt_backup_file
    from app.sqlite_backup import create_consistent_sqlite_backup

    source = tmp_path / "source" / "application.sqlite3"
    plaintext_snapshot = tmp_path / "snapshot" / "application.sqlite3"
    encrypted_artifact = tmp_path / "encrypted" / "application.sqlite3.enc"
    decrypted_snapshot = tmp_path / "decrypted" / "application.sqlite3"
    drill_backup = tmp_path / "drill" / "verified-backup.sqlite3"
    drill_restore = tmp_path / "drill-restore" / "application.sqlite3"
    source.parent.mkdir()
    _build_database(source)
    source_before = source.read_bytes()
    passphrase = b"ci-only-encrypted-restore-integration-key"

    create_consistent_sqlite_backup(source, plaintext_snapshot)
    encrypt_backup_file(plaintext_snapshot, encrypted_artifact, passphrase)
    decrypt_backup_file(encrypted_artifact, decrypted_snapshot, passphrase)

    assert encrypted_artifact.read_bytes() != plaintext_snapshot.read_bytes()
    assert hashlib.sha256(decrypted_snapshot.read_bytes()).digest() == hashlib.sha256(
        plaintext_snapshot.read_bytes()
    ).digest()

    report = run_restore_drill(decrypted_snapshot, drill_backup, drill_restore)

    assert report["status"] == "passed"
    assert report["integrity_check"] == "ok"
    assert report["table_row_counts_match"] is True
    assert report["table_content_match"] is True
    assert report["schema_match"] is True
    assert report["post_restore_write_read_cleanup"] == "passed"
    assert report["application_domain_readback"] == {
        "canonical_instruments": 1,
        "provider_mappings": 0,
        "entitlements": 1,
        "alert_zones": 1,
        "coverage_scopes": 1,
        "coverage_intervals": 2,
        "coverage_gaps": 1,
        "ohlcv_bars": 1,
        "ohlcv_series": 1,
        "outbox_high_water": 1,
    }
    assert source.read_bytes() == source_before
    assert "drill-test-subject" not in json.dumps(report)
    assert str(tmp_path) not in json.dumps(report)
    assert all(path.is_file() for path in (
        plaintext_snapshot, encrypted_artifact, decrypted_snapshot,
        drill_backup, drill_restore,
    ))
    assert list(tmp_path.rglob("*.encrypted-backup.tmp")) == []
    assert list(tmp_path.rglob("*.sqlite-backup.tmp")) == []
    assert list(tmp_path.rglob("*.sqlite-restore.tmp")) == []


def test_restore_drill_refuses_insufficient_capacity_before_creating_outputs(
    tmp_path, monkeypatch
):
    from types import SimpleNamespace
    from app import sqlite_restore_drill

    source = tmp_path / "live.sqlite3"
    backup = tmp_path / "backup" / "snapshot.sqlite3"
    restored = tmp_path / "restore" / "restored.sqlite3"
    _build_database(source)
    source_before = source.read_bytes()

    monkeypatch.setattr(
        sqlite_restore_drill.shutil,
        "disk_usage",
        lambda _path: SimpleNamespace(free=0),
    )

    with pytest.raises(OSError, match="insufficient free space"):
        run_restore_drill(source, backup, restored)

    assert source.read_bytes() == source_before
    assert not backup.exists()
    assert not restored.exists()
    assert list(tmp_path.rglob("*.sqlite-backup.tmp")) == []
    assert list(tmp_path.rglob("*.sqlite-restore.tmp")) == []


def test_restore_drill_cli_failure_redacts_paths_and_error_details(tmp_path, capsys):
    from app.sqlite_restore_drill import main

    source = tmp_path / "private" / "missing-live.sqlite3"
    backup = tmp_path / "private" / "backup.sqlite3"
    restored = tmp_path / "private" / "restored.sqlite3"

    result = main([
        "--source", str(source),
        "--backup", str(backup),
        "--restore", str(restored),
    ])

    captured = capsys.readouterr()
    assert result == 1
    assert captured.out == ""
    error = json.loads(captured.err)
    assert error == {
        "status": "failed",
        "error_type": "FileNotFoundError",
        "privacy": "error details and absolute paths withheld",
    }
    assert str(tmp_path) not in captured.err
    assert source.name not in captured.err
    assert not backup.exists()
    assert not restored.exists()


def test_restore_drill_cli_success_emits_verifiable_redacted_report(tmp_path, capsys):
    import hashlib

    from app.sqlite_restore_drill import main

    source = tmp_path / "private" / "live.sqlite3"
    backup = tmp_path / "backup" / "verified-backup.sqlite3"
    restored = tmp_path / "restore" / "restored-copy.sqlite3"
    source.parent.mkdir()
    _build_database(source)
    source_before = source.read_bytes()

    result = main([
        "--source", str(source),
        "--backup", str(backup),
        "--restore", str(restored),
    ])

    captured = capsys.readouterr()
    assert result == 0
    assert captured.err == ""
    report = json.loads(captured.out)
    assert report["status"] == "passed"
    assert report["integrity_check"] == "ok"
    assert report["foreign_key_errors"] == 0
    assert report["table_row_counts_match"] is True
    assert report["table_content_match"] is True
    assert report["schema_match"] is True
    assert report["post_restore_write_read_cleanup"] == "passed"
    assert report["application_domain_readback"]["outbox_high_water"] == 1
    assert report["application_domain_readback"]["ohlcv_bars"] == 1
    report_without_hash = dict(report)
    report_hash = report_without_hash.pop("report_sha256")
    canonical = json.dumps(report_without_hash, sort_keys=True, separators=(",", ":"))
    assert report_hash == hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert str(tmp_path) not in captured.out
    assert source.name not in captured.out
    assert backup.name not in captured.out
    assert restored.name not in captured.out
    assert source.read_bytes() == source_before
    assert backup.is_file()
    assert restored.is_file()
