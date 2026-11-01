"""HTTP and WebSocket entry point for DEZZTA CHART.

This is a backend foundation only. It does not connect to Databento or publish
market events yet. The WebSocket requires an application-level auth handshake.
"""

import asyncio
import hmac

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings.from_environment()
    application = FastAPI(
        title="DEZZTA CHART Backend",
        version="0.1.0",
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
            "instruments": ["ES", "NQ", "GC"],
        }

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
                "instruments": ["ES", "NQ", "GC"],
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

        # Keep the authenticated connection open. Market events will be
        # broadcast here only after the ingestion and recovery layers exist.
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            return

    return application


app = create_app()
