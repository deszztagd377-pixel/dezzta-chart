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
