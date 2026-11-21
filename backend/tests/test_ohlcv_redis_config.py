from __future__ import annotations

import pytest

from app.ohlcv_redis_config import (
    DEFAULT_OHLCV_STREAM_KEY,
    GATEWAY_ACL_COMMANDS,
    PUBLISHER_ACL_COMMANDS,
    OhlcvRedisRelayConfig,
)


def test_relay_config_is_disabled_by_default_and_keeps_shared_guard_separate():
    config = OhlcvRedisRelayConfig.from_environment({}, production=True)
    assert config.enabled is False
    assert config.stream_key == DEFAULT_OHLCV_STREAM_KEY
    assert config.publisher_url == ""
    assert config.gateway_url == ""


def test_enabled_relay_requires_two_distinct_acl_identities():
    config = OhlcvRedisRelayConfig.from_environment({
        "OHLCV_REDIS_ENABLED": "true",
        "OHLCV_REDIS_PUBLISH_URL": "rediss://publisher:publish-secret@redis.example:6379/0",
        "OHLCV_REDIS_GATEWAY_URL": "rediss://gateway:gateway-secret@redis.example:6379/0",
    }, production=True)
    assert config.enabled is True
    assert config.stream_key == DEFAULT_OHLCV_STREAM_KEY
    assert PUBLISHER_ACL_COMMANDS == ("+ping", "+select", "+xadd", "+xrange")
    assert GATEWAY_ACL_COMMANDS == (
        "+ping", "+select", "+xgroup|create", "+xautoclaim", "+xreadgroup", "+xack", "+xrange",
        "+set", "+eval", "+get", "+pexpire", "+del",
    )
    assert "publish-secret" not in repr(config)
    assert "gateway-secret" not in repr(config)


def test_enabled_relay_rejects_missing_dedicated_url():
    with pytest.raises(ValueError, match="OHLCV_REDIS_PUBLISH_URL is required"):
        OhlcvRedisRelayConfig.from_environment({
            "OHLCV_REDIS_ENABLED": "true",
            "OHLCV_REDIS_GATEWAY_URL": "rediss://gateway:secret@redis.example:6379/0",
        })


def test_production_relay_requires_tls_for_both_identities():
    with pytest.raises(ValueError, match="must use rediss:// TLS"):
        OhlcvRedisRelayConfig(
            enabled=True,
            publisher_url="redis://publisher:publish-secret@redis.example:6379/0",
            gateway_url="rediss://gateway:gateway-secret@redis.example:6379/0",
            production=True,
        )


def test_relay_rejects_shared_acl_username_or_password():
    with pytest.raises(ValueError, match="different Redis ACL usernames"):
        OhlcvRedisRelayConfig(
            enabled=True,
            publisher_url="rediss://same:publish-secret@redis.example:6379/0",
            gateway_url="rediss://same:gateway-secret@redis.example:6379/0",
        )
    with pytest.raises(ValueError, match="different Redis ACL passwords"):
        OhlcvRedisRelayConfig(
            enabled=True,
            publisher_url="rediss://publisher:same-secret@redis.example:6379/0",
            gateway_url="rediss://gateway:same-secret@redis.example:6379/0",
        )


@pytest.mark.parametrize("stream_key", [
    "", " bad-key", "bad key", "ohlcv:*", "ohlcv:?", "ohlcv:[x]",
])
def test_relay_config_rejects_non_exact_or_glob_stream_keys(stream_key):
    with pytest.raises(ValueError, match="exact Redis key"):
        OhlcvRedisRelayConfig(stream_key=stream_key)


def test_relay_rejects_nonzero_database_to_avoid_select_acl():
    with pytest.raises(ValueError, match="database 0"):
        OhlcvRedisRelayConfig(
            enabled=True,
            publisher_url="rediss://publisher:publish-secret@redis.example:6379/1",
            gateway_url="rediss://gateway:gateway-secret@redis.example:6379/0",
        )


def test_relay_enabled_flag_rejects_ambiguous_boolean():
    with pytest.raises(ValueError, match="must be a boolean"):
        OhlcvRedisRelayConfig.from_environment({"OHLCV_REDIS_ENABLED": "sometimes"})
