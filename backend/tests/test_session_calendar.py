from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from app.session_calendar import (
    CHICAGO,
    InvalidSessionCalendar,
    SessionCalendar,
    SessionRecord,
    datetime_to_epoch_ns,
    lookup_instant,
    resolve_trading_date,
)


def make_calendar(records, *, start=date(2024, 3, 1), end=date(2024, 3, 31)):
    return SessionCalendar(
        calendar_id="CME_EQUITY_INDEX",
        version="2024.03.1",
        product_family="ES",
        effective_start=start,
        effective_end=end,
        source_id="official-cme-schedule-release",
        source_url="https://www.cmegroup.com/trading-hours.html",
        published_at_utc=datetime(2024, 2, 1, tzinfo=timezone.utc),
        checksum="sha256:verified-release-digest",
        records={record.trading_date: record for record in records},
    )


def session(trading_date, open_local, close_local, kind="regular"):
    return SessionRecord(
        trading_date=trading_date,
        kind=kind,
        open_local=datetime.fromisoformat(open_local).replace(tzinfo=CHICAGO)
        if open_local else None,
        close_local=datetime.fromisoformat(close_local).replace(tzinfo=CHICAGO)
        if close_local else None,
    )


def test_sunday_reopen_maps_to_monday_trading_date_across_spring_dst():
    monday = session(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    calendar = make_calendar([monday])
    result = lookup_instant(calendar, datetime(2024, 3, 10, 22, 0, tzinfo=timezone.utc))
    assert result.state == "open"
    assert result.trading_date == date(2024, 3, 11)
    assert result.session_open_ns == datetime_to_epoch_ns(monday.open_local)


def test_fall_dst_uses_chicago_zone_rules_not_a_fixed_utc_offset():
    sunday = session(date(2024, 11, 4), "2024-11-03T17:00:00", "2024-11-04T16:00:00")
    assert sunday.open_local.utcoffset().total_seconds() == -6 * 3600


def test_maintenance_requires_explicit_records_on_both_sides():
    monday = session(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    tuesday = session(date(2024, 3, 12), "2024-03-11T17:00:00", "2024-03-12T16:00:00")
    calendar = make_calendar([monday, tuesday])
    result = lookup_instant(calendar, datetime(2024, 3, 11, 21, 30, tzinfo=timezone.utc))
    assert result.state == "maintenance"


def test_missing_trading_date_is_unknown_not_assumed_regular_or_closed():
    monday = session(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    calendar = make_calendar([monday])
    result = lookup_instant(calendar, datetime(2024, 3, 12, 15, 0, tzinfo=timezone.utc))
    assert result.state == "unknown"
    assert resolve_trading_date(calendar, date(2024, 3, 12)) is None


def test_explicit_holiday_closure_is_distinct_from_missing_schedule_data():
    closed = session(date(2024, 3, 12), None, None, kind="closed")
    calendar = make_calendar([closed])
    result = lookup_instant(calendar, datetime(2024, 3, 12, 15, 0, tzinfo=timezone.utc))
    assert result.state == "closed"
    assert result.trading_date == date(2024, 3, 12)


def test_special_and_early_close_records_are_labelled_as_special_sessions():
    early = session(
        date(2024, 3, 13), "2024-03-12T17:00:00", "2024-03-13T12:00:00",
        kind="early_close",
    )
    calendar = make_calendar([early])
    result = lookup_instant(calendar, datetime(2024, 3, 13, 16, 0, tzinfo=timezone.utc))
    assert result.state == "special-session"



def test_early_close_does_not_mislabel_later_closed_time_as_daily_maintenance():
    wednesday = session(
        date(2024, 3, 13), "2024-03-12T17:00:00", "2024-03-13T12:00:00",
        kind="early_close",
    )
    thursday = session(
        date(2024, 3, 14), "2024-03-13T17:00:00", "2024-03-14T16:00:00",
    )
    calendar = make_calendar([wednesday, thursday])
    result = lookup_instant(calendar, datetime(2024, 3, 13, 21, 30, tzinfo=timezone.utc))
    assert result.state == "closed"


def test_calendar_rejects_naive_or_wrong_timezone_boundaries():
    with pytest.raises(InvalidSessionCalendar):
        SessionRecord(
            date(2024, 3, 11), "regular",
            datetime(2024, 3, 10, 17, 0),
            datetime(2024, 3, 11, 16, 0, tzinfo=CHICAGO),
        )


def test_calendar_rejects_product_family_calendar_mismatch():
    with pytest.raises(InvalidSessionCalendar):
        SessionCalendar(
            calendar_id="COMEX_GOLD", version="1", product_family="ES",
            effective_start=date(2024, 3, 1), effective_end=date(2024, 3, 31),
            source_id="source", source_url="https://example.com/schedule",
            published_at_utc=datetime(2024, 2, 1, tzinfo=timezone.utc),
            checksum="sha256:test", records={},
        )
