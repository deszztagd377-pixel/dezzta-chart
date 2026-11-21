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

    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    worker_ids = [uuid.uuid4().hex for _ in range(4)]
    barrier = Barrier(len(worker_ids))

    def flush_worker(worker_id):
        request, websocket = snapshots(5)
        barrier.wait(timeout=5)
        collector.flush(worker_id, request, websocket, now=900)

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



def test_flush_reports_bounded_lock_retries(tmp_path):
    import threading
    import time

    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    request, websocket = snapshots(2)
    lock_acquired = threading.Event()

    def hold_then_release_lock():
        blocker = collector._connect()
        try:
            blocker.execute("BEGIN IMMEDIATE")
            lock_acquired.set()
            time.sleep(0.35)
            blocker.rollback()
        finally:
            blocker.close()

    releaser = threading.Thread(target=hold_then_release_lock)
    releaser.start()
    assert lock_acquired.wait(timeout=3)
    try:
        result = collector.flush(uuid.uuid4().hex, request, websocket, now=900)
    finally:
        releaser.join(timeout=3)

    assert result["lock_retries"] >= 1
    assert result["lock_retries"] <= 7
    snapshot = collector.snapshot(now=901)
    assert snapshot["series"]["http.requests|GET|/health|2xx"] == 2

def test_write_failure_rolls_back_aggregate_and_worker_checkpoint(tmp_path):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    worker = uuid.uuid4().hex
    request, websocket = snapshots(1)
    collector.flush(worker, request, websocket, now=900)

    db = collector._connect()
    try:
        db.execute("""
            CREATE TRIGGER reject_metrics_bucket_insert
            BEFORE INSERT ON metrics_buckets
            BEGIN
                SELECT RAISE(ABORT, 'simulated_storage_write_failure');
            END
        """)
    finally:
        db.close()

    next_request, next_websocket = snapshots(4)
    with pytest.raises(sqlite3.IntegrityError, match="simulated_storage_write_failure"):
        collector.flush(worker, next_request, next_websocket, now=901)

    db = collector._connect()
    try:
        db.execute("DROP TRIGGER reject_metrics_bucket_insert")
    finally:
        db.close()

    collector.flush(worker, next_request, next_websocket, now=902)
    result = collector.snapshot(now=903)
    assert result["series"]["http.requests|GET|/health|2xx"] == 4
    assert result["series"]["websocket|connections_completed"] == 4


def test_concurrent_collector_instances_initialize_shared_database(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    database_path = str(tmp_path / "shared-metrics.sqlite3")
    worker_ids = [uuid.uuid4().hex for _ in range(4)]
    barrier = Barrier(len(worker_ids))

    def flush_worker(worker_id):
        collector = SQLiteMetricsCollector(database_path)
        request, websocket = snapshots(5)
        barrier.wait(timeout=5)
        collector.flush(worker_id, request, websocket, now=900)

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(flush_worker, worker_ids))

    result = SQLiteMetricsCollector(database_path).snapshot(now=901)
    assert result["worker_count"] == 4
    assert result["series"]["http.requests|GET|/health|2xx"] == 20
    assert result["series"]["websocket|connections_completed"] == 20


def test_corrupt_metrics_database_fails_without_overwriting_file(tmp_path):
    database = tmp_path / "metrics.sqlite3"
    sentinel = b"not-a-valid-sqlite-database"
    database.write_bytes(sentinel)
    collector = SQLiteMetricsCollector(str(database))
    request, websocket = snapshots(1)

    with pytest.raises(sqlite3.DatabaseError):
        collector.flush(uuid.uuid4().hex, request, websocket, now=900)

    assert database.read_bytes() == sentinel


def test_read_only_storage_rejects_flush_without_advancing_checkpoint(tmp_path, monkeypatch):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    worker = uuid.uuid4().hex
    baseline_request, baseline_websocket = snapshots(1)
    collector.flush(worker, baseline_request, baseline_websocket, now=900)
    original_connect = collector._connect

    def read_only_connect():
        connection = original_connect()
        connection.execute("PRAGMA query_only=ON")
        return connection

    monkeypatch.setattr(collector, "_connect", read_only_connect)
    next_request, next_websocket = snapshots(3)
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        collector.flush(worker, next_request, next_websocket, now=901)

    monkeypatch.setattr(collector, "_connect", original_connect)
    unchanged = collector.snapshot(now=902)
    assert unchanged["series"]["http.requests|GET|/health|2xx"] == 1
    collector.flush(worker, next_request, next_websocket, now=903)
    recovered = collector.snapshot(now=904)
    assert recovered["series"]["http.requests|GET|/health|2xx"] == 3


def test_real_sqlite_page_limit_failure_rolls_back_and_recovers(tmp_path, monkeypatch):
    collector = SQLiteMetricsCollector(str(tmp_path / "metrics.sqlite3"))
    worker = uuid.uuid4().hex
    statuses = ("1xx", "2xx", "3xx", "4xx", "5xx", "other")
    limits = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000)

    def full_snapshots(count):
        routes = [f"/capacity/{index:03d}" for index in range(127)]
        request = {
            "schema_version": 1,
            "requests": [
                {"method": "GET", "route": route, "status_class": status, "count": count}
                for route in routes for status in statuses
            ],
            "latency_ms": [
                {
                    "method": "GET", "route": route, "count": count,
                    "sum_ms": float(count * 2),
                    "buckets": [
                        {"le_ms": limit, "count": count if limit >= 5 else 0}
                        for limit in limits
                    ] + [{"le_ms": None, "count": count}],
                }
                for route in routes
            ],
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

    baseline_request, baseline_websocket = full_snapshots(1)
    next_request, next_websocket = full_snapshots(2)
    baseline = collector.flush(worker, baseline_request, baseline_websocket, now=900)
    assert baseline["series"] == 899

    original_connect = collector._connect
    db = original_connect()
    try:
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        db.execute("VACUUM")
        page_count = db.execute("PRAGMA page_count").fetchone()[0]
        assert page_count > 0
        assert db.execute("PRAGMA freelist_count").fetchone()[0] == 0
    finally:
        db.close()

    def disk_limited_connect():
        connection = original_connect()
        applied_limit = connection.execute(f"PRAGMA max_page_count={page_count}").fetchone()[0]
        assert applied_limit == page_count
        return connection

    monkeypatch.setattr(collector, "_connect", disk_limited_connect)
    with pytest.raises(sqlite3.OperationalError, match="database or disk is full"):
        collector.flush(worker, next_request, next_websocket, now=1800)

    monkeypatch.setattr(collector, "_connect", original_connect)
    after_failure = collector.snapshot(now=1801)
    assert after_failure["series"]["http.requests|GET|/capacity/000|1xx"] == 1
    assert after_failure["worker_count"] == 1

    recovered = collector.flush(worker, next_request, next_websocket, now=1802)
    assert recovered["series"] == 899
    after_recovery = collector.snapshot(now=1803)
    assert after_recovery["series"]["http.requests|GET|/capacity/000|1xx"] == 2
    assert after_recovery["series"]["websocket|connections_completed"] == 2
