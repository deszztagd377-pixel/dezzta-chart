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
