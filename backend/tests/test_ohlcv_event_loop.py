from __future__ import annotations

import asyncio
import threading

import pytest

from app.ohlcv_event_loop import EventLoopCallbackDispatcher


@pytest.mark.asyncio
async def test_dispatch_runs_callback_on_owner_loop_before_returning():
    loop = asyncio.get_running_loop()
    owner_thread = threading.get_ident()
    observed = []
    dispatcher = EventLoopCallbackDispatcher(
        loop, lambda event: observed.append((event["cursor"], threading.get_ident())),
    )

    await asyncio.to_thread(dispatcher.dispatch, {"cursor": 17})

    assert observed == [(17, owner_thread)]


@pytest.mark.asyncio
async def test_dispatch_awaits_async_callback_before_returning():
    loop = asyncio.get_running_loop()
    observed = []

    async def callback(event):
        await asyncio.sleep(0)
        observed.append(event["cursor"])

    dispatcher = EventLoopCallbackDispatcher(loop, callback)
    await asyncio.to_thread(dispatcher.dispatch, {"cursor": 23})
    assert observed == [23]


@pytest.mark.asyncio
async def test_dispatch_propagates_callback_failure_to_prevent_ack():
    loop = asyncio.get_running_loop()

    def callback(_event):
        raise RuntimeError("simulated hub fanout failure")

    dispatcher = EventLoopCallbackDispatcher(loop, callback)
    with pytest.raises(RuntimeError, match="hub fanout failure"):
        await asyncio.to_thread(dispatcher.dispatch, {"cursor": 31})


@pytest.mark.asyncio
async def test_dispatch_rejects_blocking_call_from_owner_loop_thread():
    loop = asyncio.get_running_loop()
    dispatcher = EventLoopCallbackDispatcher(loop, lambda _event: None)
    with pytest.raises(RuntimeError, match="cannot block"):
        dispatcher.dispatch({"cursor": 1})


def test_dispatcher_rejects_closed_loop():
    loop = asyncio.new_event_loop()
    loop.close()
    with pytest.raises(RuntimeError, match="closed event loop"):
        EventLoopCallbackDispatcher(loop, lambda _event: None)
