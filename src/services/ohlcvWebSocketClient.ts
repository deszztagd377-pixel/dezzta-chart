import type { OhlcvSnapshotMessage } from '../types/ohlcv';
import { parseOhlcvSnapshot, toChartCandles, type OhlcvSeriesIdentity } from '../utils/ohlcvAdapter';
import {
  OhlcvStreamSequenceGuard,
  parseOhlcvStreamUpdate,
  type OhlcvStreamUpdateMessage,
} from './ohlcvStreamProtocol';
import type { ChartData } from '../types';

export interface OhlcvStreamOptions {
  baseUrl: string;
  identity: OhlcvSeriesIdentity;
  canonicalInstrumentId: string;
  token: string;
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
} {
  if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
    throw new Error('OHLCV WebSocket snapshot must be an object.');
  }
  const value = payload as Record<string, unknown>;
  if (
    typeof value.streamId !== 'string' || !value.streamId ||
    !Number.isSafeInteger(value.watermark) ||
    (value.watermark as number) < 0
  ) {
    throw new Error('OHLCV WebSocket snapshot is missing a valid stream watermark.');
  }
  const snapshot = parseOhlcvSnapshot(value);
  return { snapshot, streamId: value.streamId, watermark: value.watermark as number };
}

/**
 * Authenticated snapshot-plus-stream transport. It deliberately does not retry
 * or silently accept sequence gaps: callers close and reconnect to obtain a
 * new atomic snapshot/watermark after a gap or server-directed resnapshot.
 */
export function connectOhlcvStream(options: OhlcvStreamOptions): OhlcvStreamConnection {
  if (!options.token.trim()) throw new Error('A verified identity token is required.');
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
        clearTimer();
        timer = setTimeout(() => {
          fail(new Error('OHLCV WebSocket snapshot handshake timed out.'));
        }, timeoutMs);
        setState('authenticated');
        socket.send(JSON.stringify({
          type: 'market_data.subscribe',
          version: 1,
          canonicalInstrumentId: options.canonicalInstrumentId,
          series: {
            dataset: options.identity.dataset,
            publisherId: options.identity.publisherId,
            instrumentId: options.identity.instrumentId,
            rawSymbol: options.identity.rawSymbol,
            timeframe: options.identity.timeframe,
            bucketPolicy: options.identity.bucketPolicy ?? 'UTC_LEGACY',
            calendarId: options.identity.calendarId ?? '',
            calendarVersion: options.identity.calendarVersion ?? '',
          },
        }));
        return;
      }

      if (value.type === 'market_data.ohlcv.snapshot' && state === 'authenticated') {
        const parsed = snapshotFromSocket(value);
        const candles = toChartCandles(parsed.snapshot, options.identity);
        guard = new OhlcvStreamSequenceGuard(
          parsed.streamId,
          {
            dataset: options.identity.dataset,
            publisherId: options.identity.publisherId,
            instrumentId: options.identity.instrumentId,
            rawSymbol: options.identity.rawSymbol,
            timeframe: options.identity.timeframe,
            bucketPolicy: options.identity.bucketPolicy ?? 'UTC_LEGACY',
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

      if (value.type === 'market_data.ohlcv.update' && state === 'subscribed') {
        if (!guard) throw new Error('OHLCV stream update arrived before its snapshot.');
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
