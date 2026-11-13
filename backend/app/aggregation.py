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

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Callable

from app.coverage import CoverageTracker
from app.session_calendar import SessionCalendarRegistry, lookup_instant, session_bucket_bounds
from app.ohlcv import (
    BUCKET_POLICY_CME_SESSION_V1,
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
    children: list[OhlcvBar], timeframe: str, bucket_start: int, completeness: str,
    *, bucket_policy: str | None = None, calendar_id: str | None = None,
    calendar_version: str | None = None,
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
        bucket_policy=first.bucket_policy if bucket_policy is None else bucket_policy,
        calendar_id=first.calendar_id if calendar_id is None else calendar_id,
        calendar_version=first.calendar_version if calendar_version is None else calendar_version,
    )


class Aggregator:
    """Cascades derived bars into the pipeline after each accepted bar."""

    def __init__(
        self,
        pipeline: OhlcvPipeline,
        coverage: CoverageTracker | None = None,
        on_derived_bar: Callable[[OhlcvBar], None] | None = None,
        before_derived_apply: Callable[[OhlcvBar], bool] | None = None,
        session_calendars: SessionCalendarRegistry | None = None,
    ) -> None:
        self._pipeline = pipeline
        self._session_calendars = session_calendars
        self._coverage = coverage
        self._on_derived_bar = on_derived_bar
        self._before_derived_apply = before_derived_apply
        self.stats = {
            "derived_written": 0,
            "skipped_evicted": 0,
            "skipped_cme_calendar_unresolved": 0,
            "skipped_cme_daily_unresolved": 0,
            "rejected_cme_daily_child": 0,
            "rejected": 0,
        }

    def on_bar_applied(self, bar: OhlcvBar, *, session_validation=None) -> int:
        """Rebuild affected buckets; validated 1m CME inputs may seed session 1d."""
        written = 0
        stack = [bar]
        while stack:
            current = stack.pop()
            # CME session bars are structurally identifiable, but deriving
            # higher periods stays fail-closed until a verified calendar
            # resolver supplies exact exchange bucket bounds. Count this once
            # per input/derived bar, not once per possible parent timeframe.
            if current.bucket_policy == BUCKET_POLICY_CME_SESSION_V1:
                if self._session_calendars is None:
                    self.stats["skipped_cme_calendar_unresolved"] += 1
                    continue
                written += self._rebuild_session_parents(current, stack)
                continue
            if (
                session_validation is not None
                and current.timeframe == "1m"
                and current.bucket_policy == "UTC_FIXED_V1"
            ):
                minute_validation = self._session_validation_for_minute(
                    current, session_validation
                )
                if minute_validation is None:
                    self.stats["skipped_cme_daily_unresolved"] += 1
                else:
                    written += self._rebuild_session_daily(
                        current, minute_validation, stack
                    )
            for child_tf in CHILDREN.get(current.timeframe, ()):
                # UTC intraday bars must not be relabelled as session buckets.
                if current.bucket_policy == "UTC_FIXED_V1" and child_tf in ("1d", "1w", "1M", "3M"):
                    continue
                start = bucket_start_ns(current.ts_start_ns, child_tf)
                written += self._rebuild(current.series_key, child_tf, start, stack)
                written += self._close_previous(current.series_key, child_tf, start, stack)
        return written

    def _session_validation_for_minute(self, current: OhlcvBar, validation):
        """Resolve the complete UTC 1m interval under the already pinned release.

        The incoming validation may belong to a 1s/5s/15s source bar that
        produced this derived minute. Re-resolve the minute itself instead of
        incorrectly reusing the source bar's shorter interval bounds.
        """
        if self._session_calendars is None:
            return None
        try:
            calendar_id = validation.calendar_id
            calendar_version = validation.calendar_version
            trading_date = validation.trading_date
            if (
                not isinstance(calendar_id, str) or not calendar_id.strip()
                or not isinstance(calendar_version, str) or not calendar_version.strip()
                or not isinstance(trading_date, str) or not trading_date.strip()
            ):
                return None
            calendar = self._session_calendars.get(calendar_id, calendar_version)
            if calendar is None or calendar.calendar_id != calendar_id:
                return None
            seconds, nanos = divmod(current.ts_start_ns, 1_000_000_000)
            if nanos % 1_000:
                return None
            instant = datetime.fromtimestamp(seconds, tz=timezone.utc).replace(
                microsecond=nanos // 1_000
            )
            lookup = lookup_instant(calendar, instant)
            interval_end_ns = current.ts_start_ns + 60 * 1_000_000_000
            if (
                lookup.trading_date is None
                or lookup.trading_date.isoformat() != trading_date
                or lookup.state not in ("open", "special-session")
                or lookup.segment_end_ns is None
                or interval_end_ns > lookup.segment_end_ns
            ):
                return None
            return SessionBarValidation(
                calendar_id=calendar_id,
                calendar_version=calendar_version,
                trading_date=trading_date,
                session_state=lookup.state,
                interval_start_ns=current.ts_start_ns,
                interval_end_ns=interval_end_ns,
            )
        except (AttributeError, TypeError, ValueError, OverflowError, OSError):
            return None

    def _rebuild_session_daily(self, current: OhlcvBar, validation, stack: list[OhlcvBar]) -> int:
        """Derive CME 1d from validated UTC 1m source bars without changing source identity.

        A single source timeframe (1m) is intentionally used for each daily
        series so mixed-resolution provider feeds cannot overwrite one another.
        Every retained child is rechecked against the pinned release before use.
        """
        if self._session_calendars is None:
            self.stats["skipped_cme_daily_unresolved"] += 1
            return 0
        try:
            calendar_id = validation.calendar_id
            calendar_version = validation.calendar_version
            trading_date = date.fromisoformat(validation.trading_date)
            if (
                not isinstance(calendar_id, str) or not calendar_id.strip()
                or not isinstance(calendar_version, str) or not calendar_version.strip()
                or validation.session_state not in ("open", "special-session")
                or validation.interval_start_ns != current.ts_start_ns
                or validation.interval_end_ns != current.ts_start_ns + 60 * 1_000_000_000
            ):
                raise ValueError("Session validation does not match the 1m source bar.")
            calendar = self._session_calendars.get(calendar_id, calendar_version)
            if calendar is None:
                raise ValueError("Pinned calendar release is unavailable.")
            seconds, nanos = divmod(current.ts_start_ns, 1_000_000_000)
            instant = datetime.fromtimestamp(seconds, tz=timezone.utc) + timedelta(
                microseconds=nanos // 1_000
            )
            lookup = lookup_instant(calendar, instant)
            if (
                lookup.trading_date != trading_date
                or lookup.state not in ("open", "special-session")
                or lookup.segment_end_ns is None
                or validation.interval_end_ns > lookup.segment_end_ns
            ):
                raise ValueError("Source bar is outside its pinned tradable segment.")
            bounds = session_bucket_bounds(calendar, trading_date, "1d")
            if bounds is None:
                raise ValueError("Daily session bounds are not fully covered by the release.")
        except (AttributeError, TypeError, ValueError, OverflowError, OSError):
            self.stats["skipped_cme_daily_unresolved"] += 1
            return 0

        source_series = current.series_key
        if bounds.start_ns <= self._pipeline.evicted_floor(source_series):
            self.stats["skipped_evicted"] += 1
            return 0
        children = self._pipeline.range_bars(source_series, bounds.start_ns, bounds.end_ns)
        if not children:
            return 0

        # Validate all retained children, not just the latest callback. This
        # protects against previously stored unvalidated or cross-segment bars.
        for child in children:
            child_seconds, child_nanos = divmod(child.ts_start_ns, 1_000_000_000)
            child_instant = datetime.fromtimestamp(
                child_seconds, tz=timezone.utc
            ) + timedelta(microseconds=child_nanos // 1_000)
            child_lookup = lookup_instant(calendar, child_instant)
            child_end_ns = child.ts_start_ns + 60 * 1_000_000_000
            if (
                child_lookup.trading_date != trading_date
                or child_lookup.state not in ("open", "special-session")
                or child_lookup.segment_end_ns is None
                or child_end_ns > child_lookup.segment_end_ns
            ):
                self.stats["rejected_cme_daily_child"] += 1
                return 0

        scope = source_series[:6]
        completeness = (
            "complete"
            if self._coverage is not None
            and self._coverage.status(scope, bounds.start_ns, bounds.end_ns) == "covered"
            else "partial"
        )
        try:
            derived = derive_bar(
                children, "1d", bounds.start_ns, completeness,
                bucket_policy=BUCKET_POLICY_CME_SESSION_V1,
                calendar_id=calendar_id,
                calendar_version=calendar_version,
            )
        except (InvalidOhlcvBar, IndexError):
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
                    self.stats["broadcast_callback_error"] = self.stats.get("broadcast_callback_error", 0) + 1
            return 1
        return 0

    def _rebuild_session_parents(self, current: OhlcvBar, stack: list[OhlcvBar]) -> int:
        """Derive CME weekly/monthly/quarterly bars from exact pinned session bounds."""
        # Weekly and quarterly outputs are terminal tiers in this aggregation
        # graph; they do not require another calendar lookup.
        if current.timeframe not in ("1d", "1M"):
            return 0
        assert self._session_calendars is not None
        calendar = self._session_calendars.get(current.calendar_id, current.calendar_version)
        if calendar is None:
            self.stats["skipped_cme_calendar_unresolved"] += 1
            return 0
        seconds, nanos = divmod(current.ts_start_ns, 1_000_000_000)
        instant = datetime.fromtimestamp(seconds, tz=timezone.utc) + timedelta(microseconds=nanos // 1_000)
        lookup = lookup_instant(calendar, instant)
        if lookup.trading_date is None or lookup.state not in ("open", "special-session"):
            self.stats["skipped_cme_calendar_unresolved"] += 1
            return 0
        written = 0
        for child_tf in CHILDREN.get(current.timeframe, ()):
            if child_tf not in ("1w", "1M", "3M"):
                continue
            bounds = session_bucket_bounds(calendar, lookup.trading_date, child_tf)
            if bounds is None:
                self.stats["skipped_cme_calendar_unresolved"] += 1
                continue
            written += self._rebuild_session(current.series_key, child_tf, bounds.start_ns, bounds.end_ns, stack)
        return written

    def _rebuild_session(self, parent_series, child_tf: str, start: int, end: int, stack: list[OhlcvBar]) -> int:
        """Recompute one session-aligned parent; never claim completeness without coverage."""
        if start >= end:
            self.stats["rejected"] += 1
            return 0
        if start <= self._pipeline.evicted_floor(parent_series):
            self.stats["skipped_evicted"] += 1
            return 0
        children = self._pipeline.range_bars(parent_series, start, end)
        if not children:
            return 0
        scope = parent_series[:6]
        completeness = "complete" if self._coverage is not None and self._coverage.status(scope, start, end) == "covered" else "partial"
        try:
            derived = derive_bar(children, child_tf, start, completeness)
        except (InvalidOhlcvBar, IndexError):
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
                    self.stats["broadcast_callback_error"] = self.stats.get("broadcast_callback_error", 0) + 1
            return 1
        return 0

    def _close_previous(self, parent_series, child_tf, start, stack) -> int:
        child_series = parent_series[:6] + (child_tf,) + parent_series[7:]
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
        parent_tf = parent_series[6]
        latest = self._pipeline.latest_ts(parent_series)
        if latest is None or end > bucket_end_ns(latest, parent_tf):
            return "open"
        if self._coverage is None:
            return "partial"
        if any(c.origin == ORIGIN_DERIVED and c.completeness != "complete" for c in children):
            return "partial"
        scope = parent_series[:6]
        return "complete" if self._coverage.status(scope, start, end) == "covered" else "partial"
