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