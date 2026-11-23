# DEZZTA CHART — Work Cycle 62J-183
## Durable Object ticket-binding and cursor-continuity regression proof

**Date:** 23 November 2026  
**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Parent checkpoint:** `74bbd5163f3498eb3e117196130b29857721d7e1`  
**Protected branch:** `main` untouched  
**Cost policy:** ZERO COST; local Cloudflare test runtime only, no deployment or paid account.

## 1. Starting evidence

At the parent checkpoint, the dedicated Cloudflare Durable Object runtime suite had four passing cases on the exact tested commit. The cases exercised same-series fan-out/isolation, one-time ticket consumption, eviction/attachment restoration, and real Durable Object alarm expiry. The Automated Tests workflow was still completing later container-report/export steps; its overall conclusion had not yet been reported as success at the time of this work cycle.

## 2. New runtime regression coverage

Two additional tests were added to `cloudflare/proof/worker.durable-object.runtime.mjs`.

### A. Exact-series ticket binding

- Issue a ticket for synthetic series A.
- Attempt authentication on a different synthetic series B.
- Verify the wrong-series socket closes with 4401.
- Reuse the same ticket on its intended series A.
- Verify authentication succeeds and the expected 50-bar snapshot is delivered.

This tests the invariant that a wrong-series attempt cannot consume a ticket belonging to another series.

### B. Contiguous cursor acceptance and no rejected-event fan-out

- Accept sequence 51 and verify one authenticated same-series recipient receives it.
- Submit duplicate sequence 51 and require HTTP 409 / `sequence_conflict`.
- Submit skipped sequence 53 and require HTTP 409 / `sequence_conflict`.
- Verify neither rejected event is delivered to the WebSocket subscriber.
- Submit contiguous sequence 52 and verify it is accepted and delivered.

This proves the synthetic sequence gate rejects duplicates and gaps without broadcasting invalid events, while preserving the next valid cursor.

## 3. Test accounting

| Runtime behavior | Before | Added | Current definition count |
|---|---:|---:|---:|
| Exact-series fan-out / isolation | 1 | 0 | 1 |
| Single-use ticket replay rejection | 1 | 0 | 1 |
| Hibernation / attachment restoration | 1 | 0 | 1 |
| Alarm expiry / 4408 close | 1 | 0 | 1 |
| Wrong-series ticket binding | 0 | 1 | 1 |
| Duplicate / gap cursor rejection | 0 | 1 | 1 |
| **Total** | **4** | **2** | **6** |

These are test definitions. The initial exact-head run found a race in the new cursor test harness: the test installed its message listener after awaiting the emit response, so a fast runtime delivery could precede listener registration. The source WebSocket sequence gate did not fail; the test harness timed out waiting for an already-dispatched message. The follow-up correction installs each expected-message listener before the corresponding emit request. The negative assertion for rejected duplicate/gap events remains intact. The two new tests are **not marked passed until the corrected exact-head CI runtime step completes**.

## 4. Scope and safety boundaries

- Synthetic-only series and data remain isolated under `cloudflare/proof`.
- No real exchange feed, broker, user identity, Firebase token, production secret, public WSS, or live provider is used.
- No production FastAPI/Redis runtime is replaced.
- No paid Cloudflare service, account, deployment, domain, or billing configuration is introduced.
- `main` remains untouched.
- No indicator source, formula, renderer, or UI is modified.

## 5. Remaining WebSocket acceptance queue

1. Complete exact-head CI and fix any newly observed failure.
2. Continue production/reference backend tests for snapshot-to-live handoff and durable replay.
3. Verify provider demand reference-counting across chart open/switch/close and multiple users; do not infer this from downstream fan-out tests.
4. Verify owner-host Redis receipt, lease, persistence, restore and cross-instance lifecycle.
5. Keep Firebase production identity, public TLS/WSS, Android foreground/background/process-death/network-handover as external acceptance gates.
6. Verify slow-consumer/backpressure behavior against documented APIs and runtime evidence.
7. Never substitute synthetic fixtures or unlicensed public pages for live market data.

## 6. Full project and indicator ledger

| Stage / gate | Status | Evidence boundary |
|---|---|---|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 **30/40 = 75% provisional** | Existing approved provisional score; unchanged |
| Stage 2 — Market Data Infrastructure | 🟦 Synthetic runtime proof expanding; **NOT SCORED** | No production host/provider acceptance |
| Stage 3 — Chart Engine & Timeframe | ⬜ **NOT SCORED** | No new acceptance evidence |
| Stage 4 — Indicators & Analytics | ⬜ **NOT SCORED** | No indicator UI implementation in this batch |
| Stage 5 — Professional UI & Interactive Tools | ⬜ **NOT SCORED** | No new acceptance evidence |
| Stage 6 — Hardening, Validation & APK Release | ⬜ **NOT SCORED** | Exact-head workflow and external device/release gates remain |
| Gate 10 — External acceptance | 🟥 **0/10 formally closed** | CI does not close external owner-host gates |
| Gate 25 — Snapshot/replica custody | 🟧 **OPEN** | Owner-host receipt and replay custody outstanding |
| Gate 36 — Public WSS/Firebase/Android lifecycle | 🟥 **OPEN** | External production identity/network/device acceptance outstanding |
| Gate 38 — Owner-host telemetry persistence/restore/operations | 🟧 **OPEN** | Operational host evidence outstanding |
| Gate 39 — Alert acknowledgement/recovery | 🟥 **OPEN** | Operator acceptance outstanding |
| Overall project | **NOT SCORED** | Approved weighted denominator is not defined |

### Indicator status — unchanged

| Indicator | Status | Mathematical / implementation baseline | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Chart overlay, toggle, legend/value, lifecycle/render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/value, lifecycle/render/performance |
| RSI14 Wilder | 🟨 Foundation | 14-change seed; Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle/legend/lifecycle |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram index 33 | Pane, lines, histogram, zero line, toggle/legend/lifecycle |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Three-line overlay, toggle/value/lifecycle/render |
| Shared Indicator Hook | 🟨 Foundation | Exact-snapshot aligned multi-study output | Hook/chart binding, stale clearing, settings/legend/lifecycle |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator, not exchange-native bid/ask | User reference images, scoped blueprint review, validated bid/ask source, cluster renderer |
| Heatmap | 🟥 Not implemented | No accepted renderer | User reference images, scoped blueprint, validated depth data contract |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render contract | Defensible provenance/methodology, blueprint and renderer |

Indicator invariants remain mandatory: warm-up is null, outputs align to source-candle indices, prefix causality/no future leakage, reject invalid/gapped data, clear stale output on identity changes. Footprint OFF preserves ordinary candle spacing; explicit ON alone activates spaced clusters. Footprint and Heatmap visuals remain blocked until the user provides reference image(s) and reviews the scoped blueprint. Indicator aggregate remains NOT SCORED.

## 7. Delivery and accounting

**Owner target:** 24 December 2026 — planning target, not a guaranteed completion date.

No project-wide percentage is fabricated. No Stage 1 ticks, Gate 10 closures, Stage 2 production acceptance, or indicator completion credit is awarded solely for adding these tests. The two added tests receive acceptance credit only after exact-head CI passes.


## 8. Follow-up test-harness correction

The first CI execution on the initial 62J-183 commit reported 5/6 runtime tests passing. The exact-series ticket-binding test passed. The cursor test's first and final event listeners were initially attached after awaiting the emit HTTP response, which left a timing window where the WebSocket message could be dispatched before the listener existed. The test has been corrected to create the message promise before each accepted emit. This is a deterministic ordering correction only; it does not alter Worker/DO runtime behavior, remove assertions, or suppress the failure. Re-run exact-head CI before accepting the two added cases.


## 9. CI runtime compatibility correction

The first exact-head run exposed an environment mismatch in the existing CI configuration: the Worker/DO test lane installed Miniflare versions requiring Node.js >=22.0.0 and >=22.12.0, while the shared CI job was pinned to Node.js 20.20.2. npm reported EBADENGINE warnings. Although the test process started, running a Cloudflare runtime dependency on an unsupported Node major is not an acceptable reproducibility baseline. The CI Node setup is therefore advanced to Node.js 22 for the shared frontend/Worker test job. This is a CI toolchain-only change; it does not alter production application runtime or dependencies. The corrected exact-head workflow must verify frontend tests/build and the Cloudflare runtime under Node 22.
