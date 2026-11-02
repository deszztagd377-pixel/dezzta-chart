# DEZZTA CHART — Market Data Contract v1

Status: initial contract definition; not yet connected to a live provider or client.

## Scope

Initial CME futures products:
- ES — E-mini S&P 500 Futures
- NQ — E-mini Nasdaq-100 Futures
- GC — Gold Futures

Provider target: Databento, dataset `GLBX.MDP3`, schema `mbo`.

## Provider integration decision

Use the official Databento Python client for the first backend implementation candidate. Databento's official quickstart documents Python support for Live subscriptions; the repository's current application is React/TypeScript, so the backend will be a separate service rather than placing provider credentials or the Live connection in the browser bundle.

This is an implementation direction, not a claim that a backend has been built or deployed. Before adding runtime dependencies, pin and verify supported Python, Databento client, and WebSocket server versions in a reproducible backend environment.

## Instrument resolution

The product roots are not fixed-expiry contract symbols. Resolve contracts from point-in-time instrument definitions and symbology. Parent symbols such as `ES.FUT` can include both outright futures and futures spreads; inspect the instrument class and retain only outright future instruments for the primary chart selector. Store raw symbol, instrument ID, publisher ID, expiration, tick increment, and definition timestamp. Never assume an instrument ID is globally permanent or a contract month remains active.

Continuous symbology may be useful for a rolling chart, but it is not identical to a specific tradable expiry contract. The UI/API must identify whether a selected instrument is a specific expiry or a continuous series. Do not silently back-adjust prices.

## Wire contract

The TypeScript definitions in `src/types/marketData.ts` are the first app-facing DTO contract.

- `MarketDataEventEnvelope` carries one MBO record plus resolved instrument metadata.
- `MarketDataStatusMessage` reports connection and book-quality state independently of event flow.
- Provider 64-bit values (`ts_event`, `ts_recv`, `order_id`, and fixed-point `price`) cross the JSON boundary as decimal strings. JavaScript numbers cannot exactly represent all 64-bit integers.
- Databento price is a signed fixed-point integer where one unit equals 1e-9. Keep the raw integer string; convert only at a deliberate presentation/calculation boundary.
- MBO actions: A=Add, C=Cancel, M=Modify, R=Clear, T=Trade, F=Fill, N=None.
- MBO sides: A=Ask, B=Bid, N=None.
- Preserve sequence, channel, flags, timestamps, publisher and instrument identifiers.

## Integrity rules

1. Do not sample, conflate, aggregate, or silently drop valid provider MBO records in ingestion.
2. Keep provider-record capture separate from derived order-book state, candles, footprint cells, and heatmap values.
3. A book must not be reported synchronized until its initial snapshot/replay has been applied correctly.
4. Treat Databento quality flags such as bad receive timestamp and maybe-bad-book as explicit quality signals. A gap or uncertain book state must be surfaced as recovering/degraded; never display it as healthy.
5. Respect event grouping: Databento's F_LAST flag marks the final record for a single event for an instrument. Consumers that publish completed book states should wait for the event boundary.
6. On disconnect or unrecoverable sequence gap, use supported replay/snapshot recovery. If recovery cannot establish continuity, keep the stream degraded.
7. Preserve the original DBN record in backend capture where account terms and licensing permit. The JSON DTO is a mapped transport representation, not a substitute for original DBN archival.
8. Keep API credentials server-side. Never put them in React source, browser storage, or Android application assets.

## Not included yet

- No Databento API key or entitlement has been configured.
- No backend service, WebSocket endpoint, database, recorder, or reconnect loop exists yet.
- No live feed has been requested or connected.
- No chart UI consumes these contracts yet.
- No Footprint or Heatmap visuals are implemented; those remain blocked on the owner's reference images.


## Phase 2 — OHLCV provider ingestion (branch phase-2/market-data-foundation)

### Identity, sequence and ordering
- Bar slot identity: `(provider, dataset, publisher_id, instrument_id, series_type, timeframe, ts_start_ns)`.
  `instrument_id` is never assumed permanent or unique across providers/datasets. `raw_symbol` is
  validated: the same slot with a different symbol is a **conflict** (counted, not overwritten).
- `sequence` is a **local ingest sequence** assigned by this backend in arrival order
  (`sequence_origin = "local"`). Databento OHLCV records carry no provider sequence (UNVERIFIED against
  the SDK), so the field is never presented as one. Revision order = `(ts_event_ns, sequence)`;
  for OHLCV `ts_event` is constant per bar, so arrival order decides revisions.
- Re-delivering identical data is a no-op duplicate. A replay/reconnect can therefore never double count.
- Provider-origin bars always win over derived bars of the same identity.

### Instrument resolution
`InstrumentResolver` maps `(provider, dataset, publisher_id, instrument_id, ts)` to a raw symbol over a
validity window (policy for catalog rows: `[definition ts_event, end of expiration date UTC)`).
Unknown instruments are rejected and counted (`rejected_unknown_instrument`); nothing is invented.
Continuous contracts have their own `series_type="continuous"` identity and are **not enabled**
(`stype_in` is always `raw_symbol`; parent symbology for `ohlcv-1s` is disabled until verified).

### Timeframes and session policy (UTC only)
| Timeframe | Bucket start (UTC) |
|---|---|
| 1s … 4h (fixed) | multiple of the interval since the Unix epoch (all divide 24h) |
| 1d | 00:00 UTC |
| 1w | Monday 00:00 UTC |
| 1M | first day of the UTC calendar month |
| 3M | first day of Jan/Apr/Jul/Oct (UTC) |

Exchange trading-day sessions (e.g. CME 17:00 CT) and holiday calendars are **not** applied yet; a
CME "daily" bar here is a UTC-day bar.

### Tiered aggregation
Each timeframe derives from its parent (`aggregation.PARENT`): 1s→5s→15s→{30s,45s}; 30s→1m→{3m,5m};
5m→15m→{30m,45m}; 30m→1h→2h→4h→1d→{1w,1M}; 1M→3M. Buckets are *recomputed* from distinct child bars
(never incrementally summed). No bar is created for buckets without source records. Provider-sourced
`ohlcv-1m/1h/1d` bars feed the same tiers, giving 1d/1w/1M/3M history that does not require retaining
1s bars. A derived bar's `completeness` is `open` (bucket may still receive data), `partial`
(not proven covered or a gap exists) or `complete` (ingestion coverage proves the bucket). Late data for
buckets whose children were already evicted is not recomputed (no shrinking); the skip is counted.

### Retention and API limits
Per-series, per-timeframe caps (`DEFAULT_RETENTION`; minimums enforced per tier). Evictions are counted
in `ohlcv.ingestion.pipeline.evicted`. `GET /v1/ohlcv` accepts optional `provider`, `raw_symbol`,
`series_type`, `start_ns`, `end_ns`, `limit`; the newest matches are returned chronologically, capped by
`OHLCV_MAX_RESPONSE_BARS`, with `count` and `truncated` added. Old call shapes remain valid.

### Concurrency and overflow
Provider callbacks (any thread) only call `offer()` on a bounded thread-safe buffer. One consumer on the
event loop applies records (single writer). A full buffer is **never dropped silently**: it increments
`overflow_count`, carves a coverage gap for that second and reports `degraded` (`ingest_overflow`) until
an operator acknowledges it.

### Provider states
`connecting | live | recovering | degraded | disconnected`. `live` is reported only after a real record
arrived on the current connection. Reconnects use bounded exponential backoff (1,2,4,… ≤60 s, 8 attempts)
and then stay `disconnected`. WebSocket contract and authentication are unchanged; no market data is
broadcast in this phase.
