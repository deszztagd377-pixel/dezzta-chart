import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.config import Settings
from app.main import create_app
from app.identity import IdentityVerificationError, VerifiedPrincipal
from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import ProviderInstrumentMapping


def make_settings(token: str = "test-secret") -> Settings:
    return Settings(
        app_env="test",
        market_data_ws_token=token,
        cors_allowed_origins=("http://localhost:5173",),
    )


def test_health_endpoint() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "dezzta-chart-backend",
    }


def test_market_data_status_is_honest_about_unimplemented_feed() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/v1/market-data/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["instruments"] == ["ES", "NQ", "GC"]
    assert payload["connected"] is False
    assert payload["ingestion_implemented"] is False


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


def test_ohlcv_endpoint_starts_empty_and_does_not_fabricate_bars() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/v1/ohlcv")
    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "market_data.ohlcv.snapshot"
    assert payload["state"] == "unavailable"
    assert payload["timestampUnit"] == "nanoseconds"
    assert payload["priceRepresentation"] == "decimal-string"
    assert payload["bars"] == []
    assert "provider ingestion is not connected" in payload["detail"]


def test_ohlcv_endpoint_rejects_unsupported_timeframe() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/v1/ohlcv?timeframe=2m")
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
    payload = client.get("/v1/ohlcv?timeframe=1s").json()
    assert payload["state"] == "ready" and payload["count"] == 4 and payload["truncated"] is False
    assert payload["bars"][0]["sequenceOrigin"] == "local"
    limited = client.get("/v1/ohlcv?timeframe=1s&limit=2").json()
    assert limited["count"] == 2 and limited["truncated"] is True
    assert limited["bars"][-1]["tsStartNs"] == str(_T0 + 3 * _NS)
    derived = client.get("/v1/ohlcv?timeframe=1m").json()
    assert derived["bars"][0]["volume"] == "40" and derived["bars"][0]["origin"] == "derived"
    ranged = client.get(f"/v1/ohlcv?timeframe=1s&start_ns={_T0 + _NS}&end_ns={_T0 + 3 * _NS}").json()
    assert ranged["count"] == 2


@pytest.mark.parametrize("query", ["timeframe=2m", "start_ns=abc", "start_ns=10&end_ns=5", "limit=0"])
def test_ohlcv_endpoint_rejects_invalid_query_parameters(query: str) -> None:
    client = TestClient(create_app(make_settings()))
    assert client.get(f"/v1/ohlcv?{query}").status_code == 422


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
    client = TestClient(_app_with_bars())
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
        assert snapshot["count"] == 4
        assert snapshot["bars"][-1]["tsStartNs"] == str(_T0 + 3 * _NS)


def test_websocket_rejects_invalid_ohlcv_subscription() -> None:
    client = TestClient(create_app(make_settings()))
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
    )
    application = create_app(settings, live_source_factory=FakeLive)
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
