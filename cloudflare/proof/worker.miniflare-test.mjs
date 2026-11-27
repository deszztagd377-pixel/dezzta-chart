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
  let raceSocket;
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
    const replayStartPromise = nextJsonMessage(resumeSocket);
    resumeSocket.send(JSON.stringify({
      type: "market_data.subscribe",
      version: 1,
      series: CANONICAL_SERIES,
      cursor: "50",
    }));
    const replayStart = await replayStartPromise;
    assert.equal(replayStart.type, "market_data.ohlcv.replay_started");
    assert.equal(replayStart.count, 1);
    assert.equal(replayStart.fromCursor, "50");
    assert.equal(replayStart.throughCursor, "51");
    assert.equal(replayStart.fromSequence, 50);
    assert.equal(replayStart.throughSequence, 51);
    const replayEvent = await nextJsonMessage(resumeSocket);
    assert.equal(replayEvent.type, "market_data.ohlcv.update");
    assert.equal(replayEvent.sequence, 51);
    assert.equal(replayEvent.cursor, "51");
    const replayComplete = await nextJsonMessage(resumeSocket);
    assert.equal(replayComplete.type, "market_data.ohlcv.replay_complete");
    assert.equal(replayComplete.count, 1);
    assert.equal(replayComplete.cursor, "51");
    assert.equal(replayComplete.throughSequence, 51);

    // Race a reconnecting cursor-50 subscriber against commit/fan-out of sequence 52.
    // The only valid outcomes are replay [51,52], or replay [51] followed by live 52.
    const raceTicketResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/v1/auth/websocket-ticket`,
      { method: "POST", headers: authorizedHeaders(), body: JSON.stringify({ seriesKey: SERIES }) },
    );
    const raceTicket = await raceTicketResponse.json();
    const raceResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/ws/market-data?seriesKey=${encodeURIComponent(SERIES)}`,
      { headers: { Origin: ORIGIN, Upgrade: "websocket" } },
    );
    assert.equal(raceResponse.status, 101);
    raceSocket = raceResponse.webSocket;
    raceSocket.accept();
    const raceAuthPromise = nextJsonMessage(raceSocket);
    raceSocket.send(JSON.stringify({ type: "auth", ticket: raceTicket.ticket }));
    assert.equal((await raceAuthPromise).type, "market_data.status");
    const raceFirstMessagePromise = nextJsonMessage(raceSocket);
    raceSocket.send(JSON.stringify({
      type: "market_data.subscribe",
      version: 1,
      series: CANONICAL_SERIES,
      cursor: "50",
    }));
    const raceEmitPromise = miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: SERIES,
        sequence: "52",
        series: CANONICAL_SERIES,
        emittedAtNs: "1800000000000000052",
      }),
    });
    const [raceStart, raceEmitResponse] = await Promise.all([
      raceFirstMessagePromise,
      raceEmitPromise,
    ]);
    assert.equal(raceEmitResponse.status, 200);
    assert.equal((await raceEmitResponse.json()).accepted, true);
    assert.equal(raceStart.type, "market_data.ohlcv.replay_started");
    assert.ok(raceStart.count === 1 || raceStart.count === 2);
    assert.equal(raceStart.fromSequence, 50);
    const observedSequences = [];
    let event52 = null;
    let event51Digest = null;
    for (let index = 0; index < raceStart.count; index += 1) {
      const replayEvent = await nextJsonMessage(raceSocket);
      assert.equal(replayEvent.type, "market_data.ohlcv.update");
      observedSequences.push(replayEvent.sequence);
      if (replayEvent.sequence === 51) event51Digest = replayEvent.digest;
      if (replayEvent.sequence === 52) event52 = replayEvent;
    }
    const raceComplete = await nextJsonMessage(raceSocket);
    assert.equal(raceComplete.type, "market_data.ohlcv.replay_complete");
    assert.equal(raceComplete.count, raceStart.count);
    if (!observedSequences.includes(52)) {
      const liveEvent = await nextJsonMessage(raceSocket);
      assert.equal(liveEvent.type, "market_data.ohlcv.update");
      observedSequences.push(liveEvent.sequence);
      if (liveEvent.sequence === 52) event52 = liveEvent;
    }
    assert.deepEqual(observedSequences, [51, 52]);
    assert.ok(event52 && /^[0-9a-f]{64}$/.test(event52.digest));

    const ackBody = {
      seriesKey: SERIES,
      consumerId: "synthetic-proof-consumer-1",
      generationId: "synthetic-v1",
      sequence: 52,
      eventDigest: event52.digest,
    };
    const ackResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/ack`, {
      method: "POST", headers: authorizedHeaders(), body: JSON.stringify(ackBody),
    });
    assert.equal(ackResponse.status, 200);
    const ack = await ackResponse.json();
    assert.equal(ack.accepted, true);
    assert.equal(ack.duplicate, false);
    assert.equal(ack.committedCursor, "52");
    assert.equal(ack.receiptVersion, 1);

    const duplicateAckResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/ack`, {
      method: "POST", headers: authorizedHeaders(), body: JSON.stringify(ackBody),
    });
    assert.equal(duplicateAckResponse.status, 200);
    const duplicateAck = await duplicateAckResponse.json();
    assert.equal(duplicateAck.duplicate, true);
    assert.equal(duplicateAck.receiptVersion, 1);

    const regressedAckResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/ack`, {
      method: "POST", headers: authorizedHeaders(),
      body: JSON.stringify({ ...ackBody, sequence: 51, eventDigest: event51Digest }),
    });
    assert.equal(regressedAckResponse.status, 409);
    assert.equal((await regressedAckResponse.json()).reason, "ack_regression");

    const badDigestAckResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/ack`, {
      method: "POST", headers: authorizedHeaders(),
      body: JSON.stringify({ ...ackBody, eventDigest: "0".repeat(64) }),
    });
    assert.equal(badDigestAckResponse.status, 409);
    assert.equal((await badDigestAckResponse.json()).reason, "digest_mismatch");

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
    assert.equal(retainedSnapshot.cursor, "52");

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
        sequence: "54",
        series: CANONICAL_SERIES,
        emittedAtNs: "1800000000000000054",
      }),
    });
    assert.equal(gapResponse.status, 409);
  } finally {
    try {
      clientSocket?.close(1000, "Local workerd integration test complete");
      resumeSocket?.close(1000, "Replay integration test complete");
      retentionSocket?.close(1000, "Retention integration test complete");
      raceSocket?.close(1000, "Replay/live race integration test complete");
    } catch {
      // The runtime may already have closed the test socket during teardown.
    }
    await miniflare.dispose();
  }
});
