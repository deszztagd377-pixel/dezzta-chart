import type { ChartData, Timeframe } from '../types';
import type {
  OhlcvBarDto,
  OhlcvSnapshotMessage,
  OhlcvSnapshotState,
  OhlcvTimeframe,
} from '../types/ohlcv';

export interface OhlcvSeriesIdentity {
  dataset: string;
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
  timeframe: Timeframe;
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

  const open = Number(value.open);
  const high = Number(value.high);
  const low = Number(value.low);
  const close = Number(value.close);
  const volume = Number(value.volume);
  if (![open, high, low, close, volume].every(Number.isFinite)) {
    throw new Error(`OHLCV bar ${index} exceeds chart numeric range.`);
  }
  if (volume < 0 || high < low || high < Math.max(open, close) || low > Math.min(open, close)) {
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
  let previousTimestamp = -1n;
  for (const [index, bar] of bars.entries()) {
    const timestamp = BigInt(bar.tsStartNs);
    if (timestamp <= previousTimestamp) {
      throw new Error(`OHLCV bars are not strictly chronological at index ${index}.`);
    }
    previousTimestamp = timestamp;
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
    bar.timeframe === identity.timeframe
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
