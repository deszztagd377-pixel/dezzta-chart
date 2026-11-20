"""Generation-scoped Redis lease for exclusive gateway replica consumption.

The lease uses SET NX PX for acquisition and token-checked Lua scripts for
renewal, ownership checks, and release. Lease loss is fail-closed.
"""
from __future__ import annotations

import hashlib
import secrets
import threading
from typing import Any


_RENEW_SCRIPT = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('PEXPIRE', KEYS[1], ARGV[2])
end
return 0
"""
_CHECK_SCRIPT = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return 1
end
return 0
"""
_RELEASE_SCRIPT = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
end
return 0
"""


class RedisOhlcvConsumerLeaseUnavailable(RuntimeError):
    """Another process owns this replica consumer group or Redis is unavailable."""


class RedisOhlcvConsumerLeaseLost(RuntimeError):
    """This process can no longer prove exclusive ownership of its consumer group."""


class RedisOhlcvConsumerLease:
    """One token-fenced lease per generation-scoped Redis consumer group."""

    def __init__(
        self,
        redis_client: Any,
        *,
        group_name: str,
        ttl_ms: int = 15_000,
        renewal_interval_ms: int | None = None,
    ) -> None:
        if redis_client is None:
            raise ValueError("redis_client is required.")
        if not isinstance(group_name, str) or not group_name.strip():
            raise ValueError("group_name must be a non-empty string.")
        if type(ttl_ms) is not int or not 3_000 <= ttl_ms <= 120_000:
            raise ValueError("ttl_ms must be between 3000 and 120000.")
        interval = ttl_ms // 3 if renewal_interval_ms is None else renewal_interval_ms
        if type(interval) is not int or not 250 <= interval < ttl_ms:
            raise ValueError("renewal_interval_ms must be at least 250 and below ttl_ms.")
        self.redis = redis_client
        self.group_name = group_name
        digest = hashlib.sha256(group_name.encode("utf-8")).hexdigest()
        self.key = f"dezzta:ohlcv:gateway-lease:{digest}"
        self.ttl_ms = ttl_ms
        self.renewal_interval_ms = interval
        self._token = secrets.token_urlsafe(32)
        self._acquired = False
        self._lost = threading.Event()
        self._stop = threading.Event()
        self._heartbeat_thread: threading.Thread | None = None
        self._lock = threading.RLock()

    @property
    def lost(self) -> bool:
        return self._lost.is_set()

    def acquire(self) -> None:
        with self._lock:
            if self._acquired:
                self.assert_owned()
                return
            try:
                result = self.redis.set(
                    self.key, self._token, nx=True, px=self.ttl_ms,
                )
            except Exception as exc:
                raise RedisOhlcvConsumerLeaseUnavailable(
                    "Redis consumer ownership could not be acquired."
                ) from exc
            if not result:
                raise RedisOhlcvConsumerLeaseUnavailable(
                    "Another process owns this Redis replica consumer group."
                )
            self._acquired = True
            self._lost.clear()

    def assert_owned(self) -> None:
        if not self._acquired or self._lost.is_set():
            raise RedisOhlcvConsumerLeaseLost("Redis replica consumer ownership was lost.")
        try:
            valid = self.redis.eval(_CHECK_SCRIPT, 1, self.key, self._token)
        except Exception as exc:
            self._lost.set()
            raise RedisOhlcvConsumerLeaseLost(
                "Redis replica consumer ownership could not be verified."
            ) from exc
        if int(valid or 0) != 1:
            self._lost.set()
            raise RedisOhlcvConsumerLeaseLost("Redis replica consumer ownership was lost.")

    def renew(self) -> bool:
        if not self._acquired or self._lost.is_set():
            return False
        try:
            renewed = self.redis.eval(
                _RENEW_SCRIPT, 1, self.key, self._token, self.ttl_ms,
            )
        except Exception:
            self._lost.set()
            return False
        if int(renewed or 0) != 1:
            self._lost.set()
            return False
        return True

    def start_heartbeat(self) -> None:
        self.assert_owned()
        with self._lock:
            if self._heartbeat_thread is not None and self._heartbeat_thread.is_alive():
                return
            self._stop.clear()

            def run() -> None:
                while not self._stop.wait(self.renewal_interval_ms / 1000):
                    if not self.renew():
                        self._lost.set()
                        return

            self._heartbeat_thread = threading.Thread(
                target=run, name="dezzta-ohlcv-lease-renewal", daemon=True,
            )
            self._heartbeat_thread.start()

    def stop_heartbeat(self, *, timeout_seconds: float = 2.0) -> bool:
        self._stop.set()
        thread = self._heartbeat_thread
        if thread is None:
            return True
        if thread is threading.current_thread():
            return False
        thread.join(timeout=timeout_seconds)
        return not thread.is_alive()

    def release(self) -> bool:
        self.stop_heartbeat()
        if not self._acquired:
            return True
        try:
            released = self.redis.eval(
                _RELEASE_SCRIPT, 1, self.key, self._token,
            )
        except Exception:
            self._lost.set()
            return False
        self._acquired = False
        return int(released or 0) == 1
