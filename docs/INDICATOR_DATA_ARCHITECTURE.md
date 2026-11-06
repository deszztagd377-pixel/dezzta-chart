# DEZZTA CHART — Shared chart and indicator data architecture

## Product rule

The chart and every indicator must consume the same validated OHLCV series for the
currently selected canonical instrument and timeframe. Indicators must not fetch
separate prices, silently select another contract, or substitute sample candles.

## Data flow

```text
Validated instrument catalog + selected timeframe
                |
                v
       Firebase-authenticated WebSocket
                |
                v
  Snapshot + stream ID + initial sequence watermark
                |
                v
 Versioned DTO, exact series and sequence validation
                |
                v
       Shared marketDataStore
                |
          +-----+------+
          |            |
          v            v
   Candlestick chart  useMarketDataSnapshot()
                           |
                           v
                  useMarketIndicators()
                           |
                           v
             Indicator calculation engine
```

The REST OHLCV endpoint remains available as a separately authenticated snapshot
interface. The chart's current streaming lifecycle uses the WebSocket path; the
REST endpoint and WebSocket snapshot are not yet covered by a complete deployed
end-to-end parity test.

## Implemented in this phase

- `src/services/marketDataStore.ts` is the single in-memory source of truth for
  validated chart OHLCV bars and their exact series identity.
- Identity includes dataset, publisher ID, instrument ID, raw symbol, timeframe,
  bucket policy, and calendar identity.
- The chart requires `canonical_instrument_id` from the validated instrument
  catalog. It never derives a canonical ID from a raw symbol or provider ID.
- The chart clears the previous series before starting a stream for a changed
  contract or timeframe.
- `src/services/ohlcvWebSocketClient.ts` authenticates the socket, validates the
  subscription snapshot and watermark, and applies sequence-guarded updates.
- `src/services/ohlcvStreamSupervisor.ts` owns reconnect behavior, requests a
  fresh Firebase ID token for each connection attempt, and obtains a new
  snapshot/watermark after a recoverable disconnect or sequence gap.
- Accepted snapshots and updates are published through the shared market-data
  store. `CandlestickChart.tsx` subscribes to that store and renders its validated
  backend series.
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

The frontend has code-level authenticated WebSocket integration through the
chart lifecycle. The backend authenticates exact-series subscriptions, sends an
atomic in-memory snapshot/watermark handoff, and broadcasts accepted base and
derived OHLCV revisions. The frontend validates the snapshot/watermark handshake
and sequence-guarded updates before publishing accepted data into the shared
store.

This does **not** establish deployed end-to-end operation or external provider
delivery. The backend status must continue to report an unconfigured or inactive
provider honestly. DEMO fixtures remain visibly labelled and are not treated as
backend market data.

The current stream uses reconnect plus a fresh snapshot rather than durable
event replay. A backend restart or stream interruption therefore does not
provide historical WebSocket event replay. The REST snapshot endpoint remains
independently available and does not itself provide the WebSocket stream
watermark. Deployed REST/WebSocket parity and provider-backed operation remain
unverified.

## Calculation and timeframe rules

- Indicator input is the selected canonical chart series only.
- Each supported timeframe must have actual validated bars before the selector
  can advertise it as usable.
- When the timeframe changes, the old indicator values are cleared before the
  new series is accepted.
- Indicator warm-up periods remain empty until enough source bars exist.
- The current calculations are close-based where appropriate. Future volume,
  high/low, bid/ask, and order-flow studies must explicitly declare and validate
  their required source fields.
- Existing unit tests cover calculation alignment, warm-up, edge cases, invalid
  input, exact-series store identity, immutability, stale-series clearing, stream
  protocol validation, sequence gaps, and supervisor reconnect behavior.
- Full support across the target 1-second through 3-month timeframe range has
  not been established by this document or by the current indicator tests.

## Remaining integration and validation milestones

1. Verify the current branch-head frontend and backend test/build workflow.
2. Add controlled parity tests that compare the same normalized series returned
   by REST and by the WebSocket initial snapshot, including revisions and exact
   series identity.
3. Exercise the integrated frontend against a deployed test backend with
   authentication configured, without enabling external provider delivery.
4. Validate reconnect/backoff, heartbeat/timeout behavior, browser visibility
   and network transitions, and fresh-snapshot recovery with controlled fixtures.
5. Validate that accepted stream updates and REST snapshots converge in the
   shared store after reconnect and historical corrections.
6. Build visible indicator controls and chart panes/overlays on top of the shared
   indicator hook, with per-indicator timeframe and performance tests.
7. Add additional indicators only after their required source data and formulas
   are documented and tested.
