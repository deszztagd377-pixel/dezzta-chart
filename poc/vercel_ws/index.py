from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections import deque
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

IDLE_TIMEOUT_SECONDS = 25.0
MAX_MESSAGE_CHARS = 512
MAX_MESSAGES_PER_WINDOW = 12
RATE_WINDOW_SECONDS = 10.0

app = FastAPI(
    title="DEZZTA CHART isolated WebSocket proof",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DEZZTA CHART — Protected WebSocket POC</title>
<style>
:root{color-scheme:dark;font:16px system-ui,sans-serif;background:#0b1220;color:#e5edf8}
body{max-width:760px;margin:0 auto;padding:24px 16px}
main{border:1px solid #26354b;border-radius:16px;padding:20px;background:#111c2e}
h1{font-size:1.35rem;margin:0 0 8px}p{color:#a9bad0;line-height:1.5}
.status{padding:10px 12px;border-radius:8px;background:#1c2a3f;margin:16px 0}
button{border:1px solid #48617e;border-radius:9px;background:#1a2a40;color:#eef6ff;padding:11px 15px;margin:4px;min-height:44px}
button:disabled{opacity:.45}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#080e18;border-radius:10px;padding:14px;min-height:170px;max-height:360px;overflow:auto}
small{color:#91a4bd}
</style>
</head>
<body>
<main>
<h1>DEZZTA CHART — Protected WebSocket POC</h1>
<p>Isolated synthetic connectivity check only. No market data, account credentials, database, Redis, or production worker is connected.</p>
<div class="status" id="status" role="status" aria-live="polite">Disconnected</div>
<button id="connect">Connect</button>
<button id="ping" disabled>Send synthetic ping</button>
<button id="disconnect" disabled>Disconnect</button>
<pre id="log" aria-live="polite">Waiting for a test connection.</pre>
<small>Connection is intentionally short-lived. Reconnect manually after a close to verify a fresh session.</small>
</main>
<script>
(() => {
  const status = document.getElementById("status");
  const log = document.getElementById("log");
  const connectButton = document.getElementById("connect");
  const pingButton = document.getElementById("ping");
  const disconnectButton = document.getElementById("disconnect");
  let socket = null;
  let pingNumber = 0;
  const write = (value) => {
    log.textContent += "\\n" + JSON.stringify(value);
    log.scrollTop = log.scrollHeight;
  };
  const setState = (value, connected) => {
    status.textContent = value;
    connectButton.disabled = connected;
    pingButton.disabled = !connected;
    disconnectButton.disabled = !connected;
  };
  connectButton.addEventListener("click", () => {
    if (socket && socket.readyState <= WebSocket.OPEN) return;
    const scheme = location.protocol === "https:" ? "wss:" : "ws:";
    socket = new WebSocket(scheme + "//" + location.host + "/ws");
    setState("Connecting…", false);
    socket.addEventListener("open", () => setState("Connected", true));
    socket.addEventListener("message", (event) => {
      try {
        const message = JSON.parse(event.data);
        write(message);
        if (message.type === "idle_timeout") setState("Server closed idle session", false);
      } catch {
        write({type:"invalid_server_message"});
      }
    });
    socket.addEventListener("close", (event) => setState("Closed (" + event.code + ")", false));
    socket.addEventListener("error", () => {
      write({type:"transport_error",detail:"Check protected deployment access and WebSocket upgrade."});
      setState("Connection error", false);
    });
  });
  pingButton.addEventListener("click", () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    pingNumber += 1;
    socket.send(JSON.stringify({type:"ping",id:"browser-" + pingNumber}));
  });
  disconnectButton.addEventListener("click", () => socket?.close(1000, "manual test disconnect"));
})();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def home() -> HTMLResponse:
    return HTMLResponse(
        PAGE,
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self' wss:; base-uri 'none'; frame-ancestors 'none'",
        },
    )


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "service": "dezzta-ws-poc",
            "mode": "synthetic-only",
            "production_data_connected": False,
        },
        headers={"Cache-Control": "no-store"},
    )


@app.websocket("/ws")
async def websocket_probe(websocket: WebSocket) -> None:
    await websocket.accept()
    session_id = uuid.uuid4().hex
    sequence = 0
    recent_messages: deque[float] = deque()
    await websocket.send_json(
        {"type": "ready", "session_id": session_id, "mode": "synthetic-only"}
    )

    try:
        while True:
            try:
                raw_message = await asyncio.wait_for(
                    websocket.receive_text(), timeout=IDLE_TIMEOUT_SECONDS
                )
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "idle_timeout", "session_id": session_id})
                await websocket.close(code=1000, reason="idle test session complete")
                return

            if len(raw_message) > MAX_MESSAGE_CHARS:
                await websocket.send_json({"type": "error", "code": "message_too_large"})
                await websocket.close(code=1009, reason="message too large")
                return

            now = time.monotonic()
            while recent_messages and now - recent_messages[0] >= RATE_WINDOW_SECONDS:
                recent_messages.popleft()
            if len(recent_messages) >= MAX_MESSAGES_PER_WINDOW:
                await websocket.send_json({"type": "error", "code": "rate_limited"})
                await websocket.close(code=1013, reason="synthetic POC rate limit")
                return

            try:
                payload: Any = json.loads(raw_message)
            except (json.JSONDecodeError, TypeError):
                payload = None

            if (
                not isinstance(payload, dict)
                or payload.get("type") != "ping"
                or not isinstance(payload.get("id"), str)
                or not 1 <= len(payload["id"]) <= 64
            ):
                await websocket.send_json({"type": "error", "code": "invalid_message"})
                await websocket.close(code=1003, reason="unsupported test message")
                return

            recent_messages.append(now)
            sequence += 1
            await websocket.send_json(
                {
                    "type": "pong",
                    "id": payload["id"],
                    "sequence": sequence,
                    "server_time_unix_ms": int(time.time() * 1000),
                    "session_id": session_id,
                }
            )
    except WebSocketDisconnect:
        return
