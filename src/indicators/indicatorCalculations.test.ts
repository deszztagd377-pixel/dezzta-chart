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

  it('rejects invalid periods and non-finite values', () => {
    expect(() => calculateSma([1, 2], 0)).toThrow();
    expect(() => calculateEma([1, Number.NaN], 2)).toThrow();
    expect(() => calculateMacd([1, 2, 3], 26, 12)).toThrow();
  });
});
