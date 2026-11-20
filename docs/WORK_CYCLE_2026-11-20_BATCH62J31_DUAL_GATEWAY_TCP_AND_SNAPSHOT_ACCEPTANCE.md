# Batch 62J-31 — Dual-gateway TCP outage and snapshot-generation acceptance

**Date:** 20 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Exact source/test HEAD:** `cf6219a1f0fbea5a0daf8378ef47af386f8446fa`  
**Scope:** complete the two missing automated WebSocket E scenarios using the existing Redis 7 CI service and local SQLite fixtures. No runtime behavior changed.

## 1. Exact-head CI

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44708222353](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708222353) | SUCCESS |
| CodeQL | [44708222403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708222403) | SUCCESS — Python + JavaScript/TypeScript |
| Full Git History Secret Audit | [44708222417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708222417) | SUCCESS |

- Backend pytest: **1,166 passed, 6 warnings in 30.86s**.
- Frontend: **236 passed across 28 test files**.
- Backend container image build, shared Redis/persistent-volume smoke, image scan and vulnerability report export: SUCCESS.
- New TCP-outage test: PASSED.
- New two-replica snapshot-generation test: PASSED.

## 2. Dual-ASGI TCP network-path interruption

Added `_RedisTcpFaultProxy`, a test-only standard-library TCP forwarder. Each ASGI process connects through its own proxy to the same Redis 7 service.

The test:
1. Starts two independent Uvicorn/FastAPI gateway processes with separate replica SQLite databases.
2. Authenticates and subscribes two real WebSocket clients; both receive the empty cursor-0 snapshot.
3. Waits until each gateway has an established TCP connection to Redis through its own proxy.
4. Severs both existing gateway-to-Redis TCP sockets and rejects reconnect attempts while outage mode is active.
5. Restores both network paths without restarting either ASGI process.
6. Publishes source cursor 1 through the direct CI Redis connection.
7. Verifies both WebSocket clients receive cursor 1, both durable replica checkpoints reach 1, and both ASGI processes remain alive.

**Evidence boundary:** this is a controlled TCP network-path interruption, not a Redis server shutdown, host failure or production network drill. It proves the gateways recover from broken Redis TCP connections without process restart.

## 3. Two-replica snapshot-generation replacement

Added a cross-process acceptance test:
1. Two independently identified replica databases install the same initial source snapshot and create distinct generation-scoped consumer groups.
2. Both replicas apply cursor 1.
3. Cursor 2 is delivered to each old group and deliberately left pending.
4. The source exports one verified snapshot at high-water cursor 2; both durable replicas install that exact snapshot.
5. Each replica's new generation group is distinct from its old group and from the other replica's group.
6. Two separately spawned gateway consumer processes start against the new-generation replicas and consume cursor 3.
7. Both durable checkpoints converge at cursor 3.
8. Each old group still has its old pending entry; each new group has zero pending entries. No old group is destructively deleted.

**Evidence boundary:** this verifies coordinated replacement of two durable replica stores and new-generation process consumers. It is not a live in-place ASGI pipeline replacement; gateways bootstrap the installed snapshot when their new consumer processes start.

## 4. WebSocket E disposition

The two remaining automated scenarios from the prior E matrix are now passed:
- Dual-ASGI real TCP path interruption, reconnect and cursor parity.
- Two-replica snapshot-generation replacement, old-pending isolation and post-install cursor parity across independent processes.

Therefore the **automated WebSocket E failure matrix is complete for the defined repository/CI test scope**.

The following production/operational acceptance requirements remain separate and open:
- Production snapshot artifact distribution, integrity verification, rotation and rollback contract.
- Production Redis TLS, least-privilege ACL, credential rotation and target-host verification.
- Public authenticated WSS, browser and Android WebView acceptance.
- Stream retention/trim policy, authorized old-group cleanup, operator runbook and recovery drill.

Do not equate CI completion with production WebSocket readiness.

## 5. Gate 10 follow-through

| Gate | Status | Current independent acceptance requirement |
|---:|---|---|
| 8 | 🟧 OPEN | Actual host secret injection and leakage review |
| 20 | 🟧 OPEN | Real no-billing Firebase sign-in/revocation and client acceptance |
| 25 | 🟧 OPEN | Owner-host Redis TLS/ACL/persistence/recovery; new CI evidence is repository-level only |
| 30 | 🟧 OPEN | Owner-target restore drill |
| 31 | 🟧 OPEN | Off-host encrypted artifact and separate key custody |
| 34 | 🟧 OPEN | Actual host volume, restart and disk-pressure evidence |
| 35 | 🟧 OPEN | Owner-host HTTPS and certificate validation |
| 36 | 🟧 OPEN | Public WSS, browser/Android, platform lifetime and cross-instance acceptance |
| 38 | 🟧 OPEN | Protected host collector/dashboard and retention |
| 39 | 🟧 OPEN | Responsible adult operator, escalation and observed recovery drill |

Gate 10 remains **10/10 ORANGE; 0/10 formally closed**. ZERO COST is mandatory. No paid provider, hosting, deployment, billing activation or security weakening was used.

## 6. Indicator progress — unchanged

| Indicator | Status | Verified foundation | Remaining work |
|---|---|---|---|
| SMA 20 | 🟨 | Rolling mean; first valid index 19 | Overlay, toggle, legend/value, stale clearing and render tests |
| EMA 20 | 🟨 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/value, stale clearing and render tests |
| RSI 14 Wilder | 🟨 | Wilder smoothing; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend and render tests |
| MACD 12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Dedicated pane, lines, histogram, zero guide and render tests |
| Bollinger 20,2 | 🟨 | SMA20 ± 2 population standard deviations; first valid index 19 | Three-line overlay, toggle, legend/value and render tests |
| Shared indicator hook | 🟨 | Validated backend snapshot only; no DEMO fallback | Active chart binding, loading/error and cross-series isolation |
| Footprint | 🟧 | Deterministic educational accumulator; explicitly SIMULATED | Owner reference + reviewed blueprint; ON-only cluster layout |
| Heatmap | 🟥 | No implementation verified | Owner reference, blueprint, data/calculation contract and renderer |
| Liquidation Maps | 🟥 | No validated data/calculation contract | Source feasibility, reference, calculations and renderer |

No indicator percentage is fabricated. WebSocket work does not award indicator UI progress. Stage 4 remains parked while Stage 1 is active.

## 7. Project controls

- Stage 1: **30/40 criteria = 300/400 ticks = 75% provisional**.
- Gate 10: **10/10 🟧 ORANGE / 0/10 closed**.
- Stages 2–6: not scored.
- Overall project percentage: not established; M1–M8 weights unapproved.
- ZERO COST: existing Redis 7 CI service, local TCP proxy, temporary SQLite files only.
- Termux: not required for this cycle.
- No deployment, paid service, production activation or `main` modification.

## 8. Changed files

- `backend/tests/test_ohlcv_redis_consumer.py` — test-only TCP fault proxy and two-ASGI outage/recovery acceptance; no runtime source changes.
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md` — current dashboard refresh.
- `docs/INDICATOR_PROGRESS_LEDGER.md` — exact-head evidence boundary, indicator status unchanged.
- `docs/WORK_CYCLE_2026-11-20_BATCH62J31_DUAL_GATEWAY_TCP_AND_SNAPSHOT_ACCEPTANCE.md` — this report.
