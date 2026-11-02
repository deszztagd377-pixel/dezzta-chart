"""Shared deterministic fixtures for Phase 2 tests (no network, no SDK)."""
from decimal import Decimal
from types import SimpleNamespace

from app.coverage import CoverageTracker
from app.ingest import OhlcvIngestionService
from app.ohlcv import OhlcvPipeline
from app.symbology import InstrumentResolver, SymbolMapping

NS = 1_000_000_000
# 2024-01-01 00:00:00 UTC (Monday): aligned for every supported timeframe.
T0 = 1_704_067_200 * NS


def px(text: str) -> int:
    """Decimal text -> Databento fixed-point integer (1e-9), exact."""
    return int(Decimal(text) * NS)


def rec(offset_s: int, o="100", h="101", l="99", c="100.5", v=10,
        instrument_id=101, publisher_id=1, base=T0, **overrides):
    values = dict(
        open=px(o), high=px(h), low=px(l), close=px(c), volume=v,
        instrument_id=instrument_id, publisher_id=publisher_id,
        ts_event=base + offset_s * NS,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def make_resolver(symbol="ESZ6", instrument_id=101, publisher_id=1,
                  valid_from=0, valid_to=None, dataset="GLBX.MDP3"):
    resolver = InstrumentResolver()
    resolver.add(SymbolMapping(
        provider="databento", dataset=dataset, publisher_id=publisher_id,
        instrument_id=instrument_id, raw_symbol=symbol,
        valid_from_ns=valid_from, valid_to_ns=valid_to,
    ))
    return resolver


def make_service(queue_max=1000, resolver=None, retention=None, clock=None):
    pipeline = OhlcvPipeline(retention)
    resolver = resolver or make_resolver()
    coverage = CoverageTracker()
    ticks = iter(range(10**6))
    service = OhlcvIngestionService(
        pipeline=pipeline, resolver=resolver, coverage=coverage,
        queue_max=queue_max, clock_ns=clock or (lambda: T0 + 5_000 * NS + next(ticks)),
    )
    return service, pipeline, resolver, coverage