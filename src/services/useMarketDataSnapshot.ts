import { useSyncExternalStore } from 'react';
import {
  getMarketDataSnapshot,
  subscribeMarketData,
} from './marketDataStore';

/** React subscription shared by every chart-linked indicator. */
export function useMarketDataSnapshot() {
  return useSyncExternalStore(
    subscribeMarketData,
    getMarketDataSnapshot,
    getMarketDataSnapshot,
  );
}
