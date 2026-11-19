"""Regression coverage for the isolated, synthetic Vercel WebSocket POC."""
import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


POC_PATH = Path(__file__).resolve().parents[2] / "poc" / "vercel_ws" / "index.py"
SPEC = importlib.util.spec_from_file_location("dezzta_vercel_ws_poc", POC_PATH)
assert SPEC is not None and SPEC.loader is not None
POC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POC)
CLIENT = TestClient(POC.app)


def test_health_is_explicitly_synthetic_and_not_connected_to_production_data():
    response = CLIENT.get("/health")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == {
        "status": "ok",
        "service": "dezzta-ws-poc",
        "mode": "synthetic-only",
        "production_data_connected": False,
    }


def test_homepage_has_no_store_and_restrictive_content_security_policy():
    response = CLIENT.get("/")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    policy = response.headers["content-security-policy"]
    assert "default-src 'none'" in policy
    assert "frame-ancestors 'none'" in policy
    assert "connect-src 'self' wss:" in policy


def test_websocket_ready_and_ping_pong_are_bound_to_one_synthetic_session():
    with CLIENT.websocket_connect("/ws") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "ready"
        assert ready["mode"] == "synthetic-only"
        assert isinstance(ready["session_id"], str) and len(ready["session_id"]) == 32

        websocket.send_json({"type": "ping", "id": "regression-1"})
        pong = websocket.receive_json()
        assert pong["type"] == "pong"
        assert pong["id"] == "regression-1"
        assert pong["sequence"] == 1
        assert pong["session_id"] == ready["session_id"]
        assert isinstance(pong["server_time_unix_ms"], int)


def test_websocket_enforces_message_size_and_closes_with_1009():
    with CLIENT.websocket_connect("/ws") as websocket:
        assert websocket.receive_json()["type"] == "ready"
        websocket.send_text("x" * (POC.MAX_MESSAGE_CHARS + 1))

        assert websocket.receive_json() == {
            "type": "error", "code": "message_too_large"
        }
        with pytest.raises(WebSocketDisconnect) as caught:
            websocket.receive_json()
        assert caught.value.code == 1009


def test_websocket_rate_limit_allows_twelve_messages_then_closes_with_1013():
    with CLIENT.websocket_connect("/ws") as websocket:
        ready = websocket.receive_json()
        for index in range(POC.MAX_MESSAGES_PER_WINDOW):
            websocket.send_json({"type": "ping", "id": f"rate-{index}"})
            pong = websocket.receive_json()
            assert pong["type"] == "pong"
            assert pong["sequence"] == index + 1
            assert pong["session_id"] == ready["session_id"]

        websocket.send_json({"type": "ping", "id": "rate-over-limit"})
        assert websocket.receive_json() == {
            "type": "error", "code": "rate_limited"
        }
        with pytest.raises(WebSocketDisconnect) as caught:
            websocket.receive_json()
        assert caught.value.code == 1013
