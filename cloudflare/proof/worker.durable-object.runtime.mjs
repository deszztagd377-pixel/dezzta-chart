import { env, exports } from "cloudflare:workers";
import {
  evictDurableObject,
  reset,
  runDurableObjectAlarm,
  runInDurableObject,
} from "cloudflare:test";
import { afterEach, describe, expect, it } from "vitest";
import { proofLimits } from "./worker.mjs";

const ORIGIN = "http://localhost:3000";
const TOKEN = "synthetic-proof-test-token-000000000000000000000000";
const SERIES_A = "synthetic:DEMO:BTCUSD:1m";
const SERIES_B = "synthetic:DEMO:ETHUSD:1m";
const SERIES_REPLAY = "synthetic:DEMO:REPLAY:1m";
const SERIES_HIBERNATE = "synthetic:DEMO:HIBERNATE:1m";
const SERIES_ALARM = "synthetic:DEMO:ALARM:1m";

const openSockets = new Set();

function workerHeaders() {
  return {
    Origin: ORIGIN,
    Authorization: `Bearer ${TOKEN}`,
    "Content-Type": "application/json",
  };
}

async function workerFetch(path, init = {}) {
  const headers = new Headers(init.headers ?? {});
  if (!headers.has("Origin")) headers.set("Origin", ORIGIN);
  return exports.default.fetch(new Request(`https://proof.local${path}`, {
    ...init,
    headers,
  }));
}

async function issueTicket(seriesKey) {
  const response = await workerFetch("/v1/auth/websocket-ticket", {
    method: "POST",
    headers: workerHeaders(),
    body: JSON.stringify({ seriesKey }),
  });
  expect(response.status).toBe(200);
  const payload = await response.json();
  expect(payload).toMatchObject({ purpose: "market-data", seriesKey });
  expect(payload.ticket).toMatch(/^[0-9a-f]{64}$/);
  return payload.ticket;
}

async function openSocket(seriesKey) {
  const response = await workerFetch(
    `/ws/market-data?seriesKey=${encodeURIComponent(seriesKey)}`,
    { headers: { Origin: ORIGIN, Upgrade: "websocket" } },
  );
  expect(response.status).toBe(101);
  expect(response.webSocket).toBeDefined();
  const socket = response.webSocket;
  socket.accept();
  openSockets.add(socket);
  return socket;
}

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
      reject(new Error("Timed out waiting for a Durable Object WebSocket message."));
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
      reject(new Error("Durable Object WebSocket emitted an error."));
    };
    socket.addEventListener("message", onMessage, { once: true });
    socket.addEventListener("close", onClose, { once: true });
    socket.addEventListener("error", onError, { once: true });
  });
}

function nextClose(socket, timeoutMs = 5_000) {
  return new Promise((resolve, reject) => {
    const cleanup = () => {
      clearTimeout(timer);
      socket.removeEventListener("close", onClose);
      socket.removeEventListener("error", onError);
    };
    const timer = setTimeout(() => {
      cleanup();
      reject(new Error("Timed out waiting for the Durable Object WebSocket to close."));
    }, timeoutMs);
    const onClose = (event) => {
      cleanup();
      resolve(event);
    };
    const onError = () => {
      cleanup();
      reject(new Error("Durable Object WebSocket errored before closing."));
    };
    socket.addEventListener("close", onClose, { once: true });
    socket.addEventListener("error", onError, { once: true });
  });
}

function canonicalSeries(seriesKey) {
  const [, dataset, rawSymbol, timeframe] = seriesKey.split(":");
  return {
    seriesKey,
    provider: "synthetic",
    seriesType: "contract",
    dataset,
    publisherId: 1,
    instrumentId: 101,
    rawSymbol,
    timeframe,
    bucketPolicy: "UTC_LEGACY",
    calendarId: "",
    calendarVersion: "",
  };
}

async function connectAuthenticated(seriesKey, suppliedTicket) {
  const ticket = suppliedTicket ?? await issueTicket(seriesKey);
  const socket = await openSocket(seriesKey);
  const statusPromise = nextJsonMessage(socket);
  socket.send(JSON.stringify({ type: "auth", ticket }));
  const status = await statusPromise;
  expect(status).toMatchObject({
    type: "market_data.status",
    version: 1,
    providerConnected: false,
    liveProviderEnabled: false,
  });
  const snapshotPromise = nextJsonMessage(socket);
  socket.send(JSON.stringify({
    type: "market_data.subscribe",
    version: 1,
    series: canonicalSeries(seriesKey),
  }));
  const snapshot = await snapshotPromise;
  expect(snapshot).toMatchObject({
    type: "market_data.ohlcv.snapshot",
    version: 1,
    highWaterCursor: "50",
    provenance: { mode: "synthetic", dataStatus: "synthetic_only", providerConnected: false },
  });
  expect(snapshot.bars).toHaveLength(50);
  return { socket, ticket, snapshot };
}

function coordinatorStub(seriesKey) {
  return env.SERIES_COORDINATOR.get(
    env.SERIES_COORDINATOR.idFromName(seriesKey),
  );
}

async function emit(seriesKey, sequence, emittedAtNs = (1_800_000_000_000_000_000n + BigInt(sequence)).toString()) {
  const response = await workerFetch("/__proof/emit", {
    method: "POST",
    headers: workerHeaders(),
    body: JSON.stringify({
      seriesKey, sequence: String(sequence), series: canonicalSeries(seriesKey), emittedAtNs,
    }),
  });
  return { status: response.status, payload: await response.json() };
}

afterEach(async () => {
  const closePromises = [];
  for (const socket of openSockets) {
    if (socket.readyState === 1 || socket.readyState === 2) {
      const closed = nextClose(socket, 1_000).catch(() => undefined);
      if (socket.readyState === 1) {
        try {
          socket.close(1000, "Cloudflare Durable Object test teardown");
        } catch {
          // The runtime may already be closing this socket.
        }
      }
      closePromises.push(closed);
    }
  }
  await Promise.all(closePromises);
  openSockets.clear();
  await reset();
});

describe("synthetic Cloudflare Durable Object runtime", () => {
  it("serializes snapshot establishment with event persistence and fan-out", async () => {
    const stub = coordinatorStub(SERIES_A);
    const order = await runInDurableObject(stub, async (instance) => {
      const events = [];
      const snapshot = instance.runProtocolExclusive(async () => {
        events.push("snapshot-start");
        await new Promise((resolve) => setTimeout(resolve, 10));
        events.push("snapshot-ready");
      });
      const emit = instance.runProtocolExclusive(async () => {
        events.push("event-commit-and-fanout");
      });
      await Promise.all([snapshot, emit]);
      return events;
    });
    expect(order).toEqual([
      "snapshot-start",
      "snapshot-ready",
      "event-commit-and-fanout",
    ]);
  });

  it("installs the additive SQLite schema once and preserves legacy v1 KV state", async () => {
    const stub = coordinatorStub(SERIES_A);
    const first = await runInDurableObject(stub, async (_instance, state) => {
      const sql = state.storage.sql;
      const versions = sql.exec(
        "SELECT version FROM schema_migrations ORDER BY version",
      ).toArray();
      const tables = sql.exec(
        "SELECT name FROM sqlite_master WHERE type = 'table' " +
        "AND name IN ('schema_migrations', 'series_state', 'series_events', 'consumer_receipts', 'series_identity') " +
        "ORDER BY name",
      ).toArray().map((row) => row.name);
      const stateColumns = sql.exec("PRAGMA table_info(series_state)")
        .toArray().map((row) => row.name);
      const eventColumns = sql.exec("PRAGMA table_info(series_events)")
        .toArray().map((row) => row.name);
      const receiptColumns = sql.exec("PRAGMA table_info(consumer_receipts)")
        .toArray().map((row) => row.name);
      const identityColumns = sql.exec("PRAGMA table_info(series_identity)")
        .toArray().map((row) => row.name);

      sql.exec(
        "INSERT INTO series_identity (series_key, identity_json, created_at_ms) VALUES (?, ?, ?)",
        SERIES_A, "{}", 1,
      );
      expect(() => sql.exec(
        "UPDATE series_identity SET identity_json = ? WHERE series_key = ?",
        "[]", SERIES_A,
      )).toThrow();
      expect(() => sql.exec(
        "DELETE FROM series_identity WHERE series_key = ?",
        SERIES_A,
      )).toThrow();
      expect(() => sql.exec(
        "INSERT INTO series_identity (series_key, identity_json, created_at_ms) VALUES (?, ?, ?)",
        SERIES_A, "{}", 2,
      )).toThrow();

      await state.storage.put("sequence:" + SERIES_A, 50);
      const legacyCursor = await state.storage.get("sequence:" + SERIES_A);

      expect(() => sql.exec(
        "INSERT INTO series_state " +
        "(series_key, generation_id, high_water, retention_floor, updated_at_ms) " +
        "VALUES (?, ?, ?, ?, ?)",
        SERIES_A,
        "generation-invalid",
        1,
        2,
        1,
      )).toThrow();

      sql.exec(
        "INSERT INTO series_state " +
        "(series_key, generation_id, high_water, retention_floor, updated_at_ms) " +
        "VALUES (?, ?, ?, ?, ?)",
        SERIES_A,
        "generation-test",
        0,
        0,
        1,
      );
      sql.exec(
        "INSERT INTO series_events " +
        "(series_key, generation_id, sequence, event_digest, payload, committed_at_ms) " +
        "VALUES (?, ?, ?, ?, ?, ?)",
        SERIES_A,
        "generation-test",
        1,
        "a".repeat(64),
        "{}",
        1,
      );
      expect(() => sql.exec(
        "INSERT INTO series_events " +
        "(series_key, generation_id, sequence, event_digest, payload, committed_at_ms) " +
        "VALUES (?, ?, ?, ?, ?, ?)",
        SERIES_A,
        "generation-test",
        1,
        "a".repeat(64),
        "{}",
        2,
      )).toThrow();

      return {
        versions,
        tables,
        stateColumns,
        eventColumns,
        receiptColumns,
        identityColumns,
        legacyCursor,
      };
    });

    expect(first.versions).toEqual([{ version: 1 }, { version: 2 }]);
    expect(first.tables).toEqual([
      "consumer_receipts",
      "schema_migrations",
      "series_events",
      "series_identity",
      "series_state",
    ]);
    expect(first.stateColumns).toEqual([
      "series_key",
      "generation_id",
      "high_water",
      "retention_floor",
      "updated_at_ms",
    ]);
    expect(first.eventColumns).toEqual([
      "series_key",
      "generation_id",
      "sequence",
      "event_digest",
      "payload",
      "committed_at_ms",
    ]);
    expect(first.receiptColumns).toEqual([
      "series_key", "consumer_id", "generation_id", "committed_sequence",
      "event_digest", "receipt_version", "updated_at_ms",
    ]);
    expect(first.identityColumns).toEqual(["series_key", "identity_json", "created_at_ms"]);
    expect(first.legacyCursor).toBe(50);

    await evictDurableObject(stub);
    const restored = await runInDurableObject(stub, async (_instance, state) => ({
      versions: state.storage.sql.exec(
        "SELECT version FROM schema_migrations ORDER BY version",
      ).toArray(),
      legacyCursor: await state.storage.get("sequence:" + SERIES_A),
      eventCount: state.storage.sql.exec(
        "SELECT COUNT(*) AS count FROM series_events WHERE series_key = ?",
        SERIES_A,
      ).one().count,
    }));

    expect(restored.versions).toEqual([{ version: 1 }, { version: 2 }]);
    expect(restored.legacyCursor).toBe(50);
    expect(restored.eventCount).toBe(1);
  });

  it("persists canonical event bytes and high-water atomically and rejects identity mutation", async () => {
    const seriesKey = "synthetic:DEMO:ATOMIC:1m";
    const first = await emit(seriesKey, 51);
    expect(first.status).toBe(200);
    expect(first.payload).toMatchObject({ accepted: true, duplicate: false, sequence: "51" });
    const stub = coordinatorStub(seriesKey);
    const stored = await runInDurableObject(stub, async (_instance, state) => ({
      state: state.storage.sql.exec(
        "SELECT generation_id, high_water, retention_floor FROM series_state WHERE series_key = ?", seriesKey,
      ).toArray(),
      events: state.storage.sql.exec(
        "SELECT sequence, event_digest, payload FROM series_events WHERE series_key = ? ORDER BY sequence", seriesKey,
      ).toArray(),
      identity: state.storage.sql.exec(
        "SELECT identity_json FROM series_identity WHERE series_key = ?", seriesKey,
      ).toArray(),
    }));
    expect(stored.state).toEqual([{ generation_id: "synthetic-v1", high_water: 51, retention_floor: 50 }]);
    expect(stored.events).toHaveLength(1);
    expect(JSON.parse(stored.events[0].payload)).toMatchObject({
      type: "market_data.ohlcv.update", sequence: 51, digest: stored.events[0].event_digest,
      series: { seriesKey },
    });
    expect(stored.identity).toHaveLength(1);
    const changedIdentity = canonicalSeries(seriesKey);
    changedIdentity.instrumentId = 999;
    const conflict = await workerFetch("/__proof/emit", {
      method: "POST", headers: workerHeaders(),
      body: JSON.stringify({
        seriesKey, sequence: "52", series: changedIdentity, emittedAtNs: "1800000000000000002",
      }),
    });
    expect(conflict.status).toBe(409);
    expect(await conflict.json()).toMatchObject({ error: "series_identity_conflict" });
    const unchanged = await runInDurableObject(stub, async (_instance, state) => ({
      highWater: state.storage.sql.exec(
        "SELECT high_water FROM series_state WHERE series_key = ?", seriesKey,
      ).one().high_water,
      eventCount: state.storage.sql.exec(
        "SELECT COUNT(*) AS count FROM series_events WHERE series_key = ?", seriesKey,
      ).one().count,
    }));
    expect(unchanged).toEqual({ highWater: 51, eventCount: 1 });
  });

  it("fans out only to authenticated sockets for the exact series", async () => {
    const [first, second, otherSeries] = await Promise.all([
      connectAuthenticated(SERIES_A),
      connectAuthenticated(SERIES_A),
      connectAuthenticated(SERIES_B),
    ]);

    const firstUpdatePromise = nextJsonMessage(first.socket);
    const secondUpdatePromise = nextJsonMessage(second.socket);
    const result = await emit(SERIES_A, 51);

    expect(result.status).toBe(200);
    expect(result.payload).toMatchObject({
      accepted: true,
      sequence: "51",
      delivered: 2,
    });

    const [firstUpdate, secondUpdate] = await Promise.all([
      firstUpdatePromise,
      secondUpdatePromise,
    ]);
    expect(firstUpdate).toMatchObject({
      type: "market_data.ohlcv.update",
      sequence: 51,
      cursor: "51",
      provenance: { mode: "synthetic", dataStatus: "synthetic_only", providerConnected: false },
    });
    expect(secondUpdate).toMatchObject({
      type: "market_data.ohlcv.update",
      sequence: 51,
      cursor: "51",
      provenance: { mode: "synthetic", dataStatus: "synthetic_only", providerConnected: false },
    });
    expect(otherSeries.socket.readyState).toBe(1);
  });

  it("anchors the snapshot at the latest cursor before accepting subsequent live updates", async () => {
    const ticket = await issueTicket(SERIES_A);
    const beforeAuthentication = await emit(SERIES_A, 51);
    expect(beforeAuthentication.status).toBe(200);
    expect(beforeAuthentication.payload).toMatchObject({
      accepted: true,
      sequence: "51",
      delivered: 0,
    });

    const socket = await openSocket(SERIES_A);
    const statusPromise = nextJsonMessage(socket);
    socket.send(JSON.stringify({ type: "auth", ticket }));
    const status = await statusPromise;
    expect(status.type).toBe("market_data.status");
    const snapshotPromise = nextJsonMessage(socket);
    socket.send(JSON.stringify({
      type: "market_data.subscribe", version: 1, series: canonicalSeries(SERIES_A),
    }));
    const snapshot = await snapshotPromise;

    expect(snapshot).toMatchObject({
      type: "market_data.ohlcv.snapshot",
      highWaterCursor: "51",
      provenance: { dataStatus: "synthetic_only" },
    });
    expect(snapshot.bars).toHaveLength(50);
    expect(snapshot.bars[0].sequence).toBe(2);
    expect(snapshot.bars.at(-1).sequence).toBe(51);

    const nextUpdatePromise = nextJsonMessage(socket);
    const next = await emit(SERIES_A, 52);
    expect(next.status).toBe(200);
    expect(next.payload).toMatchObject({
      accepted: true,
      sequence: "52",
      delivered: 1,
    });
    expect(await nextUpdatePromise).toMatchObject({
      type: "market_data.ohlcv.update",
      sequence: 52,
      cursor: "52",
    });
  });

  it("requires a fresh canonical snapshot when a resume cursor is supplied", async () => {
    const ticket = await issueTicket(SERIES_A);
    const socket = await openSocket(SERIES_A);
    const statusPromise = nextJsonMessage(socket);
    socket.send(JSON.stringify({ type: "auth", ticket }));
    expect((await statusPromise).type).toBe("market_data.status");

    const resnapshotPromise = nextJsonMessage(socket);
    socket.send(JSON.stringify({
      type: "market_data.subscribe",
      version: 1,
      cursor: "49",
      series: canonicalSeries(SERIES_A),
    }));
    const instruction = await resnapshotPromise;
    expect(instruction).toMatchObject({
      type: "market_data.ohlcv.resnapshot_required",
      reason: "replay_unavailable_in_synthetic_proof",
      snapshotCursor: "50",
    });
    const snapshot = await nextJsonMessage(socket);
    expect(snapshot).toMatchObject({
      type: "market_data.ohlcv.snapshot",
      highWaterCursor: "50",
      cursor: "50",
    });
  });

  it("rejects non-canonical resume cursors with a stable protocol error", async () => {
    const ticket = await issueTicket(SERIES_A);
    const socket = await openSocket(SERIES_A);
    const statusPromise = nextJsonMessage(socket);
    socket.send(JSON.stringify({ type: "auth", ticket }));
    await statusPromise;
    const errorPromise = nextJsonMessage(socket);
    socket.send(JSON.stringify({
      type: "market_data.subscribe",
      version: 1,
      cursor: "050",
      series: canonicalSeries(SERIES_A),
    }));
    expect(await errorPromise).toMatchObject({
      type: "market_data.error",
      version: 1,
      code: "cursor_invalid",
      retryable: false,
    });
  });

  it("consumes a WebSocket ticket once in Durable Object storage", async () => {
    const ticket = await issueTicket(SERIES_REPLAY);
    await connectAuthenticated(SERIES_REPLAY, ticket);

    const replaySocket = await openSocket(SERIES_REPLAY);
    const closedPromise = nextClose(replaySocket);
    replaySocket.send(JSON.stringify({ type: "auth", ticket }));

    const closed = await closedPromise;
    expect(closed.code).toBe(4401);
  });

  it("allows exactly one winner when two sockets race to consume the same ticket", async () => {
    const ticket = await issueTicket(SERIES_REPLAY);
    const firstSocket = await openSocket(SERIES_REPLAY);
    const secondSocket = await openSocket(SERIES_REPLAY);

    // Install both observers before sending either authentication frame so a
    // fast Durable Object response cannot escape the test harness.
    const observe = (socket) => nextJsonMessage(socket).then(
      (message) => ({ kind: "message", message, socket }),
      (error) => ({ kind: "closed", error }),
    );
    const firstOutcome = observe(firstSocket);
    const secondOutcome = observe(secondSocket);

    firstSocket.send(JSON.stringify({ type: "auth", ticket }));
    secondSocket.send(JSON.stringify({ type: "auth", ticket }));

    const outcomes = await Promise.all([firstOutcome, secondOutcome]);
    const accepted = outcomes.filter((outcome) => outcome.kind === "message");
    const rejected = outcomes.filter((outcome) => outcome.kind === "closed");

    expect(accepted).toHaveLength(1);
    expect(accepted[0].message).toMatchObject({
      type: "market_data.status",
      providerConnected: false,
    });
    const acceptedSocket = accepted[0].socket;
    const snapshotPromise = nextJsonMessage(acceptedSocket);
    acceptedSocket.send(JSON.stringify({
      type: "market_data.subscribe", version: 1, series: canonicalSeries(SERIES_REPLAY),
    }));
    expect(await snapshotPromise).toMatchObject({
      type: "market_data.ohlcv.snapshot",
      streamId: `synthetic:${SERIES_REPLAY}`,
      highWaterCursor: "50",
    });
    expect(rejected).toHaveLength(1);
    expect(rejected[0].error.message).toMatch(/WebSocket closed before the expected message/);
  });

  it("restores serialized socket identity and resumes messages after DO eviction", async () => {
    const client = await connectAuthenticated(SERIES_HIBERNATE);
    const stub = coordinatorStub(SERIES_HIBERNATE);

    await evictDurableObject(stub);

    const restoredAttachments = await runInDurableObject(stub, async (_instance, state) => (
      state.getWebSockets().map((socket) => socket.deserializeAttachment())
    ));
    expect(restoredAttachments).toHaveLength(1);
    expect(restoredAttachments[0]).toMatchObject({
      authorized: true,
      seriesKey: SERIES_HIBERNATE,
      subject: "synthetic-proof-subject",
    });

    const pongPromise = nextJsonMessage(client.socket);
    client.socket.send(JSON.stringify({ type: "ping" }));
    expect(await pongPromise).toMatchObject({ type: "market_data.pong", version: 1 });
  });

  it("restores every authenticated socket attachment after Durable Object eviction", async () => {
    const [first, second] = await Promise.all([
      connectAuthenticated(SERIES_HIBERNATE),
      connectAuthenticated(SERIES_HIBERNATE),
    ]);
    const stub = coordinatorStub(SERIES_HIBERNATE);

    await evictDurableObject(stub);

    const attachments = await runInDurableObject(stub, async (_instance, state) => (
      state.getWebSockets().map((socket) => socket.deserializeAttachment())
    ));
    expect(attachments).toHaveLength(2);
    expect(attachments.every((attachment) => (
      attachment.authorized === true &&
      attachment.seriesKey === SERIES_HIBERNATE &&
      attachment.subject === "synthetic-proof-subject" &&
      attachment.snapshotWatermark === 50
    ))).toBe(true);

    const firstPong = nextJsonMessage(first.socket);
    const secondPong = nextJsonMessage(second.socket);
    first.socket.send(JSON.stringify({ type: "ping" }));
    second.socket.send(JSON.stringify({ type: "ping" }));
    expect(await Promise.all([firstPong, secondPong])).toEqual([
      expect.objectContaining({ type: "market_data.pong", version: 1 }),
      expect.objectContaining({ type: "market_data.pong", version: 1 }),
    ]);
    expect((await Promise.all([firstPong, secondPong])).every((pong) =>
      typeof pong.serverTimeNs === "string" && /^\d{1,32}$/.test(pong.serverTimeNs)
    )).toBe(true);
  });

  it("runs the real Durable Object alarm and closes an expired unauthenticated socket", async () => {
    const socket = await openSocket(SERIES_ALARM);
    const stub = coordinatorStub(SERIES_ALARM);

    await runInDurableObject(stub, async (_instance, state) => {
      const [serverSocket] = state.getWebSockets();
      expect(serverSocket).toBeDefined();
      const attachment = serverSocket.deserializeAttachment();
      serverSocket.serializeAttachment({
        ...attachment,
        connectedAt: Date.now() - proofLimits.unauthenticatedSocketTtlMs - 1,
      });
    });

    const closedPromise = nextClose(socket);
    expect(await runDurableObjectAlarm(stub)).toBe(true);
    const closed = await closedPromise;
    expect(closed.code).toBe(4408);
  });
  it("does not expire an authenticated socket when the authentication alarm runs", async () => {
    const client = await connectAuthenticated(SERIES_ALARM);
    // A pending unauthenticated socket keeps the authentication alarm scheduled.
    const unauthenticatedSocket = await openSocket(SERIES_ALARM);
    const stub = coordinatorStub(SERIES_ALARM);

    await runInDurableObject(stub, async (_instance, state) => {
      const sockets = state.getWebSockets();
      expect(sockets).toHaveLength(2);
      for (const serverSocket of sockets) {
        const attachment = serverSocket.deserializeAttachment();
        serverSocket.serializeAttachment({
          ...attachment,
          connectedAt: Date.now() - proofLimits.unauthenticatedSocketTtlMs - 1,
        });
      }
    });

    const unauthenticatedClose = nextClose(unauthenticatedSocket);
    expect(await runDurableObjectAlarm(stub)).toBe(true);
    expect((await unauthenticatedClose).code).toBe(4408);

    const pongPromise = nextJsonMessage(client.socket);
    client.socket.send(JSON.stringify({ type: "ping" }));
    expect(await pongPromise).toMatchObject({ type: "market_data.pong", version: 1 });
    expect(client.socket.readyState).toBe(1);
  });

  it("binds tickets to one exact series without consuming them on a wrong-series attempt", async () => {
    const ticket = await issueTicket(SERIES_A);
    const wrongSeriesSocket = await openSocket(SERIES_B);
    const rejectedPromise = nextClose(wrongSeriesSocket);
    wrongSeriesSocket.send(JSON.stringify({ type: "auth", ticket }));

    const rejected = await rejectedPromise;
    expect(rejected.code).toBe(4401);

    const validClient = await connectAuthenticated(SERIES_A, ticket);
    expect(validClient.snapshot).toMatchObject({
      type: "market_data.ohlcv.snapshot",
      streamId: `synthetic:${SERIES_A}`,
      highWaterCursor: "50",
    });
  });

  it("serializes concurrent duplicate cursor submissions before fan-out", async () => {
    const seriesKey = "synthetic:DEMO:CONCURRENT:1m";
    const client = await connectAuthenticated(seriesKey);
    const updatePromise = nextJsonMessage(client.socket);

    const results = await Promise.all([
      emit(seriesKey, 51),
      emit(seriesKey, 51),
    ]);
    const accepted = results.filter((result) => result.status === 200);
    const rejected = results.filter((result) => result.status === 409);
    expect(accepted).toHaveLength(2);
    expect(accepted.map((result) => result.payload.delivered).sort()).toEqual([0, 1]);
    expect(accepted.some((result) => result.payload.duplicate === true)).toBe(true);
    expect(rejected).toHaveLength(0);
    expect(await updatePromise).toMatchObject({
      type: "market_data.ohlcv.update",
      sequence: 51,
      cursor: "51",
    });

    const nextUpdatePromise = nextJsonMessage(client.socket);
    const contiguous = await emit(seriesKey, 52);
    expect(contiguous.status).toBe(200);
    expect(contiguous.payload).toMatchObject({
      accepted: true,
      sequence: "52",
      delivered: 1,
    });
    expect(await nextUpdatePromise).toMatchObject({
      type: "market_data.ohlcv.update",
      sequence: 52,
      cursor: "52",
    });
  });

  it("rejects duplicate and skipped cursors without fan-out, then accepts the next contiguous cursor", async () => {
    const seriesKey = "synthetic:DEMO:SEQUENCE:1m";
    const client = await connectAuthenticated(seriesKey);

    const firstUpdatePromise = nextJsonMessage(client.socket);
    const first = await emit(seriesKey, 51);
    expect(first.status).toBe(200);
    expect(first.payload).toMatchObject({ accepted: true, sequence: "51", delivered: 1 });
    expect(await firstUpdatePromise).toMatchObject({
      type: "market_data.ohlcv.update",
      sequence: 51,
      cursor: "51",
    });

    const duplicate = await emit(seriesKey, 51);
    expect(duplicate.status).toBe(200);
    expect(duplicate.payload).toMatchObject({ accepted: true, duplicate: true, sequence: "51", delivered: 0 });
    const changedTimestamp = await emit(seriesKey, 51, "1800000000000000999");
    expect(changedTimestamp.status).toBe(409);
    expect(changedTimestamp.payload).toMatchObject({ error: "sequence_conflict" });

    const skipped = await emit(seriesKey, 53);
    expect(skipped.status).toBe(409);
    expect(skipped.payload).toMatchObject({ error: "sequence_conflict" });

    await expect(nextJsonMessage(client.socket, 150)).rejects.toThrow(
      "Timed out waiting for a Durable Object WebSocket message.",
    );

    const nextUpdatePromise = nextJsonMessage(client.socket);
    const nextContiguous = await emit(seriesKey, 52);
    expect(nextContiguous.status).toBe(200);
    expect(nextContiguous.payload).toMatchObject({
      accepted: true,
      sequence: "52",
      delivered: 1,
    });
    expect(await nextUpdatePromise).toMatchObject({
      type: "market_data.ohlcv.update",
      sequence: 52,
      cursor: "52",
    });
  });

});
