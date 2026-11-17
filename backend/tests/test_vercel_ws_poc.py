from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "poc" / "vercel_ws" / "index.py"
VERCEL_CONFIG_PATH = ROOT / "poc" / "vercel_ws" / "vercel.json"
SPEC = importlib.util.spec_from_file_location("dezzta_vercel_ws_poc", APP_PATH)
assert SPEC is not None and SPEC.loader is not None
POC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POC)
client = TestClient(POC.app)


def test_vercel_project_explicitly_enables_fluid_compute() -> None:
    config = json.loads(VERCEL_CONFIG_PATH.read_text(encoding="utf-8"))
    assert config["fluid"] is True


def test_health_is_synthetic_only_and_never_claims_production_data() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "dezzta-ws-poc",
        "mode": "synthetic-only",
        "production_data_connected": False,
    }
    assert response.headers["cache-control"] == "no-store"


def test_browser_probe_page_is_present_and_no_store() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Protected WebSocket POC" in response.text
    assert 'new WebSocket(' in response.text
    assert response.headers["cache-control"] == "no-store"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert 'log.textContent += "\\n" + JSON.stringify(value);' in response.text


def test_websocket_sends_ready_then_ordered_synthetic_pongs() -> None:
    with client.websocket_connect("/ws") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "ready"
        assert ready["mode"] == "synthetic-only"
        assert isinstance(ready["session_id"], str) and len(ready["session_id"]) == 32

        websocket.send_json({"type": "ping", "id": "test-1"})
        first = websocket.receive_json()
        websocket.send_json({"type": "ping", "id": "test-2"})
        second = websocket.receive_json()

        assert first["type"] == "pong"
        assert first["id"] == "test-1"
        assert first["sequence"] == 1
        assert second["type"] == "pong"
        assert second["id"] == "test-2"
        assert second["sequence"] == 2
        assert first["session_id"] == second["session_id"] == ready["session_id"]


def test_websocket_fresh_session_gets_a_new_id_and_resets_sequence() -> None:
    session_ids: list[str] = []
    for number in (1, 2):
        with client.websocket_connect("/ws") as websocket:
            ready = websocket.receive_json()
            assert ready["type"] == "ready"
            session_ids.append(ready["session_id"])
            websocket.send_json({"type": "ping", "id": f"session-{number}"})
            pong = websocket.receive_json()
            assert pong["type"] == "pong"
            assert pong["id"] == f"session-{number}"
            assert pong["sequence"] == 1
            assert pong["session_id"] == ready["session_id"]
    assert session_ids[0] != session_ids[1]


def test_browser_probe_automatically_pings_each_fresh_session() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert 'if (message.type === "ready")' in response.text
    assert "pingNumber = 0;" in response.text
    assert "sendPing();" in response.text
    assert 'pingButton.addEventListener("click", sendPing);' in response.text


def test_websocket_rejects_oversized_message() -> None:
    with client.websocket_connect("/ws") as websocket:
        assert websocket.receive_json()["type"] == "ready"
        websocket.send_text("x" * (POC.MAX_MESSAGE_CHARS + 1))
        assert websocket.receive_json() == {"type": "error", "code": "message_too_large"}
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_json()


def test_websocket_rejects_invalid_message_shape() -> None:
    with client.websocket_connect("/ws") as websocket:
        assert websocket.receive_json()["type"] == "ready"
        websocket.send_json({"type": "subscribe", "id": "not-supported"})
        assert websocket.receive_json() == {"type": "error", "code": "invalid_message"}
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_json()


def test_websocket_enforces_bounded_message_rate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(POC, "MAX_MESSAGES_PER_WINDOW", 2)
    monkeypatch.setattr(POC, "RATE_WINDOW_SECONDS", 60.0)
    with client.websocket_connect("/ws") as websocket:
        assert websocket.receive_json()["type"] == "ready"
        for number in (1, 2):
            websocket.send_json({"type": "ping", "id": f"rate-{number}"})
            assert websocket.receive_json()["type"] == "pong"
        websocket.send_json({"type": "ping", "id": "rate-3"})
        assert websocket.receive_json() == {"type": "error", "code": "rate_limited"}
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_json()


def test_websocket_closes_an_idle_session(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(POC, "IDLE_TIMEOUT_SECONDS", 0.01)
    with client.websocket_connect("/ws") as websocket:
        assert websocket.receive_json()["type"] == "ready"
        assert websocket.receive_json()["type"] == "idle_timeout"
        with pytest.raises(WebSocketDisconnect):
            websocket.receive_json()
