"""Strict loader for externally pinned, versioned CME calendar artifacts.

The caller must obtain expected_sha256 from a trusted release manifest/channel.
A matching digest proves byte identity with that pin; it does NOT by itself
authenticate the publisher or make an unverified schedule official.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
import re
from typing import Any
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from app.session_calendar import (
    InvalidSessionCalendar,
    SessionCalendar,
    SessionRecord,
)

_CHICAGO = ZoneInfo("America/Chicago")
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
_TOP_LEVEL_KEYS = {
    "schema_version", "calendar_id", "version", "product_family",
    "effective_start", "effective_end", "timezone", "source", "records",
}
_SOURCE_KEYS = {"source_id", "source_url", "published_at_utc"}
_RECORD_KEYS = {"trading_date", "kind", "open_local", "close_local"}


class SessionCalendarArtifactError(ValueError):
    """Raised when a pinned calendar artifact is malformed or untrusted."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SessionCalendarArtifactError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise SessionCalendarArtifactError(f"Unsupported JSON constant: {value}")


def _object(value: Any, name: str, expected_keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise SessionCalendarArtifactError(f"{name} must contain exactly the documented fields.")
    return value


def _iso_date(value: Any, name: str) -> date:
    if not isinstance(value, str):
        raise SessionCalendarArtifactError(f"{name} must be an ISO date string.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise SessionCalendarArtifactError(f"{name} is not a valid ISO date.") from exc
    if parsed.isoformat() != value:
        raise SessionCalendarArtifactError(f"{name} must use YYYY-MM-DD format.")
    return parsed


def _chicago_local_datetime(value: Any, name: str) -> datetime:
    if not isinstance(value, str):
        raise SessionCalendarArtifactError(f"{name} must be a local ISO datetime string.")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise SessionCalendarArtifactError(f"{name} is not a valid ISO datetime.") from exc
    if parsed.tzinfo is not None:
        raise SessionCalendarArtifactError(f"{name} must not contain an offset; timezone is declared separately.")

    candidates = [parsed.replace(tzinfo=_CHICAGO, fold=fold) for fold in (0, 1)]
    valid: list[datetime] = []
    for candidate in candidates:
        round_trip = candidate.astimezone(timezone.utc).astimezone(_CHICAGO)
        if round_trip.replace(tzinfo=None) == parsed:
            valid.append(candidate)
    if not valid:
        raise SessionCalendarArtifactError(f"{name} falls in a nonexistent Chicago local-time interval.")
    if len(valid) == 2 and valid[0].utcoffset() != valid[1].utcoffset():
        raise SessionCalendarArtifactError(f"{name} is ambiguous during a Chicago DST transition.")
    return valid[0]


def _published_at_utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise SessionCalendarArtifactError("published_at_utc must be an ISO datetime string.")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SessionCalendarArtifactError("published_at_utc is invalid.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise SessionCalendarArtifactError("published_at_utc must have an explicit UTC offset.")
    return parsed.astimezone(timezone.utc)


def _validate_source(source: dict[str, Any]) -> None:
    source_id = source["source_id"]
    source_url = source["source_url"]
    if not isinstance(source_id, str) or not source_id.strip():
        raise SessionCalendarArtifactError("source_id is required.")
    if not isinstance(source_url, str):
        raise SessionCalendarArtifactError("source_url must be a string.")
    parsed = urlsplit(source_url)
    host = (parsed.hostname or "").lower()
    if (
        parsed.scheme != "https"
        or not (host == "cmegroup.com" or host.endswith(".cmegroup.com"))
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in (None, 443)
    ):
        raise SessionCalendarArtifactError("source_url must be an HTTPS URL on the cmegroup.com domain.")


def load_session_calendar_artifact(
    raw_bytes: bytes,
    *,
    expected_sha256: str,
) -> SessionCalendar:
    """Parse a complete canonical JSON release after verifying its pinned SHA-256.

    The expected digest must come from an independently trusted source. This
    loader rejects partial effective-date coverage, duplicate dates/JSON keys,
    unknown fields, ambiguous/nonexistent Chicago local times, and non-CME URLs.
    It never fetches remote content or registers the resulting calendar.
    """
    if not isinstance(raw_bytes, bytes) or not raw_bytes:
        raise SessionCalendarArtifactError("Calendar artifact must be non-empty bytes.")
    if not isinstance(expected_sha256, str) or not _SHA256.fullmatch(expected_sha256):
        raise SessionCalendarArtifactError("expected_sha256 must be a 64-character hexadecimal digest.")

    actual_digest = hashlib.sha256(raw_bytes).hexdigest()
    if actual_digest.lower() != expected_sha256.lower():
        raise SessionCalendarArtifactError("Calendar artifact SHA-256 does not match the trusted pin.")

    try:
        decoded = raw_bytes.decode("utf-8")
        payload = json.loads(
            decoded,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except UnicodeDecodeError as exc:
        raise SessionCalendarArtifactError("Calendar artifact must be valid UTF-8.") from exc
    except json.JSONDecodeError as exc:
        raise SessionCalendarArtifactError("Calendar artifact is not valid JSON.") from exc

    payload = _object(payload, "Calendar artifact", _TOP_LEVEL_KEYS)
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise SessionCalendarArtifactError("Unsupported calendar artifact schema_version.")
    if payload["timezone"] != "America/Chicago":
        raise SessionCalendarArtifactError("Calendar timezone must be America/Chicago.")

    source = _object(payload["source"], "source", _SOURCE_KEYS)
    _validate_source(source)
    published_at = _published_at_utc(source["published_at_utc"])

    effective_start = _iso_date(payload["effective_start"], "effective_start")
    effective_end = _iso_date(payload["effective_end"], "effective_end")
    if effective_end < effective_start:
        raise SessionCalendarArtifactError("Calendar effective date range is reversed.")

    raw_records = payload["records"]
    if not isinstance(raw_records, list):
        raise SessionCalendarArtifactError("records must be a JSON array.")

    records: dict[date, SessionRecord] = {}
    for index, raw_record in enumerate(raw_records):
        item = _object(raw_record, f"records[{index}]", _RECORD_KEYS)
        trading_date = _iso_date(item["trading_date"], f"records[{index}].trading_date")
        if trading_date in records:
            raise SessionCalendarArtifactError(f"Duplicate trading_date: {trading_date.isoformat()}")
        kind = item["kind"]
        if not isinstance(kind, str):
            raise SessionCalendarArtifactError(f"records[{index}].kind must be a string.")
        if kind == "closed":
            if item["open_local"] is not None or item["close_local"] is not None:
                raise SessionCalendarArtifactError("Closed records must have null session boundaries.")
            open_local = close_local = None
        else:
            open_local = _chicago_local_datetime(item["open_local"], f"records[{index}].open_local")
            close_local = _chicago_local_datetime(item["close_local"], f"records[{index}].close_local")
        try:
            records[trading_date] = SessionRecord(
                trading_date=trading_date,
                kind=kind,  # validated by SessionRecord
                open_local=open_local,
                close_local=close_local,
            )
        except (InvalidSessionCalendar, TypeError) as exc:
            raise SessionCalendarArtifactError(f"Invalid session record at index {index}: {exc}") from exc

    expected_days = (effective_end - effective_start).days + 1
    if len(records) != expected_days:
        raise SessionCalendarArtifactError("Calendar records do not cover every effective date exactly once.")
    expected_dates = {
        effective_start.fromordinal(effective_start.toordinal() + offset)
        for offset in range(expected_days)
    }
    if records.keys() != expected_dates:
        raise SessionCalendarArtifactError("Calendar records contain missing or out-of-range effective dates.")

    try:
        return SessionCalendar(
            calendar_id=payload["calendar_id"],
            version=payload["version"],
            product_family=payload["product_family"],
            effective_start=effective_start,
            effective_end=effective_end,
            source_id=source["source_id"],
            source_url=source["source_url"],
            published_at_utc=published_at,
            checksum=f"sha256:{actual_digest}",
            records=records,
        )
    except (InvalidSessionCalendar, AttributeError, TypeError) as exc:
        raise SessionCalendarArtifactError(f"Invalid calendar release metadata: {exc}") from exc
