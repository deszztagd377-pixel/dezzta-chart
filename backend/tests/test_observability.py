from app.observability import RequestMetrics


def test_request_metrics_caps_total_series_including_overflow_bucket():
    metrics = RequestMetrics()

    for index in range(300):
        metrics.record("GET", f"/resource/{index}", 200, float(index))

    snapshot = metrics.snapshot()
    latency = snapshot["latency_ms"]
    assert len(latency) == 127
    overflow = [
        item for item in latency
        if item["method"] == "OTHER" and item["route"] == "__overflow__"
    ]
    assert len(overflow) == 1
    assert overflow[0]["count"] == 174
    assert sum(item["count"] for item in latency) == 300


def test_request_metrics_sanitizes_unbounded_labels_and_invalid_values():
    metrics = RequestMetrics()
    metrics.record("TRACE", "/" + ("x" * 200), 503, -10)

    snapshot = metrics.snapshot()
    assert snapshot["requests"] == [{
        "method": "OTHER",
        "route": "unmatched",
        "status_class": "5xx",
        "count": 1,
    }]
    assert snapshot["latency_ms"] == [{
        "method": "OTHER",
        "route": "unmatched",
        "count": 1,
        "sum_ms": 0.0,
        "buckets": [
            {"le_ms": bound, "count": 1}
            for bound in (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000)
        ] + [{"le_ms": None, "count": 1}],
    }]


def test_request_metrics_snapshot_is_detached_from_internal_state():
    metrics = RequestMetrics()
    metrics.record("GET", "/health", 200, 4)

    snapshot = metrics.snapshot()
    snapshot["requests"][0]["count"] = 999
    snapshot["latency_ms"][0]["buckets"][0]["count"] = 999

    fresh = metrics.snapshot()
    assert fresh["requests"][0]["count"] == 1
    assert fresh["latency_ms"][0]["buckets"][0]["count"] == 1


def test_request_metrics_rejects_non_finite_and_boolean_durations():
    metrics = RequestMetrics()

    for value in (float("nan"), float("inf"), float("-inf"), True, "5"):
        metrics.record("GET", "/health", 200, value)

    snapshot = metrics.snapshot()
    assert snapshot["latency_ms"][0]["count"] == 5
    assert snapshot["latency_ms"][0]["sum_ms"] == 0.0
    assert all(bucket["count"] == 5 for bucket in snapshot["latency_ms"][0]["buckets"])


def test_request_metrics_caps_extreme_finite_duration_and_rejects_unhashable_labels():
    metrics = RequestMetrics()
    metrics.record(["GET"], "/health", True, float("nan"))
    metrics.record("GET", "/health", 200, 1e308)

    snapshot = metrics.snapshot()
    assert snapshot["requests"] == [
        {"method": "GET", "route": "/health", "status_class": "2xx", "count": 1},
        {"method": "OTHER", "route": "/health", "status_class": "other", "count": 1},
    ]
    assert snapshot["latency_ms"][0]["sum_ms"] == 86_400_000.0
    assert snapshot["latency_ms"][1]["sum_ms"] == 0.0


def test_request_metrics_concurrent_recording_preserves_all_samples():
    from concurrent.futures import ThreadPoolExecutor

    metrics = RequestMetrics()
    workers = 8
    samples_per_worker = 125

    def record_batch(worker_index):
        for sample_index in range(samples_per_worker):
            metrics.record("GET", "/health", 200, worker_index + sample_index / 1000)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        list(executor.map(record_batch, range(workers)))

    snapshot = metrics.snapshot()
    expected = workers * samples_per_worker
    assert snapshot["requests"] == [{
        "method": "GET", "route": "/health", "status_class": "2xx",
        "count": expected,
    }]
    histogram = snapshot["latency_ms"][0]
    assert histogram["count"] == expected
    assert histogram["buckets"][-1] == {"le_ms": None, "count": expected}
    assert all(
        left["count"] <= right["count"]
        for left, right in zip(histogram["buckets"], histogram["buckets"][1:])
    )


def test_request_metrics_saturates_counters_without_integer_or_float_overflow():
    from app.observability import _MAX_ACCUMULATED_MS, _MAX_COUNTER, _LATENCY_BUCKETS_MS

    metrics = RequestMetrics()
    key = ("GET", "/health")
    metrics._series.add(key)
    metrics._requests[("GET", "/health", "2xx")] = _MAX_COUNTER
    metrics._latency[key] = {
        "count": _MAX_COUNTER,
        "sum_ms": _MAX_ACCUMULATED_MS,
        "buckets": [_MAX_COUNTER for _ in _LATENCY_BUCKETS_MS],
    }

    metrics.record("GET", "/health", 200, 86_400_000.0)
    snapshot = metrics.snapshot()

    assert snapshot["requests"] == [{
        "method": "GET", "route": "/health", "status_class": "2xx",
        "count": _MAX_COUNTER,
    }]
    histogram = snapshot["latency_ms"][0]
    assert histogram["count"] == _MAX_COUNTER
    assert histogram["sum_ms"] == _MAX_ACCUMULATED_MS
    assert all(bucket["count"] == _MAX_COUNTER for bucket in histogram["buckets"])
    assert all(
        isinstance(bucket["count"], int) and bucket["count"] <= _MAX_COUNTER
        for bucket in histogram["buckets"]
    )
