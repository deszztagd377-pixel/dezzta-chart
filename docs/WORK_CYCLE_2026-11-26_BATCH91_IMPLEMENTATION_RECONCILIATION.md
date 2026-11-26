# DEZZTA CHART — Batch 91 Implementation Reconciliation

**Date:** 26 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test SHA:** `2d0d7e9a2bf1190961126105d65f77d9926e6789`  
**Current branch HEAD at audit:** `6c610c4de75649126764e0aea200abf09b103521` (documentation-only commits after source/test SHA)  
**Result:** Batch 91 implementation and exact-source CI are substantially verified; formal batch acceptance remains pending owner review and explicit gate reconciliation.

## 1. Why this reconciliation exists

The existing `PROJECT_STATUS.md` had contradictory snapshots: its leading section described Batch 91 implementation, while the following "Latest design checkpoint" section still said no Batch 91 source files had changed and cited CI runs as in progress. The latter is stale. This work cycle supersedes that stale design-only snapshot using current branch contents, commit comparison and completed exact-head GitHub Actions evidence.

## 2. Change scope confirmed by branch comparison

Compared Batch 90 accepted source baseline `9a2f2b9faebdcaf1e97e93c6dfe85a2c93319fbb` to Batch 91 source/test SHA `2d0d7e9a2bf1190961126105d65f77d9926e6789`:
- 43 commits ahead, 0 behind.
- 17 changed files: 3 added, 14 modified.
- Added `cloudflare/proof/market-data-contract.mjs` and `src/types/marketDataProtocol.ts` plus tests.
- Updated synthetic Worker, Node/Miniflare/Durable Object runtime tests, frontend OHLCV snapshot/update protocol parsers and WebSocket client, and `PROJECT_STATUS.md`.
- No application `main` branch changes are included in this work cycle.

## 3. Exact-head CI — VERIFIED 4/4

All four required workflows completed successfully on exact source/test SHA `2d0d7e9...`:
- Automated Tests: run [45746150652](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45746150652) — SUCCESS.
- CodeQL: run [45746150693](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45746150693) — SUCCESS (JavaScript/TypeScript and Python jobs).
- Full Git History Secret Audit: run [45746150657](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45746150657) — SUCCESS.
- OCI ARM64 backend image readiness: run [45746150726](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45746150726) — SUCCESS.

Automated Tests log evidence:
- Frontend Vitest: 35 files / 331 tests passed.
- Synthetic Worker Node proof: 33/33 passed.
- Pinned local workerd/Miniflare test: 1/1 passed.
- Durable Object runtime suite: 15/15 passed.
- Backend pytest: 1,435 passed, 1 skipped, 6 warnings.
- Frontend Vite production build: successful (1,532 modules transformed; 2.35 seconds).
- Backend container smoke test passed, including its CI-local Redis TLS/ACL/AOF and persistent-volume checks.
- Additional bundle-secret scanner tests: 5/5; read-only Android preflight test: 1/1; release-publisher tests: 4/4.

These are CI-hosted tests and fixtures. They do not prove owner-device, public-host, public WSS, Android release-install, Firebase production auth, or live-provider acceptance.

## 4. Batch 91 contract implementation — source evidence

The source now includes:
- Provider-neutral provenance types and strict validators in `src/types/marketDataProtocol.ts`.
- Stable SHA-256 validation and canonical event/snapshot digest builders in `cloudflare/proof/market-data-contract.mjs`.
- Fixed-position JSON-array canonical digest input with domain separation and a stable test vector.
- Canonical synthetic OHLCV bar, snapshot and update envelopes with `generationId`, `cursor`, `highWaterCursor`, `retentionFloorCursor`, digest and explicit provenance.
- Exact-series REST snapshot metadata path.
- Status-first WebSocket auth, explicit subscribe, canonical snapshot/update messages and versioned pong response to literal text `ping`.
- Frontend parsing of additive durable metadata and strict event/series/bar consistency checks.
- A Durable Object-local operation queue serializing snapshot establishment with synthetic event acceptance/fan-out to close the previously identified snapshot/live ordering gap.

The synthetic proof remains explicitly synthetic-only: `providerConnected: false`, `dataStatus: synthetic_only`; it does not connect a live provider and must not be presented as live market data.

## 5. Explicitly NOT implemented — next dependent batches

Batch 91 does not provide the durable delivery system:
- Event payload + digest + high-water atomic persistence and bounded event-log replay are Batch 92.
- ACK validation, durable consumer receipts, receipt versions, RESUME and recovery after Durable Object eviction are Batch 93.
- Lawful, compatible, genuinely zero-cost provider proof is Batch 94.
- Public WSS, TLS/reverse-proxy and browser/Android lifecycle E2E are Batch 95.

Current synthetic subscription with a resume cursor responds with `resnapshot_required` because replay storage is not yet available. This is a deliberate boundary, not proof that replay is implemented. The schema migration currently creates logical event and receipt tables, but table existence alone does not mean event persistence/receipt behavior is complete.

## 6. Acceptance disposition

| Item | Disposition |
|---|---|
| Batch 91 source implementation | VERIFIED PRESENT at source/test SHA `2d0d7e9...` |
| Exact-head required CI | VERIFIED 4/4 SUCCESS |
| Contract tests and synthetic runtime checks | VERIFIED in CI |
| Synthetic-only provenance boundary | VERIFIED in source and tests |
| Public production API / provider connection | NOT IMPLEMENTED / NOT CLAIMED |
| Durable replay / ACK / receipt / RESUME | OUT OF SCOPE; Batch 92/93 |
| Owner review of final field set, digest encoding, route mapping and synthetic-only compatibility | OWNER REVIEW REQUIRED |
| Formal Batch 91 acceptance | NOT YET CLOSED |

**Decision:** Do not start Batch 92 runtime implementation until the owner review gate is explicitly closed and the project status is updated to record formal Batch 91 acceptance. Independent Batch 92 test design may proceed, but no runtime migration or event-log implementation may bypass that gate.

## 7. Cost and safety

No provider, broker/order endpoint, Firebase production identity, production secret, public WSS, Worker deployment, Cloudflare resource creation or paid service was added by this reconciliation. App `main` remains untouched. Zero-cost policy remains mandatory.
