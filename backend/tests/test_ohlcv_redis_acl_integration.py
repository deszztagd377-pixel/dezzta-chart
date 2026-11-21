from __future__ import annotations

import os
import secrets
import uuid

import pytest

from app.ohlcv_redis_config import GATEWAY_ACL_COMMANDS, PUBLISHER_ACL_COMMANDS


def test_real_redis_publisher_and_gateway_acl_roles_are_least_privilege():
    """Exercise the actual role command/key allow-lists against the CI Redis service.

    The test creates disposable ACL users and random passwords at runtime.
    No credential is stored in the repository or emitted in assertion output.
    """
    redis_url = os.environ.get("REDIS_TEST_URL")
    if not redis_url:
        pytest.skip("REDIS_TEST_URL is not configured.")
    redis_module = pytest.importorskip("redis")
    admin = redis_module.Redis.from_url(redis_url, decode_responses=True)
    admin.ping()

    suffix = uuid.uuid4().hex
    publisher_user = f"dezzta-pub-{suffix[:12]}"
    gateway_user = f"dezzta-gw-{suffix[:12]}"
    publisher_password = secrets.token_urlsafe(32)
    gateway_password = secrets.token_urlsafe(32)
    stream_key = f"dezzta:test:relay:{suffix}"
    lease_key = f"dezzta:ohlcv:gateway-lease:{suffix}"
    group_name = f"dezzta:test:group:{suffix}"
    publisher = gateway = None

    try:
        admin.execute_command(
            "ACL", "SETUSER", publisher_user, "reset", "on",
            f">{publisher_password}", f"~{stream_key}",
            *PUBLISHER_ACL_COMMANDS,
        )
        admin.execute_command(
            "ACL", "SETUSER", gateway_user, "reset", "on",
            f">{gateway_password}", f"~{stream_key}", f"~{lease_key}",
            *GATEWAY_ACL_COMMANDS,
        )

        # from_url(.../0) initializes the database selection during connect.
        # Both dedicated identities must therefore have the explicit +select grant.
        publisher = redis_module.Redis.from_url(
            redis_url, username=publisher_user, password=publisher_password,
            decode_responses=True,
        )
        gateway = redis_module.Redis.from_url(
            redis_url, username=gateway_user, password=gateway_password,
            decode_responses=True,
        )
        assert publisher.ping() is True
        assert gateway.ping() is True

        # Publisher can append and verify deterministic stream entries.
        assert publisher.xadd(stream_key, {"payload": "one"}, id="1-0") == "1-0"
        assert publisher.xrange(stream_key, min="-", max="+") == [
            ("1-0", {"payload": "one"})
        ]
        with pytest.raises(redis_module.exceptions.ResponseError):
            publisher.xreadgroup(group_name, "publisher", {stream_key: ">"}, count=1)
        with pytest.raises(redis_module.exceptions.ResponseError):
            publisher.xadd(f"{stream_key}:outside-scope", {"payload": "forbidden"}, id="1-0")
        with pytest.raises(redis_module.exceptions.ResponseError):
            publisher.set(lease_key, "not-allowed")

        # Gateway can consume/acknowledge entries and reclaim abandoned pending work.
        assert gateway.xgroup_create(stream_key, group_name, id="0-0", mkstream=True)
        assert admin.xadd(stream_key, {"payload": "two"}, id="2-0") == "2-0"
        first = gateway.xreadgroup(
            group_name, "gateway-old", {stream_key: ">"}, count=1,
        )
        assert first[0][1][0][0] == "1-0"
        assert gateway.xack(stream_key, group_name, "1-0") == 1
        second = gateway.xreadgroup(
            group_name, "gateway-old", {stream_key: ">"}, count=1,
        )
        assert second[0][1][0][0] == "2-0"
        reclaimed = gateway.xautoclaim(
            stream_key, group_name, "gateway-new", 0, start_id="0-0", count=1,
        )
        assert reclaimed[1][0][0] == "2-0"
        assert gateway.xack(stream_key, group_name, "2-0") == 1
        assert gateway.xrange(stream_key, min="-", max="+")
        with pytest.raises(redis_module.exceptions.ResponseError):
            gateway.xadd(stream_key, {"payload": "forbidden"}, id="3-0")
        with pytest.raises(redis_module.exceptions.ResponseError):
            gateway.set(f"{lease_key}:outside-scope", "forbidden")

        # Gateway lease Lua commands must work under the exact runtime allow-list.
        assert gateway.set(lease_key, "lease-token", nx=True, px=5_000)
        renewed = gateway.eval(
            "local value=redis.call('GET',KEYS[1]); "
            "if value == ARGV[1] then return redis.call('PEXPIRE',KEYS[1],ARGV[2]) end "
            "return 0",
            1, lease_key, "lease-token", 5_000,
        )
        assert renewed == 1
        released = gateway.eval(
            "if redis.call('GET',KEYS[1]) == ARGV[1] then "
            "return redis.call('DEL',KEYS[1]) end return 0",
            1, lease_key, "lease-token",
        )
        assert released == 1
    finally:
        if publisher is not None:
            publisher.close()
        if gateway is not None:
            gateway.close()
        admin.delete(stream_key, lease_key)
        admin.execute_command("ACL", "DELUSER", publisher_user, gateway_user)
        admin.close()
