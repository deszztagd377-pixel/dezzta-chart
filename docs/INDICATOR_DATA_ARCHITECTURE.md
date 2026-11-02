# DEZZTA CHART — Shared chart and indicator data architecture

## Product rule

The chart and every indicator must consume the same validated OHLCV series for the
currently selected instrument and timeframe. Indicators must not fetch separate
prices, silently select another contract, or substitute sample candles.

## Data flow

```text
Verified contract + selected timeframe
                |
                v
      Read-only backend OHLCV API
                |
                v
  Versioned DTO + exact identity validation
                |
                v
      Chart OHLCV adapter
                |
          +-----+------+
          |            |
          v            v
   Candlestick chart  Shared marketDataStore
                           |
                           v
                 useMarketDataSnapshot()
                           |
                           v
                  useMarketIndicators()
                           |
                           v
             Indicator calculation engine
```

## Implemented in this phase

- `src/services/marketDataStore.ts` is the single in-memory source of truth for
  validated chart OHLCV bars and their exact series identity.
- Identity includes dataset, publisher ID, instrument ID, raw symbol, and timeframe.
- The chart clears the previous series from the shared store immediately when the
  selected contract or timeframe changes.
- Only non-empty, validated backend bars in `ready` or `degraded` state are
  published as indicator input. DEMO candles are never published to the store.
- Store snapshots and bar objects are immutable. Subscribers receive a revision
  update when a new snapshot or state is published.
- `useMarketDataSnapshot()` provides a React subscription for chart-linked tools.
- `useMarketIndicators()` computes indicator values only when the shared source is
  a validated backend series. DEMO, loading, unavailable, and error states return
  no indicator values.
- The reusable calculation engine currently includes SMA, EMA, Wilder RSI, MACD,
  and Bollinger Bands. Warm-up periods are represented as null rather than
  fabricated values. Indicator outputs align with their source candle indexes.

## Live-data boundary — important limitation

The frontend currently obtains read-only OHLCV snapshots over HTTP. The shared
store is ready to receive subsequent validated updates, but continuous provider
streaming, WebSocket OHLCV broadcast, reconnect/gap recovery, and incremental
bar revisions are not yet wired end to end. Therefore this phase does **not**
claim that the app currently receives live market data.

A future stream adapter must validate the same exact series identity and bar
invariants before publishing updates through the same store. The chart and all
indicators will then update from that one publication path; no indicator should
open its own market-data connection.

## Calculation and timeframe rules

- Indicator input is the selected chart series only.
- Each supported timeframe must have actual validated bars before the selector
  can advertise it as usable.
- When the timeframe changes, the old indicator values are cleared before the
  new series is accepted.
- Indicator warm-up periods remain empty until enough source bars exist.
- The current calculations are close-based where appropriate. Future volume,
  high/low, bid/ask, and order-flow studies must explicitly declare and validate
  their required source fields.
- Unit tests cover calculation alignment, warm-up, edge cases, invalid input,
  exact-series store identity, immutability, and stale-series clearing.

## Next integration milestones

1. Deploy and smoke-test the backend without enabling a provider session.
2. Connect the frontend to the deployed read-only API and verify exact contract
   and timeframe snapshots.
3. Define a versioned streaming event envelope and implement backend broadcast,
   frontend reconnect, sequence/gap handling, and snapshot resynchronization.
4. Route every accepted stream update through the shared store.
5. Build visible indicator controls and chart panes/overlays on top of the shared
   indicator hook, with per-indicator timeframe and performance tests.
6. Add additional indicators only after their required source data and formulas
   are documented and tested.
