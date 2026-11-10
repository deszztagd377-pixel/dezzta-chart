"""Configuration boundary tests for production security settings."""

from dataclasses import replace

import pytest

from app.config import Settings, _parse_bool, _parse_cors_origins, _parse_int


def make_settings(**overrides):
    values = {
        "app_env": "development",
        "market_data_ws_token": "legacy-secret",
        "cors_allowed_origins": ("http://localhost:5173",),
    }
    values.update(overrides)
    return Settings(**values)


def test_production_requires_shared_redis_guard():
    with pytest.raises(ValueError, match="REDIS_URL is required"):
        make_settings(app_env="production", firebase_project_id="dezzta-prod")


def test_production_environment_name_is_normalized_before_security_checks():
    with pytest.raises(ValueError, match="REDIS_URL is required"):
        make_settings(app_env=" Production ", firebase_project_id="dezzta-prod")


def test_production_requires_firebase_project_id():
    with pytest.raises(ValueError, match="FIREBASE_PROJECT_ID is required"):
        make_settings(
            app_env="production",
            redis_url="rediss://redis.example.invalid:6380/0",
        )


def test_production_rejects_unencrypted_redis_url():
    with pytest.raises(ValueError, match="must use rediss://"):
        make_settings(
            app_env="production",
            firebase_project_id="dezzta-prod",
            redis_url="redis://redis.example.invalid:6379/0",
        )


def test_production_accepts_tls_redis_and_firebase_configuration():
    settings = make_settings(
        app_env="production",
        firebase_project_id="dezzta-prod",
        redis_url="rediss://redis.example.invalid:6380/0",
    )
    assert settings.firebase_project_id == "dezzta-prod"


def test_development_can_use_local_redis_without_production_tls_requirement():
    settings = make_settings(redis_url="redis://localhost:6379/0")
    assert settings.redis_url == "redis://localhost:6379/0"


@pytest.mark.parametrize(
    "origin",
    [
        "https://chart.example.com",
        "https://chart.example.com:8443",
        "https://chart.example.com,https://preview.example.com",
    ],
)
def test_production_cors_accepts_exact_https_origins(origin):
    assert _parse_cors_origins(origin, app_env="production")


@pytest.mark.parametrize(
    "origin",
    [
        "*",
        "http://chart.example.com",
        "https://chart.example.com/",
        "https://chart.example.com/path",
        "https://chart.example.com?debug=1",
        "https://chart.example.com#fragment",
        "https://user:password@chart.example.com",
        "https://chart.example.com:not-a-port",
        "https://chart.example.com https://evil.example.com",
    ],
)
def test_production_cors_rejects_non_exact_or_non_tls_origins(origin):
    with pytest.raises(ValueError):
        _parse_cors_origins(origin, app_env="production")


def test_development_cors_allows_local_http_origin():
    assert _parse_cors_origins(
        "http://localhost:5173", app_env="development"
    ) == ("http://localhost:5173",)


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


def test_settings_repr_does_not_expose_backend_secrets():
    settings = make_settings(
        market_data_ws_token="legacy-secret-value",
        databento_api_key="provider-secret-value",
        firebase_project_id="private-project-id",
        redis_url="rediss://private-user:private-password@redis.example.invalid:6380/0",
        session_calendar_sha256="private-calendar-digest",
    )
    rendered = repr(settings)
    for secret in (
        "legacy-secret-value",
        "provider-secret-value",
        "private-project-id",
        "private-password",
        "private-calendar-digest",
    ):
        assert secret not in rendered


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
