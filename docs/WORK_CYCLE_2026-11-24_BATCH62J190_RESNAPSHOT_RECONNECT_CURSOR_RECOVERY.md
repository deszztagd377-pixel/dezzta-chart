# Work cycle — 24 November 2026 — Batch 62J-190: resnapshot reconnect cursor recovery

**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `8606cb460f641b0b831081aeed8aae6a6149c91d`  
**CI:** 5/5 exact-HEAD workflows SUCCESS.  
**ZERO COST:** maintained. No paid provider, hosting, deployment, production account, credential, or device operation. Protected `main` unchanged.

## 1. Defect identified

Batch 62J-189 correctly makes the backend fail closed when a replay checkpoint predates the immutable snapshot cursor. A further client-lifecycle gap remained: when the server emits `market_data.ohlcv.resnapshot_required` and then closes with retryable code 1013 because the replay/live handoff cannot be completed, the supervisor retained its prior resume cursor.

On reconnect, that stale cursor could cause the client to request the same replay path again instead of asking for a full snapshot. The protocol already has the server-directed resnapshot signal; the missing part was propagating that signal into the supervisor's reconnect state.

## 2. Implementation

Changed:
- `src/services/ohlcvWebSocketClient.ts`
- `src/services/ohlcvStreamSupervisor.ts`
- `src/services/ohlcvWebSocketClient.test.ts`
- `src/services/ohlcvStreamSupervisor.test.ts`

The WebSocket client now exposes optional `onResnapshotRequired(snapshotCursor)` and invokes it only after validating the server's resnapshot instruction. The supervisor owns this callback and clears its `resumeCursor`. The next connection therefore sends a subscribe request without a cursor and requests a full snapshot. The resume cursor is restored only when the new snapshot passes validation and its cursor is delivered through the existing `onCursor` callback.

For the ordinary same-connection fallback path, the callback also clears the old cursor first; the accepted replacement snapshot then installs the new cursor. No new wire message, timer, server endpoint, provider, or paid service was added.

## 3. Regression coverage and correction

- Client regression verifies the validated server resnapshot instruction calls `onResnapshotRequired` with its snapshot watermark.
- Supervisor regression simulates: initial snapshot cursor 100 → reconnect sends cursor 100 → server requests resnapshot at cursor 105 and closes 1013 → next connection omits cursor → full snapshot 105 accepted → following reconnect resumes from cursor 105.
- First CI attempt caught a test-fixture error: the callback mock was declared in the neighboring replay test instead of the resnapshot test. The mock declaration was moved to the correct test; runtime source did not need a change for that fixture correction.
- The corrected test suite passed on the final source/test HEAD.

## 4. Exact-head CI evidence

Final source/test HEAD: `8606cb460f641b0b831081aeed8aae6a6149c91d`

- [Automated Tests #2307](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034616) — SUCCESS. Frontend: **320 passed / 34 test files**. Backend: **1,348 passed, 1 skipped, 6 warnings**. Redis TLS fixture, synthetic Worker/DO tests, frontend build, backend dependency audit, SQLite benchmarks, container build/smoke and image scan completed successfully.
- [CodeQL #1246](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034690) — SUCCESS (JavaScript/TypeScript and Python).
- [OCI ARM64 Image Readiness #1246](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034703) — SUCCESS (native ARM64 build/smoke).
- [Full Git History Secret Audit #1246](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034693) — SUCCESS.
- [Android APK Build #1246](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034582) — SUCCESS.

### Android debug artifact

- [Download CI debug APK artifact](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034582/artifacts/14880166595)
- Artifact ID: `14880166595`
- Archive size: 3,880,092 bytes
- APK SHA-256: `39a6b0a97b3d55bfa44e5dea390d8d8b2a506fb23e7b4de68cfaca830a47e562`
- Artifact archive SHA-256: `b788300495c1cc0430337577088299722c17ff92496908a77757a2e0fdba4ac5`

This is a CI-built debug APK, not a release-signed production build or Play Store package. The build does not prove installation on the user's phone, Firebase production authentication, public WSS, network handover or real-device lifecycle acceptance.

## 5. ZERO COST and production boundaries

No provider was enabled. No paid feed, hosting, cloud resource, production account, credential, deployment, domain, or device operation was created. No main-branch change occurred.

Still open:
- public HTTPS/WSS hostname, reverse proxy and certificate lifecycle;
- real Firebase project token, revocation and entitlement acceptance;
- owner-host Redis TLS/ACL/persistence/failover and authenticated snapshot receipt custody;
- production multi-user and Android/browser network lifecycle acceptance;
- upstream provider demand pooling and recurring-$0 market-data redistribution rights.

CI's synthetic Worker/DO tests and container smoke test do not prove public WSS or owner-host production operation.

## 6. Complete indicator progress ledger — unchanged

No indicator formula, calculation kernel, chart binding, renderer, pane, toggle, legend or indicator-specific test changed in this batch.

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

Aggregate indicator progress remains **NOT SCORED** because study weights and denominator are not approved. Preserve warm-up nulls, exact source-candle alignment, prefix causality/no future repaint, invalid/gapped-input rejection and stale-output clearing on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone enables spaced clusters. Footprint and Heatmap visual work remains gated on owner reference images and scoped blueprint review.

## 7. Project progress accounting

- Stage 1 Foundation / Security / Data Integrity: **30/40 = 75% provisional 🟨** — unchanged.
- Stage 2 Market Data / Provider Integration: **NOT SCORED 🟧** — recurring-$0 data rights and upstream demand lifecycle remain unresolved.
- Stages 3–6: **NOT SCORED ⬜**.
- Gate 10: **0/10 external criteria formally closed 🟥**.
- Overall project: **NOT SCORED** — approved weighted denominator unavailable; no invented percentage.
- Delivery target: **24 December 2026**, planning target only.
- Cost: **ZERO COST**.

## 8. Next work order

1. Continue replay/live lifecycle audit across snapshot, replay, queue overflow, reconnect and multi-user isolation without duplicating existing mechanisms.
2. Keep provider demand pooling blocked until the recurring-$0 feed/redistribution rights and SDK semantics are verified.
3. Continue scoped indicator chart-integration planning; no Footprint/Heatmap visuals before owner reference images and blueprint review.
4. Keep public WSS, production Firebase, owner-host Redis and real-device acceptance open until real evidence exists.
