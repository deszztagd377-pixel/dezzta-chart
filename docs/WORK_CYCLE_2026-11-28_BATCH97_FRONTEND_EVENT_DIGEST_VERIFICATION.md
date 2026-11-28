# Work Cycle 2026-11-28 — Batch 97: frontend OHLCV event digest verification

**Checkpoint date:** 28 November 2026  
**Validated source/test HEAD:** `e29040d4f3e9e5da5c9dd1400e102f5139b9ba41`  
**Branch:** `work/batch95-websocket-ack-protocol`  
**PR:** [#13](https://github.com/deszztagd377-pixel/dezzta-chart/pull/13), OPEN and unmerged  
**Base:** `phase-2/market-data-foundation`

## Implementation delivered

The frontend now recomputes the SHA-256 event digest before applying a digest-bearing OHLCV WebSocket update.

- Added a deterministic, synchronous SHA-256 verifier in `src/services/ohlcvStreamProtocol.ts`; no package or paid dependency was added.
- Canonicalization recursively sorts object keys, preserves array order, serializes the raw event with the digest field removed, encodes UTF-8, and compares the computed lowercase SHA-256 hex digest.
- `src/services/ohlcvWebSocketClient.ts` verifies the raw WebSocket frame before protocol parsing/normalization. This preserves fields such as the replay marker in the digest input.
- ACK-capable sessions fail closed if generation identity or digest is missing. A bad digest is rejected before the sequence guard, chart callback, cursor callback, or ACK queue can advance.
- Added protocol tests for valid digest verification, payload tampering, and replay-specific raw fields. Updated WebSocket ACK fixtures to use real digest values rather than placeholder strings.
- No backend ACK handler, durable receipt table, stable consumer identity, production ACK advertisement, deployment, or Cloudflare resource was added.

## Exact-head verification — all four required workflows terminal SUCCESS

Validated exact source/test HEAD: `e29040d4f3e9e5da5c9dd1400e102f5139b9ba41`.

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [46107071181](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071181) | SUCCESS — 41/41 steps |
| CodeQL Security Analysis | [46107071199](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071199) | SUCCESS |
| OCI ARM64 Image Readiness | [46107071235](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071235) | SUCCESS |
| Full Git History Secret Audit | [46107071288](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071288) | SUCCESS |

Automated Tests details:
- Frontend: 339/339 tests across 35 files.
- Backend: 1,437 passed, 1 skipped, 6 warnings.
- Cloudflare Durable Object runtime: 26/26 tests.
- Backend container build and smoke test passed, including shared Redis guard, persistent-volume/restart checks, SQLite integrity and rate-limit checks.
- Container image scan and report steps completed.
- The one skipped backend test explicitly reports that its isolated Redis TLS test fixture was not configured for that pytest test. The separate workflow step for Redis TLS CA/hostname enforcement completed successfully. Do not describe the skipped pytest case as executed.

An earlier exact-head attempt on `ea0353da9574c6600a1c76fe5e2b69f3c30c8b26` exposed two stale WebSocket ACK test fixtures with placeholder digests. Both fixtures were corrected using digests calculated from their exact payloads. The final exact-head run above passed. The earlier failure is retained here as diagnostic history, not as the current validation state.

## Protocol and security boundary

- Production live and replay events already receive server-side generation-scoped SHA-256 digests through the existing attestation helper.
- The frontend now verifies the raw event digest before applying the update.
- SHA-256 here is an integrity consistency check, not a digital signature and not proof of provider authenticity. A party able to rewrite both payload and digest can recompute it; authenticated transport, trusted server identity, and lawful provider provenance remain separate requirements.
- FastAPI still does not advertise `consumerAckProtocolVersion: 1` and still has no production ACK receive/validation plus durable receipt handler. Therefore the frontend does not activate production ACK.
- Stable reconnect consumer identity, durable receipt ownership/fencing, receipt persistence/reconciliation, and production restart semantics remain YELLOW / pending implementation and evidence.
- Public WSS/TLS and real browser/Android end-to-end acceptance remain YELLOW / pending owner-controlled deployment and device evidence.

## Stage and project control

- Official stage: Stage 1.
- Stage 1: **30/40 = 75% provisional**; no new Stage 1 tick is awarded by this change.
- Gate 10: **0/10 formally closed**.
- Remaining owner-controlled criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39** remain YELLOW pending real owner-host, Firebase, Redis, backup/key recovery, deployment, public WSS/device, monitoring, and incident evidence.
- Stage 2 remains preparatory and unauthorized until Stage 1 reaches 40/40 and the owner explicitly approves.
- PR #13 remains OPEN and unmerged. `main` is not changed.
- ZERO COST: no paid service, billing change, deployment, new Cloudflare resource, or new dependency.
- Deadline: 24 December 2026; 26 calendar days remained at this checkpoint.

## Next engineering sequence

1. Design and test stable consumer identity across reconnects without conflating multiple devices/tabs under one account.
2. Implement a durable receipt store with explicit owner identity, monotonic cursor/sequence, digest conflict detection, idempotency, fencing, restart reconciliation, and bounded retention.
3. Add FastAPI ACK receive/validation only after the receipt store and identity contract are testable.
4. Keep server capability advertisement disabled until backend and frontend contracts pass replay, duplicate, stale-owner, takeover, expiry, restart, and concurrent ACK tests.
5. Continue independent Stage 1 work in parallel: production secret/identity gates, Redis TLS/persistence/failover, backup/key recovery, deployment/WSS/device evidence, monitoring and incident drills.

No production ACK activation, public deployment, or Stage 1 gate closure is claimed by this work cycle.
