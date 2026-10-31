
import type { ChartData, Timeframe } from '../types';

/**
 * DEZZTA CHART - Timeframe Aggregation Engine
 *
 * Input timestamps must be Unix timestamps in SECONDS.
 * Input data must be chronological OHLCV candles.
 * This module aggregates existing candles; it does not create
 * missing market data or convert coarse data into finer data.
 */

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

function getUtcDayStart(timestamp: number): number {
  return Math.floor(timestamp / SECONDS_PER_DAY) * SECONDS_PER_DAY;
}

function getUtcMonthStart(
  timestamp: number,
  monthInterval: 1 | 3,
): number {
  const date = new Date(timestamp * 1000);
  const year = date.getUTCFullYear();
  const month = date.getUTCMonth();

  const alignedMonth =
    Math.floor(month / monthInterval) * monthInterval;

  return Date.UTC(year, alignedMonth, 1) / 1000;
}

/**
 * Returns the UTC bucket start for a given timeframe.
 */
export function getTimeframeBucketStart(
  timestamp: number,
  timeframe: Timeframe,
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

    // Monday is the start of the week.
    const daysSinceMonday = (date.getUTCDay() + 6) % 7;

    return dayStart - daysSinceMonday * SECONDS_PER_DAY;
  }

  const interval = FIXED_INTERVALS[timeframe];

  if (interval === undefined) {
    throw new Error(`Unsupported timeframe: ${timeframe}`);
  }

  return Math.floor(timestamp / interval) * interval;
}

/**
 * Aggregate source OHLCV candles into a target timeframe.
 *
 * Open   = first source candle open
 * High   = highest source candle high
 * Low    = lowest source candle low
 * Close  = last source candle close
 * Volume = sum of source candle volumes
 */
export function aggregateCandles(
  candles: ChartData[],
  timeframe: Timeframe,
): ChartData[] {
  if (candles.length === 0) {
    return [];
  }

  const sortedCandles = [...candles].sort(
    (a, b) => a.timestamp - b.timestamp,
  );

  const result: ChartData[] = [];

  let currentBucket: number | null = null;
  let currentCandle: ChartData | null = null;

  for (const candle of sortedCandles) {
    if (
      !Number.isFinite(candle.timestamp) ||
      !Number.isFinite(candle.open) ||
      !Number.isFinite(candle.high) ||
      !Number.isFinite(candle.low) ||
      !Number.isFinite(candle.close) ||
      !Number.isFinite(candle.volume) ||
      candle.high < candle.low ||
      candle.volume < 0
    ) {
      continue;
    }

    const bucket = getTimeframeBucketStart(
      candle.timestamp,
      timeframe,
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
        candle.high,
      );

      currentCandle.low = Math.min(
        currentCandle.low,
        candle.low,
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
