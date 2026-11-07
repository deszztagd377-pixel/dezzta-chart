"""Provider lifecycle manager (connection state is separate from pipeline).

States reported: connecting | live | recovering | degraded | disconnected.
``live`` is reported ONLY after a valid 1s OHLCV bar is accepted by persistence
and the pipeline on the current connection (never for system/error messages or
merely because a client object exists). Without credentials or with the feature
flags off, the manager stays ``disconnected`` and starts nothing. Credentials
are never logged or returned.
"""
from __future__ import annotations

import asyncio
import re
import time
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Protocol

from app.config import Settings
from app.databento_definitions import iter_definition_mappings
from app.ingest import OhlcvIngestionService
from app.instruments import InstrumentCatalog
from app.databento_definition_sync import DatabentoDefinitionSynchronizer

_NS = 1_000_000_000
_KEY_PATTERN = re.compile(r"db-[A-Za-z0-9]{8,}")


def redact(text: str, secret: str = "") -> str:
    """Remove the configured key and any Databento-key-looking token."""
    if secret:
        text = text.replace(secret, "[REDACTED]")
    return _KEY_PATTERN.sub("[REDACTED]", text)[:300]


def safe_error(exc: BaseException, secret: str = "") -> str:
    return f"{type(exc).__name__}: {redact(str(exc), secret)}"


class LiveSource(Protocol):
    """Provider-neutral live session. ``start`` must be non-blocking after
    connecting; ``on_record`` may be called from any thread; ``on_close`` is
    called once (any thread) when the session ends, with an error or None."""

    def start(
        self,
        on_record: Callable[[Any], None],
        on_close: Callable[[BaseException | None], None],
    ) -> None: ...

    def stop(self) -> None: ...


class HistoricalSource(Protocol):
    """Blocking, bounded fetch of one time window (run in a worker thread)."""

    def fetch(
        self, *, schema: str, symbols: tuple[str, ...], stype_in: str,
        start_ns: int, end_ns: int,
    ) -> list[Any]: ...


class ProviderManager:
    def __init__(
        self,
        settings: Settings,
        ingestion: OhlcvIngestionService,
        catalog: InstrumentCatalog,
        *,
        live_factory: Callable[[], LiveSource] | None = None,
        historical_factory: Callable[[], HistoricalSource] | None = None,
        definition_sync: DatabentoDefinitionSynchronizer | None = None,
        sleep: Callable[[float], Any] = asyncio.sleep,
        clock_ns: Callable[[], int] = time.time_ns,
        backoff_seconds: tuple[float, ...] = (1, 2, 4, 8, 16, 32, 60),
        max_attempts: int = 8,
    ) -> None:
        self._s = settings
        self._ingest = ingestion
        self._catalog = catalog
        self._definition_sync = definition_sync
        self._live_factory = live_factory
        self._hist_factory = historical_factory
        self._sleep = sleep
        self._clock = clock_ns
        self._backoff = backoff_seconds
        self._max_attempts = max_attempts
        self._connection = "disconnected"
        self._detail: str | None = None
        self._tasks: list[asyncio.Task[Any]] = []
        self._source: LiveSource | None = None
        self._first_record: asyncio.Event | None = None
        self._closed: asyncio.Event | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self.attempts = 0
        self.last_error: str | None = None
        self.last_connected_ns: int | None = None
        self.backfill: dict[str, Any] = {"state": "idle", "last_error": None, "windows_done": 0}

    # ----------------------------------------------------------------- state
    @property
    def live_allowed(self) -> bool:
        return bool(self._s.provider_configured and self._s.databento_live_enabled
                    and self._live_factory and self._s.databento_live_symbols)

    @property
    def historical_allowed(self) -> bool:
        return bool(self._s.provider_configured and self._s.databento_historical_enabled
                    and self._hist_factory)

    @property
    def state(self) -> str:
        if self._connection == "live" and self._ingest.degraded_reasons:
            return "degraded"
        return self._connection

    def status(self) -> dict[str, Any]:
        return {
            "provider": "databento",
            "dataset": self._s.databento_dataset,
            "schema": "ohlcv-1s",
            "state": self.state,
            "connected": self._connection == "live",
            "configured": self._s.provider_configured,
            "live_enabled": self._s.databento_live_enabled,
            "historical_enabled": self._s.databento_historical_enabled,
            "detail": self._detail,
            "reconnect_attempts": self.attempts,
            "last_error": self.last_error,
            "ingestion": self._ingest.status(),
            "backfill": dict(self.backfill),
        }

    # ------------------------------------------------------------- lifecycle
    async def start(self) -> None:
        if self._tasks:
            return
        self._loop = asyncio.get_running_loop()
        self._ingest.attach_loop(self._loop)
        if self._definition_sync is not None:
            self._definition_sync.restore_resolver()
        self._tasks.append(asyncio.create_task(self._ingest.run(), name="ohlcv-consumer"))
        if not self._s.provider_configured:
            self._detail = "not_configured: DATABENTO_API_KEY is not set"
        elif not self.live_allowed:
            self._detail = "live_disabled_or_no_symbols"
        else:
            # Live OHLCV records contain instrument IDs, not raw symbols. Load
            # point-in-time definitions first when the resolver is empty.
            if len(self._ingest.resolver) == 0:
                if not self.historical_allowed or not self._s.databento_definition_symbols:
                    self._detail = "instrument_definitions_required"
                    return
                now_ns = self._clock()
                start_ns = max(0, now_ns - self._s.historical_max_span_hours * 3600 * _NS)
                try:
                    await self.refresh_definitions(start_ns, now_ns)
                except Exception as exc:
                    self.last_error = safe_error(exc, self._s.databento_api_key)
                    self._detail = "instrument_definitions_failed"
                    return
                if len(self._ingest.resolver) == 0:
                    self._detail = "instrument_definitions_unavailable"
                    return
            if self.historical_allowed:
                self._tasks.append(asyncio.create_task(
                    self._run_startup_reconciliation(),
                    name="ohlcv-startup-reconciliation",
                ))
            self._tasks.append(asyncio.create_task(self._supervise(), name="ohlcv-live"))

    async def stop(self) -> None:
        tasks, self._tasks = self._tasks, []
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await self._stop_source()
        self._ingest.end_live_session()
        self._connection = "disconnected"
        self._detail = "stopped"

    async def _stop_source(self) -> None:
        source, self._source = self._source, None
        if source is not None:
            try:
                await asyncio.wait_for(asyncio.to_thread(source.stop), timeout=10)
            except Exception as exc:  # never propagate shutdown errors
                self.last_error = safe_error(exc, self._s.databento_api_key)

    async def _supervise(self) -> None:
        """Controlled reconnect loop: bounded attempts with exponential backoff."""
        failures = 0
        while failures < self._max_attempts:
            self._connection = "recovering" if self.last_connected_ns else "connecting"
            self._detail = "awaiting_first_record"
            self.attempts += 1
            loop = asyncio.get_running_loop()
            self._first_record = asyncio.Event()
            self._closed = asyncio.Event()
            first, closed = self._first_record, self._closed
            outcome: dict[str, BaseException | None] = {}

            signalled = [False]  # first successfully applied 1s OHLCV bar only

            def on_live_bar_applied(bar: Any) -> None:
                if bar.timeframe != "1s" or signalled[0]:
                    return
                signalled[0] = True
                try:
                    loop.call_soon_threadsafe(first.set)
                except RuntimeError:
                    pass  # event loop is already shutting down

            self._ingest.add_live_bar_applied_callback(on_live_bar_applied)

            def on_record(record: Any) -> None:
                try:
                    self._ingest.offer(record, "ohlcv-1s")
                except Exception:
                    # Keep SDK callbacks non-blocking, but never hide callback failures.
                    self._ingest.note_provider_callback_error()

            def on_close(error: BaseException | None) -> None:
                outcome["error"] = error
                try:
                    loop.call_soon_threadsafe(closed.set)
                except RuntimeError:
                    pass

            connected_at: float | None = None
            try:
                self._source = self._live_factory()  # type: ignore[misc]
                await asyncio.to_thread(self._source.start, on_record, on_close)
                waiters = [asyncio.create_task(first.wait()), asyncio.create_task(closed.wait())]
                await asyncio.wait(waiters, return_when=asyncio.FIRST_COMPLETED)
                for waiter in waiters:
                    waiter.cancel()
                if first.is_set():
                    self._connection = "live"
                    self._detail = None
                    self.last_connected_ns = self._clock()
                    connected_at = loop.time()
                    await closed.wait()
                    # A brief connect-then-drop is still a failed attempt. Reset
                    # the retry budget only after a genuinely stable session.
                    if loop.time() - connected_at >= 60:
                        failures = 0
                error = outcome.get("error")
                self.last_error = safe_error(error, self._s.databento_api_key) if error else self.last_error
                self._detail = "session_ended"
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.last_error = safe_error(exc, self._s.databento_api_key)
                self._detail = "connection_error"
            finally:
                self._ingest.remove_live_bar_applied_callback(on_live_bar_applied)
            failures += 1
            self._ingest.end_live_session()
            await self._stop_source()
            if failures >= self._max_attempts:
                break
            self._connection = "recovering"
            delay = self._backoff[min(failures - 1, len(self._backoff) - 1)]
            await self._sleep(delay)
        self._connection = "disconnected"
        self._detail = "gave_up_after_repeated_failures"

    async def _run_startup_reconciliation(self) -> None:
        """Run bounded historical reconciliation without delaying live startup."""
        try:
            await self.reconcile_live_history()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.backfill.update(state="reconciliation_failed",
                                 last_error=safe_error(exc, self._s.databento_api_key))

    async def reconcile_live_history(self) -> dict[str, int]:
        """Reconcile uncovered history after each symbol last durable 1s bar.

        This recovers the crash window where callback overflow metadata never
        reached SQLite. Callback handling remains memory-only and non-blocking.
        Work is bounded by the configured historical span across all symbols.
        """
        if not self.historical_allowed:
            raise RuntimeError("Historical ingestion is not enabled/configured.")
        symbols = tuple(dict.fromkeys(self._s.databento_live_symbols))
        if not symbols:
            self.backfill.update(state="reconciliation_skipped",
                                 last_error="no_explicit_live_symbols")
            return {"symbols_checked": 0, "symbols_unmapped": 0, "ranges_reconciled": 0,
                    "ranges_remaining": 0, "bars_ingested": 0, "windows_done": 0}

        # Resolve symbol diagnostics before checking persistence so an unavailable
        # store cannot hide configured symbols that have no valid catalog mapping.
        mappings_by_symbol = {
            symbol: self._ingest.resolver.mappings_for_symbol(
                self._ingest.provider, self._s.databento_dataset, symbol
            )
            for symbol in symbols
        }
        symbols_unmapped = sum(not mappings for mappings in mappings_by_symbol.values())
        store = self._ingest.persistence
        if store is None or not callable(getattr(store, "query", None)):
            self.backfill.update(state="reconciliation_skipped",
                                 last_error="durable_ohlcv_store_unavailable",
                                 symbols_unmapped=symbols_unmapped)
            return {"symbols_checked": 0, "symbols_unmapped": symbols_unmapped,
                    "ranges_reconciled": 0, "ranges_remaining": 0,
                    "bars_ingested": 0, "windows_done": 0}

        now_ns = self._clock()
        budget_ns = self._s.historical_max_span_hours * 3600 * _NS
        symbols_checked = ranges_reconciled = bars_ingested = windows_done = 0
        ranges_remaining = 0
        self.backfill.update(state="reconciling", last_error=None, windows_done=0,
                             reconciliation="startup_crash_window")
        for symbol in symbols:
            mappings = mappings_by_symbol[symbol]
            if not mappings:
                continue
            for mapping in sorted(mappings, key=lambda item: item.valid_from_ns):
                upper = min(now_ns, mapping.valid_to_ns if mapping.valid_to_ns is not None else now_ns)
                if upper <= mapping.valid_from_ns:
                    continue
                latest, _ = store.query(
                    provider=self._ingest.provider, dataset=self._s.databento_dataset,
                    publisher_id=mapping.publisher_id, instrument_id=mapping.instrument_id,
                    raw_symbol=mapping.raw_symbol, series_type=mapping.series_type,
                    timeframe="1s", limit=1,
                )
                start = mapping.valid_from_ns
                if latest:
                    start = max(start, latest[-1].ts_start_ns + _NS)
                start = min(start, upper)
                if start >= upper:
                    symbols_checked += 1
                    continue

                # Reuse durable coverage so interrupted reconciliation resumes
                # from the first uncovered range instead of repeating work.
                cursor = start
                missing: list[tuple[int, int]] = []
                for covered_start, covered_end in self._ingest.coverage.intervals(mapping.coverage_scope):
                    if covered_end <= cursor or covered_start >= upper:
                        continue
                    if covered_start > cursor:
                        missing.append((cursor, min(covered_start, upper)))
                    cursor = max(cursor, covered_end)
                    if cursor >= upper:
                        break
                if cursor < upper:
                    missing.append((cursor, upper))

                symbols_checked += 1
                for gap_start, gap_end in missing:
                    if gap_end <= gap_start:
                        continue
                    if budget_ns <= 0:
                        ranges_remaining += 1
                        continue
                    query_end = min(gap_end,
                                    gap_start + self._s.historical_max_span_hours * 3600 * _NS,
                                    gap_start + budget_ns)
                    bars_ingested += await self.backfill_ohlcv(
                        (mapping.raw_symbol,), gap_start, query_end, schema="ohlcv-1s"
                    )
                    windows_done += int(self.backfill.get("windows_done", 0))
                    budget_ns -= query_end - gap_start
                    ranges_reconciled += 1
                    if query_end < gap_end:
                        ranges_remaining += 1
        self.backfill.update(state="reconciliation_done", last_error=None,
                             windows_done=windows_done, symbols_checked=symbols_checked,
                             symbols_unmapped=symbols_unmapped,
                             ranges_reconciled=ranges_reconciled, ranges_remaining=ranges_remaining,
                             bars_ingested=bars_ingested, reconciliation="startup_crash_window")
        return {"symbols_checked": symbols_checked, "symbols_unmapped": symbols_unmapped,
                "ranges_reconciled": ranges_reconciled, "ranges_remaining": ranges_remaining,
                "bars_ingested": bars_ingested, "windows_done": windows_done}

    # ------------------------------------------------------ definitions/backfill
    async def refresh_definitions(self, start_ns: int, end_ns: int) -> tuple[int, int]:
        """Apply ordered Databento definition events to catalog + resolver.
        Returns (events_applied, events_rejected). Requires historical access."""
        if not self.historical_allowed or not self._s.databento_definition_symbols:
            raise RuntimeError("Historical definitions are not enabled/configured.")
        self._validate_span(start_ns, end_ns)
        records = await self._fetch(
            "definition", self._s.databento_definition_symbols, "parent", start_ns, end_ns
        )
        rows = list(iter_definition_mappings(records))
        # Journal-first synchronization makes definition history durable and
        # keeps mapping + metadata transitions atomic across process restarts.
        if self._definition_sync is not None:
            return self._definition_sync.ingest_rows(rows)
        # Compatibility path for isolated provider tests without persistence.
        rows.sort(key=lambda row: int(row["ts_event"]))
        registered = rejected = 0
        for row in rows:
            try:
                action = str(row["security_update_action"]).strip().upper()
                applied = self._catalog.apply_definition_event(
                    row, dataset=self._s.databento_dataset
                )
                if not applied:
                    rejected += 1
                    continue

                if action == "D":
                    self._ingest.resolver.close_mapping(
                        provider=self._ingest.provider,
                        dataset=self._s.databento_dataset,
                        publisher_id=int(row["publisher_id"]),
                        instrument_id=int(row["instrument_id"]),
                        effective_to_ns=int(row["ts_event"]),
                    )
                    registered += 1
                    continue

                contract = next(
                    item for item in self._catalog.list_contracts()
                    if item["dataset"] == self._s.databento_dataset
                    and item["publisher_id"] == int(row["publisher_id"])
                    and item["instrument_id"] == int(row["instrument_id"])
                )
                added, invalid = self._ingest.resolver.register_catalog_contracts(
                    [contract], provider=self._ingest.provider
                )
                registered += added
                rejected += invalid
            except (KeyError, TypeError, ValueError, StopIteration):
                rejected += 1
        return registered, rejected

    async def backfill_ohlcv(
        self, symbols: Iterable[str], start_ns: int, end_ns: int, schema: str = "ohlcv-1s"
    ) -> int:
        """Bounded historical backfill, window by window (bounded memory)."""
        if not self.historical_allowed:
            raise RuntimeError("Historical ingestion is not enabled/configured.")
        self._validate_span(start_ns, end_ns)
        symbols = tuple(symbols)
        if not symbols:
            raise ValueError("Explicit contract symbols are required.")
        window = self._s.historical_window_minutes * 60 * _NS
        total, cursor = 0, start_ns
        self.backfill = {"state": "running", "last_error": None, "windows_done": 0}
        try:
            while cursor < end_ns:
                upper = min(cursor + window, end_ns)
                records = await self._fetch(schema, symbols, "raw_symbol", cursor, upper)
                total += self._ingest.ingest_batch(records, schema, live=False)
                # A successful get_range window covers only the explicitly
                # requested instruments and only during their valid mapping.
                for symbol in symbols:
                    for mapping in self._ingest.resolver.mappings_for_symbol(
                        self._ingest.provider, self._s.databento_dataset, symbol
                    ):
                        covered_start = max(cursor, mapping.valid_from_ns)
                        covered_end = min(
                            upper, mapping.valid_to_ns if mapping.valid_to_ns is not None else upper
                        )
                        if covered_end > covered_start:
                            self._ingest.coverage.add_covered(
                                mapping.coverage_scope, covered_start, covered_end
                            )
                self.backfill["windows_done"] += 1
                cursor = upper
                await asyncio.sleep(0)
        except Exception as exc:
            self.backfill.update(state="failed", last_error=safe_error(exc, self._s.databento_api_key))
            raise
        self.backfill["state"] = "done"
        return total

    async def recover_gaps(
        self, *, max_gaps: int = 100,
        max_total_span_hours: int | None = None,
    ) -> dict[str, int]:
        """Backfill a bounded number of durable gaps using exact provider mappings.

        This is an explicit operator/service action, not an automatic startup
        network request. Each query is clipped to the mapping's validity range
        and split by the configured maximum historical span.
        """
        if not self.historical_allowed:
            raise RuntimeError("Historical ingestion is not enabled/configured.")
        if not isinstance(max_gaps, int) or isinstance(max_gaps, bool) or max_gaps < 1:
            raise ValueError("max_gaps must be a positive integer.")
        coverage = self._ingest.coverage
        if not hasattr(coverage, "gap_scopes") or not hasattr(coverage, "gaps"):
            raise RuntimeError("Durable gap tracking is not available.")
        total_span_hours = (
            self._s.historical_max_span_hours
            if max_total_span_hours is None else max_total_span_hours
        )
        if (
            not isinstance(total_span_hours, int) or isinstance(total_span_hours, bool)
            or total_span_hours < 1
            or total_span_hours > self._s.historical_max_span_hours
        ):
            raise ValueError(
                "max_total_span_hours must be between 1 and the configured historical maximum."
            )
        attempted = recovered = skipped = bars_ingested = windows_done = 0
        max_span_ns = self._s.historical_max_span_hours * 3600 * _NS
        remaining_budget_ns = total_span_hours * 3600 * _NS

        for scope in coverage.gap_scopes():
            if attempted >= max_gaps or remaining_budget_ns <= 0:
                break
            if (
                not isinstance(scope, tuple) or len(scope) != 6
                or scope[0] != self._ingest.provider
                or scope[1] != self._s.databento_dataset
            ):
                skipped += 1
                continue
            raw_symbol = scope[5]
            mappings = [
                item for item in self._ingest.resolver.mappings_for_symbol(
                    self._ingest.provider, self._s.databento_dataset, raw_symbol
                )
                if item.coverage_scope == scope
            ]
            for gap_start, gap_end in coverage.gaps(scope):
                if attempted >= max_gaps or remaining_budget_ns <= 0:
                    break
                attempted += 1
                if not mappings:
                    skipped += 1
                    continue
                overlap_found = False
                for mapping in mappings:
                    start = max(gap_start, mapping.valid_from_ns)
                    end = min(
                        gap_end,
                        mapping.valid_to_ns if mapping.valid_to_ns is not None else gap_end,
                    )
                    if end <= start:
                        continue
                    overlap_found = True
                    cursor = start
                    while cursor < end and remaining_budget_ns > 0:
                        upper = min(
                            cursor + max_span_ns,
                            end,
                            cursor + remaining_budget_ns,
                        )
                        bars_ingested += await self.backfill_ohlcv(
                            (raw_symbol,), cursor, upper, schema="ohlcv-1s"
                        )
                        windows_done += int(self.backfill.get("windows_done", 0))
                        remaining_budget_ns -= upper - cursor
                        cursor = upper
                if not overlap_found:
                    skipped += 1
                still_missing = any(
                    left < gap_end and right > gap_start
                    for left, right in coverage.gaps(scope)
                )
                if not still_missing:
                    recovered += 1

        remaining = sum(
            len(coverage.gaps(scope)) for scope in coverage.gap_scopes()
        )
        if remaining == 0:
            self._ingest.acknowledge_overflow()
        self.backfill.update(
            state="done",
            gaps_attempted=attempted,
            gaps_recovered=recovered,
            gaps_skipped=skipped,
            gaps_remaining=remaining,
            recovery_windows_done=windows_done,
        )
        return {
            "gaps_attempted": attempted,
            "gaps_recovered": recovered,
            "gaps_skipped": skipped,
            "gaps_remaining": remaining,
            "bars_ingested": bars_ingested,
            "windows_done": windows_done,
        }

    def _validate_span(self, start_ns: int, end_ns: int) -> None:
        if not (0 <= start_ns < end_ns):
            raise ValueError("start must be before end.")
        if end_ns - start_ns > self._s.historical_max_span_hours * 3600 * _NS:
            raise ValueError("Requested historical span exceeds the configured maximum.")

    async def _fetch(self, schema, symbols, stype_in, start_ns, end_ns) -> list[Any]:
        source = self._hist_factory()  # type: ignore[misc]
        return await asyncio.to_thread(
            source.fetch, schema=schema, symbols=tuple(symbols), stype_in=stype_in,
            start_ns=start_ns, end_ns=end_ns,
        )