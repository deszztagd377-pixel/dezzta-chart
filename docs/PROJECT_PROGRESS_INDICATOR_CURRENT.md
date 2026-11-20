# DEZZTA CHART — CURRENT PROJECT CONTROL DASHBOARD

**Checkpoint:** 20 November 2026  
**Active branch:** `phase-2/market-data-foundation`  
**Latest verified code HEAD:** `407d2b38882e92cdf6db5b7df6c44350b6cd746d`  
**Latest documentation checkpoint previously recorded:** `ef2bfe439879b92cf73f74f0d6abdbf96db6dfe9`  
**Current audit batch:** 62J-15 — WebSocket lifecycle and replay/live handoff review  
**Cost policy:** ZERO COST. No paid providers, hosting, deployments, Vercel/Cloudflare actions, or Termux requirement.

> This document is the current concise dashboard. Historical work-cycle reports remain the evidence trail. Do not infer that a docs-only commit has rerun or revalidated code CI.

## 1. Project-level progress

| Measure | Verified position | Status |
|---|---:|---|
| Stage 1 | 30/40 criteria = 300/400 ticks | 🟨 75% provisional |
| Gate 10 | 0/10 formally closed | 🟥 All ten remain OPEN |
| Stages 2–6 | No approved scored acceptance denominator | ⬜ Not scored |
| Overall project | M1–M8 weighting not approved | ⬜ Not established |
| Indicator aggregate | No approved weighted denominator | ⬜ Not established |

Do not publish a guessed overall percentage. Stage 1's provisional score is not the overall project score.

## 2. Ten-gate control board

All ten tracked gates remain formally OPEN (0/10 closed) until owner-controlled acceptance evidence is recorded. Repository code and CI cannot substitute for credentials, target-environment operation, restore drills, or production access evidence.

| Gate | Status | Closure evidence still required |
|---|---|---|
| 8 | 🟧 OPEN | Owner-controlled environment/operational acceptance evidence |
| 20 | 🟧 OPEN | Target environment integration and acceptance evidence |
| 25 | 🟧 OPEN | Redis TLS/ACL credentials, independent gateway instances, outage/recovery and parity evidence |
| 30 | 🟧 OPEN | Owner-side infrastructure/security acceptance |
| 31 | 🟧 OPEN | Operational recovery/restore evidence |
| 34 | 🟧 OPEN | WSS/client integration and target-device acceptance |
| 35 | 🟧 OPEN | Collector/provider operational evidence |
| 36 | 🟧 OPEN | Multi-instance Redis relay and end-to-end gateway acceptance |
| 38 | 🟧 OPEN | Operator runbook and operational drill evidence |
| 39 | 🟧 OPEN | Final owner sign-off and evidence completeness |

The ten tracked gate IDs above are the current open set: 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. No gate has been closed by documentation-only work.

## 3. WebSocket / Redis engineering status

### Implemented library foundations

- Global source SQLite snapshot export with bounded JSONL streaming, manifest row count and SHA-256 verification.
- Isolated replica snapshot installation with atomic transaction/checkpoint update and replica identity.
- Incremental replica event apply with strict event contract, cursor continuity, dedupe and retention handling.
- Source-SQLite publisher checkpoint with fenced lease and deterministic Redis Stream IDs.
- Redis append retry/read-back validation and bounded publisher loop.
- Per-gateway consumer groups, pending reclaim via XAUTOCLAIM, durable SQLite apply before XACK, and generation-scoped group reset.
- Independent publisher/consumer process tests against the Redis 7 CI service.
- Durable replica-to-pipeline/hub bridge, cursor-aware duplicate suppression, callback dispatch onto the owning event loop, and managed worker lifecycle.
- Source-SQLite WebSocket replay/live boundary merge; replay completion is emitted only after successful merge. Handoff failure emits sanitized resnapshot-required and closes with 1013.

### 62J-15 audit findings

Reviewed the Redis consumer, managed worker, event-loop dispatcher, replica bridge, stream hub and corresponding real-Redis tests.

- Consumer applies the event to durable replica SQLite before callback and ACK.
- Callback failure leaves the event pending; same-consumer pending entries are retried before newer entries.
- Restart recovery uses XAUTOCLAIM; deleted pending entries require a fresh snapshot.
- Dispatcher marshals work to the owning event loop and waits up to its configured deadline; callback errors/timeouts prevent ACK.
- Managed worker has bounded exponential retry, terminal resnapshot-required state and bounded synchronous/asynchronous shutdown.
- Snapshot/replay/live merge validates exact series identity, monotonic replay cursors, queued live cursor ordering and queue capacity; covered live events are discarded and newer events are resequenced.
- The consumer worker is deliberately not wired into FastAPI startup. That is a safety boundary, not a completed production integration.

### Remaining WebSocket acceptance blockers

1. Separate independently started ASGI backend instances/containers with real shared Redis and independent replica SQLite files.
2. End-to-end publisher restart, consumer restart, Redis outage/recovery, snapshot reinstallation and cursor parity under process/container failure.
3. Owner-provisioned Redis TLS and least-privilege ACL credentials, including credential rotation and target-environment verification.
4. Startup/shutdown orchestration and ownership proving exactly one sequential consumer worker per gateway replica group.
5. Public WSS/browser/Android end-to-end verification.
6. Retention/stream trimming policy and operational cleanup authorization. Runtime gateway ACL must not receive destructive group-destroy permissions.

Do not wire publisher/consumer into `main.py` until these prerequisites and lifecycle tests pass. No production secrets or ACL changes have been performed.

### CI evidence boundary

At code HEAD `407d2b38882e92cdf6db5b7df6c44350b6cd746d`, the previously recorded exact-head workflows passed:
- Automated Tests: run `44564212673` — backend 1,153 passed; frontend 236 passed across 28 test files; build, scans, dependency audit, container and Redis/persistent-volume checks passed.
- CodeQL Python and JavaScript/TypeScript: run `44564212707` — SUCCESS.
- Full Git History Secret Audit: run `44564212714` — SUCCESS.

The later docs-only checkpoint does not change code and does not imply a new code CI run.

## 4. Complete indicator progress ledger

### Color legend
- 🟩 Verified implementation and required tests for the stated scope.
- 🟨 Calculation/data foundation exists; visible chart integration or lifecycle acceptance remains.
- 🟧 Gated by required reference, blueprint or owner input.
- 🟥 Not implemented / no validated implementation.
- ⬜ Not assessed.

| Indicator / subsystem | Status | Formula / contract | First valid output | Remaining work |
|---|---|---|---:|---|
| SMA 20 | 🟨 Foundation | Arithmetic mean of 20 closes | Index 19 | Chart overlay, independent toggle, legend/latest value, stale clearing, render/lifecycle tests |
| EMA 20 | 🟨 Foundation | SMA-seeded EMA; alpha = 2/21 | Index 19 | Overlay, toggle, legend/latest value, stale clearing, render/lifecycle tests |
| RSI 14 | 🟨 Foundation | Wilder-smoothed gains/losses | Index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend, stale clearing, render tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD index 25; signal/histogram index 33 | Dedicated pane, two lines, histogram, zero guide, toggle, legend, render tests |
| Bollinger 20,2 | 🟨 Foundation | SMA20 ± 2 population standard deviations | Index 19 | Upper/middle/lower overlay, toggle, current values, stale clearing, render tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot only; no DEMO fallback | Depends on snapshot | Active chart identity/timeframe binding, loading/error states, stale clearing, cross-series isolation |
| Footprint | 🟧 Gated | Deterministic educational accumulator; explicitly SIMULATED | Depends on selected candle/price levels | User reference image, reviewed blueprint, ON-only cluster renderer, bid/ask cells, tests/performance |
| Heatmap | 🟥 Not implemented | Source and calculation contract not approved | N/A | User reference, reviewed blueprint, data contract, calculations, renderer, controls and tests |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract | N/A | Source feasibility, reference/blueprint, calculation, renderer, controls and tests |

### Indicator correctness rules

1. Indicator arrays remain aligned to candle indexes.
2. Warm-up positions are null/unavailable, never fabricated zeros.
3. SMA20 first output is index 19.
4. EMA20 uses SMA seed and alpha 2/21; first output index 19.
5. RSI14 uses 14 close-to-close changes for initialization and Wilder smoothing; first output index 14.
6. MACD12/26 first output index 25; signal and histogram first output index 33.
7. Bollinger20 uses population standard deviation, not sample deviation; first output index 19.
8. Symbol, venue, dataset, timeframe and chart identity changes must invalidate stale indicator values.
9. Each indicator needs an independent visibility control, correct overlay/pane, current value and render/lifecycle tests.
10. Calculation tests do not prove visual rendering, provider correctness or live synchronization.

### Visual feature gates

- Footprint is SIMULATED and must never be labelled exchange-native order flow.
- Footprint OFF preserves ordinary candlestick spacing. Only explicit ON switches to spaced candle/cluster layout.
- Do not implement Footprint or Heatmap visuals until the user supplies the relevant reference image and reviews the scoped blueprint.
- Heatmap and Liquidation Maps must not be represented as live market-derived data without validated source and calculation contracts.

## 5. Immediate engineering work order

1. Complete isolated ASGI/container lifecycle and failure-matrix tests for the WebSocket relay.
2. Verify dispatcher timeout/cancellation behavior under a deliberately blocked event loop and ensure no ACK or cursor-order corruption.
3. Verify worker shutdown during idle polling, pending retry, callback execution and Redis disconnect.
4. Complete owner-side Gate 25/36 acceptance only with real TLS/ACL and independent-instance evidence.
5. Return to indicator implementation in the ledger order: shared hook lifecycle, SMA/EMA overlays, RSI/MACD panes, Bollinger overlay, then render-level regression tests.
6. Keep Footprint/Heatmap visual work gated on the user's references and blueprint review.

## 6. Cost, deployment and device policy

- ZERO COST remains mandatory.
- No paid data provider, hosting, subscription or publication fee is assumed.
- No Vercel or Cloudflare deployment/promotion is authorized.
- No deployment is needed to run repository CI.
- No Termux is currently required.
- `main` must remain untouched; all work stays on `phase-2/market-data-foundation`.

**Accounting rule:** Only verified code/tests change implementation status. Only owner-controlled evidence closes external gates. Documentation updates never manufacture implementation progress.
