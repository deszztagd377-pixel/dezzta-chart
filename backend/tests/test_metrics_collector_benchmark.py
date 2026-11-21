"""Contract test for the local-only full-cardinality metrics benchmark."""
import json
from pathlib import Path
import subprocess
import sys


def test_metrics_collector_benchmark_measures_full_cardinality_at_one_four_and_sixteen_workers():
    backend_dir = Path(__file__).resolve().parents[1]
    script = backend_dir / "scripts" / "benchmark_metrics_collector.py"
    result = subprocess.run(
        [sys.executable, str(script), "--flushes-per-worker", "2"],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    report = json.loads(result.stdout)
    assert report["benchmark"] == "sqlite_metrics_collector_full_cardinality_local_synthetic"
    assert report["data_source"] == "synthetic_operational_counters_only_not_market_data"
    assert report["declared_logical_series"] == 899
    assert report["request_series"] == 762
    assert report["latency_series"] == 127
    assert report["websocket_series"] == 10
    assert report["snapshot_payload_bytes"] <= report["snapshot_payload_limit_bytes"]
    assert [case["workers"] for case in report["cases"]] == [1, 4, 16]
    for case in report["cases"]:
        assert case["successful_flushes"] == case["workers"] * 2
        assert case["worker_count_verified"] == case["workers"]
        assert case["logical_series_verified"] == 899
        assert case["logical_series_expected"] == 899
        assert case["aggregated_request_count_verified"] == case["workers"] * 2
        assert case["sqlite_integrity"] == "ok"
        assert case["flush_latency"]["samples"] == case["workers"] * 2
        assert case["peak_file_sizes_bytes"]["total"] > 0
        assert case["post_checkpoint_file_sizes_bytes"]["database"] > 0
