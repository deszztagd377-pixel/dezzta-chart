from app.databento_definition_sync import DatabentoDefinitionSynchronizer
from app.instrument_registry import SQLiteInstrumentRegistry
from app.instruments import InstrumentCatalog
from app.symbology import InstrumentResolver


def definition(ts_event, action="A", **overrides):
    row = {
        "raw_symbol": "ESZ6",
        "instrument_id": 901,
        "publisher_id": 1,
        "instrument_class": "F",
        "security_update_action": action,
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
        "activation": ts_event,
        "min_lot_size": 1_000_000_000,
        "min_lot_size_round_lot": 1_000_000_000,
        "ts_event": ts_event,
    }
    row.update(overrides)
    return row


def setup_sync(tmp_path):
    path = str(tmp_path / "definitions.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    catalog = InstrumentCatalog()
    resolver = InstrumentResolver()
    sync = DatabentoDefinitionSynchronizer(
        path, registry, catalog, resolver
    )
    return path, registry, catalog, resolver, sync


def test_add_modify_delete_are_durable_and_point_in_time(tmp_path):
    path, registry, catalog, resolver, sync = setup_sync(tmp_path)
    t0 = 1_790_000_000_000_000_000
    t1, t2 = t0 + 10, t0 + 20

    assert sync.ingest_rows([definition(t0)]) == (1, 0)
    first = registry.resolve_provider_mapping(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=901, timestamp_ns=t0,
    )
    assert first is not None
    canonical_id = first.canonical_id

    assert sync.ingest_rows([
        definition(t1, action="M", min_price_increment=125_000_000)
    ]) == (1, 0)
    before_modify = registry.resolve_provider_mapping(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=901, timestamp_ns=t1 - 1,
    )
    after_modify = registry.resolve_provider_mapping(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=901, timestamp_ns=t1,
    )
    assert before_modify.valid_to_ns == t1
    assert after_modify.canonical_id == canonical_id

    assert sync.ingest_rows([
        definition(t2, action="D")
    ]) == (1, 0)
    assert registry.resolve_provider_mapping(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=901, timestamp_ns=t2,
    ) is None
    assert registry.resolve_provider_mapping(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=901, timestamp_ns=t2 - 1,
    ) is not None

    # Exact source replay is idempotent and does not create another transition.
    assert sync.ingest_rows([
        definition(t0),
        definition(t1, action="M", min_price_increment=125_000_000),
        definition(t2, action="D"),
    ]) == (0, 0)
    assert len(registry.list_provider_mappings(canonical_id)) == 2


def test_pending_journal_replay_recovers_after_registry_transition(tmp_path):
    path, registry, catalog, resolver, sync = setup_sync(tmp_path)
    t0 = 1_790_000_000_000_000_000
    # Append without applying by writing directly to the journal.
    record, created = sync._journal.append_event(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=901, source_event_ts_ns=t0,
        source_order=0, action="A", raw_symbol="ESZ6",
        payload=definition(t0),
    )
    assert created is True
    assert sync.replay_pending() == (1, 0)
    assert sync._journal.get_event(record.event_id).processing_status == "applied"

    # Rebuild in-memory state from the persistent mapping after a process restart.
    restarted_resolver = InstrumentResolver()
    restarted = DatabentoDefinitionSynchronizer(
        path, registry, catalog, restarted_resolver
    )
    assert restarted.restore_resolver() == 1
    assert restarted_resolver.resolve(
        "databento", "GLBX.MDP3", 1, 901, t0
    ).raw_symbol == "ESZ6"


def test_invalid_definition_is_quarantined_without_registry_mutation(tmp_path):
    path, registry, catalog, resolver, sync = setup_sync(tmp_path)
    t0 = 1_790_000_000_000_000_000
    invalid = definition(t0)
    invalid.pop("asset")
    assert sync.ingest_rows([invalid]) == (0, 1)
    assert registry.list_instruments(active_only=False) == []
    pending = sync._journal.list_pending()
    assert pending == []
    connection = sync._journal._connect()
    try:
        row = connection.execute(
            "SELECT processing_status, error_code FROM provider_definition_events"
        ).fetchone()
        assert row["processing_status"] == "quarantined"
        assert row["error_code"] == "missing_authoritative_asset"
    finally:
        connection.close()


def test_equal_timestamp_same_instrument_second_transition_is_quarantined(tmp_path):
    path, registry, catalog, resolver, sync = setup_sync(tmp_path)
    t0 = 1_790_000_000_000_000_000
    # Both records are retained in source order; the second cannot create a
    # zero-length validity interval and must fail closed rather than reorder.
    rows = [
        definition(t0, action="A"),
        definition(t0, action="M", min_price_increment=125_000_000),
    ]
    assert sync.ingest_rows(rows) == (1, 1)
    assert len(registry.list_provider_mappings(
        registry.list_instruments(active_only=False)[0].canonical_id
    )) == 1


def test_replay_drains_more_than_one_pending_page(tmp_path):
    path, registry, catalog, resolver, sync = setup_sync(tmp_path)
    t0 = 1_790_000_000_000_000_000
    rows = [
        definition(t0),
        definition(
            t0 + 1, instrument_id=902, raw_symbol="NQZ6", asset="NQ"
        ),
    ]
    for index, row in enumerate(rows):
        sync._journal.append_event(
            provider="databento", dataset="GLBX.MDP3",
            publisher_id=1, instrument_id=row["instrument_id"],
            source_event_ts_ns=row["ts_event"], source_order=0,
            action="A", raw_symbol=row["raw_symbol"], payload=row,
        )
    assert sync.replay_pending(limit=1) == (2, 0)
    assert sync._journal.list_pending() == []
    assert len(registry.list_instruments(active_only=False)) == 2
