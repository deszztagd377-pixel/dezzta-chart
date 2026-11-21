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
    req, ws = snapshots(3)
    original = collector._add
    def fail(*args):
        raise sqlite3.OperationalError("simulated failure")
    monkeypatch.setattr(collector, "_add", fail)
    with pytest.raises(sqlite3.OperationalError):
        collector.flush(worker, req, ws, now=900)
    monkeypatch.setattr(collector, "_add", original)
    collector.flush(worker, req, ws, now=901)
    assert collector.snapshot(now=902)["series"]["http.requests|GET|/health|2xx"] == 3


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
