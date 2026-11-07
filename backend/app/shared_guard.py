"""Redis-backed cross-instance HTTP and WebSocket security guards.

All shared counters and connection leases are updated through atomic Lua
scripts. Redis errors propagate to the FastAPI boundary, which fails closed.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any

HTTP_LIMIT_SCRIPT = """
-- dezzta:http-limit:v1
local client_count = redis.call('INCR', KEYS[1])
if client_count == 1 then redis.call('EXPIRE', KEYS[1], ARGV[3]) end
local client_ttl = redis.call('TTL', KEYS[1])
if client_count > tonumber(ARGV[1]) then
  return {0, math.max(client_ttl, 1)}
end
local global_count = redis.call('INCR', KEYS[2])
if global_count == 1 then redis.call('EXPIRE', KEYS[2], ARGV[3]) end
local global_ttl = redis.call('TTL', KEYS[2])
if global_count > tonumber(ARGV[2]) then
  return {0, math.max(global_ttl, 1)}
end
return {1, 0}
"""

WEBSOCKET_LEASE_SCRIPT = """
-- dezzta:websocket-lease:v1
local now_ms = tonumber(ARGV[1])
local expires_ms = now_ms + tonumber(ARGV[2])
local global_limit = tonumber(ARGV[3])
local account_limit = tonumber(ARGV[4])
local connection_id = ARGV[5]
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now_ms)
local global_existing = redis.call('ZSCORE', KEYS[1], connection_id)
if not global_existing and redis.call('ZCARD', KEYS[1]) >= global_limit then
  return 0
end
if KEYS[2] ~= 'dezzta:{guard-ws}:no-account' then
  redis.call('ZREMRANGEBYSCORE', KEYS[2], '-inf', now_ms)
  local account_existing = redis.call('ZSCORE', KEYS[2], connection_id)
  if not account_existing and redis.call('ZCARD', KEYS[2]) >= account_limit then
    return 0
  end
  redis.call('ZADD', KEYS[2], expires_ms, connection_id)
  redis.call('PEXPIRE', KEYS[2], tonumber(ARGV[2]) * 2)
end
redis.call('ZADD', KEYS[1], expires_ms, connection_id)
redis.call('PEXPIRE', KEYS[1], tonumber(ARGV[2]) * 2)
return 1
"""

WEBSOCKET_RELEASE_SCRIPT = """
-- dezzta:websocket-release:v1
redis.call('ZREM', KEYS[1], ARGV[1])
if KEYS[2] ~= 'dezzta:{guard-ws}:no-account' then
  redis.call('ZREM', KEYS[2], ARGV[1])
end
return 1
"""


class RedisSharedGuard:
    """Atomic HTTP fixed-window limits and leased WebSocket connection caps."""

    GLOBAL_WEBSOCKET_KEY = "dezzta:{guard-ws}:global"
    NO_ACCOUNT_KEY = "dezzta:{guard-ws}:no-account"

    def __init__(
        self,
        redis_url: str,
        *,
        http_per_client_per_minute: int = 120,
        http_global_per_minute: int = 6000,
        websocket_global_limit: int = 500,
        websocket_per_account_limit: int = 5,
        websocket_lease_seconds: int = 45,
        redis_client: Any | None = None,
    ) -> None:
        if not redis_url and redis_client is None:
            raise ValueError("A Redis URL or injected Redis client is required.")
        limits = (
            http_per_client_per_minute,
            http_global_per_minute,
            websocket_global_limit,
            websocket_per_account_limit,
            websocket_lease_seconds,
        )
        if any(value < 1 for value in limits):
            raise ValueError("Shared guard limits must all be positive integers.")

        self.http_per_client_per_minute = http_per_client_per_minute
        self.http_global_per_minute = http_global_per_minute
        self.websocket_global_limit = websocket_global_limit
        self.websocket_per_account_limit = websocket_per_account_limit
        self.websocket_lease_seconds = websocket_lease_seconds

        if redis_client is None:
            from redis.asyncio import Redis

            redis_client = Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
                health_check_interval=30,
                max_connections=100,
            )
        self._redis = redis_client

    async def start(self) -> None:
        """Verify Redis before the application starts serving requests."""
        if not await self._redis.ping():
            raise ConnectionError("Shared security store health check failed.")

    async def close(self) -> None:
        close = getattr(self._redis, "aclose", None) or getattr(self._redis, "close", None)
        if close is not None:
            result = close()
            if hasattr(result, "__await__"):
                await result

    @staticmethod
    def _digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    async def allow_http(
        self,
        client_identity: str,
        *,
        now: float | None = None,
    ) -> tuple[bool, int]:
        """Return (allowed, retry_after_seconds) for the shared minute window."""
        window = int((time.time() if now is None else now) // 60)
        client_digest = self._digest(client_identity or "unknown")
        result = await self._redis.eval(
            HTTP_LIMIT_SCRIPT,
            2,
            f"dezzta:{guard-http}:client:{client_digest}:{window}",
            f"dezzta:{guard-http}:global:{window}",
            self.http_per_client_per_minute,
            self.http_global_per_minute,
            65,
        )
        allowed = bool(int(result[0]))
        retry_after = max(1, int(result[1])) if not allowed else 0
        return allowed, retry_after

    def _account_key(self, account_subject: str) -> str:
        digest = self._digest(account_subject)
        return f"dezzta:{guard-ws}:account:{digest}"

    async def _write_websocket_lease(
        self,
        connection_id: str,
        account_subject: str | None,
    ) -> bool:
        account_key = (
            self._account_key(account_subject)
            if account_subject is not None
            else self.NO_ACCOUNT_KEY
        )
        result = await self._redis.eval(
            WEBSOCKET_LEASE_SCRIPT,
            2,
            self.GLOBAL_WEBSOCKET_KEY,
            account_key,
            int(time.time() * 1000),
            self.websocket_lease_seconds * 1000,
            self.websocket_global_limit,
            self.websocket_per_account_limit,
            connection_id,
        )
        return bool(int(result))

    async def acquire_websocket(
        self,
        connection_id: str,
        account_subject: str | None = None,
    ) -> bool:
        return await self._write_websocket_lease(connection_id, account_subject)

    async def renew_websocket(self, connection_id: str, account_subject: str) -> bool:
        return await self._write_websocket_lease(connection_id, account_subject)

    async def release_websocket(
        self,
        connection_id: str,
        account_subject: str | None = None,
    ) -> None:
        account_key = (
            self._account_key(account_subject)
            if account_subject is not None
            else self.NO_ACCOUNT_KEY
        )
        await self._redis.eval(
            WEBSOCKET_RELEASE_SCRIPT,
            2,
            self.GLOBAL_WEBSOCKET_KEY,
            account_key,
            connection_id,
        )
