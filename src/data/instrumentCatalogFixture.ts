import type { InstrumentCatalogSnapshot } from '../types/instrumentCatalog';

/**
 * Honest offline UI fixture. It lists supported product roots only and
 * deliberately contains no invented expiry-specific contracts or prices.
 */
export const instrumentCatalogFixture: InstrumentCatalogSnapshot = {
  source: 'offline_fixture',
  state: 'definitions_unavailable',
  supportedProducts: [
    {
      root: 'ES',
      productName: 'E-mini S&P 500 Futures',
      dataset: 'GLBX.MDP3',
      metadataState: 'supported_root_only',
    },
    {
      root: 'NQ',
      productName: 'E-mini Nasdaq-100 Futures',
      dataset: 'GLBX.MDP3',
      metadataState: 'supported_root_only',
    },
    {
      root: 'GC',
      productName: 'Gold Futures',
      dataset: 'GLBX.MDP3',
      metadataState: 'supported_root_only',
    },
  ],
  contractCount: 0,
  contracts: [],
  note: 'Offline reference fixture. No live provider definitions or active contracts are loaded.',
};
