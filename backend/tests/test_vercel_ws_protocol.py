from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
POC_SOURCE = REPOSITORY_ROOT / "poc" / "vercel_ws" / "index.py"
SPEC = importlib.util.spec_from_file_location("dezzta_vercel_ws_poc", POC_SOURCE)
assert SPEC is not None and SPEC.loader is not None
POC_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POC_MODULE)
client = TestClient(POC_MODULE.app)


def test_synthetic_websocket_handshake_and_ping_pong_round_trip() -> None:
    with client.websocket_connect("/ws") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "ready"
        assert ready["mode"] == "synthetic-only"
        assert isinstance(ready["session_id"], str) and ready["session_id"]

        websocket.send_json({"type": "ping", "id": "protocol-test-1"})
        pong = websocket.receive_json()

        assert pong["type"] == "pong"
        assert pong["id"] == "protocol-test-1"
        assert pong["sequence"] == 1
        assert pong["session_id"] == ready["session_id"]
        assert isinstance(pong["server_time_unix_ms"], int)


def test_synthetic_websocket_rejects_invalid_message_and_closes() -> None:
    with client.websocket_connect("/ws") as websocket:
        assert websocket.receive_json()["type"] == "ready"
        websocket.send_json({"type": "not-a-ping"})

        error = websocket.receive_json()
        assert error == {"type": "error", "code": "invalid_message"}

        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()
        assert disconnected.value.code == 1003


def test_synthetic_websocket_rejects_oversized_message_and_closes() -> None:
    with client.websocket_connect("/ws") as websocket:
        assert websocket.receive_json()["type"] == "ready"
        websocket.send_text("x" * 513)

        error = websocket.receive_json()
        assert error == {"type": "error", "code": "message_too_large"}

        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()
        assert disconnected.value.code == 1009


def test_synthetic_websocket_enforces_twelve_messages_per_ten_seconds() -> None:
    with client.websocket_connect("/ws") as websocket:
        assert websocket.receive_json()["type"] == "ready"

        for sequence in range(1, 13):
            websocket.send_json({"type": "ping", "id": f"rate-test-{sequence}"})
            pong = websocket.receive_json()
            assert pong["type"] == "pong"
            assert pong["sequence"] == sequence

        websocket.send_json({"type": "ping", "id": "rate-test-13"})
        error = websocket.receive_json()
        assert error == {"type": "error", "code": "rate_limited"}

        with pytest.raises(WebSocketDisconnect) as disconnected:
            websocket.receive_json()
        assert disconnected.value.code == 1013


def test_synthetic_websocket_health_is_explicitly_non_production() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "dezzta-ws-poc",
        "mode": "synthetic-only",
        "production_data_connected": False,
    }
    assert response.headers["cache-control"] == "no-store"
