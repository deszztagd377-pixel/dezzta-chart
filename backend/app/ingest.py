"""Bounded, single-writer OHLCV ingestion service.

Provider callbacks may run on SDK threads. They only call ``offer`` (thread
safe, non-blocking) which puts the record in a bounded buffer. All pipeline /
aggregator / coverage mutation happens on the asyncio event loop in
``process_pending`` (single writer). When the buffer is full the record is NOT
silently dropped: the overflow is counted, a coverage gap is carved out, and
the service reports the degraded reason ``ingest_overflow``.
"""
from __future__ import annotations

import asyncio
import itertools
import math
import threading
import time
from collections import deque
from typing import Any, Callable, Iterable

from app.aggregation import Aggregator
from app.coverage import CoverageTracker
from app.databento_ohlcv import RecordRejected, record_to_bar
from app.freshness import InstrumentObservationTracker
from app.ohlcv import OhlcvBar, OhlcvPipeline
from app.symbology import InstrumentResolver
from app.ohlcv_store import SQLiteOhlcvStore

_NS = 1_000_000_000


class BoundedBuffer:
    """Thread-safe FIFO with an explicit capacity and visible overflow."""

    def __init__(self, maxsize: int) -> None:
        if maxsize < 1:
            raise ValueError("maxsize must be positive")
        self._max = maxsize
        self._items: deque[Any] = deque()
        self._lock = threading.Lock()
        # Keep overflow metadata bounded even if malformed/provider input
        # contains an unbounded number of distinct instrument identifiers.
        self._max_overflow_scopes = min(maxsize, 1024)
        self._overflows: dict[tuple[int, int] | None, tuple[int, int]] = {}
        self._overflow_scoped_count = 0
        self.overflow_count = 0
        self.wakeup: Callable[[], None] | None = None

    def __len__(self) -> int:
        return len(self._items)

    def offer(self, item: Any, ts_hint: int | None, recv_ns: int, instrument_hint: tuple[int, int] | None = None) -> bool:
        with self._lock:
            if len(self._items) >= self._max:
                self.overflow_count += 1
                point = ts_hint if ts_hint is not None else recv_ns
                key = instrument_hint
                if key not in self._overflows and key is not None:
                    if self._overflow_scoped_count >= self._max_overflow_scopes:
                        # Preserve a conservative, explicitly unscoped range
                        # rather than allowing per-instrument metadata to grow
                        # without bound or assigning a gap to the wrong symbol.
                        key = None
                previous = self._overflows.get(key)
                if previous is None and key is not None:
                    self._overflow_scoped_count += 1
                self._overflows[key] = (
                    point if previous is None else min(previous[0], point),
                    point if previous is None else max(previous[1], point),
                )
                return False
            was_empty = not self._items
            self._items.append(item)
        if was_empty and self.wakeup is not None:
            try:
                self.wakeup()
            except RuntimeError:  # event loop already closed during shutdown
                pass
        return True

    def drain(self, limit: int) -> list[Any]:
        with self._lock:
            count = min(limit, len(self._items))
            return [self._items.popleft() for _ in range(count)]

    def take_overflows(self) -> list[tuple[tuple[int, int] | None, int, int]]:
        with self._lock:
            taken = [(key, bounds[0], bounds[1]) for key, bounds in self._overflows.items()]
            self._overflows.clear()
            self._overflow_scoped_count = 0
            return taken


class OhlcvIngestionService:
    def __init__(
        self,
        *,
        pipeline: OhlcvPipeline,
        resolver: InstrumentResolver,
        coverage: CoverageTracker,
        provider: str = "databento",
        dataset: str = "GLBX.MDP3",
        queue_max: int = 10_000,
        batch_size: int = 500,
        clock_ns: Callable[[], int] = time.time_ns,
        monotonic_ns: Callable[[], int] = time.perf_counter_ns,
        on_bar_applied: Callable[[OhlcvBar], None] | None = None,
        persistence: SQLiteOhlcvStore | None = None,
        bar_validator: Callable[[OhlcvBar], Any] | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.resolver = resolver
        self.bar_validator = bar_validator
        self.coverage = coverage
        self._on_bar_applied = on_bar_applied
        self._live_bar_applied_callbacks: set[Callable[[OhlcvBar], None]] = set()
        self._provider_callback_error_lock = threading.Lock()
        self._provider_callback_errors = 0
        self.persistence = persistence
        self.aggregator = Aggregator(
            pipeline, coverage, on_derived_bar=self._notify_bar_applied,
            before_derived_apply=self._persist_derived,
        )
        if self.persistence is not None:
            self.pipeline.replace_snapshot(self.persistence.load_bars())
        self.provider = provider
        self.dataset = dataset
        self._buffer = BoundedBuffer(queue_max)
        # Durable journal entries are replayed before new overflow ranges.
        self._overflow_journal = (
            coverage if all(callable(getattr(coverage, name, None)) for name in
                ("journal_overflow", "pending_overflows", "resolve_overflow"))
            else None
        )
        self._pending_overflow_gaps: list[tuple[int | None, tuple[int, int] | None, int, int]] = []
        if self._overflow_journal is not None:
            self._pending_overflow_gaps.extend(
                (int(item["id"]), item["instrument_hint"],
                 int(item["start_ns"]), int(item["end_ns"]))
                for item in self._overflow_journal.pending_overflows()
            )
        self._batch = batch_size
        self._clock = clock_ns
        self._monotonic = monotonic_ns
        self._queue_delay_samples_ms: deque[float] = deque(maxlen=256)
        self._processing_samples_ms: deque[float] = deque(maxlen=256)
        self._callback_to_apply_samples_ms: deque[float] = deque(maxlen=256)
        self._clock_skew_samples = 0
        self.observations = InstrumentObservationTracker(monotonic_ns=self._monotonic)
        sequence_start = (
            self.persistence.max_local_sequence() + 1
            if self.persistence is not None else 1
        )
        self._sequence = itertools.count(sequence_start)
        self._event: asyncio.Event | None = None
        self._session_start: int | None = None
        self.counters: dict[str, int] = {}
        self.degraded_reasons: set[str] = set()
        if self._pending_overflow_gaps:
            self.degraded_reasons.add("ingest_overflow")
        self.last_event_ns: int | None = None
        self.last_receive_ns: int | None = None

    # ----------------------------------------------------------- thread-safe
    def offer(self, record: Any, schema: str) -> bool:
        """Called from provider callbacks (any thread). Never blocks, never raises."""
        recv_ns = self._clock()
        recv_monotonic_ns = self._monotonic()
        hint = getattr(record, "ts_event", None)
        hint = hint if isinstance(hint, int) and not isinstance(hint, bool) and hint >= 0 else None
        publisher_id = getattr(record, "publisher_id", None)
        instrument_id = getattr(record, "instrument_id", None)
        valid_ids = all(isinstance(v, int) and not isinstance(v, bool) and v >= 0
                        for v in (publisher_id, instrument_id))
        instrument_hint = (publisher_id, instrument_id) if valid_ids else None
        return self._buffer.offer((record, schema, recv_ns, recv_monotonic_ns), hint, recv_ns, instrument_hint)

    def add_live_bar_applied_callback(self, callback: Callable[[OhlcvBar], None]) -> None:
        """Observe only live bars accepted by persistence and the pipeline."""
        self._live_bar_applied_callbacks.add(callback)

    def remove_live_bar_applied_callback(self, callback: Callable[[OhlcvBar], None]) -> None:
        """Remove a live-bar observer when its provider session ends."""
        self._live_bar_applied_callbacks.discard(callback)

    def note_provider_callback_error(self) -> None:
        """Count an unexpected SDK callback failure without mutating loop state."""
        with self._provider_callback_error_lock:
            self._provider_callback_errors += 1

    # ------------------------------------------------------------ loop-side
    def attach_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._event = asyncio.Event()
        event = self._event
        self._buffer.wakeup = lambda: loop.call_soon_threadsafe(event.set)

    async def run(self) -> None:
        """Consumer loop (single writer). Cancel to stop."""
        if self._event is None:
            raise RuntimeError("attach_loop() must be called first")
        retry_delay = 0.25
        max_retry_delay = 5.0
        while True:
            if self._pending_overflow_gaps:
                # Wait for either fresh provider work or the next retry deadline.
                # Provider events interrupt the backoff so ingestion is not held
                # behind a coverage-store outage.
                try:
                    await asyncio.wait_for(
                        self._event.wait(), timeout=retry_delay
                    )
                except asyncio.TimeoutError:
                    pass
            else:
                await self._event.wait()
            self._event.clear()
            while self.process_pending():
                await asyncio.sleep(0)  # yield to the loop between batches
            if self._pending_overflow_gaps:
                # Repeated SQLite failures must not cause a tight retry loop.
                retry_delay = min(retry_delay * 2, max_retry_delay)
            else:
                retry_delay = 0.25

    def process_pending(self) -> int:
        """Apply buffered records (loop thread only). Returns records handled."""
        for instrument_hint, first_ns, last_ns in self._buffer.take_overflows():
            self._pending_overflow_gaps.append((None, instrument_hint, first_ns, last_ns))
        if self._pending_overflow_gaps:
            self.degraded_reasons.add("ingest_overflow")
        pending: list[tuple[int | None, tuple[int, int] | None, int, int]] = []
        has_unscoped_pending = False
        for journal_id, instrument_hint, first_ns, last_ns in self._pending_overflow_gaps:
            try:
                if self._overflow_journal is not None:
                    if journal_id is None:
                        journal_id = self._overflow_journal.journal_overflow(
                            instrument_hint, first_ns, last_ns, self._clock()
                        )
                    # Keep the durable row if the instrument cannot yet be resolved.
                    if not self._note_overflow(instrument_hint, first_ns, last_ns):
                        has_unscoped_pending = True
                        pending.append((journal_id, instrument_hint, first_ns, last_ns))
                        continue
                    self._overflow_journal.resolve_overflow(journal_id)
                else:
                    if not self._note_overflow(instrument_hint, first_ns, last_ns):
                        has_unscoped_pending = True
                        pending.append((None, instrument_hint, first_ns, last_ns))
            except Exception:
                # Preserve the unscoped warning only when identity is still
                # unresolved; a coverage write failure after successful mapping
                # is a persistence failure, not an identity failure.
                if instrument_hint is None:
                    has_unscoped_pending = True
                else:
                    try:
                        mapping = self.resolver.resolve(
                            self.provider, self.dataset,
                            instrument_hint[0], instrument_hint[1], first_ns,
                        )
                        has_unscoped_pending = has_unscoped_pending or mapping is None
                    except Exception:
                        has_unscoped_pending = True
                # Keep both the in-memory item and durable journal for retry.
                self._count("coverage_persistence_error")
                self.degraded_reasons.add("coverage_persistence_error")
                pending.append((journal_id, instrument_hint, first_ns, last_ns))
        self._pending_overflow_gaps = pending
        if not has_unscoped_pending:
            self.degraded_reasons.discard("coverage_gap_unscoped")
        if not pending:
            self.degraded_reasons.discard("coverage_persistence_error")
        items = self._buffer.drain(self._batch)
        for record, schema, recv_ns, recv_monotonic_ns in items:
            self._process(record, schema, recv_ns, recv_monotonic_ns, live=True)
        return len(items)

    def ingest_batch(self, records: Iterable[Any], schema: str, *, live: bool = False) -> int:
        """Apply records directly (historical backfill; loop thread only)."""
        count = 0
        for record in records:
            self._process(record, schema, self._clock(), self._monotonic(), live=live)
            count += 1
        return count

    def end_live_session(self) -> None:
        """Forget the live session start; the next session begins a new range."""
        self._session_start = None

    def acknowledge_overflow(self) -> None:
        """Clear overflow degradation only after all known gaps are recovered."""
        if self._pending_overflow_gaps:
            return
        # Unresolvable overflow has no scoped SQLite gap; do not report recovery.
        if "coverage_gap_unscoped" in self.degraded_reasons:
            return
        gap_scopes = getattr(self.coverage, "gap_scopes", None)
        gaps = getattr(self.coverage, "gaps", None)
        if callable(gap_scopes) and callable(gaps):
            if any(gaps(scope) for scope in gap_scopes()):
                return
        self.degraded_reasons.discard("ingest_overflow")

    def _count(self, key: str) -> None:
        self.counters[key] = self.counters.get(key, 0) + 1

    def _notify_bar_applied(self, bar: OhlcvBar) -> None:
        if self._on_bar_applied is None:
            return
        try:
            self._on_bar_applied(bar)
        except Exception:
            # A client fan-out failure must never stop ingestion/aggregation.
            self._count("broadcast_callback_error")

    def _notify_live_bar_applied(self, bar: OhlcvBar) -> None:
        for callback in tuple(self._live_bar_applied_callbacks):
            try:
                callback(bar)
            except Exception:
                self._count("live_bar_callback_error")

    def _persist_derived(self, bar: OhlcvBar) -> bool:
        if self.persistence is None:
            return True
        try:
            result = self.persistence.apply(bar)
        except Exception:
            self._count("persistence_error")
            self.degraded_reasons.add("ohlcv_persistence_error")
            return False
        if result in ("inserted", "replaced", "duplicate"):
            return True
        self._count(f"persistence_{result}")
        self.degraded_reasons.add("ohlcv_persistence_conflict")
        return False

    def _note_overflow(self, instrument_hint: tuple[int, int] | None,
                       first_ns: int, last_ns: int) -> bool:
        start = first_ns // _NS * _NS
        end = last_ns // _NS * _NS + _NS
        if instrument_hint is None:
            self.degraded_reasons.add("coverage_gap_unscoped")
            self.degraded_reasons.add("ingest_overflow")
            return False
        publisher_id, instrument_id = instrument_hint
        mapping = self.resolver.resolve(
            self.provider, self.dataset, publisher_id, instrument_id, first_ns
        )
        if mapping is None:
            self.degraded_reasons.add("coverage_gap_unscoped")
            self.degraded_reasons.add("ingest_overflow")
            return False
        self.coverage.add_gap(mapping.coverage_scope, start, end)
        self.degraded_reasons.add("ingest_overflow")
        self._count("overflow_gap")
        return True

    @staticmethod
    def _distribution(samples: deque[float]) -> dict[str, float | int | None]:
        if not samples:
            return {"samples": 0, "p50_ms": None, "p95_ms": None, "max_ms": None}
        ordered = sorted(samples)
        p50_index = math.ceil(0.50 * len(ordered)) - 1
        p95_index = math.ceil(0.95 * len(ordered)) - 1
        return {
            "samples": len(ordered),
            "p50_ms": round(ordered[max(0, p50_index)], 3),
            "p95_ms": round(ordered[max(0, p95_index)], 3),
            "max_ms": round(ordered[-1], 3),
        }

    def _process(self, record: Any, schema: str, recv_ns: int, recv_monotonic_ns: int, *, live: bool) -> None:
        process_start_ns = self._monotonic()
        try:
            bar = record_to_bar(
                record, resolver=self.resolver, provider=self.provider,
                dataset=self.dataset, schema=schema, ts_received_ns=recv_ns,
                sequence=next(self._sequence),
            )
        except RecordRejected as exc:
            self._count(f"rejected_{exc.reason}")
            return
        except Exception:  # defensive: a bad record must never stop the consumer
            self._count("rejected_adapter_error")
            return
        if self.bar_validator is not None:
            try:
                self.bar_validator(bar)
            except Exception as exc:
                reason = getattr(exc, "reason", None)
                if isinstance(reason, str) and reason and reason.replace("_", "").isalnum():
                    self._count(f"rejected_validation_{reason}")
                else:
                    self._count("rejected_validation_error")
                return
        if self.persistence is not None:
            try:
                persisted = self.persistence.apply(bar)
            except Exception:
                self._count("persistence_error")
                self.degraded_reasons.add("ohlcv_persistence_error")
                return
            if persisted not in ("inserted", "replaced"):
                self._count(f"persistence_{persisted}")
                if persisted not in ("duplicate", "stale", "expired", "provider_precedence"):
                    self.degraded_reasons.add("ohlcv_persistence_conflict")
                return
        result = self.pipeline.apply(bar)
        process_end_ns = self._monotonic()
        self._count(result)
        if result not in ("inserted", "replaced"):
            if self.persistence is not None:
                self.degraded_reasons.add("ohlcv_persistence_memory_divergence")
            return
        if live:
            self.observations.observe(
                dataset=bar.dataset,
                publisher_id=bar.publisher_id,
                instrument_id=bar.instrument_id,
                raw_symbol=bar.raw_symbol,
                event_ns=bar.ts_event_ns,
                received_ns=bar.ts_received_ns,
                monotonic_received_ns=recv_monotonic_ns,
            )
            queue_delay_ms = max(0, process_start_ns - recv_monotonic_ns) / 1_000_000
            processing_ms = max(0, process_end_ns - process_start_ns) / 1_000_000
            self._queue_delay_samples_ms.append(queue_delay_ms)
            self._processing_samples_ms.append(processing_ms)
            self._callback_to_apply_samples_ms.append(queue_delay_ms + processing_ms)
            event_to_receive_ns = recv_ns - bar.ts_event_ns
            if event_to_receive_ns < 0:
                self._clock_skew_samples += 1
        self.last_event_ns = max(self.last_event_ns or 0, bar.ts_event_ns)
        self.last_receive_ns = max(self.last_receive_ns or 0, bar.ts_received_ns)
        # Live OHLCV omits intervals with no trades, so observed records do NOT
        # prove continuous coverage. Only successful historical query windows
        # may mark a range covered.
        self.aggregator.on_bar_applied(bar)
        self._notify_bar_applied(bar)
        if live:
            self._notify_live_bar_applied(bar)

    def status(self) -> dict[str, Any]:
        return {
            "queue_depth": len(self._buffer),
            "queue_capacity": self._buffer._max,
            "overflow_count": self._buffer.overflow_count,
            "pending_overflow_gaps": len(self._pending_overflow_gaps),
            "provider_callback_errors": self._provider_callback_errors,
            "degraded_reasons": sorted(self.degraded_reasons),
            "counters": dict(sorted(self.counters.items())),
            "aggregation": dict(self.aggregator.stats),
            "pipeline": self.pipeline.stats(),
            "persistence": None if self.persistence is None else self.persistence.stats(),
            "coverage": self.coverage.stats() if hasattr(self.coverage, "stats") else None,
            "last_event_ts_ns": None if self.last_event_ns is None else str(self.last_event_ns),
            "last_receive_ts_ns": None if self.last_receive_ns is None else str(self.last_receive_ns),
            "instrument_observations": self.observations.status(),
            "live_latency": {
                "measurement_window": "last_256_accepted_live_records",
                "queue_delay": self._distribution(self._queue_delay_samples_ms),
                "processing": self._distribution(self._processing_samples_ms),
                "callback_to_apply": self._distribution(self._callback_to_apply_samples_ms),
                "event_timestamp_clock_skew_samples": self._clock_skew_samples,
                "event_to_receive_note": "Not reported as network latency: event timestamps and backend wall clock may not be synchronized.",
            },
        }