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


## Indicator implementation status — 2026-11-07

The following are verified calculation foundations, not finished chart UI:

- SMA 20, EMA 20, Wilder RSI 14, MACD (12/26/9), and Bollinger Bands (20, 2) are implemented in `src/indicators/indicatorCalculations.ts` with warm-up nulls and unit tests.
- `src/indicators/useMarketIndicators.ts` only returns values when the shared store contains a non-empty validated backend series in `ready` or `degraded` state. DEMO, loading, unavailable, and error states return no indicator values.
- The current audit found no visible indicator controls, panes, or overlay wiring in `src/App.tsx` or `src/components/CandlestickChart.tsx`. Therefore these indicators are **not yet user-operable on the chart**.
- The Footprint module in `src/education/simulatedFootprint.ts` is an offline educational accumulator only. It does not consume a provider stream and is not real order-flow data. It must remain labelled `SIMULATED`.
- Heatmap and Liquidation Maps have no implementation verified in this audit.

### Visual implementation prerequisites

1. Wait for the owner's Footprint reference image before implementing its visual layout.
2. Keep ordinary candlestick spacing unchanged while Footprint is OFF. Only explicit Footprint ON may enable spaced candle/cluster rendering.
3. Wait for the owner's Heatmap and Liquidation Maps reference images before implementing those visual designs.
4. Respect the 40% overall project gate: prepare and review a scoped blueprint before major visual feature implementation.
5. Keep every study bound to the exact validated selected instrument/timeframe series. Never silently fall back to DEMO data for indicator calculations.


---

## Indicator status re-audit — 2026-11-13

Audited against source files on `phase-2/market-data-foundation` at pre-documentation HEAD `600ff7ee7c5494ad894c762aa7e5644694de3175`.

### Exact implemented calculation definitions

| Study | Parameters | Input | Output alignment / warm-up |
|---|---|---|---|
| SMA | 20 | Close | One value per bar; first 19 entries null |
| EMA | 20 | Close; SMA seed | One value per bar; first 19 entries null |
| RSI | Wilder 14 | Close-to-close changes | First value at index 14; earlier entries null |
| MACD | EMA 12 / EMA 26 / signal EMA 9 | Close | MACD line begins at index 25; signal/histogram begin at index 33 |
| Bollinger Bands | 20 periods, 2 population standard deviations | Close | Middle/upper/lower begin at index 19 |

The implementation rejects invalid periods and non-finite inputs. MACD rejects fast periods greater than or equal to slow periods. Bollinger deviation multipliers must be finite and non-negative.

### Hook contract

`useMarketIndicators()` exposes the exact market snapshot identity, status, source, revision, and calculated indicator arrays. It returns `indicators: null` unless the shared market-data store has a non-empty backend series in `ready` or `degraded` state. No DEMO fallback is allowed for calculations.

### Footprint educational simulation contract

The offline accumulator groups synthetic events by event-time interval and integer price tick. It keeps buy, sell, and unknown quantities separate, calculates delta only as buy volume minus sell volume, rejects duplicate event IDs, validates safe integer quantities/timestamps, and fails closed when its bounded unique-event ledger is full. Snapshots identify their origin as `SIMULATED`. This is not a live order-flow feed and must never be labelled as exchange-observed data.

### Explicitly not implemented / not accepted

- No visible indicator controls, chart overlays, or oscillator panes are wired into the current app.
- No Heatmap implementation was found.
- No Liquidation Maps implementation was found.
- No Footprint visual layout is implemented.
- No production provider feed or real bid/ask trade classification is connected to Footprint.
- Fixture-only timeframe tests do not establish live support for every interval.
- Indicator calculations are educational analysis tools, not predictions or buy/sell recommendations.

Visual implementation remains gated on owner-provided references for Footprint, Heatmap, and Liquidation Maps, plus a reviewed scoped blueprint at the 40% project milestone. The ordinary candlestick chart must retain its existing spacing while Footprint is off.
