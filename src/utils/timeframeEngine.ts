

import type { ChartData, Timeframe } from '../types';

const FIXED_INTERVALS: Partial<Record<Timeframe, number>> = {
  '1s': 1,
  '5s': 5,
  '15s': 15,
  '30s': 30,
  '45s': 45,
  '1m': 60,
  '3m': 180,
  '5m': 300,
  '15m': 900,
  '30m': 1800,
  '45m': 2700,
  '1h': 3600,
  '2h': 7200,
  '4h': 14400,
  '1d': 86400,
};

const SECONDS_PER_DAY = 86400;

const TIMEFRAME_ORDER: Timeframe[] = [
  '1s', '5s', '15s', '30s', '45s',
  '1m', '3m', '5m', '15m', '30m', '45m',
  '1h', '2h', '4h', '1d', '1w', '1M', '3M',
];

function getUtcDayStart(timestamp: number): number {
  return Math.floor(timestamp / SECONDS_PER_DAY) * SECONDS_PER_DAY;
}

function getUtcMonthStart(
  timestamp: number,
  monthInterval: 1 | 3
): number {
  const date = new Date(timestamp * 1000);
  const year = date.getUTCFullYear();
  const month = date.getUTCMonth();
  const alignedMonth =
    Math.floor(month / monthInterval) * monthInterval;

  return Date.UTC(year, alignedMonth, 1) / 1000;
}

export function getTimeframeBucketStart(
  timestamp: number,
  timeframe: Timeframe
): number {
  if (!Number.isFinite(timestamp)) {
    throw new Error('Invalid candle timestamp.');
  }

  if (timeframe === '1M') {
    return getUtcMonthStart(timestamp, 1);
  }

  if (timeframe === '3M') {
    return getUtcMonthStart(timestamp, 3);
  }

  if (timeframe === '1w') {
    const dayStart = getUtcDayStart(timestamp);
    const date = new Date(dayStart * 1000);
    const daysSinceMonday = (date.getUTCDay() + 6) % 7;

    return dayStart - daysSinceMonday * SECONDS_PER_DAY;
  }

  const interval = FIXED_INTERVALS[timeframe];

  if (interval === undefined) {
    throw new Error(`Unsupported timeframe: ${timeframe}`);
  }

  return Math.floor(timestamp / interval) * interval;
}

function validateTimeframeConversion(
  sourceTimeframe: Timeframe,
  targetTimeframe: Timeframe
): void {
  const sourceIndex = TIMEFRAME_ORDER.indexOf(sourceTimeframe);
  const targetIndex = TIMEFRAME_ORDER.indexOf(targetTimeframe);

  if (sourceIndex === -1 || targetIndex === -1) {
    throw new Error('Unsupported source or target timeframe.');
  }

  if (targetIndex < sourceIndex) {
    throw new Error(
      `Cannot convert ${sourceTimeframe} data into finer ${targetTimeframe} candles.`
    );
  }
}

function isValidCandle(candle: ChartData): boolean {
  const values = [
    candle.timestamp,
    candle.open,
    candle.high,
    candle.low,
    candle.close,
    candle.volume,
  ];

  if (!values.every(Number.isFinite)) return false;
  if (candle.volume < 0) return false;
  if (candle.high < candle.low) return false;
  if (candle.high < Math.max(candle.open, candle.close)) return false;
  if (candle.low > Math.min(candle.open, candle.close)) return false;

  return true;
}

export function aggregateCandles(
  candles: ChartData[],
  sourceTimeframe: Timeframe,
  targetTimeframe: Timeframe
): ChartData[] {
  validateTimeframeConversion(sourceTimeframe, targetTimeframe);

  if (candles.length === 0) return [];

  // A feed may publish several revisions of the same source candle.
  // Keep the last supplied snapshot for each timestamp instead of summing
  // repeated cumulative OHLCV updates into the target candle.
  const latestByTimestamp = new Map<number, ChartData>();

  for (const candle of candles) {
    if (isValidCandle(candle)) {
      latestByTimestamp.set(candle.timestamp, candle);
    }
  }

  const sortedCandles = [...latestByTimestamp.values()]
    .sort((a, b) => a.timestamp - b.timestamp);

  const result: ChartData[] = [];

  let currentBucket: number | null = null;
  let currentCandle: ChartData | null = null;

  for (const candle of sortedCandles) {
    const bucket = getTimeframeBucketStart(
      candle.timestamp,
      targetTimeframe
    );

    if (bucket !== currentBucket) {
      if (currentCandle !== null) {
        result.push(currentCandle);
      }

      currentBucket = bucket;

      currentCandle = {
        timestamp: bucket,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
        volume: candle.volume,
      };

      continue;
    }

    if (currentCandle !== null) {
      currentCandle.high = Math.max(
        currentCandle.high,
        candle.high
      );

      currentCandle.low = Math.min(
        currentCandle.low,
        candle.low
      );

      currentCandle.close = candle.close;
      currentCandle.volume += candle.volume;
    }
  }

  if (currentCandle !== null) {
    result.push(currentCandle);
  }

  return result;
}
