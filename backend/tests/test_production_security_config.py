import pytest

from app.config import Settings, _parse_cors_origins


def _production_settings(**overrides):
    values = {
        "app_env": "production",
        "market_data_ws_token": "",
        "cors_allowed_origins": ("https://chart.example.test",),
        "firebase_project_id": "dezzta-production",
        "redis_url": "rediss://redis.example.test:6379/0",
    }
    values.update(overrides)
    return Settings(**values)


def test_production_requires_shared_redis_guard():
    with pytest.raises(ValueError, match="REDIS_URL is required"):
        _production_settings(redis_url="")


def test_production_requires_firebase_project_identity_verification():
    with pytest.raises(ValueError, match="FIREBASE_PROJECT_ID is required"):
        _production_settings(firebase_project_id="")


def test_production_rejects_plaintext_redis_transport():
    with pytest.raises(ValueError, match="must use rediss:// TLS"):
        _production_settings(redis_url="redis://redis.example.test:6379/0")


def test_production_accepts_tls_redis_and_exact_https_origin():
    settings = _production_settings()
    assert settings.redis_url.startswith("rediss://")
    assert settings.cors_allowed_origins == ("https://chart.example.test",)


def test_production_rejects_http_browser_origins():
    with pytest.raises(ValueError, match="must use HTTPS"):
        _production_settings(cors_allowed_origins=("http://chart.example.test",))


def test_cors_rejects_wildcard_origins_in_every_environment():
    with pytest.raises(ValueError, match="not wildcards"):
        _parse_cors_origins("*", app_env="development")


def test_cors_rejects_origin_paths_and_non_bare_urls():
    with pytest.raises(ValueError, match="bare http"):
        _parse_cors_origins("https://chart.example.test/app", app_env="production")


def test_cors_rejects_embedded_credentials():
    with pytest.raises(ValueError, match="bare http"):
        _parse_cors_origins(
            "https://operator:secret@chart.example.test",
            app_env="production",
        )


def test_development_can_use_exact_localhost_http_origin():
    assert _parse_cors_origins(
        "http://localhost:5173",
        app_env="development",
    ) == ("http://localhost:5173",)


def test_redis_rejects_unsupported_transport_scheme():
    with pytest.raises(ValueError, match="redis:// or rediss://"):
        Settings(
            app_env="development",
            market_data_ws_token="",
            cors_allowed_origins=("http://localhost:5173",),
            redis_url="https://redis.example.test",
        )
