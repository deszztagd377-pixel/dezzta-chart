"""Runtime loading and ingestion wiring for pinned CME session calendars.

A digest is accepted only as an externally supplied trusted pin. This module
never downloads schedules or treats test fixtures as official exchange data.
If the release cannot be loaded exactly as configured, the registry stays
empty and CME futures bars are rejected before persistence and pipeline writes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from app.instrument_registry import SQLiteInstrumentRegistry
from app.ohlcv import OhlcvBar
from app.session_bar_validation import (
    SessionBarRejected,
    validate_intraday_bar_session,
)
from app.session_calendar import SessionCalendarRegistry
from app.session_calendar_loader import (
    SessionCalendarArtifactError,
    load_session_calendar_artifact,
)

_MAX_CALENDAR_ARTIFACT_BYTES = 16 * 1024 * 1024


def load_session_calendar_runtime(
    *,
    artifact_path: str,
    expected_sha256: str,
    expected_version: str,
    releases: tuple[tuple[str, str, str], ...] = (),
) -> tuple[SessionCalendarRegistry, dict[str, Any]]:
    """Load pinned calendar releases atomically; preserve the legacy single-release API."""
    registry = SessionCalendarRegistry()
    if releases:
        if any((artifact_path.strip(), expected_sha256.strip(), expected_version.strip())):
            return registry, {"state": "unavailable", "reason": "mixed_release_configuration"}
        if not isinstance(releases, tuple) or len(releases) > 32:
            return registry, {"state": "unavailable", "reason": "invalid_release_manifest"}
        calendars = []
        release_status = []
        seen_calendar_ids = set()
        try:
            for descriptor in releases:
                if not isinstance(descriptor, tuple) or len(descriptor) != 3:
                    raise SessionCalendarArtifactError("Invalid release descriptor.")
                release_path, release_digest, release_version = descriptor
                if any(not isinstance(value, str) or not value.strip() for value in descriptor):
                    raise SessionCalendarArtifactError("Release descriptor fields must be non-empty strings.")
                path = Path(release_path).expanduser()
                size = path.stat().st_size
                if size < 1 or size > _MAX_CALENDAR_ARTIFACT_BYTES:
                    raise SessionCalendarArtifactError("Calendar artifact size is outside the supported limit.")
                calendar = load_session_calendar_artifact(
                    path.read_bytes(), expected_sha256=release_digest
                )
                if calendar.version != release_version:
                    raise SessionCalendarArtifactError("Calendar artifact version does not match its explicit pin.")
                if calendar.calendar_id in seen_calendar_ids:
                    raise SessionCalendarArtifactError("Only one active pinned version per calendar_id is supported.")
                seen_calendar_ids.add(calendar.calendar_id)
                calendars.append(calendar)
                release_status.append({
                    "calendar_id": calendar.calendar_id,
                    "version": calendar.version,
                    "product_family": calendar.product_family,
                    "source_id": calendar.source_id,
                    "sha256": calendar.checksum.removeprefix("sha256:"),
                })
            registry = SessionCalendarRegistry(tuple(calendars))
        except (OSError, ValueError, TypeError):
            return SessionCalendarRegistry(), {"state": "unavailable", "reason": "release_validation_failed"}
        if not calendars:
            return registry, {"state": "unconfigured", "reason": "release_not_configured"}
        return registry, {"state": "available", "release_count": len(calendars), "releases": release_status}

    configured = (artifact_path.strip(), expected_sha256.strip(), expected_version.strip())
    if not any(configured):
        return registry, {"state": "unconfigured", "reason": "release_not_configured"}
    if not all(configured):
        return registry, {"state": "unavailable", "reason": "incomplete_release_configuration"}

    try:
        path = Path(artifact_path).expanduser()
        size = path.stat().st_size
        if size < 1 or size > _MAX_CALENDAR_ARTIFACT_BYTES:
            raise SessionCalendarArtifactError("Calendar artifact size is outside the supported limit.")
        raw_bytes = path.read_bytes()
        calendar = load_session_calendar_artifact(
            raw_bytes, expected_sha256=expected_sha256
        )
        if calendar.version != expected_version:
            raise SessionCalendarArtifactError(
                "Calendar artifact version does not match the configured explicit release."
            )
        registry = SessionCalendarRegistry((calendar,))
    except (OSError, ValueError) as exc:
        reason = (
            "artifact_unavailable"
            if isinstance(exc, OSError)
            else "release_validation_failed"
        )
        return SessionCalendarRegistry(), {"state": "unavailable", "reason": reason}

    return registry, {
        "state": "available",
        "calendar_id": calendar.calendar_id,
        "version": calendar.version,
        "product_family": calendar.product_family,
        "source_id": calendar.source_id,
        "sha256": calendar.checksum.removeprefix("sha256:"),
    }


def build_provider_session_bar_validator(
    instrument_registry: SQLiteInstrumentRegistry,
    calendar_registry: SessionCalendarRegistry,
    *,
    calendar_version: str = "",
    calendar_versions: dict[str, str] | None = None,
):
    """Validate durable provider identity and CME sessions before ingestion.

    Non-futures retain the existing provider-bar path after durable identity
    resolution. Futures require an exact canonical mapping and explicit,
    loaded calendar release. No raw-symbol inference is performed.
    """
    def validate(bar: OhlcvBar):
        if not isinstance(bar, OhlcvBar):
            raise SessionBarRejected("invalid_bar")

        try:
            mapping = instrument_registry.resolve_provider_mapping(
                provider=bar.provider,
                dataset=bar.dataset,
                publisher_id=bar.publisher_id,
                instrument_id=bar.instrument_id,
                timestamp_ns=bar.ts_event_ns,
            )
        except Exception:
            raise SessionBarRejected("provider_mapping_lookup_failed") from None
        if mapping is None:
            raise SessionBarRejected("provider_mapping_unavailable")
        if mapping.raw_symbol != bar.raw_symbol:
            raise SessionBarRejected("provider_mapping_symbol_mismatch")
        if mapping.series_type != bar.series_type:
            raise SessionBarRejected("provider_mapping_series_mismatch")

        try:
            instrument = instrument_registry.get_instrument(mapping.canonical_id)
        except Exception:
            raise SessionBarRejected("canonical_instrument_lookup_failed") from None
        if instrument is None:
            raise SessionBarRejected("canonical_instrument_unavailable")
        if not instrument.is_active:
            raise SessionBarRejected("inactive_instrument")

        if instrument.asset_class != "future" or instrument.instrument_type != "future":
            return None

        explicit_version = (calendar_versions or {}).get(
            instrument.session_calendar_id or "", calendar_version
        )
        return validate_intraday_bar_session(
            bar,
            instrument,
            calendar_registry,
            calendar_version=explicit_version,
        )

    return validate
