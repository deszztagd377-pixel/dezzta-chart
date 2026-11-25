# DEZZTA CHART — Work Cycle 70: exact-HEAD CI closure and Gate 25 runtime-wiring audit

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Audited source HEAD: `f0c474fa25f973b1069bb0cef95b9b4fc7611127`  
Scope: exact-head CI result capture; source-to-gateway snapshot receipt contract; production app/container composition; durable high-water acknowledgement boundary.  
Cost: ZERO COST.

## 1. Exact-HEAD CI — terminal result

All four required workflows completed on the same exact HEAD `f0c474fa25f973b1069bb0cef95b9b4fc7611127`:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | 45594350798 | SUCCESS — 41/41 steps |
| CodeQL Security Analysis | 45594350653 | SUCCESS — Python 8/8; JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45594350605 | SUCCESS — 7/7 steps |
| Full Git History Secret Audit | 45594350685 | SUCCESS — 6/6 steps |

Backend pytest log: **1,426 passed, 1 skipped, 6 warnings in 63.89 seconds**. The single skip is a test-level skip; it is not owner-host acceptance. The Automated Tests job also completed the container smoke sequence: Redis ACL authentication and AOF data across restart, API fail-closed behavior during Redis outage and backend reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity and restart persistence, and HTTP rate-limit rejection. All 41 job steps, including cleanup, completed. No workflow remains running for this SHA.

This is repository/CI evidence only. It does not prove public WSS, owner-host deployment, Firebase production sign-in, Android lifecycle or market-data provider entitlement.

## 2. Gate 25 source contract — what is implemented

### Gateway side
`build_gateway_replica_runtime_factory()` requires an injected `snapshot_installer`. The callback must transfer/install the snapshot into the durable replica store. Before constructing Redis, the factory:
- reads the local immutable receipt using installer source/generation and the durable local replica ID;
- re-verifies persisted Ed25519 attestation against owner-pinned public keys;
- checks authenticated source and signer key binding;
- compares source, generation, high-water, digest, retention floor, bar-retention policy, schema and protocol against the durable checkpoint;
- rejects production content-only receipts.

### Source side
`build_source_publisher_runtime_factory()` requires an injected `snapshot_verifier`. Before constructing the publisher Redis client, it requires exactly one receipt for each configured gateway and validates:
- source and authenticated source binding;
- `OWNER_SIGNATURE_VERIFIED` state;
- non-empty unique durable replica IDs;
- valid signer key IDs, with one common key ID for the installed generation;
- exact stream key, snapshot generation, high-water cursor and canonical SHA-256 digest.

The validator explicitly documents that it cannot probe remote hosts. The owner-host callback must authenticate and retrieve the persisted receipts.

## 3. Critical composition finding — Gate 25 remains OPEN

The audited default application/container path does not supply those callbacks:

- `create_app()` accepts optional `replica_runtime_factory` and `publisher_runtime_factory` arguments.
- The module-level ASGI object is `app = create_app()` with neither factory supplied.
- `backend/Dockerfile` starts `uvicorn app.main:app`.
- `backend/fly.toml.example` contains service/environment configuration but no owner-host snapshot transfer or receipt retrieval implementation.

Therefore the factories and their fail-closed validation contracts exist, but the checked-in default container entrypoint does not wire a source publisher or gateway replica runtime. No remote authenticated owner-host callback or real snapshot transfer is established by CI. This is not repaired by setting a Redis URL or by the in-memory offline demand coordinator.

No synthetic callback, fake host receipt, or guessed network endpoint was introduced. Implementing the missing composition requires a real owner-controlled transport contract, endpoint identity/authentication, timeout/retry semantics, gateway inventory and owner-host key custody. It must be scoped and reviewed before runtime wiring.

## 4. High-water acknowledgement distinction

The gateway SQLite checkpoint persists `applied_cursor`; the Redis consumer performs durable local apply and fan-out before Redis `XACK`. These are useful local recovery guarantees.

They do not yet establish an authenticated, durable source-side per-gateway high-water acknowledgement ledger. Redis `XACK` only acknowledges a stream entry to its consumer group; it is not the separate owner-accepted retention-floor acknowledgement. Do not enable `XTRIM`, `XDEL`, or consumer-group destruction.

## 5. Provider-demand boundary

Batch 69 passed only for the explicitly named offline fixture. The coordinator is process-local and not wired to a live provider manager. The existing Redis connection quota and replica consumer ownership leases are not a multi-owner provider-series registry.

Still required before live provider demand:
- verified recurring-$0 entitlement and display/redistribution rights;
- exact provider SDK/API and version;
- dynamic subscribe/unsubscribe or documented reconnect semantics;
- provider-side acknowledgement/error contract;
- multi-process owner state, fenced reconciliation and restart recovery.

## 6. WebSocket gate matrix

| Gate / requirement | Status | Evidence boundary |
|---|---|---|
| Authenticated downstream WebSocket route | 🟩 Repo/CI verified | Exact identity, entitlement, ticket and route tests |
| Offline demand sharing/release/recovery | 🟩 Repo/CI verified | Batch 69 route/lifespan tests only |
| Redis ACL/AOF and container persistence smoke | 🟩 CI verified | Isolated CI containers, not owner-host |
| Signed snapshot and immutable local receipt | 🟩 Repo/CI verified | Ed25519, digest, checkpoint and receipt tests |
| Source/gateway factory receipt validation | 🟩 Repo/CI verified | Fail-closed injected callback contract |
| Default container source/gateway runtime composition | 🟥 OPEN | Factories not supplied by `app = create_app()` / Docker entrypoint |
| Owner-host authenticated snapshot transfer and receipt retrieval | 🟥 OPEN | No actual transport/custody evidence |
| Durable source-side per-gateway high-water ACK | 🟥 OPEN | No accepted remote ACK ledger |
| Cross-process provider demand and live provider ACK | 🟥 OPEN | No lawful pinned provider contract or coordinator |
| Gate 36 public WSS/TLS/Firebase E2E | 🟥 OPEN | No public owner-host endpoint/client evidence |
| Android process death/network handover/multi-instance | 🟥 OPEN | Real device acceptance absent |
| Destructive Redis retention | 🟧 BLOCKED | Independent retention prerequisites not met |

## 7. Indicator and project progress reconciliation

No indicator formula, calculation engine, shared hook, renderer, chart UI or indicator test changed. No indicator completion credit is awarded.

- SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook: 🟨 foundation only.
- Footprint PRO 2GD: 🟧 Stage 4 gated; two supplied visual references remain authoritative; offline accumulator is not exchange-native bid/ask.
- Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps: 🟥 open.
- Focused indicator declaration inventory remains 21 calculation + 7 shared-hook declarations; declaration count is not a pass count or completion percentage.
- Stage 1: 30/40 = 75% provisional inherited baseline 🟨.
- Stage 2: active, denominator not approved 🟦 NOT SCORED.
- Stage 3: ⬜ NOT SCORED.
- Stage 4: 🟪 GATED.
- Stage 5/6: ⬜ NOT SCORED.
- Gate 10: 0/10 formally closed 🟥.
- Overall project, aggregate indicator completion and significant progress/IP3S: ⚪ NOT SCORED.

## 8. Ordered next work

1. Define and review the owner-controlled source↔gateway transport and receipt retrieval contract; do not guess endpoints or trust client-supplied gateway identity.
2. Implement the owner-host composition only after transport/authentication/key-custody decisions are accepted; keep the default development app offline and fail closed.
3. Add durable per-gateway high-water ACK storage/retrieval with fencing, restart and stale-owner tests.
4. Prove real signed snapshot transfer and receipt re-verification after gateway restart.
5. Resolve recurring-$0 provider rights and exact dynamic provider ACK semantics before distributed provider demand.
6. Complete Gate 36 public HTTPS/WSS/TLS/Firebase acceptance and Android/browser lifecycle tests.
7. Keep Redis destructive retention blocked until all gateway floor acknowledgements and crash-safe reconciliation pass.
8. Keep major indicator UI behind Stage 4 and its scoped blueprint/user review.

ZERO COST maintained. `main` untouched. Vercel deployment deferred. No paid service, production credentials, fake provider, external feed or destructive Redis action. Planning target remains approximately 24 December 2026.
