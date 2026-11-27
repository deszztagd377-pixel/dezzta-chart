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
  initializeDurableSeriesState,
  parseSequence,
  proofLimits,
  readDurableReplayPage,
  SeriesCoordinatorDO,
} from "./worker.mjs";

const SERIES = "synthetic:DEMO:BTCUSD:1m";
const TOKEN = "synthetic-proof-test-token-000000000000000000000000";



function bootstrapStorage(initialLegacyCursor, { failFirstTransaction = false } = {}) {
  let legacyCursor = initialLegacyCursor;
  let state = null;
  let transactionAttempts = 0;
  return {
    sql: {
      exec(query, ...params) {
        if (query.includes("SELECT generation_id, high_water FROM series_state")) {
          return { toArray: () => state ? [state] : [] };
        }
        if (query.includes("INSERT INTO series_state")) {
          const [series_key, generation_id, high_water, retention_floor, updated_at_ms] = params;
          state = { series_key, generation_id, high_water, retention_floor, updated_at_ms };
          return { toArray: () => [] };
        }
        throw new Error("Unexpected bootstrap SQL: " + query);
      },
    },
    async get(key) {
      assert.equal(key, "sequence:" + SERIES);
      return legacyCursor;
    },
    setLegacyCursor(value) { legacyCursor = value; },
    getState() { return state; },
    transactionSync(callback) {
      transactionAttempts += 1;
      if (failFirstTransaction && transactionAttempts === 1) {
        throw new Error("Injected interrupted bootstrap transaction");
      }
      return callback();
    },
  };
}

function replayStorage({ state, rows }) {
  return {
    sql: {
      exec(query, ...params) {
        if (query.includes("FROM series_state")) {
          return { toArray: () => state ? [state] : [] };
        }
        if (query.includes("FROM series_events")) {
          const [seriesKey, generationId, afterSequence, limit] = params;
          return {
            toArray: () => rows
              .filter((row) => row.seriesKey === seriesKey &&
                row.generationId === generationId && row.sequence > afterSequence)
              .sort((a, b) => a.sequence - b.sequence)
              .slice(0, limit),
          };
        }
        throw new Error("Unexpected replay SQL: " + query);
      },
    },
  };
}

function replayRows(start, count, { paddingBytes = 0 } = {}) {
  return Array.from({ length: count }, (_, index) => {
    const sequence = start + index;
    const digest = sequence.toString(16).padStart(64, "0");
    const event = {
      type: "market_data.ohlcv.update",
      generationId: "synthetic-v1",
      sequence,
      cursor: String(sequence),
      digest,
      ...(paddingBytes ? { padding: "x".repeat(paddingBytes) } : {}),
    };
    return {
      seriesKey: SERIES,
      generationId: "synthetic-v1",
      sequence,
      event_digest: digest,
      payload: JSON.stringify(event),
    };
  });
}

function canonicalSeriesForTest(seriesKey = SERIES) {
  const [, dataset, rawSymbol, timeframe] = seriesKey.split(":");
  return {
    seriesKey, provider: "synthetic", seriesType: "contract", dataset,
    publisherId: 1, instrumentId: 101, rawSymbol, timeframe,
    bucketPolicy: "UTC_LEGACY", calendarId: "", calendarVersion: "",
  };
}

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
        fetch: async (input, init) => {
          const req = input instanceof Request ? input : new Request(input, init);
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



test("legacy cursor bootstraps once into SQLite and SQLite remains authoritative", async () => {
  const storage = bootstrapStorage(73);
  assert.equal(await initializeDurableSeriesState(storage, SERIES, "synthetic-v1", 1234), 73);
  assert.deepEqual(storage.getState(), {
    series_key: SERIES,
    generation_id: "synthetic-v1",
    high_water: 73,
    retention_floor: 73,
    updated_at_ms: 1234,
  });
  storage.setLegacyCursor(91);
  assert.equal(await initializeDurableSeriesState(storage, SERIES, "synthetic-v1", 5678), 73);
  assert.equal(storage.getState().updated_at_ms, 1234);
});

test("interrupted legacy cursor bootstrap can retry safely and invalid legacy values fail closed", async () => {
  const storage = bootstrapStorage(64, { failFirstTransaction: true });
  await assert.rejects(
    initializeDurableSeriesState(storage, SERIES, "synthetic-v1", 1234),
    /Injected interrupted bootstrap transaction/,
  );
  assert.equal(storage.getState(), null);
  assert.equal(await initializeDurableSeriesState(storage, SERIES, "synthetic-v1", 1235), 64);
  await assert.rejects(
    initializeDurableSeriesState(bootstrapStorage(49), SERIES, "synthetic-v1", 1236),
    /Legacy sequence cursor cannot be safely bootstrapped/,
  );
});

test("durable replay returns ordered cursor-exclusive pages and rejects invalid cursor states", () => {
  const state = { generation_id: "synthetic-v1", high_water: 52, retention_floor: 50 };
  const rows = replayRows(51, 2);
  const storage = replayStorage({ state, rows });
  const result = readDurableReplayPage(storage, SERIES, "50");
  assert.equal(result.ok, true);
  assert.deepEqual(result.page.events.map((event) => event.sequence), [51, 52]);
  assert.equal(result.page.nextCursor, "52");
  assert.equal(result.page.highWaterCursor, "52");
  assert.equal(result.page.retentionFloorCursor, "50");
  assert.equal(result.page.hasMore, false);

  assert.equal(readDurableReplayPage(storage, SERIES, "53").reason, "cursor_ahead");
  assert.equal(readDurableReplayPage(storage, SERIES, "50", "other-generation").reason, "generation_mismatch");
  const expired = replayStorage({
    state: { ...state, retention_floor: 51 },
    rows,
  });
  assert.equal(readDurableReplayPage(expired, SERIES, "50").reason, "retention_expired");
});

test("durable replay fails closed on corrupt payloads and missing sequence rows", () => {
  const state = { generation_id: "synthetic-v1", high_water: 52, retention_floor: 50 };
  const corruptPayload = replayRows(51, 2);
  corruptPayload[0].payload = "{";
  assert.equal(
    readDurableReplayPage(replayStorage({ state, rows: corruptPayload }), SERIES, "50").reason,
    "corrupt_persisted_payload",
  );

  const gapRows = replayRows(52, 1);
  assert.equal(
    readDurableReplayPage(replayStorage({ state, rows: gapRows }), SERIES, "50").reason,
    "corrupt_sequence_gap",
  );
  assert.equal(
    readDurableReplayPage(replayStorage({ state, rows: [] }), SERIES, "50").reason,
    "corrupt_sequence_gap",
  );
});

test("durable replay enforces the 100-event and serialized UTF-8 byte page bounds", () => {
  const rows = replayRows(51, 101);
  const state = { generation_id: "synthetic-v1", high_water: 151, retention_floor: 50 };
  const countPage = readDurableReplayPage(replayStorage({ state, rows }), SERIES, "50");
  assert.equal(countPage.ok, true);
  assert.equal(countPage.page.events.length, 100);
  assert.equal(countPage.page.nextCursor, "150");
  assert.equal(countPage.page.hasMore, true);
  assert.ok(countPage.responseBytes <= 65_536);

  const paddedRows = replayRows(51, 100, { paddingBytes: 1_000 });
  const paddedState = { generation_id: "synthetic-v1", high_water: 150, retention_floor: 50 };
  const bytePage = readDurableReplayPage(replayStorage({ state: paddedState, rows: paddedRows }), SERIES, "50");
  assert.equal(bytePage.ok, true);
  assert.ok(bytePage.page.events.length > 0);
  assert.ok(bytePage.page.events.length < 100);
  assert.equal(bytePage.page.hasMore, true);
  assert.ok(bytePage.responseBytes <= 65_536);
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

test("REST snapshot requires and preserves the exact explicit synthetic series identity", async () => {
  const query = new URLSearchParams({
    provider: "synthetic",
    dataset: "DEMO",
    publisher_id: "9",
    instrument_id: "123",
    raw_symbol: "ESZ6",
    timeframe: "5m",
    bucket_policy: "UTC_LEGACY",
    calendar_id: "",
    calendar_version: "",
  });
  const response = await worker.fetch(
    request("/v1/ohlcv?" + query.toString(), { token: TOKEN }),
    makeEnv(),
  );
  const snapshot = await response.json();
  assert.equal(response.status, 200);
  assert.equal(snapshot.type, "market_data.ohlcv.snapshot");
  assert.equal(snapshot.bars[0].dataset, "DEMO");
  assert.equal(snapshot.bars[0].publisherId, 9);
  assert.equal(snapshot.bars[0].instrumentId, 123);
  assert.equal(snapshot.bars[0].rawSymbol, "ESZ6");
  assert.equal(snapshot.bars[0].timeframe, "5m");
  assert.equal(snapshot.bars[0].provider, "synthetic");

  const noSyntheticOptIn = await worker.fetch(
    request("/v1/ohlcv?" + new URLSearchParams({
      dataset: "DEMO", publisher_id: "9", instrument_id: "123",
      raw_symbol: "ESZ6", timeframe: "5m",
    }).toString(), { token: TOKEN }),
    makeEnv(),
  );
  assert.equal(noSyntheticOptIn.status, 400);
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

test("Node MemoryStorage adapter fails closed for snapshots without a durable identity registry", async () => {
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
  assert.equal(socket.sent[1].type, "market_data.error");
  assert.equal(socket.sent[1].code, "temporarily_unavailable");
  assert.equal(socket.closed[0].code, 1011);

  const replaySocket = new MemorySocket({
    authorized: false,
    seriesKey: SERIES,
    subject: null,
    connectedAt: Date.now(),
  });
  await coordinator.webSocketMessage(replaySocket, JSON.stringify({ type: "auth", ticket: issued.ticket }));
  assert.equal(replaySocket.closed[0].code, 4401);
});

test("Durable Object emit requires canonical identity and stable timestamp", async () => {
  const storage = new MemoryStorage();
  await storage.put("sequence:" + SERIES, 50);
  const sockets = [1, 2].map(() => new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  }));
  const coordinator = new SeriesCoordinatorDO({ storage, getWebSockets: () => sockets }, {});
  const legacy = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seriesKey: SERIES, sequence: "51" }),
  }));
  assert.equal(legacy.status, 400);
  assert.equal((await legacy.json()).error, "invalid_event");
  const withoutSqlite = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seriesKey: SERIES, sequence: "51", series: canonicalSeriesForTest(),
      emittedAtNs: "1800000000000000051",
    }),
  }));
  assert.equal(withoutSqlite.status, 503);
  assert.equal((await withoutSqlite.json()).error, "temporarily_unavailable");
  assert.equal(await storage.get("sequence:" + SERIES), 50);
  assert.equal(sockets.every((socket) => socket.sent.length === 0), true);
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

test("event write fails closed without SQLite and malformed attachments are rejected", async () => {
  const storage = new MemoryStorage();
  await storage.put("sequence:" + SERIES, 50);
  const valid = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
    subscribed: true, series: canonicalSeriesForTest(),
    consumerId: "synthetic-proof-websocket", lastDeliveredSequence: 50,
  });
  const malformed = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "invalid-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
  });
  const coordinator = new SeriesCoordinatorDO({ storage, getWebSockets: () => [valid, malformed] }, {});
  assert.equal(malformed.closed[0].code, 4401);
  const response = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seriesKey: SERIES, sequence: "51", series: canonicalSeriesForTest(),
      emittedAtNs: "1800000000000000051",
    }),
  }));
  assert.equal(response.status, 503);
  assert.equal((await response.json()).error, "temporarily_unavailable");
  assert.equal(valid.sent.length, 0);
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

test("fan-out is withheld until a durable SQLite commit succeeds", async () => {
  const storage = new MemoryStorage();
  await storage.put("sequence:" + SERIES, 50);
  const failing = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
    subscribed: true, series: canonicalSeriesForTest(),
    consumerId: "synthetic-proof-websocket", lastDeliveredSequence: 50,
  });
  failing.send = () => { throw new Error("send must not run before commit"); };
  const healthy = new MemorySocket({
    authorized: true, seriesKey: SERIES, subject: "synthetic-proof-subject",
    connectedAt: Date.now(), snapshotWatermark: 50,
    subscribed: true, series: canonicalSeriesForTest(),
    consumerId: "synthetic-proof-websocket", lastDeliveredSequence: 50,
  });
  const coordinator = new SeriesCoordinatorDO({
    storage, getWebSockets: () => [failing, healthy],
  }, {});
  const response = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seriesKey: SERIES, sequence: "51", series: canonicalSeriesForTest(),
      emittedAtNs: "1800000000000000051",
    }),
  }));
  assert.equal(response.status, 503);
  assert.equal((await response.json()).error, "temporarily_unavailable");
  assert.equal(failing.closed.length, 0);
  assert.equal(healthy.sent.length, 0);
  assert.equal(await storage.get("sequence:" + SERIES), 50);
});

test("failed event commit and snapshot fail closed without SQLite identity storage", async () => {
  const storage = new MemoryStorage();
  await initializeSequenceWatermark(storage, SERIES);
  const issued = await issueTicket(storage, SERIES, "synthetic-proof-subject");
  const socket = new MemorySocket({
    authorized: false, seriesKey: SERIES, subject: null, connectedAt: Date.now(),
  });
  const coordinator = new SeriesCoordinatorDO({ storage, getWebSockets: () => [socket] }, {});
  const eventResponse = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seriesKey: SERIES, sequence: "51", series: canonicalSeriesForTest(),
      emittedAtNs: "1800000000000000051",
    }),
  }));
  assert.equal(eventResponse.status, 503);
  assert.equal(await storage.get("sequence:" + SERIES), 50);

  await coordinator.webSocketMessage(socket, JSON.stringify({ type: "auth", ticket: issued.ticket }));
  assert.equal(socket.attachment.snapshotWatermark, 50);
  assert.equal(socket.sent[0].type, "market_data.status");
  await coordinator.webSocketMessage(socket, JSON.stringify({
    type: "market_data.subscribe", version: 1, series: canonicalSeriesForTest(),
  }));
  assert.equal(socket.sent[1].type, "market_data.error");
  assert.equal(socket.sent[1].code, "temporarily_unavailable");
  assert.equal(socket.closed[0].code, 1011);

  const nextEvent = await coordinator.fetch(new Request("https://series.internal/internal/emit", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seriesKey: SERIES, sequence: "51", series: canonicalSeriesForTest(),
      emittedAtNs: "1800000000000000051",
    }),
  }));
  assert.equal(nextEvent.status, 503);
  assert.equal(socket.sent.length, 2);
  assert.equal(await storage.get("sequence:" + SERIES), 50);
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
