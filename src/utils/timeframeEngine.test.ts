
import { describe, it, expect } from 'vitest';
import {
  getTimeframeBucketStart,
  aggregateCandles,
} from './timeframeEngine';
import type { ChartData, Timeframe } from '../types';

const makeCandle = (
  timestamp: number,
  open: number,
  high: number,
  low: number,
  close: number,
  volume: number
): ChartData => ({
  timestamp,
  open,
  high,
  low,
  close,
  volume,
});

describe('getTimeframeBucketStart', () => {
  it('groups minute candles into the correct 5-minute bucket', () => {
    expect(getTimeframeBucketStart(305, '5m')).toBe(300);
    expect(getTimeframeBucketStart(599, '5m')).toBe(300);
    expect(getTimeframeBucketStart(600, '5m')).toBe(600);
  });

  it('groups hourly candles correctly', () => {
    expect(getTimeframeBucketStart(3601, '1h')).toBe(3600);
    expect(getTimeframeBucketStart(7200, '1h')).toBe(7200);
  });

  it('groups weekly candles from Monday UTC', () => {
    // 2024-01-01 00:00:00 UTC was Monday.
    const monday = Date.UTC(2024, 0, 1) / 1000;
    const thursday = monday + 3 * 86400;

    expect(getTimeframeBucketStart(thursday, '1w')).toBe(monday);
  });

  it('groups monthly candles by calendar month', () => {
    const january = Date.UTC(2024, 0, 1) / 1000;
    const february = Date.UTC(2024, 1, 1) / 1000;

    expect(getTimeframeBucketStart(january + 86400, '1M')).toBe(january);
    expect(getTimeframeBucketStart(february + 86400, '1M')).toBe(february);
  });

  it('groups quarterly candles correctly', () => {
    const january = Date.UTC(2024, 0, 1) / 1000;
    const april = Date.UTC(2024, 3, 1) / 1000;

    expect(getTimeframeBucketStart(january + 86400, '3M')).toBe(january);
    expect(getTimeframeBucketStart(april + 86400, '3M')).toBe(april);
  });

  it('supports all configured timeframes', () => {
    const timeframes: Timeframe[] = [
      '1s', '5s', '15s', '30s', '45s',
      '1m', '3m', '5m', '15m', '30m', '45m',
      '1h', '2h', '4h', '1d', '1w', '1M', '3M',
    ];

    for (const timeframe of timeframes) {
      expect(() =>
        getTimeframeBucketStart(1704067200, timeframe)
      ).not.toThrow();
    }
  });

  it('rejects invalid timestamps', () => {
    expect(() => getTimeframeBucketStart(NaN, '1m')).toThrow();
    expect(() => getTimeframeBucketStart(Infinity, '1m')).toThrow();
  });
});

describe('aggregateCandles', () => {
  it('aggregates OHLCV values correctly', () => {
    const candles: ChartData[] = [
      makeCandle(0, 100, 110, 95, 105, 10),
      makeCandle(60, 105, 115, 100, 112, 20),
      makeCandle(120, 112, 120, 108, 118, 30),
    ];

    const result = aggregateCandles(candles, '5m');

    expect(result).toHaveLength(1);
    expect(result[0]).toEqual({
      timestamp: 0,
      open: 100,
      high: 120,
      low: 95,
      close: 118,
      volume: 60,
    });
  });

  it('sorts input candles chronologically', () => {
    const candles: ChartData[] = [
      makeCandle(60, 105, 115, 100, 112, 20),
      makeCandle(0, 100, 110, 95, 105, 10),
    ];

    const result = aggregateCandles(candles, '5m');

    expect(result[0].open).toBe(100);
    expect(result[0].close).toBe(112);
    expect(result[0].volume).toBe(30);
  });

  it('creates separate candles for separate buckets', () => {
    const candles: ChartData[] = [
      makeCandle(0, 100, 110, 95, 105, 10),
      makeCandle(300, 105, 115, 100, 112, 20),
    ];

    const result = aggregateCandles(candles, '5m');

    expect(result).toHaveLength(2);
    expect(result[0].timestamp).toBe(0);
    expect(result[1].timestamp).toBe(300);
  });

  it('returns an empty array for empty input', () => {
    expect(aggregateCandles([], '1m')).toEqual([]);
  });

  it('ignores invalid candle values', () => {
    const candles: ChartData[] = [
      makeCandle(0, 100, 110, 95, 105, 10),
      makeCandle(60, 100, 90, 95, 105, 10),
      makeCandle(120, 100, 110, 95, 105, -5),
    ];

    const result = aggregateCandles(candles, '5m');

    expect(result).toHaveLength(1);
    expect(result[0].volume).toBe(10);
  });
});
