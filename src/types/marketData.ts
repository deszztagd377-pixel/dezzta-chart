/**
 * Transport-neutral market-data contracts for DEZZTA CHART.
 *
 * These types describe the app-facing representation of Databento MBO data.
 * They do not claim to be a byte-for-byte DBN archive. Preserve the original
 * provider DBN records separately in the backend before mapping to this DTO.
 *
 * 64-bit timestamps, prices, and order IDs are strings on the JSON boundary
 * to avoid JavaScript Number precision loss.
 */

export type FuturesRoot = 'ES' | 'NQ' | 'GC';

export type MboAction = 'A' | 'C' | 'M' | 'R' | 'T' | 'F' | 'N';
export type MboSide = 'A' | 'B' | 'N';

export interface FuturesInstrument {
  root: FuturesRoot;
  productName: string;
  dataset: 'GLBX.MDP3';
  /** Resolved outright contract symbol, e.g. an expiry-specific CME symbol. */
  rawSymbol: string;
  instrumentId: number;
  publisherId: number;
  instrumentClass: 'F';
  /** ISO-8601 date/time when known; null if provider metadata omits it. */
  expiration: string | null;
  currency: string | null;
  /** Exact decimal string sourced from instrument definitions. */
  minPriceIncrement: string | null;
  /** Definition event timestamp in nanoseconds since Unix epoch. */
  definitionTsEventNs: string;
}

export interface DatabentoMboRecord {
  dataset: 'GLBX.MDP3';
  schema: 'mbo';
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
  tsEventNs: string;
  tsRecvNs: string;
  tsInDeltaNs: number;
  sequence: number;
  channelId: number;
  action: MboAction;
  side: MboSide;
  /** Signed Databento fixed-point integer; 1 unit = 1e-9 price. */
  priceRaw: string;
  size: number;
  /** uint64 venue order ID represented as a decimal string. */
  orderId: string;
  flags: number;
  rtype: 160;
}

export interface MarketDataEventEnvelope {
  type: 'market_data.mbo';
  version: 1;
  eventId: string;
  receivedAtNs: string;
  instrument: FuturesInstrument;
  record: DatabentoMboRecord;
}

export type MarketDataStreamState =
  | 'connecting'
  | 'live'
  | 'recovering'
  | 'degraded'
  | 'disconnected';

export interface MarketDataQuality {
  state: MarketDataStreamState;
  /** True only after a valid initial snapshot/replay has established book state. */
  bookSynchronized: boolean;
  /** Explicit gap count observed by the ingestion/recovery layer. */
  detectedGapCount: number;
  lastSequence: number | null;
  lastEventTsNs: string | null;
  lastReceiveTsNs: string | null;
  /** Human-readable diagnostic; must not contain credentials or secrets. */
  detail: string | null;
}

export interface MarketDataStatusMessage {
  type: 'market_data.status';
  version: 1;
  dataset: 'GLBX.MDP3';
  schema: 'mbo';
  instruments: FuturesRoot[];
  quality: MarketDataQuality;
}

/** Databento MBO flag bits used for data-quality and book-state handling. */
export const DATABENTO_MBO_FLAGS = {
  LAST: 1 << 7,
  TOP_OF_BOOK: 1 << 6,
  SNAPSHOT: 1 << 5,
  MBP: 1 << 4,
  BAD_TS_RECV: 1 << 3,
  MAYBE_BAD_BOOK: 1 << 2,
} as const;

/** Convert Databento's signed fixed-point price integer to a decimal number.
 * Use only at the presentation/calculation boundary; retain priceRaw upstream.
 */
export function databentoPriceToNumber(priceRaw: string): number {
  if (!/^-?\d+$/.test(priceRaw)) {
    throw new Error('Invalid Databento fixed-point price.');
  }

  const value = Number(priceRaw) / 1_000_000_000;
  if (!Number.isFinite(value)) {
    throw new Error('Databento price is outside the supported numeric range.');
  }

  return value;
}
