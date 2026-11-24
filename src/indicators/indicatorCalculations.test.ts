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

  it('keeps every indicator prefix-causal so future candles cannot change earlier values', () => {
    const bars = Array.from({ length: 64 }, (_, index) => {
      const close = 100 + index * 0.37 + Math.sin(index / 3) * 2 + (index % 7) * 0.11;
      const open = close - 0.2;
      return {
        timestamp: 1_800_000_000 + index * 60,
        open,
        high: Math.max(open, close) + 0.5,
        low: Math.min(open, close) - 0.5,
        close,
        volume: 10 + index,
      };
    });
    const full = calculateIndicators(bars);
    const checkpoints = [1, 14, 15, 19, 20, 26, 34, 35, 48, 64];

    for (const length of checkpoints) {
      const prefix = calculateIndicators(bars.slice(0, length));
      expect(prefix.sma20, `SMA prefix length ${length}`).toEqual(full.sma20.slice(0, length));
      expect(prefix.ema20, `EMA prefix length ${length}`).toEqual(full.ema20.slice(0, length));
      expect(prefix.rsi14, `RSI prefix length ${length}`).toEqual(full.rsi14.slice(0, length));
      expect(prefix.macd, `MACD prefix length ${length}`).toEqual(full.macd.slice(0, length));
      expect(prefix.bollinger20, `Bollinger prefix length ${length}`).toEqual(full.bollinger20.slice(0, length));
    }
  });

  it('handles falling-only RSI and period-one moving averages at exact source indices', () => {
    expect(calculateRsi([4, 3, 2, 1], 2)).toEqual([null, null, 0, 0]);
    expect(calculateSma([3, 2, 4], 1)).toEqual([3, 2, 4]);
    expect(calculateEma([3, 2, 4], 1)).toEqual([3, 2, 4]);
    expect(calculateRsi([3, 2, 4], 1)).toEqual([null, 0, 100]);
  });

  it('fails closed instead of emitting infinite values from finite extreme inputs', () => {
    const extreme = Number.MAX_VALUE;
    expect(calculateSma([extreme, extreme], 2)).toEqual([null, extreme]);
    expect(calculateEma([extreme, extreme], 2)).toEqual([null, extreme]);
    expect(() => calculateRsi([-extreme, extreme], 1)).toThrow(/finite numeric range/);
    expect(() => calculateBollingerBands([extreme, -extreme], 2, 2)).toThrow(/finite numeric range/);
  });

  it('keeps RSI numerically stable when gain/loss magnitudes are very large but finite', () => {
    const extreme = Number.MAX_VALUE;
    const result = calculateRsi([0, extreme, 0, extreme], 2);
    expect(result[2]).toBe(50);
    expect(result[3]).toBeCloseTo(75, 10);
    expect(result.slice(2).every((value) => value !== null && Number.isFinite(value))).toBe(true);
  });

  it('computes representable SMA means without overflowing the intermediate sum', () => {
    const extreme = Number.MAX_VALUE;
    expect(calculateSma([extreme, extreme], 2)).toEqual([null, extreme]);
    expect(calculateSma([extreme, extreme, -extreme], 3)[2]! / extreme).toBeCloseTo(1 / 3, 10);
    expect(calculateSma([extreme, extreme, -extreme, -extreme], 2)).toEqual([
      null, extreme, 0, -extreme,
    ]);
  });

  it('keeps Bollinger population deviation finite for large same-sign prices', () => {
    const extreme = Number.MAX_VALUE;
    const expected = extreme * 0.9;
    const result = calculateBollingerBands([expected, expected], 2, 2);
    expect(result[1].middle).toBe(expected);
    expect(result[1].upper).toBe(expected);
    expect(result[1].lower).toBe(expected);
  });

  it('preserves small residuals between large cancelling SMA inputs', () => {
    const extreme = Number.MAX_VALUE;
    const expected = 1 / 3;
    const forward = calculateSma([extreme, 1, -extreme], 3)[2];
    const reverse = calculateSma([extreme, -extreme, 1], 3)[2];

    expect(forward).toBeCloseTo(expected, 14);
    expect(reverse).toBeCloseTo(expected, 14);
    expect(Number.isFinite(forward)).toBe(true);
    expect(Number.isFinite(reverse)).toBe(true);
  });

  it('preserves small residuals in the Bollinger middle band under cancellation', () => {
    const extreme = Number.MAX_VALUE;
    const result = calculateBollingerBands([extreme, 1, -extreme], 3, 0);
    expect(result[2].middle).toBeCloseTo(1 / 3, 14);
    expect(result[2].upper).toBeCloseTo(1 / 3, 14);
    expect(result[2].lower).toBeCloseTo(1 / 3, 14);
  });

  it('matches the Wilder RSI seed and recursive smoothing on alternating gains and losses', () => {
    // Period 2: seed averages are 0.5 gain / 0.5 loss (RSI 50).
    // Wilder recurrence then produces 0.75 / 0.25 (RSI 75), followed by
    // 0.375 / 0.625 (RSI 37.5). Values stay aligned to source candle indices.
    expect(calculateRsi([1, 2, 1, 2, 1], 2)).toEqual([
      null, null, 50, 75, 37.5,
    ]);
  });

  it('rejects a non-finite close at the shared multi-indicator boundary', () => {
    const bars = Array.from({ length: 24 }, (_, index) => ({
      timestamp: index + 1,
      open: 100,
      high: 101,
      low: 99,
      close: index === 7 ? Number.NaN : 100,
      volume: 1,
    }));

    expect(() => calculateIndicators(bars)).toThrow('Bar 7 has a non-finite close value.');
  });


  it('keeps RSI bounded and finite across a deterministic mixed market path', () => {
    const values = Array.from({ length: 160 }, (_, index) => (
      250 + index * 0.13 + Math.sin(index / 4) * 3 + Math.cos(index / 11) * 1.7
    ));
    const result = calculateRsi(values, 14);

    expect(result.slice(0, 14)).toEqual(Array(14).fill(null));
    for (const value of result.slice(14)) {
      expect(value).not.toBeNull();
      expect(Number.isFinite(value)).toBe(true);
      expect(value!).toBeGreaterThanOrEqual(0);
      expect(value!).toBeLessThanOrEqual(100);
    }
  });

  it('preserves the MACD histogram identity at every initialized source index', () => {
    const values = Array.from({ length: 96 }, (_, index) => (
      100 + index * 0.21 + Math.sin(index / 5) * 4
    ));
    const result = calculateMacd(values);

    for (const point of result) {
      if (point.macd === null || point.signal === null) {
        expect(point.histogram).toBeNull();
        continue;
      }
      expect(point.histogram).toBeCloseTo(point.macd - point.signal, 12);
    }
  });

  it('keeps Bollinger width translation-invariant and bands symmetric around the mean', () => {
    const values = Array.from({ length: 48 }, (_, index) => (
      80 + index * 0.7 + Math.sin(index / 2) * 2
    ));
    const shifted = values.map((value) => value + 10_000);
    const original = calculateBollingerBands(values, 20, 2);
    const translated = calculateBollingerBands(shifted, 20, 2);

    for (let index = 19; index < values.length; index += 1) {
      const point = original[index];
      const shiftedPoint = translated[index];
      expect(point.upper! + point.lower!).toBeCloseTo(2 * point.middle!, 10);
      expect(shiftedPoint.middle! - point.middle!).toBeCloseTo(10_000, 10);
      expect(shiftedPoint.upper! - shiftedPoint.middle!).toBeCloseTo(
        point.upper! - point.middle!, 9,
      );
      expect(shiftedPoint.middle! - shiftedPoint.lower!).toBeCloseTo(
        point.middle! - point.lower!, 9,
      );
    }
  });

  it('keeps every study in warm-up state when history is shorter than its slowest period', () => {
    const bars = Array.from({ length: 19 }, (_, index) => {
      const close = 50 + index;
      return {
        timestamp: index + 1,
        open: close,
        high: close + 1,
        low: close - 1,
        close,
        volume: 1,
      };
    });
    const result = calculateIndicators(bars);

    expect(result.sma20).toEqual(Array(19).fill(null));
    expect(result.ema20).toEqual(Array(19).fill(null));
    expect(result.rsi14.slice(0, 14)).toEqual(Array(14).fill(null));
    expect(result.macd.every((point) => (
      point.macd === null && point.signal === null && point.histogram === null
    ))).toBe(true);
    expect(result.bollinger20.every((point) => (
      point.middle === null && point.upper === null && point.lower === null
    ))).toBe(true);
  });

});