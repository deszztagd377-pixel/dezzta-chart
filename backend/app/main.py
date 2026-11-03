"""HTTP and WebSocket entry point for DEZZTA CHART.

Provider OHLCV ingestion is optional and disabled unless explicitly configured
(DATABENTO_API_KEY plus feature flags). Without them the backend starts
normally and reports the provider as disconnected. Authenticated WebSocket
clients can subscribe to the in-memory OHLCV pipeline when validated bars exist.
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
from app.instrument_registry import SQLiteInstrumentRegistry
from app.alert_store import SQLitePriceAlertStore
from app.ohlcv import (
    InvalidOhlcvBar,
    OhlcvPipeline,
    bucket_start_ns,
    decimal_to_string,
)
from app.provider import ProviderManager
from app.ohlcv_stream import OhlcvStreamHub
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
    instrument_registry = SQLiteInstrumentRegistry(config.instrument_registry_db_path)
    # Durable alert storage is initialized, but no public alert routes are
    # enabled until Firebase identity and instrument entitlements are verified.
    price_alert_store = SQLitePriceAlertStore(config.instrument_registry_db_path)
    ohlcv_pipeline = OhlcvPipeline()
    resolver = InstrumentResolver()
    stream_hub = OhlcvStreamHub()
    ingestion = OhlcvIngestionService(
        pipeline=ohlcv_pipeline, resolver=resolver, coverage=CoverageTracker(),
        dataset=config.databento_dataset, queue_max=config.ohlcv_queue_max,
        on_bar_applied=stream_hub.publish,
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
    application.state.ohlcv_stream_hub = stream_hub
    application.state.provider = provider
    application.state.resolver = resolver
    application.state.catalog = catalog
    # Internal persistence adapter only. Public write routes stay disabled until
    # Firebase identity and per-instrument entitlement checks are implemented.
    application.state.instrument_registry = instrument_registry
    application.state.price_alert_store = price_alert_store

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
                "dataset": config.databento_dataset,
                "schema": "ohlcv",
                "instruments": list(config.allowed_roots),
                "quality": {
                    "state": provider.state,
                    "lastEventTsNs": None if ingestion.last_event_ns is None else str(ingestion.last_event_ns),
                    "lastReceiveTsNs": None if ingestion.last_receive_ns is None else str(ingestion.last_receive_ns),
                    "detail": "Authenticated OHLCV subscription is available; no order-book stream is provided.",
                },
            }
        )

        subscription = None
        try:
            try:
                request = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
            except asyncio.TimeoutError:
                await websocket.close(code=4408, reason="Subscription request timed out")
                return
            if not isinstance(request, dict) or request.get("type") != "market_data.subscribe" or request.get("version") != 1:
                await websocket.close(code=4400, reason="A version 1 OHLCV subscription is required")
                return
            identity = request.get("series")
            if not isinstance(identity, dict):
                await websocket.close(code=4400, reason="Exact OHLCV series identity is required")
                return
            dataset = identity.get("dataset")
            raw_symbol = identity.get("rawSymbol")
            timeframe = identity.get("timeframe")
            publisher_id = identity.get("publisherId")
            instrument_id = identity.get("instrumentId")
            if (
                dataset != config.databento_dataset
                or not isinstance(raw_symbol, str) or not raw_symbol.strip()
                or not isinstance(timeframe, str)
                or not isinstance(publisher_id, int) or isinstance(publisher_id, bool) or publisher_id <= 0
                or not isinstance(instrument_id, int) or isinstance(instrument_id, bool) or instrument_id <= 0
            ):
                await websocket.close(code=4400, reason="Invalid or unsupported OHLCV series identity")
                return
            try:
                bucket_start_ns(0, timeframe)
            except InvalidOhlcvBar:
                await websocket.close(code=4400, reason="Unsupported OHLCV timeframe")
                return

            # No await occurs between snapshot query and stream registration.
            # Ingestion and fan-out share this event loop, so this watermark is
            # an atomic boundary: later accepted revisions enter the queue.
            subscription, snapshot_bars, total = stream_hub.subscribe_snapshot(
                ohlcv_pipeline,
                dataset=dataset,
                publisher_id=publisher_id,
                instrument_id=instrument_id,
                raw_symbol=raw_symbol,
                timeframe=timeframe,
                limit=config.ohlcv_max_response_bars,
            )
            feed_state = provider.state
            snapshot_state = "ready" if snapshot_bars else "unavailable"
            await websocket.send_json({
                "type": "market_data.ohlcv.snapshot",
                "version": 1,
                "state": snapshot_state,
                "feedState": feed_state,
                "timestampUnit": "nanoseconds",
                "priceRepresentation": "decimal-string",
                "count": len(snapshot_bars),
                "truncated": total > len(snapshot_bars),
                "detail": None if snapshot_bars else "No validated bars match this exact series yet.",
                "streamId": subscription.stream_id,
                "watermark": subscription.watermark,
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
                    for bar in snapshot_bars
                ],
            })

            receive_task = asyncio.create_task(websocket.receive_text())
            queue_task = None
            try:
                while True:
                    if subscription.overflowed:
                        await websocket.close(code=1013, reason="OHLCV client queue overflow; reconnect and resnapshot")
                        return
                    queue_task = asyncio.create_task(subscription.queue.get())
                    done, _ = await asyncio.wait(
                        {receive_task, queue_task},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    if receive_task in done:
                        try:
                            client_message = receive_task.result()
                        except WebSocketDisconnect:
                            return
                        if client_message == "ping":
                            await websocket.send_json({"type": "market_data.pong", "version": 1})
                        receive_task = asyncio.create_task(websocket.receive_text())
                    if queue_task in done:
                        if subscription.overflowed:
                            await websocket.close(code=1013, reason="OHLCV client queue overflow; reconnect and resnapshot")
                            return
                        await websocket.send_json(queue_task.result())
                        queue_task = None
                    else:
                        queue_task.cancel()
                        try:
                            await queue_task
                        except asyncio.CancelledError:
                            pass
                        queue_task = None
            finally:
                if queue_task is not None and not queue_task.done():
                    queue_task.cancel()
                    try:
                        await queue_task
                    except asyncio.CancelledError:
                        pass
                receive_task.cancel()
                try:
                    await receive_task
                except (asyncio.CancelledError, WebSocketDisconnect):
                    pass
        except WebSocketDisconnect:
            return
        finally:
            if subscription is not None:
                stream_hub.unsubscribe(subscription.stream_id)

    return application


app = create_app()
