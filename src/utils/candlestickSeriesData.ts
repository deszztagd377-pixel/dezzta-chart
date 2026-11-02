import type { CandlestickData, UTCTimestamp } from 'lightweight-charts';
import type { ChartData } from '../types';

/**
 * Converts validated OHLCV adapter output to Lightweight Charts v5 candles.
 * Adapter timestamps are Unix epoch seconds, not milliseconds.
 */
export function toCandlestickSeriesData(candles: readonly ChartData[]): CandlestickData[] {
  return candles.map((candle) => ({
    time: candle.timestamp as UTCTimestamp,
    open: candle.open,
    high: candle.high,
    low: candle.low,
    close: candle.close,
  }));
}
