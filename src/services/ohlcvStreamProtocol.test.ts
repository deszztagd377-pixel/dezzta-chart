import { describe, expect, it } from 'vitest';
import {
  OhlcvStreamSequenceGuard,
  parseOhlcvStreamUpdate,
  type OhlcvStreamUpdateMessage,
} from './ohlcvStreamProtocol';

const series = {
  dataset: 'GLBX.MDP3',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'ESZ6',
  timeframe: '1s',
};

const bar = {
  dataset: 'GLBX.MDP3',
  provider: 'databento',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'ESZ6',
  seriesType: 'contract',
  timeframe: '1s',
  tsStartNs: '1793577600000000000',
  open: '6000.125',
  high: '6001.250',
  low: '5999.875',
  close: '6000.750',
  volume: '12',
  tsEventNs: '1793577600999000000',
  tsReceivedNs: '1793577601000000000',
  sequence: 7,
  sequenceOrigin: 'local',
  origin: 'provider',
  completeness: 'complete',
};

function event(overrides: Record<string, unknown> = {}): OhlcvStreamUpdateMessage {
  return parseOhlcvStreamUpdate({
    type: 'market_data.ohlcv.update',
    version: 1,
    streamId: 'stream-es-1s-a',
    eventId: 'event-8',
    sequence: 8,
    emittedAtNs: '1793577601000000000',
    operation: 'upsert',
    isFinal: true,
    series,
    bar,
    ...overrides,
  });
}

describe('parseOhlcvStreamUpdate', () => {
  it('accepts a valid versioned update with exact series identity', () => {
    const parsed = event();
    expect(parsed.type).toBe('market_data.ohlcv.update');
    expect(parsed.series).toEqual(series);
    expect(parsed.bar.open).toBe('6000.125');
  });

  it('rejects unsupported versions and missing event identity', () => {
    expect(() => event({ version: 2 })).toThrow(/type or version/i);
    expect(() => event({ eventId: '' })).toThrow(/streamId and eventId/i);
  });

  it('rejects unsafe sequence and invalid nanosecond timestamps', () => {
    expect(() => event({ sequence: Number.MAX_SAFE_INTEGER + 1 })).toThrow(/sequence/i);
    expect(() => event({ emittedAtNs: '1.5' })).toThrow(/emittedAtNs/i);
  });

  it('rejects an invalid operation or non-boolean finality', () => {
    expect(() => event({ operation: 'delete' })).toThrow(/operation/i);
    expect(() => event({ isFinal: 'true' })).toThrow(/operation/i);
  });

  it('rejects a bar whose identity differs from the declared stream series', () => {
    expect(() => event({ bar: { ...bar, instrumentId: 999 } })).toThrow(/does not match/i);
  });

  it('reuses snapshot validation for malformed OHLCV values', () => {
    expect(() => event({ bar: { ...bar, high: '5990' } })).toThrow(/OHLCV boundaries/i);
  });
});

describe('OhlcvStreamSequenceGuard', () => {
  it('accepts only the next sequence after the snapshot watermark', () => {
    const guard = new OhlcvStreamSequenceGuard('stream-es-1s-a', series, 7);
    expect(guard.accept(event())).toEqual({ accepted: true, lastSequence: 8 });
    expect(guard.watermark).toBe(8);
  });

  it('identifies duplicates and stale updates without advancing the watermark', () => {
    const guard = new OhlcvStreamSequenceGuard('stream-es-1s-a', series, 8);
    expect(guard.accept(event({ sequence: 8 })).reason).toBe('duplicate');
    expect(guard.accept(event({ sequence: 6 })).reason).toBe('stale');
    expect(guard.watermark).toBe(8);
  });

  it('detects a gap and refuses to advance until snapshot recovery', () => {
    const guard = new OhlcvStreamSequenceGuard('stream-es-1s-a', series, 7);
    const decision = guard.accept(event({ sequence: 10 }));
    expect(decision).toMatchObject({
      accepted: false,
      reason: 'gap',
      expectedSequence: 8,
      receivedSequence: 10,
    });
    expect(guard.watermark).toBe(7);
    guard.resetFromSnapshot(9);
    expect(guard.accept(event({ sequence: 10 }))).toEqual({ accepted: true, lastSequence: 10 });
  });

  it('rejects events from another stream or instrument', () => {
    const guard = new OhlcvStreamSequenceGuard('stream-es-1s-a', series, 7);
    expect(guard.accept(event({ streamId: 'other-stream' })).reason).toBe('stream_mismatch');
    expect(guard.accept(event({
      series: { ...series, instrumentId: 999 },
      bar: { ...bar, instrumentId: 999 },
    })).reason).toBe('series_mismatch');
    expect(guard.watermark).toBe(7);
  });

  it('validates snapshot watermarks before resetting', () => {
    const guard = new OhlcvStreamSequenceGuard('stream-es-1s-a', series, 7);
    expect(() => guard.resetFromSnapshot(-1)).toThrow(/snapshot sequence/i);
    expect(() => new OhlcvStreamSequenceGuard('stream-es-1s-a', series, 1.5))
      .toThrow(/snapshot sequence/i);
  });
});
