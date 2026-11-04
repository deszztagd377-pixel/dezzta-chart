"""Provider lifecycle manager (connection state is separate from pipeline).

States reported: connecting | live | recovering | degraded | disconnected.
``live`` is reported ONLY after a real provider record has been received on
the current connection (never merely because a client object exists).
Without credentials or with the feature flags off, the manager stays
``disconnected`` and starts nothing. Credentials are never logged or returned.
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
        sleep: Callable[[float], Any] = asyncio.sleep,
        clock_ns: Callable[[], int] = time.time_ns,
        backoff_seconds: tuple[float, ...] = (1, 2, 4, 8, 16, 32, 60),
        max_attempts: int = 8,
    ) -> None:
        self._s = settings
        self._ingest = ingestion
        self._catalog = catalog
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

            signalled = [False]  # signal the loop once, not per record (bounded callbacks)

            def on_record(record: Any) -> None:
                try:
                    self._ingest.offer(record, "ohlcv-1s")
                    if not signalled[0]:
                        signalled[0] = True
                        loop.call_soon_threadsafe(first.set)
                except Exception:
                    pass  # callbacks must never raise into SDK threads

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

    # ------------------------------------------------------ definitions/backfill
    async def refresh_definitions(self, start_ns: int, end_ns: int) -> tuple[int, int]:
        """Load instrument definitions for [start,end) into catalog + resolver.
        Returns (registered, rejected). Requires historical access."""
        if not self.historical_allowed or not self._s.databento_definition_symbols:
            raise RuntimeError("Historical definitions are not enabled/configured.")
        self._validate_span(start_ns, end_ns)
        records = await self._fetch(
            "definition", self._s.databento_definition_symbols, "parent", start_ns, end_ns
        )
        rows = list(iter_definition_mappings(records))
        # Historical definition records are lifecycle events, not a flat
        # snapshot. Stable sorting preserves provider order for equal ts_event.
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