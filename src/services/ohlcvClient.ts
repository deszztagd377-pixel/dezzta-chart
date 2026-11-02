import type { ChartData } from '../types';
import type { OhlcvSnapshotMessage } from '../types/ohlcv';
import { parseOhlcvSnapshot, toChartCandles, type OhlcvSeriesIdentity } from '../utils/ohlcvAdapter';

export type OhlcvRequestErrorCode =
  | 'configuration'
  | 'cancelled'
  | 'timeout'
  | 'network'
  | 'http'
  | 'invalid_json'
  | 'invalid_snapshot'
  | 'unrepresentable';

export class OhlcvRequestError extends Error {
  readonly code: OhlcvRequestErrorCode;
  readonly statusCode?: number;

  constructor(code: OhlcvRequestErrorCode, message: string, statusCode?: number) {
    super(message);
    this.name = 'OhlcvRequestError';
    this.code = code;
    this.statusCode = statusCode;
  }
}

export interface FetchOhlcvOptions {
  /** Backend origin or API base path; never a provider credential. */
  baseUrl: string;
  identity: OhlcvSeriesIdentity;
  signal?: AbortSignal;
  timeoutMs?: number;
  limit?: number;
  fetchImpl?: typeof fetch;
}

export interface OhlcvFetchResult {
  status: 'ready' | 'degraded' | 'unavailable';
  snapshot: OhlcvSnapshotMessage;
  candles: ChartData[];
  detail: string | null;
}

function buildSnapshotUrl(baseUrl: string, identity: OhlcvSeriesIdentity, limit?: number): URL {
  if (typeof baseUrl !== 'string' || baseUrl.trim() === '') {
    throw new OhlcvRequestError('configuration', 'OHLCV backend URL is not configured.');
  }

  let url: URL;
  try {
    const normalizedBase = baseUrl.trim().replace(/\/+$/, '');
    url = new URL('v1/ohlcv', `${normalizedBase}/`);
  } catch {
    throw new OhlcvRequestError('configuration', 'OHLCV backend URL is invalid.');
  }

  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) {
    throw new OhlcvRequestError('configuration', 'OHLCV backend URL must use HTTP(S) without embedded credentials.');
  }
  if (
    !identity.dataset ||
    !identity.rawSymbol ||
    !Number.isSafeInteger(identity.publisherId) ||
    identity.publisherId <= 0 ||
    !Number.isSafeInteger(identity.instrumentId) ||
    identity.instrumentId <= 0
  ) {
    throw new OhlcvRequestError('configuration', 'A complete, verified OHLCV series identity is required.');
  }
  if (limit !== undefined && (!Number.isSafeInteger(limit) || limit < 1 || limit > 5000)) {
    throw new OhlcvRequestError('configuration', 'OHLCV limit must be an integer between 1 and 5000.');
  }

  url.searchParams.set('dataset', identity.dataset);
  url.searchParams.set('publisher_id', String(identity.publisherId));
  url.searchParams.set('instrument_id', String(identity.instrumentId));
  url.searchParams.set('raw_symbol', identity.rawSymbol);
  url.searchParams.set('timeframe', identity.timeframe);
  if (limit !== undefined) url.searchParams.set('limit', String(limit));
  return url;
}

function getResultStatus(snapshot: OhlcvSnapshotMessage, candleCount: number): OhlcvFetchResult['status'] {
  if (snapshot.state === 'unavailable' || candleCount === 0) return 'unavailable';
  if (snapshot.state === 'degraded') return 'degraded';
  if (snapshot.feedState !== undefined && snapshot.feedState !== 'live') return 'degraded';
  return 'ready';
}

/**
 * Fetch one exact OHLCV series from the read-only backend endpoint.
 * Transport precision is validated before conversion to chart-engine numbers.
 * No retries or demo-data substitution occur in this function.
 */
export async function fetchOhlcvSnapshot(options: FetchOhlcvOptions): Promise<OhlcvFetchResult> {
  const timeoutMs = options.timeoutMs ?? 8000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new OhlcvRequestError('configuration', 'OHLCV timeout must be a positive finite number.');
  }
  if (options.signal?.aborted) {
    throw new OhlcvRequestError('cancelled', 'OHLCV request was cancelled.');
  }

  const url = buildSnapshotUrl(options.baseUrl, options.identity, options.limit);
  const requestFetch = options.fetchImpl ?? fetch;
  const controller = new AbortController();
  let timedOut = false;
  const onExternalAbort = () => controller.abort();
  options.signal?.addEventListener('abort', onExternalAbort, { once: true });

  const timeout = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  try {
    const response = await requestFetch(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new OhlcvRequestError('http', `OHLCV backend returned HTTP ${response.status}.`, response.status);
    }

    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      throw new OhlcvRequestError('invalid_json', 'OHLCV backend response is not valid JSON.');
    }

    let snapshot: OhlcvSnapshotMessage;
    let candles: ChartData[];
    try {
      snapshot = parseOhlcvSnapshot(payload);
      candles = toChartCandles(snapshot, options.identity);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown snapshot validation error.';
      throw new OhlcvRequestError('invalid_snapshot', `OHLCV snapshot validation failed: ${message}`);
    }

    const status = getResultStatus(snapshot, candles.length);
    return {
      status,
      snapshot,
      candles,
      detail: snapshot.detail ?? (
        status === 'unavailable' ? 'No validated bars match the requested instrument and timeframe.' :
        status === 'degraded' ? 'Bars are available, but the feed is not confirmed live.' :
        null
      ),
    };
  } catch (error) {
    if (error instanceof OhlcvRequestError) throw error;
    if (timedOut) {
      throw new OhlcvRequestError('timeout', `OHLCV request exceeded the ${timeoutMs} ms timeout.`);
    }
    if (options.signal?.aborted) {
      throw new OhlcvRequestError('cancelled', 'OHLCV request was cancelled.');
    }
    const message = error instanceof Error ? error.message : 'Unknown network error.';
    throw new OhlcvRequestError('network', `Unable to reach the OHLCV backend: ${message}`);
  } finally {
    clearTimeout(timeout);
    options.signal?.removeEventListener('abort', onExternalAbort);
  }
}
