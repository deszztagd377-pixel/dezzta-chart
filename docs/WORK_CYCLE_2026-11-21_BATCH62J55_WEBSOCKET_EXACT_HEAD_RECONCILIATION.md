# Batch 62J-55 — WebSocket exact-head integration reconciliation

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Documentation branch HEAD before this batch:** `290c4fe1b4a125e9a41b410d942e807db22c58aa`  
**Latest runtime/source-test checkpoint:** `56317eff2b71886040acb998bf692814622feedf`  
**Scope:** read-only source/test/CI reconciliation plus documentation correction. No runtime source, dependency, schema, infrastructure, secret, or deployment changes.

## 1. Exact-head CI evidence

The documentation HEAD `290c4fe1b4a125e9a41b410d942e807db22c58aa` has four completed successful check runs:

- Test and Build: [run 44848265832](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44848265832) — frontend 245/245 tests across 29 files; backend 1,218 passed, 6 warnings in 45.41 seconds.
- CodeQL JavaScript/TypeScript: [run 44848265780](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44848265780) — success.
- CodeQL Python: [run 44848265780](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44848265780) — success.
- Full reachable Git-history secret scan: [run 44848265805](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44848265805) — success.

The Test and Build job also completed frontend dependency audit (0 vulnerabilities), frontend source/bundle secret checks, backend dependency audit (no known vulnerabilities), backend container build, Redis ACL/AOF + persistent-volume smoke test, container scan/report export, and bounded synthetic outbox benchmark. These are CI/source claims only; they do not prove production WSS or owner-host infrastructure.

## 2. Current WebSocket code facts

Inspected at runtime/source-test checkpoint `56317eff2b71886040acb998bf692814622feedf`:

- `backend/app/main.py` has an opt-in `replica_runtime_factory` path in FastAPI lifespan. It validates the replica store, Redis client, stream key, consumer/store/client identity, and generation-scoped group before worker startup.
- Lifespan acquires the Redis consumer ownership lease before group initialization, creates an event-loop callback dispatcher, starts `RedisOhlcvGatewayWorker`, and exposes replica runtime state to the app.
- Shutdown stops the worker with a bounded deadline and releases the lease only after confirmed worker termination. A timed-out worker is not falsely reported as stopped; the Redis client/lease are not casually discarded.
- `/ws/market-data` selects `subscribe_replica_snapshot` when a replica store is configured. The replica snapshot is read with its checkpoint boundary; replica replay is bounded and exact-series scoped through the Redis stream. Without an injected replica runtime, the existing source-store path remains the default.
- The consumer enforces apply-before-ACK, pending-entry recovery, generation-scoped groups, and ownership checks. Worker transient failures retry with bounded backoff; resnapshot-required is terminal until a verified snapshot is rebuilt.
- Relevant source files: `backend/app/main.py`, `backend/app/ohlcv_redis_worker.py`, `backend/app/ohlcv_redis_consumer.py`, `backend/app/ohlcv_redis_lease.py`, `backend/app/ohlcv_replica_bridge.py`, and `backend/app/ohlcv_redis_replay.py`.

This corrects older statements in the Batch 62J-19 blueprint that said FastAPI lifespan did not own the worker and that the WebSocket route was always source-store-backed. Those statements describe an earlier architecture snapshot and are superseded by the inspected code state.

## 3. Remaining WebSocket blockers — do not mislabel as fixed

1. **No full two-ASGI end-to-end acceptance harness is present in the inspected backend test inventory.** Existing Redis lease/consumer/worker/replica-bridge tests validate components, but they do not establish that two independent FastAPI server processes both receive the same live event sequence through separate replica databases and WebSocket clients.
2. **Snapshot bootstrap/transport is not an approved complete deployment contract.** A consumer requires a verified installed snapshot and generation. The runtime factory is injected; this audit did not find owner-approved snapshot distribution, installation orchestration, and source identity proof for the intended real topology.
3. **Real topology and operations remain external:** independent production Redis TLS/ACL/networking/failover, per-instance durable replica paths, owner-controlled process supervision, public HTTPS/WSS, browser and Android WebView reconnect/freshness tests, and real provider delivery.
4. **Production route remains opt-in.** Do not enable replica mode by guessing configuration or sharing a SQLite WAL database across hosts. Do not add a paid service or deploy to manufacture evidence.

## 4. Next safe implementation order

1. Add a CI-only two-ASGI process harness using the existing Redis 7 service, separate temporary SQLite replica files, independent consumer groups, and test-only configuration.
2. Prove identical snapshot watermark, ordered event IDs/cursors on both WebSocket clients, exactly-once replay/live boundary handoff, and checkpoint convergence.
3. Exercise gateway restart, consumer restart, Redis interruption/recovery, stale generation, retention gap, and one-replica lease contention.
4. Keep production replica mode disabled until snapshot transport/topology is explicitly approved and owner-host security/availability evidence exists.
5. Only after the automated harness is green, resume the external Gate 25/36 acceptance sequence. Do not claim Gate 10 closure from CI alone.

## 5. Indicator and project accounting

No indicator source, calculation, hook, chart renderer, or indicator test was changed. No indicator progress is awarded.

| Indicator | Status | Evidence boundary |
|---|---|---|
| SMA 20 | 🟨 Foundation | Calculation/tests exist; visible overlay and controls remain |
| EMA 20 | 🟨 Foundation | Calculation/tests exist; visible overlay and controls remain |
| RSI 14 | 🟨 Foundation | Wilder calculation exists; dedicated pane and guides remain |
| MACD 12/26/9 | 🟨 Foundation | Calculation exists; dedicated pane/line/histogram remain |
| Bollinger 20,2 | 🟨 Foundation | Calculation exists; visible three-line overlay remains |
| Shared indicator hook | 🟨 Foundation | Validated snapshot hook exists; visible controls/lifecycle integration remain |
| Footprint | 🟧 Gated | Simulated educational aggregation only; visual work waits for user's reference image and reviewed blueprint |
| Heatmap | 🟥 Not implemented | Wait for user's reference image and reviewed blueprint |
| Liquidation Maps | 🟥 Not implemented | Source/data contract and implementation not established |

- Gate 10: 0/10 formally closed; gates 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 remain open.
- Stage 1: 30/40 = 75% provisional; no acceptance tick awarded.
- Stages 2–6: not scored.
- Overall project percentage and aggregate indicator percentage: not established; no approved denominator/weights.
- ZERO COST. No Termux/device command required for this repository-only audit. No Vercel/Cloudflare action, deployment, production credential access, or `main` modification.

## 6. Result

The previously identified repository-level Redis consumer ownership defect has CI-verified coverage. FastAPI lifespan and replica-backed snapshot/replay integration are present behind opt-in runtime injection. The unresolved technical task is the real two-ASGI-process WebSocket proof plus an approved snapshot bootstrap topology—not another isolated Redis lease patch. This batch is a documentation/source reconciliation only; it awards no Gate 10 or indicator completion credit.
