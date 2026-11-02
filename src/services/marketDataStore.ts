import type { ChartData, Timeframe } from '../types';

export interface MarketSeriesIdentity {
  dataset: string;
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
  timeframe: Timeframe;
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
}

const EMPTY_SNAPSHOT: MarketDataSnapshot = Object.freeze({
  identity: null,
  status: 'demo',
  source: 'demo',
  bars: Object.freeze([]),
  detail: 'No verified backend series is selected.',
  revision: 0,
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

function validateBars(bars: readonly ChartData[]): void {
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
  if (input.identity && (
    !input.identity.dataset ||
    !input.identity.rawSymbol ||
    !Number.isSafeInteger(input.identity.publisherId) || input.identity.publisherId <= 0 ||
    !Number.isSafeInteger(input.identity.instrumentId) || input.identity.instrumentId <= 0
  )) {
    throw new Error('Market data series identity is incomplete or invalid.');
  }
  if (isBackendStatus && bars.length === 0) {
    throw new Error('Backend market data cannot be ready without validated bars.');
  }
  if (!isBackendStatus && bars.length > 0) {
    throw new Error('Non-ready market-data states cannot publish indicator bars.');
  }
  if (isBackendStatus) validateBars(bars);

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
