import { afterEach, describe, expect, it } from 'vitest';
import {
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

  it('rejects invalid OHLCV updates without mutating the current snapshot', () => {
    publishMarketDataSnapshot({ identity, status: 'ready', bars });
    const before = getMarketDataSnapshot();
    expect(() => publishMarketDataUpdate({
      identity,
      bar: { ...bars[1], low: 105 },
    })).toThrow(/OHLCV boundaries/);
    expect(getMarketDataSnapshot()).toBe(before);
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
