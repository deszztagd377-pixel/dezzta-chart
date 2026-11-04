import type { MarketSeriesIdentity } from './marketDataStore';
import {
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
  extends Omit<OhlcvStreamOptions, 'token' | 'onSnapshot' | 'onUpdate' | 'onStatus' | 'onError'> {
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
    setStatus('reconnecting');
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      void connect();
    }, delay);
  };

  const connect = async (): Promise<void> => {
    if (stopped || connecting) return;
    connecting = true;
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
          options.onStatus?.('subscribed');
        },
        onUpdate: (_event, candle) => {
          if (stopped) return;
          publishMarketDataUpdate({ identity: options.identity, bar: candle });
        },
        onStatus: (status) => {
          if (stopped) return;
          if (status === 'authenticated') setStatus('authenticated');
          if (status === 'subscribed') setStatus('subscribed');
          if (status === 'closed') {
            connection = null;
            scheduleReconnect();
          }
        },
        onError: (error) => {
          if (stopped) return;
          options.onError?.(error);
          scheduleReconnect();
        },
      });
    } catch (error) {
      if (!stopped) {
        options.onError?.(error instanceof Error ? error : new Error('OHLCV connection failed.'));
        scheduleReconnect();
      }
    } finally {
      connecting = false;
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
