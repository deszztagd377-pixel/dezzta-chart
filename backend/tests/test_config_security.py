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
