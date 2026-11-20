"""Environment-backed settings for the DEZZTA CHART backend.

All provider credentials come exclusively from backend environment variables.
Settings.__repr__ never includes the Databento key.
"""

from dataclasses import dataclass, field
import base64
import binascii
import json
import os
from pathlib import Path
import stat
from urllib.parse import urlsplit

_TRUE = frozenset(("1", "true", "yes", "on"))


def _parse_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in _TRUE


def _unique_json_object(pairs):
    result = {}
    for key, item in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key in session calendar manifest: {key}")
        result[key] = item
    return result


def _parse_session_calendar_releases(value: str) -> tuple[tuple[str, str, str], ...]:
    """Parse a strict JSON manifest of independently pinned calendar releases."""
    if not value.strip():
        return ()
    try:
        payload = json.loads(value, object_pairs_hook=_unique_json_object)
    except json.JSONDecodeError as exc:
        raise ValueError("SESSION_CALENDAR_RELEASES_JSON must be valid JSON.") from exc
    if not isinstance(payload, list) or not payload or len(payload) > 32:
        raise ValueError("SESSION_CALENDAR_RELEASES_JSON must be a non-empty array of at most 32 releases.")
    parsed = []
    for item in payload:
        if not isinstance(item, dict) or set(item) != {"artifact_path", "sha256", "version"}:
            raise ValueError("Each release must contain exactly artifact_path, sha256, and version.")
        fields = (item["artifact_path"], item["sha256"], item["version"])
        if any(not isinstance(field, str) or not field.strip() for field in fields):
            raise ValueError("Session calendar release fields must be non-empty strings.")
        parsed.append(tuple(field.strip() for field in fields))
    if len(set(parsed)) != len(parsed):
        raise ValueError("SESSION_CALENDAR_RELEASES_JSON contains duplicate descriptors.")
    return tuple(parsed)


def _parse_cors_origins(value: str, *, app_env: str) -> tuple[str, ...]:
    """Accept exact browser origins only; production origins must use HTTPS."""
    origins = _parse_csv(value)
    production = app_env.strip().lower() == "production"

    for origin in origins:
        if origin == "*" or any(char.isspace() for char in origin):
            raise ValueError("CORS_ALLOWED_ORIGINS must contain exact origins, not wildcards or whitespace.")

        try:
            parsed = urlsplit(origin)
            # Accessing .port validates malformed port values as well.
            _ = parsed.port
        except ValueError as exc:
            raise ValueError("CORS_ALLOWED_ORIGINS contains an invalid origin.") from exc

        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
            or origin.endswith("/")
        ):
            raise ValueError("CORS_ALLOWED_ORIGINS must contain bare http(s) origins only.")

        if production and parsed.scheme != "https":
            raise ValueError("Production CORS origins must use HTTPS.")

    return origins


def _load_alert_device_encryption_key(path: str) -> bytes:
    """Load a canonical base64-encoded 256-bit key from a protected secret file."""
    if not isinstance(path, str) or not path.strip():
        raise ValueError(
            "ALERT_DEVICE_STORE_ENABLED requires ALERT_DEVICE_ENCRYPTION_KEY_FILE."
        )
    secret_path = Path(path.strip())
    if not secret_path.is_absolute():
        raise ValueError("ALERT_DEVICE_ENCRYPTION_KEY_FILE must be an absolute path.")
    try:
        if not secret_path.is_file():
            raise ValueError("ALERT_DEVICE_ENCRYPTION_KEY_FILE must reference a regular file.")
        file_stat = secret_path.stat()
        if stat.S_IMODE(file_stat.st_mode) & 0o077:
            raise ValueError(
                "Alert-device encryption key file permissions must deny group and other access."
            )
        if file_stat.st_size < 1 or file_stat.st_size > 128:
            raise ValueError("Alert-device encryption key file has an invalid size.")
        encoded = secret_path.read_bytes().decode("ascii").strip()
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError("Alert-device encryption key file is unavailable or invalid.") from exc
    try:
        key = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Alert-device encryption key file must contain canonical base64.") from exc
    if len(key) != 32 or base64.b64encode(key).decode("ascii") != encoded:
        raise ValueError("Alert-device encryption key must encode exactly 32 bytes.")
    return key


def _parse_int(value: str, default: int, *, minimum: int = 1) -> int:
    try:
        parsed = int(value.strip())
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= minimum else default


@dataclass(frozen=True)
class Settings:
    app_env: str
    market_data_ws_token: str = field(repr=False)
    cors_allowed_origins: tuple[str, ...]
    # --- Phase 2 provider settings: every field has a safe default so that
    # --- existing callers/tests that build Settings(...) keep working.
    databento_api_key: str = field(default="", repr=False)
    databento_dataset: str = "GLBX.MDP3"
    databento_live_enabled: bool = False
    databento_historical_enabled: bool = False
    # Explicit contract symbols only; nothing is auto-selected.
    databento_live_symbols: tuple[str, ...] = ()
    databento_definition_symbols: tuple[str, ...] = ()
    historical_max_span_hours: int = 24
    historical_window_minutes: int = 60
    allowed_roots: tuple[str, ...] = ("ES", "NQ", "GC")
    ohlcv_queue_max: int = 10_000
    ohlcv_max_response_bars: int = 5_000
    instrument_registry_db_path: str = "./data/instrument_registry.sqlite3"
    session_calendar_artifact_path: str = ""
    session_calendar_sha256: str = field(default="", repr=False)
    session_calendar_version: str = ""
    session_calendar_releases: tuple[tuple[str, str, str], ...] = ()
    firebase_project_id: str = field(default="", repr=False)
    alert_device_store_enabled: bool = False
    alert_device_encryption_key: bytes = field(default=b"", repr=False)
    alert_delivery_worker_enabled: bool = False
    alert_delivery_poll_interval_seconds: int = 2
    alert_delivery_batch_size: int = 1
    alert_delivery_lease_seconds: int = 120
    alert_delivery_max_attempts: int = 8
    redis_url: str = field(default="", repr=False)
    observability_metrics_token: str = field(default="", repr=False)
    http_rate_limit_per_client: int = 120
    http_rate_limit_global: int = 6000
    websocket_connection_limit_global: int = 500
    websocket_connection_limit_per_account: int = 5
    websocket_lease_seconds: int = 45

    def __post_init__(self) -> None:
        if not isinstance(self.observability_metrics_token, str):
            raise ValueError("observability_metrics_token must be a string.")
        if self.observability_metrics_token and (
            len(self.observability_metrics_token) < 32
            or len(self.observability_metrics_token) > 256
            or any(char.isspace() for char in self.observability_metrics_token)
        ):
            raise ValueError("OBSERVABILITY_METRICS_TOKEN must be 32-256 non-whitespace characters when supplied.")
        if not isinstance(self.alert_device_store_enabled, bool):
            raise ValueError("alert_device_store_enabled must be a boolean.")
        if not isinstance(self.alert_device_encryption_key, bytes) or (
            self.alert_device_encryption_key
            and len(self.alert_device_encryption_key) != 32
        ):
            raise ValueError("alert_device_encryption_key must be exactly 32 bytes when supplied.")
        if self.alert_device_store_enabled and len(self.alert_device_encryption_key) != 32:
            raise ValueError(
                "ALERT_DEVICE_STORE_ENABLED requires a valid 32-byte injected encryption key."
            )
        if not isinstance(self.alert_delivery_worker_enabled, bool):
            raise ValueError("alert_delivery_worker_enabled must be a boolean.")
        if self.alert_delivery_worker_enabled and not self.alert_device_store_enabled:
            raise ValueError(
                "ALERT_DELIVERY_WORKER_ENABLED requires ALERT_DEVICE_STORE_ENABLED."
            )
        if self.alert_delivery_worker_enabled and not self.firebase_project_id.strip():
            raise ValueError(
                "ALERT_DELIVERY_WORKER_ENABLED requires FIREBASE_PROJECT_ID."
            )
        delivery_limits = (
            self.alert_delivery_poll_interval_seconds,
            self.alert_delivery_batch_size,
            self.alert_delivery_lease_seconds,
            self.alert_delivery_max_attempts,
        )
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 1
            for value in delivery_limits
        ):
            raise ValueError("Alert delivery worker limits must be positive integers.")
        if self.alert_delivery_batch_size != 1:
            raise ValueError(
                "alert_delivery_batch_size is fixed at 1 until bounded per-event "
                "lease renewal or concurrent delivery is implemented."
            )
        if self.alert_delivery_lease_seconds < 30:
            raise ValueError("alert_delivery_lease_seconds must be at least 30.")
        if (
            self.alert_delivery_worker_enabled
            and self.alert_delivery_lease_seconds < 90
        ):
            raise ValueError(
                "Enabled alert delivery requires a lease of at least 90 seconds "
                "for the 60-second isolated event deadline and acknowledgement margin."
            )
        if self.alert_delivery_max_attempts > 32:
            raise ValueError("alert_delivery_max_attempts must not exceed 32.")
        if self.app_env.strip().lower() == "production" and not self.redis_url:
            raise ValueError("REDIS_URL is required in production; shared security guards cannot be disabled.")
        if self.app_env.strip().lower() == "production" and not self.firebase_project_id.strip():
            raise ValueError(
                "FIREBASE_PROJECT_ID is required in production; authenticated routes cannot verify identities without it."
            )
        if self.app_env.strip().lower() == "production" and (
            self.databento_api_key
            or self.databento_live_enabled
            or self.databento_historical_enabled
        ):
            raise ValueError(
                "Databento credentials and provider access are disabled in production "
                "by the ZERO MONEY policy."
            )
        if self.redis_url:
            try:
                parsed = urlsplit(self.redis_url)
                _ = parsed.port
            except ValueError as exc:
                raise ValueError("REDIS_URL is invalid.") from exc
            if parsed.scheme not in ("redis", "rediss") or not parsed.hostname:
                raise ValueError("REDIS_URL must be a valid redis:// or rediss:// URL.")
            production = self.app_env.strip().lower() == "production"
            if production and parsed.scheme != "rediss":
                raise ValueError("Production REDIS_URL must use rediss:// TLS.")
            if production and (not parsed.username or not parsed.password):
                raise ValueError(
                    "Production REDIS_URL must include a non-empty Redis ACL username and password."
                )
        limits = (
            self.http_rate_limit_per_client, self.http_rate_limit_global,
            self.websocket_connection_limit_global,
            self.websocket_connection_limit_per_account, self.websocket_lease_seconds,
        )
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 1
            for value in limits
        ):
            raise ValueError("Shared security guard limits must be positive integers.")

    @property
    def provider_configured(self) -> bool:
        return bool(self.databento_api_key)

    @classmethod
    def from_environment(cls) -> "Settings":
        registry_path = os.getenv(
            "INSTRUMENT_REGISTRY_DB_PATH", "./data/instrument_registry.sqlite3"
        ).strip()
        if not registry_path or registry_path == ":memory:":
            registry_path = "./data/instrument_registry.sqlite3"

        app_env = os.getenv("APP_ENV", "development").strip() or "development"
        alert_device_store_enabled = _parse_bool(
            os.getenv("ALERT_DEVICE_STORE_ENABLED", "false")
        )
        alert_device_encryption_key = (
            _load_alert_device_encryption_key(
                os.getenv("ALERT_DEVICE_ENCRYPTION_KEY_FILE", "")
            )
            if alert_device_store_enabled
            else b""
        )
        return cls(
            app_env=app_env,
            market_data_ws_token=os.getenv("MARKET_DATA_WS_TOKEN", "").strip(),
            cors_allowed_origins=_parse_cors_origins(
                os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173"),
                app_env=app_env,
            ),
            databento_api_key=os.getenv("DATABENTO_API_KEY", "").strip(),
            databento_dataset=os.getenv("DATABENTO_DATASET", "GLBX.MDP3").strip() or "GLBX.MDP3",
            databento_live_enabled=_parse_bool(os.getenv("DATABENTO_LIVE_ENABLED", "false")),
            databento_historical_enabled=_parse_bool(
                os.getenv("DATABENTO_HISTORICAL_ENABLED", "false")
            ),
            databento_live_symbols=_parse_csv(os.getenv("DATABENTO_LIVE_SYMBOLS", "")),
            databento_definition_symbols=_parse_csv(
                os.getenv("DATABENTO_DEFINITION_SYMBOLS", "")
            ),
            historical_max_span_hours=_parse_int(
                os.getenv("DATABENTO_HISTORICAL_MAX_SPAN_HOURS", "24"), 24
            ),
            historical_window_minutes=_parse_int(
                os.getenv("DATABENTO_HISTORICAL_WINDOW_MINUTES", "60"), 60
            ),
            allowed_roots=tuple(
                root.upper() for root in _parse_csv(os.getenv("INSTRUMENT_ROOTS", "ES,NQ,GC"))
            ) or ("ES", "NQ", "GC"),
            ohlcv_queue_max=_parse_int(os.getenv("OHLCV_QUEUE_MAX", "10000"), 10_000),
            ohlcv_max_response_bars=_parse_int(
                os.getenv("OHLCV_MAX_RESPONSE_BARS", "5000"), 5_000
            ),
            instrument_registry_db_path=registry_path,
            session_calendar_artifact_path=os.getenv("SESSION_CALENDAR_ARTIFACT_PATH", "").strip(),
            session_calendar_sha256=os.getenv("SESSION_CALENDAR_SHA256", "").strip(),
            session_calendar_version=os.getenv("SESSION_CALENDAR_VERSION", "").strip(),
            session_calendar_releases=_parse_session_calendar_releases(
                os.getenv("SESSION_CALENDAR_RELEASES_JSON", "")
            ),
            firebase_project_id=os.getenv("FIREBASE_PROJECT_ID", "").strip(),
            alert_device_store_enabled=alert_device_store_enabled,
            alert_device_encryption_key=alert_device_encryption_key,
            alert_delivery_worker_enabled=_parse_bool(
                os.getenv("ALERT_DELIVERY_WORKER_ENABLED", "false")
            ),
            alert_delivery_poll_interval_seconds=_parse_int(
                os.getenv("ALERT_DELIVERY_POLL_INTERVAL_SECONDS", "2"), 2
            ),
            alert_delivery_batch_size=_parse_int(
                os.getenv("ALERT_DELIVERY_BATCH_SIZE", "1"), 1
            ),
            alert_delivery_lease_seconds=_parse_int(
                os.getenv("ALERT_DELIVERY_LEASE_SECONDS", "120"), 120
            ),
            alert_delivery_max_attempts=_parse_int(
                os.getenv("ALERT_DELIVERY_MAX_ATTEMPTS", "8"), 8
            ),
            redis_url=os.getenv("REDIS_URL", "").strip(),
            observability_metrics_token=os.getenv("OBSERVABILITY_METRICS_TOKEN", "").strip(),
            http_rate_limit_per_client=_parse_int(os.getenv("HTTP_RATE_LIMIT_PER_CLIENT", "120"), 120),
            http_rate_limit_global=_parse_int(os.getenv("HTTP_RATE_LIMIT_GLOBAL", "6000"), 6000),
            websocket_connection_limit_global=_parse_int(os.getenv("WEBSOCKET_CONNECTION_LIMIT_GLOBAL", "500"), 500),
            websocket_connection_limit_per_account=_parse_int(os.getenv("WEBSOCKET_CONNECTION_LIMIT_PER_ACCOUNT", "5"), 5),
            websocket_lease_seconds=_parse_int(os.getenv("WEBSOCKET_LEASE_SECONDS", "45"), 45),
        )
