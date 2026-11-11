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
