"""Point-in-time instrument identity resolution.

A provider ``instrument_id`` is only meaningful within (provider, dataset,
publisher_id) and within a validity window; it may be reassigned to another
symbol later. This resolver therefore maps (provider, dataset, publisher_id,
instrument_id, timestamp) -> raw symbol, and refuses ambiguous overlaps.
It never invents mappings: an unknown instrument resolves to ``None``.
"""
from __future__ import annotations

from bisect import insort
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Iterable, Mapping

_NS = 1_000_000_000
_SECONDS_PER_DAY = 86_400


class SymbolConflict(ValueError):
    """Raised when two different symbols claim the same id and time window."""


@dataclass(frozen=True, slots=True)
class SymbolMapping:
    provider: str
    dataset: str
    publisher_id: int
    instrument_id: int
    raw_symbol: str
    valid_from_ns: int
    valid_to_ns: int | None = None  # exclusive; None = open-ended
    series_type: str = "contract"
    asset_class: str = "future"

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.dataset.strip() or not self.raw_symbol.strip():
            raise ValueError("provider, dataset and raw_symbol are required.")
        for name in ("publisher_id", "instrument_id", "valid_from_ns"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer.")
        if self.valid_to_ns is not None and (
            not isinstance(self.valid_to_ns, int) or self.valid_to_ns <= self.valid_from_ns
        ):
            raise ValueError("valid_to_ns must be greater than valid_from_ns.")

    @property
    def key(self) -> tuple[str, str, int, int]:
        return (self.provider, self.dataset, self.publisher_id, self.instrument_id)

    def contains(self, ts_ns: int) -> bool:
        return ts_ns >= self.valid_from_ns and (
            self.valid_to_ns is None or ts_ns < self.valid_to_ns
        )

    @property
    def coverage_scope(self) -> tuple[str, str, int, int, str, str]:
        return (self.provider, self.dataset, self.publisher_id, self.instrument_id,
                self.series_type, self.raw_symbol)

    def _overlaps(self, other: "SymbolMapping") -> bool:
        a_end = self.valid_to_ns if self.valid_to_ns is not None else float("inf")
        b_end = other.valid_to_ns if other.valid_to_ns is not None else float("inf")
        return self.valid_from_ns < b_end and other.valid_from_ns < a_end


class InstrumentResolver:
    """In-memory, loop-confined resolver (single writer, like the pipeline)."""

    def __init__(self) -> None:
        self._by_key: dict[tuple[str, str, int, int], list[SymbolMapping]] = {}

    def __len__(self) -> int:
        return sum(len(items) for items in self._by_key.values())

    def add(self, mapping: SymbolMapping) -> None:
        """Add a mapping. Same-symbol overlaps merge; different-symbol overlaps
        raise SymbolConflict and leave the resolver unchanged."""
        existing = self._by_key.get(mapping.key, [])
        merged = mapping
        keep: list[SymbolMapping] = []
        for item in existing:
            if not item._overlaps(merged):
                keep.append(item)
                continue
            if (item.raw_symbol, item.series_type) != (merged.raw_symbol, merged.series_type):
                raise SymbolConflict(
                    f"Instrument {mapping.instrument_id} already maps to "
                    f"{item.raw_symbol} in an overlapping window."
                )
            ends = (item.valid_to_ns, merged.valid_to_ns)
            merged = SymbolMapping(
                provider=merged.provider, dataset=merged.dataset,
                publisher_id=merged.publisher_id, instrument_id=merged.instrument_id,
                raw_symbol=merged.raw_symbol,
                valid_from_ns=min(item.valid_from_ns, merged.valid_from_ns),
                valid_to_ns=None if None in ends else max(ends),  # type: ignore[type-var]
                series_type=merged.series_type, asset_class=merged.asset_class,
            )
        keep.append(merged)
        keep.sort(key=lambda m: m.valid_from_ns)
        self._by_key[mapping.key] = keep

    def replace_all(self, mappings: Iterable[SymbolMapping]) -> None:
        """Atomically replace every mapping (built aside, swapped on success)."""
        staged = InstrumentResolver()
        for mapping in mappings:
            staged.add(mapping)
        self._by_key = staged._by_key

    def close_mapping(
        self,
        *,
        provider: str,
        dataset: str,
        publisher_id: int,
        instrument_id: int,
        effective_to_ns: int,
    ) -> bool:
        """Close active point-in-time mappings at an exclusive event timestamp."""
        if (
            not isinstance(effective_to_ns, int)
            or isinstance(effective_to_ns, bool)
            or effective_to_ns < 0
        ):
            raise ValueError("effective_to_ns must be a non-negative integer.")
        key = (provider.strip().lower(), dataset.strip().upper(), publisher_id, instrument_id)
        existing = self._by_key.get(key, [])
        changed = False
        updated: list[SymbolMapping] = []
        for item in existing:
            if (
                item.valid_from_ns < effective_to_ns
                and (item.valid_to_ns is None or item.valid_to_ns > effective_to_ns)
            ):
                updated.append(SymbolMapping(
                    provider=item.provider,
                    dataset=item.dataset,
                    publisher_id=item.publisher_id,
                    instrument_id=item.instrument_id,
                    raw_symbol=item.raw_symbol,
                    valid_from_ns=item.valid_from_ns,
                    valid_to_ns=effective_to_ns,
                    series_type=item.series_type,
                    asset_class=item.asset_class,
                ))
                changed = True
            else:
                updated.append(item)
        if changed:
            self._by_key[key] = updated
        return changed

    def mappings_for_symbol(
        self, provider: str, dataset: str, raw_symbol: str
    ) -> tuple[SymbolMapping, ...]:
        """Return known point-in-time mappings for one explicit raw symbol."""
        return tuple(
            mapping
            for key, items in self._by_key.items()
            if key[0] == provider and key[1] == dataset
            for mapping in items
            if mapping.raw_symbol == raw_symbol
        )

    def resolve(
        self, provider: str, dataset: str, publisher_id: int, instrument_id: int, ts_ns: int
    ) -> SymbolMapping | None:
        for item in self._by_key.get((provider, dataset, publisher_id, instrument_id), ()):
            if item.contains(ts_ns):
                return item
        return None

    def register_catalog_contracts(
        self,
        contracts: Iterable[Mapping[str, Any]],
        *,
        provider: str = "databento",
    ) -> tuple[int, int]:
        """Register InstrumentCatalog.list_contracts() rows. Validity policy:
        [definition ts_event, end of expiration date UTC). Returns
        (registered, rejected). Rows that conflict or are malformed are counted."""
        registered = rejected = 0
        for row in contracts:
            try:
                valid_from = int(row["definition_ts_event_ns"])
                expiry = date.fromisoformat(str(row["expiration"])[:10]) + timedelta(days=1)
                valid_to = int(
                    (expiry - date(1970, 1, 1)).days * _SECONDS_PER_DAY * _NS
                )
                mapping = SymbolMapping(
                    provider=provider, dataset=str(row["dataset"]),
                    publisher_id=int(row["publisher_id"]),
                    instrument_id=int(row["instrument_id"]),
                    raw_symbol=str(row["raw_symbol"]),
                    valid_from_ns=valid_from, valid_to_ns=valid_to,
                )
                self.close_mapping(
                    provider=mapping.provider,
                    dataset=mapping.dataset,
                    publisher_id=mapping.publisher_id,
                    instrument_id=mapping.instrument_id,
                    effective_to_ns=mapping.valid_from_ns,
                )
                self.add(mapping)
                registered += 1
            except (KeyError, TypeError, ValueError):
                rejected += 1
        return registered, rejected