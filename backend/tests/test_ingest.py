import threading
from decimal import Decimal
from types import SimpleNamespace

from app.ingest import BoundedBuffer
from helpers import NS, T0, make_service, rec


def test_buffer_overflow_is_counted_not_silent():
    buf = BoundedBuffer(2)
    assert buf.offer("a", 1, 1) and buf.offer("b", 2, 2)
    assert buf.offer("c", 3, 3) is False
    assert buf.overflow_count == 1 and buf.take_overflows() == [(None, 3, 3)]
    assert buf.drain(10) == ["a", "b"]


def test_buffer_is_safe_under_concurrent_producers():
    buf = BoundedBuffer(1000)
    def produce():
        for i in range(500):
            buf.offer(i, None, 0)
    threads = [threading.Thread(target=produce) for _ in range(4)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert len(buf) == 1000 and buf.overflow_count == 1000


def test_live_records_flow_through_one_writer_into_pipeline_and_aggregates():
    service, pipeline, *_ = make_service()
    for i in range(3):
        assert service.offer(rec(i, v=10), "ohlcv-1s")
    assert len(pipeline.list_bars()) == 0  # nothing mutates until the loop-side writer runs
    assert service.process_pending() == 3
    assert len(pipeline.list_bars(timeframe="1s")) == 3
    assert pipeline.list_bars(timeframe="1m")[0].volume == Decimal(30)
    assert service.last_event_ns == T0 + 2 * NS and service.last_receive_ns is not None
    assert service.last_receive_ns != service.last_event_ns  # separate timestamps


def test_local_sequence_is_monotonic_in_arrival_order_and_labelled_local():
    service, pipeline, *_ = make_service()
    for off in (5, 1, 3):
        service.offer(rec(off), "ohlcv-1s")
    service.process_pending()
    seqs = {b.ts_start_ns: b.sequence for b in pipeline.list_bars(timeframe="1s")}
    assert seqs[T0 + 5 * NS] < seqs[T0 + 1 * NS] < seqs[T0 + 3 * NS]
    assert {b.sequence_origin for b in pipeline.list_bars()} == {"local"}


def test_duplicates_stale_and_bad_records_are_counted_and_do_not_stop_processing():
    service, pipeline, *_ = make_service()
    batch = [
        rec(0), rec(0),                      # exact duplicate
        rec(1, instrument_id=999),           # unknown instrument
        SimpleNamespace(msg="system"),       # not an OHLCV record
        rec(2, c="100.2"), rec(2, c="100.3"),  # real revision
        rec(3, v=7.5),                       # malformed volume
    ]
    for r in batch:
        service.offer(r, "ohlcv-1s")
    service.process_pending()
    c = service.counters
    assert c["inserted"] == 2 and c["duplicate"] == 1 and c["replaced"] == 1
    assert c["rejected_unknown_instrument"] == 1 and c["rejected_unsupported_record"] == 1
    assert c["rejected_malformed"] == 1
    assert len(pipeline.list_bars(timeframe="1s")) == 2


def test_queue_overflow_marks_gap_and_degraded_instead_of_dropping_silently():
    service, pipeline, _, coverage = make_service(queue_max=2)
    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    coverage.add_covered(scope, T0, T0 + 5 * NS)
    for i in range(4):
        service.offer(rec(i), "ohlcv-1s")
    service.process_pending()
    status = service.status()
    assert status["overflow_count"] == 2 and "ingest_overflow" in status["degraded_reasons"]
    assert len(pipeline.list_bars(timeframe="1s")) == 2
    assert coverage.status(scope, T0 + 2 * NS, T0 + 4 * NS) != "covered"  # instrument-specific gap
    service.acknowledge_overflow()
    assert service.status()["degraded_reasons"] == []


def test_overflow_gap_persistence_failure_is_retried_without_stopping_ingestion():
    service, pipeline, _, coverage = make_service(queue_max=1)

    class FlakyCoverage:
        def __init__(self, delegate):
            self.delegate = delegate
            self.fail_once = True

        def add_gap(self, scope, start_ns, end_ns):
            if self.fail_once:
                self.fail_once = False
                raise OSError("temporary sqlite write failure")
            self.delegate.add_gap(scope, start_ns, end_ns)

    flaky = FlakyCoverage(coverage)
    service.coverage = flaky
    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    coverage.add_covered(scope, T0, T0 + 5 * NS)

    assert service.offer(rec(0), "ohlcv-1s")
    assert service.offer(rec(2), "ohlcv-1s") is False
    assert service.process_pending() == 1
    failed = service.status()
    assert failed["pending_overflow_gaps"] == 1
    assert "coverage_persistence_error" in failed["degraded_reasons"]
    assert "ingest_overflow" in failed["degraded_reasons"]
    assert len(pipeline.list_bars(timeframe="1s")) == 1

    # A later consumer wakeup retries the exact range instead of losing it.
    assert service.process_pending() == 0
    recovered = service.status()
    assert recovered["pending_overflow_gaps"] == 0
    assert "coverage_persistence_error" not in recovered["degraded_reasons"]
    assert coverage.intervals(scope) == [
        (T0, T0 + 2 * NS), (T0 + 3 * NS, T0 + 5 * NS)
    ]

    service.acknowledge_overflow()
    assert "ingest_overflow" not in service.status()["degraded_reasons"]


def test_consumer_retries_pending_overflow_gap_without_new_provider_events():
    import asyncio

    async def scenario():
        service, _, _, coverage = make_service(queue_max=1)

        class FlakyCoverage:
            def __init__(self, delegate):
                self.delegate = delegate
                self.failures_remaining = 2

            def add_gap(self, scope, start_ns, end_ns):
                if self.failures_remaining:
                    self.failures_remaining -= 1
                    raise OSError("temporary coverage database outage")
                self.delegate.add_gap(scope, start_ns, end_ns)

        flaky = FlakyCoverage(coverage)
        service.coverage = flaky
        scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
        coverage.add_covered(scope, T0, T0 + 5 * NS)
        service.attach_loop(asyncio.get_running_loop())
        task = asyncio.create_task(service.run())
        try:
            assert service.offer(rec(0), "ohlcv-1s")
            assert service.offer(rec(2), "ohlcv-1s") is False

            async def recovered():
                while (
                    service.counters.get("overflow_gap", 0) < 1
                    or service.status()["pending_overflow_gaps"]
                ):
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(recovered(), timeout=1.5)
            assert coverage.intervals(scope) == [
                (T0, T0 + 2 * NS), (T0 + 3 * NS, T0 + 5 * NS)
            ]
            assert "coverage_persistence_error" not in service.status()["degraded_reasons"]
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    asyncio.run(scenario())


def test_batch_backfill_does_not_extend_live_coverage_and_status_has_no_secret():
    service, _, _, coverage = make_service()
    service.ingest_batch([rec(0), rec(1)], "ohlcv-1s", live=False)
    assert coverage.intervals(("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")) == []
    assert "db-" not in repr(service.status())


def test_process_pending_is_batched():
    service, pipeline, *_ = make_service()
    service._batch = 2
    for i in range(5):
        service.offer(rec(i), "ohlcv-1s")
    assert [service.process_pending() for _ in range(4)] == [2, 2, 1, 0]

def test_live_records_do_not_claim_continuous_coverage():
    service, pipeline, _, coverage = make_service()
    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    service.ingest_batch([rec(0), rec(5)], "ohlcv-1s", live=True)
    assert coverage.status(scope, T0, T0 + 6 * NS) == "unknown"



def test_live_ingestion_latency_is_measured_with_monotonic_clock():
    ticks = iter((100, 600, 3_600, 4_000))
    service, pipeline, *_ = make_service()
    service._clock = lambda: T0 + 2 * NS
    service._monotonic = lambda: next(ticks)
    assert service.offer(rec(0), "ohlcv-1s")
    service.process_pending()
    latency = service.status()["live_latency"]
    assert latency["measurement_window"] == "last_256_accepted_live_records"
    assert latency["queue_delay"] == {
        "samples": 1, "p50_ms": 0.001, "p95_ms": 0.001, "max_ms": 0.001
    }
    assert latency["processing"] == {
        "samples": 1, "p50_ms": 0.003, "p95_ms": 0.003, "max_ms": 0.003
    }
    assert latency["callback_to_apply"]["p50_ms"] == 0.004
    assert latency["event_timestamp_clock_skew_samples"] == 0


def test_historical_backfill_does_not_pollute_live_latency_samples():
    service, *_ = make_service()
    service.ingest_batch([rec(0), rec(1)], "ohlcv-1s", live=False)
    latency = service.status()["live_latency"]
    assert latency["queue_delay"]["samples"] == 0
    assert latency["processing"]["samples"] == 0
    assert latency["callback_to_apply"]["samples"] == 0


def test_late_arrival_preserves_original_one_second_bucket_and_derived_timeframes():
    """A 2.5s receive delay must not shift event-time candles into newer buckets."""
    service, pipeline, *_ = make_service()
    delayed_receive_ns = T0 + 2_500_000_000
    service._clock = lambda: delayed_receive_ns

    # This record belongs to second 1 even though it arrives 2.5 seconds later.
    assert service.offer(rec(1, c="101"), "ohlcv-1s")
    service.process_pending()

    one_second = pipeline.list_bars(timeframe="1s")
    five_seconds = pipeline.list_bars(timeframe="5s")
    one_minute = pipeline.list_bars(timeframe="1m")

    assert len(one_second) == 1
    assert one_second[0].ts_start_ns == T0 + NS
    assert one_second[0].ts_received_ns == delayed_receive_ns
    assert len(five_seconds) == 1 and five_seconds[0].ts_start_ns == T0
    assert len(one_minute) == 1 and one_minute[0].ts_start_ns == T0
    assert one_second[0].close == five_seconds[0].close == one_minute[0].close

def test_per_instrument_observations_are_separate_and_quiet_is_not_called_stale():
    ticks = iter((10_000_000, 20_000_000, 30_000_000, 40_000_000, 50_000_000, 60_000_000))
    from app.symbology import SymbolMapping

    service, pipeline, resolver, _ = make_service()
    resolver.add(SymbolMapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1,
        instrument_id=202, raw_symbol="ESZ6B", valid_from_ns=0, valid_to_ns=None,
    ))
    service._monotonic = lambda: next(ticks)
    assert service.offer(rec(0, instrument_id=101), "ohlcv-1s")
    assert service.offer(rec(1, instrument_id=202), "ohlcv-1s")
    service.process_pending()
    observations = service.status()["instrument_observations"]
    assert observations["tracked_instruments"] == 2
    assert {item["instrument_id"] for item in observations["instruments"]} == {101, 202}
    assert all(item["health"] == "observed" for item in observations["instruments"])
    assert observations["staleness_classification"] == "not_inferred_from_OHLCV_silence"
    assert "No trade/no OHLCV update" in observations["quiet_instrument_note"]


def test_per_instrument_observations_are_bounded():
    from app.freshness import InstrumentObservationTracker

    tracker = InstrumentObservationTracker(max_instruments=2, monotonic_ns=lambda: 100)
    for instrument_id in (1, 2, 3):
        tracker.observe(
            dataset="GLBX.MDP3", publisher_id=1, instrument_id=instrument_id,
            raw_symbol=f"ES{instrument_id}", event_ns=instrument_id,
            received_ns=instrument_id, monotonic_received_ns=instrument_id,
        )
    status = tracker.status()
    assert status["tracked_instruments"] == 2
    assert status["evicted_instrument_counters"] == 1
    assert {item["instrument_id"] for item in status["instruments"]} == {2, 3}

def test_ingestion_restart_restores_pipeline_and_resumes_local_sequence(tmp_path):
    from app.coverage import CoverageTracker
    from app.ingest import OhlcvIngestionService
    from app.ohlcv import OhlcvPipeline
    from app.ohlcv_store import SQLiteOhlcvStore
    from helpers import make_resolver

    database_path = str(tmp_path / "restart.sqlite3")
    first = OhlcvIngestionService(
        pipeline=OhlcvPipeline(),
        resolver=make_resolver(),
        coverage=CoverageTracker(),
        persistence=SQLiteOhlcvStore(database_path),
    )
    first.ingest_batch([rec(0), rec(1)], "ohlcv-1s", live=False)
    original_snapshot = first.pipeline.list_bars()
    original_bars = first.pipeline.list_bars(timeframe="1s")
    assert [bar.sequence for bar in original_bars] == [1, 2]
    original_one_minute = first.pipeline.list_bars(timeframe="1m")
    assert len(original_one_minute) == 1
    assert original_one_minute[0].origin == "derived"
    assert original_one_minute[0].volume == Decimal(20)

    # A fresh service models process startup: persisted bars must be loaded
    # before new provider records are accepted.
    restarted = OhlcvIngestionService(
        pipeline=OhlcvPipeline(),
        resolver=make_resolver(),
        coverage=CoverageTracker(),
        persistence=SQLiteOhlcvStore(database_path),
    )
    restored = restarted.pipeline.list_bars()
    assert restored == original_snapshot

    # The next child must rebuild the same persisted parent buckets from the
    # complete restored child range, not just from post-restart arrivals.
    restarted.ingest_batch(
        [rec(2, c="102", h="103", v=20)], "ohlcv-1s", live=False
    )
    after_restart = restarted.pipeline.list_bars(timeframe="1s")
    assert [bar.sequence for bar in after_restart] == [1, 2, 3]
    assert after_restart[-1].ts_start_ns == T0 + 2 * NS

    rebuilt_one_minute = restarted.pipeline.list_bars(timeframe="1m")
    assert len(rebuilt_one_minute) == 1
    assert rebuilt_one_minute[0].origin == "derived"
    assert rebuilt_one_minute[0].open == Decimal("100")
    assert rebuilt_one_minute[0].high == Decimal("103")
    assert rebuilt_one_minute[0].close == Decimal("102")
    assert rebuilt_one_minute[0].volume == Decimal(40)

