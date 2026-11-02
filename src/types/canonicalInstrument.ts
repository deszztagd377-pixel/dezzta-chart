/**
 * Provider-neutral canonical instrument contract.
 *
 * canonicalId is registry-assigned and persisted; it is never derived from a
 * ticker, venue label, or provider instrument ID. Provider mappings remain a
 * separate concern.
 */

export type AssetClass =
  | 'equity'
  | 'etf'
  | 'crypto'
  | 'future'
  | 'option'
  | 'fx'
  | 'index';

export type InstrumentType =
  | 'stock'
  | 'etf'
  | 'spot'
  | 'perpetual'
  | 'future'
  | 'option'
  | 'fx_pair'
  | 'index';

export interface CanonicalInstrument {
  canonicalId: string;
  assetClass: AssetClass;
  instrumentType: InstrumentType;
  symbol: string;
  venue: string;
  name: string | null;
  baseCurrency: string | null;
  quoteCurrency: string | null;
  settlementCurrency: string | null;
  expirationDate: string | null;
  /** Exact positive decimal strings; never parse through Number for identity metadata. */
  contractMultiplier: string | null;
  tickSize: string | null;
  quantityIncrement: string | null;
  optionRight: 'call' | 'put' | null;
  strikePrice: string | null;
  underlyingCanonicalId: string | null;
  sessionCalendarId: string | null;
  isActive: boolean;
}
