"""Environment-backed settings for the DEZZTA CHART backend.

All provider credentials come exclusively from backend environment variables.
Settings.__repr__ never includes the Databento key.
"""

from dataclasses import dataclass, field
import json
import os
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
    redis_url: str = field(default="", repr=False)
    http_rate_limit_per_client: int = 120
    http_rate_limit_global: int = 6000
    websocket_connection_limit_global: int = 500
    websocket_connection_limit_per_account: int = 5
    websocket_lease_seconds: int = 45

    def __post_init__(self) -> None:
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
            redis_url=os.getenv("REDIS_URL", "").strip(),
            http_rate_limit_per_client=_parse_int(os.getenv("HTTP_RATE_LIMIT_PER_CLIENT", "120"), 120),
            http_rate_limit_global=_parse_int(os.getenv("HTTP_RATE_LIMIT_GLOBAL", "6000"), 6000),
            websocket_connection_limit_global=_parse_int(os.getenv("WEBSOCKET_CONNECTION_LIMIT_GLOBAL", "500"), 500),
            websocket_connection_limit_per_account=_parse_int(os.getenv("WEBSOCKET_CONNECTION_LIMIT_PER_ACCOUNT", "5"), 5),
            websocket_lease_seconds=_parse_int(os.getenv("WEBSOCKET_LEASE_SECONDS", "45"), 45),
        )
