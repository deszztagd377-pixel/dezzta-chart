import { useMemo } from 'react';
import { calculateIndicators } from './indicatorCalculations';
import type { MarketDataSnapshot, MarketSeriesIdentity } from '../services/marketDataStore';
import { useMarketDataSeriesSnapshot } from '../services/useMarketDataSeriesSnapshot';

type IndicatorSet = ReturnType<typeof calculateIndicators>;

// The store publishes one immutable snapshot object to every panel on the same
// series. A WeakMap shares the expensive calculation across those panels and
// releases obsolete revisions automatically when snapshots become unreachable.
const indicatorCache = new WeakMap<MarketDataSnapshot, IndicatorSet>();

function indicatorsForSnapshot(snapshot: MarketDataSnapshot): IndicatorSet | null {
  if (
    snapshot.source !== 'backend' ||
    (snapshot.status !== 'ready' && snapshot.status !== 'degraded') ||
    snapshot.bars.length === 0
  ) {
    return null;
  }

  const cached = indicatorCache.get(snapshot);
  if (cached) return cached;

  const computed = calculateIndicators(snapshot.bars);
  Object.freeze(computed.sma20);
  Object.freeze(computed.ema20);
  Object.freeze(computed.rsi14);
  computed.macd.forEach((point) => Object.freeze(point));
  Object.freeze(computed.macd);
  computed.bollinger20.forEach((point) => Object.freeze(point));
  Object.freeze(computed.bollinger20);
  Object.freeze(computed);
  indicatorCache.set(snapshot, computed);
  return computed;
}

/**
 * Returns indicators only for the exact canonical series selected by the
 * owning chart panel. Panels sharing one immutable snapshot reuse one result.
 * Demo, loading, unavailable, and error states intentionally return null.
 */
export function useMarketIndicators(identity: MarketSeriesIdentity | null = null) {
  const marketData = useMarketDataSeriesSnapshot(identity);
  const indicators = useMemo(
    () => indicatorsForSnapshot(marketData),
    [marketData],
  );

  return {
    identity: marketData.identity,
    status: marketData.status,
    source: marketData.source,
    revision: marketData.revision,
    indicators,
  };
}
