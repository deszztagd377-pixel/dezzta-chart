import type { ChartData, Timeframe } from '../types';
import { getBucketPolicyForTimeframe } from './ohlcvBucketPolicy';
import type {
  OhlcvBarDto,
  OhlcvSnapshotMessage,
  OhlcvTimeframe,
} from '../types/ohlcv';

export interface OhlcvSeriesIdentity {
  dataset: string;
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
  timeframe: Timeframe;
  bucketPolicy?: 'UTC_LEGACY' | 'UTC_FIXED_V1';
  calendarId?: string;
  calendarVersion?: string;
}

const TIMEFRAMES: readonly OhlcvTimeframe[] = [
  '1s', '5s', '15s', '30s', '45s',
  '1m', '3m', '5m', '15m', '30m', '45m',
  '1h', '2h', '4h', '1d', '1w', '1M', '3M',
];

const DECIMAL_PATTERN = /^-?(?:0|[1-9]\d*)(?:\.\d+)?$/;
const UNSIGNED_INTEGER_PATTERN = /^\d+$/;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isDecimalString(value: unknown): value is string {
  return typeof value === 'string' && DECIMAL_PATTERN.test(value);
}

function isNanosecondString(value: unknown): value is string {
  return typeof value === 'string' && UNSIGNED_INTEGER_PATTERN.test(value);
}

function isSafeInteger(value: unknown): value is number {
  return typeof value === 'number' && Number.isSafeInteger(value) && value >= 0;
}

function decimalParts(value: string): { coefficient: bigint; scale: number } {
  const negative = value.startsWith('-');
  const unsigned = negative ? value.slice(1) : value;
  const [whole, fraction = ''] = unsigned.split('.');
  const magnitude = BigInt(`${whole}${fraction}`);
  return {
    coefficient: negative ? -magnitude : magnitude,
    scale: fraction.length,
  };
}

function compareDecimals(left: string, right: string): number {
  const a = decimalParts(left);
  const b = decimalParts(right);
  const scale = Math.max(a.scale, b.scale);
  const leftValue = a.coefficient * (10n ** BigInt(scale - a.scale));
  const rightValue = b.coefficient * (10n ** BigInt(scale - b.scale));
  return leftValue < rightValue ? -1 : leftValue > rightValue ? 1 : 0;
}

function validateBar(value: unknown, index: number): OhlcvBarDto {
  if (!isRecord(value)) throw new Error(`OHLCV bar ${index} must be an object.`);

  const requiredStrings = [
    'dataset', 'rawSymbol', 'tsStartNs', 'open', 'high', 'low',
    'close', 'volume', 'tsEventNs', 'tsReceivedNs', 'timeframe',
  ] as const;
  for (const key of requiredStrings) {
    if (typeof value[key] !== 'string' || value[key] === '') {
      throw new Error(`OHLCV bar ${index} has an invalid ${key}.`);
    }
  }

  if (!isSafeInteger(value.publisherId) || value.publisherId === 0) {
    throw new Error(`OHLCV bar ${index} has an invalid publisherId.`);
  }
  if (!isSafeInteger(value.instrumentId) || value.instrumentId === 0) {
    throw new Error(`OHLCV bar ${index} has an invalid instrumentId.`);
  }
  if (!isSafeInteger(value.sequence)) {
    throw new Error(`OHLCV bar ${index} has an invalid sequence.`);
  }
  if (!TIMEFRAMES.includes(value.timeframe as OhlcvTimeframe)) {
    throw new Error(`OHLCV bar ${index} has an unsupported timeframe.`);
  }
  if (value.bucketPolicy !== undefined && !['UTC_LEGACY', 'UTC_FIXED_V1'].includes(String(value.bucketPolicy))) {
    throw new Error(`OHLCV bar ${index} has an unsupported bucketPolicy.`);
  }
  if ((value.calendarId !== undefined && value.calendarId !== '') ||
      (value.calendarVersion !== undefined && value.calendarVersion !== '')) {
    throw new Error(`OHLCV bar ${index} has unsupported calendar identity.`);
  }
  if (!isNanosecondString(value.tsStartNs) ||
      !isNanosecondString(value.tsEventNs) ||
      !isNanosecondString(value.tsReceivedNs)) {
    throw new Error(`OHLCV bar ${index} has an invalid nanosecond timestamp.`);
  }

  for (const key of ['open', 'high', 'low', 'close', 'volume'] as const) {
    if (!isDecimalString(value[key])) {
      throw new Error(`OHLCV bar ${index} has an invalid decimal ${key}.`);
    }
  }

  const { open, high, low, close, volume } = value as Record<
    'open' | 'high' | 'low' | 'close' | 'volume',
    string
  >;
  // Validate decimal relationships with integer arithmetic; never round the
  // transport values through JavaScript Number before the chart boundary.
  if (
    compareDecimals(volume, '0') < 0 ||
    compareDecimals(high, low) < 0 ||
    compareDecimals(high, open) < 0 ||
    compareDecimals(high, close) < 0 ||
    compareDecimals(low, open) > 0 ||
    compareDecimals(low, close) > 0
  ) {
    throw new Error(`OHLCV bar ${index} violates OHLCV boundaries.`);
  }

  return value as unknown as OhlcvBarDto;
}

/** Runtime validation for the JSON boundary; DTO TypeScript types alone are not validation. */
export function parseOhlcvSnapshot(payload: unknown): OhlcvSnapshotMessage {
  if (!isRecord(payload)) throw new Error('OHLCV snapshot must be an object.');
  if (payload.type !== 'market_data.ohlcv.snapshot' || payload.version !== 1) {
    throw new Error('Unsupported OHLCV snapshot type or version.');
  }
  if (!['ready', 'unavailable', 'degraded'].includes(String(payload.state))) {
    throw new Error('OHLCV snapshot has an invalid state.');
  }
  if (payload.timestampUnit !== 'nanoseconds' ||
      payload.priceRepresentation !== 'decimal-string') {
    throw new Error('OHLCV snapshot uses an unsupported numeric representation.');
  }
  if (!Array.isArray(payload.bars)) throw new Error('OHLCV snapshot bars must be an array.');
  if (payload.detail !== null && typeof payload.detail !== 'string') {
    throw new Error('OHLCV snapshot detail must be a string or null.');
  }
  if (payload.count !== undefined && !isSafeInteger(payload.count)) {
    throw new Error('OHLCV snapshot count must be a non-negative safe integer.');
  }
  if (payload.truncated !== undefined && typeof payload.truncated !== 'boolean') {
    throw new Error('OHLCV snapshot truncated must be a boolean.');
  }
  const validFeedStates = ['connecting', 'live', 'recovering', 'degraded', 'disconnected'];
  if (payload.feedState !== undefined && !validFeedStates.includes(String(payload.feedState))) {
    throw new Error('OHLCV snapshot has an invalid feedState.');
  }

  const bars = payload.bars.map(validateBar);
  const previousBySeries = new Map<string, bigint>();
  for (const [index, bar] of bars.entries()) {
    const seriesKey = [
      bar.dataset,
      bar.publisherId,
      bar.instrumentId,
      bar.rawSymbol,
      bar.timeframe,
      bar.bucketPolicy ?? 'UTC_LEGACY',
      bar.calendarId ?? '',
      bar.calendarVersion ?? '',
    ].join('|');
    const timestamp = BigInt(bar.tsStartNs);
    const previousTimestamp = previousBySeries.get(seriesKey);
    if (previousTimestamp !== undefined && timestamp <= previousTimestamp) {
      throw new Error(`OHLCV bars are not strictly chronological within a series at index ${index}.`);
    }
    previousBySeries.set(seriesKey, timestamp);
  }

  return { ...payload, bars } as unknown as OhlcvSnapshotMessage;
}

/**
 * Converts exact transport strings to chart numbers only at the rendering edge.
 * A full series identity is required to prevent mixing contracts/timeframes.
 */
export function toChartCandles(
  snapshot: OhlcvSnapshotMessage,
  identity: OhlcvSeriesIdentity,
): ChartData[] {
  if (snapshot.state === 'unavailable') return [];

  const matchingBars = snapshot.bars.filter((bar) =>
    bar.dataset === identity.dataset &&
    bar.publisherId === identity.publisherId &&
    bar.instrumentId === identity.instrumentId &&
    bar.rawSymbol === identity.rawSymbol &&
    bar.timeframe === identity.timeframe &&
    (bar.bucketPolicy ?? getBucketPolicyForTimeframe(bar.timeframe)) === (identity.bucketPolicy ?? getBucketPolicyForTimeframe(identity.timeframe)) &&
    (bar.calendarId ?? '') === (identity.calendarId ?? '') &&
    (bar.calendarVersion ?? '') === (identity.calendarVersion ?? '')
  );

  return matchingBars.map((bar, index) => {
    const timestampSecondsBigInt = BigInt(bar.tsStartNs) / 1_000_000_000n;
    const timestamp = Number(timestampSecondsBigInt);
    const candle: ChartData = {
      timestamp,
      open: Number(bar.open),
      high: Number(bar.high),
      low: Number(bar.low),
      close: Number(bar.close),
      volume: Number(bar.volume),
    };

    if (!Number.isSafeInteger(timestamp) || timestamp < 0) {
      throw new Error(`OHLCV bar ${index} timestamp is outside chart range.`);
    }
    if (![candle.open, candle.high, candle.low, candle.close, candle.volume].every(Number.isFinite)) {
      throw new Error(`OHLCV bar ${index} cannot be represented by the chart engine.`);
    }
    return candle;
  });
}
