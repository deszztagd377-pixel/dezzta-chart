# DEZZTA CHART — Batch 62J-178
## Durable unauthenticated WebSocket timeout and lifecycle cleanup

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Code/test HEAD:** `264b54fbb87b96133d13dd7f82089bde4cd9d47f`  
**Protected branch:** `main` untouched  
**Cost:** ZERO COST; no hosted deployment or paid resource  
**CI:** no completed CI status was returned for this exact commit at documentation time. No pass is claimed.

## 1. Problem addressed

The prior proof accepted a WebSocket and required a single-use ticket, but a client that never completed authentication could leave a socket open indefinitely. That consumed one of the bounded per-series connection slots and created avoidable resource retention.

## 2. Implementation

- Added a fixed 15,000 ms unauthenticated-session deadline.
- Added Durable Object storage-alarm scheduling based on the earliest unauthenticated socket deadline.
- Added an alarm handler that closes expired unauthenticated sockets with close code 4408 and reschedules only for remaining pending sessions.
- Alarm scheduling is one-shot and demand-driven; no recurring polling timer or external service was added.
- Authorized sockets do not retain the unauthenticated-session alarm.
- Authentication is rejected both before ticket consumption and after asynchronous ticket consumption if the connection deadline has passed. A ticket is therefore not consumed by an already-expired connection.
- The connection path schedules cleanup immediately after serializing its unauthenticated attachment.
- The timeout is exposed through `proofLimits.unauthenticatedSocketTtlMs` for deterministic contract tests.

## 3. Regression coverage added

The synthetic Node proof suite now declares **23 tests** (previously 20). Three new test cases cover:
1. Earliest-deadline alarm scheduling, expiration of overdue sockets, preservation of a later pending socket, and alarm deletion after all unauthenticated sockets expire.
2. Authorized sockets not retaining an unauthenticated-session alarm.
3. Authentication after the deadline being rejected without consuming its single-use ticket.

An existing bounded-limits test also asserts the exact 15,000 ms timeout contract.

The test suite uses a deterministic in-memory storage/socket test double. These tests do not replace a real Cloudflare runtime test.

## 4. Files and commits

- `cloudflare/proof/worker.mjs`: 15-second timeout, Durable Object alarm scheduler/handler, deadline checks, proof-limit export.
- `cloudflare/proof/worker.node-test.mjs`: three timeout/alarm regression tests and timeout contract assertion.

Code/test commits:
- `c3b407fe8f2a8034f66ef22fef8e8bff5a2981db` — durable unauthenticated socket alarm.
- `77d62e9e7d481af3fee5754cdc6da030f4cfaa85` — timeout/alarm regression tests.
- `8caa2d574ecf04f7334aa04693777fda8ff59c86` — expose timeout in proof limits.
- `264b54fbb87b96133d13dd7f82089bde4cd9d47f` — assert timeout contract; current code/test HEAD.

## 5. Acceptance boundary

This is still synthetic-only proof work. The current evidence does not establish:
- Cloudflare runtime alarm delivery timing or alarm persistence across real eviction;
- actual WebSocketPair handshake or network disconnect behavior;
- real hibernation/rehydration and attachment persistence;
- slow-consumer/backpressure behavior in Cloudflare's socket implementation;
- durable event replay or production authentication;
- public HTTPS/WSS, Android client acceptance, live market data or exchange integration.

Next required runtime proof: run the Worker locally with a pinned Wrangler/Miniflare toolchain, verify actual WebSocket handshake and ticket flow, and observe alarm-driven close behavior under runtime-controlled time. Hosted Workers deployment remains disabled.

## 6. Complete indicator ledger — unchanged

No indicator calculation, chart renderer or indicator UI was modified. This batch receives **zero indicator implementation credit**.

| Indicator / subsystem | Status | Mathematical/data foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial mean of 14 close changes; Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero line, toggle/legend/latest values |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, latest values, identity/lifecycle/render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | Exact-snapshot aligned multi-study output | Hook tests, chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask volume | User reference image(s), reviewed blueprint, verified data contract, cluster renderer |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), reviewed blueprint, validated data contract, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render/data contract | Defensible provenance/methodology, reviewed blueprint, renderer and tests |

### Indicator invariants
- Warm-up output is `null`, never fabricated zero.
- Exact source-candle index alignment and prefix causality.
- Invalid/non-finite bars and gaps are rejected, not silently zero-filled.
- Clear stale results on symbol, venue, dataset, chart identity and timeframe changes.
- No future-candle leakage or repainting.
- Calculation, rendering, interaction, lifecycle, accessibility and performance are independent acceptance dimensions.
- Footprint OFF preserves normal candle spacing; explicit ON alone activates spaced clusters.
- Footprint/Heatmap visual implementation remains blocked until the user provides reference images and reviews a scoped blueprint.
- Aggregate indicator completion remains **NOT SCORED**; no approved denominator/weights exist.

## 7. Project progress indicators

| Stage / gate | Status | Current evidence |
|---|---|---|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 30/40 = 75% provisional | Previously accepted score; unchanged |
| Stage 2 — Market Data Infrastructure | 🟦 Synthetic-only proof increment; not scored | Cursor/attachment integrity and unauthenticated timeout added; runtime acceptance open |
| Stage 3 — Chart Engine & Timeframe | ⬜ Not scored | No new acceptance evidence |
| Stage 4 — Indicators & Analytics | ⬜ Not scored | Full indicator ledger above; no code changes |
| Stage 5 — Professional UI & Interactive Tools | ⬜ Not scored | No new acceptance evidence |
| Stage 6 — Hardening, Validation & APK Release | ⬜ Not scored | No new device/release acceptance |
| Gate 10 — External acceptance | 🟥 0/10 formally closed | No external gate closed |
| Gate 25 — Snapshot/replica custody | 🟧 Open | Requires runtime evidence |
| Gate 36 — Public WSS/Firebase/Android lifecycle | 🟥 Open | External acceptance required |
| Gate 38 — Owner-host telemetry persistence/restore/operations | 🟧 Open | Not implemented/accepted in this batch |
| Gate 39 — Operational alert acknowledgement/recovery | 🟥 Open | Not implemented/accepted in this batch |
| Overall project | **NOT SCORED** | Approved weighted denominator not available |
| Significant progress | 🟦 Unauthenticated socket lifecycle hardening | 15-second durable alarm deadline and 3 new regression cases |

## 8. Next work queue

1. Pinned local Wrangler/Miniflare runtime smoke; no hosted deployment.
2. Real runtime WebSocketPair handshake and single-use ticket consumption.
3. Same-series fan-out and cross-series isolation.
4. Hibernation/eviction and attachment restoration.
5. Runtime alarm expiry and close-code verification.
6. Slow-consumer/backpressure behavior with only documented runtime capabilities.
7. Snapshot-to-live cursor continuity and bounded durable replay.
8. Keep production authentication, public WSS and Android acceptance as separate external gates.

**Target date:** 24 December 2026 (planning target, not a completion guarantee).

**Decision:** the unauthenticated connection retention gap is addressed in the synthetic source and test contract. CI and real runtime acceptance remain pending; no project-wide or indicator percentage is increased.
