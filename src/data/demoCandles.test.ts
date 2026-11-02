import { describe, expect, it } from 'vitest';
import type { CandlestickData } from 'lightweight-charts';
import {
  demoCandles,
  getDemoCandleValidationErrors,
} from './demoCandles';

describe('demo candle fixture', () => {
  it('contains valid daily OHLC candles in chronological order', () => {
    expect(getDemoCandleValidationErrors(demoCandles)).toEqual([]);
  });

  it('rejects an empty dataset', () => {
    expect(getDemoCandleValidationErrors([])).toContain(
      'The demo candle dataset must not be empty.',
    );
  });

  it('rejects high/low values that do not contain open and close', () => {
    const invalid: CandlestickData[] = [
      { time: '2024-01-01', open: 100, high: 99, low: 95, close: 98 },
    ];

    expect(getDemoCandleValidationErrors(invalid)).toContain(
      'Candle at index 0 violates OHLC high/low boundaries.',
    );
  });

  it('rejects non-finite OHLC values', () => {
    const invalid: CandlestickData[] = [
      { time: '2024-01-01', open: 100, high: Infinity, low: 95, close: 98 },
    ];

    expect(getDemoCandleValidationErrors(invalid)).toContain(
      'Candle at index 0 contains a non-finite OHLC value.',
    );
  });

  it('rejects invalid calendar dates', () => {
    const invalid: CandlestickData[] = [
      { time: '2024-02-30', open: 100, high: 105, low: 95, close: 102 },
    ];

    expect(getDemoCandleValidationErrors(invalid)).toContain(
      'Candle at index 0 contains an invalid calendar date.',
    );
  });

  it('rejects duplicate or descending dates', () => {
    const invalid: CandlestickData[] = [
      { time: '2024-01-02', open: 100, high: 105, low: 95, close: 102 },
      { time: '2024-01-02', open: 102, high: 106, low: 99, close: 104 },
    ];

    expect(getDemoCandleValidationErrors(invalid)).toContain(
      'Candle at index 1 is not strictly later than the previous candle.',
    );
  });

  it('rejects non-daily time values in this date-only fixture', () => {
    const invalid: CandlestickData[] = [
      { time: 1704067200 as unknown as CandlestickData['time'], open: 100, high: 105, low: 95, close: 102 },
    ];

    expect(getDemoCandleValidationErrors(invalid)).toContain(
      'Candle at index 0 must use a YYYY-MM-DD daily date.',
    );
  });
});
