# ADR — Immutable WebSocket Snapshot Installation Receipt
Status: PROPOSED — design only; no runtime/schema change authorized by this ADR alone.
Date: 22 November 2026
Scope: Gate 25, gateway replica snapshot installation.
Cost constraint: ZERO COST; owner-operated storage and cryptographic trust material only, no paid hosted dependency.

## Context

The gateway snapshot installer returns source ID, generation ID, high-water cursor and SHA-256. Runtime validates the digest format and checks source/generation/cursor against the durable SQLite replica checkpoint before constructing the Redis client. The installation path re-reads and validates snapshot content during the transactional install.

The mutable replica checkpoint records the current replication position and metadata, but does not persist the snapshot SHA-256. The returned digest is propagated as runtime evidence and is not anchored to a durable immutable installation record. A digest proves content identity only when compared to a trusted digest; by itself it does not authenticate who supplied the snapshot.

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
