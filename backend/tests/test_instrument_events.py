import sqlite3

import pytest

from app.instrument_events import (
    ProviderDefinitionEventConflict,
    SQLiteProviderDefinitionEventRepository,
)
from app.instrument_identity import CanonicalInstrument
from app.instrument_metadata import SQLiteInstrumentMetadataRepository
from app.instrument_registry import (
    ProviderInstrumentMapping,
    SQLiteInstrumentRegistry,
)

CANONICAL_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"


def instrument():
    return CanonicalInstrument(
        canonical_id=CANONICAL_ID,
        asset_class="equity",
        instrument_type="stock",
        symbol="AAPL",
        venue="XNAS",
        quote_currency="USD",
        tick_size="0.01",
    )


def provider_mapping(*, valid_from_ns=1_000, raw_symbol="AAPL"):
    return ProviderInstrumentMapping(
        provider="Databento",
        dataset="GLBX.MDP3",
        publisher_id=1,
        instrument_id=9001,
        raw_symbol=raw_symbol,
        valid_from_ns=valid_from_ns,
        valid_to_ns=None,
        canonical_id=CANONICAL_ID,
        series_type="instrument",
    )


@pytest.fixture
def event_repository(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(instrument())
    return registry, SQLiteProviderDefinitionEventRepository(path)


def test_provider_event_commits_mapping_and_metadata_together(event_repository):
    registry, events = event_repository
    mapping, metadata, created = events.apply_event(
        provider_mapping(),
        source_event_ts_ns=950,
        metadata={"tick_size": "0.25", "multiplier": "50"},
    )

    assert created is True
    assert mapping.valid_from_ns == 1_000
    assert mapping.valid_to_ns is None
    assert metadata.source_kind == "provider"
    assert metadata.source_name == "databento"
    assert metadata.source_dataset == "GLBX.MDP3"
    assert metadata.source_event_ts_ns == 950
    assert metadata.effective_from_ns == 1_000
    assert metadata.metadata == {"multiplier": "50", "tick_size": "0.25"}

    resolved_mapping = registry.resolve_provider_mapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1,
        instrument_id=9001, timestamp_ns=1_000,
    )
    assert resolved_mapping == mapping


def test_provider_event_transition_closes_both_timelines_and_replay_is_idempotent(
    event_repository,
):
    registry, events = event_repository
    _, first_metadata, first_created = events.apply_event(
        provider_mapping(valid_from_ns=1_000),
        source_event_ts_ns=1_000,
        metadata={"tick_size": "0.25"},
    )
    second_mapping, second_metadata, second_created = events.apply_event(
        provider_mapping(valid_from_ns=2_000, raw_symbol="AAPL.N"),
        source_event_ts_ns=2_000,
        metadata={"tick_size": "0.5"},
    )

    assert first_created is True
    assert second_created is True
    mappings = registry.list_provider_mappings(CANONICAL_ID)
    assert len(mappings) == 2
    assert mappings[0].valid_from_ns == 1_000
    assert mappings[0].valid_to_ns == 2_000
    assert mappings[1] == second_mapping
    assert first_metadata.effective_to_ns is None  # Returned immutable insertion snapshot.
    assert second_metadata.effective_to_ns is None

    metadata_repository = SQLiteInstrumentMetadataRepository(registry.database_path)
    revisions = metadata_repository.list_revisions(
        CANONICAL_ID, source_kind="provider", source_name="databento"
    )
    assert len(revisions) == 2
    assert revisions[0].effective_to_ns == 2_000
    assert revisions[1] == second_metadata

    replay_mapping, replay_metadata, replay_created = events.apply_event(
        provider_mapping(valid_from_ns=1_000),
        source_event_ts_ns=1_000,
        metadata={"tick_size": "0.25"},
    )
    assert replay_created is False
    assert replay_mapping.valid_to_ns == 2_000
    assert replay_metadata.effective_to_ns == 2_000
    assert len(registry.list_provider_mappings(CANONICAL_ID)) == 2
    assert len(metadata_repository.list_revisions(CANONICAL_ID, source_kind="provider")) == 2


def test_stale_and_partial_provider_event_replays_are_rejected_without_mutation(
    event_repository,
):
    registry, events = event_repository
    events.apply_event(
        provider_mapping(valid_from_ns=2_000),
        source_event_ts_ns=2_000,
        metadata={"tick_size": "0.5"},
    )
    with pytest.raises(ProviderDefinitionEventConflict, match="Out-of-order"):
        events.apply_event(
            provider_mapping(valid_from_ns=1_500),
            source_event_ts_ns=1_500,
            metadata={"tick_size": "0.25"},
        )

    with pytest.raises(ProviderDefinitionEventConflict, match="Partial event replay"):
        events.apply_event(
            provider_mapping(valid_from_ns=2_000),
            source_event_ts_ns=2_000,
            metadata={"tick_size": "0.75"},
        )

    mappings = registry.list_provider_mappings(CANONICAL_ID)
    assert len(mappings) == 1
    assert mappings[0].valid_from_ns == 2_000
    assert mappings[0].valid_to_ns is None


def test_metadata_insert_failure_rolls_back_mapping_and_metadata_closures(
    event_repository,
):
    registry, events = event_repository
    events.apply_event(
        provider_mapping(valid_from_ns=1_000),
        source_event_ts_ns=1_000,
        metadata={"tick_size": "0.25"},
    )
    connection = sqlite3.connect(registry.database_path)
    try:
        connection.execute(
            """
            CREATE TRIGGER reject_provider_event_metadata
            BEFORE INSERT ON instrument_metadata_revisions
            WHEN NEW.metadata_json = '{"tick_size":"0.5"}'
            BEGIN
                SELECT RAISE(ABORT, 'forced_provider_event_failure');
            END
            """
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.IntegrityError, match="forced_provider_event_failure"):
        events.apply_event(
            provider_mapping(valid_from_ns=2_000, raw_symbol="AAPL.N"),
            source_event_ts_ns=2_000,
            metadata={"tick_size": "0.5"},
        )

    mappings = registry.list_provider_mappings(CANONICAL_ID)
    assert len(mappings) == 1
    assert mappings[0].valid_from_ns == 1_000
    assert mappings[0].valid_to_ns is None

    revisions = SQLiteInstrumentMetadataRepository(
        registry.database_path
    ).list_revisions(CANONICAL_ID, source_kind="provider")
    assert len(revisions) == 1
    assert revisions[0].effective_from_ns == 1_000
    assert revisions[0].effective_to_ns is None


def test_delete_event_closes_mapping_and_metadata_atomically_and_replays_idempotently(
    event_repository,
):
    registry, events = event_repository
    events.apply_event(
        provider_mapping(valid_from_ns=1_000),
        source_event_ts_ns=1_000,
        metadata={"tick_size": "0.25"},
    )

    closed_mapping, closed_metadata, created = events.apply_delete_event(
        provider="Databento",
        dataset="GLBX.MDP3",
        publisher_id=1,
        instrument_id=9001,
        effective_to_ns=2_000,
    )
    assert created is True
    assert closed_mapping.valid_from_ns == 1_000
    assert closed_mapping.valid_to_ns == 2_000
    assert closed_metadata.effective_from_ns == 1_000
    assert closed_metadata.effective_to_ns == 2_000

    replay_mapping, replay_metadata, replay_created = events.apply_delete_event(
        provider="databento",
        dataset="GLBX.MDP3",
        publisher_id=1,
        instrument_id=9001,
        effective_to_ns=2_000,
    )
    assert replay_created is False
    assert replay_mapping == closed_mapping
    assert replay_metadata == closed_metadata
    assert registry.list_provider_mappings(CANONICAL_ID)[0].valid_to_ns == 2_000
    revisions = SQLiteInstrumentMetadataRepository(
        registry.database_path
    ).list_revisions(CANONICAL_ID, source_kind="provider")
    assert len(revisions) == 1
    assert revisions[0].effective_to_ns == 2_000


def test_delete_event_rejects_stale_timestamp_without_mutation(event_repository):
    registry, events = event_repository
    events.apply_event(
        provider_mapping(valid_from_ns=1_000),
        source_event_ts_ns=1_000,
        metadata={"tick_size": "0.25"},
    )

    with pytest.raises(ProviderDefinitionEventConflict, match="later than"):
        events.apply_delete_event(
            provider="databento",
            dataset="GLBX.MDP3",
            publisher_id=1,
            instrument_id=9001,
            effective_to_ns=1_000,
        )

    mapping = registry.list_provider_mappings(CANONICAL_ID)[0]
    revision = SQLiteInstrumentMetadataRepository(
        registry.database_path
    ).list_revisions(CANONICAL_ID, source_kind="provider")[0]
    assert mapping.valid_to_ns is None
    assert revision.effective_to_ns is None


def test_delete_metadata_close_failure_rolls_back_mapping_close(event_repository):
    registry, events = event_repository
    events.apply_event(
        provider_mapping(valid_from_ns=1_000),
        source_event_ts_ns=1_000,
        metadata={"tick_size": "0.25"},
    )
    connection = sqlite3.connect(registry.database_path)
    try:
        connection.execute(
            """
            CREATE TRIGGER reject_provider_event_metadata_close
            BEFORE UPDATE ON instrument_metadata_revisions
            WHEN NEW.effective_to_ns = 2_000
            BEGIN
                SELECT RAISE(ABORT, 'forced_provider_metadata_close_failure');
            END
            """
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.IntegrityError, match="forced_provider_metadata_close_failure"):
        events.apply_delete_event(
            provider="databento",
            dataset="GLBX.MDP3",
            publisher_id=1,
            instrument_id=9001,
            effective_to_ns=2_000,
        )

    mapping = registry.list_provider_mappings(CANONICAL_ID)[0]
    revision = SQLiteInstrumentMetadataRepository(
        registry.database_path
    ).list_revisions(CANONICAL_ID, source_kind="provider")[0]
    assert mapping.valid_to_ns is None
    assert revision.effective_to_ns is None
