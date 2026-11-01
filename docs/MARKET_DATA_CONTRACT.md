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
