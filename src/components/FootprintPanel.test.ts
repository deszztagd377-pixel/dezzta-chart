import { describe, expect, it } from 'vitest';
import { getFootprintCellMetrics } from './FootprintPanel';

describe('getFootprintCellMetrics', () => {
  it('calculates ask-side delta, total volume and delta percentage', () => {
    expect(getFootprintCellMetrics({ price: 4034.25, bid: 0, ask: 15000, side: 'ask' })).toEqual({
      total: 15000,
      delta: 15000,
      deltaPercent: 100,
      imbalance: 'ASK DOMINANT',
    });
  });

  it('calculates negative delta for bid-dominant levels', () => {
    const result = getFootprintCellMetrics({ price: 4033.75, bid: 47000, ask: 24000, side: 'bid' });
    expect(result.total).toBe(71000);
    expect(result.delta).toBe(-23000);
    expect(result.deltaPercent).toBeCloseTo(-32.394366, 5);
    expect(result.imbalance).toBe('BALANCED');
  });

  it('handles an empty level without division by zero', () => {
    expect(getFootprintCellMetrics({ price: 1, bid: 0, ask: 0, side: 'bid' })).toEqual({
      total: 0,
      delta: 0,
      deltaPercent: 0,
      imbalance: 'BALANCED',
    });
  });
});

// @vitest-environment jsdom
import { createElement } from 'react';
import { act } from 'react-dom/test-utils';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach } from 'vitest';
import FootprintPanel from './FootprintPanel';

const mountedRoots: Root[] = [];

afterEach(() => {
  act(() => {
    for (const root of mountedRoots.splice(0)) root.unmount();
  });
  document.body.innerHTML = '';
});

it('updates the selected details when an ask cell is tapped', () => {
  const host = document.createElement('div');
  document.body.appendChild(host);
  const root = createRoot(host);
  mountedRoots.push(root);

  act(() => root.render(createElement(FootprintPanel)));

  const cell = host.querySelector<HTMLButtonElement>(
    'button[aria-label="Select ask 15k at 4034.25"]',
  );
  expect(cell).not.toBeNull();
  act(() => cell!.click());

  expect(cell!.getAttribute('aria-pressed')).toBe('true');
  const details = host.querySelector('[aria-label="Selected footprint cell details"]');
  expect(details?.textContent).toContain('4034.25');
  expect(details?.textContent).toContain('ASK CELL SELECTED');
});

it('updates the selected details when a bid cell is tapped', () => {
  const host = document.createElement('div');
  document.body.appendChild(host);
  const root = createRoot(host);
  mountedRoots.push(root);

  act(() => root.render(createElement(FootprintPanel)));

  const cell = host.querySelector<HTMLButtonElement>(
    'button[aria-label="Select bid 19.3k at 4034.75"]',
  );
  expect(cell).not.toBeNull();
  act(() => cell!.click());

  expect(cell!.getAttribute('aria-pressed')).toBe('true');
  const details = host.querySelector('[aria-label="Selected footprint cell details"]');
  expect(details?.textContent).toContain('4034.75');
  expect(details?.textContent).toContain('BID CELL SELECTED');
});
