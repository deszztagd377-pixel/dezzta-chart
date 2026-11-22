import type { ChartData, Timeframe } from '../types';
import { getBucketPolicyForTimeframe } from '../utils/ohlcvBucketPolicy';

export interface MarketSeriesIdentity {
  provider?: string;
  seriesType?: 'contract' | 'continuous';
  dataset: string;
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
  timeframe: Timeframe;
  bucketPolicy?: 'UTC_LEGACY' | 'UTC_FIXED_V1';
  calendarId?: string;
  calendarVersion?: string;
}

/**
 * Stable, collision-safe key for one canonical market-data series.
 * Defaults are normalized so omitted and explicit default metadata identify
 * the same series. Keep this helper as the single identity comparison contract
 * for the store and every transport owner.
 */
export function getMarketSeriesIdentityKey(identity: MarketSeriesIdentity): string {
  return JSON.stringify([
    identity.provider ?? 'databento',
    identity.seriesType ?? 'contract',
    identity.dataset,
    identity.publisherId,
    identity.instrumentId,
    identity.rawSymbol,
    identity.timeframe,
    identity.bucketPolicy ?? getBucketPolicyForTimeframe(identity.timeframe),
    identity.calendarId ?? '',
    identity.calendarVersion ?? '',
  ]);
}

export function isSameMarketSeriesIdentity(
  left: MarketSeriesIdentity | null,
  right: MarketSeriesIdentity,
): boolean {
  return left !== null &&
    getMarketSeriesIdentityKey(left) === getMarketSeriesIdentityKey(right);
}

export type MarketDataStatus =
  | 'demo'
  | 'loading'
  | 'ready'
  | 'degraded'
  | 'unavailable'
  | 'error';

export interface MarketDataSnapshot {
  readonly identity: Readonly<MarketSeriesIdentity> | null;
  readonly status: MarketDataStatus;
  readonly source: 'backend' | 'demo' | 'none';
  readonly bars: readonly Readonly<ChartData>[];
  readonly detail: string | null;
  readonly revision: number;
  readonly lastChange: Readonly<{ type: 'snapshot' } | { type: 'update'; bar: Readonly<ChartData> }>;
}

const EMPTY_SNAPSHOT: MarketDataSnapshot = Object.freeze({
  identity: null,
  status: 'demo',
  source: 'demo',
  bars: Object.freeze([]),
  detail: 'No verified backend series is selected.',
  revision: 0,
  lastChange: Object.freeze({ type: 'snapshot' }),
});

let currentSnapshot = EMPTY_SNAPSHOT;
const listeners = new Set<() => void>();

export function getMarketDataSnapshot(): MarketDataSnapshot {
  return currentSnapshot;
}

export function subscribeMarketData(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function validateMarketSeriesIdentity(identity: MarketSeriesIdentity): void {
  if (
    typeof identity.dataset !== 'string' || !identity.dataset.trim() ||
    typeof identity.rawSymbol !== 'string' || !identity.rawSymbol.trim() ||
    !Number.isSafeInteger(identity.publisherId) || identity.publisherId <= 0 ||
    !Number.isSafeInteger(identity.instrumentId) || identity.instrumentId <= 0
  ) {
    throw new Error('Market data series identity is incomplete or invalid.');
  }

  const provider = identity.provider ?? 'databento';
  if (typeof provider !== 'string' || !provider.trim()) {
    throw new Error('Market data provider identity is invalid.');
  }
  const seriesType = identity.seriesType ?? 'contract';
  if (seriesType !== 'contract' && seriesType !== 'continuous') {
    throw new Error('Market data series type is unsupported.');
  }
  // Resolve the timeframe even when an explicit bucket policy is supplied,
  // so malformed runtime values cannot bypass the supported-timeframe guard.
  const defaultBucketPolicy = getBucketPolicyForTimeframe(identity.timeframe);
  const bucketPolicy = identity.bucketPolicy ?? defaultBucketPolicy;
  if (bucketPolicy !== 'UTC_LEGACY' && bucketPolicy !== 'UTC_FIXED_V1') {
    throw new Error('Market data bucket policy is unsupported by the frontend.');
  }

  const calendarId = identity.calendarId ?? '';
  const calendarVersion = identity.calendarVersion ?? '';
  if (
    typeof calendarId !== 'string' ||
    typeof calendarVersion !== 'string' ||
    calendarId.trim() ||
    calendarVersion.trim()
  ) {
    throw new Error(
      'Exchange calendar metadata cannot be used until a session-aware bucket policy is supported.',
    );
  }
}

export function validateMarketDataBars(bars: readonly ChartData[]): void {
  let previousTimestamp = -Infinity;
  bars.forEach((bar, index) => {
    if (!Number.isSafeInteger(bar.timestamp) || bar.timestamp < 0) {
      throw new Error(`Market bar ${index} has an invalid UTC timestamp.`);
    }
    if (![bar.open, bar.high, bar.low, bar.close, bar.volume].every(Number.isFinite)) {
      throw new Error(`Market bar ${index} contains a non-finite value.`);
    }
    if (
      bar.volume < 0 ||
      bar.high < bar.low ||
      bar.high < Math.max(bar.open, bar.close) ||
      bar.low > Math.min(bar.open, bar.close)
    ) {
      throw new Error(`Market bar ${index} violates OHLCV boundaries.`);
    }
    if (bar.timestamp <= previousTimestamp) {
      throw new Error('Market bars must be strictly chronological.');
    }
    previousTimestamp = bar.timestamp;
  });
}

function emit(): void {
  listeners.forEach((listener) => listener());
}

/**
 * Single in-memory source of truth shared by the chart and indicator consumers.
 * Only validated backend bars are published; DEMO candles never enter this store.
 */
export function publishMarketDataSnapshot(input: {
  identity: MarketSeriesIdentity | null;
  status: MarketDataStatus;
  bars?: readonly ChartData[];
  detail?: string | null;
}): void {
  const bars = input.bars ?? [];
  const isBackendStatus = input.status === 'ready' || input.status === 'degraded';

  if (isBackendStatus && !input.identity) {
    throw new Error('Backend market data requires an exact series identity.');
  }
  if (input.identity) validateMarketSeriesIdentity(input.identity);
  if (isBackendStatus && bars.length === 0) {
    throw new Error('Backend market data cannot be ready without validated bars.');
  }
  if (!isBackendStatus && bars.length > 0) {
    throw new Error('Non-ready market-data states cannot publish indicator bars.');
  }
  if (isBackendStatus) validateMarketDataBars(bars);

  const identity = input.identity ? Object.freeze({ ...input.identity }) : null;
  const immutableBars = Object.freeze(
    bars.map((bar) => Object.freeze({ ...bar })),
  );

  currentSnapshot = Object.freeze({
    identity,
    status: input.status,
    source: isBackendStatus ? 'backend' : input.status === 'demo' ? 'demo' : 'none',
    bars: immutableBars,
    detail: input.detail ?? null,
    revision: currentSnapshot.revision + 1,
    lastChange: Object.freeze({ type: 'snapshot' }),
  });
  emit();
}



/**
 * Apply one already transport-validated backend candle revision to the shared
 * series. The WebSocket sequence guard must run before this function; this
 * store independently enforces exact-series ownership and candle invariants.
 *
 * Existing timestamps are replaced (including an open-candle revision).
 * Previously unseen timestamps are inserted chronologically, so late
 * corrections cannot corrupt ordering or leak across contract/timeframe
 * switches. DEMO/loading/unavailable snapshots are never update targets.
 */
export function publishMarketDataUpdate(input: {
  identity: MarketSeriesIdentity;
  bar: ChartData;
}): void {
  validateMarketSeriesIdentity(input.identity);
  const current = currentSnapshot;
  if (
    current.source !== 'backend' ||
    (current.status !== 'ready' && current.status !== 'degraded') ||
    current.identity === null
  ) {
    throw new Error('Incremental market updates require an active backend snapshot.');
  }
  if (!isSameMarketSeriesIdentity(current.identity, input.identity)) {
    throw new Error('Incremental market update does not match the active series identity.');
  }

  validateMarketDataBars([input.bar]);

  const nextBars = [...current.bars];
  let low = 0;
  let high = nextBars.length;
  while (low < high) {
    const middle = low + Math.floor((high - low) / 2);
    if (nextBars[middle].timestamp < input.bar.timestamp) low = middle + 1;
    else high = middle;
  }

  if (low < nextBars.length && nextBars[low].timestamp === input.bar.timestamp) {
    nextBars[low] = input.bar;
  } else {
    nextBars.splice(low, 0, input.bar);
  }

  validateMarketDataBars(nextBars);
  const immutableBars = Object.freeze(
    nextBars.map((bar) => Object.freeze({ ...bar })),
  );
  currentSnapshot = Object.freeze({
    ...current,
    bars: immutableBars,
    revision: current.revision + 1,
    lastChange: Object.freeze({ type: 'update', bar: Object.freeze({ ...input.bar }) }),
  });
  emit();
}

/** Clear series data immediately when the selected contract/timeframe changes. */
export function resetMarketDataSnapshot(
  identity: MarketSeriesIdentity | null,
  status: MarketDataStatus,
  detail: string | null,
): void {
  publishMarketDataSnapshot({ identity, status, bars: [], detail });
}
