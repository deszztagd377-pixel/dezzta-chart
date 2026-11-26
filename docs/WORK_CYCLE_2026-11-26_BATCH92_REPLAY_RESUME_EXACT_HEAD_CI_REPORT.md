# DEZZTA CHART — Batch 92 bounded replay, retention and WebSocket resume report

**Date:** 26 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Exact source/test SHA:** `17857c948cb932d5465eaca1e46dae15ce6c0344`  
**Documentation HEAD at report creation:** `970c092240f48a9ffd9fe35743fa8e0ba51dfe85`  
**Cost/deployment:** ZERO COST; synthetic-only proof; no production deployment or new paid resource.

## Implemented

1. `readDurableReplayPage` performs ordered, cursor-exclusive SQLite reads. Each replay response is bounded by 100 events and 65,536 UTF-8 bytes measured from the complete serialized response.
2. Replay pages carry generation ID, events, next cursor, high-water cursor, retention-floor cursor and `hasMore`.
3. Explicit outcomes cover invalid cursor, cursor ahead of high-water, generation mismatch, cursor below retention floor, corrupt persisted payload and replay event/response size violations.
4. `initializeDurableSeriesState` performs one-time legacy KV cursor bootstrap into SQLite. SQLite becomes authoritative after insertion; the bootstrap path does not dual-write.
5. WebSocket subscribe replays up to 10 pages in one `runProtocolExclusive` operation. The socket becomes eligible for live fan-out only after replay messages are queued, preventing an interleaving gap within the DO's serialization boundary. More than 10 pages falls back to a fresh snapshot rather than unbounded work.
6. `compactDurableEvents` atomically deletes events through a requested sequence and advances the retention floor in the same SQLite transaction.
7. The authenticated synthetic-proof test route `/__proof/compact` exposes compaction only in the proof-mode Worker; the Durable Object's internal compaction route is not forwarded as a public API.

## Exact-head CI — 4/4 terminal SUCCESS

All four required workflows completed successfully on the same source/test SHA `17857c948cb932d5465eaca1e46dae15ce6c0344`.

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45857181350](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45855836242) | SUCCESS |
| CodeQL Security Analysis | [45857181214](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45855836274) | SUCCESS |
| OCI ARM64 Image Readiness | [45857181270](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45855836304) | SUCCESS |
| Full Git History Secret Audit | [45857181213](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45855836341) | SUCCESS |

### Test/build evidence

- Worker Node proof: **38/38 passed**, including replay cursor states, corrupt payload/sequence gaps, 100-event pagination, the serialized UTF-8 byte ceiling, seeded legacy cursor bootstrap and interrupted-bootstrap retry.
- Miniflare pinned workerd integration: **1/1 passed**, exercising authentication, snapshot, live fan-out, persisted replay from cursor 50 to 51, replay envelope byte cap, atomic compaction deleting one event and advancing floor to 51, then expired-cursor resnapshot.
- Durable Object runtime suite: **18/18 passed**, including the updated explicit `retention_expired` contract.
- Frontend Vitest: **35 test files / 331 tests passed**.
- Backend pytest: **1,435 passed / 1 skipped / 6 warnings**. The skipped test is the optional Redis TLS integration test because the isolated fixture was not configured in this run.
- Frontend build and source/bundle credential scans passed.
- Backend container build, shared-Redis/persistent-volume smoke test and vulnerability scan passed.
- Native OCI ARM64 build and smoke test passed.
- Full reachable Git-history secret audit and both CodeQL language analyses passed.

## Corrections and transparency

An earlier CI attempt on predecessor SHA `efc25e8867e852a1d3f38902bbbed9e6bcfd2256` exposed one stale Durable Object assertion expecting the old generic replay-unavailable reason. The implementation correctly returned `retention_expired`; the assertion was updated. The subsequent exact-head run listed above passed. The earlier failed run is not counted as a pass. Further source/test batches added fail-closed missing-sequence detection, replay-page boundary tests, and seeded/interrupted legacy cursor bootstrap unit tests; all 38 Worker Node tests passed on the SHA recorded above.

## Remaining work — YELLOW, not GREEN

- Legacy bootstrap: add seeded-cursor and interrupted-bootstrap fault-injection tests.
- Replay: the 100-event and 65,536-byte bounds, cursor-ahead, generation mismatch, corrupt payload and missing-sequence detection now have Node coverage; additional real-SQLite boundary and injected-corruption cases remain.
- Replay/retention: add concurrent compaction/replay and rollback/failure injection; define an operational retention policy only after storage/quota measurements.
- WebSocket: add a deterministic replay-to-live race test and exercise multi-page replay plus the >10-page snapshot fallback.
- ACK/consumer receipts/RESUME protocol extensions remain queued behind these tests.
- Public WSS, Android E2E, production identity/provider integration and deployment remain out of scope and not accepted.

## Guardrails

- `main` was not targeted by these commits.
- No live provider, broker/order endpoint, Firebase production auth, Cloudflare production deployment, paid hosting, paid monitoring or paid storage was enabled.
- Synthetic proof output remains explicitly synthetic and must not be presented as exchange market data.
- Target remains around **24 December 2026**; no completion percentage is inferred from this slice.
