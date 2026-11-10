from collections import deque

import hashlib
import pytest
import tempfile
from pathlib import Path
from uuid import uuid4
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from dataclasses import replace

from app.config import Settings
from app.main import _allow_websocket_ping, create_app
from app.identity import IdentityProviderUnavailable, IdentityVerificationError, VerifiedPrincipal
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


def make_settings(token: str = "test-secret") -> Settings:
    return Settings(
        app_env="test",
        market_data_ws_token=token,
        cors_allowed_origins=("http://localhost:5173",),
        instrument_registry_db_path=_test_database_path(),
        **_test_calendar_configuration(),
    )


def test_websocket_ping_rate_limit_allows_twenty_messages_in_window() -> None:
    timestamps: deque[float] = deque()
    assert all(_allow_websocket_ping(timestamps, 1.0) for _ in range(20))
    assert not _allow_websocket_ping(timestamps, 1.0)


def test_websocket_ping_rate_limit_expires_messages_at_window_boundary() -> None:
    timestamps: deque[float] = deque()
    assert all(_allow_websocket_ping(timestamps, 1.0) for _ in range(20))
    assert _allow_websocket_ping(timestamps, 11.0)
    assert len(timestamps) == 1


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


def _app_with_bars(count: int = 4):
    application = create_app(make_settings())
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
        assert [event["cursor"] for event in replayed] == sorted(
            event["cursor"] for event in replayed
        )
        assert all(event["series"]["rawSymbol"] == "ESZ6" for event in replayed)
        complete = websocket.receive_json()
        assert complete["type"] == "market_data.ohlcv.replay_complete"
        assert complete["cursor"] == expected_high_water


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
