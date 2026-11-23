from __future__ import annotations

import threading
import time

import pytest

from app.ohlcv_redis_lease import (
    RedisOhlcvConsumerLeaseLost,
    RedisOhlcvConsumerLeaseUnavailable,
)
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
    assert wait_until(lambda: worker.state["thread_alive"] is False)
    with pytest.raises(RuntimeError, match="verified replica snapshot"):
        worker.start()


def test_worker_preserves_ownership_lost_terminal_state_after_thread_exit():
    class LostLease:
        def start_heartbeat(self):
            return None

        def assert_owned(self):
            raise RedisOhlcvConsumerLeaseLost("ownership no longer belongs to this process")

        def stop_heartbeat(self):
            return True

    worker = RedisOhlcvGatewayWorker(
        FakeConsumer(lambda: {"status": "idle"}),
        FakeDispatcher(),
        ownership_lease=LostLease(),
    )
    worker.start()
    assert wait_until(lambda: worker.state["thread_alive"] is False)
    assert worker.state["state"] == "ownership_lost"
    assert worker.state["last_error_type"] == "RedisOhlcvConsumerLeaseLost"
    assert worker.stop(timeout_seconds=0.5) is True
    assert worker.state["state"] == "ownership_lost"


def test_worker_start_rolls_back_state_when_lease_heartbeat_cannot_start():
    consumed = []

    class UnavailableLease:
        def start_heartbeat(self):
            raise RedisOhlcvConsumerLeaseUnavailable("Redis is temporarily unavailable")

        def stop_heartbeat(self):
            raise AssertionError("Heartbeat cleanup must not run before it starts")

    worker = RedisOhlcvGatewayWorker(
        FakeConsumer(lambda: consumed.append(True) or {"status": "idle"}),
        FakeDispatcher(),
        ownership_lease=UnavailableLease(),
    )

    with pytest.raises(RedisOhlcvConsumerLeaseUnavailable):
        worker.start()

    assert worker.state == {
        "state": "stopped",
        "last_error_type": "RedisOhlcvConsumerLeaseUnavailable",
        "last_result_status": None,
        "thread_alive": False,
    }
    assert consumed == []


def test_worker_start_preserves_ownership_lost_when_lease_start_fails():
    class LostLease:
        def start_heartbeat(self):
            raise RedisOhlcvConsumerLeaseLost("lease token was replaced")

        def stop_heartbeat(self):
            return True

    worker = RedisOhlcvGatewayWorker(
        FakeConsumer(lambda: {"status": "idle"}),
        FakeDispatcher(),
        ownership_lease=LostLease(),
    )

    with pytest.raises(RedisOhlcvConsumerLeaseLost):
        worker.start()

    assert worker.state["state"] == "ownership_lost"
    assert worker.state["last_error_type"] == "RedisOhlcvConsumerLeaseLost"
    assert worker.state["thread_alive"] is False
