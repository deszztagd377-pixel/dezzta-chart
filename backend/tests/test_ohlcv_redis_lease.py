from __future__ import annotations

import multiprocessing
import os
import time
import uuid

import pytest

from app.ohlcv_redis_lease import (
    RedisOhlcvConsumerLease,
    RedisOhlcvConsumerLeaseLost,
    RedisOhlcvConsumerLeaseUnavailable,
)


def real_redis():
    url = os.environ.get("REDIS_TEST_URL")
    if not url:
        pytest.skip("REDIS_TEST_URL is not configured.")
    redis_module = pytest.importorskip("redis")
    client = redis_module.Redis.from_url(url, decode_responses=True)
    client.ping()
    return client


def _child_try_acquire(redis_url, group_name, queue):
    import redis
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    lease = RedisOhlcvConsumerLease(client, group_name=group_name, ttl_ms=3000)
    try:
        lease.acquire()
        queue.put("acquired")
        time.sleep(0.2)
        lease.release()
    except RedisOhlcvConsumerLeaseUnavailable:
        queue.put("blocked")
    finally:
        client.close()


def test_two_processes_cannot_own_the_same_replica_group():
    redis_url = os.environ.get("REDIS_TEST_URL")
    if not redis_url:
        pytest.skip("REDIS_TEST_URL is not configured.")
    redis = pytest.importorskip("redis")
    probe = redis.Redis.from_url(redis_url, decode_responses=True)
    probe.ping()
    group = f"dezzta-test:{uuid.uuid4().hex}"
    lease = RedisOhlcvConsumerLease(probe, group_name=group, ttl_ms=3000)
    queue = multiprocessing.get_context("spawn").Queue()
    process = multiprocessing.get_context("spawn").Process(
        target=_child_try_acquire, args=(redis_url, group, queue),
    )
    try:
        lease.acquire()
        process.start()
        process.join(timeout=5)
        assert process.exitcode == 0
        assert queue.get(timeout=1) == "blocked"
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=2)
        lease.release()
        probe.close()


def test_independent_replica_groups_can_be_owned_simultaneously():
    redis = real_redis()
    suffix = uuid.uuid4().hex
    first = RedisOhlcvConsumerLease(redis, group_name=f"replica-a:{suffix}")
    second = RedisOhlcvConsumerLease(redis, group_name=f"replica-b:{suffix}")
    try:
        first.acquire()
        second.acquire()
        first.assert_owned()
        second.assert_owned()
    finally:
        first.release()
        second.release()
        redis.close()


def test_expired_owner_can_be_replaced_and_old_token_cannot_renew_or_release():
    redis = real_redis()
    group = f"generation:{uuid.uuid4().hex}"
    old = RedisOhlcvConsumerLease(redis, group_name=group, ttl_ms=3000)
    new = RedisOhlcvConsumerLease(redis, group_name=group, ttl_ms=3000)
    try:
        old.acquire()
        time.sleep(3.2)
        new.acquire()
        assert old.renew() is False
        assert old.release() is False
        new.assert_owned()
    finally:
        old.release()
        new.release()
        redis.close()


def test_lease_loss_is_reported_before_consumer_can_continue():
    redis = real_redis()
    group = f"loss:{uuid.uuid4().hex}"
    owner = RedisOhlcvConsumerLease(redis, group_name=group, ttl_ms=3000)
    replacement = RedisOhlcvConsumerLease(redis, group_name=group, ttl_ms=3000)
    try:
        owner.acquire()
        # Replace the token to model expiry/takeover while the former owner is paused.
        redis.set(owner.key, "successor-token", px=3000)
        with pytest.raises(RedisOhlcvConsumerLeaseLost):
            owner.assert_owned()
        replacement._token = "successor-token"
        replacement._acquired = True
        replacement.assert_owned()
    finally:
        owner.release()
        replacement.release()
        redis.close()


def test_snapshot_generation_scopes_lease_keys():
    redis = real_redis()
    suffix = uuid.uuid4().hex
    first = RedisOhlcvConsumerLease(redis, group_name=f"replica:source:generation-1:{suffix}")
    second = RedisOhlcvConsumerLease(redis, group_name=f"replica:source:generation-2:{suffix}")
    try:
        first.acquire()
        second.acquire()
        assert first.key != second.key
    finally:
        first.release()
        second.release()
        redis.close()
