from __future__ import annotations

import asyncio
import threading

import pytest

from app.ohlcv_event_loop import EventLoopCallbackDispatcher


def test_dispatch_runs_callback_on_owner_loop_before_returning():
    async def scenario():
        loop = asyncio.get_running_loop()
        owner_thread = threading.get_ident()
        observed = []
        dispatcher = EventLoopCallbackDispatcher(
            loop, lambda event: observed.append((event["cursor"], threading.get_ident())),
        )

        await asyncio.to_thread(dispatcher.dispatch, {"cursor": 17})
        assert observed == [(17, owner_thread)]

    asyncio.run(scenario())


def test_dispatch_awaits_async_callback_before_returning():
    async def scenario():
        loop = asyncio.get_running_loop()
        observed = []

        async def callback(event):
            await asyncio.sleep(0)
            observed.append(event["cursor"])

        dispatcher = EventLoopCallbackDispatcher(loop, callback)
        await asyncio.to_thread(dispatcher.dispatch, {"cursor": 23})
        assert observed == [23]

    asyncio.run(scenario())


def test_dispatch_propagates_callback_failure_to_prevent_ack():
    async def scenario():
        loop = asyncio.get_running_loop()

        def callback(_event):
            raise RuntimeError("simulated hub fanout failure")

        dispatcher = EventLoopCallbackDispatcher(loop, callback)
        with pytest.raises(RuntimeError, match="hub fanout failure"):
            await asyncio.to_thread(dispatcher.dispatch, {"cursor": 31})

    asyncio.run(scenario())


def test_dispatch_rejects_blocking_call_from_owner_loop_thread():
    async def scenario():
        loop = asyncio.get_running_loop()
        dispatcher = EventLoopCallbackDispatcher(loop, lambda _event: None)
        with pytest.raises(RuntimeError, match="cannot block"):
            dispatcher.dispatch({"cursor": 1})

    asyncio.run(scenario())


def test_dispatcher_rejects_closed_loop():
    loop = asyncio.new_event_loop()
    loop.close()
    with pytest.raises(RuntimeError, match="closed event loop"):
        EventLoopCallbackDispatcher(loop, lambda _event: None)


def test_dispatch_preserves_timeout_raised_by_callback():
    async def scenario():
        loop = asyncio.get_running_loop()

        def callback(_event):
            raise TimeoutError("callback's own timeout")

        dispatcher = EventLoopCallbackDispatcher(loop, callback)
        with pytest.raises(TimeoutError, match="callback's own timeout"):
            await asyncio.to_thread(dispatcher.dispatch, {"cursor": 41})

    asyncio.run(scenario())


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), float("-inf"), 0, -1])
def test_dispatcher_rejects_non_finite_or_non_positive_timeout(timeout):
    loop = asyncio.new_event_loop()
    try:
        with pytest.raises(ValueError, match="positive number"):
            EventLoopCallbackDispatcher(
                loop, lambda _event: None, timeout_seconds=timeout,
            )
    finally:
        loop.close()


def test_dispatcher_timeout_cancels_pending_async_callback_before_returning():
    async def scenario():
        loop = asyncio.get_running_loop()
        started = threading.Event()
        cancelled = threading.Event()

        async def callback(_event):
            started.set()
            try:
                await asyncio.sleep(10)
            finally:
                cancelled.set()

        dispatcher = EventLoopCallbackDispatcher(
            loop, callback, timeout_seconds=0.03,
        )
        with pytest.raises(TimeoutError, match="ACK deadline"):
            await asyncio.to_thread(dispatcher.dispatch, {"cursor": 8})
        assert started.is_set()
        deadline = loop.time() + 1
        while not cancelled.is_set() and loop.time() < deadline:
            await asyncio.sleep(0.005)
        assert cancelled.is_set()

    asyncio.run(scenario())
