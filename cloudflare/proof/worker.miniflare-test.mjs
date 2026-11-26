import assert from "node:assert/strict";
import test from "node:test";
import { Miniflare } from "miniflare";
import { fileURLToPath } from "node:url";

const SERIES = "synthetic:DEMO:BTCUSD:1m";
const TOKEN = "synthetic-proof-test-token-000000000000000000000000";
const ORIGIN = "http://localhost:3000";
const BASE_URL = "https://synthetic-proof.local";
const CANONICAL_SERIES = {
  seriesKey: SERIES,
  provider: "synthetic",
  seriesType: "contract",
  dataset: "DEMO",
  publisherId: 1,
  instrumentId: 101,
  rawSymbol: "BTCUSD",
  timeframe: "1m",
  bucketPolicy: "UTC_LEGACY",
  calendarId: "",
  calendarVersion: "",
};

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
      SERIES_COORDINATOR: {
        className: "SeriesCoordinatorDO",
        useSQLite: true,
      },
    },
    bindings: {
      PROOF_MODE: "synthetic-only",
      SYNTHETIC_PROOF_TOKEN: TOKEN,
      PROOF_ALLOWED_ORIGINS: "http://localhost:3000,http://127.0.0.1:3000",
    },
    compatibilityDate: "2026-07-30",
  });

  let clientSocket;
  let resumeSocket;
  let retentionSocket;
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

    const statusPromise = nextJsonMessage(clientSocket);
    clientSocket.send(JSON.stringify({ type: "auth", ticket: ticket.ticket }));
    const status = await statusPromise;
    assert.equal(status.type, "market_data.status");
    assert.equal(status.version, 1);
    assert.equal(status.providerConnected, false);
    assert.equal(status.liveProviderEnabled, false);

    const snapshotPromise = nextJsonMessage(clientSocket);
    clientSocket.send(JSON.stringify({
      type: "market_data.subscribe",
      version: 1,
      canonicalInstrumentId: "00000000-0000-4000-8000-000000000001",
      series: {
        seriesKey: SERIES,
        provider: "synthetic",
        seriesType: "contract",
        dataset: "DEMO",
        publisherId: 1,
        instrumentId: 101,
        rawSymbol: "BTCUSD",
        timeframe: "1m",
        bucketPolicy: "UTC_LEGACY",
        calendarId: "",
        calendarVersion: "",
      },
    }));
    const snapshot = await snapshotPromise;
    assert.equal(snapshot.type, "market_data.ohlcv.snapshot");
    assert.equal(snapshot.version, 1);
    assert.equal(snapshot.highWaterCursor, "50");
    assert.equal(snapshot.watermark, 50);
    assert.equal(snapshot.cursor, "50");
    assert.equal(snapshot.bars.length, 50);
    assert.equal(snapshot.provenance.dataStatus, "synthetic_only");
    assert.equal(snapshot.provenance.providerConnected, false);

    const pongPromise = nextJsonMessage(clientSocket);
    clientSocket.send("ping");
    const pong = await pongPromise;
    assert.equal(pong.type, "market_data.pong");
    assert.equal(pong.version, 1);

    const updatePromise = nextJsonMessage(clientSocket);
    const emitResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: SERIES,
        sequence: "51",
        series: CANONICAL_SERIES,
        emittedAtNs: "1800000000000000051",
      }),
    });
    assert.equal(emitResponse.status, 200);
    const emitted = await emitResponse.json();
    assert.equal(emitted.accepted, true);
    assert.equal(emitted.duplicate, false);
    assert.equal(emitted.sequence, "51");
    assert.equal(emitted.delivered, 1);

    const update = await updatePromise;
    assert.equal(update.type, "market_data.ohlcv.update");
    assert.equal(update.sequence, 51);
    assert.equal(update.cursor, "51");
    assert.equal(update.provenance.dataStatus, "synthetic_only");
    assert.equal(update.provenance.providerConnected, false);
    assert.match(update.digest, /^[0-9a-f]{64}$/);

    const retryResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: SERIES,
        sequence: "51",
        series: CANONICAL_SERIES,
        emittedAtNs: "1800000000000000051",
      }),
    });
    assert.equal(retryResponse.status, 200);
    assert.deepEqual(await retryResponse.json(), {
      accepted: true,
      duplicate: true,
      sequence: "51",
      delivered: 0,
    });

    // A reconnect with the last durable cursor receives the persisted event,
    // not a synthetic resnapshot. This exercises replay against real workerd SQLite.
    const resumeTicketResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/v1/auth/websocket-ticket`,
      { method: "POST", headers: authorizedHeaders(), body: JSON.stringify({ seriesKey: SERIES }) },
    );
    assert.equal(resumeTicketResponse.status, 200);
    const resumeTicket = await resumeTicketResponse.json();
    const resumeResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/ws/market-data?seriesKey=${encodeURIComponent(SERIES)}`,
      { headers: { Origin: ORIGIN, Upgrade: "websocket" } },
    );
    assert.equal(resumeResponse.status, 101);
    resumeSocket = resumeResponse.webSocket;
    resumeSocket.accept();
    const resumeAuthPromise = nextJsonMessage(resumeSocket);
    resumeSocket.send(JSON.stringify({ type: "auth", ticket: resumeTicket.ticket }));
    assert.equal((await resumeAuthPromise).type, "market_data.status");
    const replayPromise = nextJsonMessage(resumeSocket);
    resumeSocket.send(JSON.stringify({
      type: "market_data.subscribe",
      version: 1,
      series: CANONICAL_SERIES,
      cursor: "50",
    }));
    const replay = await replayPromise;
    assert.equal(replay.type, "market_data.ohlcv.replay");
    assert.equal(replay.generationId, "synthetic-v1");
    assert.equal(replay.events.length, 1);
    assert.equal(replay.events[0].sequence, 51);
    assert.equal(replay.nextCursor, "51");
    assert.equal(replay.highWaterCursor, "51");
    assert.equal(replay.hasMore, false);
    assert.ok(new TextEncoder().encode(JSON.stringify(replay)).byteLength <= 65_536);

    // Retention compaction is an atomic cursor-floor advance plus event deletion.
    const compactResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/compact`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({ seriesKey: SERIES, throughSequence: 51 }),
    });
    assert.equal(compactResponse.status, 200);
    const compacted = await compactResponse.json();
    assert.equal(compacted.compacted, true);
    assert.equal(compacted.deleted, 1);
    assert.equal(compacted.retentionFloor, 51);

    const retentionTicketResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/v1/auth/websocket-ticket`,
      { method: "POST", headers: authorizedHeaders(), body: JSON.stringify({ seriesKey: SERIES }) },
    );
    const retentionTicket = await retentionTicketResponse.json();
    const retentionResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/ws/market-data?seriesKey=${encodeURIComponent(SERIES)}`,
      { headers: { Origin: ORIGIN, Upgrade: "websocket" } },
    );
    assert.equal(retentionResponse.status, 101);
    retentionSocket = retentionResponse.webSocket;
    retentionSocket.accept();
    const retentionAuthPromise = nextJsonMessage(retentionSocket);
    retentionSocket.send(JSON.stringify({ type: "auth", ticket: retentionTicket.ticket }));
    await retentionAuthPromise;
    const resnapshotPromise = nextJsonMessage(retentionSocket);
    retentionSocket.send(JSON.stringify({
      type: "market_data.subscribe",
      version: 1,
      series: CANONICAL_SERIES,
      cursor: "50",
    }));
    const resnapshotRequired = await resnapshotPromise;
    assert.equal(resnapshotRequired.type, "market_data.ohlcv.resnapshot_required");
    assert.equal(resnapshotRequired.reason, "retention_expired");
    const retainedSnapshot = await nextJsonMessage(retentionSocket);
    assert.equal(retainedSnapshot.type, "market_data.ohlcv.snapshot");
    assert.equal(retainedSnapshot.cursor, "51");

    const changedTimestampResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: SERIES,
        sequence: "51",
        series: CANONICAL_SERIES,
        emittedAtNs: "1800000000000000999",
      }),
    });
    assert.equal(changedTimestampResponse.status, 409);
    assert.deepEqual(await changedTimestampResponse.json(), { error: "sequence_conflict" });

    const gapResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: SERIES,
        sequence: "53",
        series: CANONICAL_SERIES,
        emittedAtNs: "1800000000000000053",
      }),
    });
    assert.equal(gapResponse.status, 409);
  } finally {
    try {
      clientSocket?.close(1000, "Local workerd integration test complete");
      resumeSocket?.close(1000, "Replay integration test complete");
      retentionSocket?.close(1000, "Retention integration test complete");
    } catch {
      // The runtime may already have closed the test socket during teardown.
    }
    await miniflare.dispose();
  }
});
