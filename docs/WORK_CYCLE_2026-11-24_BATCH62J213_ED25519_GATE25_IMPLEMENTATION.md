# DEZZTA CHART — Batch 62J-213: Ed25519 Snapshot Authentication

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Base HEAD:** `46a00a3ee53b6b6db365acd41e9321b12b6c3a06`  
**Cost:** ZERO COST  
**Vercel deployment:** explicitly deferred.

## Implemented in this batch

- Added canonical Ed25519 attestation payload/sign/verify helpers.
- Snapshot signature binds source ID, generation ID, high-water cursor, retention floor, bar-retention policy, row count, format version, and SHA-256 digest.
- Snapshot export supports an owner-held Ed25519 private key and stable key ID.
- Snapshot verification supports an owner-pinned public-key allow-list and fail-closed authentication mode.
- Production gateway construction now requires a valid trusted public-key map.
- Production replica snapshot installation rejects unsigned, unknown-key, altered, or invalidly signed snapshots before Redis client construction.
- Immutable receipts persist verification state, authenticated source ID, key ID, signature envelope, retention floor, and bar-retention policy.
- Gateway startup re-verifies the persisted receipt signature before Redis construction.
- Existing content-only receipt rows are migrated without fabricating authentication evidence.
- Added owner-only key loader and a keypair generation script that writes the private PEM with mode 0600, refuses overwrite, and refuses output inside the repository.
- Updated backend environment example and README with source-host/gateway-host configuration and key rotation guidance.
- No new dependency: `cryptography>=50,<51` was already present in backend requirements.

## Test coverage added

- Ed25519 canonical payload determinism and sign/verify round-trip.
- Tampered metadata and unknown signer rejection.
- Invalid key ID and malformed public key rejection.
- Signed snapshot verification and authenticated immutable receipt persistence.
- Unsigned snapshot rejection in authenticated mode.
- Existing content-only receipt migration preservation.
- Source key loading, owner-only permissions, and paired environment configuration.
- Production gateway missing-key fail-closed behavior.
- Production gateway unsigned/invalid-signature rejection before Redis construction.
- Persisted receipt signature re-verification before Redis construction.
- Public-key allow-list environment parsing.
- Existing content-only receipt idempotency, digest conflict, immutability, and transaction rollback tests remain in place.

Exact-head CI is pending for this batch and must be polled to completion before the commit receives acceptance credit.

## Security boundary

The code now provides an explicit cryptographic trust model, but no production private key or public allow-list has been provisioned. CI uses ephemeral test keys only. Gate 25 remains OPEN until the owner source host holds the private key, every required gateway receives the matching public key, and a real signed transfer plus restart re-verification is accepted.

The signature authenticates the source snapshot manifest and its content digest. It does not itself prove owner-host WSS/TLS availability, Firebase E2E, remote gateway receipt custody, or multi-gateway high-water acknowledgements.

Redis `XTRIM`, `XDEL`, and consumer-group destruction remain blocked. No secrets or generated keypairs are committed. No paid service or deployment is added. `main` remains untouched.

## Progress accounting

- Gate 25: cryptographic code path and CI tests added; external owner-host provisioning/acceptance remains OPEN.
- Receipt immutability and atomicity: implemented; exact-head CI pending.
- WebSocket WSS/Firebase/Android/monitoring acceptance: remains separately open.
- Indicator source: unchanged; detailed indicator ledger remains in Batch 62J-212.
- Stage 1: 30/40 = 75% provisional; not re-audited.
- Stage 2: active; no aggregate percentage.
- Aggregate indicators: NOT SCORED.
- Overall project: NOT SCORED.
- Target delivery planning remains around 24 December 2026.
