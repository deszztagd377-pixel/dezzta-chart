import { useMemo } from 'react';
import { calculateIndicators } from './indicatorCalculations';
import type { MarketSeriesIdentity } from '../services/marketDataStore';
import { useMarketDataSeriesSnapshot } from '../services/useMarketDataSeriesSnapshot';

/**
 * Returns indicators only for the exact canonical series selected by the
 * owning chart panel. Demo, loading, unavailable, and error states return null.
 */
export function useMarketIndicators(identity: MarketSeriesIdentity | null = null) {
  const marketData = useMarketDataSeriesSnapshot(identity);
  const indicators = useMemo(() => {
    if (
      marketData.source !== 'backend' ||
      (marketData.status !== 'ready' && marketData.status !== 'degraded') ||
      marketData.bars.length === 0
    ) {
      return null;
    }
    return calculateIndicators(marketData.bars);
  }, [marketData]);

  return {
    identity: marketData.identity,
    status: marketData.status,
    source: marketData.source,
    revision: marketData.revision,
    indicators,
  };
}
