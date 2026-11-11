"""Contract tests for the local-only OHLCV outbox benchmark."""
import json
from pathlib import Path
import subprocess
import sys


def test_local_outbox_benchmark_reports_synthetic_data_and_latency(tmp_path):
    backend_dir = Path(__file__).resolve().parents[1]
    script = backend_dir / "scripts" / "benchmark_ohlcv_outbox.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--bars",
            "20",
            "--batch-size",
            "5",
        ],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    report = json.loads(result.stdout)
    assert report["benchmark"] == "sqlite_ohlcv_outbox_local_microbenchmark"
    assert report["data_source"] == "synthetic_only_not_market_data"
    assert report["bars_inserted"] == 20
    assert report["replayed_events"] == 20
    assert report["outbox_high_water"] == 20
    assert report["replay_batch_size"] == 5
    assert report["persist_latency"]["samples"] == 20
    assert report["replay_page_latency"]["samples"] == 4
    assert report["persist_latency"]["p99_ms"] >= 0
    assert report["replay_page_latency"]["p99_ms"] >= 0
    assert any("Not a provider" in note for note in report["notes"])


def test_local_outbox_benchmark_rejects_zero_bars():
    backend_dir = Path(__file__).resolve().parents[1]
    script = backend_dir / "scripts" / "benchmark_ohlcv_outbox.py"
    result = subprocess.run(
        [sys.executable, str(script), "--bars", "0"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "greater than zero" in result.stderr

def test_local_outbox_benchmark_refuses_to_modify_existing_database(tmp_path):
    backend_dir = Path(__file__).resolve().parents[1]
    script = backend_dir / "scripts" / "benchmark_ohlcv_outbox.py"
    database = tmp_path / "existing.sqlite3"
    database.write_bytes(b"owner-data-must-remain-untouched")
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--bars",
            "2",
            "--database",
            str(database),
        ],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert "refusing to modify an existing database" in result.stderr
    assert database.read_bytes() == b"owner-data-must-remain-untouched"

def test_local_outbox_benchmark_rejects_existing_symlink(tmp_path):
    backend_dir = Path(__file__).resolve().parents[1]
    script = backend_dir / "scripts" / "benchmark_ohlcv_outbox.py"
    target = tmp_path / "target.sqlite3"
    link = tmp_path / "linked.sqlite3"
    link.symlink_to(target)
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--bars",
            "2",
            "--database",
            str(link),
        ],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert "refusing to modify an existing database" in result.stderr
    assert link.is_symlink()
    assert not target.exists()
