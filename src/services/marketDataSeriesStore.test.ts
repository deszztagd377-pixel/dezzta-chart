import { describe, expect, it } from 'vitest';
import { MarketDataSeriesStore } from './marketDataSeriesStore';

const nq = {
  provider: 'databento',
  seriesType: 'contract' as const,
  dataset: 'GLBX.MDP3',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'NQZ6',
  timeframe: '1m' as const,
};
const es = { ...nq, instrumentId: 456, rawSymbol: 'ESZ6' };
const bars = [
  { timestamp: 1_800_000_000, open: 100, high: 102, low: 99, close: 101, volume: 10 },
  { timestamp: 1_800_000_060, open: 101, high: 103, low: 100, close: 102, volume: 12 },
];

describe('keyed market-data series store', () => {
  it('keeps different canonical series snapshots and listeners isolated', () => {
    const store = new MarketDataSeriesStore();
    let nqNotifications = 0;
    let esNotifications = 0;
    store.subscribe(nq, () => { nqNotifications += 1; });
    store.subscribe(es, () => { esNotifications += 1; });

    store.publishSnapshot({ identity: nq, status: 'ready', bars });
    expect(store.getSnapshot(nq).bars).toEqual(bars);
    expect(store.getSnapshot(es).bars).toEqual([]);
    expect(store.getSnapshot(es).status).toBe('loading');
    expect(nqNotifications).toBe(1);
    expect(esNotifications).toBe(0);
    expect(store.getSeriesCount()).toBe(2);
  });

  it('shares one keyed snapshot between two panels subscribed to the same series', () => {
    const store = new MarketDataSeriesStore();
    let firstPanel = 0;
    let secondPanel = 0;
    store.subscribe(nq, () => { firstPanel += 1; });
    store.subscribe({ ...nq, provider: 'databento', calendarId: '', calendarVersion: '' }, () => {
      secondPanel += 1;
    });

    store.publishSnapshot({ identity: nq, status: 'ready', bars });
    expect(firstPanel).toBe(1);
    expect(secondPanel).toBe(1);
    expect(store.getSubscriberCount(nq)).toBe(2);
  });

  it('releases one panel idempotently without stopping another same-series panel', () => {
    const store = new MarketDataSeriesStore();
    let firstPanel = 0;
    let secondPanel = 0;
    const releaseFirst = store.subscribe(nq, () => { firstPanel += 1; });
    store.subscribe(nq, () => { secondPanel += 1; });

    store.publishSnapshot({ identity: nq, status: 'ready', bars });
    releaseFirst();
    releaseFirst();
    store.publishUpdate({
      identity: nq,
      bar: { ...bars[1], close: 102.5, high: 103, volume: 15 },
    });

    expect(firstPanel).toBe(1);
    expect(secondPanel).toBe(2);
    expect(store.getSubscriberCount(nq)).toBe(1);
    expect(store.getSnapshot(nq).bars[1].close).toBe(102.5);
  });

  it('updates only the selected series and inserts late bars chronologically', () => {
    const store = new MarketDataSeriesStore();
    let nqNotifications = 0;
    let esNotifications = 0;
    store.subscribe(nq, () => { nqNotifications += 1; });
    store.subscribe(es, () => { esNotifications += 1; });
    store.publishSnapshot({ identity: nq, status: 'ready', bars });
    store.publishSnapshot({ identity: es, status: 'ready', bars });

    store.publishUpdate({
      identity: nq,
      bar: { timestamp: 1_800_000_030, open: 100.5, high: 102, low: 100, close: 101.5, volume: 5 },
    });

    expect(store.getSnapshot(nq).bars.map((bar) => bar.timestamp)).toEqual([
      1_800_000_000, 1_800_000_030, 1_800_000_060,
    ]);
    expect(store.getSnapshot(es).bars).toEqual(bars);
    expect(nqNotifications).toBe(2);
    expect(esNotifications).toBe(1);
  });

  it('keeps series state isolated across all canonical identity dimensions', () => {
    const store = new MarketDataSeriesStore();
    const variants = [
      { ...nq, provider: 'alternate' },
      { ...nq, seriesType: 'continuous' as const },
      { ...nq, dataset: 'GLBX.MDP3.TEST' },
      { ...nq, publisherId: 2 },
      { ...nq, instrumentId: 124 },
      { ...nq, rawSymbol: 'ESZ6' },
      { ...nq, timeframe: '5m' as const },
      { ...nq, bucketPolicy: 'UTC_LEGACY' as const },
      { ...nq, calendarId: 'CME' },
      { ...nq, calendarVersion: '2026a' },
    ];
    store.publishSnapshot({ identity: nq, status: 'ready', bars });

    for (const variant of variants) {
      expect(store.getSnapshot(variant).bars).toHaveLength(0);
      expect(store.getSnapshot(variant).identity).toEqual(variant);
    }
    expect(store.getSnapshot(nq).bars).toEqual(bars);
    expect(store.getSeriesCount()).toBe(11);
  });

  it('does not expose mutable snapshot, bar, or identity references', () => {
    const store = new MarketDataSeriesStore();
    store.publishSnapshot({ identity: nq, status: 'ready', bars });
    const snapshot = store.getSnapshot(nq);

    expect(Object.isFrozen(snapshot)).toBe(true);
    expect(Object.isFrozen(snapshot.identity)).toBe(true);
    expect(Object.isFrozen(snapshot.bars)).toBe(true);
    expect(Object.isFrozen(snapshot.bars[0])).toBe(true);
    expect(() => {
      (snapshot.bars[0] as { close: number }).close = -1;
    }).toThrow();
    expect(store.getSnapshot(nq).bars[0].close).toBe(101);
  });

  it('rejects invalid updates without mutating the selected series or notifying listeners', () => {
    const store = new MarketDataSeriesStore();
    let notifications = 0;
    store.subscribe(nq, () => { notifications += 1; });
    store.publishSnapshot({ identity: nq, status: 'ready', bars });
    const before = store.getSnapshot(nq);
    notifications = 0;

    expect(() => store.publishUpdate({
      identity: es,
      bar: bars[0],
    })).toThrow(/active backend snapshot/);
    expect(() => store.publishUpdate({
      identity: nq,
      bar: { ...bars[1], low: 105 },
    })).toThrow(/OHLCV boundaries/);

    expect(store.getSnapshot(nq)).toBe(before);
    expect(notifications).toBe(0);
  });

  it('isolates listener failures so one panel cannot block another', () => {
    const store = new MarketDataSeriesStore();
    let healthyPanel = 0;
    store.subscribe(nq, () => { throw new Error('panel unmounted during notification'); });
    store.subscribe(nq, () => { healthyPanel += 1; });

    expect(() => store.publishSnapshot({ identity: nq, status: 'ready', bars })).not.toThrow();
    expect(healthyPanel).toBe(1);
  });

  it('does not let releasing the final listener erase a reusable series snapshot', () => {
    const store = new MarketDataSeriesStore();
    const release = store.subscribe(nq, () => {});
    store.publishSnapshot({ identity: nq, status: 'ready', bars });
    release();

    expect(store.getSubscriberCount(nq)).toBe(0);
    expect(store.getSnapshot(nq).bars).toEqual(bars);
    expect(store.getSnapshot(nq).status).toBe('ready');
  });
});
