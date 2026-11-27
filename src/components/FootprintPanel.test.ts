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
