import test from "node:test";
import assert from "node:assert/strict";
import {
  createProtocolError,
  createSyntheticCanonicalBar,
  createSyntheticSnapshotEnvelope,
  createSyntheticUpdateEnvelope,
  validateSyntheticCanonicalSeries,
} from "./market-data-contract.mjs";
import worker, {
  acceptNextSequence,
  consumeTicket,
  createSyntheticBar,
  createSyntheticBars,
  isValidSyntheticSeriesKey,
  issueTicket,
  initializeSequenceWatermark,
  parseSequence,
  proofLimits,
  SeriesCoordinatorDO,
} from "./worker.mjs";

const SERIES = "synthetic:DEMO:BTCUSD:1m";
const TOKEN = "synthetic-proof-test-token-000000000000000000000000";

class MemoryStorage {
  constructor() {
    this.values = new Map();
    this.tail = Promise.resolve();
    this.alarmAt = null;
  }
  async setAlarm(timestamp) { this.alarmAt = timestamp; }
  async getAlarm() { return this.alarmAt; }
  async deleteAlarm() { this.alarmAt = null; }
  async get(key) { return this.values.get(key); }
  async put(key, value) { this.values.set(key, structuredClone(value)); }
  async delete(key) { return this.values.delete(key); }
  async list({ prefix = "", limit = 1000 } = {}) {
    return new Map([...this.values.entries()].filter(([key]) => key.startsWith(prefix)).slice(0, limit));
  }
  async transaction(callback) {
    let release;
    const previous = this.tail;
    this.tail = new Promise((resolve) => { release = resolve; });
    await previous;
    try {
      return await callback(this);
    } finally {
      release();
    }
  }
}

class MemorySocket {
  constructor(attachment) {
    this.attachment = structuredClone(attachment);
    this.sent = [];
    this.closed = [];
  }
  deserializeAttachment() { return structuredClone(this.attachment); }
  serializeAttachment(attachment) { this.attachment = structuredClone(attachment); }
  send(message) { this.sent.push(JSON.parse(message)); }
  close(code, reason) { this.closed.push({ code, reason }); }
}

function request(path, { method = "GET", token, body, origin = "http://localhost:3000" } = {}) {
  const headers = new Headers();
  if (origin) headers.set("Origin", origin);
  if (token) headers.set("Authorization", "Bearer " + token);
  if (body !== undefined) headers.set("Content-Type", "application/json");
  return new Request("https://synthetic-proof.local" + path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

function makeEnv(overrides = {}) {
  return {
    PROOF_MODE: "synthetic-only",
    SYNTHETIC_PROOF_TOKEN: TOKEN,
    PROOF_ALLOWED_ORIGINS: "http://localhost:3000,http://127.0.0.1:3000",
    SERIES_COORDINATOR: {
      idFromName: (name) => name,
      get: () => ({
        fetch: async (input) => {
          const req = input instanceof Request ? input : new Request(input);
          if (req.url.includes("/internal/ticket")) {
            return new Response(JSON.stringify({ ticket: "a".repeat(64), purpose: "market-data" }), {
              headers: { "Content-Type": "application/json" },
            });
          }
          if (req.url.includes("/internal/snapshot")) {
            const body = await req.json();
            const identity = body.series;
            const asOfNs = "1800000000000000000";
            const bars = Array.from({ length: 50 }, (_, index) =>
              createSyntheticCanonicalBar(identity, index + 1, asOfNs)
            );
            const snapshot = await createSyntheticSnapshotEnvelope(identity, bars, 50);
            return new Response(JSON.stringify({
              ...snapshot,
              streamId: "synthetic:" + identity.seriesKey,
              watermark: 50,
              cursor: "50",
            }), { headers: { "Content-Type": "application/json" } });
          }
          return new Response(JSON.stringify({ accepted: true, sequence: "51", delivered: 2 }), {
            headers: { "Content-Type": "application/json" },
          });
        },
      }),
    },
    ...overrides,
  };
}

test("synthetic series identity is canonical and bounded", () => {
  assert.equal(isValidSyntheticSeriesKey(SERIES), true);
  assert.equal(isValidSyntheticSeriesKey("BTCUSD"), false);
  assert.equal(isValidSyntheticSeriesKey("synthetic:demo:BTCUSD:1m"), false);
  assert.equal(isValidSyntheticSeriesKey("synthetic:DEMO:BTCUSD:1d"), false);
  assert.equal(isValidSyntheticSeriesKey("synthetic:DEMO:BTCUSD:1m/../../health"), false);
});

test("sequence parser rejects signs, leading whitespace, decimals and unsafe bounds", () => {
  assert.equal(parseSequence("51", { minimum: 51 }), 51);
  for (const invalid of ["", "-1", "+51", " 51", "51.0", "1e2", "00000000001", 51, null]) {
    assert.equal(parseSequence(invalid), null);
  }
  assert.equal(parseSequence("50", { minimum: 51 }), null);
});

test("synthetic OHLCV bars are deterministic, coherent, and use decimal strings", () => {
  const first = createSyntheticBar(SERIES, 1);
  const repeated = createSyntheticBar(SERIES, 1);
  assert.deepEqual(first, repeated);
  assert.equal(typeof first.timestampNs, "string");
  assert.equal(typeof first.open, "string");
  assert.equal(typeof first.volume, "string");
  assert.ok(BigInt(first.timestampNs) > 0n);

  const open = Number(first.open);
  const high = Number(first.high);
  const low = Number(first.low);
  const close = Number(first.close);
  assert.ok(high >= Math.max(open, close));
  assert.ok(low <= Math.min(open, close));
  assert.ok(Number(first.volume) > 0);
});

test("synthetic snapshot is bounded to 50 bars and has monotonic cursors", () => {
  const bars = createSyntheticBars(SERIES, 50);
  assert.equal(bars.length, 50);
  assert.deepEqual(bars.map((bar) => bar.sequence), Array.from({ length: 50 }, (_, i) => String(i + 1)));
  assert.throws(() => createSyntheticBars(SERIES, 51), RangeError);
  const latestBars = createSyntheticBars(SERIES, 50, 51);
  assert.equal(latestBars[0].sequence, "2");
  assert.equal(latestBars.at(-1).sequence, "51");
  assert.equal(proofLimits.snapshotBars, 50);
  assert.equal(proofLimits.ticketTtlMs, 90_000);
  assert.equal(proofLimits.unauthenticatedSocketTtlMs, 15_000);
  assert.equal(proofLimits.maxUnauthenticatedConnectionsPerSeries, 8);
});

test("ticket is series-bound, purpose-bound, expires, and is single-use under concurrency", async () => {
  const storage = new MemoryStorage();
  await initializeSequenceWatermark(storage, SERIES);
  const now = 1_800_000_000_000;
  const issued = await issueTicket(storage, SERIES, "synthetic-proof-subject", now);
  assert.equal(issued.expiresAt, now + 90_000);

  const [first, second] = await Promise.all([
    consumeTicket(storage, issued.ticket, SERIES, now + 1),
    consumeTicket(storage, issued.ticket, SERIES, now + 1),
  ]);
  assert.equal([first, second].filter(Boolean).length, 1);
  assert.equal(await consumeTicket(storage, issued.ticket, SERIES, now + 2), null);
});

test("pending ticket capacity is enforced atomically under concurrent issuance", async () => {
  const storage = new MemoryStorage();
  const now = 1_800_000_000_000;
  const attempts = Array.from(
    { length: proofLimits.maxPendingTickets + 8 },
    () => issueTicket(storage, SERIES, "synthetic-proof-subject", now),
  );
  const results = await Promise.allSettled(attempts);
  const fulfilled = results.filter((result) => result.status === "fulfilled");
  const rejected = results.filter((result) => result.status === "rejected");
  assert.equal(fulfilled.length, proofLimits.maxPendingTickets);
  assert.equal(rejected.length, 8);
  assert.equal((await storage.list({ prefix: "ticket:", limit: 300 })).size, proofLimits.maxPendingTickets);
});

test("ticket rejects a different series and expired tickets are consumed", async () => {
  const storage = new MemoryStorage();
  await initializeSequenceWatermark(storage, SERIES);
  const now = 1_800_000_000_000;
  const issued = await issueTicket(storage, SERIES, "synthetic-proof-subject", now);
  assert.equal(await consumeTicket(storage, issued.ticket, "synthetic:DEMO:ETHUSD:1m", now + 1), null);
  assert.ok(await consumeTicket(storage, issued.ticket, SERIES, now + 1));

  const expired = await issueTicket(storage, SERIES, "synthetic-proof-subject", now);
  assert.equal(await consumeTicket(storage, expired.ticket, SERIES, now + 90_000), null);
});

test("health is explicitly synthetic-only and does not claim a provider connection", async () => {
  const response = await worker.fetch(request("/health", { token: undefined }), makeEnv());
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(payload.mode, "synthetic-only");
  assert.equal(payload.provider, "none");
  assert.equal(payload.marketData, "synthetic_only_not_market_data");
});

test("proof endpoints fail closed without the local proof token", async () => {
  const response = await worker.fetch(request("/v1/market-data/status"), makeEnv());
  assert.equal(response.status, 401);
  assert.equal((await response.json()).error, "synthetic_proof_auth_required");
});

test("proof mode disabled fails closed before serving any endpoint", async () => {
  const response = await worker.fetch(request("/health"), makeEnv({ PROOF_MODE: "production" }));
  assert.equal(response.status, 503);
  assert.equal((await response.json()).error, "synthetic_proof_disabled");
});

test("unexpected browser Origin is rejected", async () => {
  const response = await worker.fetch(
    request("/v1/market-data/status", { token: TOKEN, origin: "https://attacker.invalid" }),
    makeEnv(),
  );
  assert.equal(response.status, 403);
});

test("market status states that no live provider is connected", async () => {
  const response = await worker.fetch(
    request("/v1/market-data/status", { token: TOKEN }),
    makeEnv(),
  );
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(payload.providerConnected, false);
  assert.equal(payload.liveProviderEnabled, false);
  assert.equal(payload.dataSource, "synthetic_only_not_market_data");
});

test("snapshot endpoint returns exactly 50 synthetic bars", async () => {
  const response = await worker.fetch(
    request("/v1/ohlcv?seriesKey=" + encodeURIComponent(SERIES), { token: TOKEN }),
    makeEnv(),
  );
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(payload.type, "market_data.ohlcv.snapshot");
  assert.equal(payload.version, 1);
  assert.equal(payload.bars.length, 50);
  assert.equal(payload.highWaterCursor, "50");
  assert.equal(payload.retentionFloorCursor, "1");
  assert.equal(payload.provenance.mode, "synthetic");
  assert.equal(payload.provenance.dataStatus, "synthetic_only");
  assert.equal(payload.provenance.providerConnected, false);
  assert.equal(payload.bars[0].provider, "synthetic");
});

test("streaming JSON reader cancels an oversized body without buffering the remainder", async () => {
  let cancelled = false;
  let pulls = 0;
  const body = new ReadableStream({
    pull(controller) {
      pulls += 1;
      controller.enqueue(new Uint8Array(2_049));
    },
    cancel() {
      cancelled = true;
    },
  });
  const oversized = new Request("https://synthetic-proof.local/v1/auth/websocket-ticket", {
    method: "POST",
    headers: {
      Origin: "http://localhost:3000",
      Authorization: "Bearer " + TOKEN,
      "Content-Type": "application/json",
    },
    body,
    duplex: "half",
  });
  const response = await worker.fetch(oversized, makeEnv());
  assert.equal(response.status, 400);
  assert.equal(cancelled, true);
  assert.equal(pulls, 1);
});

test("declared oversized JSON bodies are rejected before reading", async () => {
  const oversized = new Request("https://synthetic-proof.local/v1/auth/websocket-ticket", {
    method: "POST",
    headers: {
      Origin: "http://localhost:3000",
      Authorization: "Bearer " + TOKEN,
      "Content-Type": "application/json",
      "Content-Length": "2049",
    },
    body: "{}",
  });
  const response = await worker.fetch(oversized, makeEnv());
  assert.equal(response.status, 400);
});

test("invalid UTF-8 JSON bodies fail closed", async () => {
  const body = new ReadableStream({
    start(controller) {
      controller.enqueue(new Uint8Array([0xff, 0xfe, 0x7b, 0x7d]));
      controller.close();
    },
  });
  const invalidUtf8 = new Request("https://synthetic-proof.local/v1/auth/websocket-ticket", {
    method: "POST",
    headers: {
      Origin: "http://localhost:3000",
      Authorization: "Bearer " + TOKEN,
      "Content-Type": "application/json",
    },
    body,
    duplex: "half",
  });
  const response = await worker.fetch(invalidUtf8, makeEnv());
  assert.equal(response.status, 400);
});

test("Durable Object rejects excess unauthenticated sockets before accepting another", async () => {
  const pending = Array.from({ length: proofLimits.maxUnauthenticatedConnectionsPerSeries }, () => (
    new MemorySocket({
      authorized: false,
      seriesKey: SERIES,
      subject: null,
      connectedAt: Date.now(),
    })
  ));
  const coordinator = new SeriesCoordinatorDO({
    storage: new MemoryStorage(),
    getWebSockets: () => pending,
  }, {});
  const response = await coordinator.fetch({
    url: "https://series.internal/internal/connect?seriesKey=" + encodeURIComponent(SERIES),
    method: "GET",
    headers: new Headers({ Upgrade: "websocket" }),
  });
  assert.equal(response.status, 429);
  assert.equal(await response.text(), "Authentication capacity reached");
  assert.equal(pending.length, proofLimits.maxUnauthenticatedConnectionsPerSeries);
});

test("ticket endpoint validates series before calling the coordinator", async () => {
  const response = await worker.fetch(
    request("/v1/auth/websocket-ticket", {
      method: "POST",
      token: TOKEN,
      body: { seriesKey: "BTCUSD" },
    }),
    makeEnv(),
  );
  assert.equal(response.status, 400);
  assert.equal((await response.json()).error, "invalid_series");
});

test("series sequence gate rejects gaps, duplicates, and accepts only the next cursor", async () => {
  const storage = new MemoryStorage();
  await storage.put("sequence:" + SERIES, 50);
  assert.equal(await acceptNextSequence(storage, SERIES, 52), false);
  assert.equal(await acceptNextSequence(storage, SERIES, 51), true);
  assert.equal(await acceptNextSequence(storage, SERIES, 51), false);
  assert.equal(await acceptNextSequence(storage, SERIES, 52), true);
  assert.equal(await acceptNextSequence(storage, SERIES, 1_000_000_001), false);
  assert.equal(await acceptNextSequence(storage, SERIES, Number.MAX_SAFE_INTEGER), false);
  assert.equal(await storage.get("sequence:" + SERIES), 52);

  const corrupt = new MemoryStorage();
  await corrupt.put("sequence:" + SERIES, "52");
  assert.equal(await acceptNextSequence(corrupt, SERIES, 53), false);
  await assert.rejects(initializeSequenceWatermark(corrupt, SERIES), /watermark is invalid/);
});

test("snapshot watermark initialization cannot rewind a concurrent first update", async () => {
  const initializeFirst = new MemoryStorage();
  const [watermark, accepted] = await Promise.all([
    initializeSequenceWatermark(initializeFirst, SERIES),
    acceptNextSequence(initializeFirst, SERIES, 51),
  ]);
  assert.equal(watermark, 50);
  assert.equal(accepted, true);
  assert.equal(await initializeFirst.get("sequence:" + SERIES), 51);

  const updateFirst = new MemoryStorage();
  const [acceptedBeforeInit, existingWatermark] = await Promise.all([
    acceptNextSequence(updateFirst, SERIES, 51),
    initializeSequenceWatermark(updateFirst, SERIES),
  ]);
  assert.equal(acceptedBeforeInit, true);
  assert.equal(existingWatermark, 51);
  assert.equal(await updateFirst.get("sequence:" + SERIES), 51);
  await assert.rejects(
    initializeSequenceWatermark(updateFirst, "BTCUSD"),
    TypeError,
  );
});

test("Durable Object consumes one-time ticket and sends an aligned synthetic snapshot", async () => {
  const storage = new MemoryStorage();
  await initializeSequenceWatermark(storage, SERIES);
  const issued = await issueTicket(storage, SERIES, "synthetic-proof-subject");
  const socket = new MemorySocket({
    authorized: false,
    seriesKey: SERIES,
    subject: null,
    connectedAt: Date.now(),
  });
  const ctx = { storage, getWebSockets: () => [socket] };
  const coordinator = new SeriesCoordinatorDO(ctx, {});

  await coordinator.webSocketMessage(socket, JSON.stringify({ type: "auth", ticket: issued.ticket }));
  assert.equal(socket.closed.length, 0);
  assert.equal(socket.attachment.authorized, true);
  assert.equal(socket.attachment.snapshotWatermark, 50);
  assert.equal(socket.sent.length, 1);
  assert.equal(socket.sent[0].type, "market_data.status");
  assert.equal(socket.sent[0].providerConnected, false);
  const identity = {
    seriesKey: SERIES, provider: "synthetic", seriesType: "contract",
    dataset: "DEMO", publisherId: 1, instrumentId: 101,
    rawSymbol: "BTCUSD", timeframe: "1m", bucketPolicy: "UTC_LEGACY",
    calendarId: "", calendarVersion: "",
  };
  await coordinator.webSocketMessage(socket, JSON.stringify({
    type: "market_data.subscribe", version: 1, series: identity,
  }));
  assert.equal(socket.sent[1].type, "market_data.ohlcv.snapshot");
  assert.equal(socket.sent[1].highWaterCursor, "50");
  assert.equal(socket.sent[1].bars.length, 50);
  assert.equal(socket.attachment.subscribed, true);

  const replaySocket = new MemorySocket({
    authorized: false,
    seriesKey: SERIES,
    subject: null,
    connectedAt: Date.now(),
  });
  await coordinator.webSocketMessage(replaySocket, JSON.stringify({ type: "auth", ticket: issued.ticket }));
  assert.equal(replaySocket.closed[0].code, 4401);
});

test("Durable Object synthetic fan-out is exact-series only and sequence-contiguous", async () => {
  const otherSeries = "synthetic:DEMO:ETHUSD:1m";
  const storage = new MemoryStorage();
  await storage.put("sequence:" + SERIES, 50);
  const sameA = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  const sameB = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  const other = new MemorySocket({
    authorized: true, seriesKey: otherSeries, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  const sockets = [sameA, sameB, other];
  const coordinator = new SeriesCoordinatorDO({ storage, getWebSockets: () => sockets }, {});
  const response = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seriesKey: SERIES, sequence: "51" }),
  }));
  assert.equal(response.status, 200);
  assert.equal((await response.json()).delivered, 2);
  assert.equal(sameA.sent[0].sequence, "51");
  assert.equal(sameB.sent[0].sequence, "51");
  assert.equal(other.sent.length, 0);

  const gap = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seriesKey: SERIES, sequence: "53" }),
  }));
  assert.equal(gap.status, 409);
});

test("constructor tolerates an already-closed malformed restored socket", () => {
  const malformed = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "invalid-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  malformed.close = () => { throw new Error("socket already closed"); };
  const valid = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  assert.doesNotThrow(() => new SeriesCoordinatorDO({
    storage: new MemoryStorage(),
    getWebSockets: () => [malformed, valid],
  }, {}));
  assert.equal(valid.closed.length, 0);
});

test("synthetic fan-out rejects malformed authorization attachments", async () => {
  const storage = new MemoryStorage();
  await storage.put("sequence:" + SERIES, 50);
  const valid = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  const malformed = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "invalid-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  const coordinator = new SeriesCoordinatorDO({
    storage,
    getWebSockets: () => [valid, malformed],
  }, {});
  const response = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seriesKey: SERIES, sequence: "51" }),
  }));
  assert.equal(response.status, 200);
  assert.equal((await response.json()).delivered, 1);
  assert.equal(valid.sent.length, 1);
  assert.equal(malformed.sent.length, 0);
  assert.equal(malformed.closed[0].code, 4401);
});

test("unauthenticated socket alarm schedules the earliest deadline and expires only overdue sockets", async () => {
  const now = Date.now();
  const storage = new MemoryStorage();
  const expired = new MemorySocket({
    authorized: false, seriesKey: SERIES, subject: null, connectedAt: now - 20_000,
  });
  const pending = new MemorySocket({
    authorized: false, seriesKey: SERIES, subject: null, connectedAt: now - 5_000,
  });
  const authorized = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: now - 30_000, snapshotWatermark: 50,
  });
  const sockets = [expired, pending, authorized];
  const coordinator = new SeriesCoordinatorDO({ storage, getWebSockets: () => sockets }, {});

  await coordinator.scheduleUnauthenticatedSocketAlarm();
  assert.equal(storage.alarmAt, expired.attachment.connectedAt + 15_000);

  await coordinator.alarm();
  assert.equal(expired.closed[0].code, 4408);
  assert.equal(pending.closed.length, 0);
  assert.equal(authorized.closed.length, 0);
  assert.equal(storage.alarmAt, pending.attachment.connectedAt + 15_000);

  pending.attachment.connectedAt = now - 20_000;
  await coordinator.alarm();
  assert.equal(pending.closed[0].code, 4408);
  assert.equal(storage.alarmAt, null);
});

test("authorized sockets do not retain an unauthenticated-session alarm", async () => {
  const storage = new MemoryStorage();
  const socket = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now() - 60_000, snapshotWatermark: 50,
  });
  const coordinator = new SeriesCoordinatorDO({ storage, getWebSockets: () => [socket] }, {});
  await coordinator.scheduleUnauthenticatedSocketAlarm();
  assert.equal(storage.alarmAt, null);
});

test("authentication after the connection deadline is rejected without consuming its ticket", async () => {
  const storage = new MemoryStorage();
  await initializeSequenceWatermark(storage, SERIES);
  const issued = await issueTicket(storage, SERIES, "synthetic-proof-subject");
  const socket = new MemorySocket({
    authorized: false, seriesKey: SERIES, subject: null,
    connectedAt: Date.now() - 20_000,
  });
  const coordinator = new SeriesCoordinatorDO({ storage, getWebSockets: () => [socket] }, {});
  await coordinator.webSocketMessage(socket, JSON.stringify({ type: "auth", ticket: issued.ticket }));
  assert.equal(socket.closed[0].code, 4408);
  assert.ok(await consumeTicket(storage, issued.ticket, SERIES));
});

test("Durable Object closes malformed serialized attachment state during restoration", async () => {
  const invalidSeries = new MemorySocket({
    authorized: false, seriesKey: "BTCUSD", subject: null, connectedAt: Date.now(),
  });
  const invalidSubject = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "wrong-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  const unreadable = new MemorySocket({
    authorized: false, seriesKey: SERIES, subject: null, connectedAt: Date.now(),
  });
  unreadable.deserializeAttachment = () => { throw new Error("corrupt attachment"); };
  const valid = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  new SeriesCoordinatorDO({
    storage: new MemoryStorage(),
    getWebSockets: () => [invalidSeries, invalidSubject, unreadable, valid],
  }, {});
  assert.equal(invalidSeries.closed[0].code, 4401);
  assert.equal(invalidSubject.closed[0].code, 4401);
  assert.equal(unreadable.closed[0].code, 4401);
  assert.equal(valid.closed.length, 0);

  const messageUnreadable = new MemorySocket({
    authorized: false, seriesKey: SERIES, subject: null, connectedAt: Date.now(),
  });
  messageUnreadable.deserializeAttachment = () => { throw new Error("corrupt attachment"); };
  const coordinator = new SeriesCoordinatorDO({
    storage: new MemoryStorage(),
    getWebSockets: () => [],
  }, {});
  await coordinator.webSocketMessage(messageUnreadable, JSON.stringify({ type: "auth", ticket: "x" }));
  assert.equal(messageUnreadable.closed[0].code, 4401);
});

test("health response includes local CORS only for the allow-listed origin", async () => {
  const response = await worker.fetch(request("/health"), makeEnv());
  assert.equal(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3000");
});

test("fan-out isolates a failed socket send and counts only successful deliveries", async () => {
  const storage = new MemoryStorage();
  await storage.put("sequence:" + SERIES, 50);
  const failing = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  failing.send = () => { throw new Error("simulated slow/closed consumer"); };
  const healthy = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  const coordinator = new SeriesCoordinatorDO({
    storage,
    getWebSockets: () => [failing, healthy],
  }, {});

  const response = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seriesKey: SERIES, sequence: "51" }),
  }));

  assert.equal(response.status, 200);
  assert.equal((await response.json()).delivered, 1);
  assert.deepEqual(failing.closed, [{
    code: 1011,
    reason: "Synthetic fan-out failed",
  }]);
  assert.equal(healthy.sent.length, 1);
  assert.equal(healthy.sent[0].sequence, "51");
});


test("snapshot captures the current cursor and next live update follows its watermark", async () => {
  const storage = new MemoryStorage();
  await initializeSequenceWatermark(storage, SERIES);
  const issued = await issueTicket(storage, SERIES, "synthetic-proof-subject");
  const socket = new MemorySocket({
    authorized: false,
    seriesKey: SERIES,
    subject: null,
    connectedAt: Date.now(),
  });
  const coordinator = new SeriesCoordinatorDO({
    storage,
    getWebSockets: () => [socket],
  }, {});

  const beforeAuthentication = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seriesKey: SERIES, sequence: "51" }),
  }));
  assert.equal(beforeAuthentication.status, 200);
  assert.equal((await beforeAuthentication.json()).delivered, 0);

  await coordinator.webSocketMessage(socket, JSON.stringify({
    type: "auth",
    ticket: issued.ticket,
  }));
  assert.equal(socket.attachment.snapshotWatermark, 51);
  assert.equal(socket.sent[0].type, "market_data.status");
  const identity = {
    seriesKey: SERIES, provider: "synthetic", seriesType: "contract",
    dataset: "DEMO", publisherId: 1, instrumentId: 101,
    rawSymbol: "BTCUSD", timeframe: "1m", bucketPolicy: "UTC_LEGACY",
    calendarId: "", calendarVersion: "",
  };
  await coordinator.webSocketMessage(socket, JSON.stringify({
    type: "market_data.subscribe", version: 1, series: identity,
  }));
  assert.equal(socket.sent[1].type, "market_data.ohlcv.snapshot");
  assert.equal(socket.sent[1].highWaterCursor, "51");
  assert.equal(socket.sent[1].bars.length, 50);
  assert.equal(socket.sent[1].bars[0].sequence, 2);
  assert.equal(socket.sent[1].bars.at(-1).sequence, 51);
  assert.equal(socket.attachment.subscribed, true);

  const afterSnapshot = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seriesKey: SERIES, sequence: "52" }),
  }));
  assert.equal(afterSnapshot.status, 200);
  assert.equal((await afterSnapshot.json()).delivered, 1);
  assert.equal(socket.sent[2].type, "market_data.ohlcv.update");
  assert.equal(socket.sent[2].sequence, 52);
  assert.equal(socket.sent[2].cursor, "52");
  assert.match(socket.sent[2].digest, /^[0-9a-f]{64}$/);
});


test("Batch 91 canonical synthetic OHLCV envelopes match the frontend wire contract", async () => {
  const identity = {
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
  assert.equal(validateSyntheticCanonicalSeries(identity), true);
  assert.equal(validateSyntheticCanonicalSeries({ ...identity, provider: "databento" }), false);

  const bars = Array.from({ length: 50 }, (_, index) => ({
    sequence: index + 1,
    tsReceivedNs: (1_800_000_000_000_000_000n + BigInt(index)).toString(),
    ...{},
  }));
  const { createSyntheticCanonicalBar } = await import("./market-data-contract.mjs");
  const canonicalBars = bars.map((item) =>
    createSyntheticCanonicalBar(identity, item.sequence, item.tsReceivedNs)
  );
  const snapshot = await createSyntheticSnapshotEnvelope(identity, canonicalBars, 50);
  assert.equal(snapshot.type, "market_data.ohlcv.snapshot");
  assert.equal(snapshot.version, 1);
  assert.equal(snapshot.state, "ready");
  assert.equal(snapshot.highWaterCursor, "50");
  assert.equal(snapshot.retentionFloorCursor, "1");
  assert.match(snapshot.snapshotDigest, /^[0-9a-f]{64}$/);
  assert.equal(snapshot.provenance.mode, "synthetic");
  assert.equal(snapshot.provenance.dataStatus, "synthetic_only");
  assert.equal(snapshot.provenance.providerConnected, false);
  assert.equal(snapshot.bars[0].provider, "synthetic");
  assert.equal(snapshot.bars[0].origin, "derived");

  const event = await createSyntheticUpdateEnvelope(identity, 51, "1800000000000000051");
  assert.equal(event.type, "market_data.ohlcv.update");
  assert.equal(event.sequence, 51);
  assert.equal(event.cursor, "51");
  assert.equal(event.generationId, "synthetic-v1");
  assert.match(event.digest, /^[0-9a-f]{64}$/);
  assert.equal(event.series.seriesKey, SERIES);
  assert.equal(event.provenance.dataStatus, "synthetic_only");
  assert.equal(event.bar.sequence, 51);
  assert.equal(event.bar.provider, "synthetic");

  const error = createProtocolError("invalid_request", false, "corr-51", "Invalid request.");
  assert.deepEqual(error, {
    type: "market_data.error",
    version: 1,
    code: "invalid_request",
    retryable: false,
    correlationId: "corr-51",
    message: "Invalid request.",
  });
  assert.throws(() => createProtocolError("secret_leak", false, "corr-51", "bad"));
});
