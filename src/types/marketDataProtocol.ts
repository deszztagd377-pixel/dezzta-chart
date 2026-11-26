/**
 * Provider-neutral OHLCV transport metadata.
 *
 * This contract is additive to the existing snapshot/update envelopes. It does
 * not introduce provider connectivity or imply that synthetic fixtures are live.
 */
import type { OhlcvBarDto, OhlcvBucketPolicy, OhlcvTimeframe } from './ohlcv';

export type OhlcvDataMode = 'synthetic' | 'provider';
export type OhlcvDataStatus =
  | 'synthetic_only'
  | 'live'
  | 'stale'
  | 'unavailable'
  | 'error';

export interface OhlcvProvenance {
  mode: OhlcvDataMode;
  dataStatus: OhlcvDataStatus;
  provider: string | null;
  dataset: string | null;
  asOfNs: string | null;
  providerConnected: boolean;
}

export interface OhlcvCanonicalSeriesIdentity {
  seriesKey: string;
  provider: string;
  seriesType: 'contract' | 'continuous';
  dataset: string;
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
  timeframe: OhlcvTimeframe;
  bucketPolicy?: OhlcvBucketPolicy;
  calendarId?: string;
  calendarVersion?: string;
}

export interface OhlcvDurableMetadata {
  generationId: string;
  highWaterCursor: string;
  retentionFloorCursor: string;
}

export interface OhlcvSnapshotDurableMetadata extends OhlcvDurableMetadata {
  snapshotDigest: string;
  provenance: OhlcvProvenance;
}

export interface OhlcvEventDurableMetadata {
  generationId: string;
  cursor: string;
  digest: string;
  provenance: OhlcvProvenance;
}

export interface OhlcvAckRequest {
  type: 'market_data.ack.request';
  version: 1;
  consumerId: string;
  series: OhlcvCanonicalSeriesIdentity;
  generationId: string;
  cursor: string;
  sequence: number;
  eventDigest: string;
  receiptVersion: number;
}

export interface OhlcvAckResponse {
  type: 'market_data.ack.response';
  version: 1;
  accepted: boolean;
  committedCursor: string;
  receiptVersion: number;
  committedAtNs: string;
  correlationId: string;
}

export type OhlcvProtocolErrorCode =
  | 'invalid_request'
  | 'invalid_series'
  | 'unsupported_version'
  | 'unauthorized'
  | 'forbidden'
  | 'ticket_expired'
  | 'ticket_replayed'
  | 'generation_mismatch'
  | 'cursor_invalid'
  | 'cursor_expired'
  | 'replay_limit_exceeded'
  | 'digest_mismatch'
  | 'ack_regression'
  | 'rate_limited'
  | 'temporarily_unavailable'
  | 'internal_error';

export interface OhlcvProtocolError {
  type: 'market_data.error';
  version: 1;
  code: OhlcvProtocolErrorCode;
  retryable: boolean;
  correlationId: string;
  message: string;
}

const CURSOR_PATTERN = /^(0|[1-9][0-9]*)$/;
const DIGEST_PATTERN = /^[0-9a-f]{64}$/;
const IDENTITY_PATTERN = /^[A-Za-z0-9._:-]{1,128}$/;

export function isCanonicalOhlcvCursor(value: unknown): value is string {
  return typeof value === 'string' && value.length <= 16 && CURSOR_PATTERN.test(value);
}

export function isOhlcvSha256(value: unknown): value is string {
  return typeof value === 'string' && DIGEST_PATTERN.test(value);
}

export function isValidOhlcvProvenance(value: unknown): value is OhlcvProvenance {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const item = value as Record<string, unknown>;
  const validModes = ['synthetic', 'provider'];
  const validStatuses = ['synthetic_only', 'live', 'stale', 'unavailable', 'error'];
  if (
    !validModes.includes(String(item.mode)) ||
    !validStatuses.includes(String(item.dataStatus)) ||
    !(item.provider === null || (typeof item.provider === 'string' && item.provider.length <= 128)) ||
    !(item.dataset === null || (typeof item.dataset === 'string' && item.dataset.length <= 128)) ||
    !(item.asOfNs === null || (typeof item.asOfNs === 'string' && /^\d{1,32}$/.test(item.asOfNs))) ||
    typeof item.providerConnected !== 'boolean'
  ) return false;

  if (item.mode === 'synthetic') {
    return item.dataStatus === 'synthetic_only' &&
      item.providerConnected === false &&
      item.provider === null;
  }
  return item.dataStatus !== 'synthetic_only';
}

export function isValidOhlcvDurableMetadata(value: unknown): value is OhlcvSnapshotDurableMetadata {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const item = value as Record<string, unknown>;
  return typeof item.generationId === 'string' && IDENTITY_PATTERN.test(item.generationId) &&
    isCanonicalOhlcvCursor(item.highWaterCursor) &&
    isCanonicalOhlcvCursor(item.retentionFloorCursor) &&
    BigInt(item.retentionFloorCursor) <= BigInt(item.highWaterCursor) &&
    isOhlcvSha256(item.snapshotDigest) &&
    isValidOhlcvProvenance(item.provenance);
}

/**
 * Stable digest encoding v1: UTF-8 JSON.stringify of a fixed-position array.
 * Object key ordering and whitespace are therefore excluded from the digest.
 */
export function canonicalOhlcvEventDigestInput(input: {
  series: OhlcvCanonicalSeriesIdentity;
  generationId: string;
  cursor: string;
  emittedAtNs: string;
  operation: 'upsert';
  isFinal: boolean;
  bar: OhlcvBarDto;
}): string {
  const s = input.series;
  const b = input.bar;
  return JSON.stringify([
    'dezzta-ohlcv-event-v1',
    [s.seriesKey, s.provider, s.seriesType, s.dataset, s.publisherId,
      s.instrumentId, s.rawSymbol, s.timeframe, s.bucketPolicy ?? '',
      s.calendarId ?? '', s.calendarVersion ?? ''],
    input.generationId,
    input.cursor,
    input.emittedAtNs,
    input.operation,
    input.isFinal,
    [b.dataset, b.publisherId, b.instrumentId, b.rawSymbol, b.timeframe,
      b.bucketPolicy ?? '', b.calendarId ?? '', b.calendarVersion ?? '',
      b.tsStartNs, b.open, b.high, b.low, b.close, b.volume, b.tsEventNs,
      b.tsReceivedNs, b.sequence, b.sequenceOrigin ?? '', b.provider ?? '',
      b.seriesType ?? '', b.origin ?? '', b.completeness ?? ''],
  ]);
}

export async function computeOhlcvEventDigest(input: Parameters<typeof canonicalOhlcvEventDigestInput>[0]): Promise<string> {
  const bytes = new TextEncoder().encode(canonicalOhlcvEventDigestInput(input));
  const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('');
}

export async function verifyOhlcvEventDigest(
  input: Parameters<typeof canonicalOhlcvEventDigestInput>[0],
  expectedDigest: string,
): Promise<boolean> {
  if (!isOhlcvSha256(expectedDigest)) return false;
  return (await computeOhlcvEventDigest(input)) === expectedDigest;
}
