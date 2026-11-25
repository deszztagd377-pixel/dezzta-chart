"""Dedicated least-privilege Redis relay configuration.

This is deliberately separate from Settings.redis_url, which is reserved for
shared HTTP/WebSocket security guards. The config is not wired into app startup
until snapshot transport and owner-controlled ACL credentials are ready.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Mapping
from urllib.parse import unquote, urlsplit


DEFAULT_OHLCV_STREAM_KEY = "dezzta:market-data:ohlcv:v1"
PUBLISHER_ACL_COMMANDS = ("+ping", "+xadd", "+xrange")
GATEWAY_ACL_COMMANDS = (
    # Root permissions are limited to the stream key.
    "+ping",
    "+xgroup|create",
    "+xautoclaim",
    "+xreadgroup",
    "+xack",
    "+xrange",
)
GATEWAY_LEASE_ACL_COMMANDS = ("+set", "+eval", "+get", "+pexpire", "+del")


def gateway_lease_acl_selector(lease_key: str) -> str:
    """Build a Redis 7 ACL selector that confines lease commands to one key."""
    if (
        not isinstance(lease_key, str)
        or re.fullmatch(r"[A-Za-z0-9:_-]{1,256}", lease_key) is None
    ):
        raise ValueError("lease_key must be an exact literal Redis key.")
    commands = " ".join(GATEWAY_LEASE_ACL_COMMANDS)
    return "(" + commands + " ~" + lease_key + ")"


def require_ohlcv_runtime_role(environ: Mapping[str, str], expected_role: str) -> str:
    """Require an explicit, non-conflicting source/gateway process identity."""
    if expected_role not in {"source", "gateway"}:
        raise ValueError("expected_role must be source or gateway.")
    role = environ.get("OHLCV_REDIS_ROLE", "").strip().lower()
    if role not in {"source", "gateway"}:
        raise ValueError("OHLCV_REDIS_ROLE must be explicitly set to source or gateway.")
    if role != expected_role:
        raise ValueError(
            f"OHLCV_REDIS_ROLE={role} cannot initialize the {expected_role} runtime."
        )
    return role


def validate_ohlcv_runtime_binding(
    environ: Mapping[str, str],
    *,
    publisher_runtime_factory: object | None,
    replica_runtime_factory: object | None,
) -> str | None:
    """Fail closed when relay enablement and injected app role do not agree."""
    enabled = _parse_bool(
        environ.get("OHLCV_REDIS_ENABLED", "false"),
        name="OHLCV_REDIS_ENABLED",
    )
    if not enabled:
        return None
    configured_role = environ.get("OHLCV_REDIS_ROLE", "").strip().lower()
    role = require_ohlcv_runtime_role(
        environ,
        configured_role if configured_role in {"source", "gateway"} else "gateway",
    )
    if role == "source" and not callable(publisher_runtime_factory):
        raise ValueError(
            "Source OHLCV relay is enabled but no publisher_runtime_factory was injected."
        )
    if role == "gateway" and not callable(replica_runtime_factory):
        raise ValueError(
            "Gateway OHLCV relay is enabled but no replica_runtime_factory was injected."
        )
    if role == "source" and replica_runtime_factory is not None:
        raise ValueError("Source role cannot inject a gateway replica runtime.")
    if role == "gateway" and publisher_runtime_factory is not None:
        raise ValueError("Gateway role cannot inject a source publisher runtime.")
    return role


def validate_absolute_database_path(value: str, *, name: str) -> str:
    """Reject relative, symbolic-link, and directory database targets."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required.")
    path = Path(value.strip()).expanduser()
    if not path.is_absolute():
        raise ValueError(f"{name} must be an absolute file path.")
    if path.is_symlink():
        raise ValueError(f"{name} must not be a symbolic link.")
    if path.exists() and not path.is_file():
        raise ValueError(f"{name} must reference a file, not a directory.")
    return str(path)


def _parse_bool(value: str, *, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off", ""}:
        return False
    raise ValueError(f"{name} must be a boolean value.")


def _parse_acl_url(value: str, *, name: str, production: bool) -> tuple[str, str]:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required when the OHLCV relay is enabled.")
    try:
        parsed = urlsplit(value.strip())
        # Accessing .port validates malformed port syntax.
        _ = parsed.port
    except ValueError as exc:
        raise ValueError(f"{name} is not a valid Redis URL.") from exc
    if parsed.scheme not in {"redis", "rediss"} or not parsed.hostname:
        raise ValueError(f"{name} must be a valid redis:// or rediss:// URL.")
    if production and parsed.scheme != "rediss":
        raise ValueError(f"{name} must use rediss:// TLS in production.")
    if not parsed.username or not parsed.password:
        raise ValueError(f"{name} must include a dedicated ACL username and password.")
    if parsed.path not in {"", "/0"}:
        raise ValueError(f"{name} must use Redis database 0; non-zero DB selection expands ACL scope.")
    if parsed.query or parsed.fragment:
        raise ValueError(f"{name} must not contain query parameters or fragments.")
    username = unquote(parsed.username)
    password = unquote(parsed.password)
    if not username.strip() or not password:
        raise ValueError(f"{name} must include non-empty ACL credentials.")
    return username, password


@dataclass(frozen=True, slots=True)
class OhlcvRedisRelayConfig:
    """Publisher/gateway URLs with separate ACL identities and exact key scope."""

    enabled: bool = False
    stream_key: str = DEFAULT_OHLCV_STREAM_KEY
    publisher_url: str = field(default="", repr=False)
    gateway_url: str = field(default="", repr=False)
    production: bool = False

    def __post_init__(self) -> None:
        if type(self.enabled) is not bool or type(self.production) is not bool:
            raise ValueError("enabled and production must be booleans.")
        if (
            not isinstance(self.stream_key, str)
            or not self.stream_key
            or len(self.stream_key) > 256
            or self.stream_key.strip() != self.stream_key
            or any(char.isspace() or char in "*?[]" for char in self.stream_key)
        ):
            raise ValueError("stream_key must be a non-empty exact Redis key without whitespace or glob characters.")
        if not self.enabled:
            return
        publisher_user, publisher_password = _parse_acl_url(
            self.publisher_url, name="OHLCV_REDIS_PUBLISH_URL",
            production=self.production,
        )
        gateway_user, gateway_password = _parse_acl_url(
            self.gateway_url, name="OHLCV_REDIS_GATEWAY_URL",
            production=self.production,
        )
        if publisher_user == gateway_user:
            raise ValueError("Publisher and gateway must use different Redis ACL usernames.")
        if publisher_password == gateway_password:
            raise ValueError("Publisher and gateway must use different Redis ACL passwords.")

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
        *,
        production: bool | None = None,
    ) -> "OhlcvRedisRelayConfig":
        source = os.environ if environ is None else environ
        enabled = _parse_bool(
            source.get("OHLCV_REDIS_ENABLED", "false"),
            name="OHLCV_REDIS_ENABLED",
        )
        if production is None:
            production = source.get("APP_ENV", "").strip().lower() == "production"
        return cls(
            enabled=enabled,
            stream_key=source.get("OHLCV_REDIS_STREAM_KEY", DEFAULT_OHLCV_STREAM_KEY),
            publisher_url=source.get("OHLCV_REDIS_PUBLISH_URL", ""),
            gateway_url=source.get("OHLCV_REDIS_GATEWAY_URL", ""),
            production=production,
        )
