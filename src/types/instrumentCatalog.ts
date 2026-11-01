export type FuturesRoot = 'ES' | 'NQ' | 'GC';

export interface SupportedProduct {
  root: FuturesRoot;
  productName: string;
  dataset: 'GLBX.MDP3';
  metadataState: 'supported_root_only' | 'definitions_available';
}

export interface InstrumentCatalogSnapshot {
  source: 'offline_fixture';
  state: 'definitions_unavailable' | 'ready';
  supportedProducts: SupportedProduct[];
  contractCount: number;
  contracts: [];
  note: string;
}
