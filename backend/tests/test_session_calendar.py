from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from app.session_calendar import (
    CHICAGO,
    InvalidSessionCalendar,
    SessionCalendar,
    SessionRecord,
    SessionCalendarRegistry,
    calendar_id_for_product_family,
    datetime_to_epoch_ns,
    lookup_instant,
    resolve_trading_date,
    session_bucket_bounds,
)
from app.instrument_identity import CanonicalInstrument


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


def test_product_family_selects_only_its_explicit_calendar():
    assert calendar_id_for_product_family("ES") == "CME_EQUITY_INDEX"
    assert calendar_id_for_product_family("NQ") == "CME_EQUITY_INDEX"
    assert calendar_id_for_product_family("GC") == "COMEX_GOLD"
    assert calendar_id_for_product_family("UNKNOWN") is None
    assert calendar_id_for_product_family("ESZ6") is None


def test_calendar_registry_requires_unambiguous_explicit_release_version():
    equity_v1 = make_calendar([])
    equity_v2 = SessionCalendar(
        calendar_id="CME_EQUITY_INDEX", version="2024.03.2", product_family="ES",
        effective_start=date(2024, 3, 1), effective_end=date(2024, 3, 31),
        source_id="official-cme-schedule-release",
        source_url="https://www.cmegroup.com/trading-hours.html",
        published_at_utc=datetime(2024, 2, 2, tzinfo=timezone.utc),
        checksum="sha256:second-release", records={},
    )
    registry = SessionCalendarRegistry((equity_v1, equity_v2))
    assert registry.get("CME_EQUITY_INDEX", "2024.03.1") is equity_v1
    assert registry.get("CME_EQUITY_INDEX", "2024.03.2") is equity_v2
    assert registry.get("CME_EQUITY_INDEX") is None
    assert registry.for_product_family("ES", "2024.03.2") is equity_v2
    assert registry.for_product_family("NQ", "2024.03.2") is None
    assert registry.for_product_family("GC", "2024.03.2") is None


def test_calendar_registry_rejects_conflicting_content_for_same_release_key():
    first = make_calendar([])
    conflicting = SessionCalendar(
        calendar_id=first.calendar_id, version=first.version,
        product_family=first.product_family,
        effective_start=first.effective_start, effective_end=first.effective_end,
        source_id=first.source_id, source_url=first.source_url,
        published_at_utc=first.published_at_utc,
        checksum="sha256:conflicting-content", records={},
    )
    registry = SessionCalendarRegistry((first,))
    with pytest.raises(InvalidSessionCalendar, match="cannot be replaced"):
        registry.register(conflicting)


def test_calendar_publication_timestamp_must_be_utc_and_is_normalized():
    calendar = SessionCalendar(
        calendar_id="CME_EQUITY_INDEX",
        version="2024.03.1",
        product_family="ES",
        effective_start=date(2024, 3, 1),
        effective_end=date(2024, 3, 31),
        source_id="official-cme-schedule-release",
        source_url="https://www.cmegroup.com/trading-hours.html",
        published_at_utc=datetime(
            2024, 2, 1, 12, 0, tzinfo=timezone(timedelta(0), "UTC+00")
        ),
        checksum="sha256:verified-release-digest",
        records={},
    )
    assert calendar.published_at_utc.tzinfo is timezone.utc
    assert calendar.published_at_utc == datetime(2024, 2, 1, 12, 0, tzinfo=timezone.utc)

    with pytest.raises(InvalidSessionCalendar, match="expressed in UTC"):
        SessionCalendar(
            calendar_id="CME_EQUITY_INDEX",
            version="2024.03.1",
            product_family="ES",
            effective_start=date(2024, 3, 1),
            effective_end=date(2024, 3, 31),
            source_id="official-cme-schedule-release",
            source_url="https://www.cmegroup.com/trading-hours.html",
            published_at_utc=datetime(2024, 2, 1, 12, 0, tzinfo=ZoneInfo("America/Chicago")),
            checksum="sha256:verified-release-digest",
            records={},
        )


def test_calendar_records_are_immutable_after_validation():
    monday = session(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    source_records = {monday.trading_date: monday}
    calendar = SessionCalendar(
        calendar_id="CME_EQUITY_INDEX", version="2024.03.1", product_family="ES",
        effective_start=date(2024, 3, 1), effective_end=date(2024, 3, 31),
        source_id="official-cme-schedule-release",
        source_url="https://www.cmegroup.com/trading-hours.html",
        published_at_utc=datetime(2024, 2, 1, tzinfo=timezone.utc),
        checksum="sha256:verified-release-digest", records=source_records,
    )
    source_records.clear()
    assert resolve_trading_date(calendar, monday.trading_date) is monday
    with pytest.raises(TypeError):
        calendar.records[date(2024, 3, 12)] = monday


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


def test_weekly_session_bucket_uses_first_open_and_last_close_only_with_full_coverage():
    records = []
    for offset in range(7):
        day = date(2024, 3, 11) + timedelta(days=offset)
        if offset < 5:
            open_day = day - timedelta(days=1)
            records.append(session(
                day, f"{open_day.isoformat()}T17:00:00",
                f"{day.isoformat()}T16:00:00",
            ))
        else:
            records.append(session(day, None, None, kind="closed"))
    calendar = make_calendar(records, start=date(2024, 3, 11), end=date(2024, 3, 17))
    bounds = session_bucket_bounds(calendar, date(2024, 3, 13), "1w")
    assert bounds is not None
    assert bounds.trading_period_start == date(2024, 3, 11)
    assert bounds.trading_period_end == date(2024, 3, 17)
    assert bounds.start_ns == datetime_to_epoch_ns(records[0].open_local)
    assert bounds.end_ns == datetime_to_epoch_ns(records[4].close_local)
    assert bounds.calendar_version == calendar.version


def test_weekly_session_bucket_refuses_partial_schedule_coverage():
    monday = session(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    calendar = make_calendar([monday], start=date(2024, 3, 11), end=date(2024, 3, 17))
    assert session_bucket_bounds(calendar, date(2024, 3, 11), "1w") is None


def test_session_bucket_rejects_intraday_timeframes():
    calendar = make_calendar([], start=date(2024, 3, 11), end=date(2024, 3, 17))
    with pytest.raises(ValueError):
        session_bucket_bounds(calendar, date(2024, 3, 11), "1h")



def canonical_future(*, symbol="ES", calendar_id="CME_EQUITY_INDEX"):
    return CanonicalInstrument(
        canonical_id="12345678-1234-5678-1234-567812345678",
        asset_class="future",
        instrument_type="future",
        symbol=symbol,
        venue="CME",
        settlement_currency="USD",
        expiration_date="2026-12-18",
        session_calendar_id=calendar_id,
    )


def test_calendar_registry_resolves_by_canonical_instrument_calendar_metadata():
    calendar = make_calendar([])
    registry = SessionCalendarRegistry((calendar,))

    resolved = registry.for_instrument(
        canonical_future(symbol="NQ", calendar_id="CME_EQUITY_INDEX"),
        version="2024.03.1",
    )

    assert resolved is calendar


def test_calendar_resolution_does_not_infer_from_canonical_or_raw_symbol():
    calendar = make_calendar([])
    registry = SessionCalendarRegistry((calendar,))

    resolved = registry.for_instrument(
        canonical_future(symbol="GC", calendar_id="CME_EQUITY_INDEX"),
        version="2024.03.1",
    )

    assert resolved is calendar


def test_calendar_resolution_fails_closed_without_explicit_instrument_calendar_id():
    calendar = make_calendar([])
    registry = SessionCalendarRegistry((calendar,))
    instrument = canonical_future(calendar_id=None)
    assert registry.for_instrument(instrument, version="2024.03.1") is None


def test_calendar_resolution_rejects_unsupported_instrument_calendar_id():
    calendar = make_calendar([])
    registry = SessionCalendarRegistry((calendar,))
    instrument = canonical_future(calendar_id="UNKNOWN_CALENDAR")
    assert registry.for_instrument(instrument, version="2024.03.1") is None


def test_calendar_resolution_rejects_non_future_canonical_instrument():
    calendar = make_calendar([])
    registry = SessionCalendarRegistry((calendar,))
    instrument = CanonicalInstrument(
        canonical_id="12345678-1234-5678-1234-567812345678",
        asset_class="equity",
        instrument_type="stock",
        symbol="ES",
        venue="NASDAQ",
        session_calendar_id="CME_EQUITY_INDEX",
    )
    assert registry.for_instrument(instrument, version="2024.03.1") is None


def test_calendar_resolution_requires_an_explicit_version():
    calendar = make_calendar([])
    registry = SessionCalendarRegistry((calendar,))

    with pytest.raises(ValueError, match="explicit calendar version"):
        registry.for_instrument(
            canonical_future(),
            version="",
        )


def test_calendar_resolution_never_falls_back_to_another_version():
    calendar = make_calendar([])
    registry = SessionCalendarRegistry((calendar,))

    assert registry.for_instrument(
        canonical_future(),
        version="unavailable-release",
    ) is None


@pytest.mark.parametrize("records", [
    None,
    [],
    {date(2024, 3, 11): object()},
    {datetime(2024, 3, 11, tzinfo=timezone.utc): session(
        date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00"
    )},
])
def test_calendar_rejects_malformed_record_containers_and_entries(records):
    with pytest.raises(InvalidSessionCalendar):
        SessionCalendar(
            calendar_id="CME_EQUITY_INDEX", version="2024.03.1", product_family="ES",
            effective_start=date(2024, 3, 1), effective_end=date(2024, 3, 31),
            source_id="official-cme-schedule-release",
            source_url="https://www.cmegroup.com/trading-hours.html",
            published_at_utc=datetime(2024, 2, 1, tzinfo=timezone.utc),
            checksum="sha256:verified-release-digest", records=records,
        )


@pytest.mark.parametrize("trading_date,kind,open_local,close_local", [
    (datetime(2024, 3, 11, tzinfo=timezone.utc), "regular",
     datetime(2024, 3, 10, 17, 0, tzinfo=CHICAGO),
     datetime(2024, 3, 11, 16, 0, tzinfo=CHICAGO)),
    (date(2024, 3, 11), [], None, None),
    (date(2024, 3, 11), "regular", "not-a-datetime",
     datetime(2024, 3, 11, 16, 0, tzinfo=CHICAGO)),
])
def test_session_record_rejects_malformed_field_types(
    trading_date, kind, open_local, close_local
):
    with pytest.raises(InvalidSessionCalendar):
        SessionRecord(trading_date, kind, open_local, close_local)


@pytest.mark.parametrize("field,value", [
    ("calendar_id", []),
    ("version", None),
    ("product_family", 7),
    ("source_id", {}),
    ("source_url", None),
    ("checksum", []),
    ("effective_start", datetime(2024, 3, 1, tzinfo=timezone.utc)),
    ("effective_end", "2024-03-31"),
    ("published_at_utc", "2024-02-01T00:00:00Z"),
])
def test_calendar_rejects_malformed_metadata_field_types(field, value):
    valid = make_calendar([])
    with pytest.raises(InvalidSessionCalendar):
        replace(valid, **{field: value})


@pytest.mark.parametrize("value", [None, "2024-03-11", date(2024, 3, 11)])
def test_datetime_to_epoch_ns_rejects_non_datetime_values(value):
    with pytest.raises(TypeError, match="value must be a datetime"):
        datetime_to_epoch_ns(value)


@pytest.mark.parametrize("trading_date", [
    datetime(2024, 3, 11, tzinfo=timezone.utc), "2024-03-11", None,
])
def test_resolve_trading_date_rejects_non_date_values(trading_date):
    calendar = make_calendar([])
    with pytest.raises(TypeError, match="trading_date must be a date"):
        resolve_trading_date(calendar, trading_date)


@pytest.mark.parametrize("instant", [None, "2024-03-11T12:00:00Z", date(2024, 3, 11)])
def test_lookup_instant_rejects_non_datetime_values(instant):
    calendar = make_calendar([])
    with pytest.raises(TypeError, match="instant must be a datetime"):
        lookup_instant(calendar, instant)


@pytest.mark.parametrize("trading_date", [
    datetime(2024, 3, 11, tzinfo=timezone.utc), "2024-03-11", None,
])
def test_session_bucket_bounds_rejects_non_date_values(trading_date):
    calendar = make_calendar([])
    with pytest.raises(TypeError, match="trading_date must be a date"):
        session_bucket_bounds(calendar, trading_date, "1d")


def test_session_bucket_bounds_rejects_non_string_timeframe_cleanly():
    calendar = make_calendar([])
    with pytest.raises(ValueError, match="Session buckets support only"):
        session_bucket_bounds(calendar, date(2024, 3, 11), [])


@pytest.mark.parametrize("family", [None, 7, [], {}])
def test_product_family_resolver_rejects_non_string_input(family):
    with pytest.raises(TypeError, match="product_family must be a string"):
        calendar_id_for_product_family(family)


def test_calendar_registry_rejects_non_calendar_entries():
    registry = SessionCalendarRegistry()
    with pytest.raises(TypeError, match="calendar must be a SessionCalendar"):
        registry.register(object())
    with pytest.raises(TypeError, match="every calendar must be a SessionCalendar"):
        registry.replace_all((object(),))


@pytest.mark.parametrize("calendar_id,version", [
    (None, None),
    ([], None),
    ("CME_EQUITY_INDEX", 7),
    ("CME_EQUITY_INDEX", ""),
])
def test_calendar_registry_rejects_malformed_lookup_keys(calendar_id, version):
    registry = SessionCalendarRegistry()
    with pytest.raises(TypeError):
        registry.get(calendar_id, version)
