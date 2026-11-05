"""Thin wrappers around the official ``databento`` SDK.

*** UNVERIFIED ***  This repository has never executed these wrappers against
the real SDK (no network/credentials in CI or in the authoring sandbox). The
calls below follow the SDK's documented client names (``databento.Live`` with
subscribe/add_callback/start/stop/block_for_close and
``databento.Historical().timeseries.get_range``) but argument types, exact
signatures and behaviour for the pinned SDK version are UNKNOWN until verified
by running them. The SDK is imported lazily so the backend (and CI) never need
it, an API key, or the network.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Callable

_NS = 1_000_000_000


def _iso(ns: int) -> str:
    """Format Unix nanoseconds as an exact UTC ISO-8601 timestamp.

    Databento accepts nanosecond-precision ISO-8601 strings. Do not truncate
    historical query boundaries to whole seconds: that can create overlap or
    gaps between adjacent backfill windows.
    """
    if not isinstance(ns, int) or isinstance(ns, bool) or ns < 0:
        raise ValueError("timestamp must be a non-negative integer of nanoseconds")
    seconds, fraction_ns = divmod(ns, _NS)
    whole = datetime.fromtimestamp(seconds, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    suffix = f".{fraction_ns:09d}" if fraction_ns else ""
    return f"{whole}{suffix}Z"


class DatabentoLiveSource:
    """Live ohlcv-1s session for EXPLICIT raw contract symbols only."""

    def __init__(self, api_key: str, dataset: str, symbols: tuple[str, ...], schema: str = "ohlcv-1s"):
        self._key, self._dataset, self._symbols, self._schema = api_key, dataset, symbols, schema
        self._client: Any = None

    def start(self, on_record: Callable[[Any], None], on_close: Callable[[BaseException | None], None]) -> None:
        import databento  # lazy: UNVERIFIED API surface

        # ts_out is a documented Live option: preserve the gateway-send timestamp
        # for downstream diagnostics. It does not by itself prove end-to-end latency.
        client = databento.Live(key=self._key, ts_out=True)
        client.subscribe(
            dataset=self._dataset, schema=self._schema,
            symbols=list(self._symbols), stype_in="raw_symbol",
        )
        client.add_callback(on_record)
        client.start()
        self._client = client

        def watch() -> None:
            error: BaseException | None = None
            try:
                client.block_for_close()
            except BaseException as exc:  # reported, then session considered closed
                error = exc
            on_close(error)

        threading.Thread(target=watch, name="databento-live-watch", daemon=True).start()

    def stop(self) -> None:
        client, self._client = self._client, None
        if client is not None:
            client.stop()


class DatabentoHistoricalSource:
    """One bounded get_range window per call (caller enforces window size)."""

    def __init__(self, api_key: str, dataset: str):
        self._key, self._dataset = api_key, dataset

    def fetch(self, *, schema: str, symbols: tuple[str, ...], stype_in: str,
              start_ns: int, end_ns: int) -> list[Any]:
        import databento  # lazy: UNVERIFIED API surface

        client = databento.Historical(self._key)
        store = client.timeseries.get_range(
            dataset=self._dataset, schema=schema, symbols=list(symbols),
            stype_in=stype_in, start=_iso(start_ns), end=_iso(end_ns),
        )
        return list(store)