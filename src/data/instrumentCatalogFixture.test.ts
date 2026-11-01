import { describe, expect, it } from 'vitest';
import { instrumentCatalogFixture } from '../data/instrumentCatalogFixture';

describe('instrument catalog UI fixture', () => {
  it('contains only the explicitly supported product roots', () => {
    expect(instrumentCatalogFixture.supportedProducts.map((item) => item.root))
      .toEqual(['ES', 'NQ', 'GC']);
  });

  it('does not fabricate expiry-specific contracts', () => {
    expect(instrumentCatalogFixture.contractCount).toBe(0);
    expect(instrumentCatalogFixture.contracts).toEqual([]);
    expect(instrumentCatalogFixture.state).toBe('definitions_unavailable');
  });

  it('clearly identifies itself as offline fixture data', () => {
    expect(instrumentCatalogFixture.source).toBe('offline_fixture');
    expect(instrumentCatalogFixture.note).toContain('No live provider definitions');
  });
});
