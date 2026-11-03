from concurrent.futures import ThreadPoolExecutor
import sqlite3

import pytest

from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import (
    InstrumentMappingConflict,
    InstrumentRegistryConflict,
    ProviderInstrumentMapping,
    SQLiteInstrumentRegistry,
    UnknownCanonicalInstrument,
    UnsupportedRegistrySchema,
)

INSTRUMENT_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
SECOND_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a12"


def stock(**overrides):
    values = {
        "canonical_id": INSTRUMENT_ID,
        "asset_class": "equity",
        "instrument_type": "stock",
        "symbol": "AAPL",
        "venue": "XNAS",
        "quote_currency": "USD",
        "tick_size": "0.01",
    }
    values.update(overrides)
    return CanonicalInstrument(**values)


def mapping(**overrides):
    values = {
        "provider": "Databento",
        "dataset": "EQUS.MINI",
        "publisher_id": 1,
        "instrument_id": 9001,
        "raw_symbol": "AAPL",
        "valid_from_ns": 100,
        "valid_to_ns": 200,
        "canonical_id": INSTRUMENT_ID,
        "series_type": "instrument",
    }
    values.update(overrides)
    return ProviderInstrumentMapping(**values)


@pytest.fixture
def registry(tmp_path):
    return SQLiteInstrumentRegistry(str(tmp_path / "data" / "registry.sqlite3"))


def test_file_backed_registry_survives_reopen(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    first = SQLiteInstrumentRegistry(path)
    assert first.register_instrument(stock()) is True
    second = SQLiteInstrumentRegistry(path)
    assert second.get_instrument(INSTRUMENT_ID) == stock()


def test_registration_is_idempotent_but_never_overwrites_identity(registry):
    assert registry.register_instrument(stock()) is True
    assert registry.register_instrument(stock()) is False
    with pytest.raises(InstrumentRegistryConflict):
        registry.register_instrument(stock(symbol="MSFT"))


def test_instrument_metadata_is_database_immutable(registry):
    registry.register_instrument(stock())
    connection = sqlite3.connect(registry.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="canonical_instrument_is_immutable"):
            connection.execute(
                "UPDATE canonical_instruments SET symbol = 'MSFT' WHERE canonical_id = ?",
                (INSTRUMENT_ID,),
            )
    finally:
        connection.close()


def test_list_filters_and_pagination_are_bounded(registry):
    registry.register_instrument(stock())
    registry.register_instrument(stock(
        canonical_id=SECOND_ID, symbol="BTCUSD", asset_class="crypto", venue="XCRY",
        instrument_type="spot", base_currency="BTC", quote_currency="USD",
    ))
    assert [item.symbol for item in registry.list_instruments(asset_class="equity")] == ["AAPL"]
    assert [item.symbol for item in registry.list_instruments(venue="XNAS")] == ["AAPL"]
    assert registry.list_instruments(limit=1, offset=1)[0].symbol == "AAPL"
    with pytest.raises(ValueError):
        registry.list_instruments(limit=1001)
    with pytest.raises(ValueError):
        registry.list_instruments(offset=-1)


def test_provider_mapping_requires_existing_canonical_instrument(registry):
    with pytest.raises(UnknownCanonicalInstrument):
        registry.add_provider_mapping(mapping())


def test_provider_mapping_resolves_exact_point_in_time_and_survives_reopen(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(stock())
    assert registry.add_provider_mapping(mapping()) is True
    assert registry.add_provider_mapping(mapping()) is False
    reopened = SQLiteInstrumentRegistry(path)
    assert reopened.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=100,
    ).canonical_id == INSTRUMENT_ID
    assert reopened.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=199,
    ) is not None
    assert reopened.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=200,
    ) is None


@pytest.mark.parametrize(
    "candidate",
    [
        mapping(valid_from_ns=150, valid_to_ns=250),
        mapping(valid_from_ns=50, valid_to_ns=150),
        mapping(valid_from_ns=100, valid_to_ns=300),
        mapping(valid_from_ns=150, valid_to_ns=None),
    ],
)
def test_overlapping_provider_validity_windows_are_rejected(registry, candidate):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping())
    with pytest.raises(InstrumentMappingConflict):
        registry.add_provider_mapping(candidate)


def test_adjacent_provider_validity_windows_are_allowed(registry):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping(valid_to_ns=200))
    assert registry.add_provider_mapping(mapping(
        valid_from_ns=200, valid_to_ns=300, raw_symbol="AAPL2"
    )) is True


def test_same_provider_key_can_be_reused_after_closed_validity_window(registry):
    registry.register_instrument(stock())
    registry.register_instrument(stock(canonical_id=SECOND_ID, symbol="AAPL2"))
    registry.add_provider_mapping(mapping(valid_to_ns=200))
    registry.add_provider_mapping(mapping(
        valid_from_ns=200, valid_to_ns=None,
        canonical_id=SECOND_ID, raw_symbol="AAPL2",
    ))
    assert registry.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=199,
    ).canonical_id == INSTRUMENT_ID
    assert registry.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=200,
    ).canonical_id == SECOND_ID


def test_provider_and_dataset_scope_are_isolated(registry):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping())
    assert registry.resolve_provider_mapping(
        provider="other-provider", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=150,
    ) is None
    assert registry.resolve_provider_mapping(
        provider="databento", dataset="OTHER.DATASET", publisher_id=1,
        instrument_id=9001, timestamp_ns=150,
    ) is None


def test_sql_trigger_rejects_overlap_even_when_bypassing_repository(registry):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping())
    connection = sqlite3.connect(registry.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="overlapping_provider_mapping"):
            connection.execute(
                """
                INSERT INTO provider_instrument_mappings
                (provider,dataset,publisher_id,instrument_id,raw_symbol,valid_from_ns,
                 valid_to_ns,canonical_id,series_type)
                VALUES ('databento','EQUS.MINI',1,9001,'OTHER',150,250,?,'instrument')
                """,
                (INSTRUMENT_ID,),
            )
    finally:
        connection.close()


def test_concurrent_overlapping_writes_cannot_both_succeed(registry):
    registry.register_instrument(stock())
    candidates = [
        mapping(valid_from_ns=100, valid_to_ns=200),
        mapping(valid_from_ns=150, valid_to_ns=250),
    ]

    def insert(candidate):
        try:
            return registry.add_provider_mapping(candidate)
        except InstrumentMappingConflict:
            return False

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(insert, candidates))
    assert sum(results) == 1
    assert len(registry.list_provider_mappings(INSTRUMENT_ID)) == 1


def test_rejects_memory_database_and_newer_schema(tmp_path):
    with pytest.raises(ValueError, match="file-backed"):
        SQLiteInstrumentRegistry(":memory:")
    path = str(tmp_path / "future.sqlite3")
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA user_version = 999")
    connection.close()
    with pytest.raises(UnsupportedRegistrySchema):
        SQLiteInstrumentRegistry(path)


@pytest.mark.parametrize(
    "overrides",
    [
        {"provider": ""},
        {"publisher_id": 0},
        {"instrument_id": 0},
        {"instrument_id": True},
        {"valid_from_ns": -1},
        {"valid_from_ns": 9_223_372_036_854_775_807},
        {"valid_to_ns": 100},
        {"canonical_id": "not-a-uuid"},
    ],
)
def test_invalid_provider_mapping_metadata_is_rejected(registry, overrides):
    registry.register_instrument(stock())
    with pytest.raises(ValueError):
        registry.add_provider_mapping(mapping(**overrides))


def test_mapping_resolution_rejects_timestamp_outside_sqlite_integer_range(registry):
    registry.register_instrument(stock())
    with pytest.raises(ValueError, match="SQLite-range"):
        registry.resolve_provider_mapping(
            provider="databento", dataset="EQUS.MINI", publisher_id=1,
            instrument_id=9001, timestamp_ns=9_223_372_036_854_775_808,
        )


def test_atomic_registration_creates_identity_and_mapping_and_is_idempotent(registry):
    instrument = stock()
    provider_mapping = mapping()
    assert registry.register_instrument_with_mapping(instrument, provider_mapping) == (True, True)
    assert registry.register_instrument_with_mapping(instrument, provider_mapping) == (False, False)
    assert registry.get_instrument(INSTRUMENT_ID) == instrument
    resolved = registry.list_provider_mappings(INSTRUMENT_ID)
    assert len(resolved) == 1
    assert resolved[0].provider == "databento"
    assert resolved[0].dataset == "EQUS.MINI"
    assert resolved[0].canonical_id == INSTRUMENT_ID


def test_atomic_registration_adds_mapping_to_existing_identity(registry):
    instrument = stock()
    registry.register_instrument(instrument)
    assert registry.register_instrument_with_mapping(instrument, mapping()) == (False, True)


def test_atomic_registration_rolls_back_new_identity_on_mapping_conflict(registry):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping())

    second = stock(canonical_id=SECOND_ID, symbol="AAPL2")
    conflicting = mapping(
        valid_from_ns=150, valid_to_ns=250,
        canonical_id=SECOND_ID, raw_symbol="AAPL2",
    )
    with pytest.raises(InstrumentMappingConflict):
        registry.register_instrument_with_mapping(second, conflicting)

    assert registry.get_instrument(SECOND_ID) is None
    resolved = registry.list_provider_mappings(INSTRUMENT_ID)
    assert len(resolved) == 1
    assert resolved[0].canonical_id == INSTRUMENT_ID
    assert resolved[0].valid_from_ns == 100
    assert resolved[0].valid_to_ns == 200


def test_atomic_registration_rejects_mismatched_canonical_ids(registry):
    with pytest.raises(ValueError, match="must match"):
        registry.register_instrument_with_mapping(stock(), mapping(canonical_id=SECOND_ID))
    assert registry.get_instrument(INSTRUMENT_ID) is None
