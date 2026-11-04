from datetime import datetime, timezone
from uuid import UUID

import pytest

from app.databento_definition_normalizer import (
    InvalidDatabentoDefinition,
    normalize_databento_definition,
)

CANONICAL_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"


def definition(**overrides):
    values = {
        "raw_symbol": "ESZ6",
        "instrument_id": 101,
        "publisher_id": 1,
        "instrument_class": "F",
        "security_update_action": "A",
        "expiration": 1_798_588_800_000_000_000,
        "currency": "USD",
        "settl_currency": "USD",
        "min_price_increment": 250_000_000,
        "display_factor": 1_000_000_000,
        "unit_of_measure_qty": 50_000_000_000,
        "unit_of_measure": "USD",
        "contract_multiplier": 1_000_000_000,
        "contract_multiplier_unit": "USD",
        "exchange": "XCME",
        "asset": "ES",
        "activation": 1_790_000_000_000_000_000,
        "min_lot_size": 1_000_000_000,
        "min_lot_size_round_lot": 1_000_000_000,
        "ts_event": 1_790_000_000_000_000_000,
    }
    values.update(overrides)
    return values


def test_normalizes_verified_future_identity_and_preserves_contract_terms():
    result = normalize_databento_definition(
        definition(), canonical_id=CANONICAL_ID, dataset="GLBX.MDP3"
    )
    assert result.action == "A"
    assert result.instrument is not None
    assert result.instrument.canonical_id == str(UUID(CANONICAL_ID))
    assert result.instrument.symbol == "ES"
    assert result.instrument.venue == "XCME"
    assert result.instrument.expiration_date == "2027-01-01"
    assert result.instrument.settlement_currency == "USD"
    assert result.metadata["unit_of_measure_qty_raw"] == 50_000_000_000
    assert result.metadata["contract_multiplier_raw"] == 1_000_000_000
    assert result.metadata["unit_of_measure_qty_raw"] != result.metadata["contract_multiplier_raw"]
    assert result.metadata["min_price_increment_raw"] == 250_000_000
    assert result.metadata["min_price_increment_scale"] == 1_000_000_000


def test_missing_settlement_override_uses_currency_as_documented_default():
    result = normalize_databento_definition(
        definition(settl_currency=None), canonical_id=CANONICAL_ID, dataset="GLBX.MDP3"
    )
    assert result.instrument.settlement_currency == "USD"
    assert result.metadata["settlement_currency"] == "USD"


@pytest.mark.parametrize("field", ["asset", "exchange", "currency", "expiration"])
def test_missing_authoritative_identity_fields_are_rejected(field):
    row = definition()
    row.pop(field)
    with pytest.raises(InvalidDatabentoDefinition):
        normalize_databento_definition(row, canonical_id=CANONICAL_ID, dataset="GLBX.MDP3")


def test_does_not_guess_asset_root_from_raw_symbol():
    row = definition()
    row.pop("asset")
    with pytest.raises(InvalidDatabentoDefinition, match="missing_authoritative_asset"):
        normalize_databento_definition(row, canonical_id=CANONICAL_ID, dataset="GLBX.MDP3")


def test_delete_event_does_not_require_contract_identity_fields():
    result = normalize_databento_definition(
        {
            "raw_symbol": "ESZ6", "instrument_id": 101, "publisher_id": 1,
            "security_update_action": "D", "ts_event": 1_790_000_000_000_000_000,
        },
        canonical_id=None, dataset="GLBX.MDP3",
    )
    assert result.action == "D"
    assert result.instrument is None


def test_unknown_class_and_invalid_expiration_are_quarantinable():
    with pytest.raises(InvalidDatabentoDefinition, match="unsupported_instrument_class"):
        normalize_databento_definition(
            definition(instrument_class="O"), canonical_id=CANONICAL_ID, dataset="GLBX.MDP3"
        )
    with pytest.raises(InvalidDatabentoDefinition, match="invalid_expiration"):
        normalize_databento_definition(
            definition(expiration=0), canonical_id=CANONICAL_ID, dataset="GLBX.MDP3"
        )


def test_expiration_date_uses_utc_and_integer_conversion():
    result = normalize_databento_definition(
        definition(expiration=1_798_588_800_123_456_789),
        canonical_id=CANONICAL_ID, dataset="GLBX.MDP3",
    )
    expected = datetime.fromtimestamp(1_798_588_800, tz=timezone.utc).date().isoformat()
    assert result.instrument.expiration_date == expected
