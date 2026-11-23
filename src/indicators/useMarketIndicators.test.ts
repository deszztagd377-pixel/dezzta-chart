// @vitest-environment jsdom
import { createElement } from 'react';
import { act } from 'react-dom/test-utils';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import type { MarketSeriesIdentity } from '../services/marketDataStore';
import { marketDataSeriesStore } from '../services/marketDataSeriesStore';
import { useMarketIndicators } from './useMarketIndicators';

const firstIdentity: MarketSeriesIdentity = {
  dataset: 'INDICATOR.HOOK.TEST',
  publisherId: 91,
  instrumentId: 901,
  rawSymbol: 'IND_A',
  timeframe: '1m',
};
const secondIdentity: MarketSeriesIdentity = {
  ...firstIdentity,
  instrumentId: 902,
  rawSymbol: 'IND_B',
};
const makeBars = (base: number) => Array.from({ length: 40 }, (_, index) => ({
  timestamp: 1_800_000_000 + index * 60,
  open: base + index,
  high: base + index + 2,
  low: base + index - 1,
  close: base + index + 1,
  volume: 10 + index,
}));

const roots: Root[] = [];

beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean })
    .IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(() => {
  for (const root of roots.splice(0)) act(() => root.unmount());
  marketDataSeriesStore.reset(firstIdentity, 'loading', 'test cleanup');
  marketDataSeriesStore.reset(secondIdentity, 'loading', 'test cleanup');
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean })
    .IS_REACT_ACT_ENVIRONMENT = false;
});

describe('useMarketIndicators keyed series integration', () => {
  it('returns no indicator output without a selected backend series', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);

    function Probe() {
      const result = useMarketIndicators(null);
      return createElement('span', null, result.indicators === null ? 'empty' : 'unexpected');
    }

    act(() => root.render(createElement(Probe)));
    expect(container.textContent).toBe('empty');
  });

  it('calculates indicators from the exact selected keyed snapshot', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);

    function Probe() {
      const result = useMarketIndicators(firstIdentity);
      const sma = result.indicators?.sma20[39];
      return createElement('span', null, [
        result.source,
        result.status,
        result.indicators?.sma20.length ?? 0,
        sma ?? 'null',
      ].join(':'));
    }

    act(() => root.render(createElement(Probe)));
    expect(container.textContent).toBe('none:loading:0:null');

    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity,
      status: 'ready',
      bars: makeBars(100),
    }));
    expect(container.textContent).toContain('backend:ready:40:');
    expect(marketDataSeriesStore.getSubscriberCount(firstIdentity)).toBe(1);
  });

  it('recalculates from a new immutable snapshot revision after a live bar update', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);

    function Probe() {
      const result = useMarketIndicators(firstIdentity);
      const latestSma = result.indicators?.sma20.slice(-1)[0] ?? 'empty';
      return createElement('span', null, `${result.revision}:${latestSma}`);
    }

    act(() => root.render(createElement(Probe)));
    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity,
      status: 'ready',
      bars: makeBars(100),
    }));
    expect(container.textContent).toBe('1:130.5');

    act(() => marketDataSeriesStore.publishUpdate({
      identity: firstIdentity,
      bar: {
        timestamp: 1_800_002_400,
        open: 200,
        high: 202,
        low: 199,
        close: 201,
        volume: 1,
      },
    }));
    expect(container.textContent).toBe('2:134.5');
  });

  it('keeps simultaneous panel calculations isolated by canonical series', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);

    function Probe({ identity }: { identity: MarketSeriesIdentity }) {
      const result = useMarketIndicators(identity);
      const latestSma = result.indicators?.sma20[39] ?? 'pending';
      return createElement('span', null, `${identity.rawSymbol}:${latestSma};`);
    }

    act(() => root.render(createElement(
      'div',
      null,
      createElement(Probe, { identity: firstIdentity }),
      createElement(Probe, { identity: secondIdentity }),
    )));
    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity, status: 'ready', bars: makeBars(100),
    }));
    expect(container.textContent).toContain('IND_A:');
    expect(container.textContent).toContain('IND_B:pending;');

    act(() => marketDataSeriesStore.publishSnapshot({
      identity: secondIdentity, status: 'ready', bars: makeBars(200),
    }));
    expect(container.textContent).not.toContain('pending');
    expect(marketDataSeriesStore.getSubscriberCount(firstIdentity)).toBe(1);
    expect(marketDataSeriesStore.getSubscriberCount(secondIdentity)).toBe(1);
  });

  it('shares one frozen calculation result across panels on the same snapshot revision', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);
    const observed: Array<ReturnType<typeof useMarketIndicators>['indicators']> = [];

    function Probe() {
      const result = useMarketIndicators(firstIdentity);
      observed.push(result.indicators);
      return createElement('span', null, result.indicators ? 'calculated' : 'pending');
    }

    act(() => root.render(createElement(
      'div',
      null,
      createElement(Probe),
      createElement(Probe),
    )));
    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity, status: 'ready', bars: makeBars(100),
    }));

    const computed = observed.filter((value) => value !== null);
    expect(computed).toHaveLength(2);
    expect(computed[0]).toBe(computed[1]);
    expect(Object.isFrozen(computed[0])).toBe(true);
    expect(Object.isFrozen(computed[0]?.sma20)).toBe(true);
    expect(Object.isFrozen(computed[0]?.macd[0])).toBe(true);
  });

  it('keeps degraded backend indicators but clears demo and error snapshots', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);

    function Probe() {
      const result = useMarketIndicators(firstIdentity);
      return createElement('span', null, [
        result.status,
        result.source,
        result.indicators ? 'calculated' : 'empty',
      ].join(':'));
    }

    act(() => root.render(createElement(Probe)));

    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity,
      status: 'ready',
      bars: makeBars(100),
    }));
    expect(container.textContent).toBe('ready:backend:calculated');

    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity,
      status: 'degraded',
      bars: makeBars(100),
      detail: 'Synthetic test degradation state.',
    }));
    expect(container.textContent).toBe('degraded:backend:calculated');

    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity,
      status: 'demo',
      detail: 'Demo data is not an accepted indicator source.',
    }));
    expect(container.textContent).toBe('demo:demo:empty');

    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity,
      status: 'error',
      detail: 'Backend series is unavailable.',
    }));
    expect(container.textContent).toBe('error:none:empty');
  });

  it('clears indicator output when the selected series becomes unavailable', () => {
    const container = document.createElement('div');
    const root = createRoot(container);
    roots.push(root);

    function Probe() {
      const result = useMarketIndicators(firstIdentity);
      return createElement('span', null, result.indicators ? 'calculated' : 'cleared');
    }

    act(() => root.render(createElement(Probe)));
    act(() => marketDataSeriesStore.publishSnapshot({
      identity: firstIdentity, status: 'ready', bars: makeBars(100),
    }));
    expect(container.textContent).toBe('calculated');

    act(() => marketDataSeriesStore.reset(firstIdentity, 'unavailable', 'series changed'));
    expect(container.textContent).toBe('cleared');
  });
});
