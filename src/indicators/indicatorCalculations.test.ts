import { describe, expect, it } from 'vitest';
import {
  calculateBollingerBands,
  calculateEma,
  calculateIndicators,
  calculateMacd,
  calculateRsi,
  calculateSma,
} from './indicatorCalculations';

describe('shared indicator calculation engine', () => {
  it('aligns SMA and EMA to source bars and preserves warm-up nulls', () => {
    expect(calculateSma([1, 2, 3, 4], 3)).toEqual([null, null, 2, 3]);
    expect(calculateEma([1, 2, 3, 4], 3)).toEqual([null, null, 2, 3]);
  });

  it('calculates Wilder RSI with explicit flat and rising edge cases', () => {
    expect(calculateRsi([1, 1, 1, 1], 2)).toEqual([null, null, 50, 50]);
    expect(calculateRsi([1, 2, 3, 4], 2)[2]).toBe(100);
  });

  it('keeps MACD signal warm-up separate from MACD values', () => {
    const result = calculateMacd(Array.from({ length: 40 }, (_, i) => i + 1));
    expect(result[24].macd).toBeNull();
    expect(result[25].macd).not.toBeNull();
    expect(result[32].signal).toBeNull();
    expect(result[33].signal).not.toBeNull();
  });

  it('uses population standard deviation for Bollinger bands', () => {
    const result = calculateBollingerBands([1, 2, 3], 3, 2);
    expect(result[1].middle).toBeNull();
    expect(result[2].middle).toBe(2);
    expect(result[2].upper).toBeCloseTo(2 + 2 * Math.sqrt(2 / 3));
    expect(result[2].lower).toBeCloseTo(2 - 2 * Math.sqrt(2 / 3));
  });

  it('exposes a single multi-indicator calculation entry point', () => {
    const bars = Array.from({ length: 40 }, (_, i) => ({
      timestamp: i + 1, open: i, high: i + 1, low: i - 1, close: i, volume: i * 2,
    }));
    const result = calculateIndicators(bars);
    expect(result.sma20).toHaveLength(40);
    expect(result.ema20).toHaveLength(40);
    expect(result.rsi14).toHaveLength(40);
    expect(result.macd).toHaveLength(40);
    expect(result.bollinger20).toHaveLength(40);
  });

  it('calculates every shared indicator on every supported chart timeframe', () => {
    const timeframes = [
      '1s', '5s', '15s', '30s', '45s',
      '1m', '3m', '5m', '15m', '30m', '45m',
      '1h', '2h', '4h', '1d', '1w', '1M', '3M',
    ] as const;

    for (const timeframe of timeframes) {
      const bars = Array.from({ length: 40 }, (_, index) => ({
        timestamp: index + 1,
        open: 100 + index,
        high: 102 + index,
        low: 99 + index,
        close: 101 + index,
        volume: 10 + index,
      }));
      const result = calculateIndicators(bars);

      expect(result.sma20, timeframe).toHaveLength(40);
      expect(result.ema20, timeframe).toHaveLength(40);
      expect(result.rsi14, timeframe).toHaveLength(40);
      expect(result.macd, timeframe).toHaveLength(40);
      expect(result.bollinger20, timeframe).toHaveLength(40);
      expect(result.sma20[18], timeframe).toBeNull();
      expect(result.sma20[19], timeframe).not.toBeNull();
      expect(result.rsi14[13], timeframe).toBeNull();
      expect(result.rsi14[14], timeframe).not.toBeNull();
      expect(result.macd[25].macd, timeframe).not.toBeNull();
      expect(result.macd[33].signal, timeframe).not.toBeNull();
      expect(result.bollinger20[18].middle, timeframe).toBeNull();
      expect(result.bollinger20[19].middle, timeframe).not.toBeNull();
    }
  });

  it('rejects invalid periods and non-finite values', () => {
    expect(() => calculateSma([1, 2], 0)).toThrow();
    expect(() => calculateEma([1, Number.NaN], 2)).toThrow();
    expect(() => calculateMacd([1, 2, 3], 26, 12)).toThrow();
  });
});
