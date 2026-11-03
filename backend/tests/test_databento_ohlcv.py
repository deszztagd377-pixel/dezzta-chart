from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.databento_ohlcv import (
    UNDEF_PRICE, RecordRejected, fixed_point_to_decimal, record_to_bar,
)
from helpers import NS, T0, make_resolver, px, rec


def convert(record, schema="ohlcv-1s", resolver=None, recv=T0 + 9 * NS, seq=7):
    return record_to_bar(
        record, resolver=resolver or make_resolver(), provider="databento",
        dataset="GLBX.MDP3", schema=schema, ts_received_ns=recv, sequence=seq,
    )


def test_fixed_point_conversion_is_exact_without_floats():
    assert fixed_point_to_decimal(px("4500.25")) == Decimal("4500.25")
    assert fixed_point_to_decimal(1) == Decimal("0.000000001")
    assert fixed_point_to_decimal(-250_000_000) == Decimal("-0.25")
    assert fixed_point_to_decimal(0) == Decimal("0")
    # A value a binary float cannot hold exactly.
    assert fixed_point_to_decimal(123_456_789_012_345_678) == Decimal("123456789.012345678")


def test_record_normalizes_prices_volume_and_timestamps():
    bar = convert(rec(3, o="4500.25", h="4501", l="4499.75", c="4500.5", v=12))
    assert (bar.open, bar.high, bar.low, bar.close) == (
        Decimal("4500.25"), Decimal("4501"), Decimal("4499.75"), Decimal("4500.5"))
    assert bar.volume == Decimal(12)
    assert bar.ts_start_ns == bar.ts_event_ns == T0 + 3 * NS
    assert bar.ts_received_ns == T0 + 9 * NS  # receive time kept separate
    assert bar.timeframe == "1s" and bar.raw_symbol == "ESZ6"
    assert bar.sequence == 7 and bar.sequence_origin == "local"
    assert bar.origin == "provider" and bar.series_type == "contract"


def test_gateway_send_timestamp_is_preserved_without_claiming_latency():
    gateway_ns = T0 + 8 * NS
    bar = convert(rec(3, ts_out=gateway_ns))
    assert bar.ts_provider_out_ns == gateway_ns
    assert bar.ts_received_ns == T0 + 9 * NS


def test_missing_gateway_send_timestamp_remains_unknown():
    bar = convert(rec(3))
    assert bar.ts_provider_out_ns is None


def test_malformed_gateway_send_timestamp_is_rejected():
    with pytest.raises(RecordRejected) as info:
        convert(rec(3, ts_out=1.25))
    assert info.value.reason == "malformed"


def test_volume_beyond_float_precision_is_preserved():
    big = 2**63 + 1
    assert convert(rec(0, v=big)).volume == Decimal(big)


class _NumpyLikeInt:
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value


def test_integer_like_objects_are_accepted_but_floats_are_not():
    assert convert(rec(0, v=_NumpyLikeInt(5))).volume == Decimal(5)
    with pytest.raises(RecordRejected) as info:
        convert(rec(0, v=5.0))
    assert info.value.reason == "malformed"


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"open": UNDEF_PRICE}, "undefined_price"),
        ({"volume": -1}, "malformed"),
        ({"volume": True}, "malformed"),
        ({"high": px("98")}, "invalid_bar"),
        ({"ts_event": T0 + 5 * NS + 1}, "invalid_bar"),  # not aligned to 1s
        ({"instrument_id": 999}, "unknown_instrument"),
        ({"instrument_id": "abc"}, "malformed"),
    ],
)
def test_invalid_records_are_rejected_with_a_reason(overrides, reason):
    with pytest.raises(RecordRejected) as info:
        convert(rec(0, **overrides))
    assert info.value.reason == reason


def test_non_ohlcv_records_and_unknown_schema_are_rejected_safely():
    with pytest.raises(RecordRejected) as info:
        convert(SimpleNamespace(stype_in_symbol="ESZ6"))
    assert info.value.reason == "unsupported_record"
    with pytest.raises(RecordRejected) as info:
        convert(None)
    assert info.value.reason == "unsupported_record"
    with pytest.raises(RecordRejected) as info:
        convert(rec(0), schema="mbo")
    assert info.value.reason == "unsupported_schema"


def test_instrument_id_reuse_resolves_by_validity_window():
    from app.symbology import SymbolMapping
    resolver = make_resolver(symbol="ESZ6", valid_from=0, valid_to=T0 + 10 * NS)
    resolver.add(SymbolMapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
        raw_symbol="ESH7", valid_from_ns=T0 + 10 * NS))
    assert convert(rec(2), resolver=resolver).raw_symbol == "ESZ6"
    assert convert(rec(12), resolver=resolver).raw_symbol == "ESH7"


def test_other_ohlcv_schemas_map_to_their_timeframes():
    assert convert(rec(0), schema="ohlcv-1m").timeframe == "1m"
    assert convert(rec(0), schema="ohlcv-1d").timeframe == "1d"