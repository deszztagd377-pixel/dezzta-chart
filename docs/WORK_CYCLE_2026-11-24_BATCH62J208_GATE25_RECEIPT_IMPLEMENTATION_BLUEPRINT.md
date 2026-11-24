# DEZZTA CHART — Batch 62J-208: Gate 25 Immutable Receipt Implementation Blueprint

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Code/test checkpoint:** `b71bf86c31fadd2895a2b4f18991b6742847e1a1`  
**Documentation predecessor:** `9de65685bcae78a8f244f0096dbff430a6f09f65`  
**Status:** DESIGN BLUEPRINT — pending owner review; no runtime/schema implementation in this batch  
**Cost:** ZERO COST

## 1. Verified baseline

The current source checkpoint has a nullable `snapshot_sha256` field in the mutable SQLite replica checkpoint. Snapshot installation recomputes the digest over the content being installed and persists it with the checkpoint under the installation transaction. Gateway runtime compares installer metadata with the durable checkpoint digest before Redis client construction.

This proves a digest is bound to the current mutable checkpoint. It does not establish append-only per-generation provenance, authenticate the source that supplied the snapshot, or prove durable owner-host custody of gateway receipts.

The ADR `ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md` remains PROPOSED. This document decomposes the design into reviewable implementation slices; it does not authorize schema or runtime changes.

## 2. Required invariants

1. **Atomicity:** snapshot rows, mutable checkpoint replacement, and immutable receipt insertion commit or roll back as one SQLite transaction.
2. **Append-only provenance:** a committed receipt is never rewritten when the replica advances to a newer generation.
3. **Identity binding:** receipt identity includes source, replica, generation, and the authoritative high-water cursor.
4. **Content binding:** the digest is recomputed from canonical snapshot content during installation; caller-provided digest alone is never trusted.
5. **Authenticity:** source identity must be established by an authenticated transport or a verifiable signature rooted in owner-controlled trust material. SHA-256 alone is not authentication.
6. **Idempotency:** same source/replica/generation plus same digest is a no-op success; the same identity with a different digest is a hard conflict.
7. **Legacy honesty:** pre-receipt checkpoints remain `LEGACY_UNATTESTED`; migration must not invent historical signatures or provenance.
8. **Fail closed:** invalid identity, digest, signature, cursor, or manifest rejects installation before Redis client construction.
9. **Secret hygiene:** private keys, bearer tokens, passwords, and provider credentials never enter receipts, fixtures, logs, or the repository.
10. **Zero-cost operation:** use SQLite and owner-managed cryptographic material already under user control; no paid hosted service or new recurring dependency.

## 3. Proposed receipt record

Review the following logical fields before migration design is finalized:

- receipt schema version;
- source ID and replica ID;
- generation ID and high-water cursor;
- canonical SHA-256 digest;
- manifest/schema version and row count;
- authenticated source identity and key identifier;
- signature/attestation bytes or a stable attestation reference;
- installation timestamp and installer version;
- verification state and legacy classification where applicable.

The unique identity is `(source_id, replica_id, generation_id)`. A separate immutable receipt table is preferred over overloading the mutable checkpoint row. Exact SQL types, signature envelope, canonical serialization, and key-rotation format remain review decisions.

## 4. Ordered implementation slices (after owner review)

**Slice A — contract and canonicalization**
- Define a versioned manifest schema and deterministic serialization.
- Specify exactly which manifest fields and snapshot rows participate in the digest.
- Reject duplicate, missing, out-of-order, or ambiguous records.
- Add pure tests for canonical byte stability and digest reproducibility.

**Slice B — trust boundary**
- Choose one explicit trust model: owner-pinned public key verifying a signed manifest, or an equivalently authenticated owner-controlled transfer channel.
- Define key identifier, trust-root provisioning, rotation, revocation, and recovery.
- Keep private signing material outside the repository and mobile artifacts.
- Reject unknown signer, invalid signature, wrong source/replica, and altered manifest.

**Slice C — additive SQLite migration**
- Add an immutable receipt table and uniqueness constraint.
- Preserve legacy checkpoint compatibility; classify old generations as unattested.
- Make migration repeatable and transactional.
- Do not rewrite existing receipts or fabricate provenance.

**Slice D — atomic installation**
- Verify identity/authenticity and canonical content before accepting metadata.
- Under one write transaction, install rows, replace the mutable checkpoint, and insert the immutable receipt.
- Roll back all three effects on any failure.
- Same-generation/same-digest retry is idempotent; same-generation/different-digest is rejected.

**Slice E — recovery and query**
- Expose read-only receipt lookup by source/replica/generation.
- Verify receipt-to-checkpoint consistency on startup/recovery.
- Preserve receipts across ordinary cursor advancement and backup/restore.
- Define explicit archival/retention; no automatic deletion tied to live cursor movement.

## 5. Required tests and failure injection

| Test | Expected result |
|---|---|
| Valid trusted manifest and matching content | Install + checkpoint + receipt commit |
| Unknown signer / invalid signature | Reject; no Redis client |
| Altered bytes / digest mismatch | Reject; no state mutation |
| Source or replica mismatch | Reject |
| Same generation and same digest | Idempotent success; receipt unchanged |
| Same generation and different digest | Hard conflict |
| Failure before transaction | Previous state preserved |
| Failure after row replacement but before receipt insert | Full rollback |
| Failure after receipt insert before commit | Full rollback |
| Process termination around commit boundary | Restart yields one consistent committed state |
| Legacy migration | Existing data retained and marked unattested |
| Repeated migration | No duplicate or rewritten receipt |
| Cursor advances to later generation | Earlier receipt remains queryable |
| Backup/restore | Receipt history and checkpoint remain consistent |
| Key rotation/revocation | Old receipt verification follows explicit versioned trust policy |

Tests must assert both database state and that Redis client construction does not occur on rejected installation.

## 6. Redis retention dependency

Redis Stream trimming remains prohibited until all of the following are implemented and independently accepted:
- durable gateway inventory and explicit retirement;
- authenticated per-gateway snapshot receipt custody;
- per-gateway floor acknowledgements tied to immutable receipt identity;
- pending-entry-list (PEL) recovery/retirement policy;
- dedicated retention identity with least privilege;
- crash-safe trim intent, commit, and reconciliation protocol;
- restart and multi-gateway failure-injection tests.

Do not add XTRIM, XDEL, or consumer-group destruction to runtime paths as part of Gate 25 receipt work.

## 7. Acceptance gates

Gate 25 remains OPEN until the receipt schema, trust model, migration, atomic installation, recovery, and all required tests are implemented and proven on the owner-controlled runtime. CI success alone cannot prove owner-host key custody or real transfer authentication.

This blueprint must receive owner review before any schema/runtime implementation. No source code, tests, dependencies, credentials, provider configuration, hosting, or deployment changed in Batch 62J-208.

## 8. Progress accounting

- Stage 1: 30/40 criteria = 300/400 ticks = 75% provisional; unchanged.
- Gate 10: 0/10 formally closed; unchanged.
- Gate 25: OPEN.
- Overall project: NOT SCORED.
- Aggregate indicator progress: NOT SCORED.
- `main`: untouched.
- Cost: ZERO COST.


## Batch 62J-213 — selected authentication trust model

The owner approved implementation based on this blueprint. The selected zero-cost trust model is Ed25519 signed snapshot manifests with an owner-pinned gateway public-key allow-list. The signature covers source ID, generation ID, high-water cursor, retention floor, bar-retention policy, row count, format version, and canonical SHA-256 digest. Source private keys remain on the authoritative source host with mode 0600; gateways receive only base64 raw public keys through `OHLCV_SNAPSHOT_TRUSTED_KEYS_JSON`.

Production gateway runtime now fails closed when the trust allow-list is absent or a snapshot is unsigned, signed by an unknown key, altered, or invalidly signed. The immutable receipt persists the signature envelope and the signed retention metadata, and gateway startup re-verifies that persisted signature before Redis client construction. Existing content-only receipts remain unauthenticated and are preserved as such by schema migration. Key rotation supports overlapping old/new public keys; a new signer must create a new snapshot generation rather than rewriting an existing immutable generation.

Implementation and operational configuration are documented in [GATE25_ED25519_SNAPSHOT_AUTHENTICATION.md](GATE25_ED25519_SNAPSHOT_AUTHENTICATION.md). Repository CI uses ephemeral keys only. Owner-host private-key custody, real signed transfer, remote receipt custody, multi-gateway high-water acknowledgements, and production WSS/Firebase/Android acceptance remain open. Redis destructive retention remains blocked.
