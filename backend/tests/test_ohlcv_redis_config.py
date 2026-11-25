from __future__ import annotations

import pytest

from app.ohlcv_redis_config import (
    DEFAULT_OHLCV_STREAM_KEY,
    GATEWAY_ACL_COMMANDS,
    GATEWAY_LEASE_ACL_COMMANDS,
    PUBLISHER_ACL_COMMANDS,
    gateway_lease_acl_selector,
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
    assert PUBLISHER_ACL_COMMANDS == ("+ping", "+xadd", "+xrange")
    assert GATEWAY_ACL_COMMANDS == (
        "+ping", "+xgroup|create", "+xautoclaim", "+xreadgroup", "+xack", "+xrange",
    )
    assert GATEWAY_LEASE_ACL_COMMANDS == ("+set", "+eval", "+get", "+pexpire", "+del")
    assert gateway_lease_acl_selector("dezzta:ohlcv:gateway-lease:abc123") == (
        "(+set +eval +get +pexpire +del ~dezzta:ohlcv:gateway-lease:abc123)"
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


@pytest.mark.parametrize("lease_key", ["", "bad key", "bad:*", "bad)key"])
def test_gateway_lease_acl_selector_rejects_non_literal_keys(lease_key):
    with pytest.raises(ValueError, match="exact literal Redis key"):
        gateway_lease_acl_selector(lease_key)


def test_runtime_role_requires_explicit_source_or_gateway_identity():
    from app.ohlcv_redis_config import require_ohlcv_runtime_role

    with pytest.raises(ValueError, match="explicitly set"):
        require_ohlcv_runtime_role({}, "source")
    with pytest.raises(ValueError, match="source or gateway"):
        require_ohlcv_runtime_role({"OHLCV_REDIS_ROLE": "worker"}, "source")
    with pytest.raises(ValueError, match="cannot initialize"):
        require_ohlcv_runtime_role({"OHLCV_REDIS_ROLE": "source"}, "gateway")
    assert require_ohlcv_runtime_role(
        {"OHLCV_REDIS_ROLE": "gateway"}, "gateway"
    ) == "gateway"


def test_runtime_database_path_must_be_absolute_and_file_backed(tmp_path):
    from app.ohlcv_redis_config import validate_absolute_database_path

    database_path = tmp_path / "replica.sqlite3"
    assert validate_absolute_database_path(
        str(database_path), name="DATABASE_PATH"
    ) == str(database_path)
    with pytest.raises(ValueError, match="absolute file path"):
        validate_absolute_database_path("relative/replica.sqlite3", name="DATABASE_PATH")
    with pytest.raises(ValueError, match="required"):
        validate_absolute_database_path("", name="DATABASE_PATH")
    directory = tmp_path / "database-directory"
    directory.mkdir()
    with pytest.raises(ValueError, match="file, not a directory"):
        validate_absolute_database_path(str(directory), name="DATABASE_PATH")


def test_runtime_database_path_rejects_symbolic_links(tmp_path):
    from app.ohlcv_redis_config import validate_absolute_database_path

    target = tmp_path / "target.sqlite3"
    target.write_text("", encoding="utf-8")
    link = tmp_path / "replica-link.sqlite3"
    link.symlink_to(target)
    with pytest.raises(ValueError, match="symbolic link"):
        validate_absolute_database_path(str(link), name="DATABASE_PATH")
