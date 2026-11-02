import type { CandlestickData } from 'lightweight-charts';

/**
 * Fixed, offline-only candle fixture used by the chart demonstration.
 * Dates are daily UTC calendar dates; this is not market data.
 */
export const demoCandles: CandlestickData[] = [
  { time: '2024-01-01', open: 100.0, high: 105.5, low: 98.2, close: 103.8 },
  { time: '2024-01-02', open: 103.8, high: 107.2, low: 102.1, close: 106.5 },
  { time: '2024-01-03', open: 106.5, high: 108.0, low: 104.3, close: 105.2 },
  { time: '2024-01-04', open: 105.2, high: 109.8, low: 104.5, close: 108.7 },
  { time: '2024-01-05', open: 108.7, high: 110.5, low: 107.3, close: 109.1 },
  { time: '2024-01-08', open: 109.1, high: 112.4, low: 108.6, close: 111.8 },
  { time: '2024-01-09', open: 111.8, high: 113.2, low: 110.5, close: 112.3 },
  { time: '2024-01-10', open: 112.3, high: 114.0, low: 111.2, close: 113.5 },
  { time: '2024-01-11', open: 113.5, high: 115.8, low: 112.7, close: 114.9 },
  { time: '2024-01-12', open: 114.9, high: 116.2, low: 113.8, close: 115.4 },
  { time: '2024-01-15', open: 115.4, high: 117.5, low: 114.8, close: 116.9 },
  { time: '2024-01-16', open: 116.9, high: 118.3, low: 116.1, close: 117.7 },
  { time: '2024-01-17', open: 117.7, high: 119.0, low: 116.5, close: 118.2 },
  { time: '2024-01-18', open: 118.2, high: 120.5, low: 117.8, close: 119.8 },
  { time: '2024-01-19', open: 119.8, high: 121.2, low: 119.1, close: 120.7 },
  { time: '2024-01-22', open: 120.7, high: 122.8, low: 120.3, close: 122.1 },
  { time: '2024-01-23', open: 122.1, high: 123.5, low: 121.4, close: 122.8 },
  { time: '2024-01-24', open: 122.8, high: 124.2, low: 122.0, close: 123.7 },
  { time: '2024-01-25', open: 123.7, high: 125.0, low: 123.2, close: 124.5 },
  { time: '2024-01-26', open: 124.5, high: 126.3, low: 124.1, close: 125.8 },
];

export function getDemoCandleValidationErrors(
  candles: readonly CandlestickData[],
): string[] {
  const errors: string[] = [];
  let previousDate: string | null = null;

  if (candles.length === 0) {
    return ['The demo candle dataset must not be empty.'];
  }

  candles.forEach((candle, index) => {
    const label = `Candle at index ${index}`;
    const { open, high, low, close } = candle;

    if (![open, high, low, close].every(Number.isFinite)) {
      errors.push(`${label} contains a non-finite OHLC value.`);
      return;
    }

    if (high < low || high < Math.max(open, close) || low > Math.min(open, close)) {
      errors.push(`${label} violates OHLC high/low boundaries.`);
    }

    if (typeof candle.time !== 'string' || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(candle.time)) {
      errors.push(`${label} must use a YYYY-MM-DD daily date.`);
      return;
    }

    const parsedDate = new Date(`${candle.time}T00:00:00.000Z`);
    if (
      Number.isNaN(parsedDate.getTime()) ||
      parsedDate.toISOString().slice(0, 10) !== candle.time
    ) {
      errors.push(`${label} contains an invalid calendar date.`);
      return;
    }

    if (previousDate !== null && candle.time <= previousDate) {
      errors.push(`${label} is not strictly later than the previous candle.`);
    }

    previousDate = candle.time;
  });

  return errors;
}
