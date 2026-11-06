import type { Timeframe } from '../types';
import type { OhlcvBucketPolicy } from '../types/ohlcv';

/**
 * Selects a versioned UTC bucket identity by timeframe.
 *
 * Intraday intervals use the new fixed UTC policy. Existing daily and larger
 * historical series retain their legacy identity until an authoritative
 * exchange-session calendar is implemented and validated.
 */
export function getBucketPolicyForTimeframe(timeframe: Timeframe): OhlcvBucketPolicy {
  switch (timeframe) {
    case '1s':
    case '5s':
    case '15s':
    case '30s':
    case '45s':
    case '1m':
    case '3m':
    case '5m':
    case '15m':
    case '30m':
    case '45m':
    case '1h':
    case '2h':
    case '4h':
      return 'UTC_FIXED_V1';
    case '1d':
    case '1w':
    case '1M':
    case '3M':
      return 'UTC_LEGACY';
    default: {
      const exhaustive: never = timeframe;
      throw new Error(`Unsupported timeframe: ${exhaustive}`);
    }
  }
}
