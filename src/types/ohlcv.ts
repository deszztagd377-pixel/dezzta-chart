/**
 * Canonical OHLCV transport DTO.
 *
 * Nanosecond timestamps and decimal OHLCV values remain strings across JSON
 * boundaries. Convert to chart-engine numbers only at the rendering adapter,
 * never in the ingestion or transport layer.
 */

export type OhlcvTimeframe =
  | '1s' | '5s' | '15s' | '30s' | '45s'
  | '1m' | '3m' | '5m' | '15m' | '30m' | '45m'
  | '1h' | '2h' | '4h' | '1d' | '1w' | '1M' | '3M';

export interface OhlcvBarDto {
  dataset: string;
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
  timeframe: OhlcvTimeframe;
  /** UTC bucket start, Unix nanoseconds encoded as a decimal string. */
  tsStartNs: string;
  /** Exact decimal strings; do not parse to Number in the transport layer. */
  open: string;
  high: string;
  low: string;
  close: string;
  volume: string;
  /** Provider event and backend receive timestamps are intentionally distinct. */
  tsEventNs: string;
  tsReceivedNs: string;
  sequence: number;
}

export type OhlcvSnapshotState = 'ready' | 'unavailable' | 'degraded';

export interface OhlcvSnapshotMessage {
  type: 'market_data.ohlcv.snapshot';
  version: 1;
  state: OhlcvSnapshotState;
  timestampUnit: 'nanoseconds';
  priceRepresentation: 'decimal-string';
  bars: OhlcvBarDto[];
  detail: string | null;
}
