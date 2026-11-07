import type { OhlcvBarDto, OhlcvTimeframe } from '../types/ohlcv';
import { parseOhlcvSnapshot } from '../utils/ohlcvAdapter';
import { getBucketPolicyForTimeframe } from '../utils/ohlcvBucketPolicy';

export interface OhlcvStreamSeriesIdentity {
  provider: string;
  seriesType: 'contract' | 'continuous';
  dataset: string;
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
  timeframe: OhlcvTimeframe;
  bucketPolicy?: 'UTC_LEGACY' | 'UTC_FIXED_V1';
  calendarId?: string;
  calendarVersion?: string;
}

/**
 * Versioned, provider-neutral OHLCV update.
 * sequence is scoped to streamId and is independent of the backend bar revision
 * sequence carried inside bar.sequence.
 */
export interface OhlcvStreamUpdateMessage {
  type: 'market_data.ohlcv.update';
  version: 1;
  streamId: string;
  eventId: string;
  sequence: number;
  emittedAtNs: string;
  operation: 'upsert';
  isFinal: boolean;
  series: OhlcvStreamSeriesIdentity;
  bar: OhlcvBarDto;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

function isPositiveSafeInteger(value: unknown): value is number {
  return typeof value === 'number' && Number.isSafeInteger(value) && value > 0;
}

function isNanosecondString(value: unknown): value is string {
  return typeof value === 'string' && /^\d+$/.test(value);
}

function sameSeries(
  left: OhlcvStreamSeriesIdentity,
  right: OhlcvStreamSeriesIdentity,
): boolean {
  return left.provider === right.provider &&
    left.seriesType === right.seriesType &&
    left.dataset === right.dataset &&
    left.publisherId === right.publisherId &&
    left.instrumentId === right.instrumentId &&
    left.rawSymbol === right.rawSymbol &&
    left.timeframe === right.timeframe &&
    (left.bucketPolicy ?? getBucketPolicyForTimeframe(left.timeframe)) === (right.bucketPolicy ?? getBucketPolicyForTimeframe(right.timeframe)) &&
    (left.calendarId ?? '') === (right.calendarId ?? '') &&
    (left.calendarVersion ?? '') === (right.calendarVersion ?? '');
}

/** Validate an untrusted WebSocket JSON payload before it reaches application state. */
export function parseOhlcvStreamUpdate(payload: unknown): OhlcvStreamUpdateMessage {
  if (!isRecord(payload) ||
      payload.type !== 'market_data.ohlcv.update' ||
      payload.version !== 1) {
    throw new Error('Unsupported OHLCV stream event type or version.');
  }
  if (!isNonEmptyString(payload.streamId) || !isNonEmptyString(payload.eventId)) {
    throw new Error('OHLCV stream event requires streamId and eventId.');
  }
  if (!isPositiveSafeInteger(payload.sequence)) {
    throw new Error('OHLCV stream sequence must be a positive safe integer.');
  }
  if (!isNanosecondString(payload.emittedAtNs)) {
    throw new Error('OHLCV stream emittedAtNs must be an unsigned nanosecond string.');
  }
  if (payload.operation !== 'upsert' || typeof payload.isFinal !== 'boolean') {
    throw new Error('OHLCV stream update operation or finality flag is invalid.');
  }
  if (!isRecord(payload.series)) {
    throw new Error('OHLCV stream series identity is missing.');
  }

  const series = payload.series;
  if (
    !isNonEmptyString(series.provider) ||
    !['contract', 'continuous'].includes(String(series.seriesType)) ||
    !isNonEmptyString(series.dataset) ||
    !isPositiveSafeInteger(series.publisherId) ||
    !isPositiveSafeInteger(series.instrumentId) ||
    !isNonEmptyString(series.rawSymbol) ||
    !isNonEmptyString(series.timeframe) ||
    (series.bucketPolicy !== undefined && !['UTC_LEGACY', 'UTC_FIXED_V1'].includes(String(series.bucketPolicy))) ||
    (series.calendarId !== undefined && series.calendarId !== '') ||
    (series.calendarVersion !== undefined && series.calendarVersion !== '')
  ) {
    throw new Error('OHLCV stream series identity is invalid.');
  }

  // Reuse the snapshot's strict decimal, timestamp, OHLCV-boundary and timeframe
  // validation. This keeps snapshot and streaming payload rules identical.
  const snapshot = parseOhlcvSnapshot({
    type: 'market_data.ohlcv.snapshot',
    version: 1,
    state: 'ready',
    timestampUnit: 'nanoseconds',
    priceRepresentation: 'decimal-string',
    bars: [payload.bar],
    detail: null,
    count: 1,
    truncated: false,
  });
  const bar = snapshot.bars[0];
  if (
    !isNonEmptyString(bar.provider) ||
    !['contract', 'continuous'].includes(String(bar.seriesType))
  ) {
    throw new Error('OHLCV stream bar provider or series type is invalid.');
  }
  const identity = series as unknown as OhlcvStreamSeriesIdentity;
  if (!sameSeries(identity, {
    provider: bar.provider,
    seriesType: bar.seriesType as 'contract' | 'continuous',
    dataset: bar.dataset,
    publisherId: bar.publisherId,
    instrumentId: bar.instrumentId,
    rawSymbol: bar.rawSymbol,
    timeframe: bar.timeframe,
    bucketPolicy: bar.bucketPolicy ?? getBucketPolicyForTimeframe(bar.timeframe),
    calendarId: bar.calendarId ?? '',
    calendarVersion: bar.calendarVersion ?? '',
  })) {
    throw new Error('OHLCV stream bar does not match its declared series identity.');
  }

  return {
    type: 'market_data.ohlcv.update',
    version: 1,
    streamId: payload.streamId,
    eventId: payload.eventId,
    sequence: payload.sequence,
    emittedAtNs: payload.emittedAtNs,
    operation: 'upsert',
    isFinal: payload.isFinal,
    series: identity,
    bar,
  };
}

export type OhlcvSequenceDecision =
  | { accepted: true; lastSequence: number }
  | { accepted: false; reason: 'duplicate' | 'stale' | 'gap' | 'stream_mismatch' | 'series_mismatch'; expectedSequence: number; receivedSequence: number };

/**
 * Per-subscription sequence gate. A gap is never silently accepted: the caller
 * must pause application and obtain a fresh snapshot before resetting the
 * baseline. The gate does not perform network recovery itself.
 */
export class OhlcvStreamSequenceGuard {
  private readonly streamId: string;
  private readonly series: Readonly<OhlcvStreamSeriesIdentity>;
  private lastSequence: number;

  constructor(
    streamId: string,
    series: OhlcvStreamSeriesIdentity,
    snapshotSequence: number,
  ) {
    if (!isNonEmptyString(streamId)) throw new Error('A streamId is required.');
    if (!Number.isSafeInteger(snapshotSequence) || snapshotSequence < 0) {
      throw new Error('Snapshot sequence must be a non-negative safe integer.');
    }
    this.streamId = streamId;
    this.series = Object.freeze({ ...series });
    this.lastSequence = snapshotSequence;
  }

  get watermark(): number {
    return this.lastSequence;
  }

  accept(event: OhlcvStreamUpdateMessage): OhlcvSequenceDecision {
    const expectedSequence = this.lastSequence + 1;
    const receivedSequence = event.sequence;
    if (event.streamId !== this.streamId) {
      return { accepted: false, reason: 'stream_mismatch', expectedSequence, receivedSequence };
    }
    if (!sameSeries(event.series, this.series)) {
      return { accepted: false, reason: 'series_mismatch', expectedSequence, receivedSequence };
    }
    if (receivedSequence <= this.lastSequence) {
      return {
        accepted: false,
        reason: receivedSequence === this.lastSequence ? 'duplicate' : 'stale',
        expectedSequence,
        receivedSequence,
      };
    }
    if (receivedSequence !== expectedSequence) {
      return { accepted: false, reason: 'gap', expectedSequence, receivedSequence };
    }

    this.lastSequence = receivedSequence;
    return { accepted: true, lastSequence: this.lastSequence };
  }

  /** Call only after a verified snapshot has supplied its matching watermark. */
  resetFromSnapshot(snapshotSequence: number): void {
    if (!Number.isSafeInteger(snapshotSequence) || snapshotSequence < 0) {
      throw new Error('Snapshot sequence must be a non-negative safe integer.');
    }
    this.lastSequence = snapshotSequence;
  }
}
