from __future__ import annotations

import threading
import time

import pytest

from app.ohlcv_redis_consumer import ReplicaResnapshotRequired
from app.ohlcv_redis_worker import RedisOhlcvGatewayWorker


class FakeConsumer:
    def __init__(self, handler):
        self.handler = handler
        self.on_event_applied = None
        self.block_ms = None

    def consume_once(self):
        return self.handler()


class FakeDispatcher:
    def dispatch(self, event):
        return None


def wait_until(predicate, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return bool(predicate())


def test_worker_stop_timeout_reports_still_running_then_stops_cleanly():
    entered = threading.Event()
    release = threading.Event()

    def blocked_consume():
        entered.set()
        release.wait(timeout=3)
        return {"status": "idle"}

    worker = RedisOhlcvGatewayWorker(
        FakeConsumer(blocked_consume),
        FakeDispatcher(),
        poll_interval_seconds=0.005,
    )
    worker.start()
    assert entered.wait(timeout=1)

    # stop() must not claim shutdown while consume_once is still blocked.
    assert worker.stop(timeout_seconds=0.02) is False
    assert worker.state["state"] == "stopping"
    assert worker.state["thread_alive"] is True

    release.set()
    assert wait_until(lambda: worker.state["thread_alive"] is False)
    assert worker.stop(timeout_seconds=0.5) is True
    assert worker.state["state"] == "stopped"


def test_worker_retries_transient_consumer_failure_and_recovers():
    attempts = []
    recovered = threading.Event()

    def flaky_consume():
        attempts.append(len(attempts) + 1)
        if len(attempts) == 1:
            raise ConnectionError("temporary Redis outage")
        recovered.set()
        return {"status": "idle"}

    worker = RedisOhlcvGatewayWorker(
        FakeConsumer(flaky_consume),
        FakeDispatcher(),
        poll_interval_seconds=0.005,
        initial_backoff_seconds=0.005,
        max_backoff_seconds=0.02,
    )
    worker.start()
    try:
        assert recovered.wait(timeout=1)
        assert wait_until(lambda: worker.state["state"] == "running")
        assert len(attempts) >= 2
    finally:
        assert worker.stop(timeout_seconds=1) is True


def test_worker_resnapshot_required_is_terminal_until_rebuilt():
    entered = threading.Event()

    def require_snapshot():
        entered.set()
        raise ReplicaResnapshotRequired("replica checkpoint is no longer safe")

    worker = RedisOhlcvGatewayWorker(
        FakeConsumer(require_snapshot),
        FakeDispatcher(),
    )
    worker.start()
    assert entered.wait(timeout=1)
    assert wait_until(lambda: worker.state["state"] == "resnapshot_required")
    assert worker.state["thread_alive"] is False
    with pytest.raises(RuntimeError, match="verified replica snapshot"):
        worker.start()
