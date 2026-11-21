"""Contract test for the local-only metrics collector benchmark."""
import json
from pathlib import Path
import subprocess
import sys


def test_metrics_collector_benchmark_measures_one_four_and_sixteen_workers():
    backend_dir = Path(__file__).resolve().parents[1]
    script = backend_dir / "scripts" / "benchmark_metrics_collector.py"
    result = subprocess.run(
        [sys.executable, str(script), "--flushes-per-worker", "2"],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    report = json.loads(result.stdout)
    assert report["benchmark"] == "sqlite_metrics_collector_local_synthetic"
    assert report["data_source"] == "synthetic_operational_counters_only_not_market_data"
    assert [case["workers"] for case in report["cases"]] == [1, 4, 16]
    for case in report["cases"]:
        assert case["successful_flushes"] == case["workers"] * 2
        assert case["worker_count_verified"] == case["workers"]
        assert case["aggregated_request_count_verified"] == case["workers"] * 2
        assert case["sqlite_integrity"] == "ok"
        assert case["flush_latency"]["samples"] == case["workers"] * 2
        assert case["peak_file_sizes_bytes"]["total"] > 0
        assert case["post_checkpoint_file_sizes_bytes"]["database"] > 0
