import { describe, expect, it } from 'vitest';
import {
  canonicalOhlcvEventDigestInput,
  computeOhlcvEventDigest,
  isCanonicalOhlcvCursor,
  isOhlcvSha256,
  isValidOhlcvDurableMetadata,
  isValidOhlcvProvenance,
  verifyOhlcvEventDigest,
} from './marketDataProtocol';

const series = {
  seriesKey: 'synthetic:DEMO:ES:1m',
  provider: 'synthetic',
  seriesType: 'contract' as const,
  dataset: 'DEMO',
  publisherId: 1,
  instrumentId: 2,
  rawSymbol: 'ESZ6',
  timeframe: '1m' as const,
  bucketPolicy: 'UTC_LEGACY' as const,
};
const bar = {
  dataset: 'DEMO',
  publisherId: 1,
  instrumentId: 2,
  rawSymbol: 'ESZ6',
  timeframe: '1m' as const,
  bucketPolicy: 'UTC_LEGACY' as const,
  tsStartNs: '1700000060000000000',
  open: '100.00',
  high: '101.00',
  low: '99.00',
  close: '100.50',
  volume: '10',
  tsEventNs: '1700000060000000000',
  tsReceivedNs: '1700000061000000000',
  sequence: 51,
  sequenceOrigin: 'local' as const,
  provider: 'synthetic',
  seriesType: 'contract' as const,
  origin: 'derived' as const,
  completeness: 'complete' as const,
};
const provenance = {
  mode: 'synthetic' as const,
  dataStatus: 'synthetic_only' as const,
  provider: null,
  dataset: 'DEMO',
  asOfNs: '1700000061000000000',
  providerConnected: false,
};
const eventInput = {
  series,
  generationId: 'synthetic-v1',
  cursor: '51',
  emittedAtNs: '1700000061000000000',
  operation: 'upsert' as const,
  isFinal: true,
  bar,
};

describe('provider-neutral OHLCV protocol metadata', () => {
  it('accepts only canonical unsigned cursors', () => {
    expect(isCanonicalOhlcvCursor('0')).toBe(true);
    expect(isCanonicalOhlcvCursor('51')).toBe(true);
    expect(isCanonicalOhlcvCursor('051')).toBe(false);
    expect(isCanonicalOhlcvCursor('-1')).toBe(false);
    expect(isCanonicalOhlcvCursor('1.0')).toBe(false);
    expect(isCanonicalOhlcvCursor('9'.repeat(17))).toBe(false);
  });

  it('keeps synthetic provenance explicitly disconnected from providers', () => {
    expect(isValidOhlcvProvenance(provenance)).toBe(true);
    expect(isValidOhlcvProvenance({ ...provenance, dataStatus: 'live' })).toBe(false);
    expect(isValidOhlcvProvenance({ ...provenance, providerConnected: true })).toBe(false);
    expect(isValidOhlcvProvenance({ ...provenance, provider: 'exchange' })).toBe(false);
  });

  it('validates snapshot durable metadata and retention bounds', () => {
    const valid = {
      generationId: 'synthetic-v1',
      highWaterCursor: '51',
      retentionFloorCursor: '1',
      snapshotDigest: 'a'.repeat(64),
      provenance,
    };
    expect(isValidOhlcvDurableMetadata(valid)).toBe(true);
    expect(isValidOhlcvDurableMetadata({ ...valid, retentionFloorCursor: '52' })).toBe(false);
    expect(isValidOhlcvDurableMetadata({ ...valid, snapshotDigest: 'A'.repeat(64) })).toBe(false);
  });

  it('uses a fixed-position canonical JSON encoding with a stable SHA-256 vector', async () => {
    expect(canonicalOhlcvEventDigestInput(eventInput)).toContain('dezzta-ohlcv-event-v1');
    const digest = await computeOhlcvEventDigest(eventInput);
    expect(digest).toBe('8d2a1a633a68a836fb9b7a6194da7020347d42d557e3c321877869198ecceb55');
    expect(isOhlcvSha256(digest)).toBe(true);
    expect(await verifyOhlcvEventDigest(eventInput, digest)).toBe(true);
    expect(await verifyOhlcvEventDigest({ ...eventInput, cursor: '52' }, digest)).toBe(false);
    expect(await verifyOhlcvEventDigest(eventInput, 'A'.repeat(64))).toBe(false);
  });
});
