"""HTTP and WebSocket entry point for DEZZTA CHART.

The backend currently exposes an instrument-catalog foundation. It does not
connect to Databento or publish market events yet.
"""

import asyncio
import hmac

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.instruments import InstrumentCatalog, SUPPORTED_PRODUCTS
from app.ohlcv import InvalidOhlcvBar, OhlcvPipeline, bucket_start_ns


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings.from_environment()
    catalog = InstrumentCatalog()
    ohlcv_pipeline = OhlcvPipeline()
    application = FastAPI(
        title="DEZZTA CHART Backend",
        version="0.2.0",
        description="Secure backend foundation for DEZZTA CHART market data.",
    )

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
        """Report honest scaffold status until a provider adapter exists."""
        return {
            "provider": "databento",
            "dataset": "GLBX.MDP3",
            "schema": "mbo",
            "state": "disconnected",
            "connected": False,
            "ingestion_implemented": False,
            "ohlcv_pipeline_available": True,
            "ohlcv_provider_connected": False,
            "instruments": list(SUPPORTED_PRODUCTS),
        }


    @application.get("/v1/ohlcv", tags=["market-data"])
    async def ohlcv_snapshot(
        dataset: str | None = None,
        publisher_id: int | None = None,
        instrument_id: int | None = None,
        timeframe: str | None = None,
    ) -> dict[str, object]:
        """Return normalized OHLCV bars without inventing missing market data.

        The in-memory pipeline is ready for a provider adapter, but no provider
        is connected by this scaffold. An empty response is therefore expected.
        """
        if timeframe is not None:
            try:
                bucket_start_ns(0, timeframe)
            except InvalidOhlcvBar as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

        bars = ohlcv_pipeline.list_bars(
            dataset=dataset,
            publisher_id=publisher_id,
            instrument_id=instrument_id,
            timeframe=timeframe,
        )
        return {
            "type": "market_data.ohlcv.snapshot",
            "version": 1,
            "state": "ready" if bars else "unavailable",
            "timestampUnit": "nanoseconds",
            "priceRepresentation": "decimal-string",
            "bars": [
                {
                    "dataset": bar.dataset,
                    "publisherId": bar.publisher_id,
                    "instrumentId": bar.instrument_id,
                    "rawSymbol": bar.raw_symbol,
                    "timeframe": bar.timeframe,
                    "tsStartNs": str(bar.ts_start_ns),
                    "open": str(bar.open),
                    "high": str(bar.high),
                    "low": str(bar.low),
                    "close": str(bar.close),
                    "volume": str(bar.volume),
                    "tsEventNs": str(bar.ts_event_ns),
                    "tsReceivedNs": str(bar.ts_received_ns),
                    "sequence": bar.sequence,
                }
                for bar in bars
            ],
            "detail": (
                None if bars
                else "No OHLCV bars are available; provider ingestion is not connected."
            ),
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
                "instruments": list(SUPPORTED_PRODUCTS),
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
