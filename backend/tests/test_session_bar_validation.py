from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import ProviderInstrumentMapping, SQLiteInstrumentRegistry
from app.ohlcv import BUCKET_POLICY_UTC_FIXED_V1, OhlcvBar
from app.session_calendar import (
    CHICAGO,
    SessionCalendar,
    SessionCalendarRegistry,
    SessionRecord,
    SessionSegment,
    datetime_to_epoch_ns,
)
from app.session_bar_validation import (
    SessionBarRejected,
    _epoch_ns_to_utc,
    validate_intraday_bar_session,
    validate_provider_bar_session,
)


def future(calendar_id="CME_EQUITY_INDEX", *, active=True):
    return CanonicalInstrument(
        canonical_id="12345678-1234-5678-1234-567812345678",
        asset_class="future",
        instrument_type="future",
        symbol="ES",
        venue="CME",
        settlement_currency="USD",
        expiration_date="2024-12-20",
        session_calendar_id=calendar_id,
        is_active=active,
    )


def record(day, opened, closed, kind="regular", segments=()):
    return SessionRecord(
        trading_date=day,
        kind=kind,
        open_local=datetime.fromisoformat(opened).replace(tzinfo=CHICAGO)
        if opened else None,
        close_local=datetime.fromisoformat(closed).replace(tzinfo=CHICAGO)
        if closed else None,
        segments=segments,
    )


def calendar(records, *, start=date(2024, 3, 11), end=date(2024, 3, 12)):
    return SessionCalendar(
        calendar_id="CME_EQUITY_INDEX",
        version="2024.03.1",
        product_family="ES",
        effective_start=start,
        effective_end=end,
        source_id="test-fixture-only",
        source_url="https://www.cmegroup.com/trading-hours.html",
        published_at_utc=datetime(2024, 2, 1, tzinfo=timezone.utc),
        checksum="sha256:test-fixture",
        records={item.trading_date: item for item in records},
    )


def bar(start_ns, *, timeframe="1m", policy=BUCKET_POLICY_UTC_FIXED_V1):
    return OhlcvBar(
        dataset="GLBX.MDP3",
        publisher_id=1,
        instrument_id=10,
        raw_symbol="ESZ6",
        timeframe=timeframe,
        ts_start_ns=start_ns,
        open=Decimal("5000"),
        high=Decimal("5001"),
        low=Decimal("4999"),
        close=Decimal("5000.5"),
        volume=Decimal("10"),
        ts_event_ns=start_ns,
        ts_received_ns=start_ns,
        sequence=1,
        bucket_policy=policy,
    )


def validator_for(records, *, start=date(2024, 3, 11), end=date(2024, 3, 12)):
    release = calendar(records, start=start, end=end)
    registry = SessionCalendarRegistry((release,))
    return lambda item, instrument=None, version="2024.03.1": (
        validate_intraday_bar_session(
            item, instrument or future(), registry, calendar_version=version
        )
    )


def test_accepts_complete_regular_session_bar_and_returns_release_identity():
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    result = validator_for([monday])(bar(start))
    assert result.calendar_id == "CME_EQUITY_INDEX"
    assert result.calendar_version == "2024.03.1"
    assert result.trading_date == "2024-03-11"
    assert result.interval_end_ns == start + 60_000_000_000


def test_accepts_bar_inside_explicit_early_close_session():
    early = record(
        date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T12:00:00",
        kind="early_close",
    )
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 16, 59, tzinfo=timezone.utc))
    result = validator_for([early])(bar(start))
    assert result.session_state == "special-session"


def test_rejects_bar_interval_that_crosses_early_session_close():
    early = record(
        date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T12:30:00",
        kind="early_close",
    )
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 17, 0, tzinfo=timezone.utc))
    with pytest.raises(SessionBarRejected) as error:
        validator_for([early])(bar(start, timeframe="1h"))
    assert error.value.reason == "bar_crosses_session_close"


def test_rejects_bar_crossing_explicit_intraday_segment_break():
    monday = record(
        date(2024, 3, 11),
        "2024-03-10T17:00:00",
        "2024-03-11T16:00:00",
        segments=(
            SessionSegment(
                datetime.fromisoformat("2024-03-10T17:00:00").replace(tzinfo=CHICAGO),
                datetime.fromisoformat("2024-03-11T10:32:00").replace(tzinfo=CHICAGO),
            ),
            SessionSegment(
                datetime.fromisoformat("2024-03-11T11:00:00").replace(tzinfo=CHICAGO),
                datetime.fromisoformat("2024-03-11T16:00:00").replace(tzinfo=CHICAGO),
            ),
        ),
    )
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 30, tzinfo=timezone.utc))
    with pytest.raises(SessionBarRejected) as error:
        validator_for([monday])(bar(start, timeframe="5m"))
    assert error.value.reason == "bar_crosses_session_segment"


def test_rejects_maintenance_interval():
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    tuesday = record(date(2024, 3, 12), "2024-03-11T17:00:00", "2024-03-12T16:00:00")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 21, 30, tzinfo=timezone.utc))
    with pytest.raises(SessionBarRejected) as error:
        validator_for([monday, tuesday])(bar(start))
    assert error.value.reason == "outside_trading_session"


def test_rejects_explicitly_closed_date():
    closed = record(date(2024, 3, 11), None, None, kind="closed")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    with pytest.raises(SessionBarRejected) as error:
        validator_for([closed])(bar(start))
    assert error.value.reason == "outside_trading_session"


def test_missing_date_coverage_is_unknown_and_fails_closed():
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    with pytest.raises(SessionBarRejected) as error:
        validator_for([])(bar(start))
    assert error.value.reason == "unknown_calendar_coverage"


def test_rejects_calendar_id_not_assigned_to_canonical_instrument():
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    with pytest.raises(SessionBarRejected) as error:
        validator_for([monday])(bar(start), instrument=future("COMEX_GOLD"))
    assert error.value.reason == "calendar_unavailable"


def test_rejects_missing_or_unavailable_explicit_release_version():
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    validate = validator_for([monday])
    with pytest.raises(SessionBarRejected) as error:
        validate(bar(start), version="")
    assert error.value.reason == "calendar_version_required"
    with pytest.raises(SessionBarRejected) as error:
        validate(bar(start), version="unavailable")
    assert error.value.reason == "calendar_unavailable"


def test_rejects_inactive_or_non_future_instrument():
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    validate = validator_for([monday])
    with pytest.raises(SessionBarRejected) as error:
        validate(bar(start), instrument=future(active=False))
    assert error.value.reason == "inactive_instrument"
    stock = CanonicalInstrument(
        canonical_id="12345678-1234-5678-1234-567812345678",
        asset_class="equity",
        instrument_type="stock",
        symbol="ES",
        venue="NASDAQ",
    )
    with pytest.raises(SessionBarRejected) as error:
        validate(bar(start), instrument=stock)
    assert error.value.reason == "unsupported_instrument"


def test_rejects_non_utc_intraday_policy_and_non_intraday_timeframe():
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    validate = validator_for([monday])
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    with pytest.raises(SessionBarRejected) as error:
        validate(bar(start, policy="UTC_LEGACY"))
    assert error.value.reason == "unsupported_bucket_policy"
    daily_start = datetime_to_epoch_ns(datetime(2024, 3, 11, 0, 0, tzinfo=timezone.utc))
    with pytest.raises(SessionBarRejected) as error:
        validate(bar(daily_start, timeframe="1d", policy=BUCKET_POLICY_UTC_FIXED_V1))
    assert error.value.reason == "unsupported_timeframe"


def test_rejects_sub_microsecond_timestamp_precision_without_rounding():
    with pytest.raises(SessionBarRejected) as error:
        _epoch_ns_to_utc(1)
    assert error.value.reason == "unsupported_timestamp_precision"



def durable_registry(tmp_path, *, raw_symbol="ESZ6", series_type="contract",
                     valid_from_ns=1, valid_to_ns=None):
    registry = SQLiteInstrumentRegistry(str(tmp_path / "instrument-registry.sqlite3"))
    instrument = future()
    registry.register_instrument_with_mapping(
        instrument,
        ProviderInstrumentMapping(
            provider="databento",
            dataset="GLBX.MDP3",
            publisher_id=1,
            instrument_id=10,
            raw_symbol=raw_symbol,
            valid_from_ns=valid_from_ns,
            valid_to_ns=valid_to_ns,
            canonical_id=instrument.canonical_id,
            series_type=series_type,
        ),
    )
    return registry


def test_provider_validation_uses_point_in_time_durable_mapping(tmp_path):
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    registry = durable_registry(tmp_path, valid_from_ns=start - 1)
    result = validate_provider_bar_session(
        bar(start),
        registry,
        SessionCalendarRegistry((calendar([monday]),)),
        calendar_version="2024.03.1",
    )
    assert result.calendar_id == "CME_EQUITY_INDEX"
    assert result.trading_date == "2024-03-11"


def test_provider_validation_rejects_mapping_outside_its_validity_window(tmp_path):
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    registry = durable_registry(tmp_path, valid_from_ns=1, valid_to_ns=start)
    with pytest.raises(SessionBarRejected) as error:
        validate_provider_bar_session(
            bar(start), registry, SessionCalendarRegistry((calendar([monday]),)),
            calendar_version="2024.03.1",
        )
    assert error.value.reason == "provider_mapping_unavailable"


def test_provider_validation_rejects_ephemeral_symbol_mapping_mismatch(tmp_path):
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    registry = durable_registry(tmp_path, raw_symbol="ESM6", valid_from_ns=1)
    with pytest.raises(SessionBarRejected) as error:
        validate_provider_bar_session(
            bar(start), registry, SessionCalendarRegistry((calendar([monday]),)),
            calendar_version="2024.03.1",
        )
    assert error.value.reason == "provider_mapping_symbol_mismatch"


def test_provider_validation_never_uses_matching_symbol_without_provider_id_mapping(tmp_path):
    monday = record(date(2024, 3, 11), "2024-03-10T17:00:00", "2024-03-11T16:00:00")
    start = datetime_to_epoch_ns(datetime(2024, 3, 11, 15, 0, tzinfo=timezone.utc))
    registry = SQLiteInstrumentRegistry(str(tmp_path / "empty-registry.sqlite3"))
    registry.register_instrument(future())
    with pytest.raises(SessionBarRejected) as error:
        validate_provider_bar_session(
            bar(start), registry, SessionCalendarRegistry((calendar([monday]),)),
            calendar_version="2024.03.1",
        )
    assert error.value.reason == "provider_mapping_unavailable"
