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
