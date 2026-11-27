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

let nextJsonMessageCounter = 0;
function nextJsonMessage(socket, timeoutMs = 5_000) {
  const messageIndex = ++nextJsonMessageCounter;
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
      reject(new Error(`WebSocket message #${messageIndex} closed before the expected message (code ${event.code}).`));
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
  timeout: 60_000,
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
  let pagingSocket;
  let overBudgetSocket;
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
    // Keep a persistent listener/queue: all replay frames may be sent synchronously
    // before the test reaches the next await, so one-shot listeners can lose frames.
    const raceQueue = [];
    const raceWaiters = [];
    raceSocket.addEventListener("message", (event) => {
      const message = JSON.parse(String(event.data));
      const waiter = raceWaiters.shift();
      if (waiter) waiter(message);
      else raceQueue.push(message);
    });
    const nextRaceMessage = () => raceQueue.length
      ? Promise.resolve(raceQueue.shift())
      : new Promise((resolve) => raceWaiters.push(resolve));
    const raceFirstMessagePromise = nextRaceMessage();
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
      const replayEvent = await nextRaceMessage();
      assert.equal(replayEvent.type, "market_data.ohlcv.update");
      observedSequences.push(replayEvent.sequence);
      if (replayEvent.sequence === 51) event51Digest = replayEvent.digest;
      if (replayEvent.sequence === 52) event52 = replayEvent;
    }
    const raceComplete = await nextRaceMessage();
    assert.equal(raceComplete.type, "market_data.ohlcv.replay_complete");
    assert.equal(raceComplete.count, raceStart.count);
    if (!observedSequences.includes(52)) {
      const liveEvent = await nextRaceMessage();
      assert.equal(liveEvent.type, "market_data.ohlcv.update");
      observedSequences.push(liveEvent.sequence);
      if (liveEvent.sequence === 52) event52 = liveEvent;
    }
    assert.deepEqual(observedSequences, [51, 52]);
    assert.ok(event52 && /^[0-9a-f]{64}$/.test(event52.digest));

    // ACK is now a first-class WebSocket protocol message. A cursor beyond the
    // highest event delivered on this connection is rejected before persistence.
    const aheadAckPromise = nextRaceMessage();
    raceSocket.send(JSON.stringify({
      type: "market_data.ack",
      version: 1,
      sequence: 53,
      eventDigest: event52.digest,
    }));
    const aheadAck = await aheadAckPromise;
    assert.equal(aheadAck.type, "market_data.ack_rejected");
    assert.equal(aheadAck.reason, "ack_not_delivered_or_invalid");

    const websocketAckPromise = nextRaceMessage();
    raceSocket.send(JSON.stringify({
      type: "market_data.ack",
      version: 1,
      sequence: 52,
      eventDigest: event52.digest,
    }));
    const websocketAck = await websocketAckPromise;
    assert.equal(websocketAck.type, "market_data.acknowledged", JSON.stringify(websocketAck));
    assert.equal(websocketAck.accepted, true);
    assert.equal(websocketAck.duplicate, false);
    assert.equal(websocketAck.committedCursor, "52");
    assert.equal(websocketAck.receiptVersion, 1);

    // Close the three transport consumers before isolating the manual retention
    // proof below. Their leases are required consumers too and must be released.
    const closeTestSocket = (socket, reason) => new Promise((resolve) => {
      socket.addEventListener("close", resolve, { once: true });
      socket.close(1000, reason);
    });
    await Promise.all([
      closeTestSocket(clientSocket, "initial transport complete"),
      closeTestSocket(resumeSocket, "replay transport complete"),
      closeTestSocket(raceSocket, "ACK transport complete"),
    ]);

    const primaryRegistration = await miniflare.dispatchFetch(`${BASE_URL}/__proof/register-consumer`, {
      method: "POST", headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: SERIES, consumerId: "synthetic-proof-consumer-1", generationId: "synthetic-v1",
        ownerToken: "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
      }),
    });
    assert.equal(primaryRegistration.status, 200);
    assert.equal((await primaryRegistration.json()).registered, true);

    const ackBody = {
      seriesKey: SERIES,
      consumerId: "synthetic-proof-consumer-1",
      generationId: "synthetic-v1",
      ownerToken: "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
      fenceToken: 1,
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

    // Exercise a real workerd replay that spans two SQLite pages (100 + 2 events).
    const pagingSeries = { ...CANONICAL_SERIES, seriesKey: "synthetic:PAGING:ETHUSD:1m", dataset: "PAGING", rawSymbol: "ETHUSD", instrumentId: 202 };
    for (let sequence = 51; sequence <= 152; sequence += 1) {
      const pagingEmit = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
        method: "POST",
        headers: authorizedHeaders(),
        body: JSON.stringify({
          seriesKey: pagingSeries.seriesKey,
          sequence: String(sequence),
          series: pagingSeries,
          emittedAtNs: (1_800_000_000_000_000_000n + BigInt(sequence)).toString(),
        }),
      });
      assert.equal(pagingEmit.status, 200);
      assert.equal((await pagingEmit.json()).accepted, true);
    }
    const pagingTicketResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/v1/auth/websocket-ticket`,
      { method: "POST", headers: authorizedHeaders(), body: JSON.stringify({ seriesKey: pagingSeries.seriesKey }) },
    );
    const pagingTicket = await pagingTicketResponse.json();
    const pagingUpgrade = await miniflare.dispatchFetch(
      `${BASE_URL}/ws/market-data?seriesKey=${encodeURIComponent(pagingSeries.seriesKey)}`,
      { headers: { Origin: ORIGIN, Upgrade: "websocket" } },
    );
    assert.equal(pagingUpgrade.status, 101);
    pagingSocket = pagingUpgrade.webSocket;
    pagingSocket.accept();
    const pagingAuthPromise = nextJsonMessage(pagingSocket);
    pagingSocket.send(JSON.stringify({ type: "auth", ticket: pagingTicket.ticket }));
    assert.equal((await pagingAuthPromise).type, "market_data.status");
    const pagingQueue = [];
    const pagingWaiters = [];
    pagingSocket.addEventListener("message", (event) => {
      const message = JSON.parse(String(event.data));
      const waiter = pagingWaiters.shift();
      if (waiter) waiter(message);
      else pagingQueue.push(message);
    });
    const nextPagingMessage = () => pagingQueue.length
      ? Promise.resolve(pagingQueue.shift())
      : new Promise((resolve) => pagingWaiters.push(resolve));
    const pagingStartPromise = nextPagingMessage();
    pagingSocket.send(JSON.stringify({
      type: "market_data.subscribe",
      version: 1,
      series: pagingSeries,
      cursor: "50",
    }));
    const pagingStart = await pagingStartPromise;
    assert.equal(pagingStart.type, "market_data.ohlcv.replay_started");
    assert.equal(pagingStart.count, 102);
    assert.equal(pagingStart.fromCursor, "50");
    assert.equal(pagingStart.throughCursor, "152");
    assert.equal(pagingStart.fromSequence, 50);
    assert.equal(pagingStart.throughSequence, 152);
    const pagedSequences = [];
    for (let index = 0; index < pagingStart.count; index += 1) {
      const event = await nextPagingMessage();
      assert.equal(event.type, "market_data.ohlcv.update");
      pagedSequences.push(event.sequence);
    }
    const pagingComplete = await nextPagingMessage();
    assert.equal(pagingComplete.type, "market_data.ohlcv.replay_complete");
    assert.equal(pagingComplete.count, 102);
    assert.equal(pagingComplete.cursor, "152");
    assert.deepEqual(pagedSequences, Array.from({ length: 102 }, (_, index) => index + 51));

    // A cursor requiring more than the 10-page subscribe budget must resnapshot.
    const overBudgetSeries = {
      ...CANONICAL_SERIES,
      seriesKey: "synthetic:OVERBUDGET:ETHUSD:1m",
      dataset: "OVERBUDGET",
      rawSymbol: "ETHUSD",
      instrumentId: 303,
    };
    for (let sequence = 51; sequence <= 1_051; sequence += 1) {
      const emitResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
        method: "POST",
        headers: authorizedHeaders(),
        body: JSON.stringify({
          seriesKey: overBudgetSeries.seriesKey,
          sequence: String(sequence),
          series: overBudgetSeries,
          emittedAtNs: (1_900_000_000_000_000_000n + BigInt(sequence)).toString(),
        }),
      });
      assert.equal(emitResponse.status, 200);
      assert.equal((await emitResponse.json()).accepted, true);
    }
    const overBudgetTicketResponse = await miniflare.dispatchFetch(
      `${BASE_URL}/v1/auth/websocket-ticket`,
      { method: "POST", headers: authorizedHeaders(), body: JSON.stringify({ seriesKey: overBudgetSeries.seriesKey }) },
    );
    const overBudgetTicket = await overBudgetTicketResponse.json();
    const overBudgetUpgrade = await miniflare.dispatchFetch(
      `${BASE_URL}/ws/market-data?seriesKey=${encodeURIComponent(overBudgetSeries.seriesKey)}`,
      { headers: { Origin: ORIGIN, Upgrade: "websocket" } },
    );
    assert.equal(overBudgetUpgrade.status, 101);
    overBudgetSocket = overBudgetUpgrade.webSocket;
    overBudgetSocket.accept();
    const overBudgetAuthPromise = nextJsonMessage(overBudgetSocket);
    overBudgetSocket.send(JSON.stringify({ type: "auth", ticket: overBudgetTicket.ticket }));
    assert.equal((await overBudgetAuthPromise).type, "market_data.status");
    const overBudgetResnapshotPromise = nextJsonMessage(overBudgetSocket);
    overBudgetSocket.send(JSON.stringify({
      type: "market_data.subscribe",
      version: 1,
      series: overBudgetSeries,
      cursor: "50",
    }));
    const overBudgetResnapshot = await overBudgetResnapshotPromise;
    assert.equal(overBudgetResnapshot.type, "market_data.ohlcv.resnapshot_required");
    assert.equal(overBudgetResnapshot.reason, "replay_backlog_exceeds_page_budget");
    assert.equal(overBudgetResnapshot.snapshotCursor, "1051");
    const overBudgetSnapshot = await nextJsonMessage(overBudgetSocket);
    assert.equal(overBudgetSnapshot.type, "market_data.ohlcv.snapshot");
    assert.equal(overBudgetSnapshot.cursor, "1051");
    assert.equal(overBudgetSnapshot.watermark, 1051);
    assert.equal(overBudgetSnapshot.bars.length, 50);

    // Seed the legacy KV cursor, then prove SQLite takes authority after first bootstrap.
    const legacySeries = {
      ...CANONICAL_SERIES,
      seriesKey: "synthetic:LEGACY:ETHUSD:1m",
      dataset: "LEGACY",
      rawSymbol: "ETHUSD",
      instrumentId: 404,
    };
    const legacySeedResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/seed-legacy-cursor`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({ seriesKey: legacySeries.seriesKey, sequence: 77 }),
    });
    assert.equal(legacySeedResponse.status, 200);
    assert.equal((await legacySeedResponse.json()).seeded, true);
    const legacyFirstEmit = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: legacySeries.seriesKey,
        sequence: "78",
        series: legacySeries,
        emittedAtNs: "1900000000000000078",
      }),
    });
    assert.equal(legacyFirstEmit.status, 200);
    assert.equal((await legacyFirstEmit.json()).accepted, true);

    const staleLegacyReseed = await miniflare.dispatchFetch(`${BASE_URL}/__proof/seed-legacy-cursor`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({ seriesKey: legacySeries.seriesKey, sequence: 900 }),
    });
    assert.equal(staleLegacyReseed.status, 200);
    const sqliteAuthoritativeEmit = await miniflare.dispatchFetch(`${BASE_URL}/__proof/emit`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: legacySeries.seriesKey,
        sequence: "79",
        series: legacySeries,
        emittedAtNs: "1900000000000000079",
      }),
    });
    assert.equal(sqliteAuthoritativeEmit.status, 200);
    assert.equal((await sqliteAuthoritativeEmit.json()).accepted, true);

    const emptyRegistryCompact = await miniflare.dispatchFetch(`${BASE_URL}/__proof/compact`, {
      method: "POST", headers: authorizedHeaders(),
      body: JSON.stringify({ seriesKey: legacySeries.seriesKey, throughSequence: 79 }),
    });
    assert.equal(emptyRegistryCompact.status, 409);
    assert.equal((await emptyRegistryCompact.json()).reason, "required_consumer_registry_empty");

    // Registering a required consumer without an ACK must block compaction.
    const noAckRegistration = await miniflare.dispatchFetch(`${BASE_URL}/__proof/register-consumer`, {
      method: "POST", headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: SERIES, consumerId: "synthetic-proof-consumer-no-ack", generationId: "synthetic-v1",
        ownerToken: "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
      }),
    });
    assert.equal(noAckRegistration.status, 200);
    const noAckCompactResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/compact`, {
      method: "POST", headers: authorizedHeaders(),
      body: JSON.stringify({ seriesKey: SERIES, throughSequence: 52 }),
    });
    assert.equal(noAckCompactResponse.status, 409);
    const noAckCompaction = await noAckCompactResponse.json();
    assert.equal(noAckCompaction.reason, "consumer_ack_behind");
    assert.equal(noAckCompaction.missingConsumerReceipts, 1);

    const noAckReceiptResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/ack`, {
      method: "POST", headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: SERIES, consumerId: "synthetic-proof-consumer-no-ack",
        generationId: "synthetic-v1", ownerToken: "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", fenceToken: 1,
        sequence: 52, eventDigest: event52.digest,
      }),
    });
    assert.equal(noAckReceiptResponse.status, 200);
    assert.equal((await noAckReceiptResponse.json()).accepted, true);

    // A lagging, already-registered consumer must prevent compaction past its ACK.
    const laggingRegistration = await miniflare.dispatchFetch(`${BASE_URL}/__proof/register-consumer`, {
      method: "POST", headers: authorizedHeaders(),
      body: JSON.stringify({
        seriesKey: SERIES, consumerId: "synthetic-proof-consumer-lagging", generationId: "synthetic-v1",
        ownerToken: "9999999999999999999999999999999999999999999999999999999999999999",
      }),
    });
    assert.equal(laggingRegistration.status, 200);
    const laggingAckBody = {
      seriesKey: SERIES,
      consumerId: "synthetic-proof-consumer-lagging",
      generationId: "synthetic-v1",
      ownerToken: "9999999999999999999999999999999999999999999999999999999999999999",
      fenceToken: 1,
      sequence: 51,
      eventDigest: event51Digest,
    };
    const laggingAckResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/ack`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify(laggingAckBody),
    });
    assert.equal(laggingAckResponse.status, 200);
    assert.equal((await laggingAckResponse.json()).accepted, true);

    const blockedCompactResponse = await miniflare.dispatchFetch(`${BASE_URL}/__proof/compact`, {
      method: "POST",
      headers: authorizedHeaders(),
      body: JSON.stringify({ seriesKey: SERIES, throughSequence: 52 }),
    });
    assert.equal(blockedCompactResponse.status, 409);
    const blockedCompaction = await blockedCompactResponse.json();
    assert.equal(blockedCompaction.compacted, false);
    assert.equal(blockedCompaction.reason, "consumer_ack_behind");
    assert.equal(blockedCompaction.minimumAcknowledgedSequence, 51);

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
      pagingSocket?.close(1000, "Multi-page replay integration test complete");
      overBudgetSocket?.close(1000, "Over-budget replay fallback test complete");
    } catch {
      // The runtime may already have closed the test socket during teardown.
    }
    await miniflare.dispose();
  }
});
