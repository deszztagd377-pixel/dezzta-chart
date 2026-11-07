import hashlib
import json
from datetime import date

import pytest

from app.session_calendar_loader import (
    SessionCalendarArtifactError,
    load_session_calendar_artifact,
)


def artifact_payload():
    return {
        "schema_version": 1,
        "calendar_id": "CME_EQUITY_INDEX",
        "version": "2026.11.1",
        "product_family": "ES",
        "effective_start": "2026-11-02",
        "effective_end": "2026-11-03",
        "timezone": "America/Chicago",
        "source": {
            "source_id": "cme-schedule-release-2026-11",
            "source_url": "https://www.cmegroup.com/markets/equities.html",
            "published_at_utc": "2026-10-20T12:00:00Z",
        },
        "records": [
            {
                "trading_date": "2026-11-02",
                "kind": "regular",
                "open_local": "2026-11-01T17:00:00",
                "close_local": "2026-11-02T16:00:00",
            },
            {
                "trading_date": "2026-11-03",
                "kind": "closed",
                "open_local": None,
                "close_local": None,
            },
        ],
    }


def pinned_bytes(payload=None):
    raw = json.dumps(
        artifact_payload() if payload is None else payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return raw, hashlib.sha256(raw).hexdigest()


def test_loads_complete_calendar_only_after_matching_sha256_pin():
    raw, digest = pinned_bytes()

    calendar = load_session_calendar_artifact(raw, expected_sha256=digest)

    assert calendar.calendar_id == "CME_EQUITY_INDEX"
    assert calendar.version == "2026.11.1"
    assert calendar.product_family == "ES"
    assert calendar.effective_start == date(2026, 11, 2)
    assert calendar.effective_end == date(2026, 11, 3)
    assert calendar.checksum == f"sha256:{digest}"
    assert set(calendar.records) == {date(2026, 11, 2), date(2026, 11, 3)}
    assert calendar.records[date(2026, 11, 3)].kind == "closed"


def test_rejects_digest_that_does_not_match_trusted_pin():
    raw, _ = pinned_bytes()

    with pytest.raises(SessionCalendarArtifactError, match="SHA-256"):
        load_session_calendar_artifact(raw, expected_sha256="0" * 64)


def test_rejects_missing_effective_date_instead_of_assuming_closed():
    payload = artifact_payload()
    payload["records"].pop()
    raw, digest = pinned_bytes(payload)

    with pytest.raises(SessionCalendarArtifactError, match="every effective date"):
        load_session_calendar_artifact(raw, expected_sha256=digest)


def test_rejects_duplicate_trading_date():
    payload = artifact_payload()
    payload["records"].append(dict(payload["records"][0]))
    raw, digest = pinned_bytes(payload)

    with pytest.raises(SessionCalendarArtifactError, match="Duplicate trading_date"):
        load_session_calendar_artifact(raw, expected_sha256=digest)


def test_rejects_duplicate_json_object_keys():
    raw = (
        b'{"schema_version":1,"schema_version":1,"calendar_id":"CME_EQUITY_INDEX"}'
    )
    digest = hashlib.sha256(raw).hexdigest()

    with pytest.raises(SessionCalendarArtifactError, match="Duplicate JSON key"):
        load_session_calendar_artifact(raw, expected_sha256=digest)


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("timezone", "UTC", "timezone must be America/Chicago"),
        ("effective_end", "2026-11-01", "range is reversed"),
    ],
)
def test_rejects_inconsistent_calendar_metadata(field, value, match):
    payload = artifact_payload()
    payload[field] = value
    raw, digest = pinned_bytes(payload)

    with pytest.raises(SessionCalendarArtifactError, match=match):
        load_session_calendar_artifact(raw, expected_sha256=digest)


def test_rejects_non_cme_source_url():
    payload = artifact_payload()
    payload["source"]["source_url"] = "https://example.com/calendar.json"
    raw, digest = pinned_bytes(payload)

    with pytest.raises(SessionCalendarArtifactError, match="cmegroup.com domain"):
        load_session_calendar_artifact(raw, expected_sha256=digest)


@pytest.mark.parametrize(
    "local_time,match",
    [
        ("2024-03-10T02:30:00", "nonexistent"),
        ("2024-11-03T01:30:00", "ambiguous"),
    ],
)
def test_rejects_nonexistent_or_ambiguous_chicago_local_times(local_time, match):
    payload = artifact_payload()
    payload["effective_start"] = "2024-03-10"
    payload["effective_end"] = "2024-03-10"
    payload["records"] = [
        {
            "trading_date": "2024-03-10",
            "kind": "special",
            "open_local": local_time,
            "close_local": "2024-03-10T03:30:00",
        }
    ]
    raw, digest = pinned_bytes(payload)

    with pytest.raises(SessionCalendarArtifactError, match=match):
        load_session_calendar_artifact(raw, expected_sha256=digest)


def test_rejects_unknown_schema_fields():
    payload = artifact_payload()
    payload["unreviewed_flag"] = True
    raw, digest = pinned_bytes(payload)

    with pytest.raises(SessionCalendarArtifactError, match="exactly the documented fields"):
        load_session_calendar_artifact(raw, expected_sha256=digest)
