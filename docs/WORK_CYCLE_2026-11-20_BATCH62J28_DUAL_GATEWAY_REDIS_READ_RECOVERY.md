# Batch 62J-28 — Dual-ASGI transient Redis read recovery

**Date:** 20 November 2026  
**Branch:** phase-2/market-data-foundation  
**Code/test HEAD:** ea19ce5ae6623ac09b23d36069960a5368dab3b0  
**Scope:** strengthen WebSocket failure/recovery acceptance at the two-independent-ASGI-process boundary.

## Exact-head CI

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44704944924](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44704944924) | SUCCESS |
| CodeQL Security Analysis | [44704944956](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44704944956) | SUCCESS |
| Full Git History Secret Audit | [44704944887](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44704944887) | SUCCESS |

Backend pytest: **1,164 passed in 40.74 seconds**.

## Changes

Changed backend/tests/test_ohlcv_redis_consumer.py.

- Added a test-only Redis client wrapper that injects one ConnectionError on xreadgroup for each independently spawned ASGI gateway process.
- Each gateway writes a unique Redis marker when the transient read failure is triggered.
- Each wrapper writes a separate recovery marker after a subsequent successful Redis read.
- The parent test waits for both trigger and recovery markers before asserting WebSocket connection status.
- The existing process-level flow then verifies dual-client broadcast at cursor 1, replay reconnect, gateway process restart with the same durable SQLite replica, next live cursor 2, and parity of both replica checkpoints.

The test's recovery markers are initialized before process startup so failure paths can always clean up safely.

## Existing generation evidence rechecked

The same passing backend suite includes test_real_redis_group_reset_starts_after_installed_snapshot_watermark:

1. The consumer first applies cursor 1.
2. Cursor 2 is deliberately left pending in the old group.
3. A new verified global snapshot is installed at cursor 2.
4. The consumer switches to a new snapshot-generation-scoped group.
5. The old group's pending entry remains isolated; the runtime does not destroy the old group.
6. The new group starts after the installed snapshot watermark and applies cursor 3.

This is a real-Redis single-replica generation-reset test, not a two-gateway coordinated snapshot-replacement drill.

## Evidence classification

**Verified in CI:** two separate ASGI processes independently encounter a transient Redis client read error, recover, broadcast the same cursor, retain replay behavior, and converge after one gateway restarts.

**Not verified:** a real Redis server/network outage, coordinated two-gateway snapshot-generation replacement, production snapshot transport/rotation, production TLS/ACL/credential rotation, or public WSS browser/Android acceptance.

The fault injection is deliberately described as a transient read failure at the client boundary. It must not be represented as a Redis service shutdown or network-partition test.

## Worker documentation correction

The module-level description in backend/app/ohlcv_redis_worker.py was stale: it said the worker was not wired into FastAPI startup. The current branch has an explicit opt-in FastAPI replica lifespan that hydrates the verified snapshot, constructs the event-loop dispatcher, verifies consumer-group readiness, and starts the managed worker. The docstring was corrected to describe that existing lifecycle. No runtime behavior changed.

## Project controls

- WebSocket A–D: implemented and repository/CI-verified for the explicit opt-in path.
- WebSocket E: **PARTIALLY VERIFIED**. The dual-ASGI transient read-failure case is now covered; real service/network outage and coordinated snapshot replacement remain outstanding.
- Stage 1: **30/40 = 75% provisional**, unchanged.
- Gate 10: **10 ORANGE / 0 closed**, unchanged.
- Stages 2–6: not scored. Overall percentage: not established.
- Indicator progress: unchanged; no indicator UI implementation.
- ZERO COST maintained. No deployment, paid infrastructure, production activation, main-branch modification, or Termux action.

## Changed files in the evidence/documentation follow-up

- backend/app/ohlcv_redis_worker.py — module docstring accuracy only; no behavior change.
- docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md — current dashboard checkpoint and E evidence boundary.
- docs/INDICATOR_PROGRESS_LEDGER.md — transport evidence note; indicator statuses unchanged.
- docs/WORK_CYCLE_2026-11-20_BATCH62J28_DUAL_GATEWAY_REDIS_READ_RECOVERY.md — this report.
