from types import SimpleNamespace

import pytest

from app.databento_definitions import (
    InvalidDatabentoRecord,
    definition_record_to_mapping,
    iter_definition_mappings,
)


def dbn_record(**overrides):
    values = {
        "raw_symbol": "ESZ6",
        "instrument_id": 101,
        "publisher_id": 1,
        "instrument_class": "F",
        "security_update_action": "A",
        "expiration": 1_798_588_800_000_000_000,
        "currency": "USD",
        "min_price_increment": 250_000_000,
        "ts_event": 1_790_000_000_000_000_000,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_maps_dbn_record_attributes_without_changing_numeric_units():
    result = definition_record_to_mapping(dbn_record())

    assert result["raw_symbol"] == "ESZ6"
    assert result["instrument_id"] == 101
    assert result["expiration"] == 1_798_588_800_000_000_000
    assert result["min_price_increment"] == 250_000_000


def test_decodes_null_padded_ascii_symbol():
    result = definition_record_to_mapping(dbn_record(raw_symbol=b"NQZ6\x00"))

    assert result["raw_symbol"] == "NQZ6"


def test_rejects_non_ascii_symbol():
    with pytest.raises(InvalidDatabentoRecord, match="not ASCII"):
        definition_record_to_mapping(dbn_record(raw_symbol=b"GC\xff"))


def test_rejects_record_missing_required_field():
    record = dbn_record()
    del record.ts_event

    with pytest.raises(InvalidDatabentoRecord, match="ts_event"):
        definition_record_to_mapping(record)


def test_preserves_authoritative_contract_metadata_and_lifecycle_action():
    result = definition_record_to_mapping(
        dbn_record(
            exchange=b"XCME\x00",
            unit_of_measure=b"USD\x00",
            unit_of_measure_qty=50_000_000_000,
            settl_currency=b"USD\x00",
            security_update_action=b"M",
            activation=1_789_000_000_000_000_000,
            contract_multiplier=1,
        )
    )

    assert result["exchange"] == "XCME"
    assert result["unit_of_measure"] == "USD"
    assert result["unit_of_measure_qty"] == 50_000_000_000
    assert result["settl_currency"] == "USD"
    assert result["security_update_action"] == "M"
    assert result["activation"] == 1_789_000_000_000_000_000
    assert result["contract_multiplier"] == 1


def test_rejects_non_ascii_optional_character_fields():
    with pytest.raises(InvalidDatabentoRecord, match="exchange is not ASCII"):
        definition_record_to_mapping(dbn_record(exchange=b"X\xff"))


def test_delete_definition_does_not_require_expiration():
    record = dbn_record(security_update_action=b"D")
    del record.expiration

    result = definition_record_to_mapping(record)

    assert result["security_update_action"] == "D"
    assert "expiration" not in result


def test_iter_preserves_record_order():
    records = [
        dbn_record(raw_symbol="ESH7", instrument_id=1),
        dbn_record(raw_symbol="NQH7", instrument_id=2),
        dbn_record(raw_symbol="GCH7", instrument_id=3),
    ]

    mapped = list(iter_definition_mappings(records))

    assert [item["raw_symbol"] for item in mapped] == [
        "ESH7",
        "NQH7",
        "GCH7",
    ]
    assert [item["instrument_id"] for item in mapped] == [1, 2, 3]
