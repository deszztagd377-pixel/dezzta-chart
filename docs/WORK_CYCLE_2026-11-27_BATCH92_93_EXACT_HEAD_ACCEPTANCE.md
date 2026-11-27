# DEZZTA CHART — Batch 92/93 Exact-Head Acceptance Checkpoint

**Date:** 27 November 2026  
**Branch:** `test/batch93-compaction-rollback`  
**Verified source/test commit:** `a86b515b55b2a754c07c74516212e580f6dc9eb2`  
**Scope:** isolated synthetic Cloudflare Worker + SQLite Durable Object proof only  
**Cost boundary:** ZERO COST; no production deployment or paid service.

## 1. Exact-head CI evidence

Both GitHub Actions runs on the exact source/test commit completed successfully:

| Trigger | Run | Result |
|---|---:|---|
| push | [45932912210](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45932912210) | SUCCESS; 41/41 steps |
| pull_request | [45932917674](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45932917674) | SUCCESS; 41/41 steps |

Verified test output from the completed jobs:
- Miniflare/workerd integration: 1/1 passed. It exercises the real Worker WebSocket path, Durable Object SQLite storage, fan-out, reconnect/replay race, ACK idempotency, ACK regression and digest mismatch.
- Cloudflare Durable Object Vitest suite: 22/22 passed.
- Frontend Vitest suite: 35/35 files and 332/332 tests passed.
- The job completed the frontend build and remaining configured CI steps successfully.
- No active Actions run remained at the end of the audit.

The two runs are duplicate push and pull-request triggers on the same commit, not two independent source revisions.

## 2. Implemented and tested in this bounded proof

- Additive SQLite schema/migrations for durable series state, event payloads/digests, consumer receipts and immutable series identity.
- Atomic event payload + digest + high-water persistence.
- Contiguous sequence enforcement, duplicate idempotency and conflicting/skipped sequence rejection.
- Bounded replay with retention-floor handling and pagination.
- Replay/compaction race behavior: replay returns a complete retained page or an explicit expired result; it does not silently return a partial page.
- Compaction transaction rollback when retention-floor advancement fails.
- Monotonic per-consumer receipt updates, duplicate ACK idempotency, regression rejection, generation checks and event-digest verification.
- Consumer receipt row isolation in the Durable Object storage layer.
- Real workerd integration for the synthetic WebSocket, durable storage, fan-out and reconnect/replay race.
- Existing hibernation/socket-attachment restoration and authentication timeout tests remain in the runtime suite.

## 3. Explicit acceptance boundary — not production-ready

The consumer receipt test proves storage isolation when distinct consumer IDs are supplied. It does **not** prove that a production authenticated principal is cryptographically or server-side bound to that consumer ID.

The synthetic proof currently uses a fixed synthetic subject and a shared proof token; the ACK proof request supplies `consumerId`. This is intentionally not Firebase production identity. Do not wire this proof token or synthetic identity into the production frontend.

The following remain unaccepted:
- Production Firebase ID-token verification and mapping to a stable server-derived consumer principal.
- Production source/gateway runtime composition and owner-pinned signed snapshot installation.
- Owner-accepted per-gateway durable high-water receipt and restart reconciliation.
- Lawful zero-cost live provider acceptance.
- Public Cloudflare WSS deployment, browser/Android end-to-end reconnect, network handover and process-death acceptance.
- Owner-host backup/restore, monitoring and incident drill.

No live provider, broker/order execution, production secret, Cloudflare resource, public endpoint or deployment was enabled by this work.

## 4. Official project accounting — unchanged

The official six-stage roadmap remains authoritative:
- Stage 1 — Foundation, Security & Data Integrity: **30/40 criteria (75% provisional)**.
- Gate 10: **0/10 formally closed**; open criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.
- Stage 2: preparatory only; no official stage transition.
- Stage 3: not scored.
- Stage 4: gated.
- Stages 5–6: not scored.
- Overall project/IP3S: not scored; no approved weighted denominator.

Batch 92/93 proof results do not automatically close any of the ten external Gate 10 criteria and do not advance the official stage.

## 5. Next dependency order

1. Close the production identity boundary: verify Firebase ID tokens server-side, derive a stable principal, bind tickets/ACK receipts to that principal, and test cross-user spoofing/revocation.
2. Complete source and gateway runtime factories only with authoritative snapshot verifier/installer callbacks and owner-pinned keys; keep source/gateway roles mutually exclusive.
3. Prove two independent gateways, restart/fencing and durable owner-accepted high-water receipts before any destructive Redis retention.
4. Complete the zero-cost/legal provider gate before provider mode can be enabled.
5. Only after explicit deployment authorization, validate the existing Cloudflare route and public WSS with browser and Android E2E.
6. Complete owner-host recovery/monitoring acceptance.

**Controls:** `main` remains untouched. This checkpoint is documentation-only and does not claim production deployment. Target planning date remains approximately 24 December 2026.
