import { describe, expect, it } from 'vitest';
import {
  MarketDataSeriesLeaseRegistry,
} from './marketDataSeriesLeaseRegistry';

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

describe('per-series chart-panel lease registry', () => {
  it('counts unique owners per canonical series and releases only the final owner', () => {
    const released: string[] = [];
    const registry = new MarketDataSeriesLeaseRegistry((identity) => {
      released.push(identity.rawSymbol);
    });
    const nqPanelA = registry.acquire(nq, 'panel-a');
    const nqPanelB = registry.acquire(nq, 'panel-b');
    const esPanelA = registry.acquire(es, 'panel-a');

    expect(registry.getOwnerCount(nq)).toBe(2);
    expect(registry.getOwnerCount(es)).toBe(1);
    expect(registry.getSeriesCount()).toBe(2);

    nqPanelA.release();
    expect(registry.getOwnerCount(nq)).toBe(1);
    expect(released).toEqual([]);

    nqPanelB.release();
    expect(registry.getOwnerCount(nq)).toBe(0);
    expect(registry.getSeriesCount()).toBe(1);
    expect(released).toEqual(['NQZ6']);

    esPanelA.release();
    expect(registry.getSeriesCount()).toBe(0);
    expect(released).toEqual(['NQZ6', 'ESZ6']);
  });

  it('makes stale cleanup harmless when a panel reacquires the same series', () => {
    const released: string[] = [];
    const registry = new MarketDataSeriesLeaseRegistry((identity) => {
      released.push(identity.rawSymbol);
    });
    const staleLease = registry.acquire(nq, 'panel-a');
    const currentLease = registry.acquire({ ...nq }, 'panel-a');

    expect(currentLease.generation).toBeGreaterThan(staleLease.generation);
    expect(registry.getOwnerCount(nq)).toBe(1);
    expect(registry.hasOwner(nq, 'panel-a')).toBe(true);

    staleLease.release();
    expect(registry.getOwnerCount(nq)).toBe(1);
    expect(released).toEqual([]);

    currentLease.release();
    expect(registry.getOwnerCount(nq)).toBe(0);
    expect(released).toEqual(['NQZ6']);
  });

  it('makes release idempotent and invokes final-owner cleanup exactly once', () => {
    let cleanupCalls = 0;
    const registry = new MarketDataSeriesLeaseRegistry(() => {
      cleanupCalls += 1;
    });
    const lease = registry.acquire(nq, 'panel-a');

    lease.release();
    lease.release();

    expect(cleanupCalls).toBe(1);
    expect(registry.getSeriesCount()).toBe(0);
  });

  it('keeps canonical series dimensions isolated even when owner IDs match', () => {
    const registry = new MarketDataSeriesLeaseRegistry();
    const nqLease = registry.acquire(nq, 'panel-a');
    const esLease = registry.acquire(es, 'panel-a');

    expect(registry.getOwnerCount(nq)).toBe(1);
    expect(registry.getOwnerCount(es)).toBe(1);
    expect(registry.hasOwner(nq, 'panel-a')).toBe(true);
    expect(registry.hasOwner(es, 'panel-a')).toBe(true);

    nqLease.release();
    expect(registry.getOwnerCount(nq)).toBe(0);
    expect(registry.getOwnerCount(es)).toBe(1);
    esLease.release();
  });

  it('rejects blank owner IDs and invalid series identities', () => {
    const registry = new MarketDataSeriesLeaseRegistry();
    expect(() => registry.acquire(nq, '  ')).toThrow(/owner ID/);
    expect(() => registry.acquire({ ...nq, instrumentId: 0 }, 'panel-a')).toThrow(/identity/);
    expect(registry.getSeriesCount()).toBe(0);
  });

  it('contains cleanup callback errors so release remains safe', () => {
    const registry = new MarketDataSeriesLeaseRegistry(() => {
      throw new Error('transport cleanup observer failed');
    });
    const lease = registry.acquire(nq, 'panel-a');

    expect(() => lease.release()).not.toThrow();
    expect(registry.getSeriesCount()).toBe(0);
  });
});
