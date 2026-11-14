"""Redacted owner-device SQLite restore drill for DEZZTA CHART.

Run from the backend directory:
python -m app.sqlite_restore_drill --source PATH --backup PATH --restore PATH

The source is snapshotted read-only. Backup and restore outputs must be new paths.
The report contains aggregate counts and hashes only, never row values or absolute paths.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import sys
from time import perf_counter
from uuid import uuid4

from .alert_store import SQLitePriceAlertStore
from .coverage_store import SQLiteCoverageTracker
from .entitlements import SQLiteInstrumentEntitlementStore
from .instrument_registry import SQLiteInstrumentRegistry
from .ohlcv_store import SQLiteOhlcvStore
from .sqlite_backup import create_consistent_sqlite_backup, restore_consistent_sqlite_backup

_REQUIRED = {
    "canonical_instruments", "provider_instrument_mappings",
    "user_instrument_entitlements", "price_alert_zones",
    "ohlcv_coverage_intervals", "ohlcv_coverage_meta",
    "ohlcv_bars", "ohlcv_store_state", "ohlcv_outbox",
    "ohlcv_outbox_state", "ohlcv_schema_meta",
}

def _ro(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection

def _inventory(path: Path) -> dict:
    db = _ro(path)
    try:
        integrity = [tuple(row) for row in db.execute("PRAGMA integrity_check").fetchall()]
        if integrity != [("ok",)]:
            raise sqlite3.DatabaseError("integrity_check failed")
        if db.execute("PRAGMA foreign_key_check").fetchmany(1):
            raise sqlite3.DatabaseError("foreign_key_check failed")
        tables = {row["name"] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()}
        if _REQUIRED - tables:
            raise sqlite3.DatabaseError("required application tables are missing")
        counts = {}
        for table in sorted(tables):
            quoted = '"' + table.replace('"', '""') + '"'
            counts[table] = int(db.execute("SELECT COUNT(*) FROM " + quoted).fetchone()[0])
        outbox = db.execute(
            "SELECT COUNT(*) AS n, COUNT(DISTINCT event_id) AS ids, "
            "COUNT(DISTINCT cursor) AS cursors FROM ohlcv_outbox"
        ).fetchone()
        if outbox["n"] != outbox["ids"] or outbox["n"] != outbox["cursors"]:
            raise sqlite3.DatabaseError("outbox identity check failed")
        return {"tables": sorted(tables), "counts": counts, "outbox_events": int(outbox["n"])}
    finally:
        db.close()

def _domain_readback(path: Path) -> dict[str, int]:
    registry = SQLiteInstrumentRegistry(str(path))
    instruments = 0
    mappings = 0
    offset = 0
    while True:
        batch = registry.list_instruments(active_only=False, limit=1000, offset=offset)
        instruments += len(batch)
        for item in batch:
            mappings += len(registry.list_provider_mappings(item.canonical_id))
        offset += len(batch)
        if len(batch) < 1000:
            break
    entitlement_store = SQLiteInstrumentEntitlementStore(str(path))
    alert_store = SQLitePriceAlertStore(str(path))
    db = _ro(path)
    try:
        subjects = [r[0] for r in db.execute(
            "SELECT DISTINCT subject FROM user_instrument_entitlements"
        ).fetchall()]
        owners = [r[0] for r in db.execute(
            "SELECT DISTINCT owner_id FROM price_alert_zones"
        ).fetchall()]
    finally:
        db.close()
    entitlements = sum(len(entitlement_store.list_for_subject(
        subject=s, include_revoked=True
    )) for s in subjects)
    alerts = sum(len(alert_store.list_zones(
        owner_id=o, include_deleted=True
    )) for o in owners)
    coverage = SQLiteCoverageTracker(str(path)).stats()
    ohlcv = SQLiteOhlcvStore(str(path))
    stats = ohlcv.stats()
    return {
        "canonical_instruments": instruments,
        "provider_mappings": mappings,
        "entitlements": entitlements,
        "alert_zones": alerts,
        "coverage_scopes": int(coverage["scopes"]),
        "coverage_intervals": int(coverage["covered_intervals"]),
        "coverage_gaps": int(coverage["gap_intervals"]),
        "ohlcv_bars": int(stats["bars"]),
        "ohlcv_series": int(stats["series"]),
        "outbox_high_water": int(ohlcv.outbox_high_water()),
    }

def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _write_probe(path: Path) -> None:
    table = "__dezzta_restore_drill_probe"
    probe_id = uuid4().hex
    timestamp = datetime.now(timezone.utc).isoformat()
    db = sqlite3.connect(path, timeout=30)
    try:
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                      (table,)).fetchone():
            raise sqlite3.DatabaseError("restore probe table already exists")
        db.execute("CREATE TABLE __dezzta_restore_drill_probe (probe_id TEXT PRIMARY KEY, checked_at_utc TEXT NOT NULL)")
        db.execute("INSERT INTO __dezzta_restore_drill_probe VALUES (?, ?)", (probe_id, timestamp))
        if db.execute("SELECT probe_id, checked_at_utc FROM __dezzta_restore_drill_probe").fetchone() != (probe_id, timestamp):
            raise sqlite3.DatabaseError("post-restore write/read failed")
        db.execute("DROP TABLE __dezzta_restore_drill_probe")
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def run_restore_drill(source_path: str | Path, backup_path: str | Path,
                      restore_path: str | Path) -> dict:
    started = perf_counter()
    source = Path(source_path).expanduser().resolve(strict=True)
    backup = Path(backup_path).expanduser().resolve()
    restored = Path(restore_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError("source database is not a regular file")
    if len({source, backup, restored}) != 3:
        raise ValueError("source, backup and restore paths must be distinct")
    if backup.exists():
        raise FileExistsError("backup destination exists; refusing to overwrite")
    if restored.exists():
        raise FileExistsError("restore destination exists; refusing to overwrite")

    create_consistent_sqlite_backup(source, backup)
    restore_consistent_sqlite_backup(backup, restored)
    backup_inventory = _inventory(backup)
    restored_inventory = _inventory(restored)
    if backup_inventory["counts"] != restored_inventory["counts"]:
        raise sqlite3.DatabaseError("backup and restore table row counts differ")
    domains = _domain_readback(restored)
    _write_probe(restored)
    probe_db = _ro(restored)
    try:
        probe_remains = probe_db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            ("__dezzta_restore_drill_probe",)
        ).fetchone()
    finally:
        probe_db.close()
    if probe_remains:
        raise sqlite3.DatabaseError("restore probe cleanup failed")

    report = {
        "status": "passed",
        "drill_id": uuid4().hex,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": {"python": platform.python_version(), "platform": platform.system(),
                    "machine": platform.machine(), "sqlite": sqlite3.sqlite_version},
        "source_name": source.name, "backup_name": backup.name, "restore_name": restored.name,
        "backup_size_bytes": backup.stat().st_size, "restore_size_bytes": restored.stat().st_size,
        "backup_sha256": _hash(backup), "restore_sha256": _hash(restored),
        "integrity_check": "ok", "foreign_key_errors": 0,
        "required_tables_present": True, "table_row_counts_match": True,
        "application_domain_readback": domains,
        "outbox_event_ids_unique": True,
        "post_restore_write_read_cleanup": "passed",
        "failed_checks": [],
        "elapsed_ms": round((perf_counter() - started) * 1000, 2),
        "privacy": "aggregate counts and hashes only; no row values, account IDs, or absolute paths",
    }
    canonical_report = json.dumps(report, sort_keys=True, separators=(",", ":"))
    report["report_sha256"] = hashlib.sha256(canonical_report.encode("utf-8")).hexdigest()
    return report

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a safe fresh-path DEZZTA CHART SQLite restore drill.")
    parser.add_argument("--source", required=True, help="Actual application DB path; source is read-only.")
    parser.add_argument("--backup", required=True, help="New backup path; must not already exist.")
    parser.add_argument("--restore", required=True, help="New restore path; must not already exist.")
    args = parser.parse_args(argv)
    try:
        report = run_restore_drill(args.source, args.backup, args.restore)
    except Exception as exc:
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__,
                          "privacy": "error details and absolute paths withheld"}), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
