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


class WebSocketMetrics:
    """Bounded process-local lifecycle counters for the market-data WebSocket."""

    _CODE_CLASSES = ("1xxx", "2xxx", "4xxx", "5xxx", "other")

    def __init__(self) -> None:
        self._lock = Lock()
        self._started = 0
        self._active = 0
        self._completed = 0
        self._accepted = 0
        self._peer_disconnects = 0
        self._close_codes = {key: 0 for key in self._CODE_CLASSES}
        self._duration_sum_ms = 0.0

    def start(self) -> None:
        with self._lock:
            self._started = min(self._started + 1, _MAX_COUNTER)
            self._active = min(self._active + 1, _MAX_COUNTER)

    def finish(self, *, accepted: bool, peer_disconnect: bool, close_code: object, duration_ms: float) -> None:
        if isinstance(close_code, int) and not isinstance(close_code, bool) and 1000 <= close_code <= 5999:
            code_class = f"{close_code // 1000}xxx"
            if code_class not in self._close_codes:
                code_class = "other"
        else:
            code_class = "other"
        try:
            raw_duration = float(duration_ms) if isinstance(duration_ms, (int, float)) and not isinstance(duration_ms, bool) else 0.0
        except (OverflowError, ValueError):
            raw_duration = 0.0
        duration = min(max(raw_duration, 0.0), _MAX_DURATION_MS) if math.isfinite(raw_duration) else 0.0
        with self._lock:
            self._active = max(0, self._active - 1)
            self._completed = min(self._completed + 1, _MAX_COUNTER)
            if accepted:
                self._accepted = min(self._accepted + 1, _MAX_COUNTER)
            if peer_disconnect:
                self._peer_disconnects = min(self._peer_disconnects + 1, _MAX_COUNTER)
            self._close_codes[code_class] = min(self._close_codes[code_class] + 1, _MAX_COUNTER)
            self._duration_sum_ms = min(self._duration_sum_ms + duration, _MAX_ACCUMULATED_MS)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "schema_version": 1,
                "scope": "process_local_since_start",
                "connections_started": self._started,
                "connections_active": self._active,
                "connections_completed": self._completed,
                "connections_accepted": self._accepted,
                "peer_disconnects": self._peer_disconnects,
                "close_code_classes": dict(self._close_codes),
                "duration_sum_ms": round(self._duration_sum_ms, 3),
            }


class WebSocketMetricsMiddleware:
    """Observe lifecycle metadata only; never inspect WebSocket payloads or headers."""

    def __init__(self, app, *, metrics: WebSocketMetrics) -> None:
        self.app = app
        self.metrics = metrics

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") != "websocket" or scope.get("path") != "/ws/market-data":
            await self.app(scope, receive, send)
            return

        import time
        started_ns = time.monotonic_ns()
        accepted = False
        peer_disconnect = False
        close_code = None
        self.metrics.start()

        async def observed_receive():
            nonlocal peer_disconnect
            message = await receive()
            if message.get("type") == "websocket.disconnect":
                peer_disconnect = True
            return message

        async def observed_send(message):
            nonlocal accepted, close_code
            if message.get("type") == "websocket.accept":
                accepted = True
            elif message.get("type") == "websocket.close":
                close_code = message.get("code")
            await send(message)

        try:
            await self.app(scope, observed_receive, observed_send)
        finally:
            elapsed_ms = max(0.0, (time.monotonic_ns() - started_ns) / 1_000_000)
            self.metrics.finish(
                accepted=accepted,
                peer_disconnect=peer_disconnect,
                close_code=close_code,
                duration_ms=elapsed_ms,
            )
