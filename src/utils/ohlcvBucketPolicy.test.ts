import { describe, expect, it } from 'vitest';
import type { Timeframe } from '../types';
import { getBucketPolicyForTimeframe } from './ohlcvBucketPolicy';

describe('getBucketPolicyForTimeframe', () => {
  it('assigns fixed UTC identity to all intraday intervals', () => {
    const intraday: Timeframe[] = [
      '1s', '5s', '15s', '30s', '45s',
      '1m', '3m', '5m', '15m', '30m', '45m',
      '1h', '2h', '4h',
    ];
    intraday.forEach((timeframe) => {
      expect(getBucketPolicyForTimeframe(timeframe), timeframe).toBe('UTC_FIXED_V1');
    });
  });

  it('preserves legacy identity for daily, weekly, monthly and quarterly history', () => {
    const historical: Timeframe[] = ['1d', '1w', '1M', '3M'];
    historical.forEach((timeframe) => {
      expect(getBucketPolicyForTimeframe(timeframe), timeframe).toBe('UTC_LEGACY');
    });
  });

  it('covers every currently supported timeframe exactly once', () => {
    const all: Timeframe[] = [
      '1s', '5s', '15s', '30s', '45s',
      '1m', '3m', '5m', '15m', '30m', '45m',
      '1h', '2h', '4h', '1d', '1w', '1M', '3M',
    ];
    expect(all).toHaveLength(18);
    expect(all.map(getBucketPolicyForTimeframe)).toEqual([
      ...Array(14).fill('UTC_FIXED_V1'),
      ...Array(4).fill('UTC_LEGACY'),
    ]);
  });
});
