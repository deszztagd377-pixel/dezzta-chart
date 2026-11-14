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
    assert "drill-test-subject" not in json.dumps(report)

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
