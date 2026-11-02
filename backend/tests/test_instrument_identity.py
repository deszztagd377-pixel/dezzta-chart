from dataclasses import FrozenInstanceError

import pytest

from app.instrument_identity import CanonicalInstrument, InvalidCanonicalInstrument


def make_instrument(**overrides):
    values = {
        "canonical_id": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
        "asset_class": "equity",
        "instrument_type": "stock",
        "symbol": "aapl",
        "venue": "xnas",
        "quote_currency": "usd",
        "tick_size": "0.0100",
    }
    values.update(overrides)
    return CanonicalInstrument(**values)


def test_normalizes_identity_without_changing_canonical_id():
    item = make_instrument()
    assert item.canonical_id == "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
    assert item.symbol == "AAPL"
    assert item.venue == "XNAS"
    assert item.quote_currency == "USD"
    assert item.tick_size == "0.01"


def test_canonical_identity_is_immutable():
    item = make_instrument()
    with pytest.raises(FrozenInstanceError):
        item.symbol = "MSFT"


@pytest.mark.parametrize(
    ("asset_class", "instrument_type", "extra"),
    [
        ("crypto", "spot", {"base_currency": "BTC", "quote_currency": "USD"}),
        ("crypto", "perpetual", {"base_currency": "ETH", "quote_currency": "USDT"}),
        ("future", "future", {"expiration_date": "2026-12-18"}),
        ("fx", "fx_pair", {"base_currency": "EUR", "quote_currency": "USD"}),
        ("index", "index", {}),
        ("etf", "etf", {}),
    ],
)
def test_accepts_supported_asset_instrument_combinations(asset_class, instrument_type, extra):
    item = make_instrument(asset_class=asset_class, instrument_type=instrument_type, **extra)
    assert item.asset_class == asset_class
    assert item.instrument_type == instrument_type


def test_rejects_invalid_uuid_and_incompatible_asset_type():
    with pytest.raises(InvalidCanonicalInstrument, match="UUID"):
        make_instrument(canonical_id="AAPL")
    with pytest.raises(InvalidCanonicalInstrument, match="incompatible"):
        make_instrument(asset_class="equity", instrument_type="spot",
                        base_currency="BTC", quote_currency="USD")


@pytest.mark.parametrize(
    "overrides",
    [
        {"venue": ""},
        {"symbol": ""},
        {"asset_class": "unknown"},
        {"instrument_type": "future", "expiration_date": None},
        {"asset_class": "crypto", "instrument_type": "spot"},
        {"asset_class": "fx", "instrument_type": "fx_pair",
         "base_currency": "USD", "quote_currency": "USD"},
        {"tick_size": "0"},
        {"tick_size": "-0.01"},
        {"tick_size": "NaN"},
        {"expiration_date": "2026-02-30"},
        {"is_active": 1},
    ],
)
def test_rejects_incomplete_or_invalid_metadata(overrides):
    with pytest.raises(InvalidCanonicalInstrument):
        make_instrument(**overrides)


def test_options_require_expiry_strike_right_and_valid_underlying():
    with pytest.raises(InvalidCanonicalInstrument, match="option_right"):
        make_instrument(
            asset_class="option", instrument_type="option",
            expiration_date="2026-12-18", strike_price="100",
            underlying_canonical_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a12",
        )
    option = make_instrument(
        asset_class="option", instrument_type="option",
        expiration_date="2026-12-18", option_right="call", strike_price="100.00",
        underlying_canonical_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a12",
    )
    assert option.strike_price == "100"
    assert option.option_right == "call"


def test_option_cannot_reference_itself_and_non_options_reject_option_fields():
    with pytest.raises(InvalidCanonicalInstrument, match="cannot reference itself"):
        make_instrument(
            asset_class="option", instrument_type="option",
            expiration_date="2026-12-18", option_right="put", strike_price="100",
            underlying_canonical_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
        )
    with pytest.raises(InvalidCanonicalInstrument, match="Option-only"):
        make_instrument(option_right="call")


def test_serialization_keeps_decimal_fields_as_strings():
    item = make_instrument()
    payload = item.to_dict()
    assert payload["tick_size"] == "0.01"
    assert isinstance(payload["tick_size"], str)
