
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
  it('calculates 5-minute buckets', () => {
    expect(getTimeframeBucketStart(305, '5m')).toBe(300);
    expect(getTimeframeBucketStart(599, '5m')).toBe(300);
    expect(getTimeframeBucketStart(600, '5m')).toBe(600);
  });

  it('calculates weekly buckets from Monday UTC', () => {
    const monday = Date.UTC(2024, 0, 1) / 1000;
    const thursday = monday + 3 * 86400;

    expect(getTimeframeBucketStart(thursday, '1w')).toBe(monday);
  });

  it('calculates monthly buckets', () => {
    const january = Date.UTC(2024, 0, 1) / 1000;
    const february = Date.UTC(2024, 1, 1) / 1000;

    expect(getTimeframeBucketStart(january + 86400, '1M')).toBe(january);
    expect(getTimeframeBucketStart(february + 86400, '1M')).toBe(february);
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
  it('aggregates OHLCV correctly from 1m to 5m', () => {
    const candles: ChartData[] = [
      makeCandle(0, 100, 110, 95, 105, 10),
      makeCandle(60, 105, 115, 100, 112, 20),
      makeCandle(120, 112, 120, 108, 118, 30),
    ];

    const result = aggregateCandles(candles, '1m', '5m');

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

  it('sorts candles chronologically', () => {
    const candles: ChartData[] = [
      makeCandle(60, 105, 115, 100, 112, 20),
      makeCandle(0, 100, 110, 95, 105, 10),
    ];

    const result = aggregateCandles(candles, '1m', '5m');

    expect(result[0].open).toBe(100);
    expect(result[0].close).toBe(112);
    expect(result[0].volume).toBe(30);
  });

  it('separates different target buckets', () => {
    const candles: ChartData[] = [
      makeCandle(0, 100, 110, 95, 105, 10),
      makeCandle(300, 105, 115, 100, 112, 20),
    ];

    const result = aggregateCandles(candles, '1m', '5m');

    expect(result).toHaveLength(2);
  });

  it('returns an empty array for empty input', () => {
    expect(aggregateCandles([], '1m', '5m')).toEqual([]);
  });

  it('rejects conversion from coarser to finer timeframe', () => {
    const candles = [
      makeCandle(0, 100, 110, 95, 105, 10),
    ];

    expect(() =>
      aggregateCandles(candles, '1h', '5m')
    ).toThrow();
  });

  it('rejects invalid OHLCV candles', () => {
    const candles: ChartData[] = [
      makeCandle(0, 100, 110, 95, 105, 10),
      makeCandle(60, 100, 90, 95, 105, 10),
      makeCandle(120, 100, 110, 95, 105, -5),
    ];

    const result = aggregateCandles(candles, '1m', '5m');

    expect(result).toHaveLength(1);
    expect(result[0].volume).toBe(10);
  });
});
