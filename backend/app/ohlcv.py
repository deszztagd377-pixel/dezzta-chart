"""Provider-neutral, in-memory OHLCV ingestion pipeline.

The pipeline accepts normalized bar snapshots from a future provider adapter.
It deliberately does not open provider connections, fabricate candles, or
persist data. All timestamps are integer nanoseconds at the service boundary;
prices and volume use Decimal to avoid binary-float rounding during ingestion.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Iterable, Literal

OhlcvTimeframe = Literal[
    "1s", "5s", "15s", "30s", "45s",
    "1m", "3m", "5m", "15m", "30m", "45m",
    "1h", "2h", "4h", "1d", "1w", "1M", "3M",
]

_FIXED_INTERVAL_SECONDS: dict[str, int] = {
    "1s": 1, "5s": 5, "15s": 15, "30s": 30, "45s": 45,
    "1m": 60, "3m": 180, "5m": 300, "15m": 900,
    "30m": 1800, "45m": 2700, "1h": 3600, "2h": 7200,
    "4h": 14400, "1d": 86400,
}
_SUPPORTED_TIMEFRAMES = frozenset((*_FIXED_INTERVAL_SECONDS, "1w", "1M", "3M"))
_NANOSECONDS = 1_000_000_000
_SECONDS_PER_DAY = 86_400


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
    """Return the UTC-aligned start of a supported timeframe bucket."""
    if not isinstance(timestamp_ns, int) or isinstance(timestamp_ns, bool) or timestamp_ns < 0:
        raise InvalidOhlcvBar("Bar timestamp must be a non-negative integer.")
    if timeframe not in _SUPPORTED_TIMEFRAMES:
        raise InvalidOhlcvBar(f"Unsupported OHLCV timeframe: {timeframe}")

    if timeframe in _FIXED_INTERVAL_SECONDS:
        interval_ns = _FIXED_INTERVAL_SECONDS[timeframe] * _NANOSECONDS
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


@dataclass(frozen=True, slots=True)
class OhlcvBar:
    """One normalized provider bar; prices/volume remain exact decimals."""

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

    def __post_init__(self) -> None:
        if not self.dataset.strip() or not self.raw_symbol.strip():
            raise InvalidOhlcvBar("Dataset and raw symbol are required.")
        for name in ("publisher_id", "instrument_id", "ts_start_ns",
                     "ts_event_ns", "ts_received_ns", "sequence"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise InvalidOhlcvBar(f"{name} must be a non-negative integer.")
        if self.timeframe not in _SUPPORTED_TIMEFRAMES:
            raise InvalidOhlcvBar(f"Unsupported OHLCV timeframe: {self.timeframe}")
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
    def identity(self) -> tuple[str, int, int, str, int]:
        return (
            self.dataset,
            self.publisher_id,
            self.instrument_id,
            self.timeframe,
            self.ts_start_ns,
        )


class OhlcvPipeline:
    """Atomic snapshot and timestamp/sequence-ordered in-memory bar store.

    Repeated snapshots for one bar identity replace the previous snapshot;
    they are never summed. Older event revisions cannot overwrite newer bars.
    This class is intentionally storage/provider neutral.
    """

    def __init__(self) -> None:
        self._bars: dict[tuple[str, int, int, str, int], OhlcvBar] = {}

    def replace_snapshot(self, bars: Iterable[OhlcvBar]) -> int:
        """Atomically replace all bars; the last supplied duplicate wins.

        Returns the number of duplicate snapshots superseded. Validation is
        completed before the live dictionary is replaced.
        """
        next_bars: dict[tuple[str, int, int, str, int], OhlcvBar] = {}
        duplicates = 0
        for bar in bars:
            if not isinstance(bar, OhlcvBar):
                raise InvalidOhlcvBar("Snapshot entries must be OhlcvBar instances.")
            if bar.identity in next_bars:
                duplicates += 1
            next_bars[bar.identity] = bar
        self._bars = next_bars
        return duplicates

    def upsert(self, bar: OhlcvBar) -> bool:
        """Apply a bar revision unless its event timestamp/sequence is stale."""
        if not isinstance(bar, OhlcvBar):
            raise InvalidOhlcvBar("Expected an OhlcvBar instance.")
        current = self._bars.get(bar.identity)
        if current is not None:
            incoming_order = (bar.ts_event_ns, bar.sequence)
            current_order = (current.ts_event_ns, current.sequence)
            if incoming_order <= current_order:
                return False
        self._bars[bar.identity] = bar
        return True

    def list_bars(
        self,
        *,
        dataset: str | None = None,
        publisher_id: int | None = None,
        instrument_id: int | None = None,
        timeframe: str | None = None,
    ) -> list[OhlcvBar]:
        """Return a stable chronological copy, optionally filtered by identity."""
        selected = [
            bar for bar in self._bars.values()
            if (dataset is None or bar.dataset == dataset)
            and (publisher_id is None or bar.publisher_id == publisher_id)
            and (instrument_id is None or bar.instrument_id == instrument_id)
            and (timeframe is None or bar.timeframe == timeframe)
        ]
        return sorted(
            selected,
            key=lambda bar: (
                bar.ts_start_ns, bar.dataset, bar.publisher_id, bar.instrument_id
            ),
        )

    def clear(self) -> None:
        """Clear in-memory bars; no external storage is affected."""
        self._bars.clear()
