import pytest

from app.config import Settings


def test_settings_repr_never_exposes_backend_credentials() -> None:
    settings = Settings(
        app_env="test",
        market_data_ws_token="ws-secret-value",
        cors_allowed_origins=("https://chart.example",),
        databento_api_key="databento-secret-value",
        firebase_project_id="firebase-project-secret-value",
    )

    rendered = repr(settings)

    assert "ws-secret-value" not in rendered
    assert "databento-secret-value" not in rendered
    assert "firebase-project-secret-value" not in rendered
    assert "app_env='test'" in rendered



def test_development_cors_accepts_exact_local_http_origin(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173")

    settings = Settings.from_environment()

    assert settings.cors_allowed_origins == ("http://localhost:5173",)


def test_cors_rejects_wildcard_origin(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")

    import pytest

    with pytest.raises(ValueError, match="exact origins"):
        Settings.from_environment()


def test_cors_rejects_paths_and_non_origin_urls(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://chart.example/app")

    import pytest

    with pytest.raises(ValueError, match="bare http"):
        Settings.from_environment()


def test_production_cors_requires_https(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://chart.example")

    import pytest

    with pytest.raises(ValueError, match="must use HTTPS"):
        Settings.from_environment()


def test_production_cors_accepts_exact_https_origins(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("REDIS_URL", "rediss://redis.example:6380/0")
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "dezzta-chart-prod")
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://dezzta-chart.vercel.app,https://api.example",
    )

    settings = Settings.from_environment()

    assert settings.cors_allowed_origins == (
        "https://dezzta-chart.vercel.app",
        "https://api.example",
    )


def test_production_requires_redis_shared_security_store() -> None:
    import pytest
    with pytest.raises(ValueError, match="REDIS_URL is required"):
        Settings(app_env="production", market_data_ws_token="", cors_allowed_origins=("https://chart.example",))

def test_production_requires_tls_redis_url() -> None:
    import pytest
    with pytest.raises(ValueError, match="rediss://"):
        Settings(
            app_env="production",
            market_data_ws_token="",
            cors_allowed_origins=("https://chart.example",),
            redis_url="redis://redis.example:6379/0",
            firebase_project_id="dezzta-chart-prod",
        )

def test_production_accepts_tls_redis_url_without_exposing_it_in_repr() -> None:
    redis_url="rediss://user:redis-secret@redis.example:6380/0"
    settings=Settings(
        app_env="production",
        market_data_ws_token="",
        cors_allowed_origins=("https://chart.example",),
        redis_url=redis_url,
        firebase_project_id="dezzta-chart-prod",
    )
    assert redis_url not in repr(settings)



def test_production_requires_firebase_project_id() -> None:
    import pytest

    with pytest.raises(ValueError, match="FIREBASE_PROJECT_ID is required"):
        Settings(
            app_env="production",
            market_data_ws_token="",
            cors_allowed_origins=("https://chart.example",),
            redis_url="rediss://redis.example:6380/0",
            firebase_project_id="",
        )


@pytest.mark.parametrize(
    "provider_overrides",
    [
        {"databento_api_key": "must-not-be-used"},
        {"databento_live_enabled": True},
        {"databento_historical_enabled": True},
    ],
)
def test_production_rejects_databento_credentials_and_paid_provider_access(
    provider_overrides,
) -> None:
    with pytest.raises(ValueError, match="Databento.*disabled in production"):
        Settings(
            app_env="production",
            market_data_ws_token="",
            cors_allowed_origins=("https://chart.example",),
            redis_url="rediss://redis.example:6380/0",
            firebase_project_id="dezzta-chart-prod",
            **provider_overrides,
        )
