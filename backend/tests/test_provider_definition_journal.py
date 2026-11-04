import sqlite3

import pytest

from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import SQLiteInstrumentRegistry
from app.provider_definition_journal import (
    ProviderDefinitionJournalConflict,
    SQLiteProviderDefinitionJournal,
)

CANONICAL_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"


def event_kwargs(**overrides):
    values = {
        "provider": "Databento",
        "dataset": "GLBX.MDP3",
        "publisher_id": 1,
        "instrument_id": 9001,
        "source_event_ts_ns": 1_000,
        "source_order": 0,
        "action": "A",
        "raw_symbol": "ESZ6",
        "payload": {
            "unit_of_measure_qty": 50_000_000_000,
            "unit_of_measure": "USD",
            "contract_multiplier": 1_000_000_000,
            "currency": "USD",
            "settl_currency": "USD",
        },
    }
    values.update(overrides)
    return values


@pytest.fixture
def journal(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    SQLiteInstrumentRegistry(path)
    return path, SQLiteProviderDefinitionJournal(path)


def test_append_event_is_durable_idempotent_and_preserves_raw_contract_fields(journal):
    path, events = journal
    first, created = events.append_event(**event_kwargs())
    replay, replay_created = events.append_event(**event_kwargs())

    assert created is True
    assert replay_created is False
    assert replay.event_id == first.event_id
    assert replay.payload["unit_of_measure_qty"] == 50_000_000_000
    assert replay.payload["contract_multiplier"] == 1_000_000_000
    assert replay.processing_status == "pending"

    reopened = SQLiteProviderDefinitionJournal(path)
    persisted = reopened.get_event(first.event_id)
    assert persisted == first
    assert len(reopened.list_pending()) == 1


def test_same_source_order_with_different_payload_is_rejected(journal):
    _, events = journal
    events.append_event(**event_kwargs())
    with pytest.raises(ProviderDefinitionJournalConflict, match="different event contents"):
        events.append_event(**event_kwargs(payload={"raw_symbol": "ESZ6", "price": 1}))


def test_same_timestamp_events_keep_explicit_provider_order(journal):
    _, events = journal
    later = events.append_event(**event_kwargs(source_order=1, raw_symbol="NQZ6"))[0]
    earlier = events.append_event(**event_kwargs(source_order=0, raw_symbol="ESZ6"))[0]
    assert [item.event_id for item in events.list_pending()] == [
        earlier.event_id, later.event_id
    ]


def test_event_can_be_applied_once_and_state_is_immutable(journal):
    path, events = journal
    instrument = CanonicalInstrument(
        canonical_id=CANONICAL_ID, asset_class="equity", instrument_type="stock",
        symbol="AAPL", venue="XNAS", quote_currency="USD", tick_size="0.01",
    )
    SQLiteInstrumentRegistry(path).register_instrument(instrument)
    record, _ = events.append_event(**event_kwargs())
    assert events.mark_applied(record.event_id, CANONICAL_ID) is True
    assert events.mark_applied(record.event_id, CANONICAL_ID) is False
    assert events.get_event(record.event_id).processing_status == "applied"

    connection = sqlite3.connect(path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="provider_definition_event_is_immutable"):
            connection.execute(
                "UPDATE provider_definition_events SET payload_json = '{}' WHERE event_id = ?",
                (record.event_id,),
            )
    finally:
        connection.close()


def test_event_can_be_quarantined_idempotently_and_cannot_be_reapplied(journal):
    _, events = journal
    record, _ = events.append_event(**event_kwargs(action="D"))
    assert events.mark_quarantined(record.event_id, "missing_authoritative_identity") is True
    assert events.mark_quarantined(record.event_id, "missing_authoritative_identity") is False
    with pytest.raises(ProviderDefinitionJournalConflict, match="cannot be marked applied"):
        events.mark_applied(record.event_id, CANONICAL_ID)
    quarantined = events.get_event(record.event_id)
    assert quarantined.processing_status == "quarantined"
    assert quarantined.error_code == "missing_authoritative_identity"


def test_event_journal_rejects_invalid_order_and_nonfinite_payload(journal):
    _, events = journal
    with pytest.raises(ValueError, match="source_order"):
        events.append_event(**event_kwargs(source_order=-1))
    with pytest.raises(ValueError, match="finite JSON-compatible"):
        events.append_event(**event_kwargs(payload={"bad": float("nan")}))
