// @vitest-environment jsdom
import { createElement } from 'react';
import { act } from 'react-dom/test-utils';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
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

beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean })
    .IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(() => {
  for (const root of roots.splice(0)) {
    act(() => root.unmount());
  }
  marketDataSeriesStore.reset(firstIdentity, 'unavailable', 'test cleanup');
  marketDataSeriesStore.reset(secondIdentity, 'unavailable', 'test cleanup');
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean })
    .IS_REACT_ACT_ENVIRONMENT = false;
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
    expect(observed[observed.length - 1]?.identity).toBeNull();
    expect(observed[observed.length - 1]?.bars).toHaveLength(0);
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
  it('isolates simultaneous React chart panels and preserves the remaining panel on unmount', () => {
    marketDataSeriesStore.reset(firstIdentity, 'loading', 'isolated test start');
    marketDataSeriesStore.reset(secondIdentity, 'loading', 'isolated test start');
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);

    function Probe({ identity }: { identity: MarketSeriesIdentity }) {
      const snapshot = useMarketDataSeriesSnapshot(identity);
      const latestClose = snapshot.bars[snapshot.bars.length - 1]?.close ?? '-';
      return createElement('span', null, `${identity.rawSymbol}:${snapshot.status}:${latestClose};`);
    }

    act(() => root.render(createElement(
      'div',
      null,
      createElement(Probe, { identity: firstIdentity }),
      createElement(Probe, { identity: secondIdentity }),
    )));
    expect(marketDataSeriesStore.getSubscriberCount(firstIdentity)).toBe(1);
    expect(marketDataSeriesStore.getSubscriberCount(secondIdentity)).toBe(1);

    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity,
      status: 'ready',
      bars,
    }));
    expect(container.textContent).toContain('HOOK_A:ready:101;');
    expect(container.textContent).toContain('HOOK_B:loading:-;');

    act(() => marketDataSeriesStore.publishSnapshot({
      identity: secondIdentity,
      status: 'ready',
      bars,
    }));
    expect(container.textContent).toContain('HOOK_A:1:1;');
    expect(container.textContent).toContain('HOOK_B:ready:101;');

    act(() => root.render(createElement(
      'div',
      null,
      createElement(Probe, { identity: firstIdentity }),
    )));
    expect(marketDataSeriesStore.getSubscriberCount(firstIdentity)).toBe(1);
    expect(marketDataSeriesStore.getSubscriberCount(secondIdentity)).toBe(0);

    act(() => marketDataSeriesStore.publishUpdate({
      identity: firstIdentity,
      bar: { ...bars[0], close: 101.5, high: 102, volume: 11 },
    }));
    expect(container.textContent).toContain('HOOK_A:ready:101.5;');
    expect(container.textContent).not.toContain('HOOK_B:');
  });

});
