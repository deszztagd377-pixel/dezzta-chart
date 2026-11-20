"""Additional edge-case tests for configuration security boundaries."""

from dataclasses import replace

import pytest

from app.config import Settings, _parse_bool, _parse_cors_origins, _parse_int


def make_settings(**overrides):
    values = {
        "app_env": "development",
        "market_data_ws_token": "test-only",
        "cors_allowed_origins": ("http://localhost:5173",),
    }
    values.update(overrides)
    return Settings(**values)


@pytest.mark.parametrize(
    "redis_url",
    [
        "http://redis.example.invalid:6379/0",
        "redis://",
        "redis://redis.example.invalid:not-a-port/0",
        "redis://[::1",
        "redis://redis.example.invalid:70000/0",
    ],
)
def test_settings_rejects_malformed_redis_urls(redis_url):
    with pytest.raises(ValueError, match="REDIS_URL is invalid|valid redis"):
        make_settings(redis_url=redis_url)


@pytest.mark.parametrize(
    "field",
    [
        "http_rate_limit_per_client",
        "http_rate_limit_global",
        "websocket_connection_limit_global",
        "websocket_connection_limit_per_account",
        "websocket_lease_seconds",
    ],
)
def test_shared_security_limits_reject_negative_values(field):
    with pytest.raises(ValueError, match="must be positive"):
        make_settings(**{field: -1})


def test_production_environment_name_is_normalized_before_security_checks():
    with pytest.raises(ValueError, match="REDIS_URL is required"):
        make_settings(app_env=" Production ", firebase_project_id="dezzta-prod")


def test_development_can_use_local_redis_without_production_tls_requirement():
    settings = make_settings(redis_url="redis://localhost:6379/0")
    assert settings.redis_url == "redis://localhost:6379/0"


def test_production_cors_accepts_non_default_https_port():
    assert _parse_cors_origins(
        "https://chart.example.com:8443", app_env="production"
    ) == ("https://chart.example.com:8443",)


@pytest.mark.parametrize(
    "origin",
    [
        "https://chart.example.com?debug=1",
        "https://chart.example.com#fragment",
        "https://user:password@chart.example.com",
        "https://chart.example.com:not-a-port",
        "https://chart.example.com https://evil.example.com",
        "https://chart.example.com/path?next=https://evil.example.com",
    ],
)
def test_production_cors_rejects_ambiguous_origin_components(origin):
    with pytest.raises(ValueError):
        _parse_cors_origins(origin, app_env="production")


@pytest.mark.parametrize(
    "field",
    [
        "http_rate_limit_per_client",
        "http_rate_limit_global",
        "websocket_connection_limit_global",
        "websocket_connection_limit_per_account",
        "websocket_lease_seconds",
    ],
)
def test_shared_security_limits_must_be_positive(field):
    with pytest.raises(ValueError, match="must be positive"):
        make_settings(**{field: 0})


def test_settings_repr_redacts_redis_password():
    settings = make_settings(
        redis_url="rediss://private-user:private-password@redis.example.invalid:6380/0"
    )
    assert "private-password" not in repr(settings)


@pytest.mark.parametrize("value", ["1", "true", "YES", "On"])
def test_boolean_parser_accepts_supported_true_values(value):
    assert _parse_bool(value) is True


@pytest.mark.parametrize("value", ["", "false", "no", "off", "unexpected"])
def test_boolean_parser_defaults_unknown_values_to_false(value):
    assert _parse_bool(value) is False


@pytest.mark.parametrize(
    "value,default,expected",
    [
        ("15", 10, 15),
        ("0", 10, 10),
        ("-1", 10, 10),
        ("not-a-number", 10, 10),
        (" 25 ", 10, 25),
    ],
)
def test_integer_parser_uses_safe_positive_default(value, default, expected):
    assert _parse_int(value, default) == expected


def test_settings_immutability_preserves_security_configuration():
    settings = make_settings()
    with pytest.raises(AttributeError):
        settings.redis_url = "redis://replacement.invalid"  # type: ignore[misc]
    assert replace(settings).redis_url == settings.redis_url


@pytest.mark.parametrize(
    "field",
    [
        "http_rate_limit_per_client",
        "http_rate_limit_global",
        "websocket_connection_limit_global",
        "websocket_connection_limit_per_account",
        "websocket_lease_seconds",
    ],
)
@pytest.mark.parametrize("invalid_value", [True, False, 1.5, 0.5, "2", None, -1, 0])
def test_shared_security_limits_reject_non_integer_and_invalid_values(
    field, invalid_value
):
    with pytest.raises(ValueError, match="positive integers"):
        make_settings(**{field: invalid_value})


@pytest.mark.parametrize(
    "field,value,secret",
    [
        ("market_data_ws_token", "ws-token-never-log-7f31", "ws-token-never-log-7f31"),
        ("databento_api_key", "db-credential-never-log-8a42", "db-credential-never-log-8a42"),
        ("session_calendar_sha256", "calendar-digest-never-log-9c53", "calendar-digest-never-log-9c53"),
        ("firebase_project_id", "firebase-project-private-6d64", "firebase-project-private-6d64"),
        (
            "redis_url",
            "rediss://acl-user:redis-password-never-log@redis.example.invalid:6380/0",
            "redis-password-never-log",
        ),
    ],
)
def test_sensitive_settings_are_excluded_from_repr_and_str(field, value, secret):
    settings = make_settings(**{field: value})

    assert secret not in repr(settings)
    assert secret not in str(settings)


@pytest.mark.parametrize(
    "redis_url,expected_error",
    [
        ("redis://user:password@redis.example.invalid:6379/0", "must use rediss:// TLS"),
        ("rediss://redis.example.invalid:6380/0", "ACL username and password"),
        ("rediss://:password@redis.example.invalid:6380/0", "ACL username and password"),
        ("rediss://user:@redis.example.invalid:6380/0", "ACL username and password"),
    ],
)
def test_production_requires_tls_and_complete_redis_acl_credentials(
    redis_url, expected_error
):
    with pytest.raises(ValueError, match=expected_error):
        make_settings(
            app_env="production",
            firebase_project_id="dezzta-production",
            redis_url=redis_url,
        )


def test_production_accepts_tls_redis_url_with_acl_credentials():
    settings = make_settings(
        app_env="production",
        firebase_project_id="dezzta-production",
        redis_url="rediss://guard-user:guard-password@redis.example.invalid:6380/0",
    )
    assert settings.redis_url.startswith("rediss://")
    assert "guard-password" not in repr(settings)


def test_alert_delivery_worker_is_disabled_by_default():
    settings = make_settings()
    assert settings.alert_delivery_worker_enabled is False
    assert settings.alert_delivery_batch_size == 1


def test_alert_delivery_worker_requires_encrypted_device_store():
    with pytest.raises(ValueError, match="requires ALERT_DEVICE_STORE_ENABLED"):
        make_settings(
            alert_delivery_worker_enabled=True,
            firebase_project_id="test-project",
        )


def test_alert_delivery_worker_requires_firebase_project_id():
    with pytest.raises(ValueError, match="requires FIREBASE_PROJECT_ID"):
        make_settings(
            alert_device_store_enabled=True,
            alert_device_encryption_key=b"K" * 32,
            alert_delivery_worker_enabled=True,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("alert_delivery_poll_interval_seconds", 0),
        ("alert_delivery_batch_size", 0),
        ("alert_delivery_batch_size", 2),
        ("alert_delivery_lease_seconds", 29),
        ("alert_delivery_lease_seconds", 89),
        ("alert_delivery_max_attempts", 33),
    ],
)
def test_alert_delivery_worker_rejects_unsafe_limits(field, value):
    with pytest.raises(ValueError):
        make_settings(
            alert_device_store_enabled=True,
            alert_device_encryption_key=b"K" * 32,
            alert_delivery_worker_enabled=True,
            firebase_project_id="test-project",
            **{field: value},
        )


def test_observability_metrics_token_is_redacted_and_requires_strong_value():
    token = "metrics-token-for-tests-only-32chars"
    settings = make_settings(observability_metrics_token=token)
    assert token not in repr(settings)
    assert token not in str(settings)


@pytest.mark.parametrize("token", ["short", "contains whitespace "])
def test_observability_metrics_token_rejects_weak_values(token):
    with pytest.raises(ValueError, match="32-256 non-whitespace"):
        make_settings(observability_metrics_token=token)


def test_enabled_alert_delivery_accepts_lease_with_deadline_margin():
    settings = make_settings(
        alert_device_store_enabled=True,
        alert_device_encryption_key=b"K" * 32,
        alert_delivery_worker_enabled=True,
        firebase_project_id="test-project",
        alert_delivery_lease_seconds=90,
    )
    assert settings.alert_delivery_lease_seconds == 90


def test_operator_incident_token_is_redacted_and_requires_strong_value():
    token = "operator-incident-token-for-tests-only-32"
    settings = make_settings(operator_incident_token=token)
    assert token not in repr(settings)
    assert token not in str(settings)


@pytest.mark.parametrize("token", ["short", "contains whitespace "])
def test_operator_incident_token_rejects_weak_values(token):
    with pytest.raises(ValueError, match="32-256 non-whitespace"):
        make_settings(operator_incident_token=token)
