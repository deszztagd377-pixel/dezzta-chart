from pathlib import Path

from app.websocket_tickets import WEBSOCKET_TICKET_TTL_SECONDS


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_backend_readme_matches_single_use_websocket_ticket_contract():
    readme = (BACKEND_ROOT / "README.md").read_text(encoding="utf-8")
    normalized = readme.lower()

    assert "post /v1/auth/websocket-ticket" in normalized
    assert "authorization: bearer firebase_id_token" in normalized
    assert '{"type":"auth","ticket":"one_time_websocket_ticket"}' in normalized
    assert f"current ticket ttl is {WEBSOCKET_TICKET_TTL_SECONDS} seconds" in normalized
    assert "non-production compatibility path" in normalized
    assert "not yet\nimplemented" not in normalized


def test_documented_ticket_endpoint_and_production_legacy_auth_gate_exist_in_source():
    main_source = (BACKEND_ROOT / "app" / "main.py").read_text(encoding="utf-8")

    assert '@application.post("/v1/auth/websocket-ticket"' in main_source
    assert (
        'if config.app_env.strip().lower() == "production" '
        'or not isinstance(supplied_token, str) or not supplied_token:'
    ) in main_source
