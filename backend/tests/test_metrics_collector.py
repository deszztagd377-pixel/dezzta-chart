import sqlite3
import uuid

import pytest

from app.metrics_collector import MetricsCollectorError, MetricsSnapshotRegression, SQLiteMetricsCollector


def snapshots(count=0, active=0):
    request = {
        "schema_version": 1,
        "requests": ([{"method": "GET", "route": "/health", "status_class": "2xx", "count": count}] if count else []),
        "latency_ms": ([{"method": "GET", "route": "/health", "count": count, "sum_ms": float(count * 2), "buckets": [{"le_ms": n, "count": count if n >= 5 else 0} for n in (5,10,25,50,100,250,500,1000,2500,5000)] + [{"le_ms": None, "count": count}]}] if count else []),
    }
    websocket = {
        "schema_version": 1, "connections_started": count, "connections_active": active,
        "connections_completed": count, "connections_accepted": count, "peer_disconnects": 0,
        "duration_sum_ms": float(count * 3),
        "close_code_classes": {"1xxx": count, "2xxx": 0, "4xxx": 0, "5xxx": 0, "other": 0},
    }
    return request, websocket


def test_combines_workers_and_repeated_snapshots_are_idempotent(tmp_path):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    a, b = uuid.uuid4().hex, uuid.uuid4().hex
    req_a, ws_a = snapshots(5, 2)
    req_b, ws_b = snapshots(7, 3)
    collector.flush(a, req_a, ws_a, now=900)
    collector.flush(a, req_a, ws_a, now=901)
    collector.flush(b, req_b, ws_b, now=902)
    result = collector.snapshot(now=903)
    assert result["worker_count"] == 2
    assert result["active_websocket_connections"] == 5
    assert result["series"]["http.requests|GET|/health|2xx"] == 12
    assert result["series"]["websocket|connections_completed"] == 12


def test_failed_transaction_does_not_advance_checkpoint(tmp_path, monkeypatch):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    worker = uuid.uuid4().hex
    baseline_req, baseline_ws = snapshots(1)
    collector.flush(worker, baseline_req, baseline_ws, now=900)
    req, ws = snapshots(3)
    original = collector._add
    def fail(*args):
        raise sqlite3.OperationalError("simulated failure")
    monkeypatch.setattr(collector, "_add", fail)
    with pytest.raises(sqlite3.OperationalError):
        collector.flush(worker, req, ws, now=901)
    monkeypatch.setattr(collector, "_add", original)
    collector.flush(worker, req, ws, now=902)
    assert collector.snapshot(now=903)["series"]["http.requests|GET|/health|2xx"] == 3


def test_counter_regression_is_rejected_without_mutating_aggregate(tmp_path):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    worker = uuid.uuid4().hex
    req, ws = snapshots(10)
    collector.flush(worker, req, ws, now=900)
    lower_req, lower_ws = snapshots(4)
    with pytest.raises(MetricsSnapshotRegression):
        collector.flush(worker, lower_req, lower_ws, now=901)
    assert collector.snapshot(now=902)["series"]["http.requests|GET|/health|2xx"] == 10


def test_stale_worker_expires_from_live_gauge_but_history_remains(tmp_path):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    req, ws = snapshots(2, 4)
    collector.flush(uuid.uuid4().hex, req, ws, now=900)
    assert collector.snapshot(now=989)["active_websocket_connections"] == 4
    stale = collector.snapshot(now=991)
    assert stale["active_websocket_connections"] == 0
    assert stale["worker_count"] == 0
    assert stale["series"]["http.requests|GET|/health|2xx"] == 2


def test_rejects_invalid_worker_and_dimensions(tmp_path):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    req, ws = snapshots(1)
    with pytest.raises(MetricsCollectorError):
        collector.flush("invalid", req, ws, now=900)
    req["requests"][0]["method"] = "TRACE"
    with pytest.raises(MetricsCollectorError):
        collector.flush(uuid.uuid4().hex, req, ws, now=900)



def test_worker_generation_cap_evicts_stale_checkpoints_with_tombstones(tmp_path):
    import json

    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    req, ws = snapshots(2)
    collector.flush(uuid.uuid4().hex, req, ws, now=900)
    db = collector._connect()
    stale_ids = [uuid.uuid4().hex for _ in range(255)]
    try:
        db.executemany(
            "INSERT INTO metrics_workers(worker_id,snapshot_json,last_seen,active_connections) VALUES(?,?,?,?)",
            [(worker_id, json.dumps({}), index, 0) for index, worker_id in enumerate(stale_ids)],
        )
    finally:
        db.close()

    replacement_worker = uuid.uuid4().hex
    collector.flush(replacement_worker, req, ws, now=1000)
    result = collector.snapshot(now=1001)
    assert result["worker_count"] == 1
    assert result["series"]["http.requests|GET|/health|2xx"] == 4
    with pytest.raises(MetricsSnapshotRegression):
        collector.flush(stale_ids[0], req, ws, now=1002)


def test_live_worker_limit_is_enforced(tmp_path):
    import json

    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    db = collector._connect()
    live_ids = [uuid.uuid4().hex for _ in range(16)]
    try:
        db.executemany(
            "INSERT INTO metrics_workers(worker_id,snapshot_json,last_seen,active_connections) VALUES(?,?,?,?)",
            [(worker_id, json.dumps({}), 900, 0) for worker_id in live_ids],
        )
    finally:
        db.close()
    req, ws = snapshots(1)
    with pytest.raises(MetricsCollectorError, match="live_worker_limit_exceeded"):
        collector.flush(uuid.uuid4().hex, req, ws, now=901)


def test_snapshot_hides_data_outside_retention_even_without_a_new_flush(tmp_path):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    req, ws = snapshots(3)
    collector.flush(uuid.uuid4().hex, req, ws, now=900)
    result = collector.snapshot(now=900 + 604800 + 900)
    assert result["series"] == {}
    assert result["oldest_bucket"] is None


def test_worker_timestamp_regression_does_not_mutate_checkpoint(tmp_path):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    worker = uuid.uuid4().hex
    req, ws = snapshots(4)
    collector.flush(worker, req, ws, now=900)
    lower_req, lower_ws = snapshots(5)
    with pytest.raises(MetricsSnapshotRegression, match="worker_timestamp_regressed"):
        collector.flush(worker, lower_req, lower_ws, now=899)
    assert collector.snapshot(now=901)["series"]["http.requests|GET|/health|2xx"] == 4


def test_concurrent_workers_commit_without_losing_deltas(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    import time

    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    worker_ids = [uuid.uuid4().hex for _ in range(4)]
    barrier = Barrier(len(worker_ids))

    def flush_worker(worker_id):
        request, websocket = snapshots(5)
        barrier.wait(timeout=5)
        for attempt in range(6):
            try:
                collector.flush(worker_id, request, websocket, now=900 + attempt)
                return
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc).lower() or attempt == 5:
                    raise
                time.sleep(0.01 * (2 ** attempt))
        raise AssertionError("bounded SQLite retry loop exhausted")

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(flush_worker, worker_ids))

    result = collector.snapshot(now=910)
    assert result["worker_count"] == 4
    assert result["series"]["http.requests|GET|/health|2xx"] == 20
    assert result["series"]["websocket|connections_completed"] == 20


def test_busy_database_does_not_advance_checkpoint_and_recovers(tmp_path):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    worker = uuid.uuid4().hex
    request, websocket = snapshots(3)
    blocker = collector._connect()
    try:
        blocker.execute("BEGIN IMMEDIATE")
        with pytest.raises(sqlite3.OperationalError, match="locked"):
            collector.flush(worker, request, websocket, now=900)
        blocker.rollback()
    finally:
        blocker.close()

    collector.flush(worker, request, websocket, now=901)
    result = collector.snapshot(now=902)
    assert result["series"]["http.requests|GET|/health|2xx"] == 3
    assert result["worker_count"] == 1


def test_corrupt_metrics_database_fails_without_overwriting_file(tmp_path):
    database = tmp_path / "metrics.sqlite3"
    sentinel = b"not-a-valid-sqlite-database"
    database.write_bytes(sentinel)
    collector = SQLiteMetricsCollector(str(database))
    request, websocket = snapshots(1)

    with pytest.raises(sqlite3.DatabaseError):
        collector.flush(uuid.uuid4().hex, request, websocket, now=900)

    assert database.read_bytes() == sentinel
