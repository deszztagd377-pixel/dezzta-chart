import pytest

from app.instruments import InstrumentCatalog
from app.symbology import InstrumentResolver, SymbolConflict, SymbolMapping
from helpers import NS


def mapping(symbol="ESZ6", a=0, b=None, dataset="GLBX.MDP3", provider="databento", iid=1):
    return SymbolMapping(provider=provider, dataset=dataset, publisher_id=1,
                         instrument_id=iid, raw_symbol=symbol, valid_from_ns=a, valid_to_ns=b)


def test_resolve_is_scoped_by_provider_dataset_and_window():
    resolver = InstrumentResolver()
    resolver.add(mapping("ESZ6", 0, 100))
    resolver.add(mapping("ESH7", 100, None))
    resolver.add(mapping("AAPL", 0, None, dataset="XNAS.ITCH", provider="other"))
    assert resolver.resolve("databento", "GLBX.MDP3", 1, 1, 50).raw_symbol == "ESZ6"
    assert resolver.resolve("databento", "GLBX.MDP3", 1, 1, 100).raw_symbol == "ESH7"
    assert resolver.resolve("other", "XNAS.ITCH", 1, 1, 5).raw_symbol == "AAPL"
    assert resolver.resolve("databento", "XNAS.ITCH", 1, 1, 5) is None  # no cross-dataset leak
    assert resolver.resolve("databento", "GLBX.MDP3", 2, 1, 5) is None


def test_overlapping_different_symbol_is_a_conflict_and_changes_nothing():
    resolver = InstrumentResolver()
    resolver.add(mapping("ESZ6", 0, 100))
    with pytest.raises(SymbolConflict):
        resolver.add(mapping("NQZ6", 50, 200))
    assert len(resolver) == 1


def test_overlapping_same_symbol_merges():
    resolver = InstrumentResolver()
    resolver.add(mapping("ESZ6", 0, 100))
    resolver.add(mapping("ESZ6", 50, None))
    assert len(resolver) == 1
    assert resolver.resolve("databento", "GLBX.MDP3", 1, 1, 10**12).raw_symbol == "ESZ6"


def test_replace_all_is_atomic_on_conflict():
    resolver = InstrumentResolver()
    resolver.add(mapping("ESZ6"))
    with pytest.raises(SymbolConflict):
        resolver.replace_all([mapping("ESH7", 0, 10), mapping("NQH7", 5, 20)])
    assert resolver.resolve("databento", "GLBX.MDP3", 1, 1, 5).raw_symbol == "ESZ6"


def test_invalid_mapping_values_are_rejected():
    with pytest.raises(ValueError):
        mapping(a=10, b=10)
    with pytest.raises(ValueError):
        mapping(a=-1)


def test_register_from_catalog_uses_definition_time_and_expiry_window():
    catalog = InstrumentCatalog()
    catalog.replace_definitions([{
        "raw_symbol": "ESZ6", "instrument_id": 5, "publisher_id": 1,
        "instrument_class": "F", "expiration": "2026-12-18", "currency": "USD",
        "min_price_increment": 250_000_000, "ts_event": 1_790_000_000 * NS,
    }])
    resolver = InstrumentResolver()
    registered, rejected = resolver.register_catalog_contracts(catalog.list_contracts())
    assert (registered, rejected) == (1, 0)
    assert resolver.resolve("databento", "GLBX.MDP3", 1, 5, 1_790_000_000 * NS).raw_symbol == "ESZ6"
    assert resolver.resolve("databento", "GLBX.MDP3", 1, 5, 1_790_000_000 * NS - 1) is None
    expiry_end = 1_797_638_400 * NS  # 2026-12-19 00:00 UTC
    assert resolver.resolve("databento", "GLBX.MDP3", 1, 5, expiry_end - 1) is not None
    assert resolver.resolve("databento", "GLBX.MDP3", 1, 5, expiry_end) is None


def test_catalog_root_allow_list_is_configurable_beyond_es_nq_gc():
    catalog = InstrumentCatalog(allowed_roots=("CL", "ES"))
    rows = [
        {"raw_symbol": "CLZ6", "instrument_id": 1, "publisher_id": 1, "instrument_class": "F",
         "expiration": "2026-11-20", "ts_event": 10},
        {"raw_symbol": "GCZ6", "instrument_id": 2, "publisher_id": 1, "instrument_class": "F",
         "expiration": "2026-12-29", "ts_event": 10},
    ]
    assert catalog.replace_definitions(rows) == 1  # GC is no longer allowed
    assert [c["raw_symbol"] for c in catalog.list_contracts("CL")] == ["CLZ6"]
    with pytest.raises(ValueError, match="Unsupported product root"):
        catalog.list_contracts("GC")
    assert [p["root"] for p in catalog.snapshot()["supported_products"]] == ["CL", "ES"]