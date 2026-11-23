from collections import deque

import asyncio
import ipaddress
import json
import socket
import ssl
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
import uvicorn
import websockets
import httpx

import hashlib
from decimal import Decimal
import pytest
import tempfile
from pathlib import Path
from uuid import uuid4
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from dataclasses import replace

from app.config import Settings
import app.main as main_module
from app.alert_device_store import SQLiteAlertDeviceStore
from app.main import (
    _allow_websocket_ping,
    _is_after_replay_boundary,
    create_app,
)
from app.identity import IdentityProviderUnavailable, IdentityVerificationError, VerifiedPrincipal
from app.ohlcv import OhlcvBar
from app.ohlcv_store import SQLiteOhlcvReplicaStore, SQLiteOhlcvStore
from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import ProviderInstrumentMapping


def _test_database_path() -> str:
    return str(Path(tempfile.gettempdir()) / f"dezzta-chart-test-{uuid4().hex}.sqlite3")


def _test_calendar_configuration() -> dict[str, str]:
    """Use a pinned, explicitly test-only schedule; never a production CME release."""
    artifact = Path(__file__).parent / "fixtures" / "cme_session_calendar_test_only.json"
    raw = artifact.read_bytes()
    return {
        "session_calendar_artifact_path": str(artifact),
        "session_calendar_sha256": hashlib.sha256(raw).hexdigest(),
        "session_calendar_version": "test-only-2024.01",
    }


def make_settings(token: str = "test-secret", **overrides) -> Settings:
    values = {
        "app_env": "test",
        "market_data_ws_token": token,
        "cors_allowed_origins": ("http://localhost:5173",),
        "instrument_registry_db_path": _test_database_path(),
        **_test_calendar_configuration(),
    }
    values.update(overrides)
    return Settings(**values)


def test_websocket_ping_rate_limit_allows_twenty_messages_in_window() -> None:
    timestamps: deque[float] = deque()
    assert all(_allow_websocket_ping(timestamps, 1.0) for _ in range(20))
    assert not _allow_websocket_ping(timestamps, 1.0)


def test_websocket_ping_rate_limit_expires_messages_at_window_boundary() -> None:
    timestamps: deque[float] = deque()
    assert all(_allow_websocket_ping(timestamps, 1.0) for _ in range(20))
    assert _allow_websocket_ping(timestamps, 11.0)
    assert len(timestamps) == 1


@pytest.mark.parametrize(
    ("cursor", "boundary", "expected"),
    [
        (41, 42, False),
        (42, 42, False),
        (43, 42, True),
        ("41", 42, False),
        ("42", 42, False),
        ("43", 42, True),
        ("invalid", 42, True),
        (None, 42, True),
        (True, 42, True),
    ],
)
def test_replay_handoff_compares_string_and_integer_live_cursors_safely(
    cursor, boundary: int, expected: bool,
) -> None:
    assert _is_after_replay_boundary(cursor, boundary) is expected

def test_application_durable_adapters_share_configured_database_path(tmp_path) -> None:
    """Pin the exact shared SQLite path used by every durable app adapter."""
    database_path = tmp_path / "owner-live.sqlite3"
    settings = replace(
        make_settings(),
        instrument_registry_db_path=str(database_path),
    )

    application = create_app(settings)

    durable_adapters = (
        application.state.instrument_registry,
        application.state.price_alert_store,
        application.state.instrument_entitlements,
        application.state.coverage_tracker,
        application.state.ohlcv_store,
    )
    assert all(
        adapter.database_path == str(database_path)
        for adapter in durable_adapters
    )
    assert database_path.is_file()

class UnavailableSharedGuard:
    async def start(self):
        return None

    async def close(self):
        return None

    async def allow_http(self, client_identity):
        raise ConnectionError("redis unavailable")

    async def acquire_websocket(self, connection_id, account_subject=None):
        raise ConnectionError("redis unavailable")

    async def release_websocket(self, connection_id, account_subject=None):
        return None


def test_http_api_fails_closed_when_shared_guard_is_unavailable() -> None:
    application = create_app(
        make_settings(),
        shared_guard=UnavailableSharedGuard(),
    )

    with TestClient(application) as client:
        response = client.get("/v1/market-data/status")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Shared request protection is temporarily unavailable."
    }
    assert response.headers["retry-after"] == "5"
    assert response.headers["cache-control"] == "private, no-store, max-age=0"


def test_websocket_fails_closed_when_shared_guard_is_unavailable() -> None:
    application = create_app(
        make_settings(),
        shared_guard=UnavailableSharedGuard(),
    )

    with TestClient(application) as client:
        with pytest.raises(WebSocketDisconnect) as disconnected:
            with client.websocket_connect("/ws/market-data") as websocket:
                websocket.receive_json()

    assert disconnected.value.code == 1013


class FailingRenewalSharedGuard:
    async def start(self):
        return None

    async def close(self):
        return None

    async def allow_http(self, client_identity):
        return True, 0

    async def acquire_websocket(self, connection_id, account_subject=None):
        return True

    async def renew_websocket(self, connection_id, account_subject):
        raise ConnectionError("redis unavailable during lease renewal")

    async def release_websocket(self, connection_id, account_subject=None):
        return None


def test_websocket_closes_when_redis_fails_during_lease_renewal() -> None:
    settings = replace(make_settings(), websocket_lease_seconds=3)
    application = _app_with_bars(
        settings=settings,
        shared_guard=FailingRenewalSharedGuard(),
    )

    with TestClient(application) as client:
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            assert websocket.receive_json()["type"] == "market_data.status"
            websocket.send_json({
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                "series": {
                    "dataset": "GLBX.MDP3",
                    "publisherId": 1,
                    "instrumentId": 101,
                    "rawSymbol": "ESZ6",
                    "timeframe": "1s",
                },
            })
            assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"
            with pytest.raises(WebSocketDisconnect) as disconnected:
                websocket.receive_json()

    assert disconnected.value.code == 1013


def test_health_endpoint() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "dezzta-chart-backend",
    }
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == (
        "camera=(), microphone=(), geolocation=()"
    )
    assert response.headers["cache-control"] == "private, no-store, max-age=0"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["expires"] == "0"


def test_unauthenticated_api_errors_are_not_cacheable() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/v1/auth/session")
    assert response.status_code == 401
    assert response.headers["cache-control"] == "private, no-store, max-age=0"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_market_data_status_is_honest_about_unimplemented_feed() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/v1/market-data/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["instruments"] == ["ES", "NQ", "GC"]
    assert payload["connected"] is False
    assert payload["ingestion_implemented"] is False


def test_market_data_status_uses_configured_dataset() -> None:
    settings = replace(make_settings(), databento_dataset="GLBX.TEST")
    response = TestClient(create_app(settings)).get("/v1/market-data/status")
    assert response.status_code == 200
    assert response.json()["dataset"] == "GLBX.TEST"


def test_instrument_catalog_starts_empty_without_provider_definitions() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/v1/instruments")
    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset"] == "GLBX.MDP3"
    assert payload["state"] == "definitions_unavailable"
    assert payload["contract_count"] == 0
    assert [item["root"] for item in payload["supported_products"]] == ["ES", "NQ", "GC"]
    assert payload["contracts"] == []


def test_instrument_catalog_exposes_only_registered_canonical_identity() -> None:
    application = create_app(make_settings())
    application.state.catalog.replace_definitions([{
        "raw_symbol": "ESZ6",
        "instrument_id": 101,
        "publisher_id": 1,
        "instrument_class": "F",
        "expiration": "2026-12-18",
        "currency": "USD",
        "min_price_increment": 250_000_000,
        "ts_event": 1_790_000_000_000_000_000,
    }])
    canonical_id = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
    application.state.instrument_registry.register_instrument_with_mapping(
        CanonicalInstrument(
            canonical_id=canonical_id, asset_class="future", instrument_type="future",
            symbol="ESZ6", venue="XCME", expiration_date="2026-12-18",
            settlement_currency="USD", contract_multiplier="50", tick_size="0.25",
        ),
        ProviderInstrumentMapping(
            provider="databento", dataset="GLBX.MDP3", publisher_id=1,
            instrument_id=101, raw_symbol="ESZ6", valid_from_ns=1,
            valid_to_ns=None, canonical_id=canonical_id,
        ),
    )

    response = TestClient(application).get("/v1/instruments?root=ES")
    assert response.status_code == 200
    contract = response.json()["contracts"][0]
    assert contract["canonical_instrument_id"] == canonical_id

    # A provider definition without a durable active registry mapping must not
    # receive a fabricated identity.
    unmapped_app = create_app(make_settings())
    unmapped_app.state.catalog.replace_definitions([{
        "raw_symbol": "ESZ6",
        "instrument_id": 101,
        "publisher_id": 1,
        "instrument_class": "F",
        "expiration": "2026-12-18",
        "currency": "USD",
        "min_price_increment": 250_000_000,
        "ts_event": 1_790_000_000_000_000_000,
    }])
    unmapped = TestClient(unmapped_app).get("/v1/instruments?root=ES")
    assert unmapped.json()["contracts"][0]["canonical_instrument_id"] is None


def test_instrument_catalog_can_be_filtered_by_supported_root() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/v1/instruments?root=es")
    assert response.status_code == 200
    payload = response.json()
    assert payload["requested_root"] == "ES"
    assert payload["supported_products"] == [
        {"root": "ES", "product_name": "E-mini S&P 500 Futures"}
    ]


def test_instrument_catalog_rejects_unknown_root() -> None:
    client = TestClient(create_app(make_settings()))
    assert client.get("/v1/instruments?root=MES").status_code == 404


def _install_test_identity(application, *, valid_token="valid-firebase-token", subject="firebase-user-123"):
    class FakeVerifier:
        def verify(self, token):
            if token != valid_token:
                raise IdentityVerificationError("invalid token")
            return VerifiedPrincipal(
                subject=subject,
                issuer="https://securetoken.google.com/test-project",
                audience="test-project",
                auth_time=1_798_000_000,
            )
    application.state.identity_verifier = FakeVerifier()


def _seed_stream_entitlement(application, *, grant=True):
    canonical_id = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
    instrument = CanonicalInstrument(
        canonical_id=canonical_id, asset_class="future", instrument_type="future",
        symbol="ESZ6", venue="XCME", expiration_date="2026-12-18",
        settlement_currency="USD", contract_multiplier="50", tick_size="0.25",
        session_calendar_id="CME_EQUITY_INDEX",
    )
    mapping = ProviderInstrumentMapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
        raw_symbol="ESZ6", valid_from_ns=1, valid_to_ns=None, canonical_id=canonical_id,
    )
    application.state.instrument_registry.register_instrument_with_mapping(instrument, mapping)
    if grant:
        application.state.instrument_entitlements.grant(
            subject="firebase-user-123", canonical_instrument_id=canonical_id,
        )
    return canonical_id


def test_websocket_requires_authentication() -> None:
    application = create_app(make_settings())
    _install_test_identity(application)
    client = TestClient(application)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "wrong-token"})
            websocket.receive_json()


def test_websocket_sends_status_after_authentication() -> None:
    application = create_app(make_settings())
    _install_test_identity(application)
    client = TestClient(application)
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        message = websocket.receive_json()
    assert message["type"] == "market_data.status"
    assert message["quality"]["state"] == "disconnected"
    assert message["instruments"] == ["ES", "NQ", "GC"]


def test_ohlcv_endpoint_requires_bearer_authentication() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get(
        "/v1/ohlcv?dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6&timeframe=1s"
    )
    assert response.status_code == 401


def test_ohlcv_endpoint_rejects_unsupported_timeframe() -> None:
    client = TestClient(_app_with_bars())
    response = client.get(
        "/v1/ohlcv?dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6&timeframe=2m",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )
    assert response.status_code == 422


def test_market_data_status_reports_ohlcv_pipeline_without_claiming_live_feed() -> None:
    client = TestClient(create_app(make_settings()))
    payload = client.get("/v1/market-data/status").json()
    assert payload["ohlcv_pipeline_available"] is True
    assert payload["ohlcv_provider_connected"] is False
    assert payload["connected"] is False


# ---------------------------------------------------------------- Phase 2 ---
import time
from types import SimpleNamespace

from app.symbology import SymbolMapping

_NS = 1_000_000_000
_T0 = 1_704_067_200 * _NS


def _px(text: str) -> int:
    from decimal import Decimal
    return int(Decimal(text) * _NS)


def _record(offset: int, volume: int = 10):
    return SimpleNamespace(
        open=_px("100"), high=_px("101"), low=_px("99"), close=_px("100.5"),
        volume=volume, instrument_id=101, publisher_id=1, ts_event=_T0 + offset * _NS,
    )


def _app_with_bars(count: int = 4, *, settings=None, shared_guard=None):
    application = create_app(settings or make_settings(), shared_guard=shared_guard)
    _install_test_identity(application)
    _seed_stream_entitlement(application)
    application.state.resolver.add(SymbolMapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
        raw_symbol="ESZ6", valid_from_ns=0))
    service = application.state.provider._ingest
    for offset in range(count):
        service.ingest_batch([_record(offset)], "ohlcv-1s")
    return application


def test_status_exposes_ohlcv_block_and_never_a_credential() -> None:
    secret = "db-SECRETSECRETSECRETSECRET123456"
    settings = Settings(
        app_env="test", market_data_ws_token="t", cors_allowed_origins=(),
        databento_api_key=secret,
    )
    client = TestClient(create_app(settings))  # lifespan not entered: nothing connects
    response = client.get("/v1/market-data/status")
    payload = response.json()
    assert secret not in response.text
    assert payload["ohlcv"]["state"] == "disconnected"
    assert payload["ohlcv_provider_connected"] is False
    assert payload["connected"] is False and payload["ingestion_implemented"] is False


def test_ohlcv_endpoint_returns_ingested_bars_with_local_sequence_and_limit() -> None:
    client = TestClient(_app_with_bars())
    headers = {"Authorization": "Bearer valid-firebase-token"}
    exact = "dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6"
    snapshot_response = client.get(f"/v1/ohlcv?{exact}&timeframe=1s", headers=headers)
    assert snapshot_response.status_code == 200
    assert snapshot_response.headers["cache-control"] == "private, no-store, max-age=0"
    assert snapshot_response.headers["pragma"] == "no-cache"
    assert snapshot_response.headers["x-content-type-options"] == "nosniff"
    payload = snapshot_response.json()
    assert payload["state"] == "ready" and payload["count"] == 4 and payload["truncated"] is False
    assert payload["bars"][0]["sequenceOrigin"] == "local"
    assert payload["bars"][0]["bucketPolicy"] == "UTC_FIXED_V1"
    assert payload["bars"][0]["calendarId"] == ""
    assert payload["bars"][0]["calendarVersion"] == ""
    legacy_policy = client.get(
        f"/v1/ohlcv?{exact}&timeframe=1s&bucket_policy=UTC_LEGACY",
        headers=headers,
    ).json()
    assert legacy_policy["count"] == 0 and legacy_policy["state"] == "unavailable"
    limited = client.get(f"/v1/ohlcv?{exact}&timeframe=1s&limit=2", headers=headers).json()
    assert limited["count"] == 2 and limited["truncated"] is True
    assert limited["bars"][-1]["tsStartNs"] == str(_T0 + 3 * _NS)
    derived = client.get(f"/v1/ohlcv?{exact}&timeframe=1m", headers=headers).json()
    assert derived["bars"][0]["volume"] == "40" and derived["bars"][0]["origin"] == "derived"
    ranged = client.get(
        f"/v1/ohlcv?{exact}&timeframe=1s&start_ns={_T0 + _NS}&end_ns={_T0 + 3 * _NS}",
        headers=headers,
    ).json()
    assert ranged["count"] == 2


def test_rest_snapshot_is_scoped_to_authorized_provider_series_type() -> None:
    application = _app_with_bars()
    pipeline = application.state.ohlcv_pipeline
    existing, _ = pipeline.query(
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
        raw_symbol="ESZ6", timeframe="1s", provider="databento",
        series_type="contract", limit=1,
    )
    assert existing
    pipeline.apply(replace(existing[0], series_type="continuous", sequence=999))
    client = TestClient(application)
    headers = {"Authorization": "Bearer valid-firebase-token"}
    exact = "dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6&timeframe=1s"

    response = client.get(f"/v1/ohlcv?{exact}", headers=headers)
    assert response.status_code == 200
    assert response.json()["count"] == 4
    assert {bar["seriesType"] for bar in response.json()["bars"]} == {"contract"}
    assert {bar["provider"] for bar in response.json()["bars"]} == {"databento"}

    denied = client.get(f"/v1/ohlcv?{exact}&series_type=continuous", headers=headers)
    assert denied.status_code == 403


def test_cme_rest_snapshot_requires_exact_loaded_calendar_identity() -> None:
    application = _app_with_bars()
    client = TestClient(application)
    headers = {"Authorization": "Bearer valid-firebase-token"}
    base = (
        "/v1/ohlcv?dataset=GLBX.MDP3&publisher_id=1&instrument_id=101"
        "&raw_symbol=ESZ6&timeframe=1d&bucket_policy=CME_SESSION_V1"
    )
    valid = client.get(
        base + "&calendar_id=CME_EQUITY_INDEX&calendar_version=test-only-2024.01",
        headers=headers,
    )
    assert valid.status_code == 200
    assert valid.json()["count"] == 1
    valid_bar = valid.json()["bars"][0]
    assert valid_bar["calendarId"] == "CME_EQUITY_INDEX"
    assert valid_bar["calendarVersion"] == "test-only-2024.01"

    wrong_calendar = client.get(
        base + "&calendar_id=COMEX_GOLD&calendar_version=test-only-2024.01",
        headers=headers,
    )
    assert wrong_calendar.status_code == 403

    missing_release = client.get(
        base + "&calendar_id=CME_EQUITY_INDEX&calendar_version=unknown-release",
        headers=headers,
    )
    assert missing_release.status_code == 403


def test_cme_websocket_snapshot_requires_exact_loaded_calendar_identity() -> None:
    application = _app_with_bars()
    client = TestClient(application)
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1d",
                "bucketPolicy": "CME_SESSION_V1",
                "calendarId": "CME_EQUITY_INDEX",
                "calendarVersion": "test-only-2024.01",
            },
        })
        snapshot = websocket.receive_json()
        assert snapshot["type"] == "market_data.ohlcv.snapshot"
        assert snapshot["count"] == 1
        assert snapshot["bars"][0]["calendarId"] == "CME_EQUITY_INDEX"
        assert snapshot["bars"][0]["calendarVersion"] == "test-only-2024.01"

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1d",
                "bucketPolicy": "CME_SESSION_V1",
                "calendarId": "COMEX_GOLD",
                "calendarVersion": "test-only-2024.01",
            },
        })
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_json()

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1d",
                "bucketPolicy": "CME_SESSION_V1",
                "calendarId": "CME_EQUITY_INDEX",
                "calendarVersion": "unknown-release",
            },
        })
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_json()


def test_rest_and_websocket_snapshots_return_identical_ohlcv_bars() -> None:
    """REST and WebSocket bootstrap must serialize the same exact pipeline snapshot."""
    client = TestClient(_app_with_bars())
    headers = {"Authorization": "Bearer valid-firebase-token"}
    exact = "dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6"

    for timeframe in ("1s", "1m"):
        rest_response = client.get(
            f"/v1/ohlcv?{exact}&timeframe={timeframe}",
            headers=headers,
        )
        assert rest_response.status_code == 200
        rest_snapshot = rest_response.json()

        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            status = websocket.receive_json()
            assert status["type"] == "market_data.status"
            websocket.send_json({
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                "series": {
                    "dataset": "GLBX.MDP3",
                    "publisherId": 1,
                    "instrumentId": 101,
                    "rawSymbol": "ESZ6",
                    "timeframe": timeframe,
                },
            })
            websocket_snapshot = websocket.receive_json()

        assert websocket_snapshot["type"] == rest_snapshot["type"]
        assert websocket_snapshot["version"] == rest_snapshot["version"]
        assert websocket_snapshot["state"] == rest_snapshot["state"]
        assert websocket_snapshot["feedState"] == rest_snapshot["feedState"]
        assert websocket_snapshot["count"] == rest_snapshot["count"]
        assert websocket_snapshot["bars"] == rest_snapshot["bars"]



@pytest.mark.parametrize(
    ("connection_state", "mark_degraded"),
    [("live", True), ("recovering", False)],
)
def test_rest_and_websocket_report_degraded_feed_state_consistently(
    connection_state: str,
    mark_degraded: bool,
) -> None:
    application = _app_with_bars()
    application.state.provider._connection = connection_state
    if mark_degraded:
        application.state.provider._ingest.degraded_reasons.add("ingest_overflow")
    client = TestClient(application)
    headers = {"Authorization": "Bearer valid-firebase-token"}
    exact = "dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6&timeframe=1s"

    rest_response = client.get(f"/v1/ohlcv?{exact}", headers=headers)
    assert rest_response.status_code == 200
    rest_snapshot = rest_response.json()
    assert rest_snapshot["state"] == "degraded"

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        websocket_snapshot = websocket.receive_json()

    assert websocket_snapshot["feedState"] == rest_snapshot["feedState"]
    assert websocket_snapshot["state"] == rest_snapshot["state"] == "degraded"



def test_ohlcv_endpoint_denies_accounts_without_instrument_entitlement() -> None:
    application = _app_with_bars()
    application.state.instrument_entitlements.revoke(
        subject="firebase-user-123",
        canonical_instrument_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
    )
    client = TestClient(application)
    response = client.get(
        "/v1/ohlcv?dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6&timeframe=1s",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )
    assert response.status_code == 403


@pytest.mark.parametrize("query", ["timeframe=2m", "start_ns=abc", "start_ns=10&end_ns=5", "limit=0"])
def test_ohlcv_endpoint_rejects_invalid_query_parameters(query: str) -> None:
    client = TestClient(_app_with_bars())
    exact = "dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6&timeframe=1s"
    response = client.get(
        f"/v1/ohlcv?{exact}&{query}",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )
    assert response.status_code == 422


@pytest.mark.parametrize("field", ["start_ns", "end_ns"])
def test_ohlcv_endpoint_rejects_nanosecond_timestamp_overflow(field: str) -> None:
    client = TestClient(_app_with_bars())
    exact = "dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6&timeframe=1s"
    response = client.get(
        f"/v1/ohlcv?{exact}&{field}=9223372036854775808",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )
    assert response.status_code == 422
    assert "signed 64-bit nanosecond range" in response.json()["detail"]


def test_ohlcv_endpoint_accepts_maximum_signed_64_bit_nanosecond_timestamp() -> None:
    client = TestClient(_app_with_bars())
    headers = {"Authorization": "Bearer valid-firebase-token"}
    exact = "dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6&timeframe=1s"

    start_response = client.get(f"/v1/ohlcv?{exact}&start_ns=9223372036854775807", headers=headers)
    end_response = client.get(f"/v1/ohlcv?{exact}&end_ns=9223372036854775807", headers=headers)

    assert start_response.status_code == 200
    assert start_response.json()["count"] == 0
    assert end_response.status_code == 200
    assert end_response.json()["count"] == 4


@pytest.mark.parametrize(
    "query",
    [
        "dataset=" + ("D" * 65),
        "publisher_id=0",
        "publisher_id=2147483648",
        "instrument_id=0",
        "instrument_id=2147483648",
        "timeframe=" + ("1" * 17),
        "raw_symbol=" + ("S" * 129),
        "start_ns=" + ("1" * 20),
        "end_ns=" + ("1" * 20),
        "provider=" + ("p" * 33),
        "series_type=" + ("s" * 33),
        "limit=5001",
    ],
)
def test_ohlcv_endpoint_rejects_oversized_or_out_of_range_query_values(query: str) -> None:
    client = TestClient(_app_with_bars())
    exact = "dataset=GLBX.MDP3&publisher_id=1&instrument_id=101&raw_symbol=ESZ6&timeframe=1s"
    key = query.split("=", 1)[0]
    base = "&".join(part for part in exact.split("&") if not part.startswith(f"{key}="))
    response = client.get(
        f"/v1/ohlcv?{base}&{query}",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )
    assert response.status_code == 422


def test_lifespan_connects_a_fake_live_source_and_shuts_down_cleanly() -> None:
    class FakeLive:
        stopped = False

        def start(self, on_record, on_close):
            import threading
            threading.Thread(target=lambda: on_record(_record(0)), daemon=True).start()

        def stop(self):
            FakeLive.stopped = True

    settings = Settings(
        app_env="test", market_data_ws_token="t", cors_allowed_origins=(),
        databento_api_key="db-FAKEFAKEFAKEFAKEFAKEFAKE1234", databento_live_enabled=True,
        databento_live_symbols=("ESZ6",),
        instrument_registry_db_path=_test_database_path(),
        **_test_calendar_configuration(),
    )
    application = create_app(settings, live_source_factory=FakeLive)
    _install_test_identity(application)
    _seed_stream_entitlement(application)
    application.state.resolver.add(SymbolMapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
        raw_symbol="ESZ6", valid_from_ns=0))
    with TestClient(application) as client:
        for _ in range(200):
            if client.get("/v1/market-data/status").json()["ohlcv"]["state"] == "live":
                break
            time.sleep(0.02)
        assert client.get("/v1/market-data/status").json()["ohlcv"]["state"] == "live"
    assert FakeLive.stopped is True

def test_websocket_authenticates_then_sends_exact_ohlcv_snapshot_with_watermark() -> None:
    application = _app_with_bars()
    client = TestClient(application)
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        status = websocket.receive_json()
        assert status["type"] == "market_data.status"
        assert status["schema"] == "ohlcv"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        snapshot = websocket.receive_json()
        assert snapshot["type"] == "market_data.ohlcv.snapshot"
        assert snapshot["version"] == 1
        assert snapshot["state"] == "ready"
        assert snapshot["streamId"]
        assert snapshot["watermark"] == 0
        assert int(snapshot["cursor"]) == application.state.ohlcv_store.outbox_high_water()
        assert snapshot["cursorScope"] == "global-outbox-filtered-by-exact-series"
        assert snapshot["count"] == 4
        assert snapshot["bars"][-1]["tsStartNs"] == str(_T0 + 3 * _NS)


def test_websocket_replays_exact_series_from_durable_cursor() -> None:
    application = _app_with_bars()
    client = TestClient(application)
    expected_high_water = application.state.ohlcv_store.outbox_high_water()
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "cursor": "0",
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        started = websocket.receive_json()
        assert started["type"] == "market_data.ohlcv.replay_started"
        assert started["fromCursor"] == "0"
        assert int(started["throughCursor"]) == expected_high_water
        assert started["count"] == 4
        replayed = [websocket.receive_json() for _ in range(started["count"])]
        assert all(event["type"] == "market_data.ohlcv.update" for event in replayed)
        assert all(event["replayed"] is True for event in replayed)
        assert [int(event["cursor"]) for event in replayed] == sorted(
            int(event["cursor"]) for event in replayed
        )
        assert all(event["series"]["rawSymbol"] == "ESZ6" for event in replayed)
        complete = websocket.receive_json()
        assert complete["type"] == "market_data.ohlcv.replay_complete"
        assert int(complete["cursor"]) == expected_high_water


@pytest.mark.parametrize(
    "invalid_cursor",
    ["²", "١", "1.5", "9" * 20, "9223372036854775808"],
)
def test_websocket_rejects_malformed_or_out_of_range_replay_cursor(invalid_cursor: str) -> None:
    application = _app_with_bars()
    client = TestClient(application)
    with pytest.raises(WebSocketDisconnect) as disconnected:
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            assert websocket.receive_json()["type"] == "market_data.status"
            websocket.send_json({
                "type": "market_data.subscribe",
                "version": 1,
                "cursor": invalid_cursor,
                "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                "series": {
                    "dataset": "GLBX.MDP3",
                    "publisherId": 1,
                    "instrumentId": 101,
                    "rawSymbol": "ESZ6",
                    "timeframe": "1s",
                },
            })
            websocket.receive_json()
    assert disconnected.value.code == 4400


def test_websocket_replay_cursor_ahead_falls_back_to_fresh_snapshot() -> None:
    application = _app_with_bars()
    client = TestClient(application)
    requested_cursor = application.state.ohlcv_store.outbox_high_water() + 1
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "cursor": str(requested_cursor),
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        fallback = websocket.receive_json()
        assert fallback["type"] == "market_data.ohlcv.resnapshot_required"
        assert fallback["reason"] == "cursor_ahead"
        snapshot = websocket.receive_json()
        assert snapshot["type"] == "market_data.ohlcv.snapshot"
        assert int(snapshot["cursor"]) < requested_cursor


@pytest.mark.parametrize(
    ("field", "value", "top_level"),
    [
        ("rawSymbol", "S" * 129, False),
        ("timeframe", "1" * 17, False),
        ("canonicalInstrumentId", "x" * 37, True),
    ],
)
def test_websocket_rejects_oversized_series_identity_fields(
    field: str, value: str, top_level: bool,
) -> None:
    application = create_app(make_settings())
    _install_test_identity(application)
    _seed_stream_entitlement(application)
    client = TestClient(application)

    with pytest.raises(WebSocketDisconnect) as disconnected:
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            assert websocket.receive_json()["type"] == "market_data.status"
            request = {
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                "series": {
                    "dataset": "GLBX.MDP3",
                    "publisherId": 1,
                    "instrumentId": 101,
                    "rawSymbol": "ESZ6",
                    "timeframe": "1s",
                },
            }
            if top_level:
                request[field] = value
            else:
                request["series"][field] = value
            websocket.send_json(request)
            websocket.receive_json()

    assert disconnected.value.code == 4400


def test_websocket_denies_series_without_account_entitlement() -> None:
    application = create_app(make_settings())
    _install_test_identity(application)
    canonical_id = _seed_stream_entitlement(application, grant=False)
    client = TestClient(application)
    with pytest.raises(WebSocketDisconnect) as disconnected:
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            assert websocket.receive_json()["type"] == "market_data.status"
            websocket.send_json({
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": canonical_id,
                "series": {
                    "dataset": "GLBX.MDP3",
                    "publisherId": 1,
                    "instrumentId": 101,
                    "rawSymbol": "ESZ6",
                    "timeframe": "1s",
                },
            })
            websocket.receive_json()
    assert disconnected.value.code == 4403


def test_websocket_rejects_invalid_ohlcv_subscription() -> None:
    application = create_app(make_settings())
    _install_test_identity(application)
    client = TestClient(application)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            assert websocket.receive_json()["type"] == "market_data.status"
            websocket.send_json({
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                "series": {
                    "dataset": "GLBX.MDP3",
                    "publisherId": 1,
                    "instrumentId": 101,
                    "rawSymbol": "ESZ6",
                    "timeframe": "2m",
                },
            })
            websocket.receive_json()

def test_authenticated_websocket_receives_validated_live_ohlcv_update() -> None:
    class FakeLive:
        callback = None
        stopped = False

        def start(self, on_record, on_close):
            FakeLive.callback = on_record

        def stop(self):
            FakeLive.stopped = True

    settings = Settings(
        app_env="test",
        market_data_ws_token="test-secret",
        cors_allowed_origins=(),
        databento_api_key="db-FAKEFAKEFAKEFAKEFAKEFAKE1234",
        databento_live_enabled=True,
        databento_live_symbols=("ESZ6",),
        **_test_calendar_configuration(),
    )
    application = create_app(settings, live_source_factory=FakeLive)
    _install_test_identity(application)
    _seed_stream_entitlement(application)
    application.state.resolver.add(SymbolMapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1,
        instrument_id=101, raw_symbol="ESZ6", valid_from_ns=0,
    ))

    with TestClient(application) as client:
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            assert websocket.receive_json()["type"] == "market_data.status"
            websocket.send_json({
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                "series": {
                    "dataset": "GLBX.MDP3",
                    "publisherId": 1,
                    "instrumentId": 101,
                    "rawSymbol": "ESZ6",
                    "timeframe": "1s",
                },
            })
            snapshot = websocket.receive_json()
            assert snapshot["state"] == "unavailable"
            assert snapshot["watermark"] == 0

            for _ in range(100):
                if FakeLive.callback is not None:
                    break
                time.sleep(0.01)
            assert FakeLive.callback is not None
            FakeLive.callback(_record(0))
            update = websocket.receive_json()
            assert update["type"] == "market_data.ohlcv.update"
            assert update["sequence"] == 1
            assert update["series"]["instrumentId"] == 101
            assert update["bar"]["rawSymbol"] == "ESZ6"
            assert update["bar"]["timeframe"] == "1s"

    assert FakeLive.stopped is True

def test_auth_session_requires_bearer_token():
    client = TestClient(create_app(make_settings()))
    response = client.get("/v1/auth/session")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_auth_session_offloads_firebase_verification_from_event_loop(monkeypatch):
    import asyncio

    application = create_app(make_settings())
    calls = []
    original_to_thread = asyncio.to_thread

    class FakeVerifier:
        def verify(self, token):
            assert token == "valid-firebase-token"
            return VerifiedPrincipal(
                subject="firebase-user-123",
                issuer="https://securetoken.google.com/test-project",
                audience="test-project",
                auth_time=1_798_000_000,
            )

    async def recording_to_thread(function, *args, **kwargs):
        calls.append(function)
        return await original_to_thread(function, *args, **kwargs)

    application.state.identity_verifier = FakeVerifier()
    monkeypatch.setattr("app.main.asyncio.to_thread", recording_to_thread)
    response = TestClient(application).get(
        "/v1/auth/session",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )

    assert response.status_code == 200
    assert calls == [application.state.identity_verifier.verify]


def test_auth_session_returns_only_verified_principal():
    from app.identity import VerifiedPrincipal

    application = create_app(make_settings())

    class FakeVerifier:
        def verify(self, token):
            assert token == "valid-firebase-token"
            return VerifiedPrincipal(
                subject="firebase-user-123",
                issuer="https://securetoken.google.com/test-project",
                audience="test-project",
                auth_time=1_798_000_000,
            )

    application.state.identity_verifier = FakeVerifier()
    client = TestClient(application)
    response = client.get(
        "/v1/auth/session",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "authenticated": True,
        "subject": "firebase-user-123",
        "issuer": "https://securetoken.google.com/test-project",
        "audience": "test-project",
    }


def test_auth_session_rejects_invalid_firebase_token():
    from app.identity import IdentityVerificationError

    application = create_app(make_settings())

    class FakeVerifier:
        def verify(self, token):
            raise IdentityVerificationError("bad token")

    application.state.identity_verifier = FakeVerifier()
    client = TestClient(application)
    response = client.get(
        "/v1/auth/session",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_auth_session_fails_closed_when_firebase_is_not_configured():
    client = TestClient(create_app(make_settings()))
    response = client.get(
        "/v1/auth/session",
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 503


def test_ohlcv_snapshot_recovers_from_shared_sqlite_database_after_app_restart():
    settings = make_settings()
    first_app = create_app(settings)
    _install_test_identity(first_app)
    _seed_stream_entitlement(first_app)
    first_app.state.resolver.add(SymbolMapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1,
        instrument_id=101, raw_symbol="ESZ6", valid_from_ns=0,
    ))
    first_app.state.provider._ingest.ingest_batch(
        [_record(0), _record(1)], "ohlcv-1s"
    )
    assert first_app.state.ohlcv_store.stats()["bars"] >= 3  # base + derived

    restarted_app = create_app(settings)
    _install_test_identity(restarted_app)
    exact_series = (
        "dataset=GLBX.MDP3&publisher_id=1&instrument_id=101"
        "&raw_symbol=ESZ6&timeframe=1s"
    )
    response = TestClient(restarted_app).get(
        f"/v1/ohlcv?{exact_series}",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["state"] == "ready"
    assert payload["count"] == 2
    assert payload["bars"][0]["tsStartNs"] == str(_T0)
    assert payload["bars"][1]["tsStartNs"] == str(_T0 + _NS)
    assert restarted_app.state.ohlcv_store.stats()["bars"] == first_app.state.ohlcv_store.stats()["bars"]
    restarted_app.state.resolver.add(SymbolMapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1,
        instrument_id=101, raw_symbol="ESZ6", valid_from_ns=0,
    ))
    restarted_app.state.provider._ingest.ingest_batch(
        [_record(2)], "ohlcv-1s"
    )
    resumed = restarted_app.state.ohlcv_pipeline.list_bars(
        timeframe="1s", instrument_id=101
    )
    assert resumed[-1].sequence == 3


def test_coverage_intervals_and_gaps_restore_with_application_restart():
    settings = make_settings()
    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    first = create_app(settings)
    first.state.coverage_tracker.add_covered(scope, 0, 100)
    first.state.coverage_tracker.add_gap(scope, 30, 40)

    restarted = create_app(settings)
    assert restarted.state.coverage_tracker.intervals(scope) == [(0, 30), (40, 100)]
    assert restarted.state.coverage_tracker.gaps(scope) == [(30, 40)]


def test_websocket_normalizes_raw_symbol_for_snapshot_and_live_stream_identity() -> None:
    application = _app_with_bars()
    client = TestClient(application)
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "  esz6  ",
                "timeframe": "1s",
            },
        })
        snapshot = websocket.receive_json()
        assert snapshot["type"] == "market_data.ohlcv.snapshot"
        assert snapshot["count"] == 4
        assert snapshot["bars"][-1]["rawSymbol"] == "ESZ6"

        application.state.provider._ingest.ingest_batch([_record(4)], "ohlcv-1s")
        update = websocket.receive_json()
        assert update["type"] == "market_data.ohlcv.update"
        assert update["series"]["rawSymbol"] == "ESZ6"
        assert update["bar"]["rawSymbol"] == "ESZ6"
        assert update["sequence"] == 1
        assert int(update["cursor"]) > int(snapshot["cursor"])
        assert update["eventId"] == application.state.ohlcv_store.outbox_event_id(int(update["cursor"]))


def _open_authorized_websocket_subscription(application, client):
    websocket = client.websocket_connect("/ws/market-data")
    websocket.__enter__()
    websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
    assert websocket.receive_json()["type"] == "market_data.status"
    websocket.send_json({
        "type": "market_data.subscribe",
        "version": 1,
        "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
        "series": {
            "dataset": "GLBX.MDP3",
            "publisherId": 1,
            "instrumentId": 101,
            "rawSymbol": "ESZ6",
            "timeframe": "1s",
        },
    })
    assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"
    return websocket


def test_websocket_fails_closed_on_unexpected_initial_verifier_error() -> None:
    application = create_app(make_settings())

    class BrokenVerifier:
        def verify(self, _token):
            raise RuntimeError("private verifier details")

    application.state.identity_verifier = BrokenVerifier()
    client = TestClient(application)

    with pytest.raises(WebSocketDisconnect) as disconnected:
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            websocket.receive_json()

    assert disconnected.value.code == 1013
    assert "private verifier details" not in str(disconnected.value)


def test_websocket_fails_closed_on_unexpected_verifier_error_during_recheck(monkeypatch) -> None:
    monkeypatch.setattr("app.main.WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS", 0.02)
    application = _app_with_bars()
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"

        def fail_unexpectedly(_token):
            raise RuntimeError("private verifier details")

        application.state.identity_verifier.verify = fail_unexpectedly
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()

    assert disconnected.value.code == 1013
    assert "private verifier details" not in str(disconnected.value)


def test_websocket_revalidates_firebase_token_during_idle_subscription(monkeypatch) -> None:
    monkeypatch.setattr("app.main.WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS", 0.02)
    application = _app_with_bars()
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"

        def reject_expired_or_revoked_token(_token):
            raise IdentityVerificationError("expired or revoked")

        application.state.identity_verifier.verify = reject_expired_or_revoked_token
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()

    assert disconnected.value.code == 4401


def test_websocket_fails_closed_when_identity_provider_unavailable_on_recheck(monkeypatch) -> None:
    monkeypatch.setattr("app.main.WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS", 0.02)
    application = _app_with_bars()
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"

        def unavailable(_token):
            raise IdentityProviderUnavailable("provider unavailable")

        application.state.identity_verifier.verify = unavailable
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()

    assert disconnected.value.code == 1013


def test_websocket_rechecks_revoked_entitlement_during_idle_subscription(monkeypatch) -> None:
    monkeypatch.setattr("app.main.WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS", 0.02)
    application = _app_with_bars()
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"
        application.state.instrument_entitlements.revoke(
            subject="firebase-user-123",
            canonical_instrument_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
        )
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()

    assert disconnected.value.code == 4403


def test_websocket_rechecks_revoked_entitlement_during_continuous_updates(monkeypatch) -> None:
    monkeypatch.setattr("app.main.WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS", 0.03)
    application = _app_with_bars()
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"

        application.state.instrument_entitlements.revoke(
            subject="firebase-user-123",
            canonical_instrument_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
        )

        # Keep the stream busy: access revalidation must still run on its own
        # deadline rather than only after an idle websocket timeout.
        disconnected = None
        for offset in range(4, 20):
            application.state.provider._ingest.ingest_batch([_record(offset)], "ohlcv-1s")
            try:
                message = websocket.receive_json()
            except WebSocketDisconnect as exc:
                disconnected = exc
                break
            assert message["type"] == "market_data.ohlcv.update"
            time.sleep(0.01)

        assert disconnected is not None, "revoked subscription remained active during continuous updates"
        assert disconnected.code == 4403



def test_websocket_rejects_origin_not_in_allowlist():
    application = create_app(make_settings())
    client = TestClient(application)
    with pytest.raises(WebSocketDisconnect) as disconnected:
        with client.websocket_connect(
            "/ws/market-data",
            headers={"origin": "https://attacker.example"},
        ):
            pass
    assert disconnected.value.code == 4403


def test_websocket_rejects_browser_origin_when_allowlist_is_empty():
    settings = replace(make_settings(), cors_allowed_origins=())
    application = create_app(settings)
    client = TestClient(application)
    with pytest.raises(WebSocketDisconnect) as disconnected:
        with client.websocket_connect(
            "/ws/market-data",
            headers={"origin": "https://unexpected.example"},
        ):
            pass
    assert disconnected.value.code == 4403


def test_websocket_allows_non_browser_client_without_origin_header():
    application = create_app(make_settings())
    _install_test_identity(application)
    client = TestClient(application)
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        message = websocket.receive_json()
    assert message["type"] == "market_data.status"


def test_shared_http_guard_rejects_rate_limited_request() -> None:
    class Guard:
        async def allow_http(self, client_identity):
            assert client_identity
            return False, 13
    response=TestClient(create_app(make_settings(),shared_guard=Guard())).get("/v1/market-data/status")
    assert response.status_code==429 and response.headers["retry-after"]=="13"
    assert response.headers["x-content-type-options"]=="nosniff"
    assert response.headers["cache-control"]=="private, no-store, max-age=0"
    assert "Request rate limit" in response.json()["detail"]

def test_shared_http_guard_fails_closed_when_redis_is_unavailable() -> None:
    class Guard:
        async def allow_http(self, client_identity):
            raise ConnectionError("redis offline")
    response=TestClient(create_app(make_settings(),shared_guard=Guard())).get("/v1/market-data/status")
    assert response.status_code==503 and response.headers["retry-after"]=="5"
    assert response.headers["x-content-type-options"]=="nosniff"
    assert response.headers["cache-control"]=="private, no-store, max-age=0"
    assert "redis offline" not in response.text

def test_shared_websocket_guard_rejects_before_accept_when_global_cap_is_full() -> None:
    class Guard:
        async def acquire_websocket(self, connection_id, account_subject=None):
            assert account_subject is None
            return False
        async def release_websocket(self, connection_id, account_subject=None):
            raise AssertionError("Rejected reservation must not be released")
    client=TestClient(create_app(make_settings(),shared_guard=Guard()))
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/market-data"):
            pass

def test_shared_websocket_guard_rejects_account_cap_after_firebase_auth() -> None:
    class Guard:
        def __init__(self):
            self.subject=None
            self.released=False
        async def acquire_websocket(self, connection_id, account_subject=None):
            if account_subject is None:
                return True
            self.subject=account_subject
            return False
        async def release_websocket(self, connection_id, account_subject=None):
            self.released=True
            assert account_subject=="firebase-user-123"
    guard=Guard()
    application=create_app(make_settings(),shared_guard=guard)
    _install_test_identity(application)
    client=TestClient(application)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type":"auth","token":"valid-firebase-token"})
            websocket.receive_json()
    assert guard.subject=="firebase-user-123"
    assert guard.released is True

def test_shared_guard_startup_failure_prevents_serving() -> None:
    class Guard:
        closed=False
        async def start(self):
            raise ConnectionError("redis unavailable")
        async def close(self):
            self.closed=True
    guard=Guard()
    with pytest.raises(ConnectionError):
        with TestClient(create_app(make_settings(),shared_guard=guard)):
            pass
    assert guard.closed is True



def test_websocket_rejects_identity_drift_during_idle_subscription(monkeypatch) -> None:
    """A still-valid token must not keep a socket bound to a changed principal."""
    monkeypatch.setattr("app.main.WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS", 0.02)
    application = _app_with_bars()
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"

        def changed_identity(_token):
            return VerifiedPrincipal(
                subject="different-firebase-user",
                issuer="https://securetoken.google.com/test-project",
                audience="test-project",
                auth_time=1_798_000_000,
            )

        application.state.identity_verifier.verify = changed_identity
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()

    assert disconnected.value.code == 4401

def test_alert_device_store_is_opt_in_and_uses_shared_database(tmp_path):
    disabled_app = create_app(make_settings())
    assert disabled_app.state.alert_device_store is None

    database_path = tmp_path / "alerts.sqlite3"
    settings = replace(
        make_settings(),
        instrument_registry_db_path=str(database_path),
        alert_device_store_enabled=True,
        alert_device_encryption_key=b"0123456789abcdef0123456789abcdef",
    )
    enabled_app = create_app(settings)

    store = enabled_app.state.alert_device_store
    assert isinstance(store, SQLiteAlertDeviceStore)
    assert store.database_path == str(database_path)
    store.register(
        owner_id="verified-test-subject",
        installation_id="android-test-device",
        fcm_token="test-only-fcm-token",
    )
    assert store.token_for_delivery(
        owner_id="verified-test-subject",
        installation_id="android-test-device",
    ) == "test-only-fcm-token"
    disabled_paths = {
        getattr(route, "path", "")
        for route in disabled_app.routes
    }
    enabled_paths = {
        getattr(route, "path", "")
        for route in enabled_app.routes
    }
    assert "/v1/alerts/devices" not in disabled_paths
    assert "/v1/alerts/devices" in enabled_paths
    assert "/v1/alerts/devices/{installation_id}" in enabled_paths

def test_alert_device_routes_bind_owner_to_verified_identity_and_never_return_token(
    tmp_path,
):
    database_path = tmp_path / "alert-device-routes.sqlite3"
    settings = replace(
        make_settings(),
        instrument_registry_db_path=str(database_path),
        alert_device_store_enabled=True,
        alert_device_encryption_key=b"0123456789abcdef0123456789abcdef",
    )
    application = create_app(settings)

    def verify_for_test(token):
        subject = {
            "firebase-user-a": "account-a",
            "firebase-user-b": "account-b",
        }.get(token)
        if subject is None:
            raise IdentityVerificationError("test identity rejected")
        return VerifiedPrincipal(
            subject=subject,
            issuer="https://securetoken.google.com/test-project",
            audience="test-project",
            auth_time=1_798_000_000,
        )

    application.state.identity_verifier.verify = verify_for_test
    client = TestClient(application)

    assert client.post(
        "/v1/alerts/devices",
        json={"installation_id": "phone-a", "fcm_token": "fcm-token-v1"},
    ).status_code == 401

    spoofed_owner = client.post(
        "/v1/alerts/devices",
        headers={"Authorization": "Bearer firebase-user-a"},
        json={
            "owner_id": "account-victim",
            "installation_id": "phone-a",
            "fcm_token": "fcm-token-v1",
        },
    )
    assert spoofed_owner.status_code == 422
    assert application.state.alert_device_store.active_count(owner_id="account-victim") == 0

    registered = client.post(
        "/v1/alerts/devices",
        headers={"Authorization": "Bearer firebase-user-a"},
        json={"installation_id": "phone-a", "fcm_token": "fcm-token-v1"},
    )
    assert registered.status_code == 201
    assert registered.json()["registered"] is True
    assert "fcm_token" not in registered.json()
    assert "owner_id" not in registered.json()

    rotated = client.post(
        "/v1/alerts/devices",
        headers={"Authorization": "Bearer firebase-user-a"},
        json={"installation_id": "phone-a", "fcm_token": "fcm-token-v2"},
    )
    assert rotated.status_code == 201
    assert application.state.alert_device_store.token_for_delivery(
        owner_id="account-a", installation_id="phone-a"
    ) == "fcm-token-v2"

    cross_account_revoke = client.delete(
        "/v1/alerts/devices/phone-a",
        headers={"Authorization": "Bearer firebase-user-b"},
    )
    assert cross_account_revoke.status_code == 200
    assert cross_account_revoke.json()["revoked"] is False
    assert application.state.alert_device_store.token_for_delivery(
        owner_id="account-a", installation_id="phone-a"
    ) == "fcm-token-v2"

    revoked = client.delete(
        "/v1/alerts/devices/phone-a",
        headers={"Authorization": "Bearer firebase-user-a"},
    )
    assert revoked.status_code == 200
    assert revoked.json()["revoked"] is True
    assert application.state.alert_device_store.token_for_delivery(
        owner_id="account-a", installation_id="phone-a"
    ) is None

    invalid_token = client.post(
        "/v1/alerts/devices",
        headers={"Authorization": "Bearer firebase-user-a"},
        json={"installation_id": "phone-b", "fcm_token": "not a valid token"},
    )
    assert invalid_token.status_code == 422


def test_alert_device_routes_enable_only_required_cors_methods(tmp_path):
    disabled = create_app(make_settings())
    disabled_preflight = TestClient(disabled).options(
        "/v1/alerts/devices",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert disabled_preflight.status_code == 200
    assert "POST" in disabled_preflight.headers["access-control-allow-methods"]
    assert "DELETE" not in disabled_preflight.headers["access-control-allow-methods"]

    settings = replace(
        make_settings(),
        instrument_registry_db_path=str(tmp_path / "cors.sqlite3"),
        alert_device_store_enabled=True,
        alert_device_encryption_key=b"0123456789abcdef0123456789abcdef",
    )
    enabled = create_app(settings)
    enabled_preflight = TestClient(enabled).options(
        "/v1/alerts/devices",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert enabled_preflight.status_code == 200
    assert "POST" in enabled_preflight.headers["access-control-allow-methods"]
    assert "DELETE" in enabled_preflight.headers["access-control-allow-methods"]


def test_opt_in_alert_worker_starts_and_stops_with_application_lifespan(monkeypatch):
    from app import main as main_module

    captured = {}

    def fake_build_isolated_sender(**kwargs):
        captured.update(kwargs)
        return lambda event: None

    monkeypatch.setattr(
        main_module,
        "build_isolated_alert_event_sender",
        fake_build_isolated_sender,
    )

    settings = replace(
        make_settings(),
        firebase_project_id="test-alert-project",
        alert_device_store_enabled=True,
        alert_device_encryption_key=b"K" * 32,
        alert_delivery_worker_enabled=True,
        alert_delivery_poll_interval_seconds=1,
    )
    application = create_app(settings)

    with TestClient(application):
        for _ in range(100):
            if application.state.alert_delivery_status["state"] == "running":
                break
            time.sleep(0.01)
        assert application.state.alert_delivery_status["enabled"] is True
        assert application.state.alert_delivery_status["state"] == "running"
        assert captured["database_path"] == application.state.alert_device_store.database_path
        assert captured["encryption_key"] == b"K" * 32
        assert captured["project_id"] == "test-alert-project"

    assert application.state.alert_delivery_status["state"] == "stopped"


def test_alert_worker_remains_disabled_in_default_application_lifespan():
    application = create_app(make_settings())
    with TestClient(application):
        assert application.state.alert_delivery_status == {
            "enabled": False,
            "state": "disabled",
            "last_batch": None,
            "last_error_code": None,
        }



def test_websocket_selects_provider_specific_mapping_and_snapshot_without_cross_source_mix() -> None:
    application = _app_with_bars()
    canonical_id = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
    application.state.instrument_registry.register_instrument_with_mapping(
        application.state.instrument_registry.get_instrument(canonical_id),
        ProviderInstrumentMapping(
            provider="venue_b", dataset="VENUE.B", publisher_id=2, instrument_id=202,
            raw_symbol="ESZ6B", valid_from_ns=1, valid_to_ns=None,
            canonical_id=canonical_id,
        ),
    )
    existing, _ = application.state.ohlcv_pipeline.query(
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
        raw_symbol="ESZ6", timeframe="1s", provider="databento",
        series_type="contract", limit=1,
    )
    assert existing
    provider_b_bar = replace(
        existing[0], provider="venue_b", dataset="VENUE.B", publisher_id=2,
        instrument_id=202, raw_symbol="ESZ6B", sequence=1,
    )
    assert application.state.ohlcv_pipeline.apply(provider_b_bar) == "inserted"
    client = TestClient(application)
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe", "version": 1,
            "canonicalInstrumentId": canonical_id,
            "series": {
                "provider": "venue_b", "dataset": "VENUE.B",
                "publisherId": 2, "instrumentId": 202, "rawSymbol": "ESZ6B",
                "timeframe": "1s", "seriesType": "contract",
            },
        })
        snapshot = websocket.receive_json()
    assert snapshot["type"] == "market_data.ohlcv.snapshot"
    assert snapshot["count"] == 1
    assert snapshot["bars"][0]["provider"] == "venue_b"
    assert snapshot["bars"][0]["dataset"] == "VENUE.B"
    assert snapshot["bars"][0]["rawSymbol"] == "ESZ6B"
    assert snapshot["feedState"] == "disconnected"


def test_internal_metrics_endpoint_is_disabled_without_operator_token():
    response = TestClient(create_app(make_settings())).get("/internal/metrics")
    assert response.status_code == 404


def test_internal_alert_delivery_status_is_disabled_without_operator_token():
    response = TestClient(create_app(make_settings())).get("/internal/alert-delivery")
    assert response.status_code == 404


def test_internal_alert_delivery_status_requires_token_and_returns_sanitized_snapshot():
    token = "metrics-token-for-tests-only-32chars"
    application = create_app(replace(make_settings(), observability_metrics_token=token))
    application.state.alert_delivery_status.update({
        "enabled": True,
        "state": "running",
        "last_batch": {
            "claimed": 2,
            "delivered": 1,
            "retry_scheduled": 1,
            "terminal_failed": 0,
            "lease_lost": 0,
        },
        "last_error_code": None,
    })
    client = TestClient(application)

    denied = client.get("/internal/alert-delivery")
    assert denied.status_code == 401
    assert denied.headers["www-authenticate"] == "Bearer"

    accepted = client.get(
        "/internal/alert-delivery",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert accepted.status_code == 200
    assert accepted.headers["cache-control"] == "private, no-store, max-age=0"
    payload = accepted.json()
    assert payload == {
        "schema_version": 1,
        "scope": "process_local_since_start",
        "enabled": True,
        "state": "running",
        "last_batch": {
            "claimed": 2,
            "delivered": 1,
            "retry_scheduled": 1,
            "terminal_failed": 0,
            "lease_lost": 0,
        },
        "last_error_code": None,
    }
    assert "token" not in str(payload).lower()
    assert "metrics-token" not in str(payload)


def test_internal_metrics_endpoint_requires_token_and_returns_bounded_snapshot():
    token = "metrics-token-for-tests-only-32chars"
    application = create_app(replace(make_settings(), observability_metrics_token=token))
    client = TestClient(application)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.headers["x-request-id"]

    denied = client.get("/internal/metrics")
    assert denied.status_code == 401
    assert denied.headers["www-authenticate"] == "Bearer"

    accepted = client.get("/internal/metrics", headers={"Authorization": f"Bearer {token}"})
    assert accepted.status_code == 200
    assert accepted.headers["cache-control"] == "private, no-store, max-age=0"
    payload = accepted.json()
    assert payload["schema_version"] == 1
    assert payload["scope"] == "process_local_since_start"
    health_rows = [item for item in payload["requests"] if item["route"] == "/health" and item["method"] == "GET"]
    assert health_rows and health_rows[0]["count"] >= 1
    assert all("metrics-token" not in str(item) for item in payload.values())


def test_websocket_live_event_arriving_after_replay_read_is_delivered_after_replay(monkeypatch) -> None:
    """Force a live publish after the replay page is read but before handoff."""
    application = _app_with_bars()
    real_asyncio = main_module.asyncio

    class AsyncioProxy:
        def __getattr__(self, name):
            return getattr(real_asyncio, name)

        async def to_thread(self, function, /, *args, **kwargs):
            result = function(*args, **kwargs)
            if getattr(function, "__name__", "") == "replay_outbox":
                application.state.provider._ingest.ingest_batch(
                    [_record(4)], "ohlcv-1s"
                )
            return result

    monkeypatch.setattr(main_module, "asyncio", AsyncioProxy())
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "cursor": "0",
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })

        started = websocket.receive_json()
        assert started["type"] == "market_data.ohlcv.replay_started"
        assert started["count"] == 4
        replayed = [websocket.receive_json() for _ in range(started["count"])]
        assert all(item["replayed"] is True for item in replayed)
        assert [item["sequence"] for item in replayed] == [1, 2, 3, 4]

        complete = websocket.receive_json()
        assert complete["type"] == "market_data.ohlcv.replay_complete"
        assert complete["count"] == 4

        live = websocket.receive_json()
        assert live["type"] == "market_data.ohlcv.update"
        assert live["sequence"] == 5
        assert int(live["cursor"]) > int(complete["cursor"])
        assert live["bar"]["tsStartNs"] == str(_T0 + 4 * _NS)
        assert live.get("replayed", False) is False


def test_websocket_client_ping_receives_protocol_pong() -> None:
    """The production client heartbeat frame must round-trip through the route."""
    application = _app_with_bars()
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"

        websocket.send_text("ping")
        assert websocket.receive_json() == {
            "type": "market_data.pong",
            "version": 1,
        }


def test_websocket_rejects_non_ping_client_control_frame() -> None:
    application = _app_with_bars()
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"

        websocket.send_text("not-a-ping")
        with pytest.raises(WebSocketDisconnect) as closed:
            websocket.receive_json()
        assert closed.value.code == 1008

def test_websocket_ticket_endpoint_issues_single_use_ticket_for_verified_subject():
    application = create_app(make_settings())
    _install_test_identity(application)
    client = TestClient(application)
    response = client.post("/v1/auth/websocket-ticket", headers={"Authorization": "Bearer valid-firebase-token"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["purpose"] == "market-data" and payload["expiresIn"] == 90
    assert isinstance(payload["ticket"], str) and len(payload["ticket"]) >= 40
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "ticket": payload["ticket"]})
        assert websocket.receive_json()["type"] == "market_data.status"
    with pytest.raises(WebSocketDisconnect) as disconnected:
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "ticket": payload["ticket"]})
            websocket.receive_json()
    assert disconnected.value.code == 4401


def test_websocket_ticket_renewal_is_subject_bound_and_acknowledged():
    application = _app_with_bars()
    client = TestClient(application)
    headers = {"Authorization": "Bearer valid-firebase-token"}
    first = client.post("/v1/auth/websocket-ticket", headers=headers).json()["ticket"]
    renewal = client.post("/v1/auth/websocket-ticket", headers=headers).json()["ticket"]
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "ticket": first})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe", "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {"dataset": "GLBX.MDP3", "publisherId": 1, "instrumentId": 101, "rawSymbol": "ESZ6", "timeframe": "1s"},
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"
        websocket.send_json({"type": "auth.renew", "ticket": renewal})
        assert websocket.receive_json() == {"type": "market_data.auth.renewed", "version": 1}



def test_websocket_ticket_renewal_rejects_invalid_or_expired_ticket():
    application = _app_with_bars()
    client = TestClient(application)
    initial_ticket = client.post(
        "/v1/auth/websocket-ticket",
        headers={"Authorization": "Bearer valid-firebase-token"},
    ).json()["ticket"]

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "ticket": initial_ticket})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"
        websocket.send_json({
            "type": "auth.renew",
            "ticket": "invalid-or-expired-ticket",
        })
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()

    assert disconnected.value.code == 4401


def test_websocket_ticket_renewal_fails_closed_when_ticket_store_becomes_unavailable():
    application = _app_with_bars()
    client = TestClient(application)
    initial_ticket = client.post(
        "/v1/auth/websocket-ticket",
        headers={"Authorization": "Bearer valid-firebase-token"},
    ).json()["ticket"]
    renewal_ticket = client.post(
        "/v1/auth/websocket-ticket",
        headers={"Authorization": "Bearer valid-firebase-token"},
    ).json()["ticket"]
    delegate = application.state.websocket_ticket_store

    class SwitchableTicketStore:
        unavailable = False

        async def consume_websocket_ticket(self, ticket, *, purpose):
            if self.unavailable:
                raise ConnectionError("redis credential=must-not-leak")
            return await delegate.consume_websocket_ticket(ticket, purpose=purpose)

        async def issue_websocket_ticket(self, subject):
            return await delegate.issue_websocket_ticket(subject)

    store = SwitchableTicketStore()
    application.state.websocket_ticket_store = store

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "ticket": initial_ticket})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"
        store.unavailable = True
        websocket.send_json({"type": "auth.renew", "ticket": renewal_ticket})
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()

    assert disconnected.value.code == 1013


def test_websocket_ticket_endpoint_rejects_invalid_bearer_token():
    application = create_app(make_settings())
    _install_test_identity(application)
    response = TestClient(application).post("/v1/auth/websocket-ticket", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401

def test_websocket_ticket_endpoint_rejects_missing_bearer_identity():
    application = create_app(make_settings())
    _install_test_identity(application)

    response = TestClient(application).post("/v1/auth/websocket-ticket")

    assert response.status_code == 401
    assert response.json()["detail"] == "Bearer authentication is required."


def test_websocket_ticket_endpoint_fails_closed_when_shared_store_is_unavailable():
    application = create_app(make_settings())
    _install_test_identity(application)
    application.state.websocket_ticket_store = None

    response = TestClient(application).post(
        "/v1/auth/websocket-ticket",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "WebSocket ticket protection is temporarily unavailable."


def test_websocket_ticket_endpoint_redacts_ticket_store_failure_details():
    application = create_app(make_settings())
    _install_test_identity(application)

    class BrokenTicketStore:
        async def issue_websocket_ticket(self, account_subject):
            assert account_subject == "firebase-user-123"
            raise RuntimeError("redis password=private-secret")

    application.state.websocket_ticket_store = BrokenTicketStore()
    response = TestClient(application).post(
        "/v1/auth/websocket-ticket",
        headers={"Authorization": "Bearer valid-firebase-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "WebSocket ticket protection is temporarily unavailable."
    assert "private-secret" not in response.text
    assert "redis password" not in response.text


def test_websocket_ticket_https_post_is_allowed_by_cors_preflight():
    client = TestClient(create_app(make_settings()))
    response = client.options(
        "/v1/auth/websocket-ticket",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 200
    assert "POST" in response.headers["access-control-allow-methods"]
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

def test_websocket_releases_global_lease_when_auth_frame_times_out():
    class RecordingSharedGuard:
        def __init__(self):
            self.acquired = None
            self.released = []

        async def start(self):
            return None

        async def close(self):
            return None

        async def allow_http(self, client_identity):
            return True, 0

        async def acquire_websocket(self, connection_id, account_subject=None):
            self.acquired = (connection_id, account_subject)
            return True

        async def renew_websocket(self, connection_id, account_subject):
            return True

        async def release_websocket(self, connection_id, account_subject=None):
            self.released.append((connection_id, account_subject))

    guard = RecordingSharedGuard()
    application = create_app(make_settings(), shared_guard=guard)
    with TestClient(application) as client:
        with pytest.raises(WebSocketDisconnect) as disconnected:
            with client.websocket_connect("/ws/market-data") as websocket:
                websocket.receive_json()

    assert disconnected.value.code == 4401
    assert guard.acquired is not None
    assert guard.released == [(guard.acquired[0], None)]


def test_websocket_closes_and_requires_resnapshot_when_replay_live_handoff_fails(monkeypatch) -> None:
    from app.ohlcv_stream import OhlcvStreamHub, OhlcvStreamResnapshotRequired

    def fail_handoff(self, subscription, replay_events, replay_end_cursor):
        raise OhlcvStreamResnapshotRequired("internal detail must not be sent")

    monkeypatch.setattr(OhlcvStreamHub, "merge_replay_boundary", fail_handoff)
    application = _app_with_bars()
    client = TestClient(application)

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "cursor": "0",
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3", "publisherId": 1,
                "instrumentId": 101, "rawSymbol": "ESZ6", "timeframe": "1s",
            },
        })
        started = websocket.receive_json()
        assert started["type"] == "market_data.ohlcv.replay_started"
        for _ in range(started["count"]):
            assert websocket.receive_json()["replayed"] is True
        required = websocket.receive_json()
        assert required["type"] == "market_data.ohlcv.resnapshot_required"
        assert required["reason"] == "live_queue_handoff_failed"
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()
        assert disconnected.value.code == 1013


def test_replica_runtime_hydrates_before_worker_and_serves_replica_snapshot(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "replica-source.sqlite3"))
    bar = OhlcvBar(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=101, series_type="contract",
        timeframe="1s", ts_start_ns=1_000_000_000, raw_symbol="ESZ6",
        open=Decimal("100"), high=Decimal("101"), low=Decimal("99"),
        close=Decimal("100.5"), volume=Decimal("2"),
        ts_event_ns=1_000_000_001, ts_received_ns=1_000_000_002,
        sequence=1, sequence_origin="local", origin="provider",
        completeness="unknown", bucket_policy="UTC_FIXED_V1",
    )
    assert source.apply(bar) == "inserted"
    snapshot_path = tmp_path / "replica-snapshot.jsonl"
    source.export_global_snapshot(str(snapshot_path))
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "gateway-replica.sqlite3"))
    replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=source.source_id(),
    )

    class FakeRedis:
        closed = False
        def __init__(self):
            self.values = {}
        def set(self, key, value, nx=False, px=None):
            if nx and key in self.values:
                return False
            self.values[key] = value
            return True
        def eval(self, script, numkeys, key, token, *args):
            if self.values.get(key) != token:
                return 0
            if "PEXPIRE" in script:
                return 1
            if "DEL" in script:
                self.values.pop(key, None)
                return 1
            return 1
        def close(self):
            self.closed = True

    class IdleConsumer:
        def __init__(self, redis_client, store, stream_key):
            self.redis = redis_client
            self.replica_store = store
            self.stream_key = stream_key
            self.block_ms = None
            self.on_event_applied = None
            self.group_ready = False
            self.group_name = "test:replica:group:generation-1"
        def ensure_group(self):
            self.group_ready = True
            return True
        def consume_once(self):
            return {"status": "idle"}

    redis_client = FakeRedis()
    consumer = IdleConsumer(redis_client, replica, "test:ohlcv:stream")
    application = create_app(
        make_settings(),
        replica_runtime_factory=lambda: {
            "replica_store": replica,
            "consumer": consumer,
            "redis_client": redis_client,
            "stream_key": "test:ohlcv:stream",
        },
    )
    _install_test_identity(application)
    canonical_id = _seed_stream_entitlement(application)

    with TestClient(application) as client:
        assert application.state.ohlcv_replica_hydration["applied_cursor"] == 1
        assert application.state.provider.state == "disconnected"
        assert consumer.group_ready is True
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            status = websocket.receive_json()
            assert status["type"] == "market_data.status"
            assert status["quality"]["state"] == "connected"
            websocket.send_json({
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": canonical_id,
                "series": {
                    "dataset": "GLBX.MDP3", "publisherId": 1,
                    "instrumentId": 101, "rawSymbol": "ESZ6",
                    "timeframe": "1s",
                },
            })
            snapshot = websocket.receive_json()
            assert snapshot["type"] == "market_data.ohlcv.snapshot"
            assert snapshot["count"] == 1
            assert snapshot["cursor"] == "1"
            assert snapshot["bars"][0]["close"] == "100.5"
    assert redis_client.closed is True


def test_replica_shutdown_logs_unconfirmed_lease_release_and_closes_redis(
    tmp_path, caplog,
):
    source = SQLiteOhlcvStore(str(tmp_path / "lease-release-source.sqlite3"))
    snapshot_path = tmp_path / "lease-release-snapshot.jsonl"
    source.export_global_snapshot(str(snapshot_path))
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "lease-release-replica.sqlite3"))
    replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=source.source_id(),
    )

    class FakeRedis:
        closed = False
        def __init__(self):
            self.values = {}
        def set(self, key, value, nx=False, px=None):
            if nx and key in self.values:
                return False
            self.values[key] = value
            return True
        def eval(self, script, numkeys, key, token, *args):
            if self.values.get(key) != token:
                return 0
            if "PEXPIRE" in script:
                return 1
            if "DEL" in script:
                return 0
            return 1
        def close(self):
            self.closed = True

    class IdleConsumer:
        def __init__(self, redis_client, store):
            self.redis = redis_client
            self.replica_store = store
            self.stream_key = "test:ohlcv:stream"
            self.block_ms = None
            self.on_event_applied = None
            self.group_name = "test:replica:lease-release:generation-1"
        def ensure_group(self):
            return True
        def consume_once(self):
            return {"status": "idle"}

    redis_client = FakeRedis()
    consumer = IdleConsumer(redis_client, replica)
    application = create_app(
        make_settings(),
        replica_runtime_factory=lambda: {
            "replica_store": replica,
            "consumer": consumer,
            "redis_client": redis_client,
            "stream_key": "test:ohlcv:stream",
        },
    )

    with caplog.at_level("WARNING", logger="dezzta.websocket_replica"):
        with TestClient(application):
            assert application.state.ohlcv_replica_worker is not None

    assert redis_client.closed is True
    assert any(
        "lease release was not confirmed" in record.getMessage()
        and "TTL expiry is the fallback" in record.getMessage()
        for record in caplog.records
        if record.name == "dezzta.websocket_replica"
    )


def test_replica_runtime_fails_closed_without_verified_snapshot(tmp_path):
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "empty-replica.sqlite3"))

    class FakeRedis:
        closed = False
        def close(self):
            self.closed = True

    class IdleConsumer:
        def __init__(self, redis_client, store):
            self.redis = redis_client
            self.replica_store = store
            self.stream_key = "test:ohlcv:stream"
            self.block_ms = None
            self.on_event_applied = None
            self.group_ready = False
        def ensure_group(self):
            self.group_ready = True
            return True
        def consume_once(self):
            return {"status": "idle"}

    redis_client = FakeRedis()
    consumer = IdleConsumer(redis_client, replica)
    application = create_app(
        make_settings(),
        replica_runtime_factory=lambda: {
            "replica_store": replica, "consumer": consumer,
            "redis_client": redis_client, "stream_key": "test:ohlcv:stream",
        },
    )
    with pytest.raises(RuntimeError, match="verified replica snapshot"):
        with TestClient(application):
            pass
    assert redis_client.closed is True


def test_replica_runtime_fails_closed_when_redis_group_bootstrap_fails(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "group-source.sqlite3"))
    bar = OhlcvBar(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=101, series_type="contract",
        timeframe="1s", ts_start_ns=1_000_000_000, raw_symbol="ESZ6",
        open=Decimal("100"), high=Decimal("101"), low=Decimal("99"),
        close=Decimal("100.5"), volume=Decimal("2"),
        ts_event_ns=1_000_000_001, ts_received_ns=1_000_000_002,
        sequence=1, sequence_origin="local", origin="provider",
        completeness="unknown", bucket_policy="UTC_FIXED_V1",
    )
    assert source.apply(bar) == "inserted"
    snapshot_path = tmp_path / "group-snapshot.jsonl"
    source.export_global_snapshot(str(snapshot_path))
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "group-replica.sqlite3"))
    replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=source.source_id(),
    )

    class FakeRedis:
        closed = False
        def __init__(self):
            self.values = {}
        def set(self, key, value, nx=False, px=None):
            if nx and key in self.values:
                return False
            self.values[key] = value
            return True
        def eval(self, script, numkeys, key, token, *args):
            if self.values.get(key) != token:
                return 0
            if "PEXPIRE" in script:
                return 1
            if "DEL" in script:
                self.values.pop(key, None)
                return 1
            return 1
        def close(self):
            self.closed = True

    class UnavailableConsumer:
        def __init__(self, redis_client, store):
            self.redis = redis_client
            self.replica_store = store
            self.stream_key = "test:ohlcv:stream"
            self.block_ms = None
            self.on_event_applied = None
            self.group_name = "test:replica:group:generation-1"
        def ensure_group(self):
            raise ConnectionError("test-only Redis bootstrap outage")
        def consume_once(self):
            return {"status": "idle"}

    redis_client = FakeRedis()
    consumer = UnavailableConsumer(redis_client, replica)
    application = create_app(
        make_settings(),
        replica_runtime_factory=lambda: {
            "replica_store": replica, "consumer": consumer,
            "redis_client": redis_client, "stream_key": "test:ohlcv:stream",
        },
    )
    with pytest.raises(ConnectionError, match="test-only Redis bootstrap outage"):
        with TestClient(application):
            pass
    assert redis_client.closed is True
    assert application.state.ohlcv_replica_worker is None


def test_unhandled_http_error_keeps_request_id_and_redacts_sensitive_context(caplog):
    import logging

    token = "metrics-token-for-tests-only-32chars"
    application = create_app(replace(make_settings(), observability_metrics_token=token))

    def fail_with_private_details():
        raise RuntimeError("private-exception-sentinel")

    application.add_api_route("/_test/metrics-error", fail_with_private_details, methods=["GET"])
    client = TestClient(application, raise_server_exceptions=False)

    with caplog.at_level(logging.INFO, logger="dezzta.http"):
        response = client.get(
            "/_test/metrics-error?query_secret=private-query-sentinel",
            headers={
                "Authorization": "Bearer private-header-sentinel",
                "X-Private-Context": "private-header-value-sentinel",
            },
        )

    assert response.status_code == 500
    request_id = response.headers.get("x-request-id")
    assert request_id and len(request_id) == 32
    assert response.json() == {"detail": "Internal server error."}
    assert "private-exception-sentinel" not in response.text

    metrics = client.get(
        "/internal/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert metrics.status_code == 200
    matching = [
        row for row in metrics.json()["requests"]
        if row["route"] == "/_test/metrics-error" and row["status_class"] == "5xx"
    ]
    assert matching == [{
        "method": "GET",
        "route": "/_test/metrics-error",
        "status_class": "5xx",
        "count": 1,
    }]

    http_records = [
        record.message for record in caplog.records
        if record.name == "dezzta.http"
    ]
    serialized = " ".join(http_records)
    assert request_id in serialized
    for sentinel in (
        "private-query-sentinel",
        "private-header-sentinel",
        "private-header-value-sentinel",
        "private-exception-sentinel",
    ):
        assert sentinel not in serialized


def test_internal_operations_endpoints_require_operator_token_and_exclude_scrapes_from_metrics():
    operator_token = "metrics-operator-token-" + ("x" * 32)
    settings = replace(make_settings(), observability_metrics_token=operator_token)
    application = create_app(settings)

    with TestClient(application) as client:
        assert client.get("/internal/metrics").status_code == 401
        assert client.get("/internal/alert-delivery").status_code == 401
        assert client.get(
            "/internal/metrics",
            headers={"Authorization": "Bearer wrong-operator-token"},
        ).status_code == 401
        assert client.get(
            "/internal/alert-delivery",
            headers={"Authorization": "Bearer wrong-operator-token"},
        ).status_code == 401

        health = client.get("/health?query_secret=METRICS_QUERY_SENTINEL")
        assert health.status_code == 200

        headers = {"Authorization": f"Bearer {operator_token}"}
        alert_status = client.get("/internal/alert-delivery", headers=headers)
        assert alert_status.status_code == 200
        assert alert_status.headers["cache-control"] == "private, no-store, max-age=0"
        alert_payload = alert_status.json()
        assert alert_payload["scope"] == "process_local_since_start"
        assert alert_payload["enabled"] is False
        assert alert_payload["state"] == "disabled"
        assert "last_error_code" in alert_payload
        assert operator_token not in alert_status.text

        metrics = client.get("/internal/metrics", headers=headers)
        assert metrics.status_code == 200
        assert metrics.headers["cache-control"] == "private, no-store, max-age=0"
        payload = metrics.json()
        assert payload["scope"] == "process_local_since_start"
        assert payload["requests"] == [{
            "method": "GET",
            "route": "/health",
            "status_class": "2xx",
            "count": 1,
        }]
        assert len(payload["latency_ms"]) == 1
        assert payload["latency_ms"][0]["route"] == "/health"
        assert "METRICS_QUERY_SENTINEL" not in metrics.text
        assert operator_token not in metrics.text


def test_operator_incident_routes_require_separate_token_and_persist_state(tmp_path):
    operator_token = "operator-incident-token-for-tests-only-32"
    settings = make_settings(
        operator_incident_token=operator_token,
        instrument_registry_db_path=str(tmp_path / "operator-incidents.sqlite3"),
    )
    application = create_app(settings)
    incident = application.state.incident_store.record_incident(
        fingerprint="alert_delivery_degraded", category="alert_delivery",
        severity="warning", summary_code="delivery_attention",
    )
    incident_id = incident["incident_id"]
    with TestClient(application) as client:
        assert client.get("/internal/incidents").status_code == 401
        assert client.get("/internal/incidents", headers={
            "Authorization": "Bearer " + settings.observability_metrics_token
        }).status_code == 401
        listed = client.get("/internal/incidents", headers={"Authorization": f"Bearer {operator_token}"})
        assert listed.status_code == 200
        assert listed.json()["scope"] == "persistent_local_sqlite"
        assert listed.json()["incidents"][0]["incident_id"] == incident_id
        ack = client.post(f"/internal/incidents/{incident_id}/acknowledge",
                          headers={"Authorization": f"Bearer {operator_token}"})
        assert ack.status_code == 200 and ack.json()["status"] == "acknowledged"
        assert ack.json()["next_escalation_utc"] is None
        resolved = client.post(f"/internal/incidents/{incident_id}/resolve",
                               headers={"Authorization": f"Bearer {operator_token}"})
        assert resolved.status_code == 200 and resolved.json()["status"] == "resolved"


def test_operator_incident_routes_are_disabled_without_operator_token():
    with TestClient(create_app(make_settings())) as client:
        assert client.get("/internal/incidents").status_code == 404


def test_alert_reporter_persists_incident_and_resolves_on_recovery(tmp_path):
    import logging
    from app.alert_operations import LocalAlertReporter
    from app.incident_store import SQLiteIncidentStore
    store = SQLiteIncidentStore(str(tmp_path / "journal.sqlite3"))
    reporter = LocalAlertReporter(logging.getLogger("test.incident.reporter"), incident_store=store)
    reporter.report_batch(claimed=1, delivered=0, retry_scheduled=1, terminal_failed=0, lease_lost=0)
    rows = store.list_incidents()
    assert len(rows) == 1 and rows[0]["status"] == "open"
    reporter.report_batch(claimed=1, delivered=1, retry_scheduled=0, terminal_failed=0, lease_lost=0)
    assert store.list_incidents()[0]["status"] == "resolved"

def test_websocket_ticket_renewal_rejects_ticket_for_different_subject():
    application = _app_with_bars()

    class MultiSubjectVerifier:
        def verify(self, token):
            subjects = {
                "owner-token": "firebase-user-123",
                "other-account-token": "different-firebase-user",
            }
            subject = subjects.get(token)
            if subject is None:
                raise IdentityVerificationError("invalid token")
            return VerifiedPrincipal(
                subject=subject,
                issuer="https://securetoken.google.com/test-project",
                audience="test-project",
                auth_time=1_798_000_000,
            )

    application.state.identity_verifier = MultiSubjectVerifier()
    client = TestClient(application)
    owner_headers = {"Authorization": "Bearer owner-token"}
    other_headers = {"Authorization": "Bearer other-account-token"}

    owner_ticket_response = client.post(
        "/v1/auth/websocket-ticket", headers=owner_headers,
    )
    other_ticket_response = client.post(
        "/v1/auth/websocket-ticket", headers=other_headers,
    )
    assert owner_ticket_response.status_code == 200
    assert other_ticket_response.status_code == 200
    owner_ticket = owner_ticket_response.json()["ticket"]
    other_ticket = other_ticket_response.json()["ticket"]

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "ticket": owner_ticket})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"

        websocket.send_json({"type": "auth.renew", "ticket": other_ticket})
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()

    assert disconnected.value.code == 4401


def test_websocket_ticket_renewal_rechecks_revoked_instrument_entitlement():
    application = _app_with_bars()
    client = TestClient(application)
    headers = {"Authorization": "Bearer valid-firebase-token"}
    initial_ticket = client.post(
        "/v1/auth/websocket-ticket", headers=headers,
    ).json()["ticket"]
    renewal_ticket = client.post(
        "/v1/auth/websocket-ticket", headers=headers,
    ).json()["ticket"]

    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "ticket": initial_ticket})
        assert websocket.receive_json()["type"] == "market_data.status"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
            "series": {
                "dataset": "GLBX.MDP3",
                "publisherId": 1,
                "instrumentId": 101,
                "rawSymbol": "ESZ6",
                "timeframe": "1s",
            },
        })
        assert websocket.receive_json()["type"] == "market_data.ohlcv.snapshot"

        application.state.instrument_entitlements.revoke(
            subject="firebase-user-123",
            canonical_instrument_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
        )
        websocket.send_json({"type": "auth.renew", "ticket": renewal_ticket})
        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()

    assert disconnected.value.code == 4403


def test_metrics_storage_failure_does_not_block_http_or_websocket(tmp_path, monkeypatch):
    import sqlite3
    import time
    from itertools import count
    from threading import Event
    from uuid import UUID
    from app.metrics_collector import SQLiteMetricsCollector

    flush_attempted = Event()
    operator_token = "metrics-token-for-tests-only-32chars"
    identifiers = count()

    def fail_metrics_flush(self, *args, **kwargs):
        flush_attempted.set()
        raise sqlite3.OperationalError("database or disk is full")

    monkeypatch.setattr(main_module, "uuid4", lambda: UUID(int=next(identifiers)))
    monkeypatch.setattr(SQLiteMetricsCollector, "flush", fail_metrics_flush)
    settings = replace(
        make_settings(),
        observability_metrics_token=operator_token,
        observability_metrics_db_path=str(tmp_path / "metrics.sqlite3"),
    )
    application = create_app(settings)
    _install_test_identity(application)

    with TestClient(application) as client:
        assert flush_attempted.wait(timeout=3)
        deadline = time.monotonic() + 2
        while application.state.metrics_collector_status["state"] != "degraded" and time.monotonic() < deadline:
            time.sleep(0.01)
        assert application.state.metrics_collector_status["state"] == "degraded"

        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        metrics = client.get(
            "/internal/metrics",
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        assert metrics.status_code == 200
        assert metrics.json()["collector_status"]["state"] == "degraded"

        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            assert websocket.receive_json()["type"] == "market_data.status"



def test_incident_escalation_lifespan_dispatches_sanitized_due_event(monkeypatch, tmp_path, caplog):
    import json
    import logging
    import threading
    import time
    from app.incident_store import SQLiteIncidentStore

    attempted = threading.Event()
    calls = 0

    def fake_escalate_due(self, *, now_utc=None):
        nonlocal calls
        calls += 1
        attempted.set()
        if calls == 1:
            return [{
                "incident_id": "12345678-1234-5678-1234-567812345678",
                "severity": "critical",
                "summary_code": "delivery_attention",
                "escalation_level": 1,
            }]
        return []

    monkeypatch.setattr(SQLiteIncidentStore, "escalate_due", fake_escalate_due)
    application = create_app(replace(
        make_settings(),
        instrument_registry_db_path=str(tmp_path / "incident-escalation.sqlite3"),
    ))

    with caplog.at_level(logging.ERROR, logger="dezzta.incidents"):
        with TestClient(application):
            assert attempted.wait(timeout=3)
            deadline = time.monotonic() + 2
            while not any(
                record.name == "dezzta.incidents"
                and '"operator_incident_escalated"' in record.message
                for record in caplog.records
            ) and time.monotonic() < deadline:
                time.sleep(0.01)

    events = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "dezzta.incidents"
    ]
    assert events == [{
        "event": "operator_incident_escalated",
        "incident_id": "12345678-1234-5678-1234-567812345678",
        "severity": "critical",
        "summary_code": "delivery_attention",
        "escalation_level": 1,
    }]
    assert calls >= 1



def test_websocket_metrics_middleware_is_wired_into_authenticated_application():
    application = create_app(make_settings())
    _install_test_identity(application)

    with TestClient(application) as client:
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "valid-firebase-token"})
            assert websocket.receive_json()["type"] == "market_data.status"

            active = application.state.websocket_metrics.snapshot()
            assert active["connections_started"] == 1
            assert active["connections_active"] == 1
            assert active["connections_completed"] == 0
            # A successful handshake is counted immediately, even while active.
            assert active["connections_accepted"] == 1

        completed = application.state.websocket_metrics.snapshot()
        assert completed["connections_started"] == 1
        assert completed["connections_active"] == 0
        assert completed["connections_completed"] == 1
        assert completed["connections_accepted"] == 1


def test_closing_one_websocket_client_preserves_other_client_subscription() -> None:
    """A mobile client's disconnect must never stop another user's live socket."""
    application = _app_with_bars()
    application.state.instrument_entitlements.grant(
        subject="firebase-user-456",
        canonical_instrument_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
    )

    class MultiUserVerifier:
        def verify(self, token):
            subjects = {
                "user-a-token": "firebase-user-123",
                "user-b-token": "firebase-user-456",
            }
            subject = subjects.get(token)
            if subject is None:
                raise IdentityVerificationError("invalid token")
            return VerifiedPrincipal(
                subject=subject,
                issuer="https://securetoken.google.com/test-project",
                audience="test-project",
                auth_time=1_798_000_000,
            )

    application.state.identity_verifier = MultiUserVerifier()

    with TestClient(application) as client:
        with client.websocket_connect("/ws/market-data") as surviving:
            surviving.send_json({"type": "auth", "token": "user-a-token"})
            assert surviving.receive_json()["type"] == "market_data.status"
            surviving.send_json({
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                "series": {
                    "dataset": "GLBX.MDP3",
                    "publisherId": 1,
                    "instrumentId": 101,
                    "rawSymbol": "ESZ6",
                    "timeframe": "1s",
                },
            })
            assert surviving.receive_json()["type"] == "market_data.ohlcv.snapshot"
            assert application.state.ohlcv_stream_hub.subscriber_count == 1

            with client.websocket_connect("/ws/market-data") as closing:
                closing.send_json({"type": "auth", "token": "user-b-token"})
                assert closing.receive_json()["type"] == "market_data.status"
                closing.send_json({
                    "type": "market_data.subscribe",
                    "version": 1,
                    "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                    "series": {
                        "dataset": "GLBX.MDP3",
                        "publisherId": 1,
                        "instrumentId": 101,
                        "rawSymbol": "ESZ6",
                        "timeframe": "1s",
                    },
                })
                assert closing.receive_json()["type"] == "market_data.ohlcv.snapshot"
                assert application.state.ohlcv_stream_hub.subscriber_count == 2

            # Closing the second app instance removes only its own subscription.
            assert application.state.ohlcv_stream_hub.subscriber_count == 1
            surviving.send_text("ping")
            assert surviving.receive_json()["type"] == "market_data.pong"


def test_real_tls_websocket_upgrade_ticket_auth_origin_policy_and_multi_user_heartbeat(tmp_path) -> None:
    """Exercise HTTPS ticket issuance, real WSS, Origin policy, and multi-user isolation."""
    settings = make_settings(cors_allowed_origins=("https://localhost",))
    application = _app_with_bars(settings=settings)
    canonical_id = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
    application.state.instrument_entitlements.grant(
        subject="firebase-user-456",
        canonical_instrument_id=canonical_id,
    )

    class MultiUserVerifier:
        def verify(self, token):
            subjects = {
                "valid-firebase-token": "firebase-user-123",
                "user-b-token": "firebase-user-456",
            }
            subject = subjects.get(token)
            if subject is None:
                raise IdentityVerificationError("invalid token")
            return VerifiedPrincipal(
                subject=subject,
                issuer="https://securetoken.google.com/test-project",
                audience="test-project",
                auth_time=1_798_000_000,
            )

    application.state.identity_verifier = MultiUserVerifier()

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "DEZZTA ephemeral test CA")])
    ca_certificate = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    server_certificate = (
        x509.CertificateBuilder()
        .subject_name(server_name)
        .issuer_name(ca_certificate.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            ]),
            critical=False,
        )
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    ca_path = tmp_path / "test-ca.pem"
    certificate_path = tmp_path / "server-cert.pem"
    key_path = tmp_path / "server-key.pem"
    ca_path.write_bytes(ca_certificate.public_bytes(serialization.Encoding.PEM))
    certificate_path.write_bytes(server_certificate.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(server_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ))

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(16)
    listener.setblocking(False)
    port = listener.getsockname()[1]

    server = uvicorn.Server(uvicorn.Config(
        application,
        host="127.0.0.1",
        port=port,
        lifespan="off",
        log_level="critical",
        access_log=False,
        ws="websockets",
        ssl_certfile=str(certificate_path),
        ssl_keyfile=str(key_path),
    ))

    async def exercise_real_transport() -> None:
        server_task = asyncio.create_task(server.serve(sockets=[listener]))
        try:
            for _ in range(500):
                if server.started:
                    break
                if server_task.done():
                    await server_task
                await asyncio.sleep(0.01)
            assert server.started, "Uvicorn TLS test server did not start"

            uri = f"wss://127.0.0.1:{port}/ws/market-data"
            trusted_context = ssl.create_default_context(cafile=str(ca_path))

            async def issue_ticket(token: str) -> str:
                async with httpx.AsyncClient(
                    verify=trusted_context,
                    trust_env=False,
                    timeout=5,
                    base_url=f"https://127.0.0.1:{port}",
                ) as http_client:
                    response = await http_client.post(
                        "/v1/auth/websocket-ticket",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Origin": "https://localhost",
                        },
                    )
                assert response.status_code == 200, response.text
                assert response.headers["access-control-allow-origin"] == "https://localhost"
                assert "no-store" in response.headers.get("cache-control", "").lower()
                payload = response.json()
                assert payload["expiresIn"] == 90
                assert payload["purpose"] == "market-data"
                assert isinstance(payload["ticket"], str) and len(payload["ticket"]) >= 40
                return payload["ticket"]

            initial_ticket = await issue_ticket("valid-firebase-token")
            async with websockets.connect(
                uri,
                ssl=trusted_context,
                origin="https://localhost",
                open_timeout=5,
                close_timeout=2,
                ping_interval=None,
            ) as websocket:
                await websocket.send(json.dumps({
                    "type": "auth",
                    "ticket": initial_ticket,
                }))
                status = json.loads(await asyncio.wait_for(websocket.recv(), timeout=5))
                assert status["type"] == "market_data.status"

                await websocket.send(json.dumps({
                    "type": "market_data.subscribe",
                    "version": 1,
                    "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                    "series": {
                        "dataset": "GLBX.MDP3",
                        "publisherId": 1,
                        "instrumentId": 101,
                        "rawSymbol": "ESZ6",
                        "timeframe": "1s",
                    },
                }))
                snapshot = json.loads(await asyncio.wait_for(websocket.recv(), timeout=5))
                assert snapshot["type"] == "market_data.ohlcv.snapshot"
                assert snapshot["count"] == 4

                renewal_ticket = await issue_ticket("valid-firebase-token")
                await websocket.send(json.dumps({
                    "type": "auth.renew",
                    "ticket": renewal_ticket,
                }))
                renewed = json.loads(await asyncio.wait_for(websocket.recv(), timeout=5))
                assert renewed == {"type": "market_data.auth.renewed", "version": 1}

                await websocket.send("ping")
                pong = json.loads(await asyncio.wait_for(websocket.recv(), timeout=5))
                assert pong == {"type": "market_data.pong", "version": 1}

            # Two distinct authenticated users share the real WSS service independently.
            async with websockets.connect(
                uri,
                ssl=trusted_context,
                origin="https://localhost",
                open_timeout=5,
                close_timeout=2,
                ping_interval=None,
            ) as surviving:
                surviving_ticket = await issue_ticket("valid-firebase-token")
                await surviving.send(json.dumps({
                    "type": "auth",
                    "ticket": surviving_ticket,
                }))
                assert json.loads(await asyncio.wait_for(surviving.recv(), timeout=5))["type"] == "market_data.status"
                await surviving.send(json.dumps({
                    "type": "market_data.subscribe",
                    "version": 1,
                    "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                    "series": {
                        "dataset": "GLBX.MDP3",
                        "publisherId": 1,
                        "instrumentId": 101,
                        "rawSymbol": "ESZ6",
                        "timeframe": "1s",
                    },
                }))
                assert json.loads(await asyncio.wait_for(surviving.recv(), timeout=5))["type"] == "market_data.ohlcv.snapshot"

                async with websockets.connect(
                    uri,
                    ssl=trusted_context,
                    origin="https://localhost",
                    open_timeout=5,
                    close_timeout=2,
                    ping_interval=None,
                ) as departing:
                    departing_ticket = await issue_ticket("user-b-token")
                    await departing.send(json.dumps({
                        "type": "auth",
                        "ticket": departing_ticket,
                    }))
                    assert json.loads(await asyncio.wait_for(departing.recv(), timeout=5))["type"] == "market_data.status"
                    await departing.send(json.dumps({
                        "type": "market_data.subscribe",
                        "version": 1,
                        "canonicalInstrumentId": "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
                        "series": {
                            "dataset": "GLBX.MDP3",
                            "publisherId": 1,
                            "instrumentId": 101,
                            "rawSymbol": "ESZ6",
                            "timeframe": "1s",
                        },
                    }))
                    assert json.loads(await asyncio.wait_for(departing.recv(), timeout=5))["type"] == "market_data.ohlcv.snapshot"
                    assert application.state.ohlcv_stream_hub.subscriber_count == 2

                # The client close handshake can complete just before ASGI finally cleanup.
                cleanup_deadline = asyncio.get_running_loop().time() + 5
                while (
                    application.state.ohlcv_stream_hub.subscriber_count != 1
                    and asyncio.get_running_loop().time() < cleanup_deadline
                ):
                    await asyncio.sleep(0.01)
                assert application.state.ohlcv_stream_hub.subscriber_count == 1
                await surviving.send("ping")
                assert json.loads(await asyncio.wait_for(surviving.recv(), timeout=5)) == {
                    "type": "market_data.pong",
                    "version": 1,
                }

            # A valid TLS connection with a disallowed browser Origin must not upgrade.
            try:
                async with websockets.connect(
                    uri,
                    ssl=trusted_context,
                    origin="https://untrusted.example",
                    open_timeout=5,
                    close_timeout=2,
                    ping_interval=None,
                ):
                    raise AssertionError("Disallowed Origin unexpectedly upgraded to WebSocket")
            except Exception as error:
                response = getattr(error, "response", None)
                status_code = getattr(response, "status_code", None)
                status_code = status_code or getattr(error, "status_code", None)
                assert status_code == 403, f"Expected HTTP 403 for disallowed Origin, got {error!r}"

            # The same endpoint must reject a client that does not trust its test CA.
            try:
                async with websockets.connect(
                    uri,
                    ssl=ssl.create_default_context(),
                    origin="https://localhost",
                    open_timeout=5,
                    close_timeout=2,
                    ping_interval=None,
                ):
                    raise AssertionError("Untrusted TLS certificate unexpectedly connected")
            except ssl.SSLCertVerificationError:
                pass
        finally:
            server.should_exit = True
            if not server_task.done():
                await asyncio.wait_for(server_task, timeout=10)
            else:
                await server_task
            listener.close()

    asyncio.run(exercise_real_transport())
