from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest

from app.shared_guard import (
    HTTP_LIMIT_SCRIPT,
    WEBSOCKET_LEASE_SCRIPT,
    WEBSOCKET_RENEW_SCRIPT,
    WEBSOCKET_RELEASE_SCRIPT,
    WEBSOCKET_TICKET_CONSUME_SCRIPT,
    RedisSharedGuard,
)




def _redis_guard_process_worker(redis_url, ticket, account, connection_id, ready_queue, start_event, result_queue):
    """Run an independent backend-process guard against shared Redis."""
    async def exercise():
        from redis.asyncio import Redis
        redis = Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=3, socket_timeout=3)
        guard = RedisSharedGuard(redis_url, websocket_global_limit=4, websocket_per_account_limit=1, websocket_lease_seconds=30, redis_client=redis)
        try:
            await guard.start()
            ready_queue.put(("ready", connection_id))
            if not start_event.wait(timeout=15):
                raise TimeoutError("cross-process Redis test start barrier timed out")
            consumed = await guard.consume_websocket_ticket(ticket)
            # A process that did not consume the one-time ticket must not try
            # to reserve an authenticated account lease.
            acquired = (
                await guard.acquire_websocket(connection_id, consumed)
                if consumed == account else False
            )
            result_queue.put(("result", connection_id, consumed, acquired))
        except Exception as exc:
            result_queue.put(("error", connection_id, exc.__class__.__name__))
        finally:
            await guard.close()
    asyncio.run(exercise())

class FakeRedis:
    def __init__(self):
        self.calls = []
        self.http_result = [1, 0]
        self.lease_result = 1
        self.renew_result = 1
        self.error = None
        self.closed = False
        self.ticket_values = {}
        self.ticket_set_calls = []

    async def ping(self):
        if self.error:
            raise self.error
        return True

    async def set(self, key, value, *, ex, nx):
        if self.error:
            raise self.error
        self.ticket_set_calls.append((key, value, ex, nx))
        if nx and key in self.ticket_values:
            return None
        self.ticket_values[key] = value
        return True

    async def eval(self, script, numkeys, *values):
        if self.error:
            raise self.error
        self.calls.append((script, numkeys, values))
        if script == HTTP_LIMIT_SCRIPT:
            return self.http_result
        if script == WEBSOCKET_LEASE_SCRIPT:
            return self.lease_result
        if script == WEBSOCKET_RENEW_SCRIPT:
            return self.renew_result
        if script == WEBSOCKET_RELEASE_SCRIPT:
            return 1
        if script == WEBSOCKET_TICKET_CONSUME_SCRIPT:
            return self.ticket_values.pop(values[0], None)
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
    assert redis.calls[0][0] == WEBSOCKET_RENEW_SCRIPT
    assert redis.calls[1][0] == WEBSOCKET_RELEASE_SCRIPT

def test_websocket_renewal_rejects_missing_or_expired_lease():
    redis = FakeRedis()
    redis.renew_result = 0
    assert not asyncio.run(make_guard(redis).renew_websocket("expired-connection", "account"))
    assert redis.calls[0][0] == WEBSOCKET_RENEW_SCRIPT


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


def test_rediss_client_enforces_certificate_and_hostname_validation(monkeypatch):
    from redis.asyncio import Redis

    captured = {}

    def fake_from_url(cls, url, **options):
        captured["url"] = url
        captured["options"] = options
        return FakeRedis()

    monkeypatch.setattr(Redis, "from_url", classmethod(fake_from_url))

    RedisSharedGuard("rediss://redis.example.invalid:6380/0")

    assert captured["url"] == "rediss://redis.example.invalid:6380/0"
    assert captured["options"]["ssl_cert_reqs"] == "required"
    assert captured["options"]["ssl_check_hostname"] is True
    assert captured["options"]["socket_connect_timeout"] == 2



@pytest.mark.skipif(
    not os.getenv("REDIS_TEST_URL"),
    reason="CI Redis integration service is not configured",
)
def test_redis_websocket_lease_renewal_and_expiry_are_enforced(monkeypatch):
    """Exercise lease renewal and expiry against Redis, not the fake client."""
    from types import SimpleNamespace

    from redis.asyncio import Redis
    import app.shared_guard as shared_guard_module

    logical_time = [1_000.0]
    monkeypatch.setattr(
        shared_guard_module,
        "time",
        SimpleNamespace(time=lambda: logical_time[0]),
    )

    async def exercise():
        redis = Redis.from_url(os.environ["REDIS_TEST_URL"], decode_responses=True)
        guard = RedisSharedGuard(
            os.environ["REDIS_TEST_URL"],
            websocket_global_limit=2,
            websocket_per_account_limit=1,
            websocket_lease_seconds=1,
            redis_client=redis,
        )
        suffix = uuid4().hex
        first = f"ws-lease-{suffix}-first"
        second = f"ws-lease-{suffix}-second"
        account = f"lease-account-{suffix}"
        connections = []
        try:
            await guard.start()
            assert await guard.acquire_websocket(first, account)
            connections.append((first, account))
            assert not await guard.acquire_websocket(second, account)

            # Renewal extends the first lease from t=1001 to t=1001.6.
            logical_time[0] = 1_000.6
            assert await guard.renew_websocket(first, account)

            # The original expiry has passed, but the renewed lease is active.
            logical_time[0] = 1_001.1
            assert not await guard.acquire_websocket(second, account)

            # Once the renewed lease expires, the same account can reconnect.
            logical_time[0] = 1_001.7
            assert not await guard.renew_websocket(first, account)
            assert await guard.acquire_websocket(second, account)
            connections.append((second, account))
        finally:
            for connection_id, subject in connections:
                await guard.release_websocket(connection_id, subject)
            await guard.close()

    asyncio.run(exercise())


def test_plain_redis_client_does_not_enable_tls_options(monkeypatch):
    from redis.asyncio import Redis

    captured = {}

    def fake_from_url(cls, url, **options):
        captured["url"] = url
        captured["options"] = options
        return FakeRedis()

    monkeypatch.setattr(Redis, "from_url", classmethod(fake_from_url))

    RedisSharedGuard("redis://localhost:6379/0")

    assert captured["url"] == "redis://localhost:6379/0"
    assert "ssl_cert_reqs" not in captured["options"]
    assert "ssl_check_hostname" not in captured["options"]
    assert captured["options"]["socket_connect_timeout"] == 2

def test_websocket_ticket_is_digest_keyed_single_use_and_subject_bound():
    redis = FakeRedis()
    guard = make_guard(redis)
    ticket = asyncio.run(guard.issue_websocket_ticket("verified-account"))
    assert ticket not in repr(redis.ticket_values)
    assert len(redis.ticket_values) == 1
    assert asyncio.run(guard.consume_websocket_ticket(ticket)) == "verified-account"
    assert asyncio.run(guard.consume_websocket_ticket(ticket)) is None


def test_websocket_ticket_storage_uses_digest_key_exact_ttl_and_create_only_write():
    redis = FakeRedis()
    guard = make_guard(redis)
    ticket = asyncio.run(guard.issue_websocket_ticket("verified-account"))

    assert len(redis.ticket_set_calls) == 1
    key, raw_value, ttl, create_only = redis.ticket_set_calls[0]
    assert key == f"dezzta:{{guard-ws}}:ticket:{guard._digest(ticket)}"
    assert ticket not in key
    assert ttl == 90
    assert create_only is True
    assert raw_value == '{"purpose":"market-data","subject":"verified-account"}'


def test_websocket_ticket_rejects_corrupt_stored_payload_and_consumes_it():
    redis = FakeRedis()
    guard = make_guard(redis)
    ticket = "T" * 43
    key = f"dezzta:{{guard-ws}}:ticket:{guard._digest(ticket)}"
    redis.ticket_values[key] = '{"subject":'
    
    assert asyncio.run(guard.consume_websocket_ticket(ticket)) is None
    assert key not in redis.ticket_values


def test_websocket_ticket_rejects_malformed_and_wrong_purpose():
    redis = FakeRedis()
    guard = make_guard(redis)
    ticket = asyncio.run(guard.issue_websocket_ticket("verified-account"))
    assert asyncio.run(guard.consume_websocket_ticket("short")) is None
    assert asyncio.run(guard.consume_websocket_ticket(ticket, purpose="wrong-purpose")) is None

@pytest.mark.skipif(not os.getenv("REDIS_TEST_URL"), reason="CI Redis integration service is not configured")
def test_redis_websocket_ticket_lua_consume_is_single_use():
    from redis.asyncio import Redis

    async def exercise():
        redis = Redis.from_url(os.environ["REDIS_TEST_URL"], decode_responses=True)
        guard = RedisSharedGuard(os.environ["REDIS_TEST_URL"], redis_client=redis)
        try:
            await guard.start()
            ticket = await guard.issue_websocket_ticket(f"ticket-account-{uuid4().hex}")
            assert await guard.consume_websocket_ticket(ticket) is not None
            assert await guard.consume_websocket_ticket(ticket) is None
        finally:
            await guard.close()

    asyncio.run(exercise())


@pytest.mark.skipif(
    not os.getenv("REDIS_TEST_URL"),
    reason="CI Redis integration service is not configured",
)


@pytest.mark.skipif(not os.getenv("REDIS_TEST_URL"), reason="CI Redis integration service is not configured")
def test_redis_ticket_and_account_lease_are_atomic_across_backend_processes():
    """Two independent backend processes must share atomic ticket and lease state."""
    import multiprocessing
    from redis.asyncio import Redis

    redis_url = os.environ["REDIS_TEST_URL"]
    suffix = uuid4().hex
    account = f"cross-process-account-{suffix}"
    connection_ids = [f"cross-process-ws-{suffix}-1", f"cross-process-ws-{suffix}-2"]

    async def issue_ticket():
        redis = Redis.from_url(redis_url, decode_responses=True)
        guard = RedisSharedGuard(redis_url, redis_client=redis)
        try:
            await guard.start()
            return await guard.issue_websocket_ticket(account)
        finally:
            await guard.close()

    ticket = asyncio.run(issue_ticket())
    context = multiprocessing.get_context("spawn")
    ready_queue, result_queue = context.Queue(), context.Queue()
    start_event = context.Event()
    workers = [
        context.Process(target=_redis_guard_process_worker,
            args=(redis_url, ticket, account, cid, ready_queue, start_event, result_queue))
        for cid in connection_ids
    ]
    leased = []
    cleanup_redis = Redis.from_url(redis_url, decode_responses=True)
    cleanup_guard = RedisSharedGuard(redis_url, websocket_global_limit=4,
        websocket_per_account_limit=1, websocket_lease_seconds=30, redis_client=cleanup_redis)
    try:
        for worker in workers:
            worker.start()
        ready = [ready_queue.get(timeout=20) for _ in workers]
        assert all(item[0] == "ready" for item in ready)
        start_event.set()
        outcomes = [result_queue.get(timeout=20) for _ in workers]
        for worker in workers:
            worker.join(timeout=20)
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=5)
                pytest.fail("Redis guard worker process did not exit")
            assert worker.exitcode == 0
        assert all(item[0] == "result" for item in outcomes), outcomes
        assert sum(item[2] == account for item in outcomes) == 1
        assert sum(item[3] is True for item in outcomes) == 1
        leased = [item[1] for item in outcomes if item[3] is True]
    finally:
        start_event.set()
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=5)
        async def cleanup():
            for cid in leased:
                await cleanup_guard.release_websocket(cid, account)
            await cleanup_guard.close()
        asyncio.run(cleanup())


def test_redis_ticket_and_lease_guards_share_atomic_state_across_clients():
    """Prove atomic ticket consumption and connection caps across Redis clients."""
    from redis.asyncio import Redis

    async def exercise():
        redis_url = os.environ["REDIS_TEST_URL"]
        redis_a = Redis.from_url(redis_url, decode_responses=True)
        redis_b = Redis.from_url(redis_url, decode_responses=True)
        limits = {
            "websocket_global_limit": 2,
            "websocket_per_account_limit": 1,
            "websocket_lease_seconds": 30,
        }
        guard_a = RedisSharedGuard(redis_url, redis_client=redis_a, **limits)
        guard_b = RedisSharedGuard(redis_url, redis_client=redis_b, **limits)
        suffix = uuid4().hex
        account = f"cross-client-account-{suffix}"
        first = f"cross-client-ws-{suffix}-1"
        second = f"cross-client-ws-{suffix}-2"
        third = f"cross-client-ws-{suffix}-3"
        leased = []
        try:
            await guard_a.start()
            await guard_b.start()

            ticket = await guard_a.issue_websocket_ticket(account)
            consumed = await asyncio.gather(
                guard_a.consume_websocket_ticket(ticket),
                guard_b.consume_websocket_ticket(ticket),
            )
            assert consumed.count(account) == 1
            assert consumed.count(None) == 1

            assert await guard_a.acquire_websocket(first, account)
            leased.append((first, account))
            assert not await guard_b.acquire_websocket(second, account)
            other_account = f"other-account-{suffix}"
            assert await guard_b.acquire_websocket(second, other_account)
            leased.append((second, other_account))
            assert not await guard_a.acquire_websocket(third, f"third-account-{suffix}")

            # A different Redis client can renew and release the same lease.
            assert await guard_b.renew_websocket(first, account)
            await guard_b.release_websocket(first, account)
            leased.remove((first, account))
            assert await guard_a.acquire_websocket(third, account)
            leased.append((third, account))
        finally:
            for connection_id, subject in leased:
                await guard_a.release_websocket(connection_id, subject)
            await guard_a.close()
            await guard_b.close()

    asyncio.run(exercise())


def test_in_memory_websocket_ticket_is_single_use_and_subject_bound():
    from app.websocket_tickets import InMemoryWebSocketTicketStore

    store = InMemoryWebSocketTicketStore()
    ticket = asyncio.run(store.issue_websocket_ticket("verified-account"))

    assert ticket not in repr(store._tickets)
    assert asyncio.run(store.consume_websocket_ticket(ticket)) == "verified-account"
    assert asyncio.run(store.consume_websocket_ticket(ticket)) is None


def test_in_memory_websocket_ticket_concurrent_consume_has_exactly_one_winner():
    from app.websocket_tickets import InMemoryWebSocketTicketStore

    store = InMemoryWebSocketTicketStore()
    ticket = asyncio.run(store.issue_websocket_ticket("verified-account"))

    async def consume_twice():
        return await asyncio.gather(
            store.consume_websocket_ticket(ticket),
            store.consume_websocket_ticket(ticket),
        )

    outcomes = asyncio.run(consume_twice())
    assert outcomes.count("verified-account") == 1
    assert outcomes.count(None) == 1


def test_in_memory_websocket_ticket_expires_at_exact_ttl_boundary(monkeypatch):
    import app.websocket_tickets as ticket_module

    now = [1_000.0]
    monkeypatch.setattr(ticket_module.time, "monotonic", lambda: now[0])
    store = ticket_module.InMemoryWebSocketTicketStore(ttl_seconds=30)
    ticket = asyncio.run(store.issue_websocket_ticket("verified-account"))

    now[0] = 1_030.0
    assert asyncio.run(store.consume_websocket_ticket(ticket)) is None
    assert store._tickets == {}


def test_in_memory_websocket_ticket_with_wrong_purpose_is_consumed():
    from app.websocket_tickets import InMemoryWebSocketTicketStore

    store = InMemoryWebSocketTicketStore()
    ticket = asyncio.run(store.issue_websocket_ticket("verified-account"))

    assert asyncio.run(
        store.consume_websocket_ticket(ticket, purpose="different-purpose")
    ) is None
    assert asyncio.run(store.consume_websocket_ticket(ticket)) is None
