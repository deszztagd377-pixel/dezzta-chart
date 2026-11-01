from datetime import date

import pytest

from app.instruments import InstrumentCatalog, InvalidInstrumentDefinition, FuturesInstrument


def definition(**overrides):
    values = {
        "raw_symbol": "ESZ6",
        "instrument_id": 123,
        "publisher_id": 1,
        "instrument_class": "F",
        "expiration": date(2026, 12, 18),
        "currency": "USD",
        # Databento definition prices use a signed integer scaled by 1e-9.
        "min_price_increment": 250_000_000,
        "ts_event": 1790000000000000000,
    }
    values.update(overrides)
    return values


@pytest.mark.parametrize(
    ("raw_symbol", "root"),
    [("ESH7", "ES"), ("NQZ6", "NQ"), ("GCG7", "GC")],
)
def test_normalizes_supported_outright_contracts(raw_symbol, root):
    contract = FuturesInstrument.from_provider_definition(
        definition(raw_symbol=raw_symbol)
    )

    assert contract.root == root
    assert contract.raw_symbol == raw_symbol
    assert contract.expiration == "2026-12-18"
    assert contract.min_price_increment == "0.25"


def test_normalizes_provider_expiration_nanoseconds():
    contract = FuturesInstrument.from_provider_definition(
        definition(expiration=1_798_588_800_000_000_000)
    )

    assert contract.expiration == "2027-01-01"


@pytest.mark.parametrize(
    "overrides",
    [
        {"raw_symbol": "MESZ6"},
        {"raw_symbol": "ES-ESZ6"},
        {"instrument_class": "S"},
        {"expiration": None},
        {"instrument_id": "not-an-id"},
        {"min_price_increment": "not-a-number"},
    ],
)
def test_rejects_unsupported_or_incomplete_definitions(overrides):
    with pytest.raises(InvalidInstrumentDefinition):
        FuturesInstrument.from_provider_definition(definition(**overrides))


def test_catalog_filters_invalid_definitions_and_sorts_by_expiry():
    catalog = InstrumentCatalog()
    rejected = catalog.replace_definitions(
        [
            definition(raw_symbol="ESZ6", instrument_id=1),
            definition(raw_symbol="ESH7", instrument_id=2, expiration=date(2027, 3, 19)),
            definition(raw_symbol="NQZ6", instrument_id=3),
            definition(raw_symbol="ES-ESZ6", instrument_id=4),
            definition(raw_symbol="GCG6", instrument_id=5, instrument_class="S"),
        ]
    )

    assert rejected == 2
    contracts = catalog.list_contracts("ES")
    assert [item["raw_symbol"] for item in contracts] == ["ESZ6", "ESH7"]
    assert catalog.snapshot()["contract_count"] == 3


def test_catalog_replacement_does_not_keep_stale_contracts():
    catalog = InstrumentCatalog()
    catalog.replace_definitions([definition()])
    catalog.replace_definitions([])

    assert catalog.list_contracts() == []
    assert catalog.snapshot()["state"] == "definitions_unavailable"


def test_unknown_root_is_rejected():
    catalog = InstrumentCatalog()

    with pytest.raises(ValueError, match="Unsupported product root"):
        catalog.list_contracts("MES")
