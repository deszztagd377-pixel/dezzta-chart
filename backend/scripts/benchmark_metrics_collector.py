"""Synthetic local-only benchmark for the same-host SQLite metrics collector.

Exercises the full declared 899 logical-series envelope with 1, 4 and 16
concurrent Python threads, plus a separate-OS-process contention case. This
remains a CI/local baseline, not a production-host, multi-host, or market-data
performance guarantee.

Run from the backend directory:
    python scripts/benchmark_metrics_collector.py --flushes-per-worker 32
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
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

from app.metrics_collector import MAX_SERIES, SQLiteMetricsCollector


_BASE_TIME = 1_800_000_000.0
_METHOD = "GET"
_STATUSES = ("1xx", "2xx", "3xx", "4xx", "5xx", "other")
_BUCKET_LIMITS = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000)


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
    routes = [f"/benchmark/series/{index:03d}" for index in range(127)]
    requests = [
        {
            "method": _METHOD,
            "route": route,
            "status_class": status,
            "count": count,
        }
        for route in routes
        for status in _STATUSES
    ]
    latency = [
        {
            "method": _METHOD,
            "route": route,
            "count": count,
            "sum_ms": float(count * 2),
            "buckets": [
                {"le_ms": limit, "count": count if limit >= 5 else 0}
                for limit in _BUCKET_LIMITS
            ] + [{"le_ms": None, "count": count}],
        }
        for route in routes
    ]
    request_snapshot = {
        "schema_version": 1,
        "requests": requests,
        "latency_ms": latency,
    }
    websocket_snapshot = {
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
    return request_snapshot, websocket_snapshot


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
        start_barrier = threading.Barrier(workers)
        size_lock = threading.Lock()
        peak_sizes = {"database": 0, "-wal": 0, "-shm": 0, "total": 0}
        retry_count = 0
        retry_lock = threading.Lock()
        latency_samples: list[float] = []
        lock_wait_samples: list[float] = []
        transaction_samples: list[float] = []
        latency_lock = threading.Lock()

        def record_sizes() -> None:
            observed = _file_sizes(database_path)
            with size_lock:
                for key, value in observed.items():
                    peak_sizes[key] = max(peak_sizes[key], value)

        def worker_run(worker_index: int) -> dict:
            nonlocal retry_count
            collector = SQLiteMetricsCollector(str(database_path))
            worker_id = f"{worker_index + 1:032x}"
            start_barrier.wait(timeout=10)
            local_samples = []
            local_lock_wait = []
            local_transaction = []
            local_retries = 0
            for sequence in range(1, flushes_per_worker + 1):
                request, websocket = _snapshot(sequence)
                stamp = _BASE_TIME + sequence * 15 + worker_index / 1000
                started = time.perf_counter_ns()
                flush_result = collector.flush(worker_id, request, websocket, now=stamp)
                local_retries += flush_result.get("lock_retries", 0)
                local_lock_wait.append(flush_result["lock_wait_ms"])
                local_transaction.append(flush_result["transaction_ms"])
                local_samples.append((time.perf_counter_ns() - started) / 1_000_000)
                record_sizes()
            with retry_lock:
                retry_count += local_retries
            with latency_lock:
                latency_samples.extend(local_samples)
                lock_wait_samples.extend(local_lock_wait)
                transaction_samples.extend(local_transaction)
            return {"worker_index": worker_index, "flushes": len(local_samples), "retries": local_retries}

        with ThreadPoolExecutor(max_workers=workers) as pool:
            worker_results = list(pool.map(worker_run, range(workers)))

        snapshot_time = _BASE_TIME + flushes_per_worker * 15 + 20
        collector = SQLiteMetricsCollector(str(database_path))
        result = collector.snapshot(now=snapshot_time)
        expected_total = workers * flushes_per_worker
        expected_series = 899
        first_route_key = "http.requests|GET|/benchmark/series/000|2xx"
        actual_total = result["series"].get(first_route_key, 0)
        if result["worker_count"] != workers or actual_total != expected_total:
            raise RuntimeError(
                f"aggregation mismatch: workers={result['worker_count']}/{workers}, "
                f"requests={actual_total}/{expected_total}"
            )
        if len(result["series"]) != expected_series:
            raise RuntimeError(
                f"cardinality mismatch: observed={len(result['series'])}/{expected_series}"
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
            "logical_series_verified": len(result["series"]),
            "logical_series_expected": expected_series,
            "worker_count_verified": result["worker_count"],
            "aggregated_request_count_verified": actual_total,
            "sqlite_integrity": "ok",
            "retry_count": retry_count,
            "flush_latency": _summary(latency_samples),
            "writer_lock_wait": _summary(lock_wait_samples),
            "transaction_body_and_commit": _summary(transaction_samples),
            "peak_file_sizes_bytes": peak_sizes,
            "post_checkpoint_file_sizes_bytes": final_sizes,
            "worker_results": worker_results,
        }



def _process_worker(database_path: str, worker_index: int, flushes_per_worker: int, start_event, result_queue) -> None:
    """Run a real OS-process writer; each process owns its SQLite connections."""
    try:
        collector = SQLiteMetricsCollector(database_path)
        worker_id = f"{worker_index + 1:032x}"
        if not start_event.wait(timeout=20):
            raise TimeoutError("process benchmark start barrier timed out")
        samples, lock_wait_samples, transaction_samples, retries = [], [], [], 0
        for sequence in range(1, flushes_per_worker + 1):
            request, websocket = _snapshot(sequence)
            stamp = _BASE_TIME + sequence * 15 + worker_index / 1000
            started = time.perf_counter_ns()
            flush_result = collector.flush(worker_id, request, websocket, now=stamp)
            samples.append((time.perf_counter_ns() - started) / 1_000_000)
            lock_wait_samples.append(flush_result["lock_wait_ms"])
            transaction_samples.append(flush_result["transaction_ms"])
            retries += flush_result.get("lock_retries", 0)
        result_queue.put({"worker_index": worker_index, "flushes": len(samples), "retries": retries, "latencies_ms": samples, "lock_wait_ms": lock_wait_samples, "transaction_ms": transaction_samples})
    except BaseException as exc:
        result_queue.put({"worker_index": worker_index, "error": f"{type(exc).__name__}: {exc}"})
        raise


def run_process_case(*, workers: int, flushes_per_worker: int) -> dict:
    """Exercise SQLite locking between distinct OS processes, not threads."""
    context = multiprocessing.get_context("spawn")
    with tempfile.TemporaryDirectory(prefix="dezzta-metrics-processes-") as directory:
        database_path = Path(directory) / "metrics.sqlite3"
        start_event, result_queue = context.Event(), context.Queue()
        processes = [
            context.Process(target=_process_worker, args=(str(database_path), index, flushes_per_worker, start_event, result_queue))
            for index in range(workers)
        ]
        for process in processes:
            process.start()
        start_event.set()
        for process in processes:
            process.join(timeout=120)
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                raise TimeoutError("process benchmark worker exceeded 120 seconds")
            if process.exitcode != 0:
                raise RuntimeError(f"process benchmark worker exited with code {process.exitcode}")
        worker_results = [result_queue.get(timeout=5) for _ in range(workers)]
        result_queue.close()
        result_queue.join_thread()
        errors = [item for item in worker_results if "error" in item]
        if errors:
            raise RuntimeError(f"process benchmark worker failed: {errors}")
        worker_results.sort(key=lambda item: item["worker_index"])
        snapshot_time = _BASE_TIME + flushes_per_worker * 15 + 20
        result = SQLiteMetricsCollector(str(database_path)).snapshot(now=snapshot_time)
        expected_total = workers * flushes_per_worker
        first_route_key = "http.requests|GET|/benchmark/series/000|2xx"
        actual_total = result["series"].get(first_route_key, 0)
        if result["worker_count"] != workers or actual_total != expected_total:
            raise RuntimeError(f"process aggregation mismatch: workers={result['worker_count']}/{workers}, requests={actual_total}/{expected_total}")
        if len(result["series"]) != 899:
            raise RuntimeError(f"process cardinality mismatch: observed={len(result['series'])}/899")
        with sqlite3.connect(str(database_path), timeout=1.0) as verify:
            integrity = verify.execute("PRAGMA integrity_check").fetchone()
            if integrity is None or integrity[0] != "ok":
                raise RuntimeError(f"process SQLite integrity_check failed: {integrity}")
            verify.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        latencies = [value for worker in worker_results for value in worker["latencies_ms"]]
        lock_waits = [value for worker in worker_results for value in worker["lock_wait_ms"]]
        transactions = [value for worker in worker_results for value in worker["transaction_ms"]]
        return {
            "worker_type": "separate_os_processes",
            "workers": workers,
            "flushes_per_worker": flushes_per_worker,
            "successful_flushes": expected_total,
            "logical_series_verified": len(result["series"]),
            "logical_series_expected": 899,
            "worker_count_verified": result["worker_count"],
            "aggregated_request_count_verified": actual_total,
            "sqlite_integrity": "ok",
            "retry_count": sum(worker["retries"] for worker in worker_results),
            "flush_latency": _summary(latencies),
            "writer_lock_wait": _summary(lock_waits),
            "transaction_body_and_commit": _summary(transactions),
            "post_checkpoint_file_sizes_bytes": _file_sizes(database_path),
            "worker_results": [{key: value for key, value in worker.items() if key != "latencies_ms"} for worker in worker_results],
        }



def _production_phase_delay(worker_id: str) -> int:
    """Mirror main.py's first-flush phase: UUID prefix modulo 15."""
    if not isinstance(worker_id, str) or len(worker_id) < 8:
        raise ValueError("worker_id must contain at least eight hexadecimal characters")
    try:
        return int(worker_id[:8], 16) % 15
    except ValueError as exc:
        raise ValueError("worker_id prefix must be hexadecimal") from exc


def _staggered_worker_id(worker_index: int) -> str:
    """Stable UUID-shaped ID with a reproducible 0–14 second phase."""
    return hashlib.sha256(f"dezzta-metrics-worker-{worker_index}".encode()).hexdigest()[:32]


def run_startup_staggered_case(
    *, workers: int, flushes_per_worker: int, cadence_scale: float,
) -> dict:
    """Model production startup phase offsets and its 15-second flush cadence.

    Wall-clock waits are uniformly scaled for CI. SQLite timestamps retain the
    real 15-second cadence, preserving bucket and stale-worker semantics.
    """
    if not 1 <= workers <= MAX_SERIES:
        raise ValueError("workers must be between 1 and MAX_SERIES")
    if not 0 < cadence_scale <= 1:
        raise ValueError("cadence_scale must be greater than zero and at most one")
    worker_ids = [_staggered_worker_id(index) for index in range(workers)]
    phase_delays = [_production_phase_delay(worker_id) for worker_id in worker_ids]
    with tempfile.TemporaryDirectory(prefix="dezzta-metrics-staggered-") as directory:
        database_path = Path(directory) / "metrics.sqlite3"
        start_barrier = threading.Barrier(workers)
        size_lock = threading.Lock()
        latency_lock = threading.Lock()
        peak_sizes = {"database": 0, "-wal": 0, "-shm": 0, "total": 0}
        latency_samples: list[float] = []
        lock_wait_samples: list[float] = []
        transaction_samples: list[float] = []
        retry_count = 0

        def record_sizes() -> None:
            observed = _file_sizes(database_path)
            with size_lock:
                for key, value in observed.items():
                    peak_sizes[key] = max(peak_sizes[key], value)

        def worker_run(worker_index: int) -> dict:
            nonlocal retry_count
            worker_id = worker_ids[worker_index]
            phase_delay = phase_delays[worker_index]
            collector = SQLiteMetricsCollector(str(database_path))
            start_barrier.wait(timeout=10)
            time.sleep(phase_delay * cadence_scale)
            local_latency: list[float] = []
            local_lock_wait: list[float] = []
            local_transaction: list[float] = []
            local_retries = 0
            for sequence in range(1, flushes_per_worker + 1):
                request, websocket = _snapshot(sequence)
                stamp = _BASE_TIME + phase_delay + (sequence - 1) * 15
                started = time.perf_counter_ns()
                flush_result = collector.flush(worker_id, request, websocket, now=stamp)
                local_latency.append((time.perf_counter_ns() - started) / 1_000_000)
                local_lock_wait.append(flush_result["lock_wait_ms"])
                local_transaction.append(flush_result["transaction_ms"])
                local_retries += flush_result.get("lock_retries", 0)
                record_sizes()
                if sequence < flushes_per_worker:
                    time.sleep(15 * cadence_scale)
            with latency_lock:
                latency_samples.extend(local_latency)
                lock_wait_samples.extend(local_lock_wait)
                transaction_samples.extend(local_transaction)
                retry_count += local_retries
            return {
                "worker_index": worker_index,
                "phase_delay_seconds": phase_delay,
                "flushes": len(local_latency),
                "retries": local_retries,
            }

        with ThreadPoolExecutor(max_workers=workers) as pool:
            worker_results = list(pool.map(worker_run, range(workers)))

        snapshot_time = (
            _BASE_TIME + max(phase_delays, default=0)
            + max(0, flushes_per_worker - 1) * 15 + 20
        )
        result = SQLiteMetricsCollector(str(database_path)).snapshot(now=snapshot_time)
        expected_total = workers * flushes_per_worker
        first_route_key = "http.requests|GET|/benchmark/series/000|2xx"
        actual_total = result["series"].get(first_route_key, 0)
        if result["worker_count"] != workers or actual_total != expected_total:
            raise RuntimeError(
                f"staggered aggregation mismatch: workers={result['worker_count']}/{workers}, "
                f"requests={actual_total}/{expected_total}"
            )
        if len(result["series"]) != 899:
            raise RuntimeError(
                f"staggered cardinality mismatch: observed={len(result['series'])}/899"
            )
        with sqlite3.connect(str(database_path), timeout=1.0) as verify:
            integrity = verify.execute("PRAGMA integrity_check").fetchone()
            if integrity is None or integrity[0] != "ok":
                raise RuntimeError(f"staggered SQLite integrity_check failed: {integrity}")
            verify.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        final_sizes = _file_sizes(database_path)
        record_sizes()
        return {
            "worker_type": "production_startup_phase_staggered_threads",
            "workers": workers,
            "flushes_per_worker": flushes_per_worker,
            "successful_flushes": expected_total,
            "logical_series_verified": len(result["series"]),
            "logical_series_expected": 899,
            "worker_count_verified": result["worker_count"],
            "aggregated_request_count_verified": actual_total,
            "sqlite_integrity": "ok",
            "retry_count": retry_count,
            "startup_phase_delays_seconds": phase_delays,
            "cadence_scale": cadence_scale,
            "production_startup_phase_range_seconds": [0, 14],
            "production_flush_interval_seconds": 15,
            "flush_latency": _summary(latency_samples),
            "writer_lock_wait": _summary(lock_wait_samples),
            "transaction_body_and_commit": _summary(transaction_samples),
            "peak_file_sizes_bytes": peak_sizes,
            "post_checkpoint_file_sizes_bytes": final_sizes,
            "worker_results": worker_results,
        }



def run_benchmark(*, flushes_per_worker: int, cadence_scale: float = 0.01) -> dict:
    if not 1 <= flushes_per_worker <= 1000:
        raise ValueError("flushes_per_worker must be between 1 and 1000")
    request, websocket = _snapshot(1)
    payload_bytes = len(json.dumps(
        {"request": request, "websocket": websocket},
        separators=(",", ":"), sort_keys=True, allow_nan=False,
    ).encode("utf-8"))
    cases = [
        run_case(workers=workers, flushes_per_worker=flushes_per_worker)
        for workers in (1, 4, 16)
    ]
    process_case = run_process_case(workers=4, flushes_per_worker=flushes_per_worker)
    staggered_case = run_startup_staggered_case(
        workers=16, flushes_per_worker=flushes_per_worker, cadence_scale=cadence_scale,
    )
    return {
        "benchmark": "sqlite_metrics_collector_full_cardinality_local_synthetic",
        "data_source": "synthetic_operational_counters_only_not_market_data",
        "declared_logical_series": 899,
        "collector_series_limit": MAX_SERIES,
        "request_series": len(request["requests"]),
        "latency_series": len(request["latency_ms"]),
        "websocket_series": 10,
        "snapshot_payload_bytes": payload_bytes,
        "snapshot_payload_limit_bytes": 256 * 1024,
        "commit_sha": os.environ.get("GITHUB_SHA", "not_supplied"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cases": cases,
        "process_case": process_case,
        "startup_staggered_case": staggered_case,
        "notes": [
            "Full declared 899-series envelope: 762 request + 127 latency + 10 WebSocket series.",
            "Thread cases use concurrent Python threads; process_case uses four independent OS processes.",
            "startup_staggered_case mirrors production UUID-prefix modulo-15 startup offsets and 15-second cadence; wall-clock sleeps are scaled for CI while SQLite timestamps preserve production cadence.",
            "Each process creates its own collector and SQLite connections against the same local database.",
            "Measures synthetic end-to-end flush latency, writer-lock wait, transaction body plus commit, retries, and local file/WAL/SHM sizes.",
            "Lock-wait and transaction timings are diagnostic phase measurements, not production SLA estimates.",
            "Does not simulate a production persistent volume or multi-host topology.",
            "Does not establish a production database byte cap or multi-host support.",
            "Results depend on the CI runner filesystem and must not be generalized to owner-host storage.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flushes-per-worker", type=_positive_int, default=32)
    parser.add_argument("--cadence-scale", type=float, default=0.01)
    args = parser.parse_args()
    if args.flushes_per_worker > 1000:
        parser.error("--flushes-per-worker cannot exceed 1000")
    if not 0 < args.cadence_scale <= 1:
        parser.error("--cadence-scale must be greater than zero and at most one")
    print(json.dumps(run_benchmark(flushes_per_worker=args.flushes_per_worker, cadence_scale=args.cadence_scale), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
