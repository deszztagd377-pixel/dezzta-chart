import { useCallback, useSyncExternalStore } from 'react';
import {
  getMarketSeriesIdentityKey,
  type MarketDataSnapshot,
  type MarketSeriesIdentity,
} from './marketDataStore';
import { marketDataSeriesStore } from './marketDataSeriesStore';

const EMPTY_SERIES_SNAPSHOT: MarketDataSnapshot = Object.freeze({
  identity: null,
  status: 'demo',
  source: 'demo',
  bars: Object.freeze([]),
  detail: 'No market-data series is selected.',
  revision: 0,
  lastChange: Object.freeze({ type: 'snapshot' }),
});

/**
 * React binding for one canonical market-data series.
 *
 * The canonical key is the dependency boundary: callers may recreate an
 * equivalent identity object on each render without resubscribing. Different
 * series keys receive independent snapshots and listener notifications.
 */
export function useMarketDataSeriesSnapshot(
  identity: MarketSeriesIdentity | null,
): MarketDataSnapshot {
  const identityKey = identity ? getMarketSeriesIdentityKey(identity) : null;

  const subscribe = useCallback((listener: () => void) => {
    if (!identity) return () => {};
    return marketDataSeriesStore.subscribe(identity, listener);
  }, [identityKey]);

  const getSnapshot = useCallback(() => {
    if (!identity) return EMPTY_SERIES_SNAPSHOT;
    return marketDataSeriesStore.peekSnapshot(identity);
  }, [identityKey]);

  return useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
}
