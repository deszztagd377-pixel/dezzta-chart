import type { OhlcvSnapshotMessage } from '../types/ohlcv';
import { parseOhlcvSnapshot, toChartCandles, type OhlcvSeriesIdentity } from '../utils/ohlcvAdapter';
import {
  OhlcvStreamSequenceGuard,
  parseOhlcvStreamUpdate,
  type OhlcvStreamUpdateMessage,
} from './ohlcvStreamProtocol';
import type { ChartData } from '../types';
import { getBucketPolicyForTimeframe } from '../utils/ohlcvBucketPolicy';

export interface OhlcvStreamOptions {
  baseUrl: string;
  identity: OhlcvSeriesIdentity;
  canonicalInstrumentId: string;
  token: string;
  resumeCursor?: string;
  onCursor?: (cursor: string) => void;
  onSnapshot: (snapshot: OhlcvSnapshotMessage, candles: ChartData[]) => void;
  onUpdate: (event: OhlcvStreamUpdateMessage, candle: ChartData) => void;
  onStatus?: (status: 'connecting' | 'authenticated' | 'subscribed' | 'closed') => void;
  onError?: (error: Error) => void;
  onClose?: (code: number, reason: string) => void;
  webSocketFactory?: (url: string) => WebSocket;
  timeoutMs?: number;
}

export interface OhlcvStreamConnection {
  close(): void;
  readonly state: 'connecting' | 'authenticated' | 'subscribed' | 'closed';
}

function buildWebSocketUrl(baseUrl: string): string {
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
  base.protocol = base.protocol === 'https:' ? 'wss:' : 'ws:';
  base.pathname = '/ws/market-data';
  base.search = '';
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
  if (!options.token.trim()) throw new Error('A verified identity token is required.');
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

  const factory = options.webSocketFactory ?? ((url: string) => new WebSocket(url));
  const socket = factory(buildWebSocketUrl(options.baseUrl));
  let state: OhlcvStreamConnection['state'] = 'connecting';
  let guard: OhlcvStreamSequenceGuard | null = null;
  let replayExpectedCount: number | null = null;
  let replayReceivedCount = 0;
  let replayEndCursor: string | null = null;
  let timer: ReturnType<typeof setTimeout> | null = setTimeout(() => {
    fail(new Error('OHLCV WebSocket handshake timed out.'));
  }, timeoutMs);

  const setState = (next: OhlcvStreamConnection['state']) => {
    state = next;
    options.onStatus?.(next);
  };
  const clearTimer = () => {
    if (timer !== null) clearTimeout(timer);
    timer = null;
  };
  const fail = (error: Error) => {
    clearTimer();
    options.onError?.(error);
    if (socket.readyState === 1 || socket.readyState === 0) {
      socket.close(1011, 'OHLCV stream protocol error');
    }
    setState('closed');
  };

  const refreshHandshakeTimer = () => {
    clearTimer();
    timer = setTimeout(() => {
      fail(new Error('OHLCV WebSocket replay/snapshot handshake timed out.'));
    }, timeoutMs);
  };

  socket.addEventListener('open', () => {
    if (state !== 'connecting') return;
    socket.send(JSON.stringify({ type: 'auth', token: options.token }));
  });

  socket.addEventListener('message', (message) => {
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
        refreshHandshakeTimer();
        setState('authenticated');
        socket.send(JSON.stringify({
          type: 'market_data.subscribe',
          version: 1,
          canonicalInstrumentId: options.canonicalInstrumentId,
          ...(options.resumeCursor !== undefined ? { cursor: options.resumeCursor } : {}),
          series: {
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
        if (typeof value.reason !== 'string' || typeof value.snapshotCursor !== 'string' ||
            !/^\d+$/.test(value.snapshotCursor)) {
          throw new Error('OHLCV resnapshot instruction is invalid.');
        }
        replayExpectedCount = null;
        replayReceivedCount = 0;
        replayEndCursor = null;
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
          BigInt(value.throughCursor) < BigInt(value.fromCursor)
        ) {
          throw new Error('OHLCV replay start message is invalid.');
        }
        guard = new OhlcvStreamSequenceGuard(
          value.streamId,
          {
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
          0,
        );
        replayExpectedCount = value.count as number;
        replayReceivedCount = 0;
        replayEndCursor = value.throughCursor;
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
          guard.watermark !== replayExpectedCount
        ) {
          throw new Error('OHLCV replay completion does not match the replayed event sequence.');
        }
        options.onCursor?.(value.cursor);
        replayExpectedCount = null;
        replayEndCursor = null;
        clearTimer();
        setState('subscribed');
        return;
      }

      if (value.type === 'market_data.ohlcv.snapshot' && state === 'authenticated') {
        const parsed = snapshotFromSocket(value);
        if (replayExpectedCount !== null) throw new Error('Snapshot arrived before replay completed.');
        const candles = toChartCandles(parsed.snapshot, options.identity);
        if (parsed.cursor !== undefined) options.onCursor?.(parsed.cursor);
        guard = new OhlcvStreamSequenceGuard(
          parsed.streamId,
          {
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
        return;
      }

      if (value.type === 'market_data.ohlcv.update' &&
          (state === 'subscribed' || replayExpectedCount !== null)) {
        if (!guard) throw new Error('OHLCV stream update arrived before its snapshot.');
        if (replayExpectedCount !== null && replayReceivedCount >= replayExpectedCount) {
          throw new Error('OHLCV replay delivered more events than declared.');
        }
        const event = parseOhlcvStreamUpdate(value);
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
        if (replayExpectedCount !== null) {
          replayReceivedCount += 1;
          refreshHandshakeTimer();
        }
        return;
      }

      if (value.type === 'market_data.pong') return;
      if (value.type === 'market_data.status' && state !== 'connecting') return;
      throw new Error(`Unexpected OHLCV WebSocket message in state ${state}.`);
    } catch (error) {
      fail(error instanceof Error ? error : new Error('OHLCV WebSocket protocol error.'));
    }
  });

  socket.addEventListener('error', () => {
    if (state !== 'closed') fail(new Error('OHLCV WebSocket transport error.'));
  });
  socket.addEventListener('close', (event) => {
    clearTimer();
    const closeEvent = event as CloseEvent;
    options.onClose?.(closeEvent.code, closeEvent.reason);
    if (state !== 'closed') setState('closed');
  });

  return {
    close() {
      clearTimer();
      if (socket.readyState === 1 || socket.readyState === 0) {
        socket.close(1000, 'Client closed OHLCV stream');
      }
      setState('closed');
    },
    get state() {
      return state;
    },
  };
}
