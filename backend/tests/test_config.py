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
