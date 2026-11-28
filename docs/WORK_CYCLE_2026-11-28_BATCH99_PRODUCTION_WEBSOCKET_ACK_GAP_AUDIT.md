# Work Cycle 2026-11-28 — Batch 99: Production WebSocket ACK Gap Audit

**Audit date:** 28 November 2026  
**Deadline:** 24 December 2026 (26 calendar days remaining on audit date)  
**Policy:** ZERO COST; no deployment, billing change, paid service, resource creation, or `main` modification.  
**Audit scope:** read-only source, test, PR, and Actions inspection. No application code changed in this batch.

## 1. CI and branch state — verified

Application branch `phase-2/market-data-foundation` HEAD remains `2f3b2b58c1d76ac672f60a99de2e69fc309e7517`. Its source code is unchanged from the tested commit `41f42a232a25987513c175ea6d271ae5389b1437`; the two later commits add documentation only.

Four required workflows on source SHA `41f42a2` are terminal SUCCESS:
- [Automated Tests #2664](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46108286306)
- [Full Git History Secret Audit #1591](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46108286305)
- [OCI ARM64 Image Readiness #638](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46108286297)
- [CodeQL Security Analysis #2009](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46108286284)

PR [#13](https://github.com/deszztagd377-pixel/dezzta-chart/pull/13) remains OPEN and unmerged. Current head: `119d3b621ca6067d96a0b532c1a882620b8f5597`; validated source/test SHA: `e29040d4f3e9e5da5c9dd1400e102f5139b9ba41`. The five commits after the validated source/test SHA modify documentation only. Four required workflows on `e29040d` are terminal SUCCESS:
- [Automated Tests #2663](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071181)
- [CodeQL #2008](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071199)
- [OCI ARM64 #637](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071235)
- [Full Git History Secret Audit #1590](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071288)

The PR currently has two commits of base-branch updates not yet incorporated: `41f42a2` (volume-profile requirements documentation) and `2f3b2b5` (Batch 98 CI audit documentation). GitHub reports the PR and base as diverged, with the PR head 2 commits behind the base. This is a branch synchronization item; no mergeability conclusion is inferred from the connector's null mergeable field. The available GitHub connector does not expose the PR "Update branch" operation. Do not force-push, merge, or retarget automatically.

## 2. WebSocket implementation: synthetic proof vs production backend

### Verified synthetic Durable Object proof

The PR branch contains the synthetic Worker implementation for:
- v5 Durable Object schema with required-consumer owner token, fencing token, and lease expiry;
- lease registration, renewal, expiry, release, and fencing;
- ACK checks against current owner/fence/lease, delivered event sequence, and persisted digest;
- durable consumer receipt update;
- compaction guarded by unexpired consumer leases and durable receipt watermarks;
- tests in pinned workerd/Miniflare and Node runtime suites.

The latest exact source/test SHA `e29040d` passed all four required workflows. This is synthetic runtime evidence, not proof of public production deployment.

### Confirmed production integration gap

The production FastAPI WebSocket handler in `backend/app/main.py`:
- emits `market_data.status` without `consumerAckProtocolVersion`;
- accepts literal `ping` and the `auth.renew` control message;
- closes other JSON control messages as unsupported;
- contains no `market_data.ack` receive handler and no production durable consumer receipt commit.

The frontend client correctly gates ACK sending on the server advertising `consumerAckProtocolVersion: 1`. Therefore it does not send ACK to the current FastAPI backend. This is a safe fail-closed state, but it means production ACK/receipt/retention integration is **not complete**.

### Digest/generation clarification

The current PR source does include `attest_ohlcv_stream_event`:
- live events are attested in `backend/app/ohlcv_stream.py`;
- replay events are attested in `backend/app/main.py`.

An older section of `docs/ADR_BATCH95_CONSUMER_LEASE_LIFECYCLE.md` states that FastAPI update envelopes lack generation/digest. That statement is stale relative to Batch 97. The current confirmed gap is ACK capability advertisement, ACK receive/validation, and durable receipt integration—not absence of event digest generation.

SHA-256 digest recomputation detects payload inconsistency/tampering relative to the transmitted digest, but it is not a digital signature and does not independently authenticate the event producer.

## 3. Next engineering sequence

1. Define a production ACK contract shared by FastAPI and frontend: protocol capability, connection/consumer identity, stream generation, delivered sequence, event digest, idempotent duplicate ACK, regression rejection, and stable rejection codes.
2. Design durable receipt persistence against the existing SQLite outbox and retention floor. ACK must be committed atomically only after validating that the exact sequence was delivered on the current connection and that its digest matches the persisted event.
3. Bind receipt ownership to the already verified Firebase principal and a server-generated connection/session identity. Do not trust a client-supplied consumer ID or owner token.
4. Add backend tests for ACK-before-delivery, ACK-ahead, wrong generation, wrong digest, duplicate ACK, regression, stale session, revoked identity, reconnect/resnapshot, and concurrent ACK/compaction.
5. Keep the FastAPI status capability disabled until server receive/commit behavior and client tests pass together.
6. Re-run the four required workflows on the exact resulting source/test SHA. Only then consider enabling protocol v1 in a deployment candidate.
7. Separately synchronize PR #13 with its two base-only documentation commits, inspect the resulting diff for conflicts, and rerun CI if any source/test file changes. Do not merge PR #13 or change `main` without explicit owner approval.

## 4. Stage 1 acceptance — no score inflation

- Stage 1: **30/40 = 75% provisional**.
- Gate 10: **0/10 formally closed**.
- Remaining owner-controlled evidence criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 2 remains preparatory and unauthorized until Stage 1 is formally accepted at 40/40 and the owner explicitly approves.
- CI green means repository workflows passed on the specified SHAs. It does not close owner-host, Firebase, backup/key custody, public WSS/device, provider-rights, monitoring, or incident-drill evidence gates.

## 5. Status

- Required CI on the two audited source/test SHAs: **GREEN / terminal SUCCESS**.
- Synthetic Worker ACK and lease lifecycle: **GREEN at synthetic code/test level**.
- Production FastAPI ACK/receipt integration: **YELLOW / pending implementation and exact-head tests**.
- PR branch synchronization: **YELLOW / two base-only documentation commits pending incorporation**.
- Stage 1: **YELLOW / 75% provisional**.
- Zero-cost and no-main-change constraints: **maintained during this audit**.

This is a focused Batch 99 engineering audit, not the final consolidated project completion report. The final consolidated report is due only after Stage 1 acceptance evidence is complete.