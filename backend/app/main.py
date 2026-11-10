"""HTTP and WebSocket entry point for DEZZTA CHART.

Provider OHLCV ingestion is optional and disabled unless explicitly configured
(DATABENTO_API_KEY plus feature flags). Without them the backend starts
normally and reports the provider as disconnected. Authenticated WebSocket
clients can subscribe to the in-memory OHLCV pipeline when validated bars exist.
"""

import asyncio
import time
from uuid import uuid4
from collections import deque
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.coverage_store import SQLiteCoverageTracker
from app.databento_sources import DatabentoHistoricalSource, DatabentoLiveSource
from app.ingest import OhlcvIngestionService
from app.instruments import InstrumentCatalog
from app.instrument_registry import SQLiteInstrumentRegistry
from app.alert_store import SQLitePriceAlertStore
from app.entitlements import SQLiteInstrumentEntitlementStore
from app.identity import (
    FirebaseIdentityVerifier,
    IdentityProviderUnavailable,
    IdentityVerificationError,
    VerifiedPrincipal,
)
from app.ohlcv import (
    SUPPORTED_BUCKET_POLICIES,
    InvalidOhlcvBar,
    OhlcvPipeline,
    bucket_policy_for_timeframe,
    bucket_start_ns,
    decimal_to_string,
)
from app.provider import ProviderManager
from app.databento_definition_sync import DatabentoDefinitionSynchronizer
from app.ohlcv_stream import OhlcvStreamHub
from app.ohlcv_store import SQLiteOhlcvStore
from app.symbology import InstrumentResolver
from app.shared_guard import RedisSharedGuard
from app.session_calendar_runtime import (
    build_provider_session_bar_validator,
    load_session_calendar_runtime,
)


WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS = 60.0
WEBSOCKET_PING_WINDOW_SECONDS = 10.0
WEBSOCKET_MAX_PINGS_PER_WINDOW = 20
MAX_WEBSOCKET_RAW_SYMBOL_LENGTH = 128
MAX_WEBSOCKET_TIMEFRAME_LENGTH = 16
MAX_WEBSOCKET_CANONICAL_ID_LENGTH = 36
MAX_OHLCV_RESPONSE_BARS = 5_000
MAX_WEBSOCKET_REPLAY_EVENTS = 10_000
MAX_SQLITE_CURSOR = (1 << 63) - 1
MAX_NANOSECOND_TIMESTAMP = (1 << 63) - 1


def _allow_websocket_ping(ping_timestamps: deque[float], now: float) -> bool:
    cutoff = now - WEBSOCKET_PING_WINDOW_SECONDS
    while ping_timestamps and ping_timestamps[0] <= cutoff:
        ping_timestamps.popleft()
    if len(ping_timestamps) >= WEBSOCKET_MAX_PINGS_PER_WINDOW:
        return False
    ping_timestamps.append(now)
    return True


def _parse_ns(value: str | None, name: str) -> int | None:
    if value is None:
        return None
    if not value.isdigit():
        raise HTTPException(status_code=422, detail=f"{name} must be a non-negative integer of nanoseconds.")
    timestamp_ns = int(value)
    if timestamp_ns > MAX_NANOSECOND_TIMESTAMP:
        raise HTTPException(
            status_code=422,
            detail=f"{name} exceeds the supported signed 64-bit nanosecond range.",
        )
    return timestamp_ns


def create_app(
    settings: Settings | None = None,
    *,
    live_source_factory=None,
    historical_source_factory=None,
    shared_guard=None,
) -> FastAPI:
    config = settings or Settings.from_environment()
    if shared_guard is None and config.redis_url:
        shared_guard = RedisSharedGuard(
            config.redis_url,
            http_per_client_per_minute=config.http_rate_limit_per_client,
            http_global_per_minute=config.http_rate_limit_global,
            websocket_global_limit=config.websocket_connection_limit_global,
            websocket_per_account_limit=config.websocket_connection_limit_per_account,
            websocket_lease_seconds=config.websocket_lease_seconds,
        )
    max_ohlcv_response_bars = min(
        max(1, config.ohlcv_max_response_bars),
        MAX_OHLCV_RESPONSE_BARS,
    )
    catalog = InstrumentCatalog(config.allowed_roots)
    instrument_registry = SQLiteInstrumentRegistry(config.instrument_registry_db_path)
    # Durable alert storage is initialized, but no public alert routes are
    # enabled until Firebase identity and instrument entitlements are verified.
    price_alert_store = SQLitePriceAlertStore(config.instrument_registry_db_path)
    instrument_entitlements = SQLiteInstrumentEntitlementStore(config.instrument_registry_db_path)
    identity_verifier = FirebaseIdentityVerifier(config.firebase_project_id)
    ohlcv_pipeline = OhlcvPipeline()
    resolver = InstrumentResolver()
    stream_hub = OhlcvStreamHub()
    ohlcv_store = SQLiteOhlcvStore(config.instrument_registry_db_path)

    def publish_persisted_bar(bar) -> None:
        # Resolve the exact revision: derived-timeframe persistence may occur
        # before the source bar's notification callback.
        event = ohlcv_store.outbox_event_for_bar(bar)
        if event is None:
            raise RuntimeError("Persisted OHLCV outbox event is missing.")
        stream_hub.publish(
            bar,
            durable_cursor=event["cursor"],
            durable_event_id=event["eventId"],
        )

    coverage_tracker = SQLiteCoverageTracker(config.instrument_registry_db_path)
    session_calendar_registry, session_calendar_status = load_session_calendar_runtime(
        artifact_path=config.session_calendar_artifact_path,
        expected_sha256=config.session_calendar_sha256,
        expected_version=config.session_calendar_version,
    )
    session_bar_validator = build_provider_session_bar_validator(
        instrument_registry,
        session_calendar_registry,
        calendar_version=config.session_calendar_version,
    )
    ingestion = OhlcvIngestionService(
        pipeline=ohlcv_pipeline, resolver=resolver, coverage=coverage_tracker,
        dataset=config.databento_dataset, queue_max=config.ohlcv_queue_max,
        on_bar_applied=publish_persisted_bar,
        persistence=ohlcv_store,
        bar_validator=session_bar_validator,
    )
    if live_source_factory is None and config.provider_configured:
        live_source_factory = lambda: DatabentoLiveSource(  # noqa: E731
            config.databento_api_key, config.databento_dataset, config.databento_live_symbols
        )
    if historical_source_factory is None and config.provider_configured:
        historical_source_factory = lambda: DatabentoHistoricalSource(  # noqa: E731
            config.databento_api_key, config.databento_dataset
        )
    definition_sync = DatabentoDefinitionSynchronizer(
        config.instrument_registry_db_path,
        instrument_registry,
        catalog,
        resolver,
        provider="databento",
        dataset=config.databento_dataset,
    )
    provider = ProviderManager(
        config, ingestion, catalog,
        live_factory=live_source_factory,
        historical_factory=historical_source_factory,
        definition_sync=definition_sync,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            if shared_guard is not None:
                await shared_guard.start()
            await provider.start()
            try:
                yield
            finally:
                await provider.stop()
        finally:
            if shared_guard is not None:
                await shared_guard.close()

    application = FastAPI(
        title="DEZZTA CHART Backend",
        version="0.3.0",
        description="Secure backend foundation for DEZZTA CHART market data.",
        lifespan=lifespan,
    )
    application.state.ohlcv_pipeline = ohlcv_pipeline
    application.state.ohlcv_stream_hub = stream_hub
    application.state.ohlcv_store = ohlcv_store
    application.state.coverage_tracker = coverage_tracker
    application.state.ingestion = ingestion
    application.state.session_calendar_registry = session_calendar_registry
    application.state.session_calendar_status = session_calendar_status
    application.state.provider = provider
    application.state.definition_sync = definition_sync
    application.state.resolver = resolver
    application.state.catalog = catalog
    # Internal persistence adapter only. Public write routes stay disabled until
    # Firebase identity and per-instrument entitlement checks are implemented.
    application.state.instrument_registry = instrument_registry
    application.state.price_alert_store = price_alert_store
    application.state.instrument_entitlements = instrument_entitlements
    application.state.identity_verifier = identity_verifier
    application.state.shared_guard = shared_guard
    application.state.shared_guard_enabled = shared_guard is not None

    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.cors_allowed_origins),
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @application.middleware("http")
    async def api_security_headers(request, call_next):
        if shared_guard is not None and request.url.path.startswith("/v1/"):
            client_identity = request.client.host if request.client is not None else "unknown"
            try:
                allowed, retry_after = await shared_guard.allow_http(client_identity or "unknown")
            except Exception:
                return JSONResponse(
                    status_code=503,
                    content={"detail": "Shared request protection is temporarily unavailable."},
                    headers={
                        "Retry-After": "5",
                        "Cache-Control": "private, no-store, max-age=0",
                        "X-Content-Type-Options": "nosniff",
                        "X-Frame-Options": "DENY",
                        "Referrer-Policy": "no-referrer",
                        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
                        "Pragma": "no-cache",
                        "Expires": "0",
                    },
                )
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Request rate limit exceeded."},
                    headers={
                        "Retry-After": str(retry_after),
                        "Cache-Control": "private, no-store, max-age=0",
                        "X-Content-Type-Options": "nosniff",
                        "X-Frame-Options": "DENY",
                        "Referrer-Policy": "no-referrer",
                        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
                        "Pragma": "no-cache",
                        "Expires": "0",
                    },
                )
        response = await call_next(request)
        if request.url.path == "/health" or request.url.path.startswith("/v1/"):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Permissions-Policy"] = (
                "camera=(), microphone=(), geolocation=()"
            )
            response.headers["Cache-Control"] = "private, no-store, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    async def require_verified_principal(
        authorization: str | None = Header(default=None),
    ) -> VerifiedPrincipal:
        """Resolve account identity exclusively from a verified Bearer token."""
        if not isinstance(authorization, str) or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Bearer authentication is required.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = authorization[7:].strip()
        if not token or " " in token:
            raise HTTPException(
                status_code=401,
                detail="Bearer authentication is required.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            # Firebase Admin verification can perform network I/O (including revocation checks).
            # Keep this synchronous SDK call off the ASGI event loop.
            return await asyncio.to_thread(application.state.identity_verifier.verify, token)
        except IdentityProviderUnavailable as exc:
            raise HTTPException(
                status_code=503,
                detail="Identity verification is temporarily unavailable.",
            ) from exc
        except IdentityVerificationError as exc:
            raise HTTPException(
                status_code=401,
                detail="Identity token is invalid or expired.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    @application.get("/v1/auth/session", tags=["authentication"])
    async def auth_session(
        principal: VerifiedPrincipal = Depends(require_verified_principal),
    ) -> dict[str, object]:
        """Return the authenticated account subject; never accept client owner IDs."""
        return {
            "authenticated": True,
            "subject": principal.subject,
            "issuer": principal.issuer,
            "audience": principal.audience,
        }

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
            "dataset": config.databento_dataset,
            "schema": "mbo",
            "state": "disconnected",
            "connected": False,
            "ingestion_implemented": False,
            "ohlcv_pipeline_available": True,
            "ohlcv_provider_connected": ohlcv_status["connected"],
            "instruments": list(config.allowed_roots),
            "session_calendar": application.state.session_calendar_status,
            "ohlcv": ohlcv_status,
        }


    @application.get("/v1/ohlcv", tags=["market-data"])
    async def ohlcv_snapshot(
        dataset: str = Query(min_length=1, max_length=64),
        publisher_id: int = Query(ge=1, le=2_147_483_647),
        instrument_id: int = Query(ge=1, le=2_147_483_647),
        timeframe: str = Query(min_length=1, max_length=16),
        raw_symbol: str = Query(min_length=1, max_length=128),
        provider_name: str | None = Query(default=None, alias="provider", max_length=32),
        series_type: str | None = Query(default=None, max_length=32),
        start_ns: str | None = Query(default=None, max_length=19),
        end_ns: str | None = Query(default=None, max_length=19),
        limit: int | None = Query(default=None, ge=1, le=5_000),
        bucket_policy: str | None = Query(default=None, max_length=32),
        calendar_id: str = Query(default="", max_length=128),
        calendar_version: str = Query(default="", max_length=64),
        principal: VerifiedPrincipal = Depends(require_verified_principal),
    ) -> dict[str, object]:
        """Return an exact OHLCV series after Firebase identity and entitlement checks.

        The account subject is derived only from a verified Bearer token. The
        server resolves the provider mapping and checks the active canonical
        instrument plus the account's explicit entitlement before querying bars.
        """
        # Require one exact provider series and authorize it against the
        # verified account before reading any licensed market-data bars.
        if dataset.strip().upper() != config.databento_dataset.strip().upper():
            raise HTTPException(status_code=403, detail="Instrument access denied.")
        if provider_name is not None and provider_name.strip().lower() != "databento":
            raise HTTPException(status_code=403, detail="Instrument access denied.")

        normalized_symbol = raw_symbol.strip().upper()
        if not normalized_symbol:
            raise HTTPException(status_code=422, detail="raw_symbol is required.")

        def authorized_series_type() -> str | None:
            mapping = application.state.instrument_registry.resolve_provider_mapping(
                provider="databento", dataset=dataset, publisher_id=publisher_id,
                instrument_id=instrument_id, timestamp_ns=time.time_ns(),
            )
            if (
                mapping is None or mapping.raw_symbol != normalized_symbol
                or (series_type is not None and mapping.series_type != series_type)
            ):
                return None
            instrument = application.state.instrument_registry.get_instrument(mapping.canonical_id)
            if instrument is None or not instrument.is_active:
                return None
            if not application.state.instrument_entitlements.has_access(
                subject=principal.subject, canonical_instrument_id=mapping.canonical_id,
            ):
                return None
            return mapping.series_type

        try:
            effective_series_type = await asyncio.to_thread(authorized_series_type)
        except Exception:
            effective_series_type = None
        if effective_series_type is None:
            raise HTTPException(status_code=403, detail="Instrument access denied.")

        try:
            bucket_start_ns(0, timeframe)
        except InvalidOhlcvBar as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        effective_bucket_policy = (
            bucket_policy if bucket_policy is not None else bucket_policy_for_timeframe(timeframe)
        )
        if effective_bucket_policy not in SUPPORTED_BUCKET_POLICIES or calendar_id or calendar_version:
            raise HTTPException(status_code=422, detail="Unsupported OHLCV bucket identity.")
        start_value = _parse_ns(start_ns, "start_ns")
        end_value = _parse_ns(end_ns, "end_ns")
        if start_value is not None and end_value is not None and start_value >= end_value:
            raise HTTPException(status_code=422, detail="start_ns must be before end_ns.")

        effective_limit = min(limit or max_ohlcv_response_bars, max_ohlcv_response_bars)
        bars, total = ohlcv_pipeline.query(
            dataset=dataset.strip().upper(), publisher_id=publisher_id, instrument_id=instrument_id,
            timeframe=timeframe, provider="databento", raw_symbol=normalized_symbol,
            series_type=effective_series_type, bucket_policy=effective_bucket_policy,
            calendar_id=calendar_id, calendar_version=calendar_version,
            start_ns=start_value, end_ns=end_value, limit=effective_limit,
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
                    "bucketPolicy": bar.bucket_policy,
                    "calendarId": bar.calendar_id,
                    "calendarVersion": bar.calendar_version,
                    "tsStartNs": str(bar.ts_start_ns),
                    "open": decimal_to_string(bar.open),
                    "high": decimal_to_string(bar.high),
                    "low": decimal_to_string(bar.low),
                    "close": decimal_to_string(bar.close),
                    "volume": decimal_to_string(bar.volume),
                    "tsEventNs": str(bar.ts_event_ns),
                    "tsReceivedNs": str(bar.ts_received_ns),
                    "tsProviderOutNs": None if bar.ts_provider_out_ns is None else str(bar.ts_provider_out_ns),
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
        # Expose a canonical ID only when the durable registry has an
        # active provider mapping for this exact Databento contract at the
        # current time. Never derive IDs from symbols or provider integers.
        enriched_contracts = []
        for contract in contracts:
            mapping = instrument_registry.resolve_provider_mapping(
                provider="databento",
                dataset=contract["dataset"],
                publisher_id=contract["publisher_id"],
                instrument_id=contract["instrument_id"],
                timestamp_ns=time.time_ns(),
            )
            canonical_id = None
            if mapping is not None and mapping.raw_symbol == contract["raw_symbol"]:
                instrument = instrument_registry.get_instrument(mapping.canonical_id)
                if instrument is not None and instrument.is_active:
                    canonical_id = instrument.canonical_id
            enriched_contracts.append({
                **contract,
                "canonical_instrument_id": canonical_id,
            })

        snapshot["contracts"] = enriched_contracts
        snapshot["contract_count"] = len(enriched_contracts)
        return snapshot

    @application.websocket("/ws/market-data")
    async def market_data_socket(websocket: WebSocket) -> None:
        origin = websocket.headers.get("origin")
        if origin and origin not in config.cors_allowed_origins:
            await websocket.close(code=4403, reason="Origin not allowed")
            return

        connection_id = uuid4().hex
        if shared_guard is not None:
            try:
                reserved = await shared_guard.acquire_websocket(connection_id)
            except Exception:
                await websocket.close(code=1013, reason="Shared connection protection unavailable")
                return
            if not reserved:
                await websocket.close(code=1013, reason="WebSocket capacity reached")
                return

        try:
            await websocket.accept()

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

            if not isinstance(supplied_token, str) or not supplied_token:
                await websocket.close(code=4401, reason="Authentication failed")
                return

            try:
                principal = await asyncio.to_thread(
                    application.state.identity_verifier.verify,
                    supplied_token,
                )
            except IdentityProviderUnavailable:
                await websocket.close(code=1013, reason="Identity verification unavailable")
                return
            except IdentityVerificationError:
                await websocket.close(code=4401, reason="Authentication failed")
                return
            except Exception:
                # An unexpected verifier failure must never leave the socket
                # authenticated or expose provider/internal exception details.
                await websocket.close(code=1013, reason="Identity verification unavailable")
                return

            if shared_guard is not None:
                try:
                    account_reserved = await shared_guard.acquire_websocket(
                        connection_id, principal.subject
                    )
                except Exception:
                    await websocket.close(code=1013, reason="Shared connection protection unavailable")
                    return
                if not account_reserved:
                    await websocket.close(code=1013, reason="Account WebSocket capacity reached")
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
                request_cursor = request.get("cursor")
                if "cursor" in request and (
                    not isinstance(request_cursor, int)
                    or isinstance(request_cursor, bool)
                    or request_cursor < 0
                    or request_cursor > MAX_SQLITE_CURSOR
                ):
                    await websocket.close(code=4400, reason="Invalid durable replay cursor")
                    return
                identity = request.get("series")
                if not isinstance(identity, dict):
                    await websocket.close(code=4400, reason="Exact OHLCV series identity is required")
                    return
                dataset = identity.get("dataset")
                raw_symbol = identity.get("rawSymbol")
                timeframe = identity.get("timeframe")
                bucket_policy = identity.get("bucketPolicy")
                calendar_id = identity.get("calendarId", "")
                calendar_version = identity.get("calendarVersion", "")
                publisher_id = identity.get("publisherId")
                instrument_id = identity.get("instrumentId")
                canonical_id = request.get("canonicalInstrumentId")
                if (
                    dataset != config.databento_dataset
                    or not isinstance(raw_symbol, str) or not raw_symbol.strip()
                    or len(raw_symbol) > MAX_WEBSOCKET_RAW_SYMBOL_LENGTH
                    or not isinstance(timeframe, str)
                    or not timeframe or len(timeframe) > MAX_WEBSOCKET_TIMEFRAME_LENGTH
                    or (bucket_policy is not None and (
                        not isinstance(bucket_policy, str)
                        or bucket_policy not in SUPPORTED_BUCKET_POLICIES
                    ))
                    or calendar_id != "" or calendar_version != ""
                    or not isinstance(publisher_id, int) or isinstance(publisher_id, bool) or publisher_id <= 0
                    or not isinstance(instrument_id, int) or isinstance(instrument_id, bool) or instrument_id <= 0
                    or not isinstance(canonical_id, str)
                    or len(canonical_id) != MAX_WEBSOCKET_CANONICAL_ID_LENGTH
                    or not canonical_id.strip()
                ):
                    await websocket.close(code=4400, reason="Invalid or unsupported OHLCV series identity")
                    return
                # Use the canonical resolver spelling for both the snapshot
                # query and the live fan-out identity. Authorization already
                # compares normalized symbols; leaving the request spelling here
                # would otherwise authorize lowercase/whitespace variants but
                # silently subscribe them to a different stream key.
                raw_symbol = raw_symbol.strip().upper()
                canonical_id = canonical_id.strip()

                try:
                    bucket_start_ns(0, timeframe)
                except InvalidOhlcvBar:
                    await websocket.close(code=4400, reason="Unsupported OHLCV timeframe")
                    return
                if bucket_policy is None:
                    bucket_policy = bucket_policy_for_timeframe(timeframe)

                def has_series_access() -> bool:
                    mapping = application.state.instrument_registry.resolve_provider_mapping(
                        provider="databento",
                        dataset=dataset,
                        publisher_id=publisher_id,
                        instrument_id=instrument_id,
                        timestamp_ns=time.time_ns(),
                    )
                    if (
                        mapping is None
                        or mapping.raw_symbol != raw_symbol.strip().upper()
                        or mapping.canonical_id != canonical_id.strip()
                    ):
                        return False
                    instrument = application.state.instrument_registry.get_instrument(canonical_id)
                    if instrument is None or not instrument.is_active:
                        return False
                    return application.state.instrument_entitlements.has_access(
                        subject=principal.subject,
                        canonical_instrument_id=canonical_id,
                    )

                try:
                    authorized = await asyncio.to_thread(has_series_access)
                except Exception:
                    authorized = False
                if not authorized:
                    await websocket.close(code=4403, reason="Instrument access denied")
                    return

                # No await occurs between durable high-water capture, snapshot
                # query, and stream registration. Ingestion and fan-out share this
                # event loop, so later accepted revisions enter the queue with a
                # strictly newer durable outbox cursor.
                snapshot_cursor = ohlcv_store.outbox_high_water()
                subscription, snapshot_bars, total = stream_hub.subscribe_snapshot(
                    ohlcv_pipeline,
                    dataset=dataset,
                    publisher_id=publisher_id,
                    instrument_id=instrument_id,
                    raw_symbol=raw_symbol,
                    timeframe=timeframe,
                    bucket_policy=bucket_policy,
                    calendar_id=calendar_id,
                    calendar_version=calendar_version,
                    limit=max_ohlcv_response_bars,
                    durable_cursor=snapshot_cursor,
                )
                replay_events: list[dict[str, object]] = []
                replay_fallback_reason: str | None = None
                replay_end_cursor = snapshot_cursor
                if request_cursor is not None:
                    replay_after = request_cursor
                    while True:
                        replay_page = ohlcv_store.replay_outbox(
                            after_cursor=replay_after,
                            provider="databento",
                            dataset=dataset,
                            publisher_id=publisher_id,
                            instrument_id=instrument_id,
                            series_type="contract",
                            raw_symbol=raw_symbol,
                            timeframe=timeframe,
                            bucket_policy=bucket_policy,
                            calendar_id=calendar_id,
                            calendar_version=calendar_version,
                            limit=min(500, MAX_WEBSOCKET_REPLAY_EVENTS + 1 - len(replay_events)),
                        )
                        if replay_page.get("status") != "ok":
                            replay_fallback_reason = str(replay_page.get("reason", "replay_unavailable"))
                            break
                        page_events = replay_page.get("events", [])
                        if not isinstance(page_events, list):
                            replay_fallback_reason = "invalid_replay_page"
                            break
                        if len(replay_events) + len(page_events) > MAX_WEBSOCKET_REPLAY_EVENTS:
                            replay_fallback_reason = "replay_backlog_exceeds_limit"
                            break
                        replay_events.extend(page_events)
                        next_cursor = replay_page.get("next_cursor")
                        if not isinstance(next_cursor, int) or isinstance(next_cursor, bool):
                            replay_fallback_reason = "invalid_replay_cursor"
                            break
                        replay_end_cursor = next_cursor
                        if not replay_page.get("has_more"):
                            break
                        if next_cursor <= replay_after:
                            replay_fallback_reason = "replay_cursor_did_not_advance"
                            break
                        replay_after = next_cursor

                feed_state = provider.state
                snapshot_state = (
                    "unavailable" if not snapshot_bars
                    else "degraded" if feed_state in ("degraded", "recovering")
                    else "ready"
                )
                if request_cursor is not None and replay_fallback_reason is None:
                    await websocket.send_json({
                        "type": "market_data.ohlcv.replay_started",
                        "version": 1,
                        "fromCursor": request_cursor,
                        "throughCursor": replay_end_cursor,
                        "count": len(replay_events),
                        "cursorScope": "global-outbox-filtered-by-exact-series",
                    })
                    for event in replay_events:
                        event["replayed"] = True
                        await websocket.send_json(event)
                    await websocket.send_json({
                        "type": "market_data.ohlcv.replay_complete",
                        "version": 1,
                        "cursor": replay_end_cursor,
                        "count": len(replay_events),
                    })
                    # Any notification at or below the replay boundary is
                    # already represented by replay. Keep only newer live events.
                    pending_live: list[dict[str, object]] = []
                    while not subscription.queue.empty():
                        queued = subscription.queue.get_nowait()
                        queued_cursor = queued.get("cursor")
                        if not isinstance(queued_cursor, int) or queued_cursor > replay_end_cursor:
                            pending_live.append(queued)
                    for queued in pending_live:
                        subscription.queue.put_nowait(queued)
                    subscription.durable_cursor = max(subscription.durable_cursor, replay_end_cursor)
                else:
                    if request_cursor is not None:
                        await websocket.send_json({
                            "type": "market_data.ohlcv.resnapshot_required",
                            "version": 1,
                            "reason": replay_fallback_reason or "replay_unavailable",
                            "requestedCursor": request_cursor,
                            "snapshotCursor": snapshot_cursor,
                        })
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
                        "cursor": subscription.durable_cursor,
                        "cursorScope": "global-outbox-filtered-by-exact-series",
                        "bars": [
                            {
                                "dataset": bar.dataset,
                                "provider": bar.provider,
                                "publisherId": bar.publisher_id,
                                "instrumentId": bar.instrument_id,
                                "rawSymbol": bar.raw_symbol,
                                "seriesType": bar.series_type,
                                "timeframe": bar.timeframe,
                                "bucketPolicy": bar.bucket_policy,
                                "calendarId": bar.calendar_id,
                                "calendarVersion": bar.calendar_version,
                                "tsStartNs": str(bar.ts_start_ns),
                                "open": decimal_to_string(bar.open),
                                "high": decimal_to_string(bar.high),
                                "low": decimal_to_string(bar.low),
                                "close": decimal_to_string(bar.close),
                                "volume": decimal_to_string(bar.volume),
                                "tsEventNs": str(bar.ts_event_ns),
                                "tsReceivedNs": str(bar.ts_received_ns),
                                "tsProviderOutNs": None if bar.ts_provider_out_ns is None else str(bar.ts_provider_out_ns),
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
                ping_timestamps: deque[float] = deque()
                loop = asyncio.get_running_loop()
                next_entitlement_check = loop.time() + WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS
                next_lease_refresh = loop.time() + max(1.0, config.websocket_lease_seconds / 3)
                try:
                    while True:
                        if subscription.overflowed:
                            await websocket.close(code=1013, reason="OHLCV client queue overflow; reconnect and resnapshot")
                            return
                        queue_task = asyncio.create_task(subscription.queue.get())
                        done, _ = await asyncio.wait(
                            {receive_task, queue_task},
                            timeout=max(0.0, min(next_entitlement_check, next_lease_refresh) - loop.time()),
                            return_when=asyncio.FIRST_COMPLETED,
                        )
                        # Revalidate on a monotonic deadline independent of market
                        # update frequency. A busy stream must not postpone access
                        # revocation checks indefinitely.
                        if shared_guard is not None and loop.time() >= next_lease_refresh:
                            try:
                                lease_valid = await shared_guard.renew_websocket(connection_id, principal.subject)
                            except Exception:
                                await websocket.close(code=1013, reason="Shared connection protection unavailable")
                                return
                            if not lease_valid:
                                await websocket.close(code=1013, reason="WebSocket capacity lease expired")
                                return
                            next_lease_refresh = loop.time() + max(1.0, config.websocket_lease_seconds / 3)
                        if loop.time() >= next_entitlement_check:
                            # A WebSocket can outlive the Firebase ID token used at
                            # handshake. Reverify the same token (including revocation)
                            # on the authorization deadline; fail closed on expiry,
                            # revocation, identity drift, or verifier outage.
                            try:
                                refreshed_principal = await asyncio.to_thread(
                                    application.state.identity_verifier.verify,
                                    supplied_token,
                                )
                            except IdentityProviderUnavailable:
                                await websocket.close(code=1013, reason="Identity verification unavailable")
                                return
                            except IdentityVerificationError:
                                await websocket.close(code=4401, reason="Authentication expired or revoked")
                                return
                            except Exception:
                                # Keep long-lived subscriptions fail-closed even
                                # if a verifier adapter raises outside its contract.
                                await websocket.close(code=1013, reason="Identity verification unavailable")
                                return
                            if refreshed_principal != principal:
                                await websocket.close(code=4401, reason="Authenticated identity changed")
                                return
                            try:
                                still_authorized = await asyncio.to_thread(has_series_access)
                            except Exception:
                                still_authorized = False
                            if not still_authorized:
                                await websocket.close(code=4403, reason="Instrument access revoked")
                                return
                            next_entitlement_check = loop.time() + WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS
                        if not done:
                            if queue_task is not None and not queue_task.done():
                                queue_task.cancel()
                                try:
                                    await queue_task
                                except asyncio.CancelledError:
                                    pass
                                queue_task = None
                            continue
                        if receive_task in done:
                            try:
                                client_message = receive_task.result()
                            except WebSocketDisconnect:
                                return
                            if client_message != "ping":
                                await websocket.close(code=1008, reason="Unsupported client message")
                                return
                            if not _allow_websocket_ping(ping_timestamps, loop.time()):
                                await websocket.close(code=1008, reason="WebSocket ping rate limit exceeded")
                                return
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

        finally:
            if shared_guard is not None:
                try:
                    await shared_guard.release_websocket(
                        connection_id,
                        principal.subject if "principal" in locals() else None,
                    )
                except Exception:
                    pass

    return application


app = create_app()
