"""Bounded, process-local HTTP request metrics for private operations scraping."""
import math
from threading import Lock

_LATENCY_BUCKETS_MS = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000)
_MAX_DURATION_MS = 86_400_000.0  # One day; keep pathological samples finite and bounded.
_ALLOWED_METHODS = frozenset(("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"))
_MAX_ROUTE_SERIES = 127
# Keep every exported integer exactly representable by common JSON consumers.
_MAX_COUNTER = (1 << 53) - 1
_MAX_ACCUMULATED_MS = _MAX_DURATION_MS * _MAX_COUNTER


class RequestMetrics:
    """Low-cardinality counters and latency histograms without user data."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._series: set[tuple[str, str]] = set()
        self._requests: dict[tuple[str, str, str], int] = {}
        self._latency: dict[tuple[str, str], dict[str, object]] = {}

    def record(self, method: str, route: str, status_code: int, duration_ms: float) -> None:
        method = method if isinstance(method, str) and method in _ALLOWED_METHODS else "OTHER"
        route = route if isinstance(route, str) and route.startswith("/") and len(route) <= 160 else "unmatched"
        status = (
            f"{status_code // 100}xx"
            if isinstance(status_code, int)
            and not isinstance(status_code, bool)
            and 100 <= status_code <= 599
            else "other"
        )
        try:
            raw_duration = (
                float(duration_ms)
                if isinstance(duration_ms, (int, float)) and not isinstance(duration_ms, bool)
                else 0.0
            )
        except (OverflowError, ValueError):
            raw_duration = 0.0
        duration = (
            min(max(0.0, raw_duration), _MAX_DURATION_MS)
            if math.isfinite(raw_duration)
            else 0.0
        )
        key = (method, route)
        with self._lock:
            if key not in self._series:
                # Reserve one slot for the shared overflow series so the
                # configured maximum includes, rather than adds to, overflow.
                if len(self._series) >= _MAX_ROUTE_SERIES - 1:
                    key = ("OTHER", "__overflow__")
                self._series.add(key)
            request_key = (key[0], key[1], status)
            self._requests[request_key] = min(
                self._requests.get(request_key, 0) + 1, _MAX_COUNTER
            )
            metric = self._latency.get(key)
            if metric is None:
                metric = {"count": 0, "sum_ms": 0.0, "buckets": [0 for _ in _LATENCY_BUCKETS_MS]}
                self._latency[key] = metric
            metric["count"] = min(int(metric["count"]) + 1, _MAX_COUNTER)
            metric["sum_ms"] = min(
                float(metric["sum_ms"]) + duration, _MAX_ACCUMULATED_MS
            )
            for index, bound in enumerate(_LATENCY_BUCKETS_MS):
                if duration <= bound:
                    metric["buckets"][index] = min(
                        metric["buckets"][index] + 1, _MAX_COUNTER
                    )

    def snapshot(self) -> dict[str, object]:
        """Return a detached JSON-safe snapshot with no caller-controlled labels."""
        with self._lock:
            requests = [
                {"method": m, "route": r, "status_class": s, "count": n}
                for (m, r, s), n in sorted(self._requests.items())
            ]
            latency = []
            for (method, route), metric in sorted(self._latency.items()):
                latency.append({
                    "method": method, "route": route, "count": metric["count"],
                    "sum_ms": round(float(metric["sum_ms"]), 3),
                    "buckets": [
                        {"le_ms": bound, "count": metric["buckets"][i]}
                        for i, bound in enumerate(_LATENCY_BUCKETS_MS)
                    ] + [{"le_ms": None, "count": metric["count"]}],
                })
        return {"schema_version": 1, "scope": "process_local_since_start",
                "requests": requests, "latency_ms": latency}
