# DEZZTA CHART — Work Cycle 62J-161
Date: 2026-11-22
Branch: `phase-2/market-data-foundation`
Base code HEAD: `bf76a24f6772f6a364fe75026de6aa22560b4803`

## Objective
Move the authenticated OHLCV frontend from one global chart supervisor to independent canonical-series supervisors, while sharing one transport among panels requesting the same exact series. Preserve the legacy supervisor API for existing consumers, isolate each series in the keyed store, and keep the implementation zero-cost.

## Code changes
1. `src/services/ohlcvStreamSupervisor.ts`
   - Added the opt-in `seriesScoped` mode.
   - Legacy callers retain the prior single-owner behavior and legacy singleton-store publication.
   - Series-scoped supervisors do not stop another series' supervisor and do not publish/reset the legacy singleton snapshot.
   - Snapshot, update, unavailable, authentication failure, and stop events write only to the exact keyed series store.
   - Incremental update eligibility reads the exact keyed snapshot, not the global singleton snapshot.

2. `src/services/ohlcvSeriesSupervisorRegistry.ts`
   - Added a shared registry keyed by the full normalized canonical series identity.
   - First panel creates one authenticated supervisor.
   - Additional panels for the same exact series reuse the same socket/supervisor.
   - Different series can run concurrently without cross-writing each other's snapshots.
   - Owner IDs are normalized and generation-guarded; stale cleanup cannot release a newer lease.
   - Each panel receives status/error callbacks independently; a late-joining panel receives the current supervisor status immediately.
   - Only the final owner release stops that series' supervisor.
   - This is downstream WebSocket sharing; it does not claim upstream provider ref-counting or dynamic vendor subscription support.

3. `src/components/CandlestickChart.tsx`
   - Added stable React `useId()` panel ownership.
   - Chart now acquires/releases a lease from the per-series supervisor registry.
   - Selected-series lifecycle reset is scoped to the keyed store; the no-contract DEMO path retains its legacy DEMO reset.

4. `src/components/CandlestickChart.lifecycle.test.tsx`
   - Updated browser lifecycle mocks to exercise the registry lease contract and assert keyed-store state.

5. `src/services/ohlcvSeriesSupervisorRegistry.test.ts`
   - Tests distinct series running concurrently and maintaining separate keyed snapshots.
   - Tests two panels sharing one series transport.
   - Tests final-owner-only shutdown.
   - Tests late panel join receives current subscribed status without opening a second socket.
   - Tests stale generation cleanup after owner reacquisition.

## Verification and failure handling
- An earlier Automated Tests run on intermediate commit `b6b6a3d0c8512b439c7aa7b1a466168c2d4b0047` failed in two chart lifecycle tests because the test harness still mocked the old direct supervisor import and inspected the legacy singleton snapshot.
- The implementation was changed to the registry API and the lifecycle test harness was updated to mock the new lease registry and inspect the keyed store.
- The corrected code/test HEAD is `0e21edbc03002455acb3502474e9514142cc9e23`.
- CI runs for that exact HEAD were started; final conclusions must be read from GitHub Actions before calling the batch green.
- Earlier success on an ancestor SHA does not substitute for verification of this exact code HEAD.

## Resource and data-isolation accounting
- Transport count: one supervisor/socket per canonical series key, independent across distinct series.
- Panel count: multiple owners share a series transport.
- Stop condition: owner count reaches zero.
- Series key includes provider, series type, dataset, publisher ID, instrument ID, raw symbol, timeframe, bucket policy, calendar ID, and calendar version (normalized by the shared identity helper).
- The keyed store remains bounded to 32 cached series and 5,000 bars per series by default. The theoretical cache object ceiling remains 32 × 5,000 = 160,000 bars; this is not a measured heap/RAM guarantee.
- No paid provider, hosting, VM, API key, subscription, or external data dependency was added.

## Known boundaries
- Frontend per-series WebSocket ownership is now implemented but awaits successful exact-HEAD CI and additional browser/device validation.
- Backend `ProviderManager` remains process/configuration scoped; no dynamic upstream add/remove demand coordinator is claimed.
- Databento SDK dynamic subscription semantics remain unverified in the repository's adapter; do not wire speculative SDK calls.
- No recurring-zero-cost CME feed with app redistribution rights has been verified. Unsupported live market data must remain unavailable/demo.
- OCI ARM64 image CI is not an OCI VM deployment.
- Real Android WebView foreground/background/process death, network handover, public WSS endpoint, TLS, and live Firebase acceptance remain external release gates.

## Full indicator progress
Legend: 🟩 verified/implemented foundation; 🟨 partial foundation; 🟧 prototype only; 🟥 not implemented.

| Indicator / component | Status | Verified foundation | Remaining acceptance work |
|---|---|---|---|
| SMA20 | 🟨 | 20-close arithmetic mean; first valid index 19; warm-up nulls and aligned outputs | Chart overlay, toggle, legend/latest value, identity/lifecycle/render tests |
| EMA20 | 🟨 | SMA seed; alpha 2/21; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render tests |
| RSI14 Wilder | 🟨 | Wilder smoothing; first valid index 14; regression tests | Dedicated 0–100 pane, 30/70 guides, toggle/legend/render tests |
| MACD12/26/9 | 🟨 | MACD first valid index 25; signal/histogram first valid index 33 | Pane, MACD/signal lines, histogram, zero guide, toggle/legend/render tests |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population standard deviation; first valid index 19 | Three-line overlay, toggle, latest values, render tests |
| Shared Indicator Hook | 🟨 | Backend snapshot and aligned calculations; keyed React snapshot; pure reads | Hook-level stale clearing, gap semantics, chart binding and renderer integration |
| Footprint | 🟧 | Synthetic educational accumulator only | User reference image, reviewed blueprint, validated bid/ask provenance, spaced cluster renderer and acceptance tests |
| Heatmap | 🟥 | No validated depth/liquidity renderer | User reference image, depth/liquidity source contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 | No validated liquidation calculation/renderer | Data provenance and calculation contract, reviewed blueprint, renderer and tests |

Indicator invariants:
- Warm-up values remain null; never substitute zero.
- Output remains candle-index aligned and prefix-causal.
- Gaps/invalid bars must not be silently converted into synthetic candles or zeroes.
- Clear stale values when symbol, venue/provider, dataset, timeframe, bucket policy, calendar, or chart identity changes.
- Footprint OFF keeps normal candle spacing; explicit ON switches to a dedicated spaced cluster layout.
- Do not award indicator completion from documentation, CI, or benchmark activity.
- Footprint and Heatmap visual implementation remains blocked until the user provides the relevant visual references and reviews the scoped blueprint.

## Project stage and gate dashboard
- Stage 1 — Foundation, Security & Data Integrity: 30/40 = 75% provisional 🟨.
- Stage 2 — Market Data Infrastructure: not formally scored/opened ⬜; frontend per-series transport is a substantial partial step, but upstream demand/provider lifecycle and zero-cost data entitlement remain open.
- Stage 3 — Chart Engine & Timeframe: not scored ⬜.
- Stage 4 — Indicators & Analytics: not scored ⬜.
- Stage 5 — Professional UI & Interactive Tools: not scored ⬜.
- Stage 6 — Hardening, Validation & APK Release: not scored ⬜.
- Overall project: NOT SCORED; no approved overall denominator or stage weights.
- Gate 10: 0/10 external acceptance criteria formally closed. CI success does not close external deployment/device/data-rights gates.
- Target date remains 2026-12-24.

## Commit sequence in this work cycle
- `5de6c74697d38cf9e392132a1b76dae6c7a63da3` — series-scoped supervisor isolation.
- `1285c25c87580a92d988048b86b53e8bbbb60c68` — per-series supervisor registry.
- `b6b6a3d0c8512b439c7aa7b1a466168c2d4b0047` — chart panel lease integration.
- `ffae0bafda088cdfe2e415a4fcecfc1c2d5f276c` — initial registry regression tests.
- `18a9cbf84dbce14e762e12a05dd99e444f6e4018` — lifecycle tests updated for keyed registry behavior.
- `af19807e9471424f1ccaa5607258be2402ba64a9` — immediate status for joining panel.
- `0e21edbc03002455acb3502474e9514142cc9e23` — late-join regression test.
