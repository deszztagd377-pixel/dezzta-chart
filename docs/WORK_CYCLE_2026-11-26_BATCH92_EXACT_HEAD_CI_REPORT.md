# Batch 92 — Exact-head CI verification report

**Date:** 26 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Exact tested source/test SHA:** `0657efc142299753079823bb6d98aa12bdcf517f`  
**Result:** **4/4 required workflows terminal SUCCESS**

## Required workflows

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | 45851007304 | SUCCESS |
| CodeQL Security Analysis | 45851007316 | SUCCESS |
| Full Git History Secret Audit | 45851007271 | SUCCESS |
| OCI ARM64 Image Readiness | 45851007421 | SUCCESS |

## Verified test and build evidence

- Worker Node proof: 33/33 passed.
- Miniflare pinned workerd WebSocket, Durable Object storage and fan-out: 1/1 passed.
- Durable Object runtime: 18/18 passed. Includes schema v1→v3, an existing-v2 identity row upgrade, identity digest hydration, immutable identity triggers, snapshot-first identity registration, conflicting identity rejection, atomic event commit, retry/conflict, sequence and concurrency behavior, hibernation and alarm coverage.
- Frontend Vitest: 35 test files, 331 tests passed.
- Backend pytest: 1,435 passed, 1 skipped, 6 warnings. The skipped test is the optional Redis TLS integration test because the isolated fixture was not configured.
- Frontend build, backend container build, container smoke test and vulnerability scan: passed.
- Synthetic SQLite outbox and metrics collector benchmark steps completed; reports uploaded by CI.

## Migration compatibility

The earlier digest addition was placed into schema v2, which would not upgrade an already-created v2 database. It has been corrected to additive schema v3. The migration detects whether a digest column already exists, adds it only when absent, preserves legacy identity JSON, and allows a one-time SHA-256 digest hydration for legacy rows while continuing to reject identity changes. The runtime migration regression passed in the exact-head run above.

## Scope and limits

This CI run proves the tested code at the exact SHA above. It does not prove that all Batch 92 scope is complete. Durable replay queries, retention compaction, bounded replay pages, replay-to-live WebSocket handoff, ACK/consumer receipt processing, and full resume recovery remain open. A subscription carrying a cursor still receives an explicit resnapshot-required response because replay is not yet implemented.

No paid resource, new Cloudflare namespace, provider connection, production deployment, or `main` branch change was introduced by this batch.

## Links

- [Automated Tests](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45851007304)
- [CodeQL](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45851007316)
- [Full Git History Secret Audit](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45851007271)
- [OCI ARM64 Image Readiness](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45851007421)
- [Exact tested commit](https://github.com/deszztagd377-pixel/dezzta-chart/commit/0657efc142299753079823bb6d98aa12bdcf517f)
