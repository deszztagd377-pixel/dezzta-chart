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
    ticks = iter((100, 600, 3_600))
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
