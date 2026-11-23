import { describe, expect, it } from 'vitest';
import type { Timeframe } from '../types';
import {
  getBucketIdentityForTimeframe,
  getBucketPolicyForTimeframe,
} from './ohlcvBucketPolicy';

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

  it('selects CME session identity only with an exact loaded release for higher timeframes', () => {
    const calendarId = 'CME_EQUITY_INDEX';
    const calendarVersion = 'test-only-2024.01';
    const sessionTimeframes: Timeframe[] = ['1d', '1w', '1M', '3M'];

    sessionTimeframes.forEach((timeframe) => {
      expect(getBucketIdentityForTimeframe(timeframe, calendarId, calendarVersion)).toEqual({
        bucketPolicy: 'CME_SESSION_V1',
        calendarId,
        calendarVersion,
      });
    });
  });

  it('falls back to UTC identity when the calendar release is missing or timeframe is intraday', () => {
    expect(getBucketIdentityForTimeframe('1d', 'CME_EQUITY_INDEX', null)).toEqual({
      bucketPolicy: 'UTC_LEGACY',
      calendarId: '',
      calendarVersion: '',
    });
    expect(getBucketIdentityForTimeframe('1h', 'CME_EQUITY_INDEX', 'test-only-2024.01')).toEqual({
      bucketPolicy: 'UTC_FIXED_V1',
      calendarId: '',
      calendarVersion: '',
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
