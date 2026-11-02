import { useMemo } from 'react';
import { calculateIndicators } from './indicatorCalculations';
import { useMarketDataSnapshot } from '../services/useMarketDataSnapshot';

/**
 * Returns indicator series only for the exact validated backend snapshot.
 * DEMO, loading, unavailable, and error states intentionally produce null.
 */
export function useMarketIndicators() {
  const marketData = useMarketDataSnapshot();
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
