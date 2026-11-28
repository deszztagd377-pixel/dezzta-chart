import type { OhlcvSnapshotMessage } from '../types/ohlcv';
import { parseOhlcvSnapshot, toChartCandles, type OhlcvSeriesIdentity } from '../utils/ohlcvAdapter';
import {
  OhlcvStreamSequenceGuard,
  parseOhlcvStreamUpdate,
  verifyOhlcvStreamEventDigest,
  type OhlcvStreamUpdateMessage,
} from './ohlcvStreamProtocol';
import type { ChartData } from '../types';
import { getBucketPolicyForTimeframe } from '../utils/ohlcvBucketPolicy';

export interface OhlcvStreamOptions {
  baseUrl: string;
  identity: OhlcvSeriesIdentity;
  canonicalInstrumentId: string;
  ticket: string;
  getRenewalTicket: () => Promise<string>;
  ticketRenewalIntervalMs?: number;
  resumeCursor?: string;
  onCursor?: (cursor: string) => void;
  /** Clears the reconnect cursor when the server requires a fresh snapshot. */
  onResnapshotRequired?: (snapshotCursor: string) => void;
  onSnapshot: (snapshot: OhlcvSnapshotMessage, candles: ChartData[]) => void;
  onUpdate: (event: OhlcvStreamUpdateMessage, candle: ChartData) => void;
  onStatus?: (status: 'connecting' | 'authenticated' | 'subscribed' | 'closed') => void;
  onError?: (error: Error) => void;
  onClose?: (code: number, reason: string) => void;
  webSocketFactory?: (url: string) => WebSocket;
  timeoutMs?: number;
  /** Send a text ping after subscription to keep idle sessions active. */
  heartbeatIntervalMs?: number;
  /** Close the stream if the server does not answer a heartbeat. */
  heartbeatTimeoutMs?: number;
  /** Coalesce durable consumer ACKs; only active when the server advertises ACK protocol v1. */
  consumerAckBatchIntervalMs?: number;
}

export interface OhlcvStreamConnection {
  close(): void;
  readonly state: 'connecting' | 'authenticated' | 'subscribed' | 'closed';
}

function buildWebSocketUrl(baseUrl: string, seriesKey?: string): string {
  if (!baseUrl.trim()) throw new Error('Market-data backend URL is not configured.');
  let base: URL;
  try {
    base = new URL(baseUrl);
  } catch {
    throw new Error('Market-data backend URL is invalid.');
  }
  if (!['http:', 'https:'].includes(base.protocol) || base.username || base.password) {
    throw new Error('Market-data backend URL must use HTTP(S) without embedded credentials.');
  }
  if (import.meta.env.PROD && base.protocol !== 'https:') {
    throw new Error('Production market-data WebSocket connections must use HTTPS/WSS.');
  }
  base.protocol = base.protocol === 'https:' ? 'wss:' : 'ws:';
  base.pathname = '/ws/market-data';
  base.search = '';
  if (seriesKey !== undefined) {
    if (!/^[A-Za-z0-9._:-]{1,128}$/.test(seriesKey)) {
      throw new Error('Market-data WebSocket seriesKey is invalid.');
    }
    base.searchParams.set('seriesKey', seriesKey);
  }
  base.hash = '';
  return base.toString();
}

function snapshotFromSocket(payload: unknown): {
  snapshot: OhlcvSnapshotMessage;
  streamId: string;
  watermark: number;
  cursor?: string;
} {
  if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
    throw new Error('OHLCV WebSocket snapshot must be an object.');
  }
  const value = payload as Record<string, unknown>;
  if (
    typeof value.streamId !== 'string' || !value.streamId ||
    !Number.isSafeInteger(value.watermark) ||
    (value.watermark as number) < 0 ||
    (value.cursor !== undefined && (typeof value.cursor !== 'string' || !/^\d+$/.test(value.cursor)))
  ) {
    throw new Error('OHLCV WebSocket snapshot is missing a valid stream watermark.');
  }
  const snapshot = parseOhlcvSnapshot(value);
  return {
    snapshot,
    streamId: value.streamId,
    watermark: value.watermark as number,
    ...(typeof value.cursor === 'string' ? { cursor: value.cursor } : {}),
  };
}

/**
 * Authenticated snapshot-plus-stream transport. It deliberately does not retry
 * or silently accept sequence gaps: callers close and reconnect to obtain a
 * new atomic snapshot/watermark after a gap or server-directed resnapshot.
 */
export function connectOhlcvStream(options: OhlcvStreamOptions): OhlcvStreamConnection {
  if (!options.ticket.trim()) throw new Error('A short-lived WebSocket ticket is required.');
  if (options.resumeCursor !== undefined && !/^\d+$/.test(options.resumeCursor)) {
    throw new Error('OHLCV resume cursor must be an unsigned decimal string.');
  }
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(options.canonicalInstrumentId)) {
    throw new Error('A validated canonical instrument UUID is required.');
  }
  const timeoutMs = options.timeoutMs ?? 10_000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new Error('WebSocket handshake timeout must be positive.');
  }
  const heartbeatIntervalMs = options.heartbeatIntervalMs ?? 20_000;
  const heartbeatTimeoutMs = options.heartbeatTimeoutMs ?? 10_000;
  if (!Number.isFinite(heartbeatIntervalMs) || heartbeatIntervalMs < 1_000 ||
      !Number.isFinite(heartbeatTimeoutMs) || heartbeatTimeoutMs < 1_000 ||
      heartbeatTimeoutMs >= heartbeatIntervalMs) {
    throw new Error('OHLCV WebSocket heartbeat bounds are invalid.');
  }
  const consumerAckBatchIntervalMs = options.consumerAckBatchIntervalMs ?? 10_000;
  if (!Number.isFinite(consumerAckBatchIntervalMs) || consumerAckBatchIntervalMs < 1_000 ||
      consumerAckBatchIntervalMs > 30_000) {
    throw new Error('OHLCV consumer ACK batch interval is outside safe bounds.');
  }

  const factory = options.webSocketFactory ?? ((url: string) => new WebSocket(url));
  const socket = factory(buildWebSocketUrl(options.baseUrl, options.identity.seriesKey));
  let state: OhlcvStreamConnection['state'] = 'connecting';
  let guard: OhlcvStreamSequenceGuard | null = null;
  let replayExpectedCount: number | null = null;
  let replayReceivedCount = 0;
  let replayEndCursor: string | null = null;
  let replayEndSequence: number | null = null;
  // A server-directed fallback snapshot must be anchored to the exact durable
  // cursor advertised by resnapshot_required; never accept a different watermark.
  let expectedResnapshotCursor: string | null = null;
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  let pongTimer: ReturnType<typeof setTimeout> | null = null;
  let ticketRenewalTimer: ReturnType<typeof setTimeout> | null = null;
  let renewalAckTimer: ReturnType<typeof setTimeout> | null = null;
  let renewalPending = false;
  let consumerAckEnabled = false;
  let pendingConsumerAck: { sequence: number; eventDigest: string } | null = null;
  let consumerAckTimer: ReturnType<typeof setTimeout> | null = null;
  let consumerAckResponseTimer: ReturnType<typeof setTimeout> | null = null;
  let consumerAckInFlightSequence: number | null = null;
  let lastConsumerAckSequence = 0;
  let timer: ReturnType<typeof setTimeout> | null = setTimeout(() => {
    fail(new Error('OHLCV WebSocket handshake timed out.'));
  }, timeoutMs);

  const setState = (next: OhlcvStreamConnection['state']) => {
    state = next;
    try {
      options.onStatus?.(next);
    } catch {
      // Status observers are diagnostic/UI hooks and must not break transport state.
    }
  };
  let closeNotified = false;
  const notifyClose = (code: number, reason: string) => {
    if (closeNotified) return;
    closeNotified = true;
    try {
      options.onClose?.(code, reason);
    } catch {
      // Close observers are best-effort and must not interrupt lifecycle recovery.
    }
  };
  const clearTimer = () => {
    if (timer !== null) clearTimeout(timer);
    timer = null;
  };
  const clearHeartbeat = () => {
    if (heartbeatTimer !== null) clearInterval(heartbeatTimer);
    if (pongTimer !== null) clearTimeout(pongTimer);
    heartbeatTimer = null;
    pongTimer = null;
  };
  const clearTicketRenewal = () => {
    if (ticketRenewalTimer !== null) clearTimeout(ticketRenewalTimer);
    if (renewalAckTimer !== null) clearTimeout(renewalAckTimer);
    ticketRenewalTimer = null;
    renewalAckTimer = null;
    renewalPending = false;
  };
  const clearConsumerAck = () => {
    if (consumerAckTimer !== null) clearTimeout(consumerAckTimer);
    if (consumerAckResponseTimer !== null) clearTimeout(consumerAckResponseTimer);
    consumerAckTimer = null;
    consumerAckResponseTimer = null;
    pendingConsumerAck = null;
    consumerAckInFlightSequence = null;
  };
  const startHeartbeat = () => {
    if (heartbeatTimer !== null || state !== 'subscribed') return;
    heartbeatTimer = setInterval(() => {
      if (state !== 'subscribed' || socket.readyState !== 1) return;
      if (pongTimer !== null) {
        fail(new Error('OHLCV WebSocket heartbeat pong timed out.'));
        return;
      }
      try {
        // The server protocol expects the literal text frame "ping".
        socket.send('ping');
        pongTimer = setTimeout(() => {
          pongTimer = null;
          fail(new Error('OHLCV WebSocket heartbeat pong timed out.'));
        }, heartbeatTimeoutMs);
      } catch {
        fail(new Error('OHLCV WebSocket heartbeat send failed.'));
      }
    }, heartbeatIntervalMs);
  };
  const fail = (error: Error) => {
    clearTimer();
    clearHeartbeat();
    clearTicketRenewal();
    clearConsumerAck();
    // Diagnostic observers must never interrupt transport cleanup. A consumer
    // callback can throw; isolate that exception so the socket still closes
    // and the connection state always reaches the terminal state.
    try {
      options.onError?.(error);
    } catch {
      // Error reporting is best-effort; lifecycle cleanup is mandatory.
    }
    let closeRequestFailed = false;
    if (socket.readyState === 1 || socket.readyState === 0) {
      try {
        socket.close(1011, 'OHLCV stream protocol error');
      } catch {
        // A browser/socket implementation may reject close during teardown.
        // Keep the local state terminal even when the close request throws.
        closeRequestFailed = true;
      }
    }
    if (state !== 'closed') setState('closed');
    // Preserve normal close-event ordering while the socket is still open or
    // closing. If close() throws, or the platform already reports CLOSED
    // before its close event is delivered, notify the supervisor synthetically.
    if (closeRequestFailed || socket.readyState === 3) {
      notifyClose(
        1011,
        closeRequestFailed ? 'OHLCV stream failure' : 'OHLCV stream ended before close event',
      );
    }
  };

  const flushConsumerAck = () => {
    if (!consumerAckEnabled || !pendingConsumerAck || consumerAckInFlightSequence !== null ||
        state === 'closed' || socket.readyState !== 1) return;
    const next = pendingConsumerAck;
    pendingConsumerAck = null;
    consumerAckInFlightSequence = next.sequence;
    try {
      socket.send(JSON.stringify({
        type: 'market_data.ack',
        version: 1,
        sequence: next.sequence,
        eventDigest: next.eventDigest,
      }));
    } catch {
      fail(new Error('OHLCV durable consumer ACK send failed.'));
      return;
    }
    consumerAckResponseTimer = setTimeout(() => {
      consumerAckResponseTimer = null;
      fail(new Error('OHLCV durable consumer ACK acknowledgement timed out.'));
    }, 10_000);
  };
  const queueConsumerAck = (event: OhlcvStreamUpdateMessage) => {
    if (!consumerAckEnabled) return;
    if (!event.generationId || !event.digest) {
      throw new Error('ACK-capable OHLCV server omitted generationId or event digest.');
    }
    if (event.sequence <= lastConsumerAckSequence) return;
    if (!pendingConsumerAck || event.sequence > pendingConsumerAck.sequence) {
      pendingConsumerAck = { sequence: event.sequence, eventDigest: event.digest };
    }
    // During replay, wait until replay_complete confirms the whole range was sent.
    if (replayExpectedCount !== null || consumerAckInFlightSequence !== null || consumerAckTimer !== null) return;
    consumerAckTimer = setTimeout(() => {
      consumerAckTimer = null;
      flushConsumerAck();
    }, consumerAckBatchIntervalMs);
  };

  const scheduleTicketRenewal = () => {
    clearTicketRenewal();
    if (state !== 'subscribed') return;
    const interval = options.ticketRenewalIntervalMs ?? 45_000;
    if (!Number.isFinite(interval) || interval < 5_000 || interval > 60_000) {
      fail(new Error('WebSocket ticket renewal interval is outside safe bounds.'));
      return;
    }
    ticketRenewalTimer = setTimeout(() => {
      ticketRenewalTimer = null;
      void (async () => {
        try {
          const renewedTicket = await options.getRenewalTicket();
          if (state !== 'subscribed' || socket.readyState !== 1) return;
          if (typeof renewedTicket !== 'string' || renewedTicket.length < 40 || renewedTicket.length > 128) throw new Error('WebSocket ticket renewal returned an invalid ticket.');
          renewalPending = true;
          socket.send(JSON.stringify({ type: 'auth.renew', ticket: renewedTicket }));
          renewalAckTimer = setTimeout(() => { renewalAckTimer = null; fail(new Error('WebSocket ticket renewal acknowledgement timed out.')); }, 10_000);
        } catch (error) {
          // Closing the connection while renewal is pending is an intentional
          // lifecycle transition. Ignore its late rejection instead of
          // reporting a transport failure after teardown.
          if (state !== 'subscribed') return;
          if ((error as { status?: number } | null)?.status === 401) {
            clearTimer(); clearHeartbeat(); clearTicketRenewal();
            let closeFailed = false;
            if (socket.readyState === 1 || socket.readyState === 0) { try { socket.close(4401, 'Authentication expired or revoked'); } catch { closeFailed = true; } }
            if (state !== 'closed') setState('closed');
            if (closeFailed || socket.readyState === 3) notifyClose(4401, 'Authentication expired or revoked');
            return;
          }
          fail(error instanceof Error ? error : new Error('WebSocket ticket renewal failed.'));
        }
      })();
    }, interval);
  };

  const refreshHandshakeTimer = () => {
    clearTimer();
    timer = setTimeout(() => {
      fail(new Error('OHLCV WebSocket replay/snapshot handshake timed out.'));
    }, timeoutMs);
  };

  socket.addEventListener('open', () => {
    if (state !== 'connecting') return;
    try {
      socket.send(JSON.stringify({ type: 'auth', ticket: options.ticket }));
    } catch {
      fail(new Error('OHLCV WebSocket authentication send failed.'));
    }
  });

  let messageQueue: Promise<void> = Promise.resolve();
  const processMessage = async (message: Event) => {
    if (state === 'closed') return;
    let payload: unknown;
    try {
      payload = JSON.parse(String(message.data));
    } catch {
      fail(new Error('OHLCV WebSocket sent invalid JSON.'));
      return;
    }

    if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
      fail(new Error('OHLCV WebSocket message must be an object.'));
      return;
    }
    const value = payload as Record<string, unknown>;

    try {
      if (value.type === 'market_data.status' && state === 'connecting') {
        if (value.consumerAckProtocolVersion !== undefined && value.consumerAckProtocolVersion !== 1) {
          throw new Error('Server advertised an unsupported consumer ACK protocol version.');
        }
        consumerAckEnabled = value.consumerAckProtocolVersion === 1;
        refreshHandshakeTimer();
        setState('authenticated');
        socket.send(JSON.stringify({
          type: 'market_data.subscribe',
          version: 1,
          canonicalInstrumentId: options.canonicalInstrumentId,
          ...(options.resumeCursor !== undefined ? { cursor: options.resumeCursor } : {}),
          series: {
            ...(options.identity.seriesKey !== undefined ? { seriesKey: options.identity.seriesKey } : {}),
            provider: options.identity.provider ?? 'databento',
            seriesType: options.identity.seriesType ?? 'contract',
            dataset: options.identity.dataset,
            publisherId: options.identity.publisherId,
            instrumentId: options.identity.instrumentId,
            rawSymbol: options.identity.rawSymbol,
            timeframe: options.identity.timeframe,
            bucketPolicy: options.identity.bucketPolicy ?? getBucketPolicyForTimeframe(options.identity.timeframe),
            calendarId: options.identity.calendarId ?? '',
            calendarVersion: options.identity.calendarVersion ?? '',
          },
        }));
        return;
      }

      if (value.type === 'market_data.ohlcv.resnapshot_required' && state === 'authenticated') {
        if (typeof value.reason !== 'string' || value.reason.trim().length === 0 ||
            typeof value.snapshotCursor !== 'string' || !/^\d+$/.test(value.snapshotCursor)) {
          throw new Error('OHLCV resnapshot instruction is invalid.');
        }
        replayExpectedCount = null;
        replayReceivedCount = 0;
        replayEndCursor = null;
        replayEndSequence = null;
        expectedResnapshotCursor = value.snapshotCursor;
        options.onResnapshotRequired?.(value.snapshotCursor);
        return;
      }

      if (value.type === 'market_data.ohlcv.replay_started' && state === 'authenticated') {
        if (
          (typeof value.streamId !== 'string' || value.streamId.trim().length === 0) ||
          !Number.isSafeInteger(value.count) ||
          (value.count as number) < 0 ||
          typeof value.fromCursor !== 'string' ||
          !/^\d+$/.test(value.fromCursor) ||
          typeof value.throughCursor !== 'string' ||
          !/^\d+$/.test(value.throughCursor) ||
          (options.resumeCursor !== undefined &&
            BigInt(value.fromCursor) !== BigInt(options.resumeCursor)) ||
          BigInt(value.throughCursor) < BigInt(value.fromCursor) ||
          (value.fromSequence !== undefined &&
            (!Number.isSafeInteger(value.fromSequence) || (value.fromSequence as number) < 0)) ||
          (value.throughSequence !== undefined &&
            (!Number.isSafeInteger(value.throughSequence) || (value.throughSequence as number) < 0))
        ) {
          throw new Error('OHLCV replay start message is invalid.');
        }
        const resolvedFromSequence = (value.fromSequence as number | undefined) ?? 0;
        const resolvedThroughSequence = (value.throughSequence as number | undefined) ??
          resolvedFromSequence + (value.count as number);
        if (!Number.isSafeInteger(resolvedThroughSequence) ||
            resolvedThroughSequence < resolvedFromSequence ||
            resolvedThroughSequence - resolvedFromSequence !== value.count) {
          throw new Error('OHLCV replay sequence bounds do not match its event count.');
        }
        guard = new OhlcvStreamSequenceGuard(
          value.streamId,
          {
            ...(options.identity.seriesKey !== undefined ? { seriesKey: options.identity.seriesKey } : {}),
            provider: options.identity.provider ?? 'databento',
            seriesType: options.identity.seriesType ?? 'contract',
            dataset: options.identity.dataset,
            publisherId: options.identity.publisherId,
            instrumentId: options.identity.instrumentId,
            rawSymbol: options.identity.rawSymbol,
            timeframe: options.identity.timeframe,
            bucketPolicy: options.identity.bucketPolicy ?? getBucketPolicyForTimeframe(options.identity.timeframe),
            calendarId: options.identity.calendarId ?? '',
            calendarVersion: options.identity.calendarVersion ?? '',
          },
          resolvedFromSequence,
        );
        replayExpectedCount = value.count as number;
        replayReceivedCount = 0;
        replayEndCursor = value.throughCursor;
        replayEndSequence = resolvedThroughSequence;
        refreshHandshakeTimer();
        return;
      }

      if (value.type === 'market_data.ohlcv.replay_complete' && state === 'authenticated') {
        if (
          replayExpectedCount === null ||
          !Number.isSafeInteger(value.count) ||
          value.count !== replayExpectedCount ||
          replayReceivedCount !== replayExpectedCount ||
          typeof value.cursor !== 'string' ||
          value.cursor !== replayEndCursor ||
          !guard ||
          guard.watermark !== replayEndSequence ||
          (value.throughSequence !== undefined &&
            value.throughSequence !== replayEndSequence)
        ) {
          throw new Error('OHLCV replay completion does not match the replayed event sequence.');
        }
        options.onCursor?.(value.cursor);
        replayExpectedCount = null;
        replayEndCursor = null;
        replayEndSequence = null;
        clearTimer();
        setState('subscribed');
        startHeartbeat();
        scheduleTicketRenewal();
        if (pendingConsumerAck && consumerAckInFlightSequence === null) {
          if (consumerAckTimer !== null) clearTimeout(consumerAckTimer);
          consumerAckTimer = null;
          flushConsumerAck();
        }
        return;
      }

      if (value.type === 'market_data.ohlcv.snapshot' && state === 'authenticated') {
        const parsed = snapshotFromSocket(value);
        if (replayExpectedCount !== null) throw new Error('Snapshot arrived before replay completed.');
        if (expectedResnapshotCursor !== null && parsed.cursor !== expectedResnapshotCursor) {
          throw new Error('OHLCV replacement snapshot cursor does not match the server resnapshot watermark.');
        }
        expectedResnapshotCursor = null;
        const candles = toChartCandles(parsed.snapshot, options.identity);
        if (parsed.cursor !== undefined) options.onCursor?.(parsed.cursor);
        guard = new OhlcvStreamSequenceGuard(
          parsed.streamId,
          {
            ...(options.identity.seriesKey !== undefined ? { seriesKey: options.identity.seriesKey } : {}),
            provider: options.identity.provider ?? 'databento',
            seriesType: options.identity.seriesType ?? 'contract',
            dataset: options.identity.dataset,
            publisherId: options.identity.publisherId,
            instrumentId: options.identity.instrumentId,
            rawSymbol: options.identity.rawSymbol,
            timeframe: options.identity.timeframe,
            bucketPolicy: options.identity.bucketPolicy ?? getBucketPolicyForTimeframe(options.identity.timeframe),
            calendarId: options.identity.calendarId ?? '',
            calendarVersion: options.identity.calendarVersion ?? '',
          },
          parsed.watermark,
        );
        // The timeout protects only the auth + initial snapshot handshake.
        // Once the atomic snapshot is accepted, a healthy long-lived stream
        // must not be closed by the expired handshake timer.
        clearTimer();
        options.onSnapshot(parsed.snapshot, candles);
        setState('subscribed');
        startHeartbeat();
        scheduleTicketRenewal();
        return;
      }

      if (value.type === 'market_data.ohlcv.update' &&
          (state === 'subscribed' || replayExpectedCount !== null)) {
        if (!guard) throw new Error('OHLCV stream update arrived before its snapshot.');
        if (replayExpectedCount !== null && replayReceivedCount >= replayExpectedCount) {
          throw new Error('OHLCV replay delivered more events than declared.');
        }
        const event = parseOhlcvStreamUpdate(value);
        if (consumerAckEnabled && (!event.generationId || !event.digest)) {
          throw new Error('ACK-capable OHLCV server omitted generationId or event digest.');
        }
        if (event.digest !== undefined && !(await verifyOhlcvStreamEventDigest(event))) {
          throw new Error('OHLCV stream event SHA-256 digest verification failed.');
        }
        const decision = guard.accept(event);
        if (!decision.accepted) {
          throw new Error(
            decision.reason === 'gap'
              ? `OHLCV stream sequence gap: expected ${decision.expectedSequence}, received ${decision.receivedSequence}. Reconnect and resnapshot.`
              : `OHLCV stream rejected ${decision.reason} event.`,
          );
        }
        const singleSnapshot = parseOhlcvSnapshot({
          type: 'market_data.ohlcv.snapshot',
          version: 1,
          state: 'ready',
          timestampUnit: 'nanoseconds',
          priceRepresentation: 'decimal-string',
          bars: [event.bar],
          detail: null,
        });
        const candle = toChartCandles(singleSnapshot, options.identity)[0];
        if (!candle) throw new Error('OHLCV update did not contain the subscribed series.');
        options.onUpdate(event, candle);
        if (event.cursor !== undefined) options.onCursor?.(event.cursor);
        queueConsumerAck(event);
        if (replayExpectedCount !== null) {
          replayReceivedCount += 1;
          refreshHandshakeTimer();
        }
        return;
      }

      if (value.type === 'market_data.acknowledged') {
        if (!consumerAckEnabled || consumerAckInFlightSequence === null || value.version !== 1 ||
            value.accepted !== true || typeof value.committedCursor !== 'string' ||
            !/^\d+$/.test(value.committedCursor) || Number(value.committedCursor) !== consumerAckInFlightSequence ||
            !Number.isSafeInteger(value.receiptVersion) || (value.receiptVersion as number) < 1 ||
            typeof value.duplicate !== 'boolean') {
          throw new Error('Unexpected or invalid durable consumer ACK acknowledgement.');
        }
        if (consumerAckResponseTimer !== null) clearTimeout(consumerAckResponseTimer);
        consumerAckResponseTimer = null;
        lastConsumerAckSequence = consumerAckInFlightSequence;
        consumerAckInFlightSequence = null;
        if (pendingConsumerAck && pendingConsumerAck.sequence > lastConsumerAckSequence && consumerAckTimer === null) {
          consumerAckTimer = setTimeout(() => {
            consumerAckTimer = null;
            flushConsumerAck();
          }, consumerAckBatchIntervalMs);
        }
        return;
      }

      if (value.type === 'market_data.ack_rejected') {
        if (!consumerAckEnabled || consumerAckInFlightSequence === null || value.version !== 1 ||
            typeof value.reason !== 'string' || !value.reason.trim()) {
          throw new Error('Unexpected or invalid durable consumer ACK rejection.');
        }
        throw new Error(`Server rejected durable consumer ACK: ${value.reason}`);
      }

      if (value.type === 'market_data.auth.renewed') {
        if (state !== 'subscribed' || !renewalPending || value.version !== 1) throw new Error('Unexpected WebSocket authentication renewal acknowledgement.');
        if (renewalAckTimer !== null) clearTimeout(renewalAckTimer);
        renewalAckTimer = null;
        renewalPending = false;
        scheduleTicketRenewal();
        return;
      }

      if (value.type === 'market_data.pong') {
        if (state !== 'subscribed' || pongTimer === null || value.version !== 1) {
          throw new Error('Unexpected or invalid OHLCV WebSocket heartbeat pong.');
        }
        clearTimeout(pongTimer);
        pongTimer = null;
        return;
      }
      if (value.type === 'market_data.status' && state !== 'connecting') return;
      throw new Error(`Unexpected OHLCV WebSocket message in state ${state}.`);
    } catch (error) {
      fail(error instanceof Error ? error : new Error('OHLCV WebSocket protocol error.'));
    }
  };

  socket.addEventListener('message', (message) => {
    // Web Crypto verification is asynchronous; serialize frames so a later
    // update cannot overtake an earlier update while its digest is checked.
    messageQueue = messageQueue.then(() => processMessage(message)).catch((error) => {
      fail(error instanceof Error ? error : new Error('OHLCV WebSocket message processing failed.'));
    });
  });

  socket.addEventListener('error', () => {
    if (state !== 'closed') fail(new Error('OHLCV WebSocket transport error.'));
  });
  socket.addEventListener('close', (event) => {
    clearTimer();
    clearHeartbeat();
    clearTicketRenewal();
    clearConsumerAck();
    const closeEvent = event as CloseEvent;
    if (state !== 'closed') setState('closed');
    notifyClose(closeEvent.code, closeEvent.reason);
  });

  return {
    close() {
      clearTimer();
      clearHeartbeat();
      clearTicketRenewal();
      clearConsumerAck();
      let closeRequestFailed = false;
      if (socket.readyState === 1 || socket.readyState === 0) {
        try {
          socket.close(1000, 'Client closed OHLCV stream');
        } catch {
          // Local shutdown remains terminal even if the platform rejects close().
          closeRequestFailed = true;
        }
      }
      if (state !== 'closed') setState('closed');
      // Match fail(): callers must not wait forever for a native close event
      // when the platform rejects close() or the socket is already CLOSED.
      if (closeRequestFailed || socket.readyState === 3) {
        notifyClose(
          1006,
          closeRequestFailed ? 'Client close request failed' : 'Client closed after transport ended',
        );
      }
    },
    get state() {
      return state;
    },
  };
}
