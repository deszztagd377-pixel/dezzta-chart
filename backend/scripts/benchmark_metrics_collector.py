"""Synthetic local-only benchmark for the same-host SQLite metrics collector.

Run from the backend directory:
    python scripts/benchmark_metrics_collector.py --flushes-per-worker 32

This measures the local Python/SQLite runtime only. It is not a production-host,
multi-host, or market-data performance guarantee.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sqlite3
import statistics
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.metrics_collector import SQLiteMetricsCollector


_BASE_TIME = 1_800_000_000.0


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _percentile(samples: list[float], percentile: float) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    rank = max(1, int(percentile * len(ordered) + 0.9999999999))
    return round(ordered[min(rank - 1, len(ordered) - 1)], 6)


def _summary(samples: list[float]) -> dict[str, float | int]:
    return {
        "samples": len(samples),
        "p50_ms": _percentile(samples, 0.50),
        "p95_ms": _percentile(samples, 0.95),
        "p99_ms": _percentile(samples, 0.99),
        "mean_ms": round(statistics.fmean(samples), 6) if samples else 0.0,
        "max_ms": round(max(samples), 6) if samples else 0.0,
    }


def _snapshot(count: int) -> tuple[dict, dict]:
    request = {
        "schema_version": 1,
        "requests": [{
            "method": "GET",
            "route": "/benchmark/metrics",
            "status_class": "2xx",
            "count": count,
        }],
        "latency_ms": [{
            "method": "GET",
            "route": "/benchmark/metrics",
            "count": count,
            "sum_ms": float(count * 2),
            "buckets": [
                {"le_ms": limit, "count": count if limit >= 5 else 0}
                for limit in (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000)
            ] + [{"le_ms": None, "count": count}],
        }],
    }
    websocket = {
        "schema_version": 1,
        "connections_started": count,
        "connections_active": 0,
        "connections_completed": count,
        "connections_accepted": count,
        "peer_disconnects": count,
        "duration_sum_ms": float(count * 3),
        "close_code_classes": {
            "1xxx": count, "2xxx": count, "4xxx": count, "5xxx": count, "other": count,
        },
    }
    return request, websocket


def _file_sizes(database_path: Path) -> dict[str, int]:
    result = {}
    for suffix in ("", "-wal", "-shm"):
        path = Path(str(database_path) + suffix)
        try:
            result[suffix or "database"] = path.stat().st_size
        except FileNotFoundError:
            result[suffix or "database"] = 0
    result["total"] = result["database"] + result["-wal"] + result["-shm"]
    return result


def run_case(*, workers: int, flushes_per_worker: int) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"dezzta-metrics-{workers}-workers-") as directory:
        database_path = Path(directory) / "metrics.sqlite3"
        collector = SQLiteMetricsCollector(str(database_path))
        start_barrier = threading.Barrier(workers)
        size_lock = threading.Lock()
        peak_sizes = {"database": 0, "-wal": 0, "-shm": 0, "total": 0}
        retry_count = 0
        retry_lock = threading.Lock()
        latency_samples: list[float] = []
        latency_lock = threading.Lock()

        def record_sizes() -> None:
            observed = _file_sizes(database_path)
            with size_lock:
                for key, value in observed.items():
                    peak_sizes[key] = max(peak_sizes[key], value)

        def worker_run(worker_index: int) -> dict:
            nonlocal retry_count
            worker_id = f"{worker_index + 1:032x}"
            start_barrier.wait(timeout=10)
            local_samples = []
            local_retries = 0
            for sequence in range(1, flushes_per_worker + 1):
                request, websocket = _snapshot(sequence)
                stamp = _BASE_TIME + sequence * 15 + worker_index / 1000
                started = time.perf_counter_ns()
                for attempt in range(6):
                    try:
                        collector.flush(worker_id, request, websocket, now=stamp)
                        break
                    except sqlite3.OperationalError as exc:
                        if "locked" not in str(exc).lower() or attempt == 5:
                            raise
                        local_retries += 1
                        time.sleep(0.01 * (2 ** attempt))
                else:
                    raise RuntimeError("bounded retry loop exhausted")
                local_samples.append((time.perf_counter_ns() - started) / 1_000_000)
                record_sizes()
            with retry_lock:
                retry_count += local_retries
            with latency_lock:
                latency_samples.extend(local_samples)
            return {"worker_index": worker_index, "flushes": len(local_samples), "retries": local_retries}

        with ThreadPoolExecutor(max_workers=workers) as pool:
            worker_results = list(pool.map(worker_run, range(workers)))

        snapshot_time = _BASE_TIME + flushes_per_worker * 15 + 20
        result = collector.snapshot(now=snapshot_time)
        expected_total = workers * flushes_per_worker
        actual_total = result["series"].get("http.requests|GET|/benchmark/metrics|2xx", 0)
        if result["worker_count"] != workers or actual_total != expected_total:
            raise RuntimeError(
                f"aggregation mismatch: workers={result['worker_count']}/{workers}, "
                f"requests={actual_total}/{expected_total}"
            )

        with sqlite3.connect(str(database_path), timeout=1.0) as verify:
            integrity = verify.execute("PRAGMA integrity_check").fetchone()
            if integrity is None or integrity[0] != "ok":
                raise RuntimeError(f"SQLite integrity_check failed: {integrity}")
            verify.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()

        final_sizes = _file_sizes(database_path)
        record_sizes()
        return {
            "workers": workers,
            "flushes_per_worker": flushes_per_worker,
            "successful_flushes": expected_total,
            "worker_count_verified": result["worker_count"],
            "aggregated_request_count_verified": actual_total,
            "sqlite_integrity": "ok",
            "retry_count": retry_count,
            "flush_latency": _summary(latency_samples),
            "peak_file_sizes_bytes": peak_sizes,
            "post_checkpoint_file_sizes_bytes": final_sizes,
            "worker_results": worker_results,
        }


def run_benchmark(*, flushes_per_worker: int) -> dict:
    if not 1 <= flushes_per_worker <= 1000:
        raise ValueError("flushes_per_worker must be between 1 and 1000")
    cases = [
        run_case(workers=workers, flushes_per_worker=flushes_per_worker)
        for workers in (1, 4, 16)
    ]
    return {
        "benchmark": "sqlite_metrics_collector_local_synthetic",
        "data_source": "synthetic_operational_counters_only_not_market_data",
        "commit_sha": os.environ.get("GITHUB_SHA", "not_supplied"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cases": cases,
        "notes": [
            "Single-host SQLite WAL benchmark using concurrent Python worker threads.",
            "Measures synthetic flush throughput, lock retries, local file and WAL sizes.",
            "Does not simulate separate OS processes or a production persistent volume.",
            "Does not establish a production database byte cap or multi-host support.",
            "Results depend on the CI runner filesystem and must not be generalized to owner-host storage.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flushes-per-worker", type=_positive_int, default=32)
    args = parser.parse_args()
    if args.flushes_per_worker > 1000:
        parser.error("--flushes-per-worker cannot exceed 1000")
    print(json.dumps(run_benchmark(flushes_per_worker=args.flushes_per_worker), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
