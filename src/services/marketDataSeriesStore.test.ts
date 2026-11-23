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
    ];
    store.publishSnapshot({ identity: nq, status: 'ready', bars });

    for (const variant of variants) {
      expect(store.getSnapshot(variant).bars).toHaveLength(0);
      expect(store.getSnapshot(variant).identity).toEqual(variant);
    }
    expect(store.getSnapshot(nq).bars).toEqual(bars);
    expect(store.getSeriesCount()).toBe(9);
    expect(() => store.getSnapshot({ ...nq, calendarId: 'CME' })).toThrow(/UTC bucket policies/);
    expect(() => store.getSnapshot({ ...nq, calendarVersion: '2026a' })).toThrow(/UTC bucket policies/);

    const cmeIdentity = {
      ...nq,
      timeframe: '1d' as const,
      bucketPolicy: 'CME_SESSION_V1' as const,
      calendarId: 'CME_EQUITY_INDEX',
      calendarVersion: '2026.11.1',
    };
    store.publishSnapshot({ identity: cmeIdentity, status: 'ready', bars });
    expect(store.getSnapshot(cmeIdentity).bars).toEqual(bars);
    expect(store.getSnapshot({
      ...cmeIdentity,
      calendarVersion: '2026.11.2',
    }).bars).toHaveLength(0);
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

  it('evicts the least-recently-used inactive series but pins active chart subscriptions', () => {
    const store = new MarketDataSeriesStore(2);
    const releaseNq = store.subscribe(nq, () => {});
    store.publishSnapshot({ identity: es, status: 'ready', bars });

    const ym = { ...nq, instrumentId: 789, rawSymbol: 'YMZ6' };
    store.publishSnapshot({ identity: ym, status: 'ready', bars });

    expect(store.getSeriesCount()).toBe(2);
    expect(store.hasSeries(nq)).toBe(true);
    expect(store.hasSeries(es)).toBe(false);
    expect(store.hasSeries(ym)).toBe(true);
    expect(store.getSnapshot(ym).bars).toEqual(bars);
    expect(store.getSubscriberCount(nq)).toBe(1);

    releaseNq();
  });

  it('rejects new series when every cache entry is pinned by active panels', () => {
    const store = new MarketDataSeriesStore(2);
    const releaseNq = store.subscribe(nq, () => {});
    const releaseEs = store.subscribe(es, () => {});
    const ym = { ...nq, instrumentId: 789, rawSymbol: 'YMZ6' };

    expect(() => store.getSnapshot(ym)).toThrow(/capacity is exhausted/);
    expect(store.getSeriesCount()).toBe(2);
    expect(store.getSnapshot(nq).status).toBe('loading');
    expect(store.getSnapshot(es).status).toBe('loading');

    releaseNq();
    releaseEs();
    expect(store.getSnapshot(ym).status).toBe('loading');
    expect(store.getSeriesCount()).toBe(2);
  });

  it('validates bounded-store capacity at construction', () => {
    expect(() => new MarketDataSeriesStore(0)).toThrow(/positive safe integer/);
    expect(() => new MarketDataSeriesStore(1.5)).toThrow(/positive safe integer/);
    expect(new MarketDataSeriesStore(3).getCapacity()).toBe(3);
  });

  it('does not evict a valid series when a rejected write targets an unknown series', () => {
    const store = new MarketDataSeriesStore(1);
    store.publishSnapshot({ identity: nq, status: 'ready', bars });

    expect(() => store.publishSnapshot({
      identity: es,
      status: 'ready',
      bars: [],
    })).toThrow(/cannot be ready without validated bars/);
    expect(() => store.publishUpdate({
      identity: es,
      bar: bars[0],
    })).toThrow(/active backend snapshot/);

    expect(store.hasSeries(nq)).toBe(true);
    expect(store.hasSeries(es)).toBe(false);
    expect(store.getSnapshot(nq).bars).toEqual(bars);
    expect(store.getSeriesCount()).toBe(1);
  });

  it('provides stable render-pure reads without allocating entries or changing LRU order', () => {
    const store = new MarketDataSeriesStore(2);
    const missingBeforeSubscribe = store.peekSnapshot(nq);
    expect(store.peekSnapshot(nq)).toBe(missingBeforeSubscribe);
    expect(missingBeforeSubscribe.identity).toBeNull();
    expect(store.getSeriesCount()).toBe(0);

    store.publishSnapshot({ identity: nq, status: 'ready', bars });
    store.publishSnapshot({ identity: es, status: 'ready', bars });
    const nqSnapshot = store.peekSnapshot(nq);
    expect(nqSnapshot.bars).toEqual(bars);

    // A pure render read must not make NQ more recent than ES.
    const ym = { ...nq, instrumentId: 789, rawSymbol: 'YMZ6' };
    store.publishSnapshot({ identity: ym, status: 'ready', bars });

    expect(store.hasSeries(nq)).toBe(false);
    expect(store.hasSeries(es)).toBe(true);
    expect(store.hasSeries(ym)).toBe(true);
    expect(store.getSeriesCount()).toBe(2);
  });

  it('bounds each series to its configured bar window and reuses unchanged frozen bars', () => {
    const store = new MarketDataSeriesStore(2, 2);
    const threeBars = [
      bars[0],
      bars[1],
      { timestamp: 1_800_000_120, open: 102, high: 104, low: 101, close: 103, volume: 14 },
    ];
    store.publishSnapshot({ identity: nq, status: 'ready', bars: threeBars.slice(0, 2) });
    const before = store.getSnapshot(nq);

    store.publishUpdate({ identity: nq, bar: threeBars[2] });
    const after = store.getSnapshot(nq);

    expect(after.bars).toHaveLength(2);
    expect(after.bars[0]).toBe(before.bars[1]);
    expect(after.bars[1].timestamp).toBe(threeBars[2].timestamp);
    expect(Object.isFrozen(after.bars[1])).toBe(true);
    expect(after.lastChange.type).toBe('update');
    if (after.lastChange.type === 'update') {
      expect(after.lastChange.bar).toBe(after.bars[1]);
    }

    const stableSnapshot = store.getSnapshot(nq);
    expect(() => store.publishUpdate({
      identity: nq,
      bar: { ...bars[0], timestamp: 1_799_999_940 },
    })).toThrow(/older than the retained per-series bar window/);
    expect(store.getSnapshot(nq)).toBe(stableSnapshot);
  });

  it('rejects snapshots larger than the configured per-series bar window', () => {
    const store = new MarketDataSeriesStore(2, 1);
    expect(() => store.publishSnapshot({ identity: nq, status: 'ready', bars })).toThrow(/retention limit/);
    expect(store.hasSeries(nq)).toBe(false);
  });

  it('rejects per-series bar capacities above the server hard limit', () => {
    expect(() => new MarketDataSeriesStore(2, 5_001)).toThrow(/between 1 and 5000/);
    expect(new MarketDataSeriesStore(2, 2).getBarCapacity()).toBe(2);
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
