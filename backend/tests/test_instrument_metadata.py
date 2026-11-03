import pytest

from app.instrument_identity import CanonicalInstrument
from app.instrument_metadata import (
    MetadataRevisionConflict,
    SQLiteInstrumentMetadataRepository,
    UnknownMetadataInstrument,
)
from app.instrument_registry import SQLiteInstrumentRegistry

CANONICAL_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
UNKNOWN_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a99"


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


@pytest.fixture
def repositories(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(instrument())
    return registry, SQLiteInstrumentMetadataRepository(path)


def test_append_revision_is_normalized_persistent_and_idempotent(repositories):
    registry, metadata = repositories
    record, created = metadata.append_revision(
        canonical_id=CANONICAL_ID.upper(),
        source_kind="provider",
        source_name=" Databento ",
        source_dataset=" eq us.mini ",
        source_event_ts_ns=900,
        effective_from_ns=1_000,
        metadata={"tick_size": "0.01", "multiplier": "20"},
    )
    assert created is True
    assert record.canonical_id == CANONICAL_ID
    assert record.source_name == "databento"
    assert record.source_dataset == "EQ US.MINI"
    assert record.source_event_ts_ns == 900
    assert record.effective_from_ns == 1_000
    assert record.effective_to_ns is None
    assert record.validity_status == "known"
    assert record.metadata == {"multiplier": "20", "tick_size": "0.01"}
    assert record.received_at_utc

    duplicate, duplicate_created = metadata.append_revision(
        canonical_id=CANONICAL_ID,
        source_kind="provider",
        source_name="databento",
        source_dataset="EQ US.MINI",
        source_event_ts_ns=900,
        effective_from_ns=1_000,
        metadata={"multiplier": "20", "tick_size": "0.01"},
    )
    assert duplicate_created is False
    assert duplicate.revision_id == record.revision_id
    assert metadata.list_revisions(CANONICAL_ID) == [record]


def test_overlapping_same_source_revision_is_rejected_but_adjacent_is_allowed(repositories):
    _, metadata = repositories
    first, _ = metadata.append_revision(
        canonical_id=CANONICAL_ID,
        source_kind="provider",
        source_name="databento",
        source_dataset="GLBX.MDP3",
        effective_from_ns=100,
        effective_to_ns=200,
        metadata={"tick_size": "0.25"},
    )
    with pytest.raises(MetadataRevisionConflict, match="overlaps"):
        metadata.append_revision(
            canonical_id=CANONICAL_ID,
            source_kind="provider",
            source_name="databento",
            source_dataset="GLBX.MDP3",
            effective_from_ns=150,
            effective_to_ns=250,
            metadata={"tick_size": "0.5"},
        )
    adjacent, created = metadata.append_revision(
        canonical_id=CANONICAL_ID,
        source_kind="provider",
        source_name="databento",
        source_dataset="GLBX.MDP3",
        effective_from_ns=200,
        effective_to_ns=300,
        metadata={"tick_size": "0.5"},
    )
    assert created is True
    assert adjacent.revision_id > first.revision_id


def test_resolve_as_of_uses_half_open_intervals_and_excludes_unknown_history(repositories):
    _, metadata = repositories
    revision, _ = metadata.append_revision(
        canonical_id=CANONICAL_ID,
        source_kind="provider",
        source_name="databento",
        source_dataset="GLBX.MDP3",
        effective_from_ns=100,
        effective_to_ns=200,
        metadata={"tick_size": "0.25"},
    )
    assert metadata.resolve_as_of(CANONICAL_ID, 99) is None
    assert metadata.resolve_as_of(CANONICAL_ID, 100) == revision
    assert metadata.resolve_as_of(CANONICAL_ID, 199) == revision
    assert metadata.resolve_as_of(CANONICAL_ID, 200) is None
    # The schema-v2 legacy baseline is historical-unknown, not a fabricated
    # effective revision, and therefore never resolves at an arbitrary time.


def test_ambiguous_cross_source_claims_fail_closed(repositories):
    _, metadata = repositories
    provider, _ = metadata.append_revision(
        canonical_id=CANONICAL_ID,
        source_kind="provider",
        source_name="databento",
        effective_from_ns=100,
        metadata={"tick_size": "0.25"},
    )
    operator, _ = metadata.append_revision(
        canonical_id=CANONICAL_ID,
        source_kind="operator",
        source_name="manual-review",
        effective_from_ns=100,
        metadata={"tick_size": "0.5"},
    )
    with pytest.raises(MetadataRevisionConflict, match="Multiple source claims"):
        metadata.resolve_as_of(CANONICAL_ID, 150)
    assert metadata.resolve_as_of(
        CANONICAL_ID, 150, source_kind="provider", source_name="databento"
    ) == provider
    assert metadata.resolve_as_of(
        CANONICAL_ID, 150, source_kind="operator"
    ) == operator


def test_open_revision_can_be_closed_once_without_changing_payload(repositories):
    _, metadata = repositories
    revision, _ = metadata.append_revision(
        canonical_id=CANONICAL_ID,
        source_kind="provider",
        source_name="databento",
        effective_from_ns=100,
        metadata={"tick_size": "0.25"},
    )
    closed = metadata.close_open_revision(revision.revision_id, 200)
    assert closed.effective_to_ns == 200
    assert closed.metadata == revision.metadata
    assert metadata.resolve_as_of(CANONICAL_ID, 199) == closed
    assert metadata.resolve_as_of(CANONICAL_ID, 200) is None
    with pytest.raises(ValueError, match="open known revision"):
        metadata.close_open_revision(revision.revision_id, 300)


def test_unknown_canonical_instrument_and_invalid_payloads_are_rejected(repositories):
    _, metadata = repositories
    with pytest.raises(UnknownMetadataInstrument):
        metadata.append_revision(
            canonical_id=UNKNOWN_ID,
            source_kind="provider",
            source_name="databento",
            effective_from_ns=100,
            metadata={"tick_size": "0.25"},
        )
    with pytest.raises(ValueError, match="SQLite-range"):
        metadata.append_revision(
            canonical_id=CANONICAL_ID,
            source_kind="provider",
            source_name="databento",
            effective_from_ns=-1,
            metadata={},
        )
    with pytest.raises(ValueError, match="finite JSON"):
        metadata.append_revision(
            canonical_id=CANONICAL_ID,
            source_kind="provider",
            source_name="databento",
            effective_from_ns=100,
            metadata={"bad_number": float("nan")},
        )
    with pytest.raises(ValueError, match="source_kind"):
        metadata.append_revision(
            canonical_id=CANONICAL_ID,
            source_kind="legacy_migration",
            source_name="legacy",
            effective_from_ns=100,
            metadata={},
        )
