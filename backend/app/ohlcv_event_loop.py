"""Thread-to-asyncio bridge for durable Redis consumer callbacks.

Redis consumers are synchronous workers. OhlcvPipeline and OhlcvStreamHub are
event-loop confined, so a consumer callback must be marshalled onto the owning
loop and awaited before the consumer is allowed to ACK the Redis entry.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import math
from typing import Any, Callable


class EventLoopCallbackDispatcher:
    """Synchronously wait for a callback to complete on its owning event loop.

    Construct this on the application loop and pass `dispatch` to the
    synchronous Redis consumer as its on_event_applied callback. The callback
    may be synchronous or asynchronous. Exceptions propagate to the consumer,
    preventing ACK. A timeout also prevents ACK; a retry remains safe only when
    the downstream handler uses the durable cursor fence.
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        callback: Callable[[dict[str, Any]], Any],
        *,
        timeout_seconds: float = 10.0,
    ) -> None:
        if not isinstance(loop, asyncio.AbstractEventLoop):
            raise TypeError("loop must be an asyncio event loop.")
        if not callable(callback):
            raise TypeError("callback must be callable.")
        if loop.is_closed():
            raise RuntimeError("Cannot bind a callback dispatcher to a closed event loop.")
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(float(timeout_seconds))
            or timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be a positive number.")
        self._loop = loop
        self._callback = callback
        self._timeout_seconds = float(timeout_seconds)

    async def _invoke(self, event: dict[str, Any]) -> None:
        result = self._callback(event)
        if inspect.isawaitable(result):
            await result

    def dispatch(self, event: dict[str, Any]) -> None:
        """Run callback on the owner loop; propagate failure before Redis ACK."""
        if not isinstance(event, dict):
            raise TypeError("event must be an object.")
        if self._loop.is_closed() or not self._loop.is_running():
            raise RuntimeError("The owning event loop is not running.")
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None
        if running_loop is self._loop:
            raise RuntimeError(
                "Synchronous dispatch cannot block the owning event-loop thread."
            )

        future = asyncio.run_coroutine_threadsafe(self._invoke(event), self._loop)
        try:
            future.result(timeout=self._timeout_seconds)
        except concurrent.futures.TimeoutError as exc:
            if future.done():
                # The callback itself raised TimeoutError; preserve its cause
                # rather than misreporting it as a dispatcher deadline.
                raise
            future.cancel()
            raise TimeoutError(
                "Event-loop callback did not complete before the ACK deadline."
            ) from exc
