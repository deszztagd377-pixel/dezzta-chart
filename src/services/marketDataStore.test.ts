import { afterEach, describe, expect, it } from 'vitest';
import type { MarketSeriesIdentity } from './marketDataStore';
import {
  getMarketSeriesIdentityKey,
  MAX_MARKET_DATA_BARS_PER_SERIES,
  isSameMarketSeriesIdentity,
  getMarketDataSnapshot,
  publishMarketDataSnapshot,
  publishMarketDataUpdate,
  resetMarketDataSnapshot,
  subscribeMarketData,
} from './marketDataStore';

const identity = {
  dataset: 'GLBX.MDP3',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'NQZ6',
  timeframe: '1m' as const,
};
const bars = [
  { timestamp: 1_800_000_000, open: 100, high: 102, low: 99, close: 101, volume: 10 },
  { timestamp: 1_800_000_060, open: 101, high: 103, low: 100, close: 102, volume: 12 },
];

afterEach(() => resetMarketDataSnapshot(null, 'demo', 'test reset'));

describe('shared market data store', () => {
  it('uses one normalized, collision-safe canonical key across store and stream ownership', () => {
    const explicitDefaults = {
      ...identity,
      provider: 'databento',
      seriesType: 'contract' as const,
      bucketPolicy: 'UTC_FIXED_V1' as const,
      calendarId: '',
      calendarVersion: '',
    };
    expect(getMarketSeriesIdentityKey(identity)).toBe(getMarketSeriesIdentityKey(explicitDefaults));
    expect(isSameMarketSeriesIdentity(identity, explicitDefaults)).toBe(true);
    const distinctDimensions: MarketSeriesIdentity[] = [
      { ...identity, provider: 'other-provider' },
      { ...identity, seriesType: 'continuous' },
      { ...identity, dataset: 'GLBX.MDP3.TEST' },
      { ...identity, publisherId: 2 },
      { ...identity, instrumentId: 124 },
      { ...identity, rawSymbol: 'ESZ6' },
      { ...identity, timeframe: '5m' },
      { ...identity, bucketPolicy: 'UTC_LEGACY' },
      { ...identity, calendarId: 'CME' },
      { ...identity, calendarVersion: '2026a' },
    ];
    for (const distinctIdentity of distinctDimensions) {
      expect(isSameMarketSeriesIdentity(identity, distinctIdentity)).toBe(false);
      expect(getMarketSeriesIdentityKey(identity)).not.toBe(getMarketSeriesIdentityKey(distinctIdentity));
    }

    const delimiterLeft = { ...identity, dataset: 'A|B', rawSymbol: 'C' };
    const delimiterRight = { ...identity, dataset: 'A', rawSymbol: 'B|C' };
    expect(getMarketSeriesIdentityKey(delimiterLeft)).not.toBe(getMarketSeriesIdentityKey(delimiterRight));
  });

  it('publishes immutable exact-series backend bars for subscribers', () => {
    let notifications = 0;
    const unsubscribe = subscribeMarketData(() => { notifications += 1; });
    publishMarketDataSnapshot({ identity, status: 'ready', bars, detail: 'validated' });
    const snapshot = getMarketDataSnapshot();
    unsubscribe();

    expect(snapshot.identity).toEqual(identity);
    expect(snapshot.status).toBe('ready');
    expect(snapshot.source).toBe('backend');
    expect(snapshot.bars).toEqual(bars);
    expect(snapshot.lastChange).toEqual({ type: 'snapshot' });
    expect(Object.isFrozen(snapshot)).toBe(true);
    expect(Object.isFrozen(snapshot.bars)).toBe(true);
    expect(notifications).toBe(1);
  });

  it('clears old bars synchronously on contract/timeframe changes', () => {
    publishMarketDataSnapshot({ identity, status: 'ready', bars });
    resetMarketDataSnapshot({ ...identity, rawSymbol: 'ESZ6' }, 'loading', 'switching');
    expect(getMarketDataSnapshot().bars).toHaveLength(0);
    expect(getMarketDataSnapshot().identity?.rawSymbol).toBe('ESZ6');
    expect(getMarketDataSnapshot().status).toBe('loading');
  });

  it('never publishes DEMO or unavailable bars as indicator input', () => {
    expect(() => publishMarketDataSnapshot({ identity, status: 'demo', bars })).toThrow();
    expect(() => publishMarketDataSnapshot({ identity, status: 'unavailable', bars })).toThrow();
  });

  it('rejects backend bars without exact identity or with invalid chronology/OHLCV', () => {
    expect(() => publishMarketDataSnapshot({ identity: null, status: 'ready', bars })).toThrow();
    expect(() => publishMarketDataSnapshot({
      identity, status: 'ready', bars: [bars[1], bars[0]],
    })).toThrow();
    expect(() => publishMarketDataSnapshot({
      identity, status: 'ready', bars: [{ ...bars[0], volume: -1 }],
    })).toThrow();
  });


  it('applies an incremental candle revision by timestamp and notifies subscribers', () => {
    publishMarketDataSnapshot({ identity, status: 'ready', bars });
    let notifications = 0;
    const unsubscribe = subscribeMarketData(() => { notifications += 1; });
    const revisionBeforeUpdate = getMarketDataSnapshot().revision;

    publishMarketDataUpdate({
      identity,
      bar: { ...bars[1], close: 102.5, high: 103, volume: 15 },
    });
    const revised = getMarketDataSnapshot();
    expect(revised.bars).toHaveLength(2);
    expect(revised.bars[1].close).toBe(102.5);
    expect(revised.revision).toBe(revisionBeforeUpdate + 1);
    expect(revised.lastChange).toEqual({ type: 'update', bar: { ...bars[1], close: 102.5, high: 103, volume: 15 } });
    expect(notifications).toBe(1);

    publishMarketDataUpdate({
      identity,
      bar: { timestamp: 1_800_000_030, open: 100.5, high: 102, low: 100, close: 101.5, volume: 5 },
    });
    expect(getMarketDataSnapshot().bars.map((bar) => bar.timestamp)).toEqual([
      1_800_000_000, 1_800_000_030, 1_800_000_060,
    ]);
    expect(notifications).toBe(2);
    unsubscribe();
  });

  it('rejects incremental updates for another series or a non-backend state', () => {
    publishMarketDataSnapshot({ identity, status: 'ready', bars });
    expect(() => publishMarketDataUpdate({
      identity: { ...identity, rawSymbol: 'ESZ6' },
      bar: bars[0],
    })).toThrow(/identity/);

    resetMarketDataSnapshot(identity, 'loading', 'switching');
    expect(() => publishMarketDataUpdate({ identity, bar: bars[0] })).toThrow(/active backend snapshot/);
  });

  it('rejects updates that cross bucket-policy identity boundaries', () => {
    const fixedIdentity = { ...identity, bucketPolicy: 'UTC_FIXED_V1' as const };
    const legacyIdentity = { ...identity, bucketPolicy: 'UTC_LEGACY' as const };
    publishMarketDataSnapshot({ identity: fixedIdentity, status: 'ready', bars });
    expect(() => publishMarketDataUpdate({
      identity: legacyIdentity,
      bar: bars[0],
    })).toThrow(/identity/);
    expect(getMarketDataSnapshot().identity?.bucketPolicy).toBe('UTC_FIXED_V1');
  });

  it('accepts versioned CME session identities only for daily-or-higher buckets', () => {
    const cmeIdentity: MarketSeriesIdentity = {
      ...identity,
      timeframe: '1d',
      bucketPolicy: 'CME_SESSION_V1',
      calendarId: 'CME_EQUITY_INDEX',
      calendarVersion: '2026.11.1',
    };
    publishMarketDataSnapshot({ identity: cmeIdentity, status: 'ready', bars });
    expect(getMarketDataSnapshot().identity).toEqual(cmeIdentity);

    const nextRelease = { ...cmeIdentity, calendarVersion: '2026.11.2' };
    expect(isSameMarketSeriesIdentity(cmeIdentity, nextRelease)).toBe(false);
    expect(getMarketSeriesIdentityKey(cmeIdentity)).not.toBe(getMarketSeriesIdentityKey(nextRelease));
  });

  it('rejects unsupported or malformed series identity metadata without mutating state', () => {
    const invalidIdentities = [
      { ...identity, calendarId: 'CME', calendarVersion: '2026a' },
      { ...identity, provider: '   ' },
      { ...identity, seriesType: 'unsupported' },
      { ...identity, bucketPolicy: 'CME_SESSION_V1' },
      { ...identity, timeframe: 'invalid', bucketPolicy: 'UTC_FIXED_V1' },
    ] as unknown as MarketSeriesIdentity[];

    for (const invalidIdentity of invalidIdentities) {
      expect(() => publishMarketDataSnapshot({
        identity: invalidIdentity,
        status: 'loading',
        detail: 'invalid identity fixture',
      })).toThrow();
    }
    expect(getMarketDataSnapshot().identity).toBeNull();

    publishMarketDataSnapshot({ identity, status: 'ready', bars });
    const before = getMarketDataSnapshot();
    expect(() => publishMarketDataUpdate({
      identity: {
        ...identity,
        calendarId: 'CME',
        calendarVersion: '2026a',
      },
      bar: bars[0],
    })).toThrow(/UTC bucket policies/);
    expect(getMarketDataSnapshot()).toBe(before);
  });

  it('rejects invalid OHLCV updates without mutating the current snapshot', () => {
    publishMarketDataSnapshot({ identity, status: 'ready', bars });
    const before = getMarketDataSnapshot();
    expect(() => publishMarketDataUpdate({
      identity,
      bar: { ...bars[1], low: 105 },
    })).toThrow(/OHLCV boundaries/);
    expect(getMarketDataSnapshot()).toBe(before);
  });

  it('bounds legacy live history at the backend hard limit and structurally shares unchanged bars', () => {
    const largeBars = Array.from({ length: MAX_MARKET_DATA_BARS_PER_SERIES }, (_, index) => ({
      timestamp: 1_800_000_000 + index * 60,
      open: 100,
      high: 102,
      low: 99,
      close: 101,
      volume: 10,
    }));
    publishMarketDataSnapshot({ identity, status: 'ready', bars: largeBars });
    const before = getMarketDataSnapshot();
    const incoming = {
      timestamp: 1_800_000_000 + MAX_MARKET_DATA_BARS_PER_SERIES * 60,
      open: 101,
      high: 103,
      low: 100,
      close: 102,
      volume: 11,
    };

    publishMarketDataUpdate({ identity, bar: incoming });
    const after = getMarketDataSnapshot();
    expect(after.bars).toHaveLength(MAX_MARKET_DATA_BARS_PER_SERIES);
    expect(after.bars[0]).toBe(before.bars[1]);
    expect(after.bars[after.bars.length - 1].timestamp).toBe(incoming.timestamp);
    expect(Object.isFrozen(after.bars[after.bars.length - 1])).toBe(true);
    expect(after.lastChange.type).toBe('update');
    if (after.lastChange.type === 'update') {
      expect(after.lastChange.bar).toBe(after.bars[after.bars.length - 1]);
    }

    const stable = getMarketDataSnapshot();
    expect(() => publishMarketDataUpdate({
      identity,
      bar: { ...bars[0], timestamp: stable.bars[0].timestamp - 60 },
    })).toThrow(/older than the retained bar window/);
    expect(getMarketDataSnapshot()).toBe(stable);
  });

  it('rejects legacy snapshots larger than the server hard limit', () => {
    const oversized = Array.from({ length: MAX_MARKET_DATA_BARS_PER_SERIES + 1 }, (_, index) => ({
      timestamp: 1_800_000_000 + index * 60,
      open: 100,
      high: 102,
      low: 99,
      close: 101,
      volume: 10,
    }));
    expect(() => publishMarketDataSnapshot({ identity, status: 'ready', bars: oversized })).toThrow(/retention limit/);
    expect(getMarketDataSnapshot().identity).toBeNull();
  });

  it('increments revision and notifies subscribers on each publication', () => {
    let count = 0;
    const unsubscribe = subscribeMarketData(() => { count += 1; });
    const before = getMarketDataSnapshot().revision;
    resetMarketDataSnapshot(identity, 'loading', 'loading');
    resetMarketDataSnapshot(identity, 'unavailable', 'empty');
    unsubscribe();
    expect(getMarketDataSnapshot().revision).toBe(before + 2);
    expect(count).toBe(2);
  });
});
