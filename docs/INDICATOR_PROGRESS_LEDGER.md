# DEZZTA CHART — Complete Indicator Progress Ledger

**Checkpoint:** 20 November 2026 — indicator ledger reconciled with 62J-18 gate color clarification  
**Branch:** `phase-2/market-data-foundation`  
**Indicator implementation status:** unchanged by WebSocket Batches 62H-3, 62H-4, 62I, 62J-1, 62J-2 and 62J-16. The WebSocket reliability work does not award indicator progress.  
**Interpretation:** statuses describe verified implementation boundaries, not a guessed completion percentage. No indicator weights or acceptance percentages have been approved, so per-indicator or total-indicator percentages are intentionally not fabricated.

## Color legend

- 🟩 **Verified** — implementation and required tests verified for the stated scope.
- 🟨 **Foundation** — calculation/data foundation exists; visible chart integration or lifecycle acceptance remains.
- 🟧 **Gated** — work is intentionally blocked on required reference/blueprint/owner input.
- 🟥 **Not implemented** — no implementation verified.
- ⬜ **Not assessed** — evidence is insufficient to assign a status.

## Indicator dashboard

| Indicator / subsystem | Current state | Calculation / data contract | First valid output | Remaining acceptance work |
|---|---|---|---:|---|
| SMA 20 | 🟨 Foundation | Rolling arithmetic mean of 20 closes | Candle index 19 | Chart overlay, visibility toggle, legend/current value, stale clearing, render/lifecycle tests |
| EMA 20 | 🟨 Foundation | SMA-seeded EMA; alpha \(2/21\) | Candle index 19 | Chart overlay, visibility toggle, legend/current value, stale clearing, render/lifecycle tests |
| RSI 14 | 🟨 Foundation | Wilder-smoothed close-to-close gains/losses | Candle index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing, render/lifecycle tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD index 25; signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/current values, render/lifecycle tests |
| Bollinger 20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations | Candle index 19 | Three-line overlay, toggle, legend/current values, stale clearing, render/lifecycle tests |
| Shared indicator hook | 🟨 Foundation | Validated backend snapshot only; no DEMO fallback | Depends on validated snapshot | Bind to active chart identity/timeframe, loading/error states, stale-result clearing, no cross-symbol/timeframe leakage |
| Footprint | 🟧 Gated | Deterministic educational accumulator; data explicitly SIMULATED, not exchange-native order flow | Depends on selected candle/price levels | User reference image, reviewed blueprint, explicit-ON cluster renderer, bid/ask cells, tests and performance |
| Heatmap | 🟥 Not implemented | Data source and calculation contract not approved | Not applicable | User reference image, reviewed blueprint, source/data contract, calculation, renderer, controls and tests |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract | Not applicable | Data-source feasibility, reference/blueprint, calculation, renderer, controls and tests |

## Formula and correctness contracts

### SMA 20

\[
SMA_t = \frac{1}{20}\sum_{i=0}^{19} C_{t-i}
\]

- Requires 20 valid closing prices.
- Warm-up outputs before index 19 must be null/unavailable, not zero.
- Must remain aligned with the candle index.
- Remaining UI work: visible overlay, on/off control, legend and latest value, stale clearing when symbol/timeframe changes.

### EMA 20

\[
\alpha = \frac{2}{20+1} = \frac{2}{21}
\]

\[
EMA_t = \alpha C_t + (1-\alpha)EMA_{t-1}
\]

- Seed uses the initial 20-period SMA.
- First valid value is index 19.
- Warm-up values must be null.
- Remaining UI work matches the SMA overlay lifecycle.

### RSI 14

- Uses close-to-close change, positive gains and absolute losses.
- Initial average gain/loss is formed from 14 changes.
- Subsequent averages use Wilder smoothing.
- First valid RSI output is index 14.
- Calculation edge fixtures exist; the dedicated pane, 0–100 scale, 30/70 guides, toggle, legend and chart lifecycle tests remain.

### MACD 12/26/9

\[
MACD_t = EMA_{12,t} - EMA_{26,t}
\]

\[
Signal_t = EMA_9(MACD)_t
\]

\[
Histogram_t = MACD_t - Signal_t
\]

- MACD first becomes valid at index 25.
- Signal and histogram first become valid at index 33.
- Warm-up values remain null.
- Remaining work: dedicated pane, both lines, histogram bars, zero reference line, toggle, legend and render tests.

### Bollinger Bands 20,2

\[
Middle_t = SMA_{20,t}
\]

\[
Upper_t = Middle_t + 2\sigma_{population}
\]

\[
Lower_t = Middle_t - 2\sigma_{population}
\]

- Uses population standard deviation, not sample standard deviation.
- First valid band is index 19.
- Remaining work: upper/middle/lower overlays, toggle, current values, stale clearing and rendering tests.

## Shared data and lifecycle requirements

1. Indicator arrays must align to candle indexes; no independent array shifting.
2. Warm-up positions must be null/unavailable, not fabricated values.
3. Only validated backend snapshots may feed the shared indicator hook. No demo fallback.
4. Symbol, venue, dataset, timeframe and chart identity changes must invalidate stale results.
5. Loading and error states must be visible and must not leave old indicator values displayed as if current.
6. Each indicator must have an independent visibility control and correct chart layer/pane.
7. Current values and legends must reflect the active series and last valid candle.
8. Calculation fixtures do not prove chart rendering, provider correctness, or real-time synchronization.

The current calculation test suite covers alignment/warm-up, RSI edge cases, MACD signal warm-up, Bollinger population deviation, the shared calculation entry point, 18 timeframe labels and invalid inputs. This is calculation-level evidence only; it does not prove visual integration.

## Footprint, Heatmap and Liquidation gates

- Footprint remains explicitly SIMULATED and educational until a validated exchange-native bid/ask source is available.
- Footprint OFF must preserve ordinary candlestick layout and normal spacing.
- Only when Footprint is explicitly ON may the chart switch to the dedicated spaced-candle/cluster layout.
- Do not begin Footprint or Heatmap visual implementation before the user supplies the corresponding reference image and reviews the scoped blueprint.
- Heatmap and Liquidation Maps must not be represented as live market-derived features without a validated data source and calculation contract.

## Project-level accounting (separate from indicator completion)

| Project measure | Current evidence | Status |
|---|---:|---|
| Stage 1 | 30/40 criteria = 300/400 ticks | 🟨 75% provisional |
| Gate 10 | 0/10 formally closed | 🟧 All ten remain OPEN; active/in progress |
| Stages 2–6 | Not scored | ⬜ |
| Overall project percentage | M1–M8 weights unapproved | ⬜ Not established |
| Indicator aggregate percentage | No approved weights/acceptance denominator | ⬜ Not established |

WebSocket publisher work does not award indicator progress, Stage ticks or Gate closure. CI success is not owner-side acceptance.

## Indicator work order after the current WebSocket reliability gate

1. Preserve the existing calculation contracts and tests.
2. Audit the shared hook and chart identity/timeframe lifecycle.
3. Complete SMA/EMA overlay controls, legend/current values and stale clearing.
4. Complete RSI and MACD panes with scales/guides and correct warm-up behavior.
5. Complete Bollinger overlay and lifecycle.
6. Add render-level and chart-switch regression tests.
7. Only then begin gated Footprint/Heatmap/Liquidation design after the required references and blueprint review.

No paid provider, hosting, deployment, or Termux is required for this documentation or calculation-level work.


## Live evidence refresh — 19 November 2026

Indicator implementation remains unchanged by WebSocket Batch 62J-2. The exact-head CI repair commit `9eb936778f75caa4b0c5aaa512f8e3091be8ad1b` now has Automated Tests, CodeQL and Full Git History Secret Audit all SUCCESS (runs `44548655650`, `44548655582`, `44548655649`). This validates the bridge/test repository state, not chart-visible indicator rendering, provider quality or real-time indicator synchronization. Do not increase any indicator status on the strength of WebSocket CI.

| Indicator / subsystem | Status | Verified foundation | Still required |
|---|---|---|---|
| SMA 20 | 🟨 | Rolling mean; first valid index 19; calculation fixtures | Overlay, toggle, legend/latest value, stale clearing, chart render/lifecycle tests |
| EMA 20 | 🟨 | SMA seed, alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, stale clearing, chart render/lifecycle tests |
| RSI 14 | 🟨 | Wilder smoothing; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend, stale clearing, render tests |
| MACD 12/26/9 | 🟨 | EMA12−EMA26; MACD index 25, signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend and render tests |
| Bollinger 20,2 | 🟨 | SMA20 ± 2 population standard deviations; first valid index 19 | Three-line/band overlay, toggle, legend/latest values, stale clearing and render tests |
| Shared indicator hook | 🟨 | Validated backend snapshot only; no DEMO fallback | Active chart binding, loading/error UI, identity/timeframe stale clearing and cross-series isolation tests |
| Footprint | 🟧 | Deterministic educational accumulator; explicitly SIMULATED | Owner reference image, reviewed blueprint, ON-only spaced clusters, bid/ask cells, performance/render tests |
| Heatmap | 🟥 | No implementation verified | Owner reference, reviewed blueprint, source contract, calculations, renderer, controls and tests |
| Liquidation Maps | 🟥 | No validated data/calculation contract | Source feasibility, reference/blueprint, calculation, renderer, controls and tests |

Formula/warm-up contract remains unchanged: SMA20 and EMA20 first output at 19; RSI14 at 14; MACD at 25 with signal/histogram at 33; Bollinger20,2 at 19. Warm-up slots remain null and index-aligned. Footprint OFF retains normal candle spacing; explicit ON alone may switch to the spaced cluster layout. Footprint and Heatmap visuals remain blocked until the user's reference image(s) and reviewed blueprint are available. No per-indicator percentages are invented.


## 19 November 2026 — WebSocket integration evidence boundary

The 62J-3 callback-recovery tests and 62J-4 replica snapshot read-model work do not alter indicator calculations or chart rendering. Therefore all indicator statuses and warm-up indices above remain unchanged. The replica snapshot query now returns its applied cursor from the same SQLite read transaction as its bars, which is a prerequisite for reliable chart snapshot/live handoff, not proof that indicators are synchronized in the browser. Keep SMA/EMA/RSI/MACD/Bollinger at 🟨 until chart bindings, UI state, stale-series clearing and render/lifecycle tests pass. Keep Footprint 🟧 pending user references and reviewed blueprint; Heatmap and Liquidation Maps remain 🟥.


## 19 November 2026 — Batch 62J-5 replay-read-model boundary

Added a bounded Redis replay reader with strict global cursor continuity, exact ten-field series filtering, canonical event/source/ID validation, and fail-closed behavior on missing or trimmed cursor history. This is WebSocket transport infrastructure only. It does not change indicator calculation, chart rendering, provider validation or client synchronization evidence. Keep SMA20/EMA20/RSI14/MACD12/26/9/Bollinger20,2 and Shared Indicator Hook at 🟨; Footprint at 🟧; Heatmap and Liquidation Maps at 🟥. No indicator percentage is awarded.


## 19 November 2026 — Batch 62J-6 event-loop dispatch boundary

Added an event-loop dispatcher that marshals synchronous Redis worker callbacks onto the owning asyncio loop, awaits sync/async callback completion, propagates callback failures before ACK, and rejects same-loop blocking. A real-Redis integration test connects this adapter to replica-to-hub fan-out. This remains transport/lifecycle infrastructure; no indicator calculation, chart binding, visual rendering, or indicator lifecycle acceptance changed. All indicator statuses remain as listed above.


## Batch 62J-7 — 19 November 2026: replica snapshot/replay boundary

The replica snapshot/hub handoff and bounded reconnect replay are transport consistency foundations only. No indicator formula, active chart binding, indicator UI, pane/overlay rendering or chart lifecycle acceptance changed. Preserve the statuses and warm-up indices above: SMA20 🟨 (first index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (MACD 25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧 (SIMULATED and waiting for owner reference/blueprint), Heatmap 🟥, Liquidation Maps 🟥. Do not award indicator percentage for WebSocket work.


## Batch 62J-8 — 19 November 2026: Gate 25 ACL hardening boundary

The consumer now uses snapshot-generation-scoped Redis groups so routine snapshot replacement does not require destructive XGROUP DESTROY permission. This is transport/security infrastructure only. All indicator statuses, formulas and warm-up indices remain unchanged: SMA20 🟨 (19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. No indicator progress is awarded.


## Batch 62J-9 — 19 November 2026: Redis ACL evidence boundary

A real Redis 7 ACL integration test now exercises restricted publisher and gateway identities, including positive publish/consume/replay and negative command/key-scope checks. This advances WebSocket transport security evidence only. It does not alter indicator calculations, chart rendering or indicator lifecycle acceptance. Keep SMA20 🟨 (first index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. No indicator percentage is awarded.


## Batch 62J-10 — 19 November 2026: pending event ordering boundary

The Redis consumer now retries its own pending entry before reading new entries, preserving callback/fan-out cursor order after transient callback failure. This is WebSocket transport correctness only; no indicator calculation or visual acceptance changed. SMA20 🟨 (19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥 remain unchanged.


## Batch 62J-11 — 19 November 2026: worker lifecycle evidence boundary

A managed Redis gateway worker now provides bounded thread lifecycle, event-loop dispatch, retry/backoff and fail-closed resnapshot state. This is transport lifecycle evidence only; no indicator calculation, chart binding or visible rendering changed. All indicator statuses and warm-up indices remain unchanged: SMA20 🟨 (19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.


## Batch 62J-12 — 19 November 2026: dedicated Redis config boundary

The separate OHLCV relay configuration contract is added with distinct publisher/gateway ACL credentials, exact key scope, DB0-only and production TLS validation. It is not startup-wired and does not change indicator calculations or visuals. Indicator statuses and formula warm-up indices remain unchanged.


## Batch 62J-13 — 19 November 2026: snapshot/replay/live evidence boundary

A tested replay/live merge helper now drops events already covered by replay, resequences only newer live events, and fails closed on overflow or identity/cursor mismatch. Real Redis 7 integration covers the snapshot cursor-1, replay cursor-1, live cursor-2 handoff. This is transport correctness only; indicator statuses and warm-up indices remain unchanged.


## Batch 62J-14 — 19 November 2026: main route handoff boundary

The source-SQLite WebSocket reconnect path now uses the tested replay/live merge helper and closes with a resnapshot-required signal if handoff validation or queue capacity fails. This does not alter indicator calculations or rendering; all indicator statuses and warm-up indices remain unchanged.


## Batch 62J-14 — 20 November 2026: exact-head CI and indicator boundary

Exact branch head `407d2b38882e92cdf6db5b7df6c44350b6cd746d` passed Automated Tests (backend 1,153 passed; frontend 236 passed across 28 files), CodeQL (Python and JavaScript/TypeScript), and Full Git History Secret Audit. The WebSocket route handoff change is transport-only. No indicator formulas, warm-up positions, chart overlays/panes, controls or lifecycle acceptance changed. Keep the dashboard statuses unchanged: SMA20 🟨 (first index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (MACD 25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧 (SIMULATED; owner reference/blueprint required), Heatmap 🟥, Liquidation Maps 🟥. No indicator progress percentage is awarded for WebSocket infrastructure.


## 62J-16 status refresh — 20 November 2026

The WebSocket worker lifecycle and callback deadline regression tests were expanded in code batch 62J-16. This is infrastructure reliability work only and **does not change any indicator implementation status or completion percentage**.

| Indicator / subsystem | Status after 62J-16 | Reason |
|---|---|---|
| SMA 20 | 🟨 Foundation | No indicator code or chart overlay changed |
| EMA 20 | 🟨 Foundation | No indicator code or chart overlay changed |
| RSI 14 | 🟨 Foundation | No indicator pane or lifecycle change |
| MACD 12/26/9 | 🟨 Foundation | No indicator pane or rendering change |
| Bollinger 20,2 | 🟨 Foundation | No overlay or rendering change |
| Shared indicator hook | 🟨 Foundation | No chart binding or stale-state lifecycle change |
| Footprint | 🟧 Gated | User visual reference and reviewed blueprint still required |
| Heatmap | 🟥 Not implemented | User visual reference, blueprint and validated data contract still required |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract |

No weighted indicator completion percentage is introduced. Formula/warm-up contracts and visual acceptance criteria above remain unchanged.


## 20 November 2026 — 62J-16 verification reconciliation

No indicator calculation, chart renderer, indicator hook, or indicator UI source was changed in 62J-16. Therefore every indicator row above retains its previous status and acceptance requirements. WebSocket CI success is infrastructure evidence only and must not be counted as indicator completion.

The descendant code/documentation HEAD `468d0aa4a348d997dc7affb71374bc8712cfc39d` completed all three GitHub Actions workflows successfully: Automated Tests run `44642566787`, CodeQL run `44642566989`, and Full Git History Secret Audit run `44642566911`. This confirms the current indicator calculation/test code remains build- and CI-compatible at that repository HEAD; it does not demonstrate visible chart rendering, real-time synchronization, provider correctness, or completion of any indicator acceptance item.

| Indicator / subsystem | Reconciled status | Explicit boundary |
|---|---|---|
| SMA 20 | 🟨 Foundation | Calculation foundation only; overlay/toggle/legend/stale clearing/render tests remain |
| EMA 20 | 🟨 Foundation | SMA-seeded calculation only; visible integration remains |
| RSI 14 | 🟨 Foundation | Wilder calculation only; dedicated pane and guides remain |
| MACD 12/26/9 | 🟨 Foundation | Calculation/warm-up only; MACD/signal/histogram pane remains |
| Bollinger 20,2 | 🟨 Foundation | Population-deviation calculation only; visible band remains |
| Shared indicator hook | 🟨 Foundation | Validated snapshot foundation; chart identity/timeframe lifecycle remains |
| Footprint | 🟧 Gated | Wait for user's reference image and reviewed blueprint; SIMULATED data only |
| Heatmap | 🟥 Not implemented | Wait for reference image, approved data contract and blueprint |
| Liquidation Maps | 🟥 Not implemented | No validated data/calculation contract |

No indicator percentage is published because there is no approved per-indicator acceptance denominator or weighting. Stage 1 provisional 75% and Gate 10 0/10 closure remain separate project measures; neither is an indicator completion score.


## 62J-18 — Gate status color clarification (20 November 2026)

The project owner clarified that all ten gates are ORANGE, not RED. This ledger uses two independent attributes:
- **Closure:** all ten gates remain OPEN (0/10 accepted/closed).
- **Work state/color:** 🟧 ORANGE means active/in progress; it does not mean closed, and it does not mean the gate is blocked/abandoned.

The ten orange/open gates are 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. No acceptance evidence is fabricated and no gate is marked green.

Indicator statuses remain unchanged. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 Foundation. Footprint remains 🟧 Gated and SIMULATED pending user reference and approved blueprint. Heatmap and Liquidation Maps remain 🟥 Not implemented pending references/data contracts. WebSocket CI does not increase indicator completion.


## 62J-19 reconciliation — 20 November 2026

No indicator implementation or calculation changed in this WebSocket engineering batch. Indicator status remains exactly as recorded above; WebSocket CI success does not increase indicator completion.

Current indicator acceptance sequence:
1. Shared indicator hook: active chart identity/timeframe binding, loading/error lifecycle, stale-result invalidation and cross-series isolation.
2. SMA20 and EMA20 chart overlays: independent toggles, aligned candle-index data, legend/current values and stale clearing.
3. RSI14 pane: 0–100 scale, 30/70 guides, toggle and lifecycle tests.
4. MACD12/26/9 pane: MACD and signal lines, histogram, zero guide, toggle and lifecycle tests.
5. Bollinger20,2 overlay: upper/middle/lower lines, toggle, current values and lifecycle tests.
6. Footprint and Heatmap visual work remains gated by the user's reference images and reviewed blueprint. Footprint remains SIMULATED; Footprint OFF must preserve standard candle spacing.
7. Liquidation Maps remains unimplemented until a validated source and calculation contract exists.

Do not assign percentages to indicators or the whole project until acceptance denominators and weights are explicitly approved. Gate 10 remains 10/10 ORANGE and 0/10 closed.


## 62J-21 — 20 November 2026: documentation integrity and CI reconciliation

The complete indicator ledger was restored from parent revision `a91a104db0acc6391d1511f65e881642b766d81e` after the previous documentation update was found to contain an object-string placeholder in place of the original ledger. The formulas, warm-up indices, indicator statuses, visual gates and work order remain unchanged.

Exact branch HEAD `99bc549e95341310945b987ab4ae11a86c962ea9` completed all three workflows successfully:
- Automated Tests run `44680830387`: SUCCESS — frontend tests/build, backend tests, dependency audits, synthetic outbox benchmark, backend container build, Redis ACL/persistent-volume smoke test, vulnerability scan and report export all passed.
- CodeQL run `44680830205`: SUCCESS — Python and JavaScript/TypeScript jobs.
- Full Git History Secret Audit run `44680830208`: SUCCESS.

This validates repository state at that exact SHA. It does not prove two independent ASGI gateways, production snapshot transport, production Redis TLS/ACL rotation, public WSS, browser/Android acceptance, or external gate closure. No runtime code changed. No indicator progress is awarded for CI or documentation repair.

## 62J-22 — 20 November 2026: WebSocket replica hydration consistency audit

The WebSocket engineering audit found and corrected a consistency race in replica startup hydration. Previously, hydrate_replica_pipeline() read the replica checkpoint and retained bars through two separate SQLite connections/transactions. A Redis consumer commit between those reads could pair a pre-commit cursor with post-commit bars, making the in-memory pipeline state inconsistent with its durable watermark.

The replica store now exposes load_snapshot(), which reads the checkpoint and all retained bars inside one SQLite read transaction. The bridge hydrates from that single snapshot and validates the cursor fields before replacing the in-memory pipeline. Regression coverage asserts hydration no longer calls the two independent read methods and fails closed when no verified checkpoint exists.

**Indicator accounting:** no indicator calculation, chart renderer, or indicator acceptance item changed in this batch. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 Foundation; Footprint remains 🟧 Gated/SIMULATED; Heatmap and Liquidation Maps remain 🟥 Not implemented. WebSocket correctness work does not increase indicator completion.

## 62J-23 — 20 November 2026: opt-in FastAPI replica runtime and WebSocket read path

FastAPI now accepts an explicit owner-injected replica runtime factory. When supplied, startup validates the replica store, dedicated Redis client, consumer/store/client/stream identity, atomically hydrates the in-memory pipeline from the verified snapshot, then starts exactly one managed consumer worker for that app instance. The source provider is not started in replica mode, preventing competing local ingestion.

The /ws/market-data route now selects one read domain per application instance: source SQLite remains the default when no runtime factory is supplied; opt-in replica mode uses the replica snapshot/checkpoint and bounded Redis replay. It does not combine source SQLite cursors with replica live events. Existing authentication, exact-series entitlement checks, ping/lease behavior and queue semantics remain shared.

Regression tests cover replica-mode snapshot delivery, startup hydration-before-worker ordering, provider suppression, Redis client cleanup and fail-closed startup without a verified snapshot. The runtime factory is deliberately not environment-enabled: snapshot bootstrap and owner-provisioned Redis TLS/ACL remain explicit deployment responsibilities.

**Indicator accounting:** no indicator formulas or visible chart components changed. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 Foundation; Footprint remains 🟧 Gated/SIMULATED; Heatmap and Liquidation Maps remain 🟥 Not implemented.

## 62J-24 — 20 November 2026: replica runtime readiness hardening

Replica-mode FastAPI startup now validates that the injected consumer exposes ensure_group() and awaits consumer-group bootstrap before starting the worker or accepting application traffic. This verifies the dedicated Redis connection and group readiness during startup rather than allowing a disconnected consumer to appear ready while retrying in the background. Regression coverage checks both successful group bootstrap and fail-closed cleanup on a simulated Redis bootstrap outage.

The replica WebSocket snapshot test fixture now uses UTC_FIXED_V1 for the 1-second timeframe, matching bucket_policy_for_timeframe() and the exact series identity contract. The earlier CI failure was a test-fixture policy mismatch, not a runtime data-loss failure. No indicator implementation or status changed.

## 62J-25 — 20 November 2026: two independent ASGI gateway process acceptance

Added a real multi-process acceptance test that launches two independent Uvicorn/FastAPI gateway processes. Each process opens its own SQLite replica database, its own Redis client and consumer identity, and the same shared Redis stream. Both authenticate and subscribe through the actual /ws/market-data route. A source event is then appended once; the test requires both WebSocket clients to receive cursor 1 and both independent replica checkpoints to advance to 1.

This validates the opt-in FastAPI lifecycle, replica snapshot, live Redis consumer, event-loop dispatcher and WebSocket fan-out together across separate OS processes. It uses the existing CI Redis 7 service and local temporary SQLite files; no paid infrastructure or public deployment is involved.

Indicator calculations and chart UI remain unchanged. No indicator progress is awarded for transport acceptance.

62J-25 test-fixture note: the process acceptance uses the existing make_bar() helper, which emits UTC_LEGACY for backward compatibility. Its WebSocket series identity now explicitly requests UTC_LEGACY so the test validates exact matching rather than mixing it with the default UTC_FIXED_V1 selector.

62J-25 harness note: the initial child process failed before server startup because the test harness used incorrect module ownership for CanonicalInstrument and ProviderInstrumentMapping. The imports now use app.instrument_identity and app.instrument_registry, matching the repository's actual structure.

## 62J-26 — 20 November 2026: replica-backed WebSocket reconnect replay acceptance

Extended the two-process ASGI integration scenario with a reconnecting client that presents an older durable cursor. The actual WebSocket route must replay the retained Redis event from cursor 0 through cursor 1, mark the event as replayed, and complete at the same watermark. This verifies that replica snapshot/checkpoint state and Redis replay use the same cursor domain at the application boundary.

Indicator calculation and visible chart status remain unchanged.


## 62J-27 — 20 November 2026: WebSocket exact-head reconciliation

The exact branch head `5c5205ebc5d6b58b8e177854edb79f93ba9ea118` passed Automated Tests (`44686658866`), CodeQL (`44686658770`) and Full Git History Secret Audit (`44686658757`). The new reconnect assertion extends the real two-ASGI-process test: after both replicas receive live cursor 1, a reconnecting client requests from cursor 0 and the actual replica-backed WebSocket route returns replay cursor 1 and replay completion at cursor 1.

This is transport/reconnect evidence only. No indicator formulas, indicator hook, chart renderer, pane, overlay, control, or visual acceptance item changed. Keep SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook at 🟨 Foundation; Footprint at 🟧 Gated/SIMULATED; Heatmap and Liquidation Maps at 🟥 Not implemented. No indicator aggregate percentage is assigned without an approved denominator.
