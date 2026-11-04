"""Durable Databento definition lifecycle synchronization.

Provider records are journaled before canonical resolution. Registry mapping and
metadata transitions are committed atomically; journal state advances only
after that transaction succeeds. In-memory views are projections of persisted
state and can be rebuilt after process restart.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping
from uuid import uuid4

from app.databento_definition_normalizer import (
    InvalidDatabentoDefinition,
    normalize_databento_definition,
)
from app.instrument_events import (
    ProviderDefinitionEventConflict,
    SQLiteProviderDefinitionEventRepository,
)
from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import (
    CanonicalIdentityConflict,
    ProviderInstrumentMapping,
    SQLiteInstrumentRegistry,
)
from app.instruments import InstrumentCatalog
from app.provider_definition_journal import SQLiteProviderDefinitionJournal
from app.symbology import InstrumentResolver, SymbolMapping


class DatabentoDefinitionSynchronizer:
    """Journal, resolve, persist, and project Add/Modify/Delete definitions."""

    def __init__(
        self,
        database_path: str,
        registry: SQLiteInstrumentRegistry,
        catalog: InstrumentCatalog,
        resolver: InstrumentResolver,
        *,
        provider: str = "databento",
        dataset: str = "GLBX.MDP3",
    ) -> None:
        self._registry = registry
        self._catalog = catalog
        self._resolver = resolver
        self._provider = provider.strip().lower()
        self._dataset = dataset.strip().upper()
        self._journal = SQLiteProviderDefinitionJournal(database_path)
        self._events = SQLiteProviderDefinitionEventRepository(database_path)

    def restore_resolver(self) -> int:
        """Rebuild the point-in-time resolver from durable registry mappings."""
        mappings: list[SymbolMapping] = []
        instruments = []
        offset = 0
        while True:
            page = self._registry.list_instruments(
                active_only=False, limit=1000, offset=offset
            )
            instruments.extend(page)
            if len(page) < 1000:
                break
            offset += len(page)
        for instrument in instruments:
            for item in self._registry.list_provider_mappings(instrument.canonical_id):
                if item.provider != self._provider or item.dataset != self._dataset:
                    continue
                mappings.append(SymbolMapping(
                    provider=item.provider,
                    dataset=item.dataset,
                    publisher_id=item.publisher_id,
                    instrument_id=item.instrument_id,
                    raw_symbol=item.raw_symbol,
                    valid_from_ns=item.valid_from_ns,
                    valid_to_ns=item.valid_to_ns,
                    series_type=item.series_type,
                    asset_class=instrument.asset_class,
                ))
        self._resolver.replace_all(mappings)
        return len(mappings)

    def ingest_rows(self, rows: Iterable[Mapping[str, Any]]) -> tuple[int, int]:
        """Append a historical batch then replay pending events in stable order.

        The source iterator's order is retained within equal event timestamps.
        A deterministic per-instrument ordinal is used because DBN definition
        records do not expose a universally available sequence field here.
        """
        ordered = list(rows)
        ordered.sort(key=lambda row: self._required_int(row, "ts_event"))
        ordinals: dict[tuple[int, int, int], int] = defaultdict(int)
        for row in ordered:
            if not isinstance(row, Mapping):
                raise TypeError("definition rows must be mappings")
            publisher_id = self._required_int(row, "publisher_id")
            instrument_id = self._required_int(row, "instrument_id")
            event_ts = self._required_int(row, "ts_event")
            key = (publisher_id, instrument_id, event_ts)
            source_order = ordinals[key]
            ordinals[key] += 1
            action = self._text(row, "security_update_action").upper()
            raw_symbol = self._text(row, "raw_symbol").upper()
            self._journal.append_event(
                provider=self._provider,
                dataset=self._dataset,
                publisher_id=publisher_id,
                instrument_id=instrument_id,
                source_event_ts_ns=event_ts,
                source_order=source_order,
                action=action,
                raw_symbol=raw_symbol,
                payload=dict(row),
            )
        return self.replay_pending()

    def replay_pending(self, *, limit: int = 1000) -> tuple[int, int]:
        """Replay a bounded, deterministically ordered pending journal page."""
        applied = rejected = 0
        while True:
            batch = self._journal.list_pending(limit=limit)
            if not batch:
                break
            for record in batch:
                try:
                    canonical_id = self._apply_record(record)
                    self._journal.mark_applied(record.event_id, canonical_id)
                    applied += 1
                except (InvalidDatabentoDefinition, ProviderDefinitionEventConflict,
                        CanonicalIdentityConflict, KeyError, TypeError, ValueError) as exc:
                    code = self._error_code(exc)
                    self._journal.mark_quarantined(record.event_id, code)
                    rejected += 1
        return applied, rejected

    @staticmethod
    def _required_int(row: Mapping[str, Any], field: str) -> int:
        value = row.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"invalid_{field}")
        return value

    @staticmethod
    def _text(row: Mapping[str, Any], field: str) -> str:
        value = row.get(field)
        if isinstance(value, bytes):
            value = value.decode("ascii", errors="strict")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"missing_{field}")
        return value.strip()

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        message = str(exc).strip().lower()
        if message and all(ch.isalnum() or ch == "_" for ch in message):
            return message[:96]
        return type(exc).__name__.lower()

    def _apply_record(self, record) -> str:
        if record.provider != self._provider or record.dataset != self._dataset:
            raise InvalidDatabentoDefinition("unexpected_provider_or_dataset")
        row = record.payload
        normalized = normalize_databento_definition(
            row,
            canonical_id=None,
            dataset=self._dataset,
            provider=self._provider,
        )
        key = dict(
            provider=self._provider,
            dataset=self._dataset,
            publisher_id=record.publisher_id,
            instrument_id=record.instrument_id,
        )
        if normalized.action == "D":
            previous = self._registry.resolve_provider_mapping(
                **key, timestamp_ns=record.source_event_ts_ns
            )
            if previous is None:
                raise ProviderDefinitionEventConflict("delete_without_active_mapping")
            mapping, _, _ = self._events.apply_delete_event(
                **key, effective_to_ns=record.source_event_ts_ns
            )
            self._resolver.close_mapping(
                **key, effective_to_ns=record.source_event_ts_ns
            )
            self._catalog.apply_definition_event(
                row, dataset=self._dataset
            )
            return mapping.canonical_id

        previous = self._registry.resolve_provider_mapping(
            **key, timestamp_ns=record.source_event_ts_ns
        )
        if normalized.action == "M" and previous is None:
            raise ProviderDefinitionEventConflict("modify_without_active_mapping")

        identity_candidate = normalize_databento_definition(
            row,
            canonical_id=str(uuid4()),
            dataset=self._dataset,
            provider=self._provider,
        ).instrument
        canonical_id = previous.canonical_id if previous else self._find_or_create_identity(
            identity_candidate
        )
        existing = self._registry.get_instrument(canonical_id)
        candidate = normalize_databento_definition(
            row,
            canonical_id=canonical_id,
            dataset=self._dataset,
            provider=self._provider,
        ).instrument
        if existing is None or candidate is None:
            raise ProviderDefinitionEventConflict("canonical_identity_missing")
        if self._identity_tuple(existing) != self._identity_tuple(candidate):
            raise ProviderDefinitionEventConflict("canonical_identity_changed")

        self._registry.register_instrument(existing)
        mapping = ProviderInstrumentMapping(
            provider=self._provider,
            dataset=self._dataset,
            publisher_id=record.publisher_id,
            instrument_id=record.instrument_id,
            raw_symbol=record.raw_symbol,
            valid_from_ns=record.source_event_ts_ns,
            valid_to_ns=None,
            canonical_id=canonical_id,
            series_type="contract",
        )
        self._events.apply_event(
            mapping,
            metadata=normalized.metadata,
            source_event_ts_ns=record.source_event_ts_ns,
            payload_schema_version=1,
        )
        self._resolver.close_mapping(
            **key, effective_to_ns=record.source_event_ts_ns
        )
        self._resolver.add(SymbolMapping(
            provider=self._provider,
            dataset=self._dataset,
            publisher_id=record.publisher_id,
            instrument_id=record.instrument_id,
            raw_symbol=record.raw_symbol,
            valid_from_ns=record.source_event_ts_ns,
            series_type="contract",
            asset_class="future",
        ))
        self._catalog.apply_definition_event(row, dataset=self._dataset)
        return canonical_id

    def _find_or_create_identity(self, candidate: CanonicalInstrument | None) -> str:
        if candidate is None:
            raise InvalidDatabentoDefinition("canonical_identity_not_normalized")
        matches = []
        offset = 0
        while True:
            page = self._registry.list_instruments(
                asset_class=candidate.asset_class,
                venue=candidate.venue,
                symbol=candidate.symbol,
                active_only=False,
                limit=1000,
                offset=offset,
            )
            matches.extend(
                item for item in page
                if self._identity_tuple(item) == self._identity_tuple(candidate)
            )
            if len(page) < 1000:
                break
            offset += len(page)
        if len(matches) > 1:
            raise ProviderDefinitionEventConflict("ambiguous_canonical_identity")
        if matches:
            return matches[0].canonical_id
        new_instrument = CanonicalInstrument(
            **{**candidate.to_dict(), "canonical_id": str(uuid4())}
        )
        try:
            self._registry.register_instrument(new_instrument)
            return new_instrument.canonical_id
        except CanonicalIdentityConflict:
            # A concurrent writer may have won the same identity insert.
            return self._find_existing_identity(candidate)

    def _find_existing_identity(self, candidate: CanonicalInstrument) -> str:
        page = self._registry.list_instruments(
            asset_class=candidate.asset_class,
            venue=candidate.venue,
            symbol=candidate.symbol,
            active_only=False,
            limit=1000,
        )
        matches = [item for item in page if self._identity_tuple(item) == self._identity_tuple(candidate)]
        if len(matches) != 1:
            raise ProviderDefinitionEventConflict("canonical_identity_race_unresolved")
        return matches[0].canonical_id

    @staticmethod
    def _identity_tuple(instrument: CanonicalInstrument) -> tuple[Any, ...]:
        return (
            instrument.asset_class,
            instrument.instrument_type,
            instrument.venue,
            instrument.symbol,
            instrument.expiration_date,
            instrument.settlement_currency,
            instrument.contract_multiplier,
        )
