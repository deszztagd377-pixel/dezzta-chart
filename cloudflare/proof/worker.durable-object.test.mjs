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

async function connectAuthenticated(seriesKey, suppliedTicket) {
  const ticket = suppliedTicket ?? await issueTicket(seriesKey);
  const socket = await openSocket(seriesKey);
  const snapshotPromise = nextJsonMessage(socket);
  socket.send(JSON.stringify({ type: "auth", ticket }));
  const snapshot = await snapshotPromise;
  expect(snapshot).toMatchObject({
    type: "market_data.snapshot",
    version: 1,
    watermarkCursor: "50",
    dataSource: "synthetic_only_not_market_data",
  });
  expect(snapshot.bars).toHaveLength(50);
  return { socket, ticket, snapshot };
}

function coordinatorStub(seriesKey) {
  return env.SERIES_COORDINATOR.get(
    env.SERIES_COORDINATOR.idFromName(seriesKey),
  );
}

async function emit(seriesKey, sequence) {
  const response = await workerFetch("/__proof/emit", {
    method: "POST",
    headers: workerHeaders(),
    body: JSON.stringify({ seriesKey, sequence: String(sequence) }),
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
      type: "market_data.update",
      sequence: "51",
      dataSource: "synthetic_only_not_market_data",
    });
    expect(secondUpdate).toMatchObject({
      type: "market_data.update",
      sequence: "51",
      dataSource: "synthetic_only_not_market_data",
    });
    expect(otherSeries.socket.readyState).toBe(1);
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
    expect(await pongPromise).toMatchObject({ type: "pong", version: 1 });
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
});
