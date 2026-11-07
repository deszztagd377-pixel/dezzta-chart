"""Provider-neutral, in-memory OHLCV ingestion pipeline.

The pipeline accepts normalized bars from provider adapters or the derived-bar
aggregator. It deliberately does not open provider connections, fabricate
candles, or persist data. Timestamps are integer nanoseconds at the service
boundary; prices and volume use Decimal to avoid binary-float rounding.

Threading: the pipeline is NOT thread-safe. Exactly one writer (the asyncio
event loop) may mutate it; readers must run on the same loop.

Ordering: ``OhlcvBar.sequence`` is a LOCAL ingest sequence assigned by this
backend (``sequence_origin == "local"``). It is never a provider sequence.
"""
from __future__ import annotations

from bisect import bisect_left, insort
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Iterable, Literal, Mapping

OhlcvTimeframe = Literal[
    "1s", "5s", "15s", "30s", "45s",
    "1m", "3m", "5m", "15m", "30m", "45m",
    "1h", "2h", "4h", "1d", "1w", "1M", "3M",
]

FIXED_INTERVAL_SECONDS: dict[str, int] = {
    "1s": 1, "5s": 5, "15s": 15, "30s": 30, "45s": 45,
    "1m": 60, "3m": 180, "5m": 300, "15m": 900,
    "30m": 1800, "45m": 2700, "1h": 3600, "2h": 7200,
    "4h": 14400, "1d": 86400,
}
_FIXED_INTERVAL_SECONDS = FIXED_INTERVAL_SECONDS  # backwards-compatible alias
SUPPORTED_TIMEFRAMES = frozenset((*FIXED_INTERVAL_SECONDS, "1w", "1M", "3M"))
_SUPPORTED_TIMEFRAMES = SUPPORTED_TIMEFRAMES
_NANOSECONDS = 1_000_000_000
_SECONDS_PER_DAY = 86_400

ORIGIN_PROVIDER = "provider"
ORIGIN_DERIVED = "derived"
SERIES_CONTRACT = "contract"
SERIES_CONTINUOUS = "continuous"
_ORIGINS = frozenset((ORIGIN_PROVIDER, ORIGIN_DERIVED))
_SERIES_TYPES = frozenset((SERIES_CONTRACT, SERIES_CONTINUOUS))
_SEQUENCE_ORIGINS = frozenset(("local", "provider"))
COMPLETENESS_VALUES = frozenset(("unknown", "open", "partial", "complete"))

# Per-series, per-timeframe maximum number of retained bars. Configurable.
DEFAULT_RETENTION: dict[str, int] = {
    **{tf: 20_000 for tf in FIXED_INTERVAL_SECONDS if tf != "1d"},
    "1d": 10_000, "1w": 2_000, "1M": 600, "3M": 200,
}

# Lower bound on retention per tier: a tier must keep at least as many bars as
# one bucket of the tier it feeds can contain (e.g. 1d feeds 1M: up to 31 bars),
# otherwise a derived bar could be recomputed from evicted children and shrink.
MIN_RETENTION: dict[str, int] = {
    "1s": 5, "5s": 3, "15s": 3, "30s": 2, "45s": 1, "1m": 5, "3m": 1, "5m": 3,
    "15m": 3, "30m": 2, "45m": 1, "1h": 2, "2h": 2, "4h": 6, "1d": 31,
    "1w": 1, "1M": 3, "3M": 1,
}

BUCKET_POLICY_UTC_LEGACY = "UTC_LEGACY"
BUCKET_POLICY_UTC_FIXED_V1 = "UTC_FIXED_V1"
# Structural identity only. Session-aware aggregation remains disabled until a
# caller supplies a verified, version-matched exchange calendar.
BUCKET_POLICY_CME_SESSION_V1 = "CME_SESSION_V1"
_SESSION_TIMEFRAMES = frozenset(("1d", "1w", "1M", "3M"))
SUPPORTED_BUCKET_POLICIES = frozenset((
    BUCKET_POLICY_UTC_LEGACY,
    BUCKET_POLICY_UTC_FIXED_V1,
    BUCKET_POLICY_CME_SESSION_V1,
))


def bucket_policy_for_timeframe(timeframe: str) -> str:
    """Select bucket identity for newly ingested OHLCV records.

    Intraday bars use UTC_FIXED_V1. Daily and larger bars retain UTC_LEGACY
    until an authoritative exchange-session calendar is available. Existing
    persisted rows are not rewritten by this selector.
    """
    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise InvalidOhlcvBar(f"Unsupported OHLCV timeframe: {timeframe}")
    if timeframe in FIXED_INTERVAL_SECONDS and timeframe != "1d":
        return BUCKET_POLICY_UTC_FIXED_V1
    return BUCKET_POLICY_UTC_LEGACY

SeriesKey = tuple[str, str, int, int, str, str, str, str, str, str]
Identity = tuple[str, str, int, int, str, str, int, str, str, str]


class InvalidOhlcvBar(ValueError):
    """Raised when an incoming OHLCV bar violates the canonical contract."""


def _decimal(value: Decimal | int | str, field: str) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise InvalidOhlcvBar(f"{field} must be a valid decimal.") from exc
    if not result.is_finite():
        raise InvalidOhlcvBar(f"{field} must be finite.")
    return result


def bucket_start_ns(timestamp_ns: int, timeframe: str) -> int:
    """Return the UTC-aligned start of a supported timeframe bucket.

    Session policy (UTC only): fixed intervals are multiples of the interval
    since the Unix epoch; 1d starts 00:00 UTC; 1w starts Monday 00:00 UTC;
    1M/3M start on UTC calendar month / quarter (Jan, Apr, Jul, Oct) boundaries.
    Exchange trading-day sessions (e.g. CME 17:00 CT) are NOT applied.
    """
    if not isinstance(timestamp_ns, int) or isinstance(timestamp_ns, bool) or timestamp_ns < 0:
        raise InvalidOhlcvBar("Bar timestamp must be a non-negative integer.")
    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise InvalidOhlcvBar(f"Unsupported OHLCV timeframe: {timeframe}")

    if timeframe in FIXED_INTERVAL_SECONDS:
        interval_ns = FIXED_INTERVAL_SECONDS[timeframe] * _NANOSECONDS
        return (timestamp_ns // interval_ns) * interval_ns

    seconds = timestamp_ns // _NANOSECONDS
    day_start = (seconds // _SECONDS_PER_DAY) * _SECONDS_PER_DAY
    if timeframe == "1w":
        weekday = datetime.fromtimestamp(day_start, tz=timezone.utc).weekday()
        return (day_start - weekday * _SECONDS_PER_DAY) * _NANOSECONDS

    date = datetime.fromtimestamp(seconds, tz=timezone.utc)
    month_interval = 1 if timeframe == "1M" else 3
    aligned_month = ((date.month - 1) // month_interval) * month_interval + 1
    month_start = datetime(date.year, aligned_month, 1, tzinfo=timezone.utc)
    return int(month_start.timestamp()) * _NANOSECONDS


def bucket_end_ns(start_ns: int, timeframe: str) -> int:
    """Exclusive end of the bucket that starts at ``start_ns`` (must be aligned)."""
    if bucket_start_ns(start_ns, timeframe) != start_ns:
        raise InvalidOhlcvBar("Bucket start is not aligned to its timeframe.")
    if timeframe in FIXED_INTERVAL_SECONDS:
        return start_ns + FIXED_INTERVAL_SECONDS[timeframe] * _NANOSECONDS
    if timeframe == "1w":
        return start_ns + 7 * _SECONDS_PER_DAY * _NANOSECONDS
    date = datetime.fromtimestamp(start_ns // _NANOSECONDS, tz=timezone.utc)
    step = 1 if timeframe == "1M" else 3
    month_index = date.month - 1 + step
    nxt = datetime(date.year + month_index // 12, month_index % 12 + 1, 1, tzinfo=timezone.utc)
    return int(nxt.timestamp()) * _NANOSECONDS


@dataclass(frozen=True, slots=True)
class OhlcvBar:
    """One normalized bar; prices/volume remain exact decimals.

    ``sequence`` is a local ingest sequence (see module docstring). The
    trailing fields have defaults so pre-existing constructors keep working.
    """

    dataset: str
    publisher_id: int
    instrument_id: int
    raw_symbol: str
    timeframe: OhlcvTimeframe
    ts_start_ns: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    ts_event_ns: int
    ts_received_ns: int
    sequence: int
    sequence_origin: str = "local"
    provider: str = "databento"
    series_type: str = SERIES_CONTRACT
    origin: str = ORIGIN_PROVIDER
    completeness: str = "unknown"
    # Databento gateway-send timestamp; None for historical/derived or when absent.
    ts_provider_out_ns: int | None = None
    # Bucket identity is explicit; legacy constructors remain UTC_LEGACY.
    bucket_policy: str = BUCKET_POLICY_UTC_LEGACY
    calendar_id: str = ""
    calendar_version: str = ""

    def __post_init__(self) -> None:
        if not self.dataset.strip() or not self.raw_symbol.strip():
            raise InvalidOhlcvBar("Dataset and raw symbol are required.")
        if not self.provider.strip():
            raise InvalidOhlcvBar("Provider is required.")
        for name in ("publisher_id", "instrument_id", "ts_start_ns",
                     "ts_event_ns", "ts_received_ns", "sequence"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise InvalidOhlcvBar(f"{name} must be a non-negative integer.")
        if self.timeframe not in SUPPORTED_TIMEFRAMES:
            raise InvalidOhlcvBar(f"Unsupported OHLCV timeframe: {self.timeframe}")
        if self.sequence_origin not in _SEQUENCE_ORIGINS:
            raise InvalidOhlcvBar("Unsupported sequence_origin.")
        if self.series_type not in _SERIES_TYPES:
            raise InvalidOhlcvBar("Unsupported series_type.")
        if self.origin not in _ORIGINS:
            raise InvalidOhlcvBar("Unsupported bar origin.")
        if self.completeness not in COMPLETENESS_VALUES:
            raise InvalidOhlcvBar("Unsupported completeness value.")
        if self.bucket_policy not in SUPPORTED_BUCKET_POLICIES:
            raise InvalidOhlcvBar("Unsupported bucket policy.")
        if self.bucket_policy == BUCKET_POLICY_CME_SESSION_V1:
            if self.timeframe not in _SESSION_TIMEFRAMES:
                raise InvalidOhlcvBar("CME session bucket policy is only valid for 1d, 1w, 1M, and 3M.")
            if not self.calendar_id.strip() or not self.calendar_version.strip():
                raise InvalidOhlcvBar("CME session bars require calendar_id and calendar_version.")
            # Session starts are exchange-defined instants (e.g. 17:00 Chicago),
            # not UTC-midnight/fixed-interval boundaries. The authoritative
            # calendar resolver must validate their actual bounds before ingest.
        else:
            if self.calendar_id or self.calendar_version:
                raise InvalidOhlcvBar("UTC bucket policies must not carry exchange calendar metadata.")
            if bucket_start_ns(self.ts_start_ns, self.timeframe) != self.ts_start_ns:
                raise InvalidOhlcvBar("Bar start timestamp is not aligned to its timeframe.")
        if self.ts_provider_out_ns is not None and (
            not isinstance(self.ts_provider_out_ns, int)
            or isinstance(self.ts_provider_out_ns, bool)
            or self.ts_provider_out_ns < 0
        ):
            raise InvalidOhlcvBar("ts_provider_out_ns must be a non-negative integer or None.")
        if bucket_start_ns(self.ts_start_ns, self.timeframe) != self.ts_start_ns:
            raise InvalidOhlcvBar("Bar start timestamp is not aligned to its timeframe.")

        for name in ("open", "high", "low", "close", "volume"):
            object.__setattr__(self, name, _decimal(getattr(self, name), name))
        if self.volume < 0:
            raise InvalidOhlcvBar("Volume cannot be negative.")
        if self.high < self.low:
            raise InvalidOhlcvBar("High cannot be lower than low.")
        if self.high < max(self.open, self.close):
            raise InvalidOhlcvBar("High must contain open and close.")
        if self.low > min(self.open, self.close):
            raise InvalidOhlcvBar("Low must contain open and close.")

    @property
    def ingest_seq(self) -> int:
        """Alias of the local ingest sequence stored in ``sequence``."""
        return self.sequence

    @property
    def identity(self) -> Identity:
        """Bar slot identity. instrument_id is never assumed globally unique."""
        return (
            self.provider, self.dataset, self.publisher_id, self.instrument_id,
            self.series_type, self.timeframe, self.ts_start_ns,
            self.bucket_policy, self.calendar_id, self.calendar_version,
        )

    @property
    def series_key(self) -> SeriesKey:
        return (
            self.provider, self.dataset, self.publisher_id, self.instrument_id,
            self.series_type, self.raw_symbol, self.timeframe,
            self.bucket_policy, self.calendar_id, self.calendar_version,
        )


def _identity_for(series: SeriesKey, ts_start_ns: int) -> Identity:
    (provider, dataset, publisher_id, instrument_id, series_type, _symbol,
     timeframe, bucket_policy, calendar_id, calendar_version) = series
    return (provider, dataset, publisher_id, instrument_id, series_type,
            timeframe, ts_start_ns, bucket_policy, calendar_id, calendar_version)


def _same_payload(a: OhlcvBar, b: OhlcvBar) -> bool:
    return (
        a.open == b.open and a.high == b.high and a.low == b.low
        and a.close == b.close and a.volume == b.volume
        and a.origin == b.origin and a.completeness == b.completeness
    )


class OhlcvPipeline:
    """Atomic snapshot and ordered in-memory bar store with bounded retention.

    Repeated snapshots for one bar identity replace the previous snapshot;
    they are never summed. Older revisions cannot overwrite newer bars.
    Provider-origin bars always take precedence over derived bars with the
    same identity. Evictions are counted, never silent.
    """

    def __init__(self, retention: Mapping[str, int] | None = None) -> None:
        self._retention = dict(DEFAULT_RETENTION)
        for timeframe, cap in (retention or {}).items():
            if timeframe not in SUPPORTED_TIMEFRAMES or not isinstance(cap, int) or cap < 1:
                raise ValueError(f"Invalid retention for {timeframe!r}.")
            if cap < MIN_RETENTION[timeframe]:
                raise ValueError(
                    f"Retention for {timeframe} must be at least {MIN_RETENTION[timeframe]}: "
                    "a bucket's children must fit in retention or aggregation would shrink."
                )
            self._retention[timeframe] = cap
        self._bars: dict[Identity, OhlcvBar] = {}
        self._series: dict[SeriesKey, list[int]] = {}
        self._floor: dict[SeriesKey, int] = {}
        self._stats: dict[str, int] = {
            "evicted": 0, "stale": 0, "duplicate": 0, "symbol_conflict": 0,
            "provider_precedence": 0, "expired": 0,
        }

    # ------------------------------------------------------------------ write
    def apply(self, bar: OhlcvBar) -> str:
        """Apply one bar. Returns inserted|replaced|duplicate|stale|conflict|
        provider_precedence|expired. Only inserted/replaced mutate the store."""
        if not isinstance(bar, OhlcvBar):
            raise InvalidOhlcvBar("Expected an OhlcvBar instance.")
        identity = bar.identity
        series = bar.series_key
        current = self._bars.get(identity)
        if current is not None:
            if current.raw_symbol != bar.raw_symbol:
                self._stats["symbol_conflict"] += 1
                return "conflict"
            provider_upgrade = current.origin != ORIGIN_PROVIDER and bar.origin == ORIGIN_PROVIDER
            if current.origin == ORIGIN_PROVIDER and bar.origin != ORIGIN_PROVIDER:
                self._stats["provider_precedence"] += 1
                return "provider_precedence"
            if not provider_upgrade:
                if _same_payload(current, bar):
                    self._stats["duplicate"] += 1
                    return "duplicate"
                incoming_order = (bar.ts_event_ns, bar.sequence)
                current_order = (current.ts_event_ns, current.sequence)
                # Derived bars may be re-issued with the same order key when only
                # their completeness label changed (open -> complete/partial).
                if incoming_order < current_order or (
                    incoming_order == current_order and bar.origin != ORIGIN_DERIVED
                ):
                    self._stats["stale"] += 1
                    return "stale"
            self._bars[identity] = bar
            return "replaced"

        timestamps = self._series.setdefault(series, [])
        cap = self._retention[bar.timeframe]
        if bar.ts_start_ns <= self._floor.get(series, -1) or (
            len(timestamps) >= cap and bar.ts_start_ns < timestamps[0]
        ):
            self._stats["expired"] += 1
            if not timestamps:
                del self._series[series]
            return "expired"
        self._bars[identity] = bar
        insort(timestamps, bar.ts_start_ns)
        while len(timestamps) > cap:
            oldest = timestamps.pop(0)
            del self._bars[_identity_for(series, oldest)]
            self._floor[series] = max(self._floor.get(series, -1), oldest)
            self._stats["evicted"] += 1
        return "inserted"

    def upsert(self, bar: OhlcvBar) -> bool:
        """Apply a bar revision unless stale/duplicate/conflicting."""
        return self.apply(bar) in ("inserted", "replaced")

    def replace_snapshot(self, bars: Iterable[OhlcvBar]) -> int:
        """Atomically replace all bars; the last supplied duplicate wins.

        Returns the number of duplicate snapshots superseded. Validation and
        retention are completed before the live structures are replaced.
        """
        next_bars: dict[Identity, OhlcvBar] = {}
        duplicates = 0
        for bar in bars:
            if not isinstance(bar, OhlcvBar):
                raise InvalidOhlcvBar("Snapshot entries must be OhlcvBar instances.")
            existing = next_bars.get(bar.identity)
            if existing is not None:
                if existing.raw_symbol != bar.raw_symbol:
                    raise InvalidOhlcvBar(
                        "Snapshot contains conflicting raw symbols for one instrument identity."
                    )
                duplicates += 1
            next_bars[bar.identity] = bar
        grouped: dict[SeriesKey, list[int]] = {}
        for bar in next_bars.values():
            grouped.setdefault(bar.series_key, []).append(bar.ts_start_ns)
        next_series: dict[SeriesKey, list[int]] = {}
        next_floor: dict[SeriesKey, int] = {}
        evicted = 0
        for series, timestamps in grouped.items():
            timestamps.sort()
            cap = self._retention[series[6]]
            if len(timestamps) > cap:
                dropped, timestamps = timestamps[:-cap], timestamps[-cap:]
                for ts in dropped:
                    del next_bars[_identity_for(series, ts)]
                next_floor[series] = dropped[-1]
                evicted += len(dropped)
            next_series[series] = timestamps
        self._bars, self._series, self._floor = next_bars, next_series, next_floor
        self._stats["evicted"] += evicted
        return duplicates

    def clear(self) -> None:
        """Clear in-memory bars; no external storage is affected."""
        self._bars.clear()
        self._series.clear()
        self._floor.clear()

    # ------------------------------------------------------------------- read
    def evicted_floor(self, series: SeriesKey) -> int:
        """Highest ts_start evicted from the series (-1 if none). Bars at or
        below this value may no longer be fully available."""
        return self._floor.get(series, -1)

    def latest_ts(self, series: SeriesKey) -> int | None:
        timestamps = self._series.get(series)
        return timestamps[-1] if timestamps else None

    def range_bars(self, series: SeriesKey, start_ns: int, end_ns: int) -> list[OhlcvBar]:
        """Bars of one series with start_ns <= ts_start < end_ns, chronological."""
        timestamps = self._series.get(series, [])
        lo = bisect_left(timestamps, start_ns)
        hi = bisect_left(timestamps, end_ns)
        return [self._bars[_identity_for(series, ts)] for ts in timestamps[lo:hi]]

    def previous_bar(self, series: SeriesKey, before_ns: int) -> OhlcvBar | None:
        timestamps = self._series.get(series, [])
        index = bisect_left(timestamps, before_ns) - 1
        return self._bars[_identity_for(series, timestamps[index])] if index >= 0 else None

    def query(
        self,
        *,
        dataset: str | None = None,
        publisher_id: int | None = None,
        instrument_id: int | None = None,
        timeframe: str | None = None,
        provider: str | None = None,
        raw_symbol: str | None = None,
        series_type: str | None = None,
        bucket_policy: str | None = None,
        calendar_id: str | None = None,
        calendar_version: str | None = None,
        start_ns: int | None = None,
        end_ns: int | None = None,
        limit: int | None = None,
    ) -> tuple[list[OhlcvBar], int]:
        """Return (bars, total_matching). With ``limit`` the NEWEST ``limit``
        matching bars are returned in chronological order."""
        if limit is not None and limit < 1:
            raise ValueError("limit must be positive.")
        selected: list[OhlcvBar] = []
        total = 0
        for series, timestamps in self._series.items():
            (s_provider, s_dataset, s_pub, s_inst, s_type, s_symbol, s_tf,
             s_policy, s_calendar, s_calendar_version) = series
            if (
                (provider is not None and s_provider != provider)
                or (dataset is not None and s_dataset != dataset)
                or (publisher_id is not None and s_pub != publisher_id)
                or (instrument_id is not None and s_inst != instrument_id)
                or (series_type is not None and s_type != series_type)
                or (raw_symbol is not None and s_symbol != raw_symbol)
                or (timeframe is not None and s_tf != timeframe)
                or (bucket_policy is not None and s_policy != bucket_policy)
                or (calendar_id is not None and s_calendar != calendar_id)
                or (calendar_version is not None and s_calendar_version != calendar_version)
            ):
                continue
            lo = 0 if start_ns is None else bisect_left(timestamps, start_ns)
            hi = len(timestamps) if end_ns is None else bisect_left(timestamps, end_ns)
            if hi <= lo:
                continue
            total += hi - lo
            if limit is not None:
                lo = max(lo, hi - limit)
            selected.extend(self._bars[_identity_for(series, ts)] for ts in timestamps[lo:hi])
        selected.sort(key=lambda b: (
            b.ts_start_ns, b.provider, b.dataset, b.publisher_id, b.instrument_id,
            b.series_type, b.raw_symbol, b.timeframe, b.bucket_policy,
            b.calendar_id, b.calendar_version,
        ))
        if limit is not None and len(selected) > limit:
            selected = selected[-limit:]
        return selected, total

    def list_bars(
        self,
        *,
        dataset: str | None = None,
        publisher_id: int | None = None,
        instrument_id: int | None = None,
        timeframe: str | None = None,
        provider: str | None = None,
        raw_symbol: str | None = None,
        series_type: str | None = None,
        bucket_policy: str | None = None,
        calendar_id: str | None = None,
        calendar_version: str | None = None,
        start_ns: int | None = None,
        end_ns: int | None = None,
        limit: int | None = None,
    ) -> list[OhlcvBar]:
        """Return a stable chronological copy, optionally filtered."""
        return self.query(
            dataset=dataset, publisher_id=publisher_id, instrument_id=instrument_id,
            timeframe=timeframe, provider=provider, raw_symbol=raw_symbol,
            series_type=series_type, bucket_policy=bucket_policy,
            calendar_id=calendar_id, calendar_version=calendar_version,
            start_ns=start_ns, end_ns=end_ns, limit=limit,
        )[0]

    def stats(self) -> dict[str, int]:
        return {"bars": len(self._bars), "series": len(self._series), **self._stats}


def decimal_to_string(value: Decimal) -> str:
    """Plain (non-scientific) decimal string for JSON transport."""
    return format(value, "f")
