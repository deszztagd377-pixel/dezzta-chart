"""Managed background lifecycle for a synchronous Redis OHLCV replica consumer.

The opt-in FastAPI replica lifespan starts this worker only after installing
and verifying the replica snapshot, constructing an event-loop dispatcher on
the owning loop, and injecting a dedicated Redis client whose ACLs are
configured by the owner for least-privilege access.
"""
from __future__ import annotations

import asyncio
import math
import threading
from typing import Any


class RedisOhlcvGatewayWorker:
    """Run one sequential Redis consumer on a managed daemon thread.

    Callback exceptions are retried with bounded exponential backoff. The
    consumer's own-pending-first behavior ensures the failed cursor is retried
    before new entries. A replica gap/trim signal is terminal and transitions
    the worker to resnapshot_required rather than continuing from bad state.
    """

    def __init__(
        self,
        consumer: Any,
        dispatcher: Any,
        *,
        poll_interval_seconds: float = 0.05,
        initial_backoff_seconds: float = 0.25,
        max_backoff_seconds: float = 5.0,
        ownership_lease: Any | None = None,
    ) -> None:
        if not callable(getattr(consumer, "consume_once", None)):
            raise TypeError("consumer must provide consume_once().")
        if not hasattr(consumer, "on_event_applied"):
            raise TypeError("consumer must expose on_event_applied.")
        if not callable(getattr(dispatcher, "dispatch", None)):
            raise TypeError("dispatcher must provide dispatch().")
        block_ms = getattr(consumer, "block_ms", None)
        if block_ms is not None and (
            type(block_ms) is not int or not 1 <= block_ms <= 1_000
        ):
            raise ValueError("Managed worker requires block_ms=None or <= 1000.")
        for name, value, maximum in (
            ("poll_interval_seconds", poll_interval_seconds, 5.0),
            ("initial_backoff_seconds", initial_backoff_seconds, 30.0),
            ("max_backoff_seconds", max_backoff_seconds, 30.0),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or value <= 0
                or value > maximum
            ):
                raise ValueError(f"{name} must be finite and within (0, {maximum}].")
        if max_backoff_seconds < initial_backoff_seconds:
            raise ValueError("max_backoff_seconds must be >= initial_backoff_seconds.")

        self.consumer = consumer
        self.dispatcher = dispatcher
        self.ownership_lease = ownership_lease
        self.consumer.on_event_applied = dispatcher.dispatch
        self.poll_interval_seconds = float(poll_interval_seconds)
        self.initial_backoff_seconds = float(initial_backoff_seconds)
        self.max_backoff_seconds = float(max_backoff_seconds)
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._thread: threading.Thread | None = None
        self._state = "stopped"
        self._last_error_type: str | None = None
        self._last_result_status: str | None = None

    @property
    def state(self) -> dict[str, Any]:
        with self._lock:
            return {
                "state": self._state,
                "last_error_type": self._last_error_type,
                "last_result_status": self._last_result_status,
                "thread_alive": self._thread is not None and self._thread.is_alive(),
            }

    def _set_state(
        self,
        state: str,
        *,
        error_type: str | None = None,
        result_status: str | None = None,
    ) -> None:
        with self._lock:
            self._state = state
            self._last_error_type = error_type
            if result_status is not None:
                self._last_result_status = result_status

    def start(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError("Redis OHLCV gateway worker is already running.")
            if self._state == "resnapshot_required":
                raise RuntimeError("A new verified replica snapshot is required before restart.")
            self._stop_event.clear()
            self._state = "starting"
            self._last_error_type = None
            self._last_result_status = None
            if self.ownership_lease is not None:
                self.ownership_lease.start_heartbeat()
            self._thread = threading.Thread(
                target=self._run,
                name="dezzta-ohlcv-redis-consumer",
                daemon=True,
            )
            self._thread.start()

    def _run(self) -> None:
        from app.ohlcv_redis_consumer import ReplicaResnapshotRequired
        from app.ohlcv_redis_lease import RedisOhlcvConsumerLeaseLost

        backoff = self.initial_backoff_seconds
        try:
            self._set_state("running")
            while not self._stop_event.is_set():
                try:
                    if self.ownership_lease is not None:
                        self.ownership_lease.assert_owned()
                    result = self.consumer.consume_once()
                    status = result.get("status") if isinstance(result, dict) else None
                    self._set_state(
                        "running",
                        error_type=None,
                        result_status=status if isinstance(status, str) else "processed",
                    )
                    backoff = self.initial_backoff_seconds
                    if status == "idle":
                        self._stop_event.wait(self.poll_interval_seconds)
                except RedisOhlcvConsumerLeaseLost as exc:
                    self._set_state("ownership_lost", error_type=type(exc).__name__)
                    return
                except ReplicaResnapshotRequired as exc:
                    self._set_state(
                        "resnapshot_required",
                        error_type=type(exc).__name__,
                    )
                    return
                except Exception as exc:
                    self._set_state(
                        "degraded",
                        error_type=type(exc).__name__,
                    )
                    if self._stop_event.wait(backoff):
                        break
                    backoff = min(self.max_backoff_seconds, backoff * 2)
        finally:
            with self._lock:
                # Preserve terminal failure states for readiness/operations
                # diagnostics. A lost lease is not an ordinary clean stop.
                if self._state not in {"resnapshot_required", "ownership_lost"}:
                    self._state = "stopped"

    def stop(self, *, timeout_seconds: float = 3.0) -> bool:
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(float(timeout_seconds))
            or timeout_seconds <= 0
            or timeout_seconds > 30
        ):
            raise ValueError("timeout_seconds must be finite and within (0, 30].")
        with self._lock:
            thread = self._thread
            if thread is None:
                if self._state != "resnapshot_required":
                    self._state = "stopped"
                return True
            if thread is threading.current_thread():
                raise RuntimeError("Worker cannot synchronously join its own thread.")
            self._stop_event.set()
        thread.join(timeout=float(timeout_seconds))
        if thread.is_alive():
            self._set_state("stopping")
            return False
        if self.ownership_lease is not None:
            self.ownership_lease.stop_heartbeat()
        with self._lock:
            if self._state not in {"resnapshot_required", "ownership_lost"}:
                self._state = "stopped"
        return True

    async def stop_async(self, *, timeout_seconds: float = 3.0) -> bool:
        """Stop without blocking the FastAPI/event-loop thread."""
        return await asyncio.to_thread(
            self.stop, timeout_seconds=timeout_seconds,
        )
