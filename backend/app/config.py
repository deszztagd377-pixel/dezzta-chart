"""Environment-backed settings for the DEZZTA CHART backend."""

from dataclasses import dataclass
import os


def _parse_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    app_env: str
    market_data_ws_token: str
    cors_allowed_origins: tuple[str, ...]

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "development").strip() or "development",
            market_data_ws_token=os.getenv("MARKET_DATA_WS_TOKEN", "").strip(),
            cors_allowed_origins=_parse_csv(
                os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
            ),
        )
