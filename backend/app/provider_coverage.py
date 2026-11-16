"""Evidence-gated provider/instrument coverage calculations.

This module calculates coverage only from explicit, reviewed mappings. It never
infers symbol support from provider names or external search results. A mapping
is counted only when its provider is eligible for the recurring-$0 baseline.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.provider_catalog import ProviderCandidate


@dataclass(frozen=True, slots=True)
class ProviderInstrumentMapping:
    provider_id: str
    instrument_id: str
    venue: str
    data_family: str
    evidence_ref: str


@dataclass(frozen=True, slots=True)
class CoverageReport:
    watchlist: tuple[str, ...]
    covered: tuple[str, ...]
    uncovered: tuple[str, ...]
    redundant: tuple[str, ...]
    eligible_mapping_count: int
    rejected_mapping_count: int
    provider_counts: tuple[tuple[str, int], ...]

    @property
    def coverage_ratio(self) -> float:
        if not self.watchlist:
            return 1.0
        return len(self.covered) / len(self.watchlist)


def build_coverage_report(
    watchlist: Iterable[str],
    mappings: Iterable[ProviderInstrumentMapping],
    candidates: Iterable[ProviderCandidate],
) -> CoverageReport:
    """Return a deterministic coverage union using eligible, evidence-backed mappings.

    Invalid, duplicate, out-of-watchlist, unknown-provider, or ineligible-provider
    mappings are rejected. No network calls or provider activation occur.
    """
    instruments = tuple(sorted({item.strip() for item in watchlist if isinstance(item, str) and item.strip()}))
    wanted = set(instruments)
    candidate_by_id = {item.provider_id: item for item in candidates}
    covered_by: dict[str, set[str]] = {item: set() for item in instruments}
    seen: set[tuple[str, str, str, str]] = set()
    eligible_count = 0
    rejected_count = 0

    for mapping in mappings:
        if not isinstance(mapping, ProviderInstrumentMapping):
            rejected_count += 1
            continue
        provider_id = mapping.provider_id.strip().lower()
        instrument_id = mapping.instrument_id.strip()
        venue = mapping.venue.strip()
        data_family = mapping.data_family.strip().lower()
        evidence_ref = mapping.evidence_ref.strip()
        key = (provider_id, instrument_id, venue, data_family)

        candidate = candidate_by_id.get(provider_id)
        if (
            not provider_id
            or not instrument_id
            or not venue
            or not data_family
            or not evidence_ref
            or instrument_id not in wanted
            or candidate is None
            or not candidate.eligible_for_zero_cost_baseline
            or key in seen
        ):
            rejected_count += 1
            continue

        seen.add(key)
        covered_by[instrument_id].add(provider_id)
        eligible_count += 1

    covered = tuple(item for item in instruments if covered_by[item])
    uncovered = tuple(item for item in instruments if not covered_by[item])
    redundant = tuple(item for item in instruments if len(covered_by[item]) > 1)
    provider_counts = tuple(
        sorted(
            (provider_id, count)
            for provider_id, count in _count_providers(covered_by).items()
            if count
        )
    )
    return CoverageReport(
        watchlist=instruments,
        covered=covered,
        uncovered=uncovered,
        redundant=redundant,
        eligible_mapping_count=eligible_count,
        rejected_mapping_count=rejected_count,
        provider_counts=provider_counts,
    )


def _count_providers(covered_by: dict[str, set[str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for providers in covered_by.values():
        for provider_id in providers:
            counts[provider_id] = counts.get(provider_id, 0) + 1
    return counts
