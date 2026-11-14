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


## Exact-HEAD regression verification — 2026-11-13

The complete frontend workflow passed on commit `da7d000d789bdb445f0c551b7879beed89e5e7d4` (Automated Tests run [#43419736603](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43419736603)); CodeQL passed on the same SHA ([#43419736562](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43419736562)). The frontend workflow included the indicator calculation tests and simulated Footprint tests. This is regression evidence for the existing calculations and simulation module only. It is not visual, interaction, live-provider, or Android-device acceptance.

### Indicator acceptance ledger

| Area | Current verified state | Remaining acceptance evidence |
|---|---|---|
| SMA 20 / EMA 20 | Close-based calculation helpers; aligned output; null warm-up; unit-tested | User-facing enable/disable controls, overlay rendering, legend/value display, selected-series/timeframe change behavior, rendering tests |
| RSI 14 Wilder | Calculation helper; index-14 first value; flat=50 and rising-only=100 edge cases tested | Dedicated oscillator pane, scale/guide presentation, controls, stale-series clearing and rendering tests |
| MACD 12/26/9 | MACD line from index 25; signal and histogram from index 33; warm-up tested | Dedicated pane, line/histogram rendering, controls, timeframe/series transitions and rendering tests |
| Bollinger Bands 20,2 | Close-based population-standard-deviation bands; first output at index 19; validation tested | Overlay rendering, legend/value display, controls, chart-boundary and timeframe tests |
| Shared indicator hook | Uses only the exact validated backend snapshot; no DEMO fallback; regression coverage included in frontend workflow | Integration tests for visible controls and proving old values clear immediately on instrument/timeframe switch |
| Footprint | Bounded deterministic educational accumulator; synthetic events; duplicate/invalid/capacity safeguards; SIMULATED provenance | Owner reference image, reviewed scoped blueprint, explicit mode control, spaced-cluster renderer only while ON, visual/performance tests; real provider order flow is a separate unimplemented data project |
| Heatmap | Not implemented | Owner reference image, approved blueprint, source-data definition, calculation and rendering tests |
| Liquidation Maps | Not implemented | Owner reference image, approved blueprint, source-data definition, calculation and rendering tests |

### Release boundary

- The ordinary candlestick chart remains unchanged when Footprint is OFF.
- No Footprint, Heatmap, or Liquidation Maps visual implementation begins before the relevant owner reference image(s) and blueprint review.
- No feature is marked complete solely because its calculation helper or unit test exists.
- The exact-HEAD CI pass does not change the feature acceptance state or project completion percentage.


## Indicator progress verification update — 2026-11-13 (latest available CI evidence)

The latest inspected automated workflow job (run [#43420429575](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43420429575)) reports:

- Frontend: **26 test files / 211 tests passed**.
- `src/indicators/indicatorCalculations.test.ts`: **7 tests passed**.
- `src/education/simulatedFootprint.test.ts`: **8 tests passed**.
- `src/education/simulatedFootprintFixtures.test.ts`: **4 tests passed**.
- Backend: **776 tests passed**.
- The workflow job completed successfully, including frontend build and backend/container checks.

This is calculation/simulation regression evidence. It does **not** close any visible-chart acceptance item. The latest available evidence does not demonstrate user-facing indicator toggles, rendered overlays/panes, legends/current values, instrument/timeframe transition rendering, live provider order flow, or Android-native operation.

### Current indicator acceptance matrix

| Indicator / component | Calculation / engine | Automated evidence | User-facing chart acceptance | Current result |
|---|---|---|---|---|
| SMA 20 | Implemented; close-based; 20-bar warm-up | Included in 7 calculation tests | Toggle, overlay, legend/value, series/timeframe transitions, render tests | **Foundation verified; UI incomplete** |
| EMA 20 | Implemented; close-based; SMA seed; 20-bar warm-up | Included in 7 calculation tests | Toggle, overlay, legend/value, series/timeframe transitions, render tests | **Foundation verified; UI incomplete** |
| RSI 14 Wilder | Implemented; first output index 14; flat=50 and rising-only=100 edge cases | Included in 7 calculation tests | Oscillator pane, scale/guides, toggle, stale-series clearing, render tests | **Foundation verified; UI incomplete** |
| MACD 12/26/9 | Implemented; MACD begins index 25; signal/histogram begin index 33 | Included in 7 calculation tests | Dedicated pane, line/histogram, controls, transition/render tests | **Foundation verified; UI incomplete** |
| Bollinger 20,2 | Implemented; population standard deviation; first output index 19 | Included in 7 calculation tests | Overlay, legend/value, controls, boundary/timeframe render tests | **Foundation verified; UI incomplete** |
| Shared market-indicator hook | Reads exact validated shared backend series; no DEMO fallback | Covered by frontend regression suite; stale/invalid states return no values | Visible controls and integration proof of immediate stale-value clearing | **Data hook implemented; UI incomplete** |
| Footprint simulation | Bounded deterministic synthetic event accumulator; buy/sell/unknown separate; duplicate/invalid/capacity safeguards; SIMULATED provenance | 8 core + 4 fixture tests passed | Owner reference, reviewed blueprint, explicit mode, spaced clusters only while ON, visual/performance tests | **Simulation verified; visual/live implementation incomplete** |
| Heatmap | No implementation verified | None | Owner reference, approved blueprint, source-data contract, calculation/render tests | **Not implemented** |
| Liquidation Maps | No implementation verified | None | Owner reference, approved blueprint, source-data contract, calculation/render tests | **Not implemented** |

### Progress accounting rule

Do not calculate a single completion percentage by averaging test counts or by counting indicator helpers. No indicator is considered complete until its formula/data contract, controls, rendering, transition behavior, and applicable regression evidence satisfy its acceptance criteria. No progress percentage is awarded by this documentation update or by CI alone.

### Required owner inputs and design gate

Footprint, Heatmap, and Liquidation Maps visual implementation remains blocked on the owner's respective reference image(s). At the 40% overall project gate, prepare a scoped blueprint and obtain owner review before major UI implementation. Until then, preserve the current normal candlestick rendering and spacing when Footprint is OFF.


## Android APK device evidence — owner confirmation (2026-11-13)

The owner confirms installing the 4.23 MB APK on the Infinix GT20. The sole APK inside Android workflow run [#43442780935](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43442780935), artifact ID `14046691238`, is `app-debug.apk` with an extracted size of 4,233,778 bytes. This is a size/context match to the owner's report, not a cryptographic on-device identity verification.

This device-installation report does not change indicator acceptance:
- SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9, and Bollinger Bands 20,2 retain verified calculation foundations and the same incomplete visible UI acceptance.
- Shared indicator hook retains its validated-backend-only/no-DEMO-fallback contract; visible controls and rendering remain incomplete.
- Footprint remains a bounded synthetic educational simulation labelled SIMULATED; no visual cluster renderer or live order-flow source is accepted.
- Heatmap and Liquidation Maps remain unimplemented.
- Full calculation definitions, warm-up alignment, test evidence, rendering acceptance criteria, and owner-reference/blueprint gates above remain authoritative.

Do not award indicator progress for APK file size or installation alone. The next indicator credit requires implementation plus exact-head regression evidence and the applicable user-visible acceptance checks. Preserve ordinary candle spacing while Footprint is OFF; spaced cluster layout is permitted only when Footprint is explicitly ON.


## APK security-audit cross-check — 2026-11-13

The Android debug APK static review is recorded in `docs/PROJECT_PROGRESS.md` under **APK static security review — 2026-11-13**. It confirms artifact/package metadata and identifies the debug signing certificate plus `debuggable=true`; it does not demonstrate indicator rendering or indicator behavior on-device.

**Indicator acceptance remains unchanged:**

- SMA 20 / EMA 20: calculation foundations tested; visible chart overlays, controls, legends, and transition acceptance remain open.
- Wilder RSI 14: calculation foundation tested; visible oscillator pane, scale/guides, controls, and stale-series transition acceptance remain open.
- MACD 12/26/9: calculation foundation tested; visible dedicated pane, line/histogram, controls, and transition acceptance remain open.
- Bollinger Bands 20,2: calculation foundation tested; visible overlay, controls, legend/value, and boundary/timeframe rendering acceptance remain open.
- Shared market-indicator hook: validated-backend-only data contract exists; visible user controls and integration acceptance remain open.
- Footprint: bounded educational synthetic accumulator only, visibly labelled `SIMULATED`; no visual cluster renderer or live order-flow feed is accepted. Keep ordinary candlestick spacing unchanged while Footprint is OFF.
- Heatmap and Liquidation Maps: no implementation verified; their visual work remains gated on the owner's references and scoped blueprint review.

The APK's successful build, debug certificate, manifest review, and owner-reported antivirus scan result award **zero indicator completion credit**. The complete acceptance matrix and calculation/test definitions above remain authoritative.


## Owner hardware constraint cross-check — 2026-11-13

The owner has one Android phone only and no PC, laptop, or second phone. This changes the feasible operational test environment but does not change any indicator formula or acceptance result. Indicator work must remain buildable and testable through the existing phone/CI workflow; no desktop-only requirement or paid service may be introduced.

Current indicator acceptance remains unchanged:
- SMA 20, EMA 20, RSI 14 Wilder, MACD 12/26/9, and Bollinger Bands 20,2: tested calculation foundations; visible controls, chart overlays/panes, legends/scales and transition/render acceptance remain incomplete.
- Shared market-indicator hook: validated backend-series contract exists; visible chart controls and integration remain incomplete.
- Footprint: bounded synthetic educational accumulator, labelled SIMULATED; visual cluster renderer remains gated on the owner's reference and reviewed blueprint. Normal candle spacing must remain unchanged while OFF.
- Heatmap and Liquidation Maps: not implemented; owner references and reviewed scoped blueprints remain prerequisites.

No indicator percentage is awarded for the phone-only constraint analysis or Stage 1 documentation. This matrix remains the complete indicator acceptance record.


## Indicator status cross-check — Criterion 8 security work (2026-11-13)

The Criterion 8 secret-audit changes do not modify indicator calculations, data contracts, chart rendering, or indicator acceptance evidence. The full indicator acceptance matrix above remains authoritative and unchanged:

- SMA 20 / EMA 20: calculation foundations tested; visible chart toggles, overlays, legends/values, and series/timeframe rendering acceptance remain incomplete.
- Wilder RSI 14: calculation foundation tested; visible oscillator pane, scale/guides, controls, and stale-series transition acceptance remain incomplete.
- MACD 12/26/9: calculation foundation tested; visible dedicated pane, line/histogram, controls, and transition/render acceptance remain incomplete.
- Bollinger Bands 20,2: calculation foundation tested; visible overlay, controls, legend/value, and boundary/timeframe rendering acceptance remain incomplete.
- Shared market-indicator hook: validated-backend-only data contract exists; visible controls and immediate stale-value clearing integration acceptance remain incomplete.
- Footprint: bounded synthetic educational accumulator only, labelled \`SIMULATED\`; visual cluster implementation remains gated on the owner's reference image and reviewed blueprint. Ordinary candle spacing must remain unchanged while Footprint is OFF.
- Heatmap and Liquidation Maps: not implemented; owner reference images and reviewed scoped blueprints remain prerequisites.

No indicator progress is awarded for secret scanning, settings representation tests, documentation, or CI alone.


## Indicator progress cross-check — Criterion 8 history audit (2026-11-13)

The Gitleaks history audit, source/bundle scans, and secret-redaction tests do not change indicator calculation engines, chart rendering, data contracts, or indicator acceptance evidence. The complete indicator matrix and acceptance requirements documented above remain unchanged:

- SMA 20 / EMA 20: calculation foundations tested; chart toggles, overlays, legends/values, and series/timeframe rendering acceptance remain incomplete.
- Wilder RSI 14: calculation foundation tested; oscillator pane, scale/guides, controls, and stale-series transition acceptance remain incomplete.
- MACD 12/26/9: calculation foundation tested; dedicated pane, line/histogram, controls, and transition/render acceptance remain incomplete.
- Bollinger Bands 20,2: calculation foundation tested; overlay, controls, legend/value, and boundary/timeframe rendering acceptance remain incomplete.
- Shared market-indicator hook: validated-backend-only data contract exists; visible controls and immediate stale-value clearing integration acceptance remain incomplete.
- Footprint: bounded synthetic accumulator only, labelled `SIMULATED`; visual cluster implementation remains gated on owner reference images and reviewed blueprint. Normal candle spacing remains mandatory while OFF.
- Heatmap and Liquidation Maps: no verified implementation; owner references and reviewed scoped blueprints remain prerequisites.

No indicator percentage is awarded for security scanning, documentation, or CI. Stage 1 remains 30/40 provisional and overall project progress remains 20.9% historical.

## Exact branch-head CI verification — 2026-11-14

- Branch: `phase-2/market-data-foundation`
- Exact tested commit: `2945bf9987f4437f2e67939dbcbde4fca5c6f86b`
- Automated Tests & Build [run #43537168454](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43537168454): **success**.
- Frontend: **26 test files / 211 tests passed**. Dependency audit, source secret scan (74 files), production build, bundle scan, scanner tests and Android host preflight also passed.
- Backend: **795 tests passed in 22.63s**. Synthetic SQLite outbox benchmark, backend dependency audit, container build, isolated Redis + persistent-volume smoke test and HIGH/CRITICAL Trivy scan/report export also completed successfully.
- CodeQL [run #43537168511](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43537168511): **success** for JavaScript/TypeScript and Python.
- Full reachable Git-history Gitleaks audit [run #43537168437](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43537168437): **success**; log explicitly reports `no leaks found`.
- The backend suite includes the new complete Digest Authorization redaction regression test, which passed on this exact commit.

### Indicator-specific interpretation

This exact-HEAD workflow reran the existing frontend suite, including indicator calculation and simulated Footprint regression tests. The security-redaction changes did not modify indicator code or chart wiring. This refreshes regression evidence only; it does **not** close user-facing indicator acceptance items or award indicator/project completion credit.

| Indicator / component | Verified foundation | Remaining acceptance |
|---|---|---|
| SMA 20 | Close-based calculation, 20-bar warm-up, aligned output, unit-tested | Visible toggle, candlestick overlay, legend/current value, selected-series/timeframe transitions and render tests |
| EMA 20 | Close-based calculation with SMA seed, 20-bar warm-up, unit-tested | Visible toggle, overlay, legend/current value, selected-series/timeframe transitions and render tests |
| RSI 14 Wilder | Wilder calculation, first output at index 14, flat/rising-only edge cases tested | Oscillator pane, scale/guides, controls, stale-value clearing and render tests |
| MACD 12/26/9 | MACD line starts at index 25; signal/histogram start at index 33 | Dedicated pane, line/histogram rendering, controls, series/timeframe transitions and render tests |
| Bollinger Bands 20,2 | Close-based population-standard-deviation bands; first output at index 19 | Overlay, controls, legend/current values, chart-boundary and timeframe render tests |
| Shared indicator hook | Exact validated backend series only; no DEMO fallback | Visible controls and integration proof of immediate stale-value clearing on instrument/timeframe changes |
| Footprint | Bounded deterministic synthetic accumulator; provenance `SIMULATED` | Owner reference image, reviewed blueprint, explicit mode, spaced cluster renderer only while ON, visual/performance tests; live provider order flow remains unimplemented |
| Heatmap | No implementation verified | Owner reference image, reviewed blueprint, source-data contract, calculation and rendering tests |
| Liquidation Maps | No implementation verified | Owner reference image, reviewed blueprint, source-data contract, calculation and rendering tests |

### Non-negotiable visual behavior and gates

- Footprint OFF preserves the ordinary candlestick chart and normal candle spacing.
- Only explicit Footprint ON may activate the dedicated spaced-candle/cluster layout.
- Footprint, Heatmap and Liquidation Maps visual work remains gated on the corresponding owner reference image(s) and scoped blueprint review.
- The 40% overall-project gate permits blueprint/review work; it does not waive reference-image requirements or authorize unreviewed implementation.
- Synthetic Footprint values must never be presented as live exchange order flow.

**Indicator acceptance is unchanged by this CI run:** calculation foundations are verified; user-facing indicator implementation remains incomplete.

## Indicator progress checkpoint — security-only branch update (2026-11-14)

The exact branch-head security/configuration update `ed62578eafad89b0d27ec233c06e5503c9f00123` passed its full automated workflow:

- Frontend regression: **26 test files / 211 tests passed**.
- Backend regression: **798 tests passed in 26.48s**.
- CodeQL: Python and JavaScript/TypeScript **success**.
- Gitleaks: **1,150 reachable commits / ~2.59 MB scanned; no leaks found**.
- Trivy HIGH/CRITICAL backend image scan: **0 findings**.
- CI Redis + persistent-volume smoke test: **success**.

This change hardened production Redis ACL configuration only. It did not alter indicator formulas, market-data series, chart components, indicator hooks, or visual rendering. Therefore the indicator acceptance ledger above is **unchanged**: SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9, and Bollinger Bands 20,2 retain their tested calculation foundations while their chart UI acceptance remains incomplete; the shared hook still lacks visible control integration; Footprint remains synthetic and visual work remains gated by owner reference image(s) and reviewed blueprint; Heatmap and Liquidation Maps remain unimplemented.

No indicator or overall project progress credit is awarded for this security-only code, tests, CI, or documentation update.



## Benchmark concurrency follow-up — 2026-11-14

A backend CI run exposed one failure in the local synthetic SQLite outbox benchmark concurrency test: 797 backend tests passed and `test_local_outbox_benchmark_reports_synthetic_data_and_latency` failed. The initial audit identified a completion-boundary race: a replay reader could compare its cursor with a page high-water mark captured before the writer's final commit.

A narrowly scoped correction was committed as `fd3eae1506b8efc2790cdda0eb498fde749cc714` in `backend/scripts/benchmark_ohlcv_outbox.py`. After the writer signals completion, the reader now compares its cursor with a fresh durable `store.outbox_high_water()` value before exiting.

**Verification state: pending.** The failing run predates this correction; no passing CI result for the correction is recorded here. The fix does not change indicator calculations, market-data contracts, chart rendering, or user-facing controls. Therefore it awards no indicator or project completion credit.

The indicator acceptance matrix above remains authoritative and unchanged: SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9, and Bollinger Bands 20,2 have tested calculation foundations but incomplete chart UI acceptance; the shared indicator hook lacks completed visible-control integration; Footprint remains a bounded synthetic accumulator labelled `SIMULATED` with visual implementation gated by owner reference and blueprint review; Heatmap and Liquidation Maps remain unimplemented and similarly gated.


## Indicator progress checkpoint — exact branch-head CI verification — 2026-11-14

Exact branch-head commit `290dd2a812ef9068fce82b9dd78bbfdb2d990d1e` passed Automated Tests & Build [run #43542532632](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43542532632), including **26 frontend test files / 211 tests** and **803 backend tests**. The synthetic SQLite outbox concurrency benchmark also passed; the separate 1,000-bar benchmark replayed all 1,000 synthetic events with two in-process readers. CodeQL [run #43542532635](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43542532635) and Gitleaks [run #43542532618](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43542532618) succeeded. These are repository regression/security results, not indicator UI acceptance.

**No indicator source, formula, chart component, indicator hook, market-data contract, or visual renderer changed in commits `6298afe`, `2658434`, or `290dd2a`. Therefore indicator progress is unchanged and no indicator completion credit is awarded.**

### Complete indicator acceptance ledger

| Indicator / component | Verified calculation or data foundation | Outstanding acceptance / implementation |
|---|---|---|
| SMA 20 | Close-based simple moving average; 20-bar warm-up; aligned output; unit-tested | Visible toggle, candlestick overlay, legend/current value, selected-series and timeframe transitions, chart render tests |
| EMA 20 | Close-based EMA with SMA seed; 20-bar warm-up; unit-tested | Visible toggle, candlestick overlay, legend/current value, selected-series and timeframe transitions, chart render tests |
| RSI 14 Wilder | Wilder smoothing; first output at index 14; flat and rising-only edge cases tested | Dedicated oscillator pane, scale and guide levels, controls, stale-value clearing, render tests |
| MACD 12/26/9 | MACD line starts at index 25; signal and histogram start at index 33 | Dedicated pane, MACD/signal lines and histogram, controls, selected-series/timeframe transitions, render tests |
| Bollinger Bands 20,2 | Close-based population-standard-deviation bands; first output at index 19 | Visible upper/middle/lower overlay, controls, legend/current values, chart-boundary and timeframe render tests |
| Shared indicator hook | Validated-backend-series-only data contract; no implicit DEMO fallback | Visible controls and integration proof that stale series clear immediately on instrument/timeframe changes |
| Footprint | Bounded deterministic synthetic accumulator; provenance is explicitly `SIMULATED` | Owner reference image(s), reviewed scoped blueprint, explicit mode control, spaced cluster renderer only while ON, visual/performance tests; live provider order flow is not implemented |
| Heatmap | No implementation verified | Owner reference image(s), reviewed scoped blueprint, source-data contract, calculations, rendering and tests |
| Liquidation Maps | No implementation verified | Owner reference image(s), reviewed scoped blueprint, source-data contract, calculations, rendering and tests |

### Non-negotiable chart behavior and visual gates

- Footprint OFF must preserve the standard candlestick layout and ordinary candle spacing.
- Only an explicit Footprint ON action may activate the dedicated spaced-candle/cluster layout.
- Footprint synthetic values must remain clearly labelled `SIMULATED` and must not be represented as live exchange order flow.
- Footprint, Heatmap and Liquidation Maps visual implementation remains gated on the corresponding owner-provided reference image(s) and reviewed scoped blueprint.
- The 40% overall-project threshold permits blueprint/review work; it does not waive reference-image requirements or authorize unreviewed visual implementation.
- Security tests, Gitleaks, CodeQL, Redis ACL CI, benchmark success, documentation and CI success do not increase indicator completion.

**Current indicator status:** calculation foundations for SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9 and Bollinger Bands 20,2 are tested; user-facing rendering/control acceptance remains incomplete. Shared hook integration remains incomplete. Footprint remains synthetic and visually gated. Heatmap and Liquidation Maps remain unimplemented.
