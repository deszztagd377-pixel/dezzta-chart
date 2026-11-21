"""HTTP and WebSocket entry point for DEZZTA CHART.

Provider OHLCV ingestion is optional and disabled unless explicitly configured
(DATABENTO_API_KEY plus feature flags). Without them the backend starts
normally and reports the provider as disconnected. Authenticated WebSocket
clients can subscribe to the in-memory OHLCV pipeline when validated bars exist.
"""

import asyncio
import hmac
import inspect
import json
import logging
import time
from uuid import uuid4
from collections import deque
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Path as ApiPath, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field, StrictStr
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.observability import RequestMetrics
from app.coverage_store import SQLiteCoverageTracker
from app.databento_sources import DatabentoHistoricalSource, DatabentoLiveSource
from app.ingest import OhlcvIngestionService
from app.instruments import InstrumentCatalog
from app.instrument_registry import SQLiteInstrumentRegistry
from app.alert_store import SQLitePriceAlertStore
from app.alert_delivery import run_alert_delivery_batch
from app.alert_operations import LocalAlertReporter
from app.incident_store import SQLiteIncidentStore
from app.alert_device_store import AlertDeviceQuotaExceeded, SQLiteAlertDeviceStore
from app.alert_fcm_process import build_isolated_alert_event_sender
from app.entitlements import SQLiteInstrumentEntitlementStore
from app.identity import (
    FirebaseIdentityVerifier,
    IdentityProviderUnavailable,
    IdentityVerificationError,
    VerifiedPrincipal,
)
from app.ohlcv import (
    BUCKET_POLICY_CME_SESSION_V1,
    SUPPORTED_BUCKET_POLICIES,
    InvalidOhlcvBar,
    OhlcvPipeline,
    bucket_policy_for_timeframe,
    bucket_start_ns,
    decimal_to_string,
)
from app.provider import ProviderManager
from app.databento_definition_sync import DatabentoDefinitionSynchronizer
from app.ohlcv_stream import OhlcvStreamHub, OhlcvStreamResnapshotRequired
from app.ohlcv_store import SQLiteOhlcvReplicaStore, SQLiteOhlcvStore
from app.ohlcv_event_loop import EventLoopCallbackDispatcher
from app.ohlcv_redis_worker import RedisOhlcvGatewayWorker
from app.ohlcv_redis_publisher import PublisherResnapshotRequired
from app.ohlcv_redis_replay import replay_replica_history
from app.ohlcv_replica_bridge import (
    forward_replica_event,
    hydrate_replica_pipeline,
    subscribe_replica_snapshot,
)
from app.symbology import InstrumentResolver
from app.shared_guard import RedisSharedGuard
from app.websocket_tickets import InMemoryWebSocketTicketStore, WEBSOCKET_TICKET_PURPOSE, WEBSOCKET_TICKET_TTL_SECONDS
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
MAX_WEBSOCKET_PROVIDER_LENGTH = 32
MAX_WEBSOCKET_DATASET_LENGTH = 64
MAX_OHLCV_RESPONSE_BARS = 5_000
MAX_WEBSOCKET_REPLAY_EVENTS = 10_000
MAX_SQLITE_CURSOR = (1 << 63) - 1
MAX_NANOSECOND_TIMESTAMP = (1 << 63) - 1


class AlertDeviceRegistrationRequest(BaseModel):
    """Strict client payload; account ownership is never client-selectable."""

    model_config = ConfigDict(extra="forbid")

    installation_id: StrictStr = Field(min_length=1, max_length=128)
    fcm_token: StrictStr = Field(min_length=1, max_length=4096)


def _is_after_replay_boundary(cursor: object, boundary: int) -> bool:
    """Keep only live notifications newer than a completed durable replay.

    Queue cursors are decimal strings on the wire. Accept integers too for
    focused tests; preserve unknown shapes conservatively.
    """
    if isinstance(cursor, int) and not isinstance(cursor, bool):
        return cursor > boundary
    if isinstance(cursor, str) and cursor.isascii() and cursor.isdigit():
        return int(cursor) > boundary
    return True

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


def _calendar_identity_matches(
    instrument,
    *,
    timeframe: str,
    bucket_policy: str,
    calendar_id: str,
    calendar_version: str,
    calendar_registry,
) -> bool:
    """Require an exact loaded calendar release for CME series identity."""
    if bucket_policy != BUCKET_POLICY_CME_SESSION_V1:
        return not calendar_id and not calendar_version
    if (
        timeframe not in {"1d", "1w", "1M", "3M"}
        or instrument.asset_class != "future"
        or instrument.instrument_type != "future"
        or not instrument.session_calendar_id
        or calendar_id != instrument.session_calendar_id
        or not calendar_version
    ):
        return False
    return calendar_registry.get(calendar_id, calendar_version) is not None


def create_app(
    settings: Settings | None = None,
    *,
    live_source_factory=None,
    historical_source_factory=None,
    shared_guard=None,
    replica_runtime_factory=None,
    publisher_runtime_factory=None,
) -> FastAPI:
    if replica_runtime_factory is not None and not callable(replica_runtime_factory):
        raise TypeError("replica_runtime_factory must be callable when provided.")
    if publisher_runtime_factory is not None and not callable(publisher_runtime_factory):
        raise TypeError("publisher_runtime_factory must be callable when provided.")
    if replica_runtime_factory is not None and publisher_runtime_factory is not None:
        raise ValueError("Source publisher and gateway replica runtimes must use separate app roles.")
    config = settings or Settings.from_environment()
    request_metrics = RequestMetrics()
    if shared_guard is None and config.redis_url:
        shared_guard = RedisSharedGuard(
            config.redis_url,
            http_per_client_per_minute=config.http_rate_limit_per_client,
            http_global_per_minute=config.http_rate_limit_global,
            websocket_global_limit=config.websocket_connection_limit_global,
            websocket_per_account_limit=config.websocket_connection_limit_per_account,
            websocket_lease_seconds=config.websocket_lease_seconds,
        )
    websocket_ticket_store = shared_guard if shared_guard is not None else InMemoryWebSocketTicketStore()
    max_ohlcv_response_bars = min(
        max(1, config.ohlcv_max_response_bars),
        MAX_OHLCV_RESPONSE_BARS,
    )
    catalog = InstrumentCatalog(config.allowed_roots)
    instrument_registry = SQLiteInstrumentRegistry(config.instrument_registry_db_path)
    # Durable alert storage is initialized, but no public alert routes are
    # enabled until Firebase identity and instrument entitlements are verified.
    price_alert_store = SQLitePriceAlertStore(config.instrument_registry_db_path)
    incident_store = SQLiteIncidentStore(config.instrument_registry_db_path)
    # Device-token persistence is opt-in and requires an owner-injected key.
    # Delivery worker is separately opt-in and is started only in lifespan.
    alert_device_store = (
        SQLiteAlertDeviceStore(
            config.instrument_registry_db_path,
            encryption_key=config.alert_device_encryption_key,
        )
        if config.alert_device_store_enabled
        else None
    )
    instrument_entitlements = SQLiteInstrumentEntitlementStore(config.instrument_registry_db_path)
    identity_verifier = FirebaseIdentityVerifier(config.firebase_project_id)
    ohlcv_pipeline = OhlcvPipeline()
    resolver = InstrumentResolver()
    stream_hub = OhlcvStreamHub()
    ohlcv_store = SQLiteOhlcvStore(config.instrument_registry_db_path)
    publisher_wakeup = asyncio.Event()
    publisher_event_loop = None
    publisher_status = {
        "enabled": publisher_runtime_factory is not None,
        "state": "disabled" if publisher_runtime_factory is None else "not_started",
        "last_batch": None,
        "last_error_code": None,
    }

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
        # Provider callbacks may originate outside the ASGI event-loop thread.
        if publisher_event_loop is not None:
            publisher_event_loop.call_soon_threadsafe(publisher_wakeup.set)

    coverage_tracker = SQLiteCoverageTracker(config.instrument_registry_db_path)
    session_calendar_registry, session_calendar_status = load_session_calendar_runtime(
        artifact_path=config.session_calendar_artifact_path,
        expected_sha256=config.session_calendar_sha256,
        expected_version=config.session_calendar_version,
        releases=config.session_calendar_releases,
    )
    session_bar_validator = build_provider_session_bar_validator(
        instrument_registry,
        session_calendar_registry,
        calendar_version=config.session_calendar_version,
        calendar_versions={
            item["calendar_id"]: item["version"]
            for item in session_calendar_status.get("releases", ())
        },
    )
    ingestion = OhlcvIngestionService(
        pipeline=ohlcv_pipeline, resolver=resolver, coverage=coverage_tracker,
        dataset=config.databento_dataset, queue_max=config.ohlcv_queue_max,
        on_bar_applied=publish_persisted_bar,
        persistence=ohlcv_store,
        bar_validator=session_bar_validator,
        session_calendars=session_calendar_registry,
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

    # Replica mode is strictly opt-in through an owner-injected runtime factory.
    # Without it, the existing source-SQLite/provider mode remains unchanged.
    replica_worker = None

    def current_websocket_feed_state() -> str:
        if replica_worker is None:
            return provider.state
        worker_state = replica_worker.state.get("state")
        if worker_state in {"starting", "running"}:
            return "connected"
        if worker_state in {"degraded", "resnapshot_required", "stopping"}:
            return "degraded"
        return "disconnected"

    alert_delivery_status = {
        "enabled": config.alert_delivery_worker_enabled,
        "state": "disabled" if not config.alert_delivery_worker_enabled else "not_started",
        "last_batch": None,
        "last_error_code": None,
    }

    # Local operator alerts are emitted to the application logger only. No
    # external notification provider is required for this operational signal.
    alert_reporter = LocalAlertReporter(
        logging.getLogger("dezzta.alert_operations"), incident_store=incident_store
    )
    incident_logger = logging.getLogger("dezzta.incidents")

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        nonlocal replica_worker, publisher_event_loop
        worker_stop = asyncio.Event()
        worker_task = None
        incident_task = None
        publisher_task = None
        publisher_instance = None
        publisher_redis_client = None
        provider_started = False
        replica_redis_client = None
        ownership_lease = None
        try:
            if shared_guard is not None:
                await shared_guard.start()
            if publisher_runtime_factory is not None:
                runtime = publisher_runtime_factory(ohlcv_store)
                if inspect.isawaitable(runtime):
                    runtime = await runtime
                if not isinstance(runtime, dict):
                    raise RuntimeError("Publisher runtime factory must return a mapping.")
                publisher_instance = runtime.get("publisher")
                publisher_redis_client = runtime.get("redis_client")
                publisher_stream_key = runtime.get("stream_key")
                appender = getattr(publisher_instance, "appender", None)
                if (
                    not callable(getattr(publisher_instance, "publish_available", None))
                    or publisher_redis_client is None
                    or not isinstance(publisher_stream_key, str)
                    or not publisher_stream_key.strip()
                    or getattr(appender, "redis", None) is not publisher_redis_client
                    or getattr(appender, "stream_key", None) != publisher_stream_key
                ):
                    raise RuntimeError("Publisher runtime does not match its dedicated Redis client and stream.")
                await asyncio.to_thread(publisher_redis_client.ping)
                publisher_event_loop = asyncio.get_running_loop()
                publisher_status.update({
                    "enabled": True,
                    "state": "starting",
                    "last_error_code": None,
                })
                application.state.ohlcv_publisher = publisher_instance
                application.state.ohlcv_publisher_redis_client = publisher_redis_client
                application.state.ohlcv_publisher_stream_key = publisher_stream_key

                async def source_publisher_loop() -> None:
                    retry_seconds = 1.0
                    while not worker_stop.is_set():
                        publisher_wakeup.clear()
                        try:
                            batch = await asyncio.to_thread(
                                publisher_instance.publish_available
                            )
                            publisher_status["state"] = "running"
                            publisher_status["last_error_code"] = None
                            publisher_status["last_batch"] = {
                                key: batch[key]
                                for key in (
                                    "status", "published", "verified_existing",
                                    "published_cursor", "high_water", "has_more",
                                )
                                if key in batch
                            }
                            retry_seconds = 1.0
                            if batch.get("has_more"):
                                continue
                        except PublisherResnapshotRequired as exc:
                            publisher_status["state"] = "resnapshot_required"
                            publisher_status["last_error_code"] = type(exc).__name__
                            logging.getLogger("dezzta.websocket_publisher").error(
                                "OHLCV publisher requires a fresh globally installed snapshot."
                            )
                            return
                        except Exception as exc:
                            publisher_status["state"] = "degraded"
                            publisher_status["last_error_code"] = type(exc).__name__[:64]
                            logging.getLogger("dezzta.websocket_publisher").warning(
                                "OHLCV publisher batch failed; durable outbox remains authoritative."
                            )
                            try:
                                await asyncio.wait_for(
                                    worker_stop.wait(), timeout=retry_seconds
                                )
                            except asyncio.TimeoutError:
                                pass
                            retry_seconds = min(retry_seconds * 2.0, 30.0)
                            continue
                        try:
                            await asyncio.wait_for(
                                publisher_wakeup.wait(), timeout=1.0
                            )
                        except asyncio.TimeoutError:
                            pass
                    if publisher_status["state"] != "resnapshot_required":
                        publisher_status["state"] = "stopped"

                publisher_task = asyncio.create_task(
                    source_publisher_loop(), name="dezzta-ohlcv-source-publisher"
                )
            if replica_runtime_factory is None:
                await provider.start()
                provider_started = True
            else:
                runtime = replica_runtime_factory()
                if inspect.isawaitable(runtime):
                    runtime = await runtime
                if not isinstance(runtime, dict):
                    raise RuntimeError("Replica runtime factory must return a mapping.")
                replica_store = runtime.get("replica_store")
                consumer = runtime.get("consumer")
                replica_redis_client = runtime.get("redis_client")
                stream_key = runtime.get("stream_key")
                if not isinstance(replica_store, SQLiteOhlcvReplicaStore):
                    raise RuntimeError("Replica runtime requires a SQLiteOhlcvReplicaStore.")
                if replica_redis_client is None:
                    raise RuntimeError("Replica runtime requires its dedicated Redis client.")
                if not isinstance(stream_key, str) or not stream_key.strip():
                    raise RuntimeError("Replica runtime requires a non-empty stream key.")
                if (
                    not callable(getattr(consumer, "consume_once", None))
                    or not callable(getattr(consumer, "ensure_group", None))
                    or not hasattr(consumer, "on_event_applied")
                    or getattr(consumer, "replica_store", replica_store) is not replica_store
                    or getattr(consumer, "redis", replica_redis_client) is not replica_redis_client
                    or getattr(consumer, "stream_key", stream_key) != stream_key
                ):
                    raise RuntimeError("Replica consumer does not match its runtime store/client/stream.")
                hydration = hydrate_replica_pipeline(replica_store, ohlcv_pipeline)
                # One generation-scoped owner per local replica identity. The
                # Redis lease is acquired before group access or consumption.
                from app.ohlcv_redis_lease import RedisOhlcvConsumerLease
                group_name = getattr(consumer, "group_name", None)
                if not isinstance(group_name, str) or not group_name:
                    raise RuntimeError("Replica consumer requires a generation-scoped group name.")
                ownership_lease = RedisOhlcvConsumerLease(
                    replica_redis_client, group_name=group_name,
                )
                await asyncio.to_thread(ownership_lease.acquire)
                consumer.ownership_guard = ownership_lease
                # Prove Redis connectivity and group readiness before the app
                # accepts traffic; the worker must not hide a failed bootstrap.
                await asyncio.to_thread(consumer.ensure_group)
                dispatcher = EventLoopCallbackDispatcher(
                    asyncio.get_running_loop(),
                    lambda event: forward_replica_event(event, ohlcv_pipeline, stream_hub),
                )
                replica_worker = RedisOhlcvGatewayWorker(
                    consumer, dispatcher, ownership_lease=ownership_lease,
                )
                replica_worker.start()
                application.state.ohlcv_replica_store = replica_store
                application.state.ohlcv_replica_redis_client = replica_redis_client
                application.state.ohlcv_replica_stream_key = stream_key
                application.state.ohlcv_replica_worker = replica_worker
                application.state.ohlcv_replica_hydration = hydration

            async def incident_escalation_loop() -> None:
                while not worker_stop.is_set():
                    try:
                        due = await asyncio.to_thread(incident_store.escalate_due)
                        for item in due:
                            incident_logger.error(json.dumps({
                                "event": "operator_incident_escalated", **item,
                            }, separators=(",", ":"), sort_keys=True))
                    except Exception as exc:
                        incident_logger.error(json.dumps({
                            "event": "operator_incident_escalation_failed",
                            "error_code": type(exc).__name__[:64],
                        }, separators=(",", ":"), sort_keys=True))
                    try:
                        await asyncio.wait_for(worker_stop.wait(), timeout=15.0)
                    except asyncio.TimeoutError:
                        pass

            incident_task = asyncio.create_task(
                incident_escalation_loop(), name="dezzta-incident-escalation"
            )

            if config.alert_delivery_worker_enabled:
                if alert_device_store is None:
                    raise RuntimeError("Alert delivery worker requires the encrypted device store.")
                event_sender = build_isolated_alert_event_sender(
                    database_path=alert_device_store.database_path,
                    encryption_key=config.alert_device_encryption_key,
                    project_id=config.firebase_project_id,
                )

                async def alert_delivery_loop() -> None:
                    alert_delivery_status["state"] = "running"
                    while not worker_stop.is_set():
                        try:
                            batch = await asyncio.to_thread(
                                run_alert_delivery_batch,
                                price_alert_store,
                                event_sender,
                                clock_ns=time.time_ns,
                                lease_duration_ns=(
                                    config.alert_delivery_lease_seconds * 1_000_000_000
                                ),
                                batch_size=config.alert_delivery_batch_size,
                                max_attempts=config.alert_delivery_max_attempts,
                            )
                            alert_delivery_status["last_batch"] = {
                                "claimed": batch.claimed,
                                "delivered": batch.delivered,
                                "retry_scheduled": batch.retry_scheduled,
                                "terminal_failed": batch.terminal_failed,
                                "lease_lost": batch.lease_lost,
                            }
                            alert_reporter.report_batch(
                                claimed=batch.claimed,
                                delivered=batch.delivered,
                                retry_scheduled=batch.retry_scheduled,
                                terminal_failed=batch.terminal_failed,
                                lease_lost=batch.lease_lost,
                            )
                            alert_delivery_status["last_error_code"] = None
                        except Exception as exc:
                            # Keep operational visibility without logging raw
                            # provider errors, credentials, or device tokens.
                            alert_delivery_status["last_error_code"] = (
                                exc.__class__.__name__[:64]
                            )
                            alert_reporter.report_error(exc)
                        try:
                            await asyncio.wait_for(
                                worker_stop.wait(),
                                timeout=config.alert_delivery_poll_interval_seconds,
                            )
                        except asyncio.TimeoutError:
                            pass
                    alert_delivery_status["state"] = "stopped"

                worker_task = asyncio.create_task(
                    alert_delivery_loop(),
                    name="dezzta-alert-delivery",
                )
            await asyncio.sleep(0)
            yield
        finally:
            worker_stop.set()
            publisher_wakeup.set()
            if incident_task is not None:
                await incident_task
            if worker_task is not None:
                await worker_task
            if replica_worker is not None:
                stopped = await replica_worker.stop_async(timeout_seconds=3.0)
                if stopped:
                    if ownership_lease is not None:
                        await asyncio.to_thread(ownership_lease.release)
                    close_client = getattr(replica_redis_client, "close", None)
                    if callable(close_client):
                        try:
                            if inspect.iscoroutinefunction(close_client):
                                await close_client()
                            else:
                                await asyncio.to_thread(close_client)
                        except Exception:
                            logging.getLogger("dezzta.websocket_replica").exception(
                                "Replica Redis client close failed."
                            )
                else:
                    logging.getLogger("dezzta.websocket_replica").error(
                        "Replica worker did not stop within the shutdown deadline; Redis client left open."
                    )
                replica_worker = None
                application.state.ohlcv_replica_worker = None
            elif replica_redis_client is not None:
                if ownership_lease is not None:
                    await asyncio.to_thread(ownership_lease.release)
                close_client = getattr(replica_redis_client, "close", None)
                if callable(close_client):
                    if inspect.iscoroutinefunction(close_client):
                        await close_client()
                    else:
                        await asyncio.to_thread(close_client)
            if publisher_task is not None:
                done, _ = await asyncio.wait({publisher_task}, timeout=15.0)
                if publisher_task in done:
                    publisher_event_loop = None
                    if publisher_redis_client is not None:
                        close_client = getattr(publisher_redis_client, "close", None)
                        if callable(close_client):
                            try:
                                if inspect.iscoroutinefunction(close_client):
                                    await close_client()
                                else:
                                    await asyncio.to_thread(close_client)
                            except Exception:
                                logging.getLogger("dezzta.websocket_publisher").exception(
                                    "Publisher Redis client close failed."
                                )
                else:
                    logging.getLogger("dezzta.websocket_publisher").error(
                        "Publisher did not stop within the shutdown deadline; Redis client left open."
                    )
                application.state.ohlcv_publisher = None
                application.state.ohlcv_publisher_redis_client = None
            elif publisher_redis_client is not None:
                publisher_event_loop = None
                close_client = getattr(publisher_redis_client, "close", None)
                if callable(close_client):
                    if inspect.iscoroutinefunction(close_client):
                        await close_client()
                    else:
                        await asyncio.to_thread(close_client)
            if provider_started:
                await provider.stop()
            if shared_guard is not None:
                await shared_guard.close()

    application = FastAPI(
        title="DEZZTA CHART Backend",
        version="0.3.0",
        description="Secure backend foundation for DEZZTA CHART market data.",
        lifespan=lifespan,
    )

    @application.exception_handler(Exception)
    async def sanitized_internal_error(request, exc):
        """Return a non-sensitive 500 body with the middleware correlation ID."""
        request_id = getattr(request.state, "request_id", None) or uuid4().hex
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
            headers={
                "X-Request-ID": request_id,
                "Cache-Control": "private, no-store, max-age=0",
                "Pragma": "no-cache",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
            },
        )
    application.state.ohlcv_pipeline = ohlcv_pipeline
    application.state.ohlcv_stream_hub = stream_hub
    application.state.ohlcv_store = ohlcv_store
    application.state.ohlcv_replica_store = None
    application.state.ohlcv_replica_redis_client = None
    application.state.ohlcv_replica_stream_key = None
    application.state.ohlcv_replica_worker = None
    application.state.ohlcv_replica_hydration = None
    application.state.ohlcv_publisher = None
    application.state.ohlcv_publisher_redis_client = None
    application.state.ohlcv_publisher_stream_key = None
    application.state.ohlcv_publisher_status = publisher_status
    application.state.ohlcv_publisher_wakeup = publisher_wakeup
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
    application.state.alert_device_store = alert_device_store
    application.state.alert_delivery_status = alert_delivery_status
    application.state.incident_store = incident_store
    application.state.instrument_entitlements = instrument_entitlements
    application.state.identity_verifier = identity_verifier
    application.state.shared_guard = shared_guard
    application.state.websocket_ticket_store = websocket_ticket_store
    application.state.shared_guard_enabled = shared_guard is not None
    application.state.request_metrics = request_metrics

    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.cors_allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"] if alert_device_store is not None else ["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

    http_logger = logging.getLogger("dezzta.http")

    def observe_http_request(request, status_code: int, started_ns: int, route_override: str | None = None) -> str:
        duration_ms = max(0.0, (time.monotonic_ns() - started_ns) / 1_000_000)
        matched_route = request.scope.get("route")
        route = route_override or getattr(matched_route, "path", "unmatched")
        request_id = uuid4().hex
        if request.url.path not in {"/internal/metrics", "/internal/alert-delivery"} and not request.url.path.startswith("/internal/incidents"):
            request_metrics.record(request.method, route, status_code, duration_ms)
            # Deliberately omit raw URL, query, path parameters, headers and client address.
            http_logger.info(json.dumps({
                "event": "http_request", "request_id": request_id,
                "method": request.method, "route": route,
                "status_class": f"{status_code // 100}xx",
                "duration_ms": round(duration_ms, 3),
            }, separators=(",", ":"), sort_keys=True))
        return request_id

    @application.middleware("http")
    async def api_security_headers(request, call_next):
        started_ns = time.monotonic_ns()
        if shared_guard is not None and request.url.path.startswith("/v1/"):
            client_identity = request.client.host if request.client is not None else "unknown"
            try:
                allowed, retry_after = await shared_guard.allow_http(client_identity or "unknown")
            except Exception:
                response = JSONResponse(status_code=503, content={"detail": "Shared request protection is temporarily unavailable."}, headers={
                    "Retry-After": "5", "Cache-Control": "private, no-store, max-age=0",
                    "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
                    "Referrer-Policy": "no-referrer",
                    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
                    "Pragma": "no-cache", "Expires": "0",
                })
                response.headers["X-Request-ID"] = observe_http_request(request, 503, started_ns, "security_guard")
                return response
            if not allowed:
                response = JSONResponse(status_code=429, content={"detail": "Request rate limit exceeded."}, headers={
                    "Retry-After": str(retry_after), "Cache-Control": "private, no-store, max-age=0",
                    "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
                    "Referrer-Policy": "no-referrer",
                    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
                    "Pragma": "no-cache", "Expires": "0",
                })
                response.headers["X-Request-ID"] = observe_http_request(request, 429, started_ns, "security_guard")
                return response
        try:
            response = await call_next(request)
        except Exception:
            # Preserve the same request correlation ID in the sanitized 500 response.
            request.state.request_id = observe_http_request(request, 500, started_ns)
            raise
        response.headers["X-Request-ID"] = observe_http_request(request, response.status_code, started_ns)
        if request.url.path == "/health" or request.url.path.startswith("/v1/"):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
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

    @application.post("/v1/auth/websocket-ticket", tags=["authentication"])
    async def issue_websocket_ticket(
        principal: VerifiedPrincipal = Depends(require_verified_principal),
    ) -> dict[str, object]:
        issuer = getattr(application.state.websocket_ticket_store, "issue_websocket_ticket", None)
        if not callable(issuer):
            raise HTTPException(status_code=503, detail="WebSocket ticket protection is temporarily unavailable.")
        try:
            ticket = await issuer(principal.subject)
        except Exception as exc:
            raise HTTPException(status_code=503, detail="WebSocket ticket protection is temporarily unavailable.") from exc
        return {"ticket": ticket, "expiresIn": WEBSOCKET_TICKET_TTL_SECONDS, "purpose": WEBSOCKET_TICKET_PURPOSE}

    if alert_device_store is not None:
        @application.post(
            "/v1/alerts/devices",
            status_code=201,
            tags=["alerts"],
        )
        async def register_alert_device(
            payload: AlertDeviceRegistrationRequest,
            principal: VerifiedPrincipal = Depends(require_verified_principal),
        ) -> dict[str, object]:
            """Register or rotate a device token for the verified account only."""
            try:
                stored = alert_device_store.register(
                    owner_id=principal.subject,
                    installation_id=payload.installation_id,
                    fcm_token=payload.fcm_token,
                )
            except AlertDeviceQuotaExceeded as exc:
                raise HTTPException(
                    status_code=409,
                    detail="The account has reached its active alert-device limit.",
                ) from exc
            except ValueError as exc:
                raise HTTPException(
                    status_code=422,
                    detail="Alert-device registration details are invalid.",
                ) from exc
            return {
                "registered": True,
                "installation_id": stored.installation_id,
                "created_at_utc": stored.created_at_utc,
                "updated_at_utc": stored.updated_at_utc,
            }

        @application.delete(
            "/v1/alerts/devices/{installation_id}",
            tags=["alerts"],
        )
        async def revoke_alert_device(
            installation_id: str = ApiPath(min_length=1, max_length=128),
            principal: VerifiedPrincipal = Depends(require_verified_principal),
        ) -> dict[str, object]:
            """Revoke only a device belonging to the verified account."""
            try:
                revoked = alert_device_store.revoke(
                    owner_id=principal.subject,
                    installation_id=installation_id,
                )
            except ValueError as exc:
                raise HTTPException(
                    status_code=422,
                    detail="Alert-device identifier is invalid.",
                ) from exc
            return {"installation_id": installation_id, "revoked": revoked}

    @application.get("/health", tags=["operations"])
    async def health() -> dict[str, str]:
        """Liveness endpoint; deliberately reveals no secrets or feed state."""
        return {"status": "ok", "service": "dezzta-chart-backend"}

    if config.observability_metrics_token:
        @application.get("/internal/metrics", tags=["operations"], include_in_schema=False)
        async def internal_metrics(
            authorization: str | None = Header(default=None),
        ) -> JSONResponse:
            """Expose bounded process-local metrics only to an injected operator token."""
            expected = f"Bearer {config.observability_metrics_token}"
            if not isinstance(authorization, str) or not hmac.compare_digest(authorization, expected):
                raise HTTPException(status_code=401, detail="Metrics authentication is required.",
                                    headers={"WWW-Authenticate": "Bearer"})
            return JSONResponse(content=request_metrics.snapshot(), headers={
                "Cache-Control": "private, no-store, max-age=0",
                "Pragma": "no-cache", "X-Content-Type-Options": "nosniff",
            })

        @application.get(
            "/internal/alert-delivery",
            tags=["operations"],
            include_in_schema=False,
        )
        async def internal_alert_delivery_status(
            authorization: str | None = Header(default=None),
        ) -> JSONResponse:
            """Expose sanitized process-local alert-worker status to the operator."""
            expected = f"Bearer {config.observability_metrics_token}"
            if not isinstance(authorization, str) or not hmac.compare_digest(authorization, expected):
                raise HTTPException(
                    status_code=401,
                    detail="Metrics authentication is required.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return JSONResponse(
                content={
                    "schema_version": 1,
                    "scope": "process_local_since_start",
                    **dict(alert_delivery_status),
                },
                headers={
                    "Cache-Control": "private, no-store, max-age=0",
                    "Pragma": "no-cache",
                    "X-Content-Type-Options": "nosniff",
                },
            )

    if config.operator_incident_token:
        def require_operator_incident_token(authorization: str | None) -> None:
            expected = f"Bearer {config.operator_incident_token}"
            if not isinstance(authorization, str) or not hmac.compare_digest(authorization, expected):
                raise HTTPException(status_code=401, detail="Operator incident authentication is required.",
                                    headers={"WWW-Authenticate": "Bearer"})

        @application.get("/internal/incidents", tags=["operations"], include_in_schema=False)
        async def list_operator_incidents(
            limit: int = Query(default=50, ge=1, le=100),
            authorization: str | None = Header(default=None),
        ) -> JSONResponse:
            require_operator_incident_token(authorization)
            incidents = await asyncio.to_thread(incident_store.list_incidents, limit=limit)
            return JSONResponse(content={"schema_version": 1, "scope": "persistent_local_sqlite",
                                         "incidents": incidents},
                                headers={"Cache-Control": "private, no-store, max-age=0",
                                         "Pragma": "no-cache", "X-Content-Type-Options": "nosniff"})

        @application.post("/internal/incidents/{incident_id}/acknowledge", tags=["operations"], include_in_schema=False)
        async def acknowledge_operator_incident(
            incident_id: str = ApiPath(min_length=36, max_length=36),
            authorization: str | None = Header(default=None),
        ) -> JSONResponse:
            require_operator_incident_token(authorization)
            incident = await asyncio.to_thread(incident_store.acknowledge, incident_id)
            if incident is None:
                raise HTTPException(status_code=404, detail="Incident not found.")
            return JSONResponse(content=incident, headers={"Cache-Control": "private, no-store, max-age=0",
                                 "Pragma": "no-cache", "X-Content-Type-Options": "nosniff"})

        @application.post("/internal/incidents/{incident_id}/resolve", tags=["operations"], include_in_schema=False)
        async def resolve_operator_incident(
            incident_id: str = ApiPath(min_length=36, max_length=36),
            authorization: str | None = Header(default=None),
        ) -> JSONResponse:
            require_operator_incident_token(authorization)
            incident = await asyncio.to_thread(incident_store.resolve, incident_id)
            if incident is None:
                raise HTTPException(status_code=404, detail="Incident not found.")
            return JSONResponse(content=incident, headers={"Cache-Control": "private, no-store, max-age=0",
                                 "Pragma": "no-cache", "X-Content-Type-Options": "nosniff"})

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
        try:
            bucket_start_ns(0, timeframe)
        except InvalidOhlcvBar as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        effective_bucket_policy = (
            bucket_policy if bucket_policy is not None else bucket_policy_for_timeframe(timeframe)
        )

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
            if effective_bucket_policy in SUPPORTED_BUCKET_POLICIES and not _calendar_identity_matches(
                instrument,
                timeframe=timeframe,
                bucket_policy=effective_bucket_policy,
                calendar_id=calendar_id,
                calendar_version=calendar_version,
                calendar_registry=application.state.session_calendar_registry,
            ):
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

        if effective_bucket_policy not in SUPPORTED_BUCKET_POLICIES:
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

        principal = None
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

            supplied_token = None
            ticket_auth = False
            if not isinstance(auth_message, dict) or auth_message.get("type") != "auth":
                await websocket.close(code=4401, reason="Authentication failed")
                return
            supplied_ticket = auth_message.get("ticket")
            if isinstance(supplied_ticket, str) and supplied_ticket:
                try:
                    subject = await application.state.websocket_ticket_store.consume_websocket_ticket(supplied_ticket, purpose=WEBSOCKET_TICKET_PURPOSE)
                except Exception:
                    await websocket.close(code=1013, reason="WebSocket ticket protection unavailable")
                    return
                if not isinstance(subject, str) or not subject:
                    await websocket.close(code=4401, reason="Authentication ticket is invalid or expired")
                    return
                principal = VerifiedPrincipal(subject=subject, issuer="", audience="", auth_time=0)
                ticket_auth = True
            else:
                supplied_token = auth_message.get("token")
                if config.app_env.strip().lower() == "production" or not isinstance(supplied_token, str) or not supplied_token:
                    await websocket.close(code=4401, reason="Authentication ticket is required")
                    return
                try:
                    principal = await asyncio.to_thread(application.state.identity_verifier.verify, supplied_token)
                except IdentityProviderUnavailable:
                    await websocket.close(code=1013, reason="Identity verification unavailable")
                    return
                except IdentityVerificationError:
                    await websocket.close(code=4401, reason="Authentication failed")
                    return
                except Exception:
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
                        "state": current_websocket_feed_state(),
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
                cursor_value = request.get("cursor")
                request_cursor: int | None = None
                if "cursor" in request:
                    if (
                        not isinstance(cursor_value, str)
                        or not cursor_value.isascii()
                        or not cursor_value.isdigit()
                        or len(cursor_value) > 19
                    ):
                        await websocket.close(code=4400, reason="Invalid durable replay cursor")
                        return
                    request_cursor = int(cursor_value)
                    if request_cursor > MAX_SQLITE_CURSOR:
                        await websocket.close(code=4400, reason="Invalid durable replay cursor")
                        return
                identity = request.get("series")
                if not isinstance(identity, dict):
                    await websocket.close(code=4400, reason="Exact OHLCV series identity is required")
                    return
                provider_id = identity.get("provider", "databento")
                dataset = identity.get("dataset")
                raw_symbol = identity.get("rawSymbol")
                series_type = identity.get("seriesType", "contract")
                timeframe = identity.get("timeframe")
                bucket_policy = identity.get("bucketPolicy")
                calendar_id = identity.get("calendarId", "")
                calendar_version = identity.get("calendarVersion", "")
                publisher_id = identity.get("publisherId")
                instrument_id = identity.get("instrumentId")
                canonical_id = request.get("canonicalInstrumentId")
                if (
                    not isinstance(provider_id, str)
                    or not provider_id.strip()
                    or len(provider_id) > MAX_WEBSOCKET_PROVIDER_LENGTH
                    or not provider_id.isascii()
                    or not all(char.isalnum() or char in "._-" for char in provider_id)
                    or provider_id != provider_id.lower()
                    or not isinstance(dataset, str)
                    or not dataset.strip()
                    or len(dataset) > MAX_WEBSOCKET_DATASET_LENGTH
                    or not dataset.isascii()
                    or not all(char.isalnum() or char in "._-" for char in dataset)
                    or not isinstance(series_type, str)
                    or series_type != "contract"
                    or not isinstance(raw_symbol, str) or not raw_symbol.strip()
                    or len(raw_symbol) > MAX_WEBSOCKET_RAW_SYMBOL_LENGTH
                    or not isinstance(timeframe, str)
                    or not timeframe or len(timeframe) > MAX_WEBSOCKET_TIMEFRAME_LENGTH
                    or (bucket_policy is not None and (
                        not isinstance(bucket_policy, str)
                        or bucket_policy not in SUPPORTED_BUCKET_POLICIES
                    ))
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
                provider_id = provider_id.strip()
                dataset = dataset.strip().upper()
                series_type = series_type.strip().lower()
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
                        provider=provider_id,
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
                    if bucket_policy in SUPPORTED_BUCKET_POLICIES and not _calendar_identity_matches(
                        instrument,
                        timeframe=timeframe,
                        bucket_policy=bucket_policy,
                        calendar_id=calendar_id,
                        calendar_version=calendar_version,
                        calendar_registry=application.state.session_calendar_registry,
                    ):
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
                replica_store = application.state.ohlcv_replica_store
                replica_redis_client = application.state.ohlcv_replica_redis_client
                if replica_store is not None:
                    (
                        subscription, snapshot_bars, total, replica_snapshot_meta,
                    ) = subscribe_replica_snapshot(
                        replica_store,
                        stream_hub,
                        dataset=dataset,
                        publisher_id=publisher_id,
                        instrument_id=instrument_id,
                        raw_symbol=raw_symbol,
                        timeframe=timeframe,
                        limit=max_ohlcv_response_bars,
                        bucket_policy=bucket_policy,
                        calendar_id=calendar_id,
                        calendar_version=calendar_version,
                        provider=provider_id,
                        series_type=series_type,
                    )
                    snapshot_cursor = replica_snapshot_meta["cursor"]
                else:
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
                        provider=provider_id,
                        series_type=series_type,
                    )
                replay_events: list[dict[str, object]] = []
                replay_fallback_reason: str | None = None
                replay_end_cursor = snapshot_cursor
                if request_cursor is not None:
                    if replica_store is not None:
                        try:
                            replica_checkpoint = await asyncio.to_thread(replica_store.checkpoint)
                            if replica_checkpoint is None:
                                replay_fallback_reason = "replica_checkpoint_unavailable"
                            else:
                                replay_result = await asyncio.to_thread(
                                    replay_replica_history,
                                    replica_redis_client,
                                    stream_key=application.state.ohlcv_replica_stream_key,
                                    checkpoint=replica_checkpoint,
                                    after_cursor=request_cursor,
                                    series_identity={
                                        "provider": provider_id,
                                        "dataset": dataset,
                                        "publisherId": publisher_id,
                                        "instrumentId": instrument_id,
                                        "seriesType": series_type,
                                        "rawSymbol": raw_symbol,
                                        "timeframe": timeframe,
                                        "bucketPolicy": bucket_policy,
                                        "calendarId": calendar_id,
                                        "calendarVersion": calendar_version,
                                    },
                                )
                                if replay_result.get("status") != "ok":
                                    replay_fallback_reason = str(
                                        replay_result.get("reason", "replica_replay_unavailable")
                                    )
                                else:
                                    replay_events = replay_result.get("events", [])
                                    replay_end_cursor = replay_result.get("next_cursor", snapshot_cursor)
                                    if not isinstance(replay_events, list) or type(replay_end_cursor) is not int:
                                        replay_events = []
                                        replay_fallback_reason = "invalid_replica_replay_result"
                        except Exception:
                            replay_fallback_reason = "replica_replay_storage_unavailable"
                    else:
                        replay_after = request_cursor
                        while True:
                            try:
                                replay_page = await asyncio.to_thread(
                                    ohlcv_store.replay_outbox,
                                    after_cursor=replay_after,
                                    provider=provider_id,
                                    dataset=dataset,
                                    publisher_id=publisher_id,
                                    instrument_id=instrument_id,
                                    series_type=series_type,
                                    raw_symbol=raw_symbol,
                                    timeframe=timeframe,
                                    bucket_policy=bucket_policy,
                                    calendar_id=calendar_id,
                                    calendar_version=calendar_version,
                                    limit=min(500, MAX_WEBSOCKET_REPLAY_EVENTS + 1 - len(replay_events)),
                                )
                            except Exception:
                                replay_fallback_reason = "replay_storage_unavailable"
                                break
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

                feed_state = current_websocket_feed_state() if provider_id == "databento" else "disconnected"
                snapshot_state = (
                    "unavailable" if not snapshot_bars
                    else "degraded" if feed_state in ("degraded", "recovering")
                    else "ready"
                )
                if request_cursor is not None and replay_fallback_reason is None:
                    # Reserve the replay sequence range before yielding to the
                    # socket so concurrently queued live events start after it.
                    subscription.watermark = len(replay_events)
                    await websocket.send_json({
                        "type": "market_data.ohlcv.replay_started",
                        "version": 1,
                        "fromCursor": str(request_cursor),
                        "throughCursor": str(replay_end_cursor),
                        "streamId": subscription.stream_id,
                        "count": len(replay_events),
                        "cursorScope": "global-outbox-filtered-by-exact-series",
                    })
                    for replay_sequence, event in enumerate(replay_events, start=1):
                        replay_bar = event.get("bar", {})
                        replay_payload = dict(event)
                        replay_payload["streamId"] = subscription.stream_id
                        replay_payload["sequence"] = replay_sequence
                        replay_payload["emittedAtNs"] = str(time.time_ns())
                        replay_payload["isFinal"] = isinstance(replay_bar, dict) and replay_bar.get("completeness") == "complete"
                        replay_payload["cursor"] = str(event["cursor"])
                        replay_payload["replayed"] = True
                        await websocket.send_json(replay_payload)
                    try:
                        stream_hub.merge_replay_boundary(
                            subscription, replay_events, replay_end_cursor,
                        )
                    except (OhlcvStreamResnapshotRequired, ValueError):
                        await websocket.send_json({
                            "type": "market_data.ohlcv.resnapshot_required",
                            "version": 1,
                            "reason": "live_queue_handoff_failed",
                            "requestedCursor": str(request_cursor),
                            "snapshotCursor": str(snapshot_cursor),
                        })
                        await websocket.close(code=1013, reason="Resnapshot required")
                        return
                    await websocket.send_json({
                        "type": "market_data.ohlcv.replay_complete",
                        "version": 1,
                        "cursor": str(replay_end_cursor),
                        "count": len(replay_events),
                    })
                else:
                    if request_cursor is not None:
                        await websocket.send_json({
                            "type": "market_data.ohlcv.resnapshot_required",
                            "version": 1,
                            "reason": replay_fallback_reason or "replay_unavailable",
                            "requestedCursor": str(request_cursor),
                            "snapshotCursor": str(snapshot_cursor),
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
                        "cursor": str(subscription.durable_cursor),
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
                            if ticket_auth:
                                await websocket.close(code=1013, reason="WebSocket authentication renewal timed out")
                                return
                            try:
                                refreshed_principal = await asyncio.to_thread(application.state.identity_verifier.verify, supplied_token)
                            except IdentityProviderUnavailable:
                                await websocket.close(code=1013, reason="Identity verification unavailable")
                                return
                            except IdentityVerificationError:
                                await websocket.close(code=4401, reason="Authentication expired or revoked")
                                return
                            except Exception:
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
                            if client_message == "ping":
                                if not _allow_websocket_ping(ping_timestamps, loop.time()):
                                    await websocket.close(code=1008, reason="WebSocket ping rate limit exceeded")
                                    return
                                await websocket.send_json({"type": "market_data.pong", "version": 1})
                            else:
                                try:
                                    control = json.loads(client_message)
                                except (TypeError, ValueError):
                                    control = None
                                if not ticket_auth or not isinstance(control, dict) or control.get("type") != "auth.renew" or not isinstance(control.get("ticket"), str):
                                    await websocket.close(code=1008, reason="Unsupported client message")
                                    return
                                try:
                                    renewed_subject = await application.state.websocket_ticket_store.consume_websocket_ticket(control["ticket"], purpose=WEBSOCKET_TICKET_PURPOSE)
                                except Exception:
                                    await websocket.close(code=1013, reason="WebSocket ticket protection unavailable")
                                    return
                                if renewed_subject != principal.subject:
                                    await websocket.close(code=4401, reason="Authentication renewal rejected")
                                    return
                                try:
                                    still_authorized = await asyncio.to_thread(has_series_access)
                                except Exception:
                                    still_authorized = False
                                if not still_authorized:
                                    await websocket.close(code=4403, reason="Instrument access revoked")
                                    return
                                next_entitlement_check = loop.time() + WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS
                                await websocket.send_json({"type": "market_data.auth.renewed", "version": 1})
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
                        principal.subject if principal is not None else None,
                    )
                except Exception:
                    pass

    return application


app = create_app()
