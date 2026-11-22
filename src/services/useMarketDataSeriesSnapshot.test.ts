// @vitest-environment jsdom
import { createElement } from 'react';
import { act } from 'react-dom/test-utils';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, describe, expect, it } from 'vitest';
import type { MarketDataSnapshot, MarketSeriesIdentity } from './marketDataStore';
import { marketDataSeriesStore } from './marketDataSeriesStore';
import { useMarketDataSeriesSnapshot } from './useMarketDataSeriesSnapshot';

const firstIdentity: MarketSeriesIdentity = {
  dataset: 'HOOK.TEST',
  publisherId: 91,
  instrumentId: 901,
  rawSymbol: 'HOOK_A',
  timeframe: '1m',
};
const secondIdentity: MarketSeriesIdentity = {
  ...firstIdentity,
  instrumentId: 902,
  rawSymbol: 'HOOK_B',
};
const bars = [
  { timestamp: 1_800_000_000, open: 100, high: 102, low: 99, close: 101, volume: 10 },
];

const roots: Root[] = [];

afterEach(() => {
  for (const root of roots.splice(0)) {
    act(() => root.unmount());
  }
  marketDataSeriesStore.reset(firstIdentity, 'unavailable', 'test cleanup');
  marketDataSeriesStore.reset(secondIdentity, 'unavailable', 'test cleanup');
});

describe('useMarketDataSeriesSnapshot', () => {
  it('returns a stable empty state when no series is selected', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);
    const observed: MarketDataSnapshot[] = [];

    function Probe() {
      const snapshot = useMarketDataSeriesSnapshot(null);
      observed.push(snapshot);
      return createElement('span', null, snapshot.status);
    }

    act(() => root.render(createElement(Probe)));
    expect(container.textContent).toBe('demo');
    expect(observed.at(-1)?.identity).toBeNull();
    expect(observed.at(-1)?.bars).toHaveLength(0);
  });

  it('subscribes by canonical key and rerenders only for the selected series', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);
    let selectedIdentity = firstIdentity;

    function Probe() {
      const snapshot = useMarketDataSeriesSnapshot(selectedIdentity);
      return createElement('span', null, `${snapshot.status}:${snapshot.bars.length}`);
    }

    act(() => root.render(createElement(Probe)));
    expect(marketDataSeriesStore.getSubscriberCount(firstIdentity)).toBe(1);
    expect(marketDataSeriesStore.getSubscriberCount(secondIdentity)).toBe(0);

    act(() => {
      marketDataSeriesStore.publishSnapshot({
        identity: firstIdentity,
        status: 'ready',
        bars,
      });
    });
    expect(container.textContent).toBe('ready:1');

    act(() => {
      marketDataSeriesStore.publishSnapshot({
        identity: secondIdentity,
        status: 'ready',
        bars,
      });
    });
    expect(container.textContent).toBe('ready:1');

    act(() => {
      selectedIdentity = { ...firstIdentity };
      root.render(createElement(Probe));
    });
    expect(marketDataSeriesStore.getSubscriberCount(firstIdentity)).toBe(1);

    act(() => {
      selectedIdentity = secondIdentity;
      root.render(createElement(Probe));
    });
    expect(marketDataSeriesStore.getSubscriberCount(firstIdentity)).toBe(0);
    expect(marketDataSeriesStore.getSubscriberCount(secondIdentity)).toBe(1);
    expect(container.textContent).toBe('ready:1');
  });
});
