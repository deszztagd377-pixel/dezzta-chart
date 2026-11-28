import type { OhlcvBarDto, OhlcvTimeframe } from '../types/ohlcv';
import { parseOhlcvSnapshot } from '../utils/ohlcvAdapter';
import { getBucketPolicyForTimeframe } from '../utils/ohlcvBucketPolicy';
import { isOhlcvSha256, isValidOhlcvProvenance } from '../types/marketDataProtocol';

export interface OhlcvStreamSeriesIdentity {
  seriesKey?: string;
  provider: string;
  seriesType: 'contract' | 'continuous';
  dataset: string;
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
  timeframe: OhlcvTimeframe;
  bucketPolicy?: 'UTC_LEGACY' | 'UTC_FIXED_V1' | 'CME_SESSION_V1';
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
  cursor?: string;
  sequence: number;
  emittedAtNs: string;
  operation: 'upsert';
  isFinal: boolean;
  series: OhlcvStreamSeriesIdentity;
  bar: OhlcvBarDto;
  generationId?: string;
  digest?: string;
  provenance?: import('../types/marketDataProtocol').OhlcvProvenance;
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
  return (!left.seriesKey || !right.seriesKey || left.seriesKey === right.seriesKey) &&
    left.provider === right.provider &&
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
  if (payload.cursor !== undefined &&
      (typeof payload.cursor !== 'string' || !/^(0|[1-9][0-9]*)$/.test(payload.cursor))) {
    throw new Error('OHLCV durable cursor must be an unsigned decimal string.');
  }
  if (!isPositiveSafeInteger(payload.sequence)) {
    throw new Error('OHLCV stream sequence must be a positive safe integer.');
  }
  const hasGenerationId = payload.generationId !== undefined;
  const hasDigest = payload.digest !== undefined;
  if (hasGenerationId !== hasDigest) {
    throw new Error('OHLCV generationId and event digest must be provided together.');
  }
  if (hasGenerationId &&
      (typeof payload.generationId !== 'string' || !/^[A-Za-z0-9._:-]{1,128}$/.test(payload.generationId))) {
    throw new Error('OHLCV generationId is invalid.');
  }
  if (hasDigest && !isOhlcvSha256(payload.digest)) {
    throw new Error('OHLCV event digest must be lowercase SHA-256 hex.');
  }
  if (payload.provenance !== undefined && !isValidOhlcvProvenance(payload.provenance)) {
    throw new Error('OHLCV event provenance is invalid.');
  }
  if (hasGenerationId) {
    const provenance = payload.provenance as import('../types/marketDataProtocol').OhlcvProvenance | undefined;
    if (provenance?.mode === 'synthetic') {
      if (payload.generationId !== 'synthetic-v1' ||
          typeof payload.series !== 'object' || payload.series === null ||
          typeof (payload.series as Record<string, unknown>).seriesKey !== 'string' ||
          payload.streamId !== `synthetic:${(payload.series as Record<string, unknown>).seriesKey}`) {
        throw new Error('Synthetic OHLCV generation identity does not match its canonical stream.');
      }
    } else if (payload.generationId !== payload.streamId) {
      throw new Error('Production OHLCV generationId must match its subscription streamId.');
    }
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
  if (series.seriesKey !== undefined &&
      (typeof series.seriesKey !== 'string' || !/^[A-Za-z0-9._:-]{1,128}$/.test(series.seriesKey))) {
    throw new Error('OHLCV stream seriesKey is invalid.');
  }
  if (
    !isNonEmptyString(series.provider) ||
    !['contract', 'continuous'].includes(String(series.seriesType)) ||
    !isNonEmptyString(series.dataset) ||
    !isPositiveSafeInteger(series.publisherId) ||
    !isPositiveSafeInteger(series.instrumentId) ||
    !isNonEmptyString(series.rawSymbol) ||
    !isNonEmptyString(series.timeframe) ||
    (series.bucketPolicy !== undefined &&
      !['UTC_LEGACY', 'UTC_FIXED_V1', 'CME_SESSION_V1'].includes(String(series.bucketPolicy))) ||
    (series.calendarId !== undefined && typeof series.calendarId !== 'string') ||
    (series.calendarVersion !== undefined && typeof series.calendarVersion !== 'string') ||
    (series.bucketPolicy === 'CME_SESSION_V1' && (
      !['1d', '1w', '1M', '3M'].includes(String(series.timeframe)) ||
      !isNonEmptyString(series.calendarId) ||
      !isNonEmptyString(series.calendarVersion)
    )) ||
    (series.bucketPolicy !== 'CME_SESSION_V1' && (
      (series.calendarId !== undefined && series.calendarId !== '') ||
      (series.calendarVersion !== undefined && series.calendarVersion !== '')
    ))
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
    ...(typeof payload.cursor === 'string' ? { cursor: payload.cursor } : {}),
    ...(typeof payload.generationId === 'string' ? { generationId: payload.generationId } : {}),
    ...(typeof payload.digest === 'string' ? { digest: payload.digest } : {}),
    ...(payload.provenance !== undefined ? { provenance: payload.provenance as import('../types/marketDataProtocol').OhlcvProvenance } : {}),
    sequence: payload.sequence,
    emittedAtNs: payload.emittedAtNs,
    operation: 'upsert',
    isFinal: payload.isFinal,
    series: identity,
    bar,
  };
}



function canonicalizeDigestValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonicalizeDigestValue);
  if (isRecord(value)) {
    return Object.fromEntries(
      Object.keys(value).sort().map((key) => [key, canonicalizeDigestValue(value[key])]),
    );
  }
  return value;
}

const SHA256_K = new Uint32Array([
  0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2,
]);

function sha256Hex(input: Uint8Array): string {
  const bitLength = input.length * 8;
  const paddedLength = Math.ceil((input.length + 9) / 64) * 64;
  const bytes = new Uint8Array(paddedLength);
  bytes.set(input);
  bytes[input.length] = 0x80;
  const view = new DataView(bytes.buffer);
  view.setUint32(paddedLength - 8, Math.floor(bitLength / 0x100000000), false);
  view.setUint32(paddedLength - 4, bitLength >>> 0, false);

  const hash = new Uint32Array([
    0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
    0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19,
  ]);
  const words = new Uint32Array(64);
  const rotate = (value: number, bits: number) => (value >>> bits) | (value << (32 - bits));
  for (let offset = 0; offset < paddedLength; offset += 64) {
    for (let i = 0; i < 16; i++) words[i] = view.getUint32(offset + i * 4, false);
    for (let i = 16; i < 64; i++) {
      const x = words[i - 15], y = words[i - 2];
      const s0 = rotate(x, 7) ^ rotate(x, 18) ^ (x >>> 3);
      const s1 = rotate(y, 17) ^ rotate(y, 19) ^ (y >>> 10);
      words[i] = (words[i - 16] + s0 + words[i - 7] + s1) >>> 0;
    }
    let [a,b,c,d,e,f,g,h] = hash;
    for (let i = 0; i < 64; i++) {
      const s1 = rotate(e, 6) ^ rotate(e, 11) ^ rotate(e, 25);
      const choose = (e & f) ^ (~e & g);
      const t1 = (h + s1 + choose + SHA256_K[i] + words[i]) >>> 0;
      const s0 = rotate(a, 2) ^ rotate(a, 13) ^ rotate(a, 22);
      const majority = (a & b) ^ (a & c) ^ (b & c);
      const t2 = (s0 + majority) >>> 0;
      h=g; g=f; f=e; e=(d+t1)>>>0; d=c; c=b; b=a; a=(t1+t2)>>>0;
    }
    hash[0]=(hash[0]+a)>>>0; hash[1]=(hash[1]+b)>>>0;
    hash[2]=(hash[2]+c)>>>0; hash[3]=(hash[3]+d)>>>0;
    hash[4]=(hash[4]+e)>>>0; hash[5]=(hash[5]+f)>>>0;
    hash[6]=(hash[6]+g)>>>0; hash[7]=(hash[7]+h)>>>0;
  }
  return Array.from(hash, (word) => word.toString(16).padStart(8, '0')).join('');
}

/** Recompute the canonical SHA-256 event attestation synchronously before applying an update. */
export function verifyOhlcvStreamEventDigest(value: unknown): boolean {
  if (!isRecord(value) || typeof value.generationId !== 'string' ||
      typeof value.digest !== 'string' || !isOhlcvSha256(value.digest)) return false;
  const payload: Record<string, unknown> = { ...value };
  const expected = value.digest;
  delete payload.digest;
  const canonical = JSON.stringify(canonicalizeDigestValue(payload));
  return sha256Hex(new TextEncoder().encode(canonical)) === expected;
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
