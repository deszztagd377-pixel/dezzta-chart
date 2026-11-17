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
