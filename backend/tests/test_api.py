import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.config import Settings
from app.main import create_app


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


def test_websocket_requires_authentication() -> None:
    client = TestClient(create_app(make_settings()))
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/market-data") as websocket:
            websocket.send_json({"type": "auth", "token": "wrong-token"})
            websocket.receive_json()


def test_websocket_sends_status_after_authentication() -> None:
    client = TestClient(create_app(make_settings()))
    with client.websocket_connect("/ws/market-data") as websocket:
        websocket.send_json({"type": "auth", "token": "test-secret"})
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
        websocket.send_json({"type": "auth", "token": "test-secret"})
        status = websocket.receive_json()
        assert status["type"] == "market_data.status"
        assert status["schema"] == "ohlcv"
        websocket.send_json({
            "type": "market_data.subscribe",
            "version": 1,
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
            websocket.send_json({"type": "auth", "token": "test-secret"})
            assert websocket.receive_json()["type"] == "market_data.status"
            websocket.send_json({
                "type": "market_data.subscribe",
                "version": 1,
                "series": {
                    "dataset": "GLBX.MDP3",
                    "publisherId": 1,
                    "instrumentId": 101,
                    "rawSymbol": "ESZ6",
                    "timeframe": "2m",
                },
            })
            websocket.receive_json()
