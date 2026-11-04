"""Deterministic tiered OHLCV aggregation (UTC bucket policy).

Each timeframe is derived from its PARENT timeframe (the largest finer
timeframe whose interval divides it), e.g. 1s -> 5s -> 15s -> 30s -> 1m ->
5m -> 15m -> 30m -> 1h -> 2h -> 4h -> 1d -> 1w / 1M -> 3M. Provider-sourced
bars of any timeframe (e.g. historical ohlcv-1d) take precedence over derived
bars with the same identity and feed the next tier, so 1d/1w/1M/3M history
does not depend on retaining every 1-second bar.

A bucket is always RECOMPUTED from the distinct child bars currently stored
(never incrementally added), so duplicates and revisions cannot double-count
volume. No bar is created for a bucket without child bars. A bucket is not
recomputed when children may already have been evicted (bucket start at or
below the child series' evicted floor): that skip is counted, never silent.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Callable

from app.coverage import CoverageTracker
from app.ohlcv import (
    FIXED_INTERVAL_SECONDS,
    ORIGIN_DERIVED,
    InvalidOhlcvBar,
    OhlcvBar,
    OhlcvPipeline,
    bucket_end_ns,
    bucket_start_ns,
)

_ORDER = list(FIXED_INTERVAL_SECONDS) + ["1w", "1M", "3M"]


def _build_parents() -> dict[str, str | None]:
    parents: dict[str, str | None] = {"1s": None, "1w": "1d", "1M": "1d", "3M": "1M"}
    fixed = list(FIXED_INTERVAL_SECONDS.items())
    for name, seconds in fixed:
        if name == "1s":
            continue
        candidates = [
            (s, n) for n, s in fixed if s < seconds and seconds % s == 0
        ]
        parents[name] = max(candidates)[1]
    return parents


PARENT: dict[str, str | None] = _build_parents()
CHILDREN: dict[str, tuple[str, ...]] = {
    parent: tuple(tf for tf in _ORDER if PARENT[tf] == parent)
    for parent in _ORDER
}


def derive_bar(
    children: list[OhlcvBar], timeframe: str, bucket_start: int, completeness: str
) -> OhlcvBar:
    """Pure: build one derived bar from distinct, same-series child bars."""
    ordered = sorted(children, key=lambda b: b.ts_start_ns)
    first, last = ordered[0], ordered[-1]
    return OhlcvBar(
        dataset=first.dataset, publisher_id=first.publisher_id,
        instrument_id=first.instrument_id, raw_symbol=first.raw_symbol,
        timeframe=timeframe, ts_start_ns=bucket_start,  # type: ignore[arg-type]
        open=first.open, close=last.close,
        high=max(b.high for b in ordered), low=min(b.low for b in ordered),
        volume=sum((b.volume for b in ordered), Decimal(0)),
        ts_event_ns=max(b.ts_event_ns for b in ordered),
        ts_received_ns=max(b.ts_received_ns for b in ordered),
        sequence=max(b.sequence for b in ordered), sequence_origin="local",
        provider=first.provider, series_type=first.series_type,
        origin=ORIGIN_DERIVED, completeness=completeness,
    )


class Aggregator:
    """Cascades derived bars into the pipeline after each accepted bar."""

    def __init__(
        self,
        pipeline: OhlcvPipeline,
        coverage: CoverageTracker | None = None,
        on_derived_bar: Callable[[OhlcvBar], None] | None = None,
        before_derived_apply: Callable[[OhlcvBar], bool] | None = None,
    ) -> None:
        self._pipeline = pipeline
        self._coverage = coverage
        self._on_derived_bar = on_derived_bar
        self._before_derived_apply = before_derived_apply
        self.stats = {"derived_written": 0, "skipped_evicted": 0, "rejected": 0}

    def on_bar_applied(self, bar: OhlcvBar) -> int:
        """Rebuild every affected derived bucket; returns bars written."""
        written = 0
        stack = [bar]
        while stack:
            current = stack.pop()
            for child_tf in CHILDREN.get(current.timeframe, ()):
                start = bucket_start_ns(current.ts_start_ns, child_tf)
                written += self._rebuild(current.series_key, child_tf, start, stack)
                written += self._close_previous(current.series_key, child_tf, start, stack)
        return written

    def _close_previous(self, parent_series, child_tf, start, stack) -> int:
        child_series = parent_series[:-1] + (child_tf,)
        previous = self._pipeline.previous_bar(child_series, start)
        if previous is None or previous.origin != ORIGIN_DERIVED or previous.completeness != "open":
            return 0
        return self._rebuild(parent_series, child_tf, previous.ts_start_ns, stack)

    def _rebuild(self, parent_series, child_tf: str, start: int, stack: list[OhlcvBar]) -> int:
        end = bucket_end_ns(start, child_tf)
        if start <= self._pipeline.evicted_floor(parent_series):
            self.stats["skipped_evicted"] += 1
            return 0
        children = self._pipeline.range_bars(parent_series, start, end)
        if not children:
            return 0
        completeness = self._completeness(parent_series, children, start, end)
        try:
            derived = derive_bar(children, child_tf, start, completeness)
        except InvalidOhlcvBar:
            self.stats["rejected"] += 1
            return 0
        if self._before_derived_apply is not None:
            try:
                if not self._before_derived_apply(derived):
                    self.stats["persistence_rejected"] = self.stats.get("persistence_rejected", 0) + 1
                    return 0
            except Exception:
                self.stats["persistence_error"] = self.stats.get("persistence_error", 0) + 1
                return 0
        if self._pipeline.apply(derived) in ("inserted", "replaced"):
            self.stats["derived_written"] += 1
            stack.append(derived)
            if self._on_derived_bar is not None:
                try:
                    self._on_derived_bar(derived)
                except Exception:
                    # A stream client failure must not interrupt aggregation.
                    self.stats["broadcast_callback_error"] = self.stats.get("broadcast_callback_error", 0) + 1
            return 1
        return 0

    def _completeness(self, parent_series, children: list[OhlcvBar], start: int, end: int) -> str:
        parent_tf = parent_series[-1]
        latest = self._pipeline.latest_ts(parent_series)
        if latest is None or end > bucket_end_ns(latest, parent_tf):
            return "open"
        if self._coverage is None:
            return "partial"
        if any(c.origin == ORIGIN_DERIVED and c.completeness != "complete" for c in children):
            return "partial"
        scope = parent_series[:-1]
        return "complete" if self._coverage.status(scope, start, end) == "covered" else "partial"