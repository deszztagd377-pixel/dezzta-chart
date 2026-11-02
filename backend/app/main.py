"""HTTP and WebSocket entry point for DEZZTA CHART.

Provider OHLCV ingestion is optional and disabled unless explicitly configured
(DATABENTO_API_KEY plus feature flags). Without them the backend starts
normally and reports the provider as disconnected. No market-data broadcast is
published over the WebSocket in this phase.
"""

import asyncio
import hmac
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.coverage import CoverageTracker
from app.databento_sources import DatabentoHistoricalSource, DatabentoLiveSource
from app.ingest import OhlcvIngestionService
from app.instruments import InstrumentCatalog
from app.ohlcv import (
    InvalidOhlcvBar,
    OhlcvPipeline,
    bucket_start_ns,
    decimal_to_string,
)
from app.provider import ProviderManager
from app.symbology import InstrumentResolver


def _parse_ns(value: str | None, name: str) -> int | None:
    if value is None:
        return None
    if not value.isdigit():
        raise HTTPException(status_code=422, detail=f"{name} must be a non-negative integer of nanoseconds.")
    return int(value)


def create_app(
    settings: Settings | None = None,
    *,
    live_source_factory=None,
    historical_source_factory=None,
) -> FastAPI:
    config = settings or Settings.from_environment()
    catalog = InstrumentCatalog(config.allowed_roots)
    ohlcv_pipeline = OhlcvPipeline()
    resolver = InstrumentResolver()
    ingestion = OhlcvIngestionService(
        pipeline=ohlcv_pipeline, resolver=resolver, coverage=CoverageTracker(),
        dataset=config.databento_dataset, queue_max=config.ohlcv_queue_max,
    )
    if live_source_factory is None and config.provider_configured:
        live_source_factory = lambda: DatabentoLiveSource(  # noqa: E731
            config.databento_api_key, config.databento_dataset, config.databento_live_symbols
        )
    if historical_source_factory is None and config.provider_configured:
        historical_source_factory = lambda: DatabentoHistoricalSource(  # noqa: E731
            config.databento_api_key, config.databento_dataset
        )
    provider = ProviderManager(
        config, ingestion, catalog,
        live_factory=live_source_factory, historical_factory=historical_source_factory,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await provider.start()
        try:
            yield
        finally:
            await provider.stop()

    application = FastAPI(
        title="DEZZTA CHART Backend",
        version="0.3.0",
        description="Secure backend foundation for DEZZTA CHART market data.",
        lifespan=lifespan,
    )
    application.state.ohlcv_pipeline = ohlcv_pipeline
    application.state.provider = provider
    application.state.resolver = resolver
    application.state.catalog = catalog

    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.cors_allowed_origins),
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Content-Type"],
    )

    @application.get("/health", tags=["operations"])
    async def health() -> dict[str, str]:
        """Liveness endpoint; deliberately reveals no secrets or feed state."""
        return {"status": "ok", "service": "dezzta-chart-backend"}

    @application.get("/v1/market-data/status", tags=["market-data"])
    async def market_data_status() -> dict[str, object]:
        """Honest status. Top-level legacy keys describe the (unimplemented) MBO
        stream; the ``ohlcv`` block describes the OHLCV-1s provider ingestion."""
        ohlcv_status = provider.status()
        return {
            "provider": "databento",
            "dataset": "GLBX.MDP3",
            "schema": "mbo",
            "state": "disconnected",
            "connected": False,
            "ingestion_implemented": False,
            "ohlcv_pipeline_available": True,
            "ohlcv_provider_connected": ohlcv_status["connected"],
            "instruments": list(config.allowed_roots),
            "ohlcv": ohlcv_status,
        }


    @application.get("/v1/ohlcv", tags=["market-data"])
    async def ohlcv_snapshot(
        dataset: str | None = None,
        publisher_id: int | None = None,
        instrument_id: int | None = None,
        timeframe: str | None = None,
        provider_name: str | None = Query(default=None, alias="provider"),
        raw_symbol: str | None = None,
        series_type: str | None = None,
        start_ns: str | None = None,
        end_ns: str | None = None,
        limit: int | None = Query(default=None, ge=1),
    ) -> dict[str, object]:
        """Return normalized OHLCV bars without inventing missing market data.

        New optional filters keep the old call shape valid. With ``limit`` (or
        the server cap) the NEWEST matching bars are returned chronologically
        and ``truncated`` tells whether more matched.
        """
        if timeframe is not None:
            try:
                bucket_start_ns(0, timeframe)
            except InvalidOhlcvBar as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
        start_value = _parse_ns(start_ns, "start_ns")
        end_value = _parse_ns(end_ns, "end_ns")
        if start_value is not None and end_value is not None and start_value >= end_value:
            raise HTTPException(status_code=422, detail="start_ns must be before end_ns.")

        effective_limit = min(limit or config.ohlcv_max_response_bars, config.ohlcv_max_response_bars)
        bars, total = ohlcv_pipeline.query(
            dataset=dataset, publisher_id=publisher_id, instrument_id=instrument_id,
            timeframe=timeframe, provider=provider_name, raw_symbol=raw_symbol,
            series_type=series_type, start_ns=start_value, end_ns=end_value,
            limit=effective_limit,
        )
        feed_state = provider.state
        if not bars:
            state = "unavailable"
            detail = (
                "No OHLCV bars are available; provider ingestion is not connected."
                if feed_state != "live"
                else "No OHLCV bars are available for this query yet."
            )
        else:
            state = "degraded" if feed_state in ("degraded", "recovering") else "ready"
            detail = None
        return {
            "type": "market_data.ohlcv.snapshot",
            "version": 1,
            "state": state,
            "feedState": feed_state,
            "timestampUnit": "nanoseconds",
            "priceRepresentation": "decimal-string",
            "count": len(bars),
            "truncated": total > len(bars),
            "bars": [
                {
                    "dataset": bar.dataset,
                    "provider": bar.provider,
                    "publisherId": bar.publisher_id,
                    "instrumentId": bar.instrument_id,
                    "rawSymbol": bar.raw_symbol,
                    "seriesType": bar.series_type,
                    "timeframe": bar.timeframe,
                    "tsStartNs": str(bar.ts_start_ns),
                    "open": decimal_to_string(bar.open),
                    "high": decimal_to_string(bar.high),
                    "low": decimal_to_string(bar.low),
                    "close": decimal_to_string(bar.close),
                    "volume": decimal_to_string(bar.volume),
                    "tsEventNs": str(bar.ts_event_ns),
                    "tsReceivedNs": str(bar.ts_received_ns),
                    "sequence": bar.sequence,
                    "sequenceOrigin": bar.sequence_origin,
                    "origin": bar.origin,
                    "completeness": bar.completeness,
                }
                for bar in bars
            ],
            "detail": detail,
        }

    @application.get("/v1/instruments", tags=["instruments"])
    async def instrument_catalog(root: str | None = None) -> dict[str, object]:
        """Return verified outright futures definitions currently in memory.

        An empty contract list is expected until a provider definition source
        is configured. No synthetic expiry or active contract is fabricated.
        """
        try:
            contracts = catalog.list_contracts(root)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        snapshot = catalog.snapshot()
        if root:
            normalized_root = root.upper()
            snapshot["supported_products"] = [
                product
                for product in snapshot["supported_products"]
                if product["root"] == normalized_root
            ]
            snapshot["requested_root"] = normalized_root
        snapshot["contracts"] = contracts
        snapshot["contract_count"] = len(contracts)
        return snapshot

    @application.websocket("/ws/market-data")
    async def market_data_socket(websocket: WebSocket) -> None:
        origin = websocket.headers.get("origin")
        if (
            origin
            and config.cors_allowed_origins
            and origin not in config.cors_allowed_origins
        ):
            await websocket.close(code=4403, reason="Origin not allowed")
            return

        await websocket.accept()

        if not config.market_data_ws_token:
            await websocket.close(
                code=1013,
                reason="WebSocket authentication is not configured",
            )
            return

        try:
            auth_message = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=5.0,
            )
        except (asyncio.TimeoutError, ValueError):
            await websocket.close(code=4401, reason="Authentication required")
            return
        except WebSocketDisconnect:
            return

        supplied_token = (
            auth_message.get("token")
            if isinstance(auth_message, dict)
            and auth_message.get("type") == "auth"
            else None
        )

        if not isinstance(supplied_token, str) or not hmac.compare_digest(
            supplied_token,
            config.market_data_ws_token,
        ):
            await websocket.close(code=4401, reason="Authentication failed")
            return

        await websocket.send_json(
            {
                "type": "market_data.status",
                "version": 1,
                "dataset": "GLBX.MDP3",
                "schema": "mbo",
                "instruments": list(config.allowed_roots),
                "quality": {
                    "state": "disconnected",
                    "bookSynchronized": False,
                    "detectedGapCount": 0,
                    "lastSequence": None,
                    "lastEventTsNs": None,
                    "lastReceiveTsNs": None,
                    "detail": "Provider ingestion has not been implemented.",
                },
            }
        )

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            return

    return application


app = create_app()
