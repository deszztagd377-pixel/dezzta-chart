from pathlib import Path
import re


def test_synthetic_websocket_lifetime_probe_is_bounded_and_beats_idle_timeout():
    source_path = (
        Path(__file__).resolve().parents[2]
        / "poc"
        / "vercel_ws"
        / "index.py"
    )
    source = source_path.read_text(encoding="utf-8")

    idle_match = re.search(r"IDLE_TIMEOUT_SECONDS\s*=\s*([0-9.]+)", source)
    heartbeat_match = re.search(
        r"HEARTBEAT_INTERVAL_MS\s*=\s*(\d+)", source
    )
    probe_limit_match = re.search(r"PROBE_LIMIT_MS\s*=\s*(\d+)", source)

    assert idle_match is not None
    assert heartbeat_match is not None
    assert probe_limit_match is not None

    idle_ms = float(idle_match.group(1)) * 1000
    heartbeat_ms = int(heartbeat_match.group(1))
    probe_limit_ms = int(probe_limit_match.group(1))

    # Heartbeats must remain comfortably below the application idle timeout.
    assert heartbeat_ms <= idle_ms / 2
    # The bounded client observation must extend beyond Hobby's documented
    # 300-second Fluid Compute maximum, but stop shortly afterward.
    assert 300_000 < probe_limit_ms <= 360_000
    assert 'type:"lifetime_probe_started"' in source
    assert 'type:"websocket_close"' in source
    assert "performance.now()" in source
    assert "setInterval" in source
    assert "clearInterval" in source
    assert 'socket.close(1000, "bounded synthetic probe complete")' in source
