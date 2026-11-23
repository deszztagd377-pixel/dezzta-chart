import type { Timeframe } from '../types';
import type { OhlcvBucketPolicy } from '../types/ohlcv';

/**
 * Selects the default bucket identity when no exact exchange calendar release
 * is supplied. CME session identity is selected separately and only when both
 * the canonical calendar ID and one loaded release version are available.
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


export interface OhlcvBucketIdentity {
  bucketPolicy: OhlcvBucketPolicy;
  calendarId: string;
  calendarVersion: string;
}

const CME_SESSION_TIMEFRAMES: readonly Timeframe[] = ['1d', '1w', '1M', '3M'];

/**
 * Select CME session buckets only for supported higher timeframes and only
 * when the catalog supplies a loaded, exact calendar release. Incomplete
 * metadata safely falls back to the existing UTC identity.
 */
export function getBucketIdentityForTimeframe(
  timeframe: Timeframe,
  calendarId?: string | null,
  calendarVersion?: string | null,
): OhlcvBucketIdentity {
  const normalizedCalendarId = calendarId ?? '';
  const normalizedCalendarVersion = calendarVersion ?? '';
  if (typeof normalizedCalendarId !== 'string' || typeof normalizedCalendarVersion !== 'string') {
    throw new Error('Exchange calendar identity must contain strings.');
  }

  if (
    CME_SESSION_TIMEFRAMES.includes(timeframe) &&
    normalizedCalendarId.trim() &&
    normalizedCalendarVersion.trim()
  ) {
    return {
      bucketPolicy: 'CME_SESSION_V1',
      calendarId: normalizedCalendarId,
      calendarVersion: normalizedCalendarVersion,
    };
  }

  return {
    bucketPolicy: getBucketPolicyForTimeframe(timeframe),
    calendarId: '',
    calendarVersion: '',
  };
}
