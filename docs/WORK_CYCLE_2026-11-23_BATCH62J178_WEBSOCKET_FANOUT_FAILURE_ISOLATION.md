# DEZZTA CHART — Batch 62J-178
## WebSocket fan-out failure isolation regression and exact-head CI acceptance

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Code/test HEAD:** `4c845f3912857cbdebe01e007952e80f080cb634`  
**Protected `main`:** unchanged at `e3841681bc69b73619058deaf939df82ae5116a1`  
**ZERO COST:** preserved  
**Exact-HEAD CI:** all four workflows SUCCESS.

## 1. Scope

This batch adds a focused regression test for the synthetic Durable Object fan-out failure path. It does not change production runtime code, indicator formulas, chart rendering, authentication, provider integration, deployment configuration, or production infrastructure.

## 2. Regression added

File: `cloudflare/proof/worker.node-test.mjs`

The new test simulates a connection whose `send()` throws while a second connection for the same authorized series remains healthy. It asserts:

1. The failed connection is closed with code 1011 and the existing generic fan-out failure reason.
2. The failure does not abort delivery to the healthy connection.
3. The healthy connection receives sequence 51.
4. The response reports exactly one successful delivery, not two attempted deliveries.

This verifies isolation of synchronous send failures. It does **not** implement or prove a bounded outbound queue, a buffered-byte threshold, sustained slow-consumer detection, or a production backpressure policy.

## 3. Exact-head verification

All workflows completed successfully against code/test SHA `4c845f3912857cbdebe01e007952e80f080cb634`:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45206936976](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45206936976) | SUCCESS |
| CodeQL Security Analysis | [45206937012](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45206937012) | SUCCESS |
| Full Git History Secret Audit | [45206936989](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45206936989) | SUCCESS |
| OCI ARM64 Image Readiness | [45206937290](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45206937290) | SUCCESS |

The Automated Tests run completed the following relevant steps successfully:
- isolated synthetic Worker Node tests;
- pinned local workerd WebSocket/runtime smoke;
- Durable Object runtime tests for hibernation, alarms and per-series isolation;
- frontend unit tests and production build;
- backend test suite;
- Redis TLS CA/hostname enforcement and AOF restart fixture;
- synthetic outbox and metrics collector benchmarks;
- backend dependency audit and container build;
- backend container/shared-Redis/persistent-volume smoke;
- container image scan and vulnerability-report export;
- frontend dependency audit enforcement.

CI evidence is scoped to the exact commit and configured test environment. It does not establish public WSS, production Firebase, owner-host Redis failover, Android WebView lifecycle, or live market-data acceptance.

## 4. WebSocket evidence and remaining work

### Verified in repository CI
- Real local workerd WebSocket handshake and synthetic snapshot/update.
- Durable Object same-series two-client fan-out and different-series isolation.
- Single-use ticket consumption, including a concurrent two-socket race.
- Attachment restoration after Durable Object eviction.
- Authentication timeout alarms and preservation of authenticated sockets.
- Cursor duplicate/gap rejection and contiguous sequence acceptance.
- New failed-send isolation regression in this batch.

### Still open
1. Snapshot watermark and first-live-update continuity under interleaved ticket issuance, authentication, and update emission; define an explicit bounded replay/resnapshot contract.
2. A true slow-consumer policy with bounded outbound buffering or a justified close/resnapshot rule. The new test covers a thrown send only.
3. External production acceptance: public hostname/reverse proxy/TLS, live Firebase identity lifecycle, owner-host Redis persistence/failover, Android WebView foreground/background/process-death/network handover, and cross-instance fan-out.
4. Immutable snapshot installation receipt and independent owner-host receipt custody remain external acceptance items.

The Cloudflare proof remains synthetic-only. It uses no exchange feed, no production credentials, no hosted deployment, no domain, no paid account activation and no workers.dev/preview URL.

## 5. Indicator progress ledger — unchanged

No indicator formula, calculation kernel, shared hook, renderer, settings UI, or indicator-specific test was changed. This WebSocket regression receives **zero indicator implementation credit**.

| Indicator / subsystem | Status | Verified mathematical/data foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Candlestick overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial mean of 14 close-to-close changes; Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle/legend/latest values, lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/lifecycle/render/performance |
| Shared Indicator Hook | 🟨 Foundation | Exact-snapshot aligned multi-study output; ready/degraded accepted; demo/error suppressed; immutable revision recalculation regression | Actual chart binding, stale clearing on all identity changes, settings/legend, lifecycle/accessibility/performance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, verified bid/ask source contract, spaced-cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), reviewed blueprint, validated depth/liquidity contract, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance/methodology, reviewed blueprint, renderer and tests |

**Indicator invariants:** warm-up values remain null; output aligns to exact source-candle indices; prefix-causal/no future repaint; invalid/non-finite/gapped inputs are not silently converted to zero; stale outputs clear on symbol, venue, dataset, chart identity or timeframe changes. Footprint OFF preserves normal candle spacing; explicit ON alone enables spaced clusters. Footprint and Heatmap visual implementation remains blocked pending user reference images and scoped blueprint review.

Aggregate indicator completion remains **NOT SCORED** because study weights and denominator have not been approved.

## 6. Project progress dashboard

| Area | Status | Accounting |
|---|---|---|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 75% provisional | 30/40 criteria; 300/400 ticks |
| Stage 2 — Market Data Infrastructure | 🟧 Synthetic proof increment; not scored | Local workerd/DO tests verified; production acceptance remains open |
| Stage 3 — Chart Engine & Timeframe | ⬜ Not scored | No approved scoring denominator |
| Stage 4 — Indicators & Analytics | 🟨 Foundation states above; aggregate not scored | No indicator implementation delta in this batch |
| Stage 5 — Professional UI & Interactive Tools | ⬜ Not scored | No new acceptance evidence |
| Stage 6 — Hardening, Validation & APK Release | ⬜ Not scored | No new device/release acceptance |
| Gate 10 — external acceptance | 🟥 0/10 formally closed | No external gate closed by this batch |
| Overall project | **NOT SCORED** | Approved six-stage weights and denominator remain unavailable |

No historical overall percentage is promoted as current. Stage 1's 75% remains provisional and is not the overall project completion.

## 7. Next work queue

1. Specify and test snapshot/live cursor continuity across interleavings; then define bounded replay and resnapshot behavior.
2. Specify bounded slow-consumer handling and test queue limits, send failure, healthy-peer isolation, and cleanup.
3. Reconcile the synthetic proof's acceptance boundary against the production Redis-backed WebSocket path without conflating their guarantees.
4. Keep public WSS, live Firebase, owner-host Redis, Android and external acceptance gates visibly open until direct evidence exists.

**Target date:** approximately 24 December 2026. Planning target only, not a completion guarantee.

**Decision:** Batch 62J-178 is accepted as a test-only reliability improvement after all four exact-head CI workflows passed. No production or indicator completion credit is claimed.
