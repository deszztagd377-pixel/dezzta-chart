"""Bounded per-instrument observation telemetry.

This tracker reports when a valid live OHLCV record was last observed. It
intentionally does not infer that a quiet instrument is stale: no-trade
intervals are normal for OHLCV feeds. Provider connection health is reported
separately by ProviderManager.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable
import time


class InstrumentObservationTracker:
    """Keep bounded last-observation telemetry keyed by provider instrument."""

    def __init__(
        self,
        *,
        max_instruments: int = 2048,
        monotonic_ns: Callable[[], int] = time.perf_counter_ns,
    ) -> None:
        if not isinstance(max_instruments, int) or isinstance(max_instruments, bool) or max_instruments < 1:
            raise ValueError("max_instruments must be a positive integer")
        self._max = max_instruments
        self._monotonic = monotonic_ns
        self._items: OrderedDict[tuple[str, int, int, str], dict[str, int]] = OrderedDict()
        self.evicted_count = 0

    def observe(
        self,
        *,
        dataset: str,
        publisher_id: int,
        instrument_id: int,
        raw_symbol: str,
        event_ns: int,
        received_ns: int,
        monotonic_received_ns: int | None = None,
    ) -> None:
        key = (dataset, publisher_id, instrument_id, raw_symbol)
        observed_mono = self._monotonic() if monotonic_received_ns is None else monotonic_received_ns
        current = self._items.get(key)
        if current is None:
            current = {
                "last_event_ns": event_ns,
                "last_received_ns": received_ns,
                "last_received_monotonic_ns": observed_mono,
                "accepted_records": 1,
            }
            self._items[key] = current
        else:
            # Out-of-order event-time records may arrive late. Observation time
            # still advances, while event-time high-water mark never regresses.
            current["last_event_ns"] = max(current["last_event_ns"], event_ns)
            current["last_received_ns"] = max(current["last_received_ns"], received_ns)
            current["last_received_monotonic_ns"] = max(
                current["last_received_monotonic_ns"], observed_mono
            )
            current["accepted_records"] += 1
            self._items.move_to_end(key)
        while len(self._items) > self._max:
            self._items.popitem(last=False)
            self.evicted_count += 1

    def status(self) -> dict[str, Any]:
        now = self._monotonic()
        instruments = []
        for (dataset, publisher_id, instrument_id, raw_symbol), item in self._items.items():
            age_ns = max(0, now - item["last_received_monotonic_ns"])
            instruments.append({
                "dataset": dataset,
                "publisher_id": publisher_id,
                "instrument_id": instrument_id,
                "raw_symbol": raw_symbol,
                "last_event_ts_ns": str(item["last_event_ns"]),
                "last_receive_ts_ns": str(item["last_received_ns"]),
                "last_observed_age_ms": round(age_ns / 1_000_000, 3),
                "accepted_live_records": item["accepted_records"],
                "health": "observed",
            })
        return {
            "tracked_instruments": len(self._items),
            "capacity": self._max,
            "evicted_instrument_counters": self.evicted_count,
            "staleness_classification": "not_inferred_from_OHLCV_silence",
            "quiet_instrument_note": "No trade/no OHLCV update is not proof of a disconnected feed.",
            "instruments": instruments,
        }
