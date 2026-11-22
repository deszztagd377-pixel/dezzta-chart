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



def test_database_path_is_read_from_backend_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv(
        "INSTRUMENT_REGISTRY_DB_PATH",
        "/tmp/dezzta-chart-configured-live.sqlite3",
    )

    settings = Settings.from_environment()

    assert settings.instrument_registry_db_path == (
        "/tmp/dezzta-chart-configured-live.sqlite3"
    )

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
    monkeypatch.setenv("REDIS_URL", "rediss://dezzta_guard:redis-test-secret@redis.example:6380/0")
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

@pytest.mark.parametrize(
    "redis_url",
    [
        "rediss://redis.example:6380/0",
        "rediss://:redis-test-secret@redis.example:6380/0",
        "rediss://dezzta_guard@redis.example:6380/0",
    ],
)
def test_production_requires_redis_acl_username_and_password(redis_url: str) -> None:
    with pytest.raises(ValueError, match="ACL username and password"):
        Settings(
            app_env="production",
            market_data_ws_token="",
            cors_allowed_origins=("https://chart.example",),
            redis_url=redis_url,
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



def test_redis_tls_ca_bundle_path_is_loaded_and_must_be_absolute(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://chart.example")
    monkeypatch.setenv("REDIS_URL", "rediss://guard-user:secret@redis.example:6380/0")
    monkeypatch.setenv("REDIS_TLS_CA_CERTS", "/run/certs/redis-private-ca.pem")
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "dezzta-chart-prod")
    settings = Settings.from_environment()
    assert settings.redis_tls_ca_certs == "/run/certs/redis-private-ca.pem"

    with pytest.raises(ValueError, match="absolute path"):
        Settings(
            app_env="production", market_data_ws_token="",
            cors_allowed_origins=("https://chart.example",),
            redis_url="rediss://guard-user:secret@redis.example:6380/0",
            redis_tls_ca_certs="relative/ca.pem",
            firebase_project_id="dezzta-chart-prod",
        )


def test_production_requires_firebase_project_id() -> None:
    import pytest

    with pytest.raises(ValueError, match="FIREBASE_PROJECT_ID is required"):
        Settings(
            app_env="production",
            market_data_ws_token="",
            cors_allowed_origins=("https://chart.example",),
            redis_url="rediss://dezzta_guard:redis-test-secret@redis.example:6380/0",
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
            redis_url="rediss://dezzta_guard:redis-test-secret@redis.example:6380/0",
            firebase_project_id="dezzta-chart-prod",
            **provider_overrides,
        )


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("DATABENTO_API_KEY", "must-not-be-used"),
        ("DATABENTO_LIVE_ENABLED", "true"),
        ("DATABENTO_HISTORICAL_ENABLED", "true"),
    ],
)
def test_production_environment_rejects_databento_configuration(
    monkeypatch, variable, value
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("REDIS_URL", "rediss://dezzta_guard:redis-test-secret@redis.example:6380/0")
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "dezzta-chart-prod")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://chart.example")
    monkeypatch.setenv(variable, value)

    with pytest.raises(ValueError, match="Databento.*disabled in production"):
        Settings.from_environment()


def test_production_environment_keeps_databento_disabled_by_default(
    monkeypatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("REDIS_URL", "rediss://dezzta_guard:redis-test-secret@redis.example:6380/0")
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "dezzta-chart-prod")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://chart.example")
    monkeypatch.delenv("DATABENTO_API_KEY", raising=False)
    monkeypatch.delenv("DATABENTO_LIVE_ENABLED", raising=False)
    monkeypatch.delenv("DATABENTO_HISTORICAL_ENABLED", raising=False)

    settings = Settings.from_environment()

    assert settings.provider_configured is False
    assert settings.databento_live_enabled is False
    assert settings.databento_historical_enabled is False


def test_settings_repr_and_str_hide_all_runtime_secret_fields() -> None:
    redis_url = "rediss://audit-user:audit-redis-secret@redis.example:6380/0"
    settings = Settings(
        app_env="test",
        market_data_ws_token="audit-ws-secret",
        cors_allowed_origins=("https://chart.example",),
        databento_api_key="audit-provider-secret",
        session_calendar_sha256="audit-calendar-secret",
        firebase_project_id="audit-firebase-project",
        redis_url=redis_url,
    )

    for rendered in (repr(settings), str(settings)):
        for secret in (
            "audit-ws-secret",
            "audit-provider-secret",
            "audit-calendar-secret",
            "audit-firebase-project",
            "audit-redis-secret",
            redis_url,
        ):
            assert secret not in rendered

def test_alert_device_store_loads_canonical_key_from_protected_file(monkeypatch, tmp_path):
    import base64

    key = b"0123456789abcdef0123456789abcdef"
    secret_file = tmp_path / "alert-device-key.b64"
    secret_file.write_text(base64.b64encode(key).decode("ascii"), encoding="ascii")
    secret_file.chmod(0o600)

    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("ALERT_DEVICE_STORE_ENABLED", "true")
    monkeypatch.setenv("ALERT_DEVICE_ENCRYPTION_KEY_FILE", str(secret_file))

    settings = Settings.from_environment()

    assert settings.alert_device_store_enabled is True
    assert settings.alert_device_encryption_key == key
    assert base64.b64encode(key).decode("ascii") not in repr(settings)
    assert key.hex() not in str(settings)


def test_alert_device_store_refuses_to_start_without_key_file(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("ALERT_DEVICE_STORE_ENABLED", "true")
    monkeypatch.delenv("ALERT_DEVICE_ENCRYPTION_KEY_FILE", raising=False)

    with pytest.raises(ValueError, match="requires ALERT_DEVICE_ENCRYPTION_KEY_FILE"):
        Settings.from_environment()


@pytest.mark.parametrize(
    "contents",
    [
        b"not-base64",
        b"AA==",
        b"!",
        b"",
    ],
)
def test_alert_device_store_rejects_invalid_or_wrong_length_key_file(
    monkeypatch, tmp_path, contents
):
    secret_file = tmp_path / "alert-device-key.b64"
    secret_file.write_bytes(contents)
    secret_file.chmod(0o600)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("ALERT_DEVICE_STORE_ENABLED", "true")
    monkeypatch.setenv("ALERT_DEVICE_ENCRYPTION_KEY_FILE", str(secret_file))

    with pytest.raises(ValueError, match="canonical base64|exactly 32 bytes|invalid size"):
        Settings.from_environment()


def test_alert_device_store_rejects_group_or_world_readable_key_file(
    monkeypatch, tmp_path
):
    import base64

    secret_file = tmp_path / "alert-device-key.b64"
    secret_file.write_text(
        base64.b64encode(b"0123456789abcdef0123456789abcdef").decode("ascii"),
        encoding="ascii",
    )
    secret_file.chmod(0o644)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("ALERT_DEVICE_STORE_ENABLED", "true")
    monkeypatch.setenv("ALERT_DEVICE_ENCRYPTION_KEY_FILE", str(secret_file))

    with pytest.raises(ValueError, match="deny group and other access"):
        Settings.from_environment()


def test_alert_device_store_requires_32_byte_key_when_enabled():
    with pytest.raises(ValueError, match="valid 32-byte injected encryption key"):
        Settings(
            app_env="test",
            market_data_ws_token="test",
            cors_allowed_origins=("https://chart.example",),
            alert_device_store_enabled=True,
        )

@pytest.mark.parametrize("enabled", ["true", 1, None])
def test_alert_device_store_opt_in_requires_a_boolean(enabled):
    with pytest.raises(ValueError, match="must be a boolean"):
        Settings(
            app_env="test",
            market_data_ws_token="test",
            cors_allowed_origins=("https://chart.example",),
            alert_device_store_enabled=enabled,
        )
