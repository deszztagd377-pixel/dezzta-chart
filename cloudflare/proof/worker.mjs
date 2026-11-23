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
const UNAUTHENTICATED_SOCKET_TTL_MS = 15_000;
const MAX_REQUEST_BYTES = 2_048;
const SNAPSHOT_BARS = 50;
const SNAPSHOT_WATERMARK = SNAPSHOT_BARS;
const TICKET_PURPOSE = "market-data";
const SERIES_PATTERN = /^synthetic:[A-Z0-9._-]{1,24}:[A-Z0-9._-]{1,24}:(1m|5m|15m|1h)$/;

export function isValidSyntheticSeriesKey(value) {
  return typeof value === "string" && value.length <= 128 && SERIES_PATTERN.test(value);
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

export function createSyntheticBars(seriesKey, count = SNAPSHOT_BARS) {
  if (!Number.isSafeInteger(count) || count < 1 || count > SNAPSHOT_BARS) {
    throw new RangeError("Synthetic snapshot size must be between 1 and 50 bars.");
  }
  return Array.from({ length: count }, (_, index) => createSyntheticBar(seriesKey, index + 1));
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
    await transaction.delete(key);
    return record;
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
    return attachment.subject === "synthetic-proof-subject" &&
      attachment.snapshotWatermark === SNAPSHOT_WATERMARK;
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
  const declaredLength = Number(request.headers.get("Content-Length") || "0");
  if (declaredLength > MAX_REQUEST_BYTES) return null;
  const body = await request.text();
  if (new TextEncoder().encode(body).byteLength > MAX_REQUEST_BYTES) return null;
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

export class SeriesCoordinatorDO {
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
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
      if (this.ctx.getWebSockets().length >= MAX_CONNECTIONS_PER_SERIES) {
        return new Response("Series connection capacity reached", { status: 429 });
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
        if (attachment.authorized && attachment.seriesKey === body.seriesKey) {
          try {
            socket.send(JSON.stringify(event));
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

      const authorized = {
        ...attachment,
        authorized: true,
        subject: record.subject,
        snapshotWatermark: SNAPSHOT_WATERMARK,
      };
      if (Date.now() >= attachment.connectedAt + UNAUTHENTICATED_SOCKET_TTL_MS) {
        socket.close(4408, "Authentication timeout");
        return;
      }
      socket.serializeAttachment(authorized);
      await this.scheduleUnauthenticatedSocketAlarm();
      socket.send(JSON.stringify({
        type: "market_data.snapshot",
        version: PROTOCOL_VERSION,
        streamId: "synthetic:" + attachment.seriesKey,
        snapshotGeneration: "synthetic-v1",
        watermarkCursor: String(SNAPSHOT_WATERMARK),
        bars: createSyntheticBars(attachment.seriesKey, SNAPSHOT_BARS),
        dataSource: "synthetic_only_not_market_data",
      }));
      return;
    }

    if (payload?.type === "ping") {
      socket.send(JSON.stringify({ type: "pong", version: PROTOCOL_VERSION }));
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
      const seriesKey = url.searchParams.get("seriesKey");
      if (!isValidSyntheticSeriesKey(seriesKey)) {
        return withCors(jsonResponse({ error: "invalid_series" }, 400), origin);
      }
      return withCors(jsonResponse({
        type: "market_data.snapshot",
        version: PROTOCOL_VERSION,
        streamId: "synthetic:" + seriesKey,
        snapshotGeneration: "synthetic-v1",
        watermarkCursor: String(SNAPSHOT_WATERMARK),
        bars: createSyntheticBars(seriesKey, SNAPSHOT_BARS),
        dataSource: "synthetic_only_not_market_data",
      }), origin);
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
  unauthenticatedSocketTtlMs: UNAUTHENTICATED_SOCKET_TTL_MS,
  maxRequestBytes: MAX_REQUEST_BYTES,
  snapshotBars: SNAPSHOT_BARS,
});
