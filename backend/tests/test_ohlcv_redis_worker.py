from __future__ import annotations

import asyncio
import threading

import pytest

from app.ohlcv_event_loop import EventLoopCallbackDispatcher
from app.ohlcv_redis_consumer import ReplicaResnapshotRequired
from app.ohlcv_redis_worker import RedisOhlcvGatewayWorker


class FakeConsumer:
    def __init__(self, callback=None, *, block_ms=None):
        self.on_event_applied = callback
        self.block_ms = block_ms
        self.calls = 0

    def consume_once(self):
        self.calls += 1
        return {"status": "idle"}


def _wait_for_calls(consumer, minimum):
    import time

    deadline = time.monotonic() + 1
    while time.monotonic() < deadline:
        if consumer.calls >= minimum:
            return
        time.sleep(0.005)
    raise AssertionError("worker did not call consume_once()")


def test_worker_starts_runs_and_stops_without_blocking_event_loop():
    async def scenario():
        consumer = FakeConsumer()
        dispatcher = EventLoopCallbackDispatcher(
            asyncio.get_running_loop(), lambda _event: None,
        )
        worker = RedisOhlcvGatewayWorker(
            consumer, dispatcher, poll_interval_seconds=0.01,
        )
        worker.start()
        await asyncio.to_thread(_wait_for_calls, consumer, 1)
        assert consumer.on_event_applied == dispatcher.dispatch
        assert worker.state["state"] == "running"
        assert await worker.stop_async(timeout_seconds=2)
        assert worker.state["state"] == "stopped"
        assert worker.state["thread_alive"] is False

    asyncio.run(scenario())


def test_worker_recovers_from_transient_error_with_bounded_backoff():
    async def scenario():
        recovered = threading.Event()

        class FlakyConsumer(FakeConsumer):
            def consume_once(self):
                self.calls += 1
                if self.calls == 1:
                    raise ConnectionError("simulated Redis outage")
                recovered.set()
                return {"status": "idle"}

        consumer = FlakyConsumer()
        dispatcher = EventLoopCallbackDispatcher(
            asyncio.get_running_loop(), lambda _event: None,
        )
        worker = RedisOhlcvGatewayWorker(
            consumer, dispatcher,
            poll_interval_seconds=0.01,
            initial_backoff_seconds=0.01,
            max_backoff_seconds=0.02,
        )
        worker.start()
        assert await asyncio.to_thread(recovered.wait, 1)
        assert worker.state["state"] == "running"
        assert worker.state["last_error_type"] is None
        assert await worker.stop_async(timeout_seconds=2)

    asyncio.run(scenario())


def test_worker_stops_on_replica_gap_and_requires_new_snapshot():
    async def scenario():
        finished = threading.Event()

        class GapConsumer(FakeConsumer):
            def consume_once(self):
                self.calls += 1
                finished.set()
                raise ReplicaResnapshotRequired("sensitive detail must not leak")

        consumer = GapConsumer()
        dispatcher = EventLoopCallbackDispatcher(
            asyncio.get_running_loop(), lambda _event: None,
        )
        worker = RedisOhlcvGatewayWorker(consumer, dispatcher)
        worker.start()
        assert await asyncio.to_thread(finished.wait, 1)
        assert await worker.stop_async(timeout_seconds=2)
        state = worker.state
        assert state["state"] == "resnapshot_required"
        assert state["last_error_type"] == "ReplicaResnapshotRequired"
        with pytest.raises(RuntimeError, match="verified replica snapshot"):
            worker.start()

    asyncio.run(scenario())


@pytest.mark.parametrize("block_ms", [1001, 5000, 30_000])
def test_worker_rejects_unbounded_shutdown_blocking(block_ms):
    loop = asyncio.new_event_loop()
    try:
        dispatcher = EventLoopCallbackDispatcher(loop, lambda _event: None)
        with pytest.raises(ValueError, match="block_ms"):
            RedisOhlcvGatewayWorker(FakeConsumer(block_ms=block_ms), dispatcher)
    finally:
        loop.close()


def test_worker_rejects_invalid_backoff_relationship():
    loop = asyncio.new_event_loop()
    try:
        dispatcher = EventLoopCallbackDispatcher(loop, lambda _event: None)
        with pytest.raises(ValueError, match="max_backoff_seconds"):
            RedisOhlcvGatewayWorker(
                FakeConsumer(), dispatcher,
                initial_backoff_seconds=2, max_backoff_seconds=1,
            )
    finally:
        loop.close()
