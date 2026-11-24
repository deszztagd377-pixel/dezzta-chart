# Work cycle — 24 November 2026 — Batch 62J-189: replay checkpoint floor integrity

**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `713449822022e555b6fe98964952814b012f3520`  
**Status at report creation:** CodeQL, OCI ARM64 readiness and full-history secret audit SUCCESS; Automated Tests still RUNNING. See run links below.  
**ZERO COST:** maintained. No provider activation, paid API, hosting, deployment, account, production credential, or device operation. Protected `main` unchanged.

## 1. Defect identified

The replay/live handoff captures an immutable snapshot cursor when a WebSocket subscription is registered. During replay, accepted live events may be queued and advance the subscription's mutable `durable_cursor`. Those two cursor values have different meanings:

- `snapshot_cursor`: immutable lower bound represented by the snapshot installed at subscription creation.
- `durable_cursor`: moving high-water mark, advanced as new live events are queued.

Before this batch, `merge_replay_boundary()` validated the replay events and their ordering but did not reject a replay checkpoint older than the snapshot's cursor. If a replica checkpoint regressed behind the snapshot watermark, the replay could finish without covering the interval already absent from the client's prior state, while queued live events only begin after the snapshot watermark. That is a potential silent continuity gap.

Comparing the replay checkpoint against the moving `durable_cursor` would be incorrect: valid live events queued after the replay checkpoint naturally advance that value. The correct comparison is against the immutable snapshot cursor.

## 2. Implementation

Changed:
- `backend/app/ohlcv_stream.py`
- `backend/tests/test_ohlcv_stream.py`

The subscription now records `snapshot_cursor` separately from `durable_cursor`. Both registration paths initialize it from the cursor represented by the snapshot:
1. in-memory pipeline snapshot registration;
2. externally consistent replica snapshot registration.

Before inspecting or draining the live queue, `merge_replay_boundary()` now raises `OhlcvStreamResnapshotRequired` if `replay_end_cursor < snapshot_cursor`. The existing WebSocket handler already maps this fail-closed exception to `market_data.ohlcv.resnapshot_required` and closes with retryable code 1013. No new network protocol message or client behavior was invented.

## 3. Regression coverage

Added `test_replay_boundary_rejects_checkpoint_older_than_snapshot_cursor`:
- initial snapshot cursor = 41;
- a live event at cursor 43 is queued during replay;
- moving `durable_cursor` advances to 43 while immutable `snapshot_cursor` stays 41;
- replay checkpoint 40 is rejected as requiring a new snapshot;
- the queued event remains untouched, proving validation occurs before queue draining;
- the replica snapshot registration path is also checked with snapshot cursor 51 and replay checkpoint 50.

The existing valid handoff test remains important: replay through cursor 42 with a later queued live event at cursor 43 must still merge and resequence normally. The implementation deliberately does not compare the replay checkpoint against the moving live cursor.

## 4. CI evidence

Exact source/test HEAD: `713449822022e555b6fe98964952814b012f3520`

- [Automated Tests #2307](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45302691457) — RUNNING at report creation; frontend tests/build and pre-backend steps had succeeded; backend dependency setup and Redis TLS fixture had succeeded; backend test step was running.
- [CodeQL #1246](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45302691477) — SUCCESS (JavaScript/TypeScript and Python).
- [OCI ARM64 Image Readiness #1246](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45302691475) — SUCCESS (native ARM64 build/smoke).
- [Full Git History Secret Audit #1246](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45302691440) — SUCCESS.

Automated Tests must finish successfully before this batch receives full CI acceptance credit. No Android APK was rebuilt: the source diff is backend-only; the workflow's Android host preflight and immutable preview publisher checks did run as part of Automated Tests. CI-only OCI and synthetic Worker/DO results are not public hosting, production WSS, or owner-host evidence.

## 5. Adjacent provider-demand / ZERO COST audit

Reviewed `backend/app/provider.py`, `backend/app/databento_sources.py`, configuration and backend README:
- `ProviderManager` is application-lifecycle/configuration scoped.
- `DatabentoLiveSource` subscribes once to the fixed configured symbol tuple.
- No verified dynamic add/remove subscription path is wired to chart open/switch/close.
- The SDK wrapper itself is explicitly marked UNVERIFIED against the installed real SDK.
- Existing downstream `OhlcvStreamHub` is per-client exact-series fan-out, not upstream provider demand pooling.
- The repository already records that recurring-$0 live market-data redistribution rights have not been approved.

Decision: no disconnected reference counter, guessed SDK call, paid feed activation, or public-page scraping was added. Upstream demand pooling remains blocked until a recurring-$0 feed and redistribution rights are verified, then requires an explicit provider adapter contract and lifecycle tests.

## 6. Indicator ledger — no implementation credit in this batch

No indicator formula, numeric kernel, hook, chart binding, renderer, pane, legend, toggle, or indicator test changed.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Candlestick overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean and Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values, lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity clearing, lifecycle, render/performance |
| Shared Indicator Hook | 🟨 Foundation | Exact backend snapshot; aligned multi-study calculations; trust-state and immutable-revision regressions | Actual chart binding, stale clearing across identity changes, settings/legend, accessibility/performance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask truth | Owner reference image(s), reviewed blueprint, verified bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | Owner reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible provenance/calculation contract, reviewed blueprint, renderer and tests |

Mandatory indicator invariants remain: warm-up values null; exact source-candle alignment; prefix causality/no future repaint; invalid/non-finite/gapped input rejection; stale-output clearing on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone activates spaced clusters. Footprint and Heatmap visual work remains gated on owner reference images and scoped blueprint review. Aggregate indicator progress remains NOT SCORED because study weights and denominator are not approved.

## 7. Project accounting and remaining blockers

- Stage 1 Foundation / Security / Data Integrity: **30/40 = 75% provisional 🟨** — unchanged; this fix is a reliability improvement, not a new stage acceptance criterion.
- Stage 2 Market Data / Provider Integration: **NOT SCORED 🟧** — recurring-$0 data rights and upstream demand lifecycle remain unresolved.
- Stages 3–6: **NOT SCORED ⬜**.
- Gate 10: **0/10 external criteria formally closed 🟥**.
- Overall project: **NOT SCORED** — approved weighted denominator is unavailable; do not invent a percentage.
- Public WSS, real Firebase production ticket authority, owner-host Redis persistence/receipt custody, production multi-user acceptance and real Android device acceptance remain open.
- Delivery target: **24 December 2026**, planning target only.
- Cost: **ZERO COST**.

## 8. Next sequence

1. Finish and inspect exact-HEAD Automated Tests; repair any regression before granting acceptance.
2. Continue replay/resnapshot lifecycle audit against snapshot, replica, reconnect and queue-overflow boundaries without duplicating existing mechanisms.
3. Keep provider upstream pooling blocked until recurring-$0 source rights and SDK semantics are verified.
4. Continue indicator chart-integration planning within scope; do not implement Footprint/Heatmap visuals before owner references and blueprint review.
