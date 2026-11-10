import type { MarketSeriesIdentity } from './marketDataStore';
import { getBucketPolicyForTimeframe } from '../utils/ohlcvBucketPolicy';
import {
  getMarketDataSnapshot,
  publishMarketDataSnapshot,
  publishMarketDataUpdate,
  resetMarketDataSnapshot,
} from './marketDataStore';
import {
  connectOhlcvStream,
  type OhlcvStreamConnection,
  type OhlcvStreamOptions,
} from './ohlcvWebSocketClient';

export type OhlcvSupervisorStatus =
  | 'connecting'
  | 'authenticated'
  | 'subscribed'
  | 'reconnecting'
  | 'stopped';

export interface OhlcvStreamSupervisorOptions
  extends Omit<OhlcvStreamOptions, 'token' | 'onSnapshot' | 'onUpdate' | 'onStatus' | 'onError' | 'onClose' | 'onCursor'> {
  /** Must return a fresh Firebase ID token; called again for every reconnect. */
  getIdToken: () => Promise<string>;
  minReconnectDelayMs?: number;
  maxReconnectDelayMs?: number;
  random?: () => number;
  onStatus?: (status: OhlcvSupervisorStatus) => void;
  onError?: (error: Error) => void;
}

export interface OhlcvStreamSupervisor {
  stop(): void;
  readonly status: OhlcvSupervisorStatus;
}

function sameIdentity(left: MarketSeriesIdentity | null, right: MarketSeriesIdentity): boolean {
  return left !== null &&
    (left.provider ?? 'databento') === (right.provider ?? 'databento') &&
    (left.seriesType ?? 'contract') === (right.seriesType ?? 'contract') &&
    left.dataset === right.dataset &&
    left.publisherId === right.publisherId &&
    left.instrumentId === right.instrumentId &&
    left.rawSymbol === right.rawSymbol &&
    left.timeframe === right.timeframe &&
    (left.bucketPolicy ?? getBucketPolicyForTimeframe(left.timeframe)) === (right.bucketPolicy ?? getBucketPolicyForTimeframe(right.timeframe)) &&
    (left.calendarId ?? '') === (right.calendarId ?? '') &&
    (left.calendarVersion ?? '') === (right.calendarVersion ?? '');
}

/**
 * Owns the authenticated stream lifecycle and bridges validated events into
 * the shared market-data store. A fresh ID token is requested for every
 * connection attempt. Sequence gaps/protocol failures cause a clean
 * reconnect; the transport obtains a new snapshot + watermark before updates
 * are accepted again.
 */
export function startOhlcvStreamSupervisor(
  options: OhlcvStreamSupervisorOptions,
): OhlcvStreamSupervisor {
  const minDelay = options.minReconnectDelayMs ?? 500;
  const maxDelay = options.maxReconnectDelayMs ?? 15_000;
  const random = options.random ?? Math.random;
  if (!Number.isFinite(minDelay) || minDelay < 1 ||
      !Number.isFinite(maxDelay) || maxDelay < minDelay) {
    throw new Error('OHLCV reconnect delay bounds are invalid.');
  }

  let currentStatus: OhlcvSupervisorStatus = 'connecting';
  let stopped = false;
  let connecting = false;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let connection: OhlcvStreamConnection | null = null;
  let attempt = 0;
  let resumeCursor = options.resumeCursor;

  const setStatus = (next: OhlcvSupervisorStatus) => {
    currentStatus = next;
    options.onStatus?.(next);
  };

  const scheduleReconnect = () => {
    if (stopped || connecting || reconnectTimer !== null) return;
    const exponential = Math.min(maxDelay, minDelay * (2 ** Math.min(attempt, 20)));
    const jitter = 0.5 + Math.min(1, Math.max(0, random())) * 0.5;
    const delay = Math.max(1, Math.floor(exponential * jitter));
    attempt += 1;
    // Preserve the last validated chart state while reconnecting. The next
    // socket resumes from its durable cursor; only an explicit resnapshot
    // response replaces the local window.
    setStatus('reconnecting');
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      void connect();
    }, delay);
  };

  const connect = async (): Promise<void> => {
    if (stopped || connecting) return;
    connecting = true;
    let reconnectAfterAttempt = false;
    setStatus('connecting');
    try {
      const token = await options.getIdToken();
      if (stopped) return;
      if (typeof token !== 'string' || token.trim().length === 0) {
        throw new Error('Identity provider returned an empty ID token.');
      }
      connection = connectOhlcvStream({
        ...options,
        token,
        resumeCursor,
        onCursor: (cursor) => {
          resumeCursor = cursor;
        },
        onSnapshot: (snapshot, candles) => {
          if (stopped) return;
          if (snapshot.state === 'unavailable' || candles.length === 0) {
            resetMarketDataSnapshot(
              options.identity,
              'unavailable',
              snapshot.detail ?? 'The authenticated stream has no validated bars yet.',
            );
          } else {
            publishMarketDataSnapshot({
              identity: options.identity,
              status: snapshot.state,
              bars: candles,
              detail: snapshot.detail,
            });
          }
          attempt = 0;
          setStatus('subscribed');
        },
        onUpdate: (_event, candle) => {
          if (stopped) return;
          if (_event.cursor !== undefined) resumeCursor = _event.cursor;
          const current = getMarketDataSnapshot();
          if (current.source === 'backend' && sameIdentity(current.identity, options.identity)) {
            publishMarketDataUpdate({ identity: options.identity, bar: candle });
          } else {
            // A valid stream may produce its first bar after an empty snapshot.
            // Seed the store with that validated event rather than rejecting it.
            publishMarketDataSnapshot({
              identity: options.identity,
              status: 'degraded',
              bars: [candle],
              detail: 'Streaming bars received; awaiting a complete snapshot window.',
            });
          }
        },
        onStatus: (status) => {
          if (stopped) return;
          if (status === 'authenticated') setStatus('authenticated');
          if (status === 'subscribed') setStatus('subscribed');
          if (status === 'closed') connection = null;
        },
        onError: (error) => {
          if (stopped) return;
          options.onError?.(error);
          scheduleReconnect();
        },
        onClose: (code, reason) => {
          if (stopped) return;
          connection = null;
          // Authentication, authorization, and malformed-subscription closes
          // are terminal until the user/session/selection changes. Retrying
          // these codes would create a needless reconnect loop.
          if (code === 4400 || code === 4401 || code === 4403) {
            stopped = true;
            if (reconnectTimer !== null) clearTimeout(reconnectTimer);
            reconnectTimer = null;
            resetMarketDataSnapshot(
              options.identity,
              'unavailable',
              code === 4401
                ? 'Firebase authentication was rejected. Sign in again to restore access.'
                : code === 4403
                  ? 'The account is not entitled to this instrument or its access was revoked.'
                  : 'The server rejected the subscription request. Check the selected instrument and timeframe.',
            );
            setStatus('stopped');
            options.onError?.(new Error(
              code === 4401 ? 'Market-data authentication rejected (4401).' :
              code === 4403 ? 'Market-data entitlement denied (4403).' :
              'Market-data subscription rejected (4400).',
            ));
            return;
          }
          scheduleReconnect();
        },
      });
    } catch (error) {
      if (!stopped) {
        options.onError?.(error instanceof Error ? error : new Error('OHLCV connection failed.'));
        reconnectAfterAttempt = true;
      }
    } finally {
      connecting = false;
      // scheduleReconnect() intentionally refuses to run while a connection
      // attempt is active. Defer this failure path until the attempt releases
      // that lock, otherwise token-provider/network setup failures stall forever.
      if (reconnectAfterAttempt) scheduleReconnect();
    }
  };

  resetMarketDataSnapshot(options.identity, 'loading', 'Authenticating the OHLCV stream.');
  void connect();

  return {
    stop() {
      if (stopped) return;
      stopped = true;
      if (reconnectTimer !== null) clearTimeout(reconnectTimer);
      reconnectTimer = null;
      const active = connection;
      connection = null;
      active?.close();
      resetMarketDataSnapshot(options.identity, 'unavailable', 'OHLCV stream stopped.');
      setStatus('stopped');
    },
    get status() {
      return currentStatus;
    },
  };
}
