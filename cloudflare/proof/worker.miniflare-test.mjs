import assert from "node:assert/strict";
import test from "node:test";
import { Miniflare } from "miniflare";
import { fileURLToPath } from "node:url";

const SERIES = "synthetic:DEMO:BTCUSD:1m";
const TOKEN = "synthetic-proof-test-token-000000000000000000000000";
const ORIGIN = "http://localhost:3000";
const BASE_URL = "https://synthetic-proof.local";

function nextJsonMessage(socket, timeoutMs = 5_000) {
  return new Promise((resolve, reject) => {
    const cleanup = () => {
      clearTimeout(timer);
      socket.removeEventListener("message", onMessage);
      socket.removeEventListener("close", onClose);
      socket.removeEventListener("error", onError);
    };
    const timer = setTimeout(() => {
      cleanup();
      reject(new Error("Timed out waiting for a message from the local workerd WebSocket."));
    }, timeoutMs);
    const onMessage = (event) => {
      cleanup();
      try {
        resolve(JSON.parse(String(event.data)));
      } catch (error) {
        reject(error);
      }
    };
    const onClose = (event) => {
      cleanup();
      reject(new Error(`WebSocket closed before the expected message (code ${event.code}).`));
    };
    const onError = () => {
      cleanup();
      reject(new Error("Local workerd WebSocket emitted an error before the expected message."));
    };
    socket.addEventListener("message", onMessage, { once: true });
    socket.addEventListener("close", onClose, { once: true });
    socket.addEventListener("error", onError, { once: true });
  });
}

function authorizedHeaders() {
  return {
    Origin: ORIGIN,
    Authorization: `Bearer ${TOKEN}`,
    "Content-Type": "application/json",
  };
}

test("synthetic Worker executes real workerd WebSocket, Durable Object storage and fan-out", {
  timeout: 20_000,
}, async () => {
  const miniflare = new Miniflare({
    modules: true,
    scriptPath: fileURLToPath(new URL("./worker.mjs", import.meta.url)),
    durableObjects: {
      SERIES_COORDINATOR: "SeriesCoordinatorDO",
    },
    bindings: {
      PROOF_MODE: "synthetic-only",
      SYNTHETIC_PROOF_TOKEN: TOKEN,
      PROOF_ALLOWED_ORIGINS: "http://localhost:3000,http://127.0.0.1:3000",
    },
    compatibilityDate: "2026-07-30",
  });

  let clientSocket;
  try {
    await miniflare.ready;

    const healthResponse = await miniflare.dispatchFetch(`${BASE_URL}/health`, {
      headers: { Origin: ORIGIN },
    });
    const health = await healthResponse.json();
    assert.equal(healthResponse.status, 200);
    assert.equal(health.mode, "synthetic-only");
    assert.equal(health.provider, "none");
    assert.equal(health.marketData, "synthetic_only_not_market_data");

    const ticketResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/v1/auth/websocket-ticket`,
      {
        method: "POST",
        headers: authorizedHeaders(),
        body: JSON.stringify({ seriesKey: SERIES }),
      },
    );
    assert.equal(ticketResponse.status, 200);
    const ticket = await ticketResponse.json();
    assert.match(ticket.ticket, /^[0-9a-f]{64}$/);
    assert.equal(ticket.purpose, "market-data");
    assert.equal(ticket.seriesKey, SERIES);

    const websocketResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/ws/market-data?seriesKey=${encodeURIComponent(SERIES)}`,
      { headers: { Origin: ORIGIN, Upgrade: "websocket" } },
    );
    assert.equal(websocketResponse.status, 101);
    assert.ok(websocketResponse.webSocket, "Worker must return the client side of a real WebSocketPair.");
    clientSocket = websocketResponse.webSocket;
    clientSocket.accept();

    const snapshotPromise = nextJsonMessage(clientSocket);
    clientSocket.send(JSON.stringify({ type: "auth", ticket: ticket.ticket }));
    const snapshot = await snapshotPromise;
    assert.equal(snapshot.type, "market_data.snapshot");
    assert.equal(snapshot.version, 1);
    assert.equal(snapshot.watermarkCursor, "50");
    assert.equal(snapshot.bars.length, 50);
    assert.equal(snapshot.dataSource, "synthetic_only_not_market_data");

    const pongPromise = nextJsonMessage(clientSocket);
    clientSocket.send(JSON.stringify({ type: "ping" }));
    const pong = await pongPromise;
    assert.equal(pong.type, "pong");
    assert.equal(pong.version, 1);

    const updatePromise = nextJsonMessage(clientSocket);
    const emitResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({ seriesKey: SERIES, sequence: "51" }),
    });
    assert.equal(emitResponse.status, 200);
    const emitted = await emitResponse.json();
    assert.equal(emitted.accepted, true);
    assert.equal(emitted.sequence, "51");
    assert.equal(emitted.delivered, 1);

    const update = await updatePromise;
    assert.equal(update.type, "market_data.update");
    assert.equal(update.sequence, "51");
    assert.equal(update.dataSource, "synthetic_only_not_market_data");

    const gapResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({ seriesKey: SERIES, sequence: "53" }),
    });
    assert.equal(gapResponse.status, 409);
  } finally {
    try {
      clientSocket?.close(1000, "Local workerd integration test complete");
    } catch {
      // The runtime may already have closed the test socket during teardown.
    }
    await miniflare.dispose();
  }
});
