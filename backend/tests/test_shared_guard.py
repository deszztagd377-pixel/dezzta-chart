from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest

from app.shared_guard import (
    HTTP_LIMIT_SCRIPT,
    WEBSOCKET_LEASE_SCRIPT,
    WEBSOCKET_RELEASE_SCRIPT,
    RedisSharedGuard,
)


class FakeRedis:
    def __init__(self):
        self.calls = []
        self.http_result = [1, 0]
        self.lease_result = 1
        self.error = None
        self.closed = False

    async def ping(self):
        if self.error:
            raise self.error
        return True

    async def eval(self, script, numkeys, *values):
        if self.error:
            raise self.error
        self.calls.append((script, numkeys, values))
        if script == HTTP_LIMIT_SCRIPT:
            return self.http_result
        if script == WEBSOCKET_LEASE_SCRIPT:
            return self.lease_result
        if script == WEBSOCKET_RELEASE_SCRIPT:
            return 1
        raise AssertionError("Unexpected Redis script")

    async def aclose(self):
        self.closed = True


def make_guard(redis):
    return RedisSharedGuard(
        "rediss://redis.example.invalid",
        http_per_client_per_minute=10,
        http_global_per_minute=100,
        websocket_global_limit=20,
        websocket_per_account_limit=2,
        websocket_lease_seconds=45,
        redis_client=redis,
    )


def test_start_requires_healthy_shared_store():
    asyncio.run(make_guard(FakeRedis()).start())


def test_start_fails_when_redis_is_unavailable():
    redis = FakeRedis()
    redis.error = ConnectionError("offline")
    with pytest.raises(ConnectionError):
        asyncio.run(make_guard(redis).start())


def test_http_limit_uses_atomic_script_and_hashed_client_key():
    redis = FakeRedis()
    result = asyncio.run(make_guard(redis).allow_http("203.0.113.7", now=120.0))
    assert result == (True, 0)
    script, key_count, args = redis.calls[0]
    assert script == HTTP_LIMIT_SCRIPT and key_count == 2
    assert "203.0.113.7" not in args[0]
    assert args[2:] == (10, 100, 65)


def test_http_limit_returns_retry_after_when_rejected():
    redis = FakeRedis()
    redis.http_result = [0, 17]
    result = asyncio.run(make_guard(redis).allow_http("client", now=120.0))
    assert result == (False, 17)


def test_http_limit_propagates_redis_failure():
    redis = FakeRedis()
    redis.error = TimeoutError("redis timeout")
    with pytest.raises(TimeoutError):
        asyncio.run(make_guard(redis).allow_http("client", now=120.0))


def test_websocket_reserves_global_slot_before_account_identity():
    redis = FakeRedis()
    assert asyncio.run(make_guard(redis).acquire_websocket("connection-1"))
    script, key_count, args = redis.calls[0]
    assert script == WEBSOCKET_LEASE_SCRIPT and key_count == 2
    assert args[-1] == "connection-1"
    assert args[1] == RedisSharedGuard.NO_ACCOUNT_KEY


def test_websocket_account_key_does_not_store_raw_subject():
    redis = FakeRedis()
    assert asyncio.run(
        make_guard(redis).acquire_websocket("connection-2", "firebase-user-private")
    )
    assert "firebase-user-private" not in redis.calls[0][2][1]


def test_websocket_cap_rejection_is_reported():
    redis = FakeRedis()
    redis.lease_result = 0
    assert not asyncio.run(make_guard(redis).acquire_websocket("connection-3"))


def test_websocket_renewal_and_release_use_atomic_scripts():
    redis = FakeRedis()
    guard = make_guard(redis)
    assert asyncio.run(guard.renew_websocket("connection-4", "account"))
    asyncio.run(guard.release_websocket("connection-4", "account"))
    assert redis.calls[0][0] == WEBSOCKET_LEASE_SCRIPT
    assert redis.calls[1][0] == WEBSOCKET_RELEASE_SCRIPT


def test_websocket_renewal_propagates_redis_failure():
    redis = FakeRedis()
    redis.error = ConnectionError("offline")
    with pytest.raises(ConnectionError):
        asyncio.run(make_guard(redis).renew_websocket("connection-5", "account"))


def test_close_releases_redis_client():
    redis = FakeRedis()
    asyncio.run(make_guard(redis).close())
    assert redis.closed


@pytest.mark.skipif(not os.getenv("REDIS_TEST_URL"), reason="CI Redis integration service is not configured")
def test_redis_lua_scripts_enforce_http_and_websocket_limits():
    from redis.asyncio import Redis

    async def exercise():
        redis = Redis.from_url(os.environ["REDIS_TEST_URL"], decode_responses=True)
        guard = RedisSharedGuard(
            os.environ["REDIS_TEST_URL"],
            http_per_client_per_minute=2,
            http_global_per_minute=2,
            websocket_global_limit=2,
            websocket_per_account_limit=1,
            websocket_lease_seconds=30,
            redis_client=redis,
        )
        suffix = uuid4().hex
        connections = []
        try:
            await guard.start()
            identity = f"redis-integration-{suffix}"
            assert await guard.allow_http(identity) == (True, 0)
            assert await guard.allow_http(identity) == (True, 0)
            assert (await guard.allow_http(identity))[0] is False

            first = f"ws-{suffix}-1"
            second = f"ws-{suffix}-2"
            third = f"ws-{suffix}-3"
            assert await guard.acquire_websocket(first, f"account-{suffix}-a")
            connections.append((first, f"account-{suffix}-a"))
            assert not await guard.acquire_websocket(second, f"account-{suffix}-a")
            assert await guard.acquire_websocket(second, f"account-{suffix}-b")
            connections.append((second, f"account-{suffix}-b"))
            assert not await guard.acquire_websocket(third, f"account-{suffix}-c")
        finally:
            for connection_id, subject in connections:
                await guard.release_websocket(connection_id, subject)
            await guard.close()

    asyncio.run(exercise())



@pytest.mark.parametrize(
    "limit_name",
    [
        "http_per_client_per_minute",
        "http_global_per_minute",
        "websocket_global_limit",
        "websocket_per_account_limit",
        "websocket_lease_seconds",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [True, False, 0, -1, 1.5, 0.5, "2", None],
)
def test_shared_guard_rejects_non_positive_or_non_integer_limits(
    limit_name, invalid_value
):
    with pytest.raises(ValueError, match="positive integers"):
        RedisSharedGuard(
            "rediss://redis.example.invalid",
            **{limit_name: invalid_value},
            redis_client=FakeRedis(),
        )
