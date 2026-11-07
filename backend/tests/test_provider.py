import asyncio
import threading
from types import SimpleNamespace

import pytest

from app.config import Settings
from app.instruments import InstrumentCatalog
from app.provider import ProviderManager, redact, safe_error
from helpers import NS, T0, make_service, rec

SECRET = "db-SECRETSECRETSECRETSECRET123456"


def settings(**kw):
    base = dict(app_env="test", market_data_ws_token="t", cors_allowed_origins=())
    base.update(kw)
    return Settings(**base)


class FakeLive:
    """Scriptable LiveSource: emits records from a thread, can close or fail."""
    instances: list = []

    def __init__(self, *, fail_start=None, records=(), close_after=None):
        self.fail_start, self.records, self.close_after = fail_start, records, close_after
        self.started = self.stopped = False
        FakeLive.instances.append(self)

    def start(self, on_record, on_close):
        if self.fail_start:
            raise self.fail_start
        self.started = True
        self.on_close = on_close

        def emit():
            for r in self.records:
                on_record(r)
            if self.close_after is not None:
                on_close(self.close_after if isinstance(self.close_after, BaseException) else None)
        threading.Thread(target=emit, daemon=True).start()

    def stop(self):
        self.stopped = True


def manager(factory=None, hist=None, sleeps=None, **kw):
    service, pipeline, resolver, coverage = make_service()
    cfg = settings(**{"databento_api_key": SECRET, "databento_live_enabled": True,
                      "databento_live_symbols": ("ESZ6",), **kw})
    async def fake_sleep(seconds):
        if sleeps is not None:
            sleeps.append(seconds)
        await asyncio.sleep(0)
    m = ProviderManager(cfg, service, InstrumentCatalog(), live_factory=factory,
                        historical_factory=hist, sleep=fake_sleep, max_attempts=3)
    return m, service, pipeline


async def wait_for(predicate, tries=500):
    for _ in range(tries):
        if predicate():
            return True
        await asyncio.sleep(0.005)
    return False


def test_without_credentials_nothing_connects_and_state_is_disconnected():
    async def go():
        service, *_ = make_service()
        m = ProviderManager(settings(), service, InstrumentCatalog())
        await m.start()
        s = m.status()
        await m.stop()
        return s
    s = asyncio.run(go())
    assert s["state"] == "disconnected" and s["connected"] is False and s["configured"] is False
    assert "not_configured" in s["detail"]


def test_live_is_reported_only_after_a_real_record_arrives():
    FakeLive.instances.clear()
    async def go():
        m, service, pipeline = manager(lambda: FakeLive(records=[rec(0), rec(1)]))
        await m.start()
        assert await wait_for(lambda: m.state == "live")
        assert await wait_for(lambda: len(pipeline.list_bars(timeframe="1s")) == 2)
        status = m.status()
        await m.stop()
        return status, m.state
    status, final = asyncio.run(go())
    assert status["state"] == "live" and status["connected"] is True
    assert final == "disconnected"
    assert FakeLive.instances[0].stopped is True  # graceful shutdown stops the source


def test_system_message_does_not_mark_live_before_a_valid_bar_is_applied():
    async def go():
        system = SimpleNamespace(msg="heartbeat", code=0)
        m, service, pipeline = manager(lambda: FakeLive(records=[system, rec(0)]))
        await m.start()
        assert await wait_for(lambda: m.state == "live")
        assert await wait_for(lambda: len(pipeline.list_bars(timeframe="1s")) == 1)
        status = m.status()
        await m.stop()
        return status, service
    status, service = asyncio.run(go())
    assert status["state"] == "live"
    assert service.counters["rejected_unsupported_record"] == 1


def test_error_message_alone_does_not_mark_live():
    async def go():
        error = SimpleNamespace(err="invalid subscription", code=5, is_last=True)
        m, service, _ = manager(lambda: FakeLive(records=[error]))
        await m.start()
        await asyncio.sleep(0.1)
        state = m.state
        counters = dict(service.counters)
        await m.stop()
        return state, counters
    state, counters = asyncio.run(go())
    assert state == "connecting"
    assert counters["rejected_unsupported_record"] == 1


def test_unknown_instrument_record_does_not_mark_live():
    async def go():
        m, service, _ = manager(lambda: FakeLive(records=[rec(0, instrument_id=999)]))
        await m.start()
        await asyncio.sleep(0.1)
        state = m.state
        counters = dict(service.counters)
        await m.stop()
        return state, counters
    state, counters = asyncio.run(go())
    assert state == "connecting"
    assert counters["rejected_unknown_instrument"] == 1


def test_provider_callback_failures_are_counted_not_silently_swallowed():
    async def go():
        m, service, _ = manager(lambda: FakeLive(records=[rec(0)]))
        def broken_offer(record, schema):
            raise RuntimeError("synthetic callback failure")
        service.offer = broken_offer
        await m.start()
        assert await wait_for(lambda: service.status()["provider_callback_errors"] == 1)
        state = m.state
        await m.stop()
        return state, service.status()
    state, status = asyncio.run(go())
    assert state == "connecting"
    assert status["provider_callback_errors"] == 1


def test_silent_connection_is_never_reported_live():
    async def go():
        m, *_ = manager(lambda: FakeLive(records=[]))
        await m.start()
        await asyncio.sleep(0.1)
        state = m.state
        await m.stop()
        return state
    assert asyncio.run(go()) == "connecting"


def test_unexpected_disconnect_recovers_with_backoff_not_a_tight_loop():
    FakeLive.instances.clear()
    sleeps = []
    async def go():
        m, *_ = manager(lambda: FakeLive(records=[rec(0)], close_after=True), sleeps=sleeps)
        await m.start()
        assert await wait_for(lambda: m.status()["detail"] == "gave_up_after_repeated_failures")
        status = m.status()
        await m.stop()
        return status
    status = asyncio.run(go())
    assert status["reconnect_attempts"] == 3
    assert sleeps == [1, 2]  # fast connect-then-drop consumes the bounded retry budget


def test_repeated_failures_give_up_and_errors_are_redacted():
    sleeps = []
    async def go():
        err = RuntimeError(f"auth failed for key {SECRET}")
        m, *_ = manager(lambda: FakeLive(fail_start=err), sleeps=sleeps)
        await m.start()
        assert await wait_for(lambda: m.status()["detail"] == "gave_up_after_repeated_failures")
        status = m.status()
        await m.stop()
        return status
    status = asyncio.run(go())
    assert status["state"] == "disconnected" and status["reconnect_attempts"] == 3
    assert SECRET not in repr(status) and "[REDACTED]" in status["last_error"]
    assert sleeps == [1, 2]  # bounded exponential backoff between the 3 attempts


def test_redaction_helpers():
    assert SECRET not in redact(f"x {SECRET} y", SECRET)
    assert "db-ABCDEFGH12345" not in redact("token db-ABCDEFGH12345 leaked")
    assert safe_error(ValueError(SECRET), SECRET) == "ValueError: [REDACTED]"


def test_cancellation_during_connect_stops_cleanly():
    async def go():
        m, *_ = manager(lambda: FakeLive(records=[]))
        await m.start()
        await asyncio.sleep(0.02)
        await m.stop()
        await m.stop()  # idempotent
        return m.state
    assert asyncio.run(go()) == "disconnected"


def test_overflow_makes_a_live_connection_degraded():
    async def go():
        m, service, _ = manager(lambda: FakeLive(records=[rec(0)]))
        await m.start()
        assert await wait_for(lambda: m.state == "live")
        service.degraded_reasons.add("ingest_overflow")
        state = m.state
        await m.stop()
        return state
    assert asyncio.run(go()) == "degraded"


class FakeHistorical:
    def __init__(self):
        self.calls = []

    def fetch(self, *, schema, symbols, stype_in, start_ns, end_ns):
        self.calls.append((schema, symbols, stype_in, start_ns, end_ns))
        if schema == "definition":
            return [SimpleNamespace(
                raw_symbol="ESZ6", instrument_id=101, publisher_id=1, instrument_class="F",
                security_update_action="A",
                expiration=1_797_638_400 * NS - NS, ts_event=T0 - 10 * NS,
                min_price_increment=250_000_000, currency="USD")]
        return [rec(int((start_ns - T0) // NS) + i) for i in range(2)]


def test_backfill_is_bounded_windowed_and_records_coverage():
    hist = FakeHistorical()
    async def go():
        m, service, pipeline = manager(hist=lambda: hist, databento_historical_enabled=True,
                                       historical_window_minutes=1, historical_max_span_hours=1)
        total = await m.backfill_ohlcv(["ESZ6"], T0, T0 + 150 * NS)
        return m, service, pipeline, total
    m, service, pipeline, total = asyncio.run(go())
    assert [c[4] - c[3] for c in hist.calls] == [60 * NS, 60 * NS, 30 * NS]  # bounded windows
    assert all(c[2] == "raw_symbol" for c in hist.calls)  # explicit contracts, no parent symbology
    assert total == 6 and m.backfill["state"] == "done"
    assert service.coverage.intervals(("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")) == [(T0, T0 + 150 * NS)]



def test_concurrent_backfills_are_serialized_and_keep_status_consistent():
    import time

    class TrackingHistorical:
        def __init__(self):
            self.active = 0
            self.max_active = 0
            self.lock = threading.Lock()
        def fetch(self, *, schema, symbols, stype_in, start_ns, end_ns):
            with self.lock:
                self.active += 1
                self.max_active = max(self.max_active, self.active)
            time.sleep(0.02)
            with self.lock:
                self.active -= 1
            return []

    async def go():
        hist = TrackingHistorical()
        m, *_ = manager(hist=lambda: hist, databento_historical_enabled=True,
                        historical_window_minutes=1, historical_max_span_hours=1)
        results = await asyncio.gather(
            m.backfill_ohlcv(["ESZ6"], T0, T0 + 2 * NS),
            m.backfill_ohlcv(["ESZ6"], T0 + 2 * NS, T0 + 4 * NS),
        )
        return hist, results, m.backfill

    hist, results, status = asyncio.run(go())
    assert hist.max_active == 1
    assert results == [0, 0]
    assert status["state"] == "done"
    assert status["windows_done"] == 1

def test_backfill_requires_explicit_enable_symbols_and_bounded_span():
    async def run(coro_factory, **kw):
        m, *_ = manager(hist=lambda: FakeHistorical(), **kw)
        return await coro_factory(m)
    with pytest.raises(RuntimeError):
        asyncio.run(run(lambda m: m.backfill_ohlcv(["ESZ6"], T0, T0 + NS)))  # disabled by default
    with pytest.raises(ValueError):
        asyncio.run(run(lambda m: m.backfill_ohlcv(["ESZ6"], T0, T0 + 3 * 3600 * NS),
                        databento_historical_enabled=True, historical_max_span_hours=1))
    with pytest.raises(ValueError):
        asyncio.run(run(lambda m: m.backfill_ohlcv([], T0, T0 + NS), databento_historical_enabled=True))


def test_definitions_populate_catalog_and_resolver_for_ohlcv_normalization():
    hist = FakeHistorical()
    async def go():
        m, service, pipeline = manager(hist=lambda: hist, databento_historical_enabled=True,
                                       databento_definition_symbols=("ES.FUT",))
        result = await m.refresh_definitions(T0 - 3600 * NS, T0)
        service.ingest_batch([rec(0)], "ohlcv-1s")
        return result, pipeline
    result, pipeline = asyncio.run(go())
    assert result == (1, 0)
    assert pipeline.list_bars()[0].raw_symbol == "ESZ6"


class DefinitionEventHistorical:
    def __init__(self, records):
        self.records = records

    def fetch(self, *, schema, symbols, stype_in, start_ns, end_ns):
        if schema == "definition":
            return self.records
        return []


def test_refresh_definitions_applies_ordered_add_modify_delete_events():
    records = [
        SimpleNamespace(
            raw_symbol="ESZ6", instrument_id=101, publisher_id=1,
            instrument_class="F", security_update_action="A",
            expiration=1_797_638_400 * NS, currency="USD",
            min_price_increment=250_000_000, ts_event=T0 + 100,
        ),
        SimpleNamespace(
            raw_symbol="ESU6", instrument_id=101, publisher_id=1,
            instrument_class="F", security_update_action="M",
            expiration=1_789_948_800 * NS, currency="USD",
            min_price_increment=250_000_000, ts_event=T0 + 200,
        ),
        SimpleNamespace(
            raw_symbol="ESU6", instrument_id=101, publisher_id=1,
            instrument_class="F", security_update_action="D",
            ts_event=T0 + 300,
        ),
    ]
    hist = DefinitionEventHistorical(records)

    async def go():
        m, service, _ = manager(
            hist=lambda: hist,
            databento_historical_enabled=True,
            databento_definition_symbols=("ES.FUT",),
        )
        result = await m.refresh_definitions(T0, T0 + 400)
        return result, service, m

    result, service, manager_instance = asyncio.run(go())
    assert result == (3, 0)
    assert manager_instance._catalog.list_contracts() == []
    resolver = service.resolver
    assert resolver.resolve(
        "databento", "GLBX.MDP3", 1, 101, T0 + 150
    ).raw_symbol == "ESZ6"
    assert resolver.resolve(
        "databento", "GLBX.MDP3", 1, 101, T0 + 250
    ).raw_symbol == "ESU6"
    assert resolver.resolve(
        "databento", "GLBX.MDP3", 1, 101, T0 + 350
    ) is None


def test_without_definitions_records_are_rejected_not_invented():
    from app.coverage import CoverageTracker
    from app.ingest import OhlcvIngestionService
    from app.ohlcv import OhlcvPipeline
    from app.symbology import InstrumentResolver
    service = OhlcvIngestionService(pipeline=OhlcvPipeline(), resolver=InstrumentResolver(),
                                    coverage=CoverageTracker())
    service.ingest_batch([rec(0)], "ohlcv-1s")
    assert service.counters == {"rejected_unknown_instrument": 1}

def test_startup_reconciliation_scans_bounded_horizon_and_keeps_callback_nonblocking(tmp_path):
    from app.ohlcv import OhlcvPipeline
    from app.ingest import OhlcvIngestionService
    from app.ohlcv_store import SQLiteOhlcvStore
    from app.symbology import InstrumentResolver, SymbolMapping
    from app.coverage import CoverageTracker

    class EmptyHistorical:
        def __init__(self): self.calls = []
        def fetch(self, *, schema, symbols, stype_in, start_ns, end_ns):
            self.calls.append((schema, symbols, stype_in, start_ns, end_ns))
            return []

    async def go():
        store = SQLiteOhlcvStore(str(tmp_path / "ohlcv.sqlite3"))
        resolver = InstrumentResolver()
        resolver.add(SymbolMapping(provider="databento", dataset="GLBX.MDP3",
            publisher_id=1, instrument_id=101, raw_symbol="ESZ6", valid_from_ns=T0))
        service = OhlcvIngestionService(pipeline=OhlcvPipeline(), resolver=resolver,
            coverage=CoverageTracker(), persistence=store, clock_ns=lambda: T0 + 10 * NS)
        service.ingest_batch([rec(2)], "ohlcv-1s")
        hist = EmptyHistorical()
        cfg = settings(databento_api_key=SECRET, databento_live_enabled=True,
            databento_live_symbols=("ESZ6",), databento_historical_enabled=True,
            historical_window_minutes=1, historical_max_span_hours=1)
        manager_instance = ProviderManager(cfg, service, InstrumentCatalog(),
            historical_factory=lambda: hist, clock_ns=lambda: T0 + 10 * NS)
        result = await manager_instance.reconcile_live_history()
        return result, hist, service, manager_instance

    result, hist, service, manager_instance = asyncio.run(go())
    assert result == {"symbols_checked": 1, "symbols_unmapped": 0, "ranges_reconciled": 1,
        "ranges_remaining": 0, "bars_ingested": 0, "windows_done": 1}
    # The in-memory coverage tracker has no covered interval in this fixture,
    # so reconciliation scans the configured recent horizon as one range.
    # The existing durable bar remains safe because ingestion is idempotent.
    assert hist.calls == [
        ("ohlcv-1s", ("ESZ6",), "raw_symbol", T0, T0 + 10 * NS),
    ]
    assert service.offer(rec(9), "ohlcv-1s") is True
    assert manager_instance.backfill["state"] == "reconciliation_done"


def test_startup_reconciliation_reports_explicit_symbols_without_a_valid_mapping():
    async def go():
        service, *_ = make_service()
        cfg = settings(databento_api_key=SECRET, databento_live_enabled=True,
            databento_live_symbols=("NQZ6",), databento_historical_enabled=True)
        manager_instance = ProviderManager(cfg, service, InstrumentCatalog(),
            historical_factory=lambda: FakeHistorical(), clock_ns=lambda: T0 + NS)
        return await manager_instance.reconcile_live_history()

    result = asyncio.run(go())
    assert result == {"symbols_checked": 0, "symbols_unmapped": 1,
        "ranges_reconciled": 0, "ranges_remaining": 0, "bars_ingested": 0, "windows_done": 0}


def test_startup_reconciliation_finds_hole_before_latest_durable_bar(tmp_path):
    from app.ohlcv import OhlcvPipeline
    from app.ingest import OhlcvIngestionService
    from app.ohlcv_store import SQLiteOhlcvStore
    from app.coverage import CoverageTracker
    from app.symbology import InstrumentResolver, SymbolMapping

    class EmptyHistorical:
        def __init__(self): self.calls = []
        def fetch(self, *, schema, symbols, stype_in, start_ns, end_ns):
            self.calls.append((symbols, start_ns, end_ns))
            return []

    async def go():
        store = SQLiteOhlcvStore(str(tmp_path / "ohlcv.sqlite3"))
        resolver = InstrumentResolver()
        resolver.add(SymbolMapping(provider="databento", dataset="GLBX.MDP3",
            publisher_id=1, instrument_id=101, raw_symbol="ESZ6", valid_from_ns=T0))
        coverage = CoverageTracker()
        scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
        coverage.add_covered(scope, T0, T0 + 4 * NS)
        coverage.add_covered(scope, T0 + 5 * NS, T0 + 10 * NS)
        service = OhlcvIngestionService(pipeline=OhlcvPipeline(), resolver=resolver,
            coverage=coverage, persistence=store, clock_ns=lambda: T0 + 10 * NS)
        # A newer durable bar exists after the uncovered one-second interval.
        service.ingest_batch([rec(8)], "ohlcv-1s")
        hist = EmptyHistorical()
        cfg = settings(databento_api_key=SECRET, databento_live_enabled=True,
            databento_live_symbols=("ESZ6",), databento_historical_enabled=True,
            historical_window_minutes=1, historical_max_span_hours=1)
        manager_instance = ProviderManager(cfg, service, InstrumentCatalog(),
            historical_factory=lambda: hist, clock_ns=lambda: T0 + 10 * NS)
        result = await manager_instance.reconcile_live_history()
        return result, hist

    result, hist = asyncio.run(go())
    assert result["ranges_reconciled"] == 1
    assert result["ranges_remaining"] == 0
    assert hist.calls == [(("ESZ6",), T0 + 4 * NS, T0 + 5 * NS)]

def test_startup_reconciliation_respects_global_budget_and_existing_coverage(tmp_path):
    from app.ohlcv import OhlcvPipeline
    from app.ingest import OhlcvIngestionService
    from app.ohlcv_store import SQLiteOhlcvStore
    from app.coverage import CoverageTracker
    from app.symbology import InstrumentResolver, SymbolMapping

    class EmptyHistorical:
        def __init__(self): self.calls = []
        def fetch(self, *, schema, symbols, stype_in, start_ns, end_ns):
            self.calls.append((symbols, start_ns, end_ns))
            return []

    async def go():
        store = SQLiteOhlcvStore(str(tmp_path / "ohlcv.sqlite3"))
        resolver = InstrumentResolver()
        for instrument_id, symbol in ((101, "ESZ6"), (102, "NQZ6")):
            resolver.add(SymbolMapping(provider="databento", dataset="GLBX.MDP3",
                publisher_id=1, instrument_id=instrument_id, raw_symbol=symbol, valid_from_ns=T0))
        coverage = CoverageTracker()
        coverage.add_covered(("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6"),
                             T0, T0 + 30 * NS)
        service = OhlcvIngestionService(pipeline=OhlcvPipeline(), resolver=resolver,
            coverage=coverage, persistence=store, clock_ns=lambda: T0 + 7200 * NS)
        hist = EmptyHistorical()
        cfg = settings(databento_api_key=SECRET, databento_live_enabled=True,
            databento_live_symbols=("ESZ6", "NQZ6"), databento_historical_enabled=True,
            historical_window_minutes=60, historical_max_span_hours=1)
        manager_instance = ProviderManager(cfg, service, InstrumentCatalog(),
            historical_factory=lambda: hist, clock_ns=lambda: T0 + 7200 * NS)
        result = await manager_instance.reconcile_live_history()
        return result, hist

    result, hist = asyncio.run(go())
    assert result["symbols_unmapped"] == 0
    assert result["ranges_reconciled"] == 1 and result["ranges_remaining"] == 1
    assert hist.calls == [(("ESZ6",), T0 + 3600 * NS, T0 + 7200 * NS)]

def test_recover_gaps_uses_valid_mapping_and_bounded_historical_windows(tmp_path):
    from app.coverage_store import SQLiteCoverageTracker
    from app.ohlcv import OhlcvPipeline
    from app.ingest import OhlcvIngestionService
    from app.symbology import InstrumentResolver, SymbolMapping

    class EmptyHistorical:
        def __init__(self):
            self.calls = []

        def fetch(self, *, schema, symbols, stype_in, start_ns, end_ns):
            self.calls.append((schema, symbols, stype_in, start_ns, end_ns))
            return []

    async def go():
        scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
        coverage = SQLiteCoverageTracker(str(tmp_path / "coverage.sqlite3"))
        coverage.add_gap(scope, T0, T0 + 120 * NS)
        resolver = InstrumentResolver()
        resolver.add(SymbolMapping(
            provider="databento", dataset="GLBX.MDP3",
            publisher_id=1, instrument_id=101, raw_symbol="ESZ6",
            valid_from_ns=T0, valid_to_ns=T0 + 120 * NS,
        ))
        service = OhlcvIngestionService(
            pipeline=OhlcvPipeline(), resolver=resolver, coverage=coverage
        )
        service.degraded_reasons.add("ingest_overflow")
        hist = EmptyHistorical()
        cfg = settings(
            databento_api_key=SECRET,
            databento_historical_enabled=True,
            historical_window_minutes=1,
            historical_max_span_hours=1,
        )
        manager = ProviderManager(
            cfg, service, InstrumentCatalog(), historical_factory=lambda: hist
        )
        result = await manager.recover_gaps()
        return result, hist, coverage, scope, service

    result, hist, coverage, scope, service = asyncio.run(go())
    assert result == {
        "gaps_attempted": 1, "gaps_recovered": 1, "gaps_skipped": 0,
        "gaps_remaining": 0, "bars_ingested": 0, "windows_done": 2,
    }
    assert [call[4] - call[3] for call in hist.calls] == [60 * NS, 60 * NS]
    assert all(call[1] == ("ESZ6",) and call[2] == "raw_symbol" for call in hist.calls)
    assert coverage.gaps(scope) == []
    assert coverage.intervals(scope) == [(T0, T0 + 120 * NS)]
    assert "ingest_overflow" not in service.degraded_reasons


def test_recover_gaps_skips_unresolvable_scope_without_erasing_gap(tmp_path):
    from app.coverage_store import SQLiteCoverageTracker
    from app.ohlcv import OhlcvPipeline
    from app.ingest import OhlcvIngestionService
    from app.symbology import InstrumentResolver

    async def go():
        scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
        coverage = SQLiteCoverageTracker(str(tmp_path / "coverage.sqlite3"))
        coverage.add_gap(scope, T0, T0 + NS)
        service = OhlcvIngestionService(
            pipeline=OhlcvPipeline(), resolver=InstrumentResolver(), coverage=coverage
        )
        service.degraded_reasons.add("ingest_overflow")
        cfg = settings(
            databento_api_key=SECRET, databento_historical_enabled=True
        )
        manager = ProviderManager(
            cfg, service, InstrumentCatalog(), historical_factory=lambda: FakeHistorical()
        )
        result = await manager.recover_gaps()
        return result, coverage, scope, service

    result, coverage, scope, service = asyncio.run(go())
    assert result["gaps_attempted"] == 1
    assert result["gaps_recovered"] == 0
    assert result["gaps_skipped"] == 1
    assert result["gaps_remaining"] == 1
    assert coverage.gaps(scope) == [(T0, T0 + NS)]
    assert "ingest_overflow" in service.degraded_reasons


def test_gap_recovery_enforces_total_historical_span_budget(tmp_path):
    from app.coverage_store import SQLiteCoverageTracker
    from app.ohlcv import OhlcvPipeline
    from app.ingest import OhlcvIngestionService
    from app.symbology import InstrumentResolver, SymbolMapping

    async def go():
        scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
        coverage = SQLiteCoverageTracker(str(tmp_path / "coverage.sqlite3"))
        coverage.add_gap(scope, T0, T0 + 2 * 3600 * NS)
        resolver = InstrumentResolver()
        resolver.add(SymbolMapping(
            provider="databento", dataset="GLBX.MDP3",
            publisher_id=1, instrument_id=101, raw_symbol="ESZ6",
            valid_from_ns=T0, valid_to_ns=T0 + 2 * 3600 * NS,
        ))
        service = OhlcvIngestionService(
            pipeline=OhlcvPipeline(), resolver=resolver, coverage=coverage
        )
        hist = FakeHistorical()
        cfg = settings(
            databento_api_key=SECRET,
            databento_historical_enabled=True,
            historical_window_minutes=60,
            historical_max_span_hours=2,
        )
        manager = ProviderManager(
            cfg, service, InstrumentCatalog(), historical_factory=lambda: hist
        )
        result = await manager.recover_gaps(max_total_span_hours=1)
        return result, hist, coverage, scope

    result, hist, coverage, scope = asyncio.run(go())
    assert result["gaps_attempted"] == 1
    assert result["gaps_recovered"] == 0
    assert result["gaps_remaining"] == 1
    assert result["windows_done"] == 1
    assert len(hist.calls) == 1
    assert hist.calls[0][4] - hist.calls[0][3] == 3600 * NS
    assert coverage.intervals(scope) == [(T0, T0 + 3600 * NS)]
    assert coverage.gaps(scope) == [(T0 + 3600 * NS, T0 + 2 * 3600 * NS)]



def test_reconciliation_and_explicit_gap_recovery_are_serialized():
    async def go():
        m, *_ = manager(hist=lambda: FakeHistorical(),
                        databento_historical_enabled=True)
        active = 0
        max_active = 0
        calls = []

        async def operation(name, result):
            nonlocal active, max_active
            active += 1
            max_active = max(max_active, active)
            calls.append((name, "start"))
            await asyncio.sleep(0.01)
            calls.append((name, "end"))
            active -= 1
            return result

        async def reconcile():
            return await operation("reconcile", {"ok": "reconcile"})

        async def recover(*, max_gaps=100, max_total_span_hours=None):
            return await operation("recover", {"ok": "recover"})

        m._reconcile_live_history_locked = reconcile
        m._recover_gaps_locked = recover
        results = await asyncio.gather(
            m.reconcile_live_history(),
            m.recover_gaps(max_gaps=5, max_total_span_hours=1),
        )
        return max_active, calls, results

    max_active, calls, results = asyncio.run(go())
    assert max_active == 1
    assert calls in (
        [("reconcile", "start"), ("reconcile", "end"),
         ("recover", "start"), ("recover", "end")],
        [("recover", "start"), ("recover", "end"),
         ("reconcile", "start"), ("reconcile", "end")],
    )
    assert results == [{"ok": "reconcile"}, {"ok": "recover"}]
