# Batch 62J-213 implementation update — 24 November 2026

The implementation now uses an owner-pinned Ed25519 manifest signature. The signature binds source ID, generation ID, high-water cursor, retention floor, bar-retention policy, row count, format version, and canonical SHA-256 digest. Production gateway startup requires a non-empty trusted public-key map and rejects unsigned/unknown/invalid signatures before Redis construction. The immutable local receipt stores the verified source identity, key ID, signature envelope, digest, replica identity, cursor, retention floor, and bar-retention policy. Gateway startup re-verifies the persisted receipt signature before Redis construction.

Existing content-only receipts remain explicitly unauthenticated during additive schema migration. The source host private key is generated/protected outside Git and the container build context; only public keys are configured on gateways. CI uses ephemeral test keys and does not prove owner-host key custody or real snapshot transfer. Gate 25 remains OPEN until owner-host provisioning, real transfer, restart re-verification, remote receipt custody, and multi-gateway high-water acceptance are verified. Redis destructive retention remains blocked.

Detailed trust and key lifecycle: [GATE25_ED25519_SNAPSHOT_AUTHENTICATION.md](GATE25_ED25519_SNAPSHOT_AUTHENTICATION.md).

---

# ADR — Immutable WebSocket Snapshot Installation Receipt
Status: PROPOSED — design only; no runtime/schema change authorized by this ADR alone.
Date: 22 November 2026
Scope: Gate 25, gateway replica snapshot installation.
Cost constraint: ZERO COST; owner-operated storage and cryptographic trust material only, no paid hosted dependency.

## Context

The gateway snapshot installer returns source ID, generation ID, high-water cursor and SHA-256. Runtime validates the digest format and checks source/generation/cursor against the durable SQLite replica checkpoint before constructing the Redis client. The installation path re-reads and validates snapshot content during the transactional install.

**Superseded historical wording:** the mutable replica checkpoint DOES persist `snapshot_sha256` in the current branch. The current implementation binds the recomputed snapshot digest to the mutable checkpoint in the same SQLite transaction as snapshot installation, and runtime verifies callback metadata against that durable checkpoint before Redis client construction. What remains absent is a separate append-only immutable receipt per generation and authenticated owner-host custody/provenance. A digest proves content identity only when compared to a trusted digest; by itself it does not authenticate who supplied the snapshot.

## Decision direction

Keep the mutable replica checkpoint focused on current replication state. Add a separate immutable installation receipt record in a future, separately approved migration.

Proposed receipt fields:
- receipt schema/version;
- source ID and replica ID;
- snapshot generation ID;
- high-water cursor;
- canonical SHA-256 digest;
- row/bar count and manifest/schema version;
- authenticated source identity or key identifier;
- signature/attestation reference or verification result;
- installation timestamp and installer/runtime version.

The receipt must not contain bearer tokens, passwords, private keys, Firebase credentials or other secrets.

## Integrity, authenticity and idempotency

1. Verify the transfer authentication envelope and authoritative source identity before accepting installation metadata.
2. Recompute the canonical snapshot digest from the exact content being installed.
3. Persist the receipt in the same SQLite transaction as snapshot rows and checkpoint replacement.
4. Use a uniqueness rule for (source_id, replica_id, generation_id).
5. Reinstalling the same generation with the same digest is idempotent and must not rewrite historical provenance.
6. The same generation with a different digest is a hard conflict and fails closed.
7. A new generation creates a new receipt; previous receipts remain immutable for audit.
8. Digest comparison without a trusted signature/key or authenticated channel is not sufficient evidence of origin.

A practical trust model can use an owner-managed pinned public key to verify a signed source manifest, or an equivalent authenticated owner-controlled transfer protocol. Private signing keys remain outside the repository and outside client/mobile builds. Exact signature format and key-rotation policy require a separate threat-model decision.

## Migration and recovery

- Existing checkpoints without a receipt are classified as LEGACY_UNATTESTED; do not fabricate a digest or retroactively mark them authenticated.
- Migration is additive and idempotent.
- A failed install must roll back both data replacement and receipt insertion.
- Crash/restart tests must prove there is no state where new bars/checkpoint exist without the corresponding receipt, or a receipt exists for an uncommitted snapshot.
- Rollback must preserve legacy read compatibility and must never silently downgrade a verified receipt.
- Receipt retention/archival policy must be explicit; deletion is not automatic merely because the live cursor advances.

## Required acceptance tests before implementation is considered complete

- correct signed/authenticated snapshot accepted;
- wrong signer/key, invalid signature, altered bytes and digest mismatch rejected;
- same generation/same digest retry is idempotent;
- same generation/different digest rejected;
- source or replica identity mismatch rejected;
- transaction failure leaves prior snapshot, checkpoint and receipts unchanged;
- process termination at transaction boundaries followed by restart yields a consistent state;
- migration from legacy checkpoint succeeds without fabricated provenance;
- rollback and repeated migration are safe;
- receipt remains queryable after ordinary replica cursor advancement.

## Consequences

Positive: separates immutable installation provenance from mutable replication progress; supports restart-time audit and detects generation/digest conflicts.

Costs/risks: additive schema, migration and retention decisions; owner-managed key lifecycle; extra tests. No external service or paid infrastructure is required.

## Non-goals

This ADR does not close Gate 25, authenticate a real owner-host transfer, configure Redis TLS/AOF, prove Redis failover, or approve public WSS. It authorizes no code changes by itself.


## Batch 62J-135 source audit clarification (22 November 2026)

The following details were verified directly against the branch source and tests:

- `SQLiteOhlcvReplicaStore.install_global_snapshot()` performs preflight verification and then re-reads/validates the manifest and content while inserting the replacement snapshot under a write transaction. Snapshot replacement and checkpoint changes are atomic.
- At that audit checkpoint, the mutable replica checkpoint was described as not containing the snapshot digest. That statement is superseded by the Batch 62J-205 current-source correction below; do not use it as a description of the current branch.
- Publisher-side `_validate_snapshot_evidence()` requires a receipt per configured gateway and matches source, stream, generation, cursor and digest. The owner-host callback remains responsible for authenticating and retrieving those receipts; the validator itself does not contact remote gateways.

This confirms the design gap described above. Gate 25 remains OPEN. Do not treat digest syntax validation, transactional snapshot installation, or callback-supplied receipt validation as proof of durable gateway receipt custody. The implementation acceptance matrix and ordered migration plan are recorded in `WORK_CYCLE_2026-11-22_BATCH62J135_GATE25_SOURCE_AUDIT_IP3S.md`.

No implementation was performed; the ADR remains PROPOSED and design-only. The source-backed review does not authorize schema/runtime changes.


## Batch 62J-205 — current-source correction: digest is durable in the mutable checkpoint, receipt is still missing (24 November 2026)

The earlier Batch 62J-135 wording that the replica checkpoint does not contain a snapshot digest is superseded by the current source/test checkpoint `b71bf86c31fadd2895a2b4f18991b6742847e1a1`.

Verified source behavior in `backend/app/ohlcv_store.py`:
- `ohlcv_replica_checkpoint` has a nullable `snapshot_sha256` column; initialization adds the column to older databases when absent.
- `SQLiteOhlcvReplicaStore.install_global_snapshot()` validates the snapshot in a preflight pass, then re-reads and hashes the exact content while inserting the replacement bars under `BEGIN IMMEDIATE`.
- It validates manifest row count and digest against both the recomputed digest and preflight metadata.
- It writes the digest in the same transaction as the replica checkpoint replacement; `checkpoint()` and `load_snapshot()` expose that digest.
- `build_gateway_replica_runtime_factory()` compares installer metadata against the durable checkpoint digest before constructing the Redis client. The regression `test_gateway_runtime_rejects_callback_digest_not_bound_to_durable_checkpoint` proves a forged callback digest is rejected and no Redis client is created.

**Important distinction:** this is a digest bound to the current mutable checkpoint, not a separate immutable installation receipt. The checkpoint is updated when a newer snapshot generation is installed; it is not an append-only provenance history. The publisher-side callback still supplies the per-gateway receipt map, and the validator checks its fields but does not authenticate or retrieve remote receipts itself.

Therefore the ADR's original statement that no durable checkpoint digest exists is stale and corrected below. The remaining Gate 25 design gap is narrower but still material: authenticated owner-controlled receipt custody, immutable per-generation receipt persistence, signer/key provenance and crash-safe audit retention. Gate 25 remains OPEN; no schema or runtime migration is authorized by this clarification.
