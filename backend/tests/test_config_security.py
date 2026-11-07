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
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://dezzta-chart.vercel.app,https://api.example",
    )

    settings = Settings.from_environment()

    assert settings.cors_allowed_origins == (
        "https://dezzta-chart.vercel.app",
        "https://api.example",
    )
