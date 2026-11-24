# Work Cycle — 24 November 2026 — Batch 62J-199
## Redis destructive-command ACL boundary, exact-head CI and indicator reconciliation

**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Verified source/test HEAD:** `23bf2da93ec8b4c935d2898a993f4d1c80ce9a7d`  
**Parent:** `4015ae0ffa70b82305c31c2fde7dd40f046cf824`  
**Official stage:** Stage 1 — Foundation, Security & Data Integrity  
**ZERO COST:** maintained  
**`main`:** untouched  
**Delivery target:** approximately 24 December 2026; planning target only

---

## 1. Scope and change summary

This batch closes a specific Redis ACL evidence gap discovered during the Batch 62J-198 retention lifecycle audit. It does not implement Redis Stream trimming or a retention worker.

**Changed source/test file:**
- `backend/tests/test_ohlcv_redis_acl_integration.py`

**Change:** the existing real-Redis ACL integration test now explicitly verifies that neither runtime identity can destroy replay history:
- Publisher `XTRIM` is denied.
- Publisher `XDEL` is denied.
- Gateway `XTRIM` is denied.
- Gateway `XDEL` is denied.
- Gateway `XGROUP DESTROY` is denied.

The test also retains its positive checks for publisher append/read-back and gateway group-create/read/ack/pending-reclaim operations, plus negative checks for database switching, out-of-scope keys, unauthorized writes and publisher consumer-group access.

No production runtime code, dependency, credential, Redis ACL definition, provider configuration, deployment or device was modified. The test uses disposable ACL users, random per-run credentials and an ephemeral CI Redis service.

## 2. Exact-head CI — all terminal

All four configured workflows completed **4/4 SUCCESS** on the exact source/test HEAD `23bf2da93ec8b4c935d2898a993f4d1c80ce9a7d`.

| Workflow | Run | Terminal result |
|---|---:|---|
| Automated Tests | [45313574302](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45313574302) | 🟩 SUCCESS — 40/40 job steps |
| CodeQL Security Analysis | [45313574375](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45313574375) | 🟩 SUCCESS — Python and JavaScript/TypeScript |
| Full Git History Secret Audit | [45313574338](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45313574338) | 🟩 SUCCESS — 6/6 steps |
| OCI ARM64 Image Readiness | [45313574445](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45313574445) | 🟩 SUCCESS — native ARM64 build/smoke workflow |

### Automated test evidence

- Backend pytest: **1,359 passed, 1 skipped, 6 warnings in 58.57 seconds**.
- Frontend: **320 passed across 34 test files**.
- The updated real Redis ACL integration test `test_real_redis_publisher_and_gateway_acl_roles_are_least_privilege` explicitly **PASSED**; it was not skipped.
- Dedicated Redis TLS fixture: **1 passed in 0.10 seconds**. It exercised CA and hostname validation against a TLS-only Redis listener.
- CI Redis TLS-only listener, AOF data and ACL survived the container restart check.
- npm audit: **0 vulnerabilities**.
- Backend `pip-audit`: **No known vulnerabilities found**.
- Frontend production build and bundle-secret scan: passed.
- Synthetic Durable Object runtime proof: **11 tests passed**.
- Backend container build and smoke: passed. Smoke covered health, persisted Redis ACL authentication, AOF data across restart, API fail-closed behavior during Redis outage, backend reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence and HTTP rate-limit rejection.
- Trivy image scan and JSON report export/upload: completed successfully. Artifact ID **14884616320**, 19,046 bytes. This report is CI artifact evidence, not an owner-host security certification.
- Six pytest warnings are non-failing WebSocket/Uvicorn deprecation warnings.

**Evidence boundary:** CI uses isolated runner services and temporary volumes. It does not prove a public owner-host WSS endpoint, production Firebase account flow, owner-host Redis durability/failover, provider entitlement, or physical Android lifecycle.

## 3. Redis retention — current precise state

### Implemented source-side retention

SQLite is the authoritative source/outbox:
- Global outbox window: **100,000 events**.
- Event insertion, high-water update, row deletion and monotonic retention-floor advancement share one SQLite transaction.
- Replay reads use a consistent source snapshot.
- Expired cursors, cursor-ahead requests and global cursor gaps fail closed and require a new snapshot.
- Per-timeframe bar history is independently bounded by configured caps.

### Redis Stream retention remains open

- Publisher appends deterministic IDs using `XADD` and verifies by `XRANGE`.
- Publisher ACL is limited to its intended append/read-back commands.
- Gateway ACL supports its group/consumer/ack/read and lease operations.
- Neither role has `XTRIM`, `XDEL` or destructive group-cleanup permission.
- Consumer groups are generation-scoped and old groups/PEL entries are retained rather than deleted without a safe cleanup protocol.
- No project-owned Redis retention controller, trim janitor, durable gateway inventory or group/PEL cleanup worker was found.

### Additional missing contract: authoritative gateway inventory

The source publisher activation path receives `required_gateway_ids` and installation receipts from an owner-supplied snapshot-verifier callback. The code validates receipt identity and equality for source ID, stream key, snapshot generation, cursor and SHA-256. This is a strict callback boundary, not a persistent gateway registry.

Before implementing retention, the owner-controlled design must define:
1. The durable authoritative gateway inventory and stable gateway identity.
2. Explicit gateway lifecycle states, including how an operator retires a gateway; elapsed time or last-seen timestamps alone cannot silently retire a required replica.
3. Authenticated receipt provenance, key ownership/rotation/revocation and immutable evidence custody.
4. Snapshot-generation transition and per-gateway durable applied-cursor/floor acknowledgement.
5. Treatment of old generation consumer groups and pending entries.
6. A crash-safe monotonic intent/commit/trim/reconcile protocol.
7. A separate least-privilege retention identity limited to the exact stream and proven commands.
8. Real Redis 7.x integration tests for floor boundaries, lagging gateways, PEL behavior, concurrent replay, trim crashes and ACL-negative cases.

**Decision:** do not implement naive `XTRIM MAXLEN`, do not add trim rights to publisher/gateway identities, and do not invent a gateway registry lifecycle. Retaining more Redis history is safer than deleting entries needed for a lagging gateway or recovery generation.

## 4. WebSocket progress and remaining acceptance

Repository-side foundations remain present and CI-tested:
- Single-use authenticated ticket and origin/entitlement checks.
- Snapshot/watermark and sequence validation.
- Durable publisher checkpoint and fenced lease.
- Redis append/read-back and per-gateway replica consumer.
- Apply-before-ACK, pending reclaim and generation-scoped consumer groups.
- Cursor-contiguous replay and resnapshot-required handling for missing/expired history.
- Subscriber isolation, queue bounds, failure cleanup and reconnect lifecycle.
- CI real Redis ACL, TLS-only fixture, AOF restart and two-ASGI-process regression coverage.

Still open:
- Public HTTPS/WSS route on a verified zero-cost owner-controlled host.
- Real no-billing Firebase sign-in, expiry/revocation and entitlement-to-ticket exchange.
- Owner-host Redis TLS/ACL/secret rotation/persistence/failover and gateway inventory/receipt authentication.
- Authenticated snapshot transfer and per-gateway durable receipts on actual hosts.
- Browser and Android WebView foreground/background/network/force-stop/reboot acceptance.
- Real operator metrics persistence, alerts, acknowledgement and recovery drills.

Synthetic CI tests are not production WSS acceptance. The user has not been asked to install or repair any artifact.

## 5. Complete indicator progress ledger

No indicator source, formula, hook, chart binding, renderer, pane, toggle, legend or indicator-specific test was changed by Batch 62J-199. Indicator implementation credit for this batch: **0**. The existing calculation and trust-boundary evidence is preserved and reconciled below.

| Indicator/subsystem | Status | Verified calculation/data foundation | First valid index | Remaining acceptance |
|---|---|---|---:|---|
| SMA20 | 🟨 Foundation | Arithmetic mean of latest 20 closes | 19 | Candlestick overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; multiplier (2/(20+1)=2/21) | 19 | Overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change average followed by Wilder-smoothed gain/loss recurrence | 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD 25; signal/histogram 33 | Pane, lines, histogram, zero guide, toggle, legend/latest values, lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations | 19 | Upper/middle/lower overlay, toggle, latest values, identity clearing, lifecycle, render/performance |
| Shared `useMarketIndicators()` | 🟨 Foundation | Immutable canonical-series snapshot; shared calculation cache per snapshot revision; backend trust-state gate | Per study | Actual chart binding, stale clearing on identity/timeframe changes, settings, legend, accessibility and performance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask truth | N/A | Owner visual reference, approved blueprint, verified bid/ask source contract, dedicated spaced-cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | N/A | Owner visual reference, validated depth/liquidity contract, approved blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted calculation/runtime renderer | N/A | Defensible data provenance/calculation contract, approved blueprint, renderer and tests |

### Indicator test and integration evidence

- `src/indicators/indicatorCalculations.test.ts`: **17 tests** cover warm-up alignment, SMA/EMA behavior, Wilder RSI edge cases and recurrence, MACD separate warm-ups, population standard deviation, supported timeframe alignment, invalid/non-finite inputs, prefix causality, large finite values and cancellation stability.
- `src/indicators/useMarketIndicators.test.ts`: **7 tests** cover no output without selected backend data, exact keyed snapshot, recalculation after immutable revision, canonical-series isolation, shared frozen result, ready/degraded versus demo/error behavior, and unavailable clearing.
- The shared hook only emits indicator values from non-empty validated backend snapshots in `ready` or `degraded` state. Demo, loading, unavailable and error states do not emit values.
- `CandlestickChart.tsx` currently creates only the candlestick series and does not bind `useMarketIndicators()`. Visible indicator overlays, panes, toggles and legends are therefore **not implemented**.
- Footprint is simulation-only. Heatmap and Liquidation Maps are unimplemented.

### Required invariants and visual gates

1. Warm-up remains `null`; never replace missing values with zero.
2. Outputs preserve source-array length and candle-index/timestamp alignment.
3. Prefix causality: future bars must not rewrite earlier outputs.
4. Reject invalid/non-finite/gapped input instead of fabricating values.
5. Instrument, venue, dataset, chart identity and timeframe changes clear stale output.
6. Footprint OFF preserves ordinary candlestick spacing; only explicit Footprint ON may activate the dedicated spaced candle/cluster layout.
7. Do not start visible indicator work before official Stage 4 and the applicable blueprint review.
8. Do not start Footprint or Heatmap visual implementation before the owner provides reference images and reviews the scoped blueprint.

**Aggregate indicator progress: NOT SCORED.** There is no approved per-study weighting or acceptance denominator. Calculation readiness must not be presented as finished user-facing indicators.

## 6. Project progress and stage accounting

| Meter | Current state | Status |
|---|---:|---|
| Official stage | Stage 1 of 6 | 🟨 Active |
| Stage 1 | 30/40 criteria = 300/400 ticks = 75% provisional | 🟨 |
| Gate 10 | 0/10 formally closed | 🟥 |
| Stages 2–6 | Not scored / not officially opened | ⬜ |
| Overall project | NOT SCORED | ⚪ |
| Aggregate indicator progress | NOT SCORED | ⚪ |
| Exact-head CI | 4/4 SUCCESS on `23bf2da...` | 🟩 |

Open Stage 1 external criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38 and 39**. The ACL negative-test improvement does not close a criterion or award a Stage 1 tick.

## 7. Next engineering sequence

1. Preserve the newly verified exact-head CI.
2. Specify the owner-controlled durable gateway inventory, explicit retirement semantics and receipt-authentication boundary before writing retention-controller code.
3. Design the retention intent/commit/trim/reconcile state machine and exact Redis version/PEL behavior; keep destructive commands denied to publisher/gateway roles.
4. Add real Redis 7.x crash, lagging-gateway, PEL and concurrent-replay tests before enabling trim.
5. Continue reconciling Stage 1 external evidence without inflating 30/40.
6. Keep standard indicator UI parked until Stage 4; keep Footprint/Heatmap visuals reference-gated.

**ZERO COST:** no paid hosting, Redis, data provider, backup, monitoring, domain, subscription, trial conversion, billing activation or publication fee introduced. If a requirement cannot be met safely at zero incremental cost, mark it constrained/deferred rather than weaken security or persistence.

---

**Final disposition:** Batch 62J-199 is accepted at repository/CI level. The destructive-command ACL boundary is now explicitly tested against real ephemeral Redis in CI. Redis Stream retention itself remains intentionally unimplemented pending an authoritative gateway inventory and crash-safe floor protocol. Stage 1 remains 75% provisional; Gate 10 remains 0/10 closed; overall project and aggregate indicator percentages remain NOT SCORED. Delivery target remains approximately 24 December 2026.
