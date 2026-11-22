# Batch 62J-138 — Gate 25 executable acceptance sequence and negative-test boundaries
Date: 22 November 2026
Audited parent: `9270daa2e82437f74ccf9ed16dce27f4f969d359`
Branch: `phase-2/market-data-foundation`
Scope: source-backed acceptance sequencing and test design. Documentation only; no runtime/schema/test code changed.

## Exact-parent CI

- Automated Tests run [44992826757](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992826757): IN PROGRESS at the time of this audit.
- CodeQL run [44992826808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992826808): SUCCESS for JavaScript/TypeScript and Python.
- Full Git History Secret Audit run [44992826751](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992826751): SUCCESS.

Do not describe the parent as fully green until Automated Tests completes. These are checks on the audited parent, not on this new documentation commit.

## Source-level behavior and test coverage

Files reviewed:
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/ohlcv_redis_runtime.py`
- `backend/app/ohlcv_store.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`
- `backend/tests/test_ohlcv_redis_runtime.py`

### Gateway factory

The gateway factory calls the owner-provided `snapshot_installer(replica_store)`, requires `status == "installed"`, then reads the durable replica checkpoint. It compares callback source ID, generation and high-water cursor with checkpoint source/generation/applied cursor. It validates the callback SHA-256 as 64 lowercase hexadecimal characters, but has no persisted receipt digest to compare it with. Redis client construction happens only after those checks.

Existing tests cover successful snapshot setup, wrong configured source, missing checkpoint, opt-in environment behavior, TLS configuration, and client cleanup on consumer-construction failure. They do not yet exercise an installer that returns a syntactically valid but incorrect digest while the checkpoint's source/generation/cursor are correct. This is not evidence of an unauthenticated remote exploit: the installer is explicitly an owner-trusted callback. It is an acceptance gap in independently binding runtime evidence to durable receipt state.

### Publisher factory

The publisher calls `snapshot_verifier(source_store, state)`, then validates source, stream, generation, publisher cursor, digest syntax, unique required gateway IDs and one matching mapping per gateway. It checks gateway mapping source/stream/generation/cursor/digest equality. The callback contract is responsible for authenticating and reading actual gateway receipts. Existing tests cover mismatched gateway cursor/digest, malformed manifest digest, missing checkpoint and valid envelope. They use synthetic callback evidence and do not prove callback authentication, durable remote receipt lookup, identity binding or key revocation.

### Replica installer

`install_global_snapshot()` verifies the artifact before installation, acquires an immediate SQLite transaction, checks source binding and cursor rollback, rereads/revalidates snapshot header/content during installation, replaces bars and upserts the mutable checkpoint, then commits. The checkpoint currently stores generation and cursor but not the installed digest/immutable receipt. It does not enforce same-generation/same-digest idempotency or same-generation/conflicting-digest rejection as a durable invariant.

## Acceptance sequence — execution order

**A. Local SQLite migration contract**
1. Create a pre-receipt database fixture containing identity, checkpoint, bars and applied-event rows.
2. Open it through the current store initialization path.
3. Assert all existing rows and values are preserved; classify checkpoint as LEGACY_UNATTESTED.
4. Reopen twice and assert migration idempotence.
5. Assert no historical receipt, digest, attestation key or installation timestamp is fabricated.

**B. Receipt transaction contract**
1. Install a fresh snapshot and assert bars, checkpoint and receipt become visible together.
2. Replay same source/replica/generation/digest/immutable manifest and assert original receipt ID and installed timestamp remain unchanged.
3. Replay same generation with different digest or conflicting immutable metadata; assert fail-closed and byte-for-byte equivalent logical state before/after.
4. Inject failures after bar replacement, checkpoint update and receipt insertion; assert full rollback.
5. Restart after pre-commit and post-commit interruption; assert old-complete or new-complete state, never mixed state.
6. Advance event cursor; assert installation receipt remains immutable and queryable.

**C. Gateway runtime binding**
1. Callback returns installed metadata; runtime reads durable receipt from the replica store.
2. Assert source, stable replica ID, generation, cursor, digest, row count and manifest version match the receipt.
3. Return a well-formed but incorrect callback digest; runtime must reject it against persisted receipt.
4. Return a receipt for another replica/source/generation/cursor; reject before Redis client construction.
5. Remove or corrupt receipt after callback; reject startup and close any already-created resource.
6. Restart gateway; evidence must be reconstructed from durable receipt, not callback memory.

**D. Publisher and owner-host boundary**
1. Verify required gateway inventory is unique and complete.
2. Authenticate each gateway identity and retrieve its receipt from authoritative durable storage.
3. Verify attestation signature/MAC under approved trust policy, key ID, validity, rotation and revocation state.
4. Reject missing, duplicate, stale, replayed, revoked-key, wrong-gateway, wrong-replica and mismatched-digest receipts.
5. Record auditable decision metadata without recording credentials or private key material.
6. Test owner-host restart, Redis restart, gateway restart, backup/restore and receipt retention independently.

## Decision gates before code

No authentication scheme, cryptographic algorithm, key custody, schema or generation progression rule is selected by this report. Owner approval is required for:
- whether the receipt is signed by source, gateway, or both;
- whether asymmetric signature or owner-controlled MAC is the trust primitive;
- key issuance, storage, rotation, revocation and recovery responsibilities;
- whether generation identity is unique per source or per source+replica;
- the exact cursor transition rule for a new generation;
- receipt archival/retention and restore semantics.

Never store private keys, shared secrets or credentials in SQLite receipts, logs, source control or test fixtures. Use test-only ephemeral keys only after the trust model is approved.

## Gate 25 closure evidence

Gate 25 cannot close until local transactional receipt tests pass AND owner-host evidence proves authenticated transfer, independently retrieved durable receipts, trusted key lifecycle, persistent storage/backup, restart/recovery, and audit/retention behavior. A CI pass or local SQLite test alone is insufficient.

## Indicator and project status

No indicator implementation changed. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic prototype/reference-gated; Heatmap and Liquidation Maps remain 🟥 not implemented. No implementation credit.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 remain NOT SCORED/not officially opened. Overall project remains NOT SCORED. Gate 10 remains 0/10 external criteria formally closed. WebSocket Gates 25, 36 and 38 remain OPEN.

IP3S Batch 62J-138 is PENDING exact-HEAD CI. Do not award numeric score until exact-HEAD checks finish. This report adds an executable ordered acceptance plan, not a runtime completion claim.

ZERO COST. No paid hosting/API/domain, deployment, external account, production credentials, device or Termux work. `main` untouched.
