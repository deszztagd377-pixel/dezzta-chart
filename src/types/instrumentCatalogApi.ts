export type InstrumentRoot = 'ES' | 'NQ' | 'GC';

export interface SupportedInstrumentProduct {
  root: InstrumentRoot;
  product_name: string;
}

export interface FuturesContractDto {
  root: InstrumentRoot;
  product_name: string;
  dataset: string;
  raw_symbol: string;
  instrument_id: number;
  publisher_id: number;
  instrument_class: 'F';
  expiration: string;
  currency: string | null;
  min_price_increment: string | null;
  definition_ts_event_ns: string;
  provider: string;
  series_type: 'contract';
  /** Null until an exact active provider mapping exists in the durable registry. */
  canonical_instrument_id: string | null;
  /** Canonical session calendar; version is null unless exactly one pinned release is loaded. */
  session_calendar_id?: string | null;
  session_calendar_version?: string | null;
}

export interface InstrumentCatalogResponse {
  dataset: string;
  state: 'definitions_unavailable' | 'ready';
  supported_products: SupportedInstrumentProduct[];
  contract_count: number;
  contracts: FuturesContractDto[];
  selection_policy: string;
  requested_root?: InstrumentRoot;
}
