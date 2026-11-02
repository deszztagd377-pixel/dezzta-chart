import { describe, expect, it } from 'vitest';
import { toCandlestickSeriesData } from './candlestickSeriesData';

describe('toCandlestickSeriesData', () => {
  it('maps epoch seconds and OHLC values without millisecond conversion', () => {
    const result = toCandlestickSeriesData([{
      timestamp: 1793577600,
      open: 6000.125,
      high: 6001.25,
      low: 5999.875,
      close: 6000.75,
      volume: 12,
    }]);
    expect(result).toEqual([{
      time: 1793577600,
      open: 6000.125,
      high: 6001.25,
      low: 5999.875,
      close: 6000.75,
    }]);
  });

  it('preserves chronological order and empty input', () => {
    const result = toCandlestickSeriesData([
      { timestamp: 10, open: 1, high: 2, low: 1, close: 2, volume: 1 },
      { timestamp: 20, open: 2, high: 3, low: 2, close: 2.5, volume: 2 },
    ]);
    expect(result.map((item) => item.time)).toEqual([10, 20]);
    expect(toCandlestickSeriesData([])).toEqual([]);
  });
});
