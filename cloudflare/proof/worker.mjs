import {
  createSyntheticCanonicalBar,
  createSyntheticSnapshotEnvelope,
  createSyntheticUpdateEnvelope,
  validateSyntheticCanonicalSeries,
} from "./market-data-contract.mjs";

/**
 * DEZZTA CHART synthetic-only Cloudflare proof.
 *
 * This is an isolated Worker/DO experiment. It is deliberately not wired into
 * the production FastAPI app, Firebase, any market-data provider, or the UI.
 * No provider connection or recurring timer is created.
 */

const PROTOCOL_VERSION = 1;
const TICKET_TTL_MS = 90_000;
const MAX_TICKET_COUNT = 256;
const MAX_CONNECTIONS_PER_SERIES = 64;
const MAX_UNAUTHENTICATED_CONNECTIONS_PER_SERIES = 8;
const UNAUTHENTICATED_SOCKET_TTL_MS = 15_000;
const MAX_REQUEST_BYTES = 2_048;
const SNAPSHOT_BARS = 50;
const SNAPSHOT_WATERMARK = SNAPSHOT_BARS;
const TICKET_PURPOSE = "market-data";
const SERIES_PATTERN = /^synthetic:[A-Z0-9._-]{1,24}:[A-Z0-9._-]{1,24}:(1m|5m|15m|1h)$/;

export function isValidSyntheticSeriesKey(value) {
  return typeof value === "string" && value.length <= 128 && SERIES_PATTERN.test(value);
}

function syntheticSeriesFromUrl(url) {
  const suppliedKey = url.searchParams.get("seriesKey");
  if (suppliedKey && isValidSyntheticSeriesKey(suppliedKey)) {
    const [, keyDataset, keySymbol, keyTimeframe] = suppliedKey.split(":");
    if (url.searchParams.has("provider") && url.searchParams.get("provider") !== "synthetic") return null;
    const identity = {
      seriesKey: suppliedKey,
      provider: "synthetic",
      seriesType: url.searchParams.get("series_type") || "contract",
      dataset: url.searchParams.get("dataset") || keyDataset,
      publisherId: url.searchParams.has("publisher_id") ? Number(url.searchParams.get("publisher_id")) : 1,
      instrumentId: url.searchParams.has("instrument_id") ? Number(url.searchParams.get("instrument_id")) : 1,
      rawSymbol: url.searchParams.get("raw_symbol") || keySymbol,
      timeframe: url.searchParams.get("timeframe") || keyTimeframe,
      bucketPolicy: url.searchParams.get("bucket_policy") || "UTC_LEGACY",
      calendarId: url.searchParams.get("calendar_id") || "",
      calendarVersion: url.searchParams.get("calendar_version") || "",
    };
    if (identity.dataset !== keyDataset || identity.rawSymbol !== keySymbol ||
        identity.timeframe !== keyTimeframe) return null;
    return validateSyntheticCanonicalSeries(identity) ? identity : null;
  }
  if (url.searchParams.get("provider") !== "synthetic") return null;
  const dataset = url.searchParams.get("dataset");
  const rawSymbol = url.searchParams.get("raw_symbol");
  const timeframe = url.searchParams.get("timeframe");
  const publisherId = Number(url.searchParams.get("publisher_id"));
  const instrumentId = Number(url.searchParams.get("instrument_id"));
  const bucketPolicy = url.searchParams.get("bucket_policy") || "UTC_LEGACY";
  const calendarId = url.searchParams.get("calendar_id") || "";
  const calendarVersion = url.searchParams.get("calendar_version") || "";
  if (!dataset || !rawSymbol || !timeframe ||
      !Number.isSafeInteger(publisherId) || publisherId <= 0 ||
      !Number.isSafeInteger(instrumentId) || instrumentId <= 0) return null;
  const seriesKey = `synthetic:${dataset}:${rawSymbol}:${timeframe}`;
  const identity = {
    seriesKey, provider: "synthetic", seriesType: "contract",
    dataset, publisherId, instrumentId, rawSymbol, timeframe,
    bucketPolicy, calendarId, calendarVersion,
  };
  if (suppliedKey && suppliedKey !== seriesKey) return null;
  return validateSyntheticCanonicalSeries(identity) ? identity : null;
}

export function parseSequence(value, { minimum = 1, maximum = 1_000_000_000 } = {}) {
  if (typeof value !== "string" || value.length > 10 || !/^[0-9]+$/.test(value)) return null;
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) && parsed >= minimum && parsed <= maximum ? parsed : null;
}

function hashSeed(value) {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function formatCents(value) {
  return (value / 100).toFixed(2);
}

function intervalNs(timeframe) {
  const intervals = {
    "1m": 60_000_000_000n,
    "5m": 300_000_000_000n,
    "15m": 900_000_000_000n,
    "1h": 3_600_000_000_000n,
  };
  return intervals[timeframe];
}

/** Stable deterministic OHLCV fixture. It is never sourced from an exchange. */
export function createSyntheticBar(seriesKey, sequence) {
  if (!isValidSyntheticSeriesKey(seriesKey)) throw new TypeError("Invalid synthetic series identity.");
  if (!Number.isSafeInteger(sequence) || sequence < 1 || sequence > 1_000_000_000) {
    throw new RangeError("Synthetic sequence is outside the supported range.");
  }

  const parts = seriesKey.split(":");
  const timeframe = parts[3];
  const seed = hashSeed(seriesKey);
  const openCents = 9_500_000 + ((seed + sequence * 37) % 80_000);
  const closeCents = 9_500_000 + ((seed * 7 + sequence * 53) % 80_000);
  const highCents = Math.max(openCents, closeCents) + 50 + (sequence % 70);
  const lowCents = Math.max(1, Math.min(openCents, closeCents) - 40 - (sequence % 60));
  const timestampNs = 1_700_000_000_000_000_000n + BigInt(sequence) * intervalNs(timeframe);

  return {
    sequence: String(sequence),
    timestampNs: timestampNs.toString(),
    open: formatCents(openCents),
    high: formatCents(highCents),
    low: formatCents(lowCents),
    close: formatCents(closeCents),
    volume: String(100 + ((seed + sequence * 13) % 5_000)),
  };
}

export function createSyntheticBars(seriesKey, count = SNAPSHOT_BARS, throughSequence = count) {
  if (
    !Number.isSafeInteger(count) || count < 1 || count > SNAPSHOT_BARS ||
    !Number.isSafeInteger(throughSequence) || throughSequence < count ||
    throughSequence > 1_000_000_000
  ) {
    throw new RangeError("Synthetic snapshot size or watermark is outside the supported range.");
  }
  const firstSequence = throughSequence - count + 1;
  return Array.from({ length: count }, (_, index) => (
    createSyntheticBar(seriesKey, firstSequence + index)
  ));
}

export function constantTimeEqual(left, right) {
  if (typeof left !== "string" || typeof right !== "string") return false;
  let difference = left.length ^ right.length;
  const length = Math.max(left.length, right.length);
  for (let index = 0; index < length; index += 1) {
    difference |= (left.charCodeAt(index) || 0) ^ (right.charCodeAt(index) || 0);
  }
  return difference === 0;
}

async function sha256Hex(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (item) => item.toString(16).padStart(2, "0")).join("");
}

function randomTicket() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return Array.from(bytes, (item) => item.toString(16).padStart(2, "0")).join("");
}

/** Durable, hashed, purpose- and series-bound one-time ticket storage. */
export async function issueTicket(storage, seriesKey, subject, now = Date.now()) {
  if (!isValidSyntheticSeriesKey(seriesKey)) throw new TypeError("Invalid synthetic series identity.");
  if (typeof subject !== "string" || subject !== "synthetic-proof-subject") {
    throw new TypeError("Only the synthetic proof subject is accepted.");
  }

  const ticket = randomTicket();
  const digest = await sha256Hex(ticket);
  const expiresAt = now + TICKET_TTL_MS;
  await storage.transaction(async (transaction) => {
    const existing = await transaction.list({ prefix: "ticket:", limit: MAX_TICKET_COUNT + 1 });
    for (const [key, record] of existing) {
      if (!record || record.expiresAt <= now) await transaction.delete(key);
    }
    const remaining = await transaction.list({ prefix: "ticket:", limit: MAX_TICKET_COUNT + 1 });
    if (remaining.size >= MAX_TICKET_COUNT) {
      throw new Error("Synthetic proof ticket capacity reached.");
    }
    await transaction.put("ticket:" + digest, {
      subject,
      purpose: TICKET_PURPOSE,
      seriesKey,
      expiresAt,
    });
  });
  return { ticket, expiresAt };
}

/** Consume is a single storage transaction: concurrent duplicate use has one winner. */
export async function consumeTicket(storage, ticket, expectedSeriesKey, now = Date.now()) {
  if (
    typeof ticket !== "string" ||
    !/^[0-9a-f]{64}$/.test(ticket) ||
    !isValidSyntheticSeriesKey(expectedSeriesKey)
  ) return null;

  const digest = await sha256Hex(ticket);
  return storage.transaction(async (transaction) => {
    const key = "ticket:" + digest;
    const record = await transaction.get(key);
    if (!record) return null;
    if (record.expiresAt <= now) {
      await transaction.delete(key);
      return null;
    }
    if (
      record.purpose !== TICKET_PURPOSE ||
      record.seriesKey !== expectedSeriesKey ||
      record.subject !== "synthetic-proof-subject"
    ) return null;
    const snapshotWatermark = await transaction.get("sequence:" + expectedSeriesKey);
    if (
      !Number.isSafeInteger(snapshotWatermark) ||
      snapshotWatermark < SNAPSHOT_WATERMARK ||
      snapshotWatermark > 1_000_000_000
    ) return null;
    await transaction.delete(key);
    return { ...record, snapshotWatermark };
  });
}

function readSocketAttachment(socket) {
  try {
    return socket.deserializeAttachment();
  } catch {
    return null;
  }
}

function isValidSocketAttachment(attachment) {
  if (
    !attachment ||
    typeof attachment !== "object" ||
    !isValidSyntheticSeriesKey(attachment.seriesKey) ||
    typeof attachment.authorized !== "boolean" ||
    !Number.isSafeInteger(attachment.connectedAt) ||
    attachment.connectedAt < 0
  ) return false;

  if (attachment.authorized) {
    const validBase = attachment.subject === "synthetic-proof-subject" &&
      Number.isSafeInteger(attachment.snapshotWatermark) &&
      attachment.snapshotWatermark >= SNAPSHOT_WATERMARK &&
      attachment.snapshotWatermark <= 1_000_000_000;
    if (!validBase) return false;
    if (attachment.subscribed === true) {
      return validateSyntheticCanonicalSeries(attachment.series) &&
        attachment.series.seriesKey === attachment.seriesKey;
    }
    return attachment.subscribed === undefined || attachment.subscribed === false;
  }
  return attachment.subject === null;
}

function jsonResponse(payload, status = 200, headers = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...headers },
  });
}

function parseAllowedOrigins(env) {
  const raw = typeof env.PROOF_ALLOWED_ORIGINS === "string"
    ? env.PROOF_ALLOWED_ORIGINS
    : "http://localhost:3000,http://127.0.0.1:3000";
  return new Set(raw.split(",").map((item) => item.trim()).filter(Boolean));
}

function withCors(response, origin) {
  if (!origin) return response;
  const headers = new Headers(response.headers);
  headers.set("Access-Control-Allow-Origin", origin);
  headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  headers.set("Access-Control-Allow-Headers", "Authorization, Content-Type");
  headers.set("Vary", "Origin");
  return new Response(response.body, { status: response.status, headers });
}

function hasProofAuthorization(request, env) {
  const configured = env.SYNTHETIC_PROOF_TOKEN;
  if (typeof configured !== "string" || configured.length < 32) return false;
  const supplied = request.headers.get("Authorization") || "";
  if (!supplied.startsWith("Bearer ")) return false;
  return constantTimeEqual(supplied.slice(7), configured);
}

async function readSmallJson(request) {
  if (!(request.headers.get("Content-Type") || "").toLowerCase().startsWith("application/json")) {
    return null;
  }

  const declaredLength = request.headers.get("Content-Length");
  if (declaredLength !== null) {
    if (!/^(0|[1-9][0-9]*)$/.test(declaredLength)) return null;
    const parsedLength = Number(declaredLength);
    if (!Number.isSafeInteger(parsedLength) || parsedLength > MAX_REQUEST_BYTES) return null;
  }

  if (!request.body) return null;
  const reader = request.body.getReader();
  const chunks = [];
  let totalBytes = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      totalBytes += value.byteLength;
      if (totalBytes > MAX_REQUEST_BYTES) {
        await reader.cancel("Request body exceeds the configured limit");
        return null;
      }
      chunks.push(value);
    }
  } catch {
    return null;
  } finally {
    reader.releaseLock();
  }

  const bytes = new Uint8Array(totalBytes);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }

  let body;
  try {
    body = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    return null;
  }
  try {
    const parsed = JSON.parse(body);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

/**
 * Initialize the snapshot cursor without racing the first live synthetic event.
 * The read and conditional write share the same transaction as sequence updates.
 */
export async function initializeSequenceWatermark(storage, seriesKey) {
  if (!isValidSyntheticSeriesKey(seriesKey)) throw new TypeError("Invalid synthetic series identity.");
  const sequenceKey = "sequence:" + seriesKey;
  return storage.transaction(async (transaction) => {
    const current = await transaction.get(sequenceKey);
    if (current === undefined) {
      await transaction.put(sequenceKey, SNAPSHOT_WATERMARK);
      return SNAPSHOT_WATERMARK;
    }
    if (!Number.isSafeInteger(current) || current < SNAPSHOT_WATERMARK || current > 1_000_000_000) {
      throw new Error("Stored synthetic sequence watermark is invalid.");
    }
    return current;
  });
}

export async function acceptNextSequence(storage, seriesKey, sequence) {
  if (
    !isValidSyntheticSeriesKey(seriesKey) ||
    !Number.isSafeInteger(sequence) ||
    sequence < SNAPSHOT_WATERMARK + 1 ||
    sequence > 1_000_000_000
  ) {
    return false;
  }
  const sequenceKey = "sequence:" + seriesKey;
  return storage.transaction(async (transaction) => {
    const current = await transaction.get(sequenceKey);
    if (
      current !== undefined &&
      (!Number.isSafeInteger(current) || current < SNAPSHOT_WATERMARK || current > 1_000_000_000)
    ) return false;
    const expected = (current === undefined ? SNAPSHOT_WATERMARK : current) + 1;
    if (sequence !== expected) return false;
    await transaction.put(sequenceKey, sequence);
    return true;
  });
}

const DURABLE_SCHEMA_VERSION = 1;
const MAX_DURABLE_EVENT_BYTES = 8_192;

/**
 * Additive application-level schema migration for the existing SQLite-backed DO.
 * This is separate from Wrangler's v1 class-creation migration. Legacy KV keys
 * (including sequence:* and ticket:*) are deliberately left untouched.
 */
export function applyDurableSchemaMigrations(storage, now = Date.now()) {
  if (
    !storage ||
    !storage.sql ||
    typeof storage.sql.exec !== "function" ||
    typeof storage.transactionSync !== "function"
  ) {
    throw new TypeError("SQLite Durable Object storage is required for schema migration.");
  }
  if (!Number.isSafeInteger(now) || now < 0) {
    throw new RangeError("Schema migration timestamp is invalid.");
  }

  return storage.transactionSync(() => {
    const sql = storage.sql;
    sql.exec(`
      CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY CHECK (version > 0),
        applied_at_ms INTEGER NOT NULL CHECK (applied_at_ms >= 0)
      )
    `);

    const versions = sql.exec(
      "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1",
    ).toArray();
    const currentVersion = versions.length === 0 ? 0 : versions[0].version;
    if (!Number.isSafeInteger(currentVersion) || currentVersion < 0) {
      throw new Error("Stored Durable Object schema version is invalid.");
    }
    if (currentVersion > DURABLE_SCHEMA_VERSION) {
      throw new Error("Durable Object schema is newer than this Worker supports.");
    }

    if (currentVersion < 1) {
      sql.exec(`
        CREATE TABLE IF NOT EXISTS series_state (
          series_key TEXT PRIMARY KEY
            CHECK (length(series_key) BETWEEN 1 AND 128),
          generation_id TEXT NOT NULL
            CHECK (length(generation_id) BETWEEN 1 AND 128),
          high_water INTEGER NOT NULL DEFAULT 0
            CHECK (high_water >= 0),
          retention_floor INTEGER NOT NULL DEFAULT 0
            CHECK (retention_floor >= 0 AND retention_floor <= high_water),
          updated_at_ms INTEGER NOT NULL
            CHECK (updated_at_ms >= 0)
        );

        CREATE TABLE IF NOT EXISTS series_events (
          series_key TEXT NOT NULL
            CHECK (length(series_key) BETWEEN 1 AND 128),
          generation_id TEXT NOT NULL
            CHECK (length(generation_id) BETWEEN 1 AND 128),
          sequence INTEGER NOT NULL
            CHECK (sequence > 0 AND sequence <= 1000000000),
          event_digest TEXT NOT NULL
            CHECK (
              length(event_digest) = 64
              AND event_digest NOT GLOB '*[^0-9a-f]*'
            ),
          payload TEXT NOT NULL
            CHECK (length(CAST(payload AS BLOB)) <= ${MAX_DURABLE_EVENT_BYTES}),
          committed_at_ms INTEGER NOT NULL
            CHECK (committed_at_ms >= 0),
          PRIMARY KEY (series_key, generation_id, sequence)
        );

        CREATE TABLE IF NOT EXISTS consumer_receipts (
          series_key TEXT NOT NULL
            CHECK (length(series_key) BETWEEN 1 AND 128),
          consumer_id TEXT NOT NULL
            CHECK (length(consumer_id) BETWEEN 1 AND 128),
          generation_id TEXT NOT NULL
            CHECK (length(generation_id) BETWEEN 1 AND 128),
          committed_sequence INTEGER NOT NULL
            CHECK (committed_sequence >= 0 AND committed_sequence <= 1000000000),
          event_digest TEXT NOT NULL
            CHECK (
              length(event_digest) = 64
              AND event_digest NOT GLOB '*[^0-9a-f]*'
            ),
          receipt_version INTEGER NOT NULL
            CHECK (receipt_version > 0),
          updated_at_ms INTEGER NOT NULL
            CHECK (updated_at_ms >= 0),
          PRIMARY KEY (series_key, consumer_id)
        );

        INSERT INTO schema_migrations (version, applied_at_ms)
        VALUES (1, ${now});
      `);
    }

    const verified = sql.exec(
      "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1",
    ).toArray();
    if (verified.length !== 1 || verified[0].version !== DURABLE_SCHEMA_VERSION) {
      throw new Error("Durable Object schema migration did not reach its expected version.");
    }
    return DURABLE_SCHEMA_VERSION;
  });
}

export class SeriesCoordinatorDO {
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
    if (this.ctx.storage?.sql) {
      if (typeof this.ctx.blockConcurrencyWhile !== "function") {
        throw new Error("SQLite Durable Object initialization requires blockConcurrencyWhile.");
      }
      this.ctx.blockConcurrencyWhile(() => applyDurableSchemaMigrations(this.ctx.storage));
    }
    // Hibernation-safe connection state is restored from serialized attachments.
    for (const socket of this.ctx.getWebSockets()) {
      const attachment = readSocketAttachment(socket);
      if (!isValidSocketAttachment(attachment)) {
        try { socket.close(4401, "Invalid connection state"); } catch { /* already closed */ }
      }
    }
  }

  async scheduleUnauthenticatedSocketAlarm() {
    let nextDeadline = Number.POSITIVE_INFINITY;
    for (const socket of this.ctx.getWebSockets()) {
      const attachment = readSocketAttachment(socket);
      if (!isValidSocketAttachment(attachment)) {
        try { socket.close(4401, "Invalid connection state"); } catch { /* already closed */ }
        continue;
      }
      if (!attachment.authorized) {
        nextDeadline = Math.min(
          nextDeadline,
          attachment.connectedAt + UNAUTHENTICATED_SOCKET_TTL_MS,
        );
      }
    }
    if (Number.isFinite(nextDeadline)) {
      await this.ctx.storage.setAlarm(nextDeadline);
    } else {
      await this.ctx.storage.deleteAlarm();
    }
  }

  async alarm() {
    const now = Date.now();
    let nextDeadline = Number.POSITIVE_INFINITY;
    for (const socket of this.ctx.getWebSockets()) {
      const attachment = readSocketAttachment(socket);
      if (!isValidSocketAttachment(attachment)) {
        try { socket.close(4401, "Invalid connection state"); } catch { /* already closed */ }
        continue;
      }
      if (attachment.authorized) continue;
      const deadline = attachment.connectedAt + UNAUTHENTICATED_SOCKET_TTL_MS;
      if (deadline <= now) {
        try { socket.close(4408, "Authentication timeout"); } catch { /* already closed */ }
      } else {
        nextDeadline = Math.min(nextDeadline, deadline);
      }
    }
    if (Number.isFinite(nextDeadline)) {
      await this.ctx.storage.setAlarm(nextDeadline);
    } else {
      await this.ctx.storage.deleteAlarm();
    }
  }

  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === "/internal/snapshot" && request.method === "POST") {
      const body = await readSmallJson(request);
      if (!body || !validateSyntheticCanonicalSeries(body.series)) {
        return jsonResponse({ error: "invalid_series" }, 400);
      }
      const current = await this.ctx.storage.get("sequence:" + body.series.seriesKey);
      const watermark = current === undefined ? SNAPSHOT_WATERMARK : current;
      if (!Number.isSafeInteger(watermark) || watermark < SNAPSHOT_WATERMARK || watermark > 1_000_000_000) {
        return jsonResponse({ error: "temporarily_unavailable" }, 503);
      }
      const asOfNs = (BigInt(Date.now()) * 1_000_000n).toString();
      const firstSequence = watermark - SNAPSHOT_BARS + 1;
      const bars = Array.from({ length: SNAPSHOT_BARS }, (_, index) =>
        createSyntheticCanonicalBar(body.series, firstSequence + index, asOfNs)
      );
      const snapshot = await createSyntheticSnapshotEnvelope(body.series, bars, watermark);
      return jsonResponse({
        ...snapshot,
        streamId: "synthetic:" + body.series.seriesKey,
        watermark,
        cursor: String(watermark),
      });
    }

    if (url.pathname === "/internal/ticket" && request.method === "POST") {
      const body = await readSmallJson(request);
      if (!body || !isValidSyntheticSeriesKey(body.seriesKey)) {
        return jsonResponse({ error: "invalid_series" }, 400);
      }
      try {
        await initializeSequenceWatermark(this.ctx.storage, body.seriesKey);
        const issued = await issueTicket(
          this.ctx.storage,
          body.seriesKey,
          "synthetic-proof-subject",
        );
        return jsonResponse({
          ticket: issued.ticket,
          expiresAt: issued.expiresAt,
          purpose: TICKET_PURPOSE,
          seriesKey: body.seriesKey,
        });
      } catch {
        return jsonResponse({ error: "ticket_unavailable" }, 503);
      }
    }

    if (url.pathname === "/internal/connect" && request.headers.get("Upgrade") === "websocket") {
      const seriesKey = url.searchParams.get("seriesKey");
      if (!isValidSyntheticSeriesKey(seriesKey)) return new Response("Invalid series", { status: 400 });
      const sockets = this.ctx.getWebSockets();
      if (sockets.length >= MAX_CONNECTIONS_PER_SERIES) {
        return new Response("Series connection capacity reached", { status: 429 });
      }
      let unauthenticatedCount = 0;
      for (const socket of sockets) {
        const attachment = readSocketAttachment(socket);
        if (!isValidSocketAttachment(attachment)) {
          try { socket.close(4401, "Invalid connection state"); } catch { /* already closed */ }
          continue;
        }
        if (!attachment.authorized) unauthenticatedCount += 1;
      }
      if (unauthenticatedCount >= MAX_UNAUTHENTICATED_CONNECTIONS_PER_SERIES) {
        return new Response("Authentication capacity reached", { status: 429 });
      }
      const pair = new WebSocketPair();
      const client = pair[0];
      const server = pair[1];
      this.ctx.acceptWebSocket(server);
      server.serializeAttachment({
        authorized: false,
        seriesKey,
        subject: null,
        connectedAt: Date.now(),
      });
      await this.scheduleUnauthenticatedSocketAlarm();
      return new Response(null, { status: 101, webSocket: client });
    }

    if (url.pathname === "/internal/emit" && request.method === "POST") {
      const body = await readSmallJson(request);
      const sequence = body ? parseSequence(body.sequence, { minimum: SNAPSHOT_WATERMARK + 1 }) : null;
      if (!body || !isValidSyntheticSeriesKey(body.seriesKey) || sequence === null) {
        return jsonResponse({ error: "invalid_event" }, 400);
      }

      const accepted = await acceptNextSequence(this.ctx.storage, body.seriesKey, sequence);
      if (!accepted) return jsonResponse({ error: "sequence_conflict" }, 409);

      const event = {
        type: "market_data.update",
        version: PROTOCOL_VERSION,
        streamId: "synthetic:" + body.seriesKey,
        sequence: String(sequence),
        bar: createSyntheticBar(body.seriesKey, sequence),
        dataSource: "synthetic_only_not_market_data",
      };
      let delivered = 0;
      for (const socket of this.ctx.getWebSockets()) {
        const attachment = readSocketAttachment(socket);
        if (!isValidSocketAttachment(attachment)) {
          try { socket.close(4401, "Invalid connection state"); } catch { /* already closed */ }
          continue;
        }
        if (attachment.authorized && attachment.seriesKey === body.seriesKey &&
            attachment.subscribed !== false) {
          try {
            const outbound = attachment.subscribed === true && attachment.series
              ? await createSyntheticUpdateEnvelope(
                  attachment.series,
                  sequence,
                  (BigInt(Date.now()) * 1_000_000n).toString(),
                )
              : event;
            socket.send(JSON.stringify(outbound));
            delivered += 1;
          } catch {
            try { socket.close(1011, "Synthetic fan-out failed"); } catch { /* already closed */ }
          }
        }
      }
      return jsonResponse({ accepted: true, sequence: String(sequence), delivered });
    }

    return new Response("Not found", { status: 404 });
  }

  async webSocketMessage(socket, message) {
    const raw = typeof message === "string"
      ? message
      : new TextDecoder().decode(message);
    if (raw === "ping") {
      socket.send(JSON.stringify({
        type: "market_data.pong",
        version: PROTOCOL_VERSION,
        serverTimeNs: (BigInt(Date.now()) * 1_000_000n).toString(),
      }));
      return;
    }
    if (new TextEncoder().encode(raw).byteLength > MAX_REQUEST_BYTES) {
      socket.close(4400, "Message too large");
      return;
    }

    let payload;
    try {
      payload = JSON.parse(raw);
    } catch {
      socket.close(4400, "Invalid message");
      return;
    }

    const attachment = readSocketAttachment(socket);
    if (!isValidSocketAttachment(attachment)) {
      socket.close(4401, "Connection state unavailable");
      return;
    }

    if (!attachment.authorized) {
      if (payload?.type !== "auth" || typeof payload.ticket !== "string") {
        socket.close(4401, "Single-use ticket required");
        return;
      }
      if (Date.now() >= attachment.connectedAt + UNAUTHENTICATED_SOCKET_TTL_MS) {
        socket.close(4408, "Authentication timeout");
        return;
      }
      const record = await consumeTicket(
        this.ctx.storage,
        payload.ticket,
        attachment.seriesKey,
      );
      if (!record) {
        socket.close(4401, "Ticket invalid, expired, or already consumed");
        return;
      }

      const snapshotWatermark = record.snapshotWatermark;
      const authorized = {
        ...attachment,
        authorized: true,
        subject: record.subject,
        snapshotWatermark,
      };
      if (Date.now() >= attachment.connectedAt + UNAUTHENTICATED_SOCKET_TTL_MS) {
        socket.close(4408, "Authentication timeout");
        return;
      }
      socket.serializeAttachment({ ...authorized, subscribed: false, series: null });
      socket.send(JSON.stringify({
        type: "market_data.status",
        version: PROTOCOL_VERSION,
        source: "synthetic",
        dataSource: "synthetic_only_not_market_data",
        providerConnected: false,
        liveProviderEnabled: false,
      }));
      await this.scheduleUnauthenticatedSocketAlarm();
      return;
    }

    if (raw === "ping" || payload?.type === "ping") {
      socket.send(JSON.stringify({
        type: "market_data.pong",
        version: PROTOCOL_VERSION,
        serverTimeNs: (BigInt(Date.now()) * 1_000_000n).toString(),
      }));
      return;
    }

    if (payload?.type === "market_data.subscribe" && payload.version === PROTOCOL_VERSION) {
      const series = payload.series;
      if (!validateSyntheticCanonicalSeries(series) || series.seriesKey !== attachment.seriesKey) {
        socket.send(JSON.stringify({
          type: "market_data.error",
          version: PROTOCOL_VERSION,
          code: "invalid_series",
          retryable: false,
          correlationId: "subscribe-" + Date.now(),
          message: "The requested synthetic series identity is invalid.",
        }));
        socket.close(4400, "Invalid subscription");
        return;
      }
      const watermark = attachment.snapshotWatermark;
      const asOfNs = (BigInt(Date.now()) * 1_000_000n).toString();
      const firstSequence = watermark - SNAPSHOT_BARS + 1;
      const bars = Array.from({ length: SNAPSHOT_BARS }, (_, index) =>
        createSyntheticCanonicalBar(series, firstSequence + index, asOfNs)
      );
      const snapshot = await createSyntheticSnapshotEnvelope(series, bars, watermark);
      // The connection is made fan-out eligible only after the complete snapshot
      // digest exists. There is no await between enabling fan-out and sending it.
      socket.serializeAttachment({ ...attachment, subscribed: true, series });
      socket.send(JSON.stringify({
        ...snapshot,
        streamId: "synthetic:" + attachment.seriesKey,
        watermark: watermark,
        cursor: String(watermark),
      }));
      return;
    }

    socket.close(4400, "Unsupported synthetic proof message");
  }

  webSocketClose(socket, code, reason) {
    if (code >= 1000 && code < 5000 && ![1004, 1005, 1006, 1015].includes(code)) {
      try { socket.close(code, reason); } catch { /* already closed */ }
    } else {
      try { socket.close(); } catch { /* already closed */ }
    }
  }

  webSocketError(socket) {
    try { socket.close(1011, "WebSocket error"); } catch { /* already closed */ }
  }
}

export default {
  async fetch(request, env) {
    if (env.PROOF_MODE !== "synthetic-only") {
      return jsonResponse({ error: "synthetic_proof_disabled" }, 503);
    }

    const url = new URL(request.url);
    const origin = request.headers.get("Origin");
    if (origin && !parseAllowedOrigins(env).has(origin)) {
      return jsonResponse({ error: "origin_not_allowed" }, 403);
    }

    if (request.method === "OPTIONS") {
      return withCors(new Response(null, { status: 204 }), origin);
    }

    if (url.pathname === "/health" && request.method === "GET") {
      return withCors(jsonResponse({
        status: "ok",
        mode: "synthetic-only",
        provider: "none",
        marketData: "synthetic_only_not_market_data",
      }), origin);
    }

    if (url.pathname === "/ws/market-data" && request.headers.get("Upgrade") === "websocket") {
      const seriesKey = url.searchParams.get("seriesKey");
      if (!isValidSyntheticSeriesKey(seriesKey)) {
        return withCors(jsonResponse({ error: "invalid_series" }, 400), origin);
      }
      const id = env.SERIES_COORDINATOR.idFromName(seriesKey);
      const stub = env.SERIES_COORDINATOR.get(id);
      const target = new URL(request.url);
      target.pathname = "/internal/connect";
      target.search = "?seriesKey=" + encodeURIComponent(seriesKey);
      return stub.fetch(new Request(target, request));
    }

    if (!hasProofAuthorization(request, env)) {
      return withCors(jsonResponse({ error: "synthetic_proof_auth_required" }, 401), origin);
    }

    if (url.pathname === "/v1/market-data/status" && request.method === "GET") {
      return withCors(jsonResponse({
        type: "market_data.status",
        version: PROTOCOL_VERSION,
        source: "synthetic",
        dataSource: "synthetic_only_not_market_data",
        providerConnected: false,
        liveProviderEnabled: false,
      }), origin);
    }

    if (url.pathname === "/v1/ohlcv" && request.method === "GET") {
      const series = syntheticSeriesFromUrl(url);
      if (!series) {
        return withCors(jsonResponse({
          type: "market_data.error",
          version: PROTOCOL_VERSION,
          code: "invalid_series",
          retryable: false,
          correlationId: "snapshot-" + Date.now(),
          message: "A complete explicit synthetic series identity is required for this proof endpoint.",
        }, 400), origin);
      }
      const stub = env.SERIES_COORDINATOR.get(env.SERIES_COORDINATOR.idFromName(series.seriesKey));
      const snapshotResponse = await stub.fetch("https://series.internal/internal/snapshot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ series }),
      });
      return withCors(snapshotResponse, origin);
    }

    if (url.pathname === "/v1/auth/websocket-ticket" && request.method === "POST") {
      const body = await readSmallJson(request);
      if (!body || !isValidSyntheticSeriesKey(body.seriesKey)) {
        return withCors(jsonResponse({ error: "invalid_series" }, 400), origin);
      }
      const stub = env.SERIES_COORDINATOR.get(env.SERIES_COORDINATOR.idFromName(body.seriesKey));
      const issued = await stub.fetch("https://series.internal/internal/ticket", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seriesKey: body.seriesKey }),
      });
      return withCors(issued, origin);
    }

    if (url.pathname === "/__proof/emit" && request.method === "POST") {
      const body = await readSmallJson(request);
      if (!body || !isValidSyntheticSeriesKey(body.seriesKey) || parseSequence(body.sequence, { minimum: SNAPSHOT_WATERMARK + 1 }) === null) {
        return withCors(jsonResponse({ error: "invalid_event" }, 400), origin);
      }
      const stub = env.SERIES_COORDINATOR.get(env.SERIES_COORDINATOR.idFromName(body.seriesKey));
      const emitted = await stub.fetch("https://series.internal/internal/emit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      return withCors(emitted, origin);
    }

    return withCors(jsonResponse({ error: "not_found" }, 404), origin);
  },
};

export const proofLimits = Object.freeze({
  ticketTtlMs: TICKET_TTL_MS,
  maxPendingTickets: MAX_TICKET_COUNT,
  maxConnectionsPerSeries: MAX_CONNECTIONS_PER_SERIES,
  maxUnauthenticatedConnectionsPerSeries: MAX_UNAUTHENTICATED_CONNECTIONS_PER_SERIES,
  unauthenticatedSocketTtlMs: UNAUTHENTICATED_SOCKET_TTL_MS,
  maxRequestBytes: MAX_REQUEST_BYTES,
  snapshotBars: SNAPSHOT_BARS,
});
