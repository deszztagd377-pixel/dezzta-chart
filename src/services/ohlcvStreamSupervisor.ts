import {
  isSameMarketSeriesIdentity,
  type MarketSeriesIdentity,
} from './marketDataStore';
import {
  getMarketDataSnapshot,
  publishMarketDataSnapshot,
  publishMarketDataUpdate,
  resetMarketDataSnapshot,
} from './marketDataStore';
import { marketDataSeriesStore } from './marketDataSeriesStore';
import { requestOhlcvWebSocketTicket } from './ohlcvWebSocketTicket';
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
  extends Omit<OhlcvStreamOptions, 'ticket' | 'getRenewalTicket' | 'token' | 'onSnapshot' | 'onUpdate' | 'onStatus' | 'onError' | 'onClose' | 'onCursor' | 'onResnapshotRequired'> {
  /** Must return a fresh Firebase ID token; called again for every reconnect. */
  getIdToken: () => Promise<string>;
  /** Enables independent keyed-store ownership without touching the legacy singleton snapshot. */
  seriesScoped?: boolean;
  /** Bounds Firebase token acquisition for initial connect and ticket renewal. */
  identityTokenTimeoutMs?: number;
  requestWebSocketTicket?: (baseUrl: string, idToken: string) => Promise<string>;
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

function createRuntimeClientInstanceId(): string {
  const bytes = new Uint8Array(16);
  if (typeof globalThis.crypto !== 'undefined' &&
      typeof globalThis.crypto.getRandomValues === 'function') {
    globalThis.crypto.getRandomValues(bytes);
  } else {
    // This identifier is a stable slot label, not a credential or security token.
    for (let index = 0; index < bytes.length; index += 1) {
      bytes[index] = Math.floor(Math.random() * 256);
    }
  }
  return `runtime-${Array.from(bytes, (value) => value.toString(16).padStart(2, '0')).join('')}`;
}

// One opaque consumer identity per page runtime; the supervisor reuses it
// across transport reconnects. A native host may inject a persisted ID.
const DEFAULT_CLIENT_INSTANCE_ID = createRuntimeClientInstanceId();

// The market-data store is a singleton, so it must have exactly one active
// supervisor owner. Replacing a chart selection stops the previous owner first.
let activeSupervisorStop: (() => void) | null = null;

function resetMarketDataStores(
  identity: MarketSeriesIdentity,
  status: Parameters<typeof resetMarketDataSnapshot>[1],
  detail: string | null,
  seriesScoped = false,
): void {
  if (!seriesScoped) resetMarketDataSnapshot(identity, status, detail);
  marketDataSeriesStore.reset(identity, status, detail);
}

function publishMarketDataStores(
  input: Parameters<typeof publishMarketDataSnapshot>[0],
  seriesScoped = false,
): void {
  if (!seriesScoped) publishMarketDataSnapshot(input);
  if (input.identity) {
    marketDataSeriesStore.publishSnapshot({
      identity: input.identity,
      status: input.status,
      bars: input.bars,
      detail: input.detail,
    });
  }
}

function publishMarketDataUpdates(
  input: Parameters<typeof publishMarketDataUpdate>[0],
  seriesScoped = false,
): void {
  if (!seriesScoped) publishMarketDataUpdate(input);
  marketDataSeriesStore.publishUpdate(input);
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
  const clientInstanceId = options.clientInstanceId ?? DEFAULT_CLIENT_INSTANCE_ID;
  if (!/^[A-Za-z0-9._:-]{1,128}$/.test(clientInstanceId)) {
    throw new Error('OHLCV client instance ID is invalid.');
  }
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
  const identityTokenTimeoutMs = options.identityTokenTimeoutMs ?? 10_000;
  if (!Number.isFinite(identityTokenTimeoutMs) || identityTokenTimeoutMs <= 0 || identityTokenTimeoutMs > 60_000) {
    throw new Error('Firebase ID-token timeout must be positive and no greater than 60 seconds.');
  }
  const seriesScoped = options.seriesScoped === true;
  // Legacy consumers retain the historical single-owner behavior. Series-scoped
  // supervisors are independently owned by canonical series and never reset
  // another series' chart state.
  if (!seriesScoped) activeSupervisorStop?.();

  const pendingIdentityRequests = new Set<() => void>();
  const getFreshIdToken = (): Promise<string> => new Promise((resolve, reject) => {
    let settled = false;
    let cancelRequest = () => {};
    let timer: ReturnType<typeof setTimeout>;
    const finish = (complete: () => void) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      pendingIdentityRequests.delete(cancelRequest);
      complete();
    };
    cancelRequest = () => finish(() => reject(new Error('Firebase ID-token request was cancelled because the stream stopped.')));
    pendingIdentityRequests.add(cancelRequest);
    timer = setTimeout(
      () => finish(() => reject(new Error('Firebase ID-token request timed out.'))),
      identityTokenTimeoutMs,
    );
    let tokenRequest: Promise<string>;
    try {
      // Preserve the existing eager request behavior while still bounding its
      // completion time. The promise handlers remain attached after timeout
      // so a late rejection cannot become an unhandled rejection.
      tokenRequest = options.getIdToken();
    } catch (error) {
      finish(() => reject(error));
      return;
    }
    void Promise.resolve(tokenRequest).then(
      (token) => finish(() => resolve(token)),
      (error) => finish(() => reject(error)),
    );
  });

  const setStatus = (next: OhlcvSupervisorStatus) => {
    currentStatus = next;
    try {
      options.onStatus?.(next);
    } catch {
      // UI/diagnostic observers must not interrupt reconnect or stop lifecycle.
    }
  };
  const reportError = (error: Error) => {
    try {
      const observer = options.onError;
      observer?.(error);
    } catch {
      // Error reporting is best-effort; supervisor recovery must continue.
    }
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
      const token = await getFreshIdToken();
      if (stopped) return;
      if (typeof token !== 'string' || token.trim().length === 0) {
        // An empty credential is an authentication/session state, not a
        // transient transport failure. Retrying it forever only hammers the
        // identity provider; wait for a new session/supervisor instead.
        stopped = true;
        resetMarketDataStores(
          options.identity,
          'unavailable',
          'No valid Firebase ID token is available. Sign in again before reconnecting.',
          seriesScoped,
        );
        setStatus('stopped');
        reportError(new Error('Identity provider returned an empty ID token.'));
        return;
      }
      const issueTicket = options.requestWebSocketTicket ?? requestOhlcvWebSocketTicket;
      const getTicket = async () => {
        const freshIdToken = await getFreshIdToken();
        if (typeof freshIdToken !== 'string' || !freshIdToken.trim()) throw new Error('A fresh Firebase ID token is required for WebSocket ticket renewal.');
        return issueTicket(options.baseUrl, freshIdToken);
      };
      const ticket = await issueTicket(options.baseUrl, token);
      if (stopped) return;
      connection = connectOhlcvStream({
        ...options,
        clientInstanceId,
        ticket,
        getRenewalTicket: getTicket,
        resumeCursor,
        onCursor: (cursor) => {
          resumeCursor = cursor;
        },
        onResnapshotRequired: () => {
          // A failed replay/live handoff must not retry from the same stale
          // cursor. The next connection requests a full snapshot; its cursor
          // becomes the new resume point only after client validation.
          resumeCursor = undefined;
        },
        onSnapshot: (snapshot, candles) => {
          if (stopped) return;
          if (snapshot.state === 'unavailable' || candles.length === 0) {
            resetMarketDataStores(
              options.identity,
              'unavailable',
              snapshot.detail ?? 'The authenticated stream has no validated bars yet.',
              seriesScoped,
            );
          } else {
            publishMarketDataStores({
              identity: options.identity,
              status: snapshot.state,
              bars: candles,
              detail: snapshot.detail,
            }, seriesScoped);
          }
          attempt = 0;
          setStatus('subscribed');
        },
        onUpdate: (_event, candle) => {
          if (stopped) return;
          if (_event.cursor !== undefined) resumeCursor = _event.cursor;
          const current = seriesScoped
            ? marketDataSeriesStore.peekSnapshot(options.identity)
            : getMarketDataSnapshot();
          if (current.source === 'backend' && isSameMarketSeriesIdentity(current.identity, options.identity)) {
            publishMarketDataUpdates({ identity: options.identity, bar: candle }, seriesScoped);
          } else {
            // A valid stream may produce its first bar after an empty snapshot.
            // Seed the store with that validated event rather than rejecting it.
            publishMarketDataStores({
              identity: options.identity,
              status: 'degraded',
              bars: [candle],
              detail: 'Streaming bars received; awaiting a complete snapshot window.',
            }, seriesScoped);
          }
        },
        onStatus: (status) => {
          if (stopped) return;
          if (status === 'authenticated') setStatus('authenticated');
          if (status === 'subscribed') {
            // A validated replay completion is just as healthy as a fresh
            // snapshot. Reset backoff here too, otherwise a later outage after
            // replay recovery inherits the previous failure streak.
            attempt = 0;
            setStatus('subscribed');
          }
          if (status === 'closed') connection = null;
        },
        onError: (error) => {
          if (stopped) return;
          reportError(error);
          // Wait for the socket's authoritative close event before opening a replacement.
          // Scheduling here can race a delayed close and briefly overlap two sockets.
          setStatus('reconnecting');
        },
        onClose: (code, reason) => {
          if (stopped) return;
          connection = null;
          // Authentication, authorization, malformed-subscription, and
          // protocol-policy closes are terminal until the user/session/
          // selection changes. Backend close 1008 covers unsupported client
          // control frames and ping-rate violations; reconnecting unchanged
          // would repeat the same policy violation indefinitely.
          if (code === 1008 || code === 4400 || code === 4401 || code === 4403) {
            stopped = true;
            if (reconnectTimer !== null) clearTimeout(reconnectTimer);
            reconnectTimer = null;
            const originRejected = code === 4403 && /origin not allowed/i.test(reason);
            const closeDetail = code === 1008
              ? 'The server rejected the WebSocket protocol policy. Check client protocol and ping rate before reconnecting.'
              : code === 4401
                ? 'Firebase authentication was rejected. Sign in again to restore access.'
                : code === 4403
                  ? originRejected
                    ? 'The WebSocket Origin is not allowlisted by the backend. Check the configured frontend origin.'
                    : 'The account is not entitled to this instrument or its access was revoked.'
                  : 'The server rejected the subscription request. Check the selected instrument and timeframe.';
            resetMarketDataStores(options.identity, 'unavailable', closeDetail, seriesScoped);
            setStatus('stopped');
            reportError(new Error(
              code === 1008 ? 'Market-data WebSocket protocol policy rejected (1008).' :
              code === 4401 ? 'Market-data authentication rejected (4401).' :
              code === 4403
                ? originRejected
                  ? 'Market-data WebSocket Origin rejected (4403).'
                  : 'Market-data entitlement denied (4403).' :
              'Market-data subscription rejected (4400).',
            ));
            return;
          }
          scheduleReconnect();
        },
      });
    } catch (error) {
      if (!stopped) {
        if ((error as { status?: number } | null)?.status === 401) {
          stopped = true;
          resetMarketDataStores(
            options.identity,
            'unavailable',
            'Firebase authentication was rejected. Sign in again before reconnecting.',
            seriesScoped,
          );
          setStatus('stopped');
          reportError(new Error('Market-data WebSocket ticket authentication rejected (401).'));
        } else {
          reportError(error instanceof Error ? error : new Error('OHLCV connection failed.'));
          reconnectAfterAttempt = true;
        }
      }
    } finally {
      connecting = false;
      // scheduleReconnect() intentionally refuses to run while a connection
      // attempt is active. Defer this failure path until the attempt releases
      // that lock, otherwise token-provider/network setup failures stall forever.
      if (reconnectAfterAttempt) scheduleReconnect();
    }
  };

  resetMarketDataStores(options.identity, 'loading', 'Authenticating the OHLCV stream.', seriesScoped);
  void connect();

  const supervisor: OhlcvStreamSupervisor = {
    stop() {
      if (stopped) return;
      stopped = true;
      for (const cancelRequest of [...pendingIdentityRequests]) cancelRequest();
      if (reconnectTimer !== null) clearTimeout(reconnectTimer);
      reconnectTimer = null;
      const active = connection;
      connection = null;
      active?.close();
      // A superseded supervisor must never clear or overwrite the new
      // selection's shared snapshot when its cleanup runs later.
      if (seriesScoped) {
        resetMarketDataStores(options.identity, 'unavailable', 'OHLCV stream stopped.', true);
        setStatus('stopped');
      } else if (activeSupervisorStop === supervisor.stop) {
        activeSupervisorStop = null;
        resetMarketDataStores(options.identity, 'unavailable', 'OHLCV stream stopped.');
        setStatus('stopped');
      } else {
        currentStatus = 'stopped';
      }
    },
    get status() {
      return currentStatus;
    },
  };
  if (!seriesScoped) activeSupervisorStop = supervisor.stop;
  return supervisor;
}
