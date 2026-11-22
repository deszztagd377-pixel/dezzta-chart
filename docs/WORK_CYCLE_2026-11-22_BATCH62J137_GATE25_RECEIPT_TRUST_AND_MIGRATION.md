# Batch 62J-137 — Gate 25 receipt trust-boundary and migration contract
Date: 22 November 2026
Audited parent: `26445cb6853bdce2ed6d2b19a08406ff735d9704`
Branch: `phase-2/market-data-foundation`
Scope: source/test audit and acceptance design. No runtime/schema/test changes.

## Exact-parent CI evidence

Parent commit checks:
- Automated Tests: IN PROGRESS at audit time (check run 137116797619; workflow run 44992604680).
- CodeQL JavaScript/TypeScript: SUCCESS (137116760152).
- CodeQL Python: SUCCESS (137116759817).
- Full Git History Secret Audit: not yet independently verified as completed on this parent at audit time.
Do not describe exact-parent CI as fully green.

## New source-backed findings

### 1. Gateway startup trusts callback metadata for digest evidence

`backend/app/ohlcv_redis_gateway_runtime.py`:
- Calls owner-supplied `snapshot_installer(replica_store)`.
- Requires callback result status `installed`.
- Reads durable `replica_store.checkpoint()`.
- Compares source ID, generation ID and cursor against that checkpoint.
- Validates the callback-returned digest only for lowercase SHA-256 shape.
- It does not compare that digest to a digest stored in the durable checkpoint, because no such field/receipt exists.

Therefore source/generation/cursor are bound to durable checkpoint state, while digest provenance remains dependent on the trusted callback and its authenticated transfer/install implementation. A well-formed digest string is not independent proof that the exact digest is durably recorded.

### 2. Publisher receipt verification is delegated to owner-host callback

`backend/app/ohlcv_redis_runtime.py`:
- `_validate_snapshot_evidence()` checks source, stream, generation, cursor, SHA-256 syntax and a one-to-one set of required gateway IDs to installation mappings.
- Each callback-provided gateway mapping must match the global snapshot source, stream, generation, cursor and digest.
- The function cannot independently query gateway hosts or authenticate their receipt stores.
- The callback is explicitly responsible for authenticating and reading authoritative installation receipts.

Acceptance consequence: unit tests prove envelope consistency and fail-closed behavior for malformed/mismatched evidence, not remote receipt authenticity, custody or non-repudiation. Owner-host acceptance must demonstrate callback authentication, gateway identity binding, receipt retrieval from durable storage, replay resistance, key rotation/revocation and audit logging.

### 3. Migration boundary is small but must preserve legacy semantics

`SQLiteOhlcvReplicaStore._initialize_replica_metadata()` currently creates:
- `ohlcv_replica_identity`
- `ohlcv_replica_checkpoint`
- `ohlcv_replica_applied_events`

The checkpoint table has a narrow compatibility ALTER for `bar_retention_json`. A receipt migration should be additive and transactional; it must not rebuild or reinterpret existing checkpoint rows. Existing rows without receipts must remain explicitly `LEGACY_UNATTESTED`, with no fabricated digest, timestamp, key ID or historical attestation.

## Receipt schema decision draft — pending owner approval

Recommended separate append-only table, not digest columns in the mutable checkpoint:

`ohlcv_replica_snapshot_receipts`
- `receipt_id`: stable random opaque ID, primary key
- `source_id`, `replica_id`, `generation_id`: non-null identity tuple
- `snapshot_sha256`: canonical lowercase 64-char SHA-256
- `high_water_cursor`, `retention_floor`: validated non-negative integers
- `row_count`: validated non-negative integer
- `snapshot_format_version`, `replica_schema_version`, `replica_protocol_version`: integers
- `attestation_scheme`, `attestation_key_id`: non-secret identifiers; nullable only for explicitly unauthenticated legacy state
- `authenticated_transfer_id`: opaque audit correlation ID, not a credential
- `installed_at_utc`: immutable timestamp captured at successful commit
- `receipt_state`: only states explicitly defined by protocol; no mutable "verified" flag as a substitute for signature verification

Constraints:
- Unique `(source_id, replica_id, generation_id)`.
- A second unique policy may be needed for source/generation across replicas; decide based on whether a single generation is intentionally installable on multiple gateways. Do not accidentally forbid legitimate multi-replica installation.
- Receipts are append-only. No UPDATE/DELETE in normal application path.
- Same tuple + same digest + same immutable manifest identity is idempotent and returns the original receipt.
- Same tuple + different digest or conflicting immutable metadata is rejected without changing bars/checkpoint/receipt.
- New generation progression must follow explicit source/cursor policy. Do not assume generation UUID lexical order is meaningful.
- Snapshot rows, checkpoint update and receipt insert commit atomically in one SQLite transaction.
- Receipt lookup is read-only and used to produce gateway startup evidence; callback-returned digest must be compared to the persisted receipt, not accepted on syntax alone.

This is a design proposal, not an approved schema or implementation.

## Required test additions

1. Fresh replica installs snapshot and persists receipt atomically.
2. Same generation + same digest returns original receipt ID/timestamp and leaves rows unchanged.
3. Same generation + different digest fails closed; prior bars/checkpoint/receipt unchanged.
4. Same generation + cursor or manifest metadata conflict fails closed.
5. New generation follows the approved cursor transition rule; prior receipt remains queryable.
6. Legacy checkpoint opens without synthetic receipt and is classified LEGACY_UNATTESTED.
7. Reopening/migrating a legacy DB repeatedly is idempotent and preserves all checkpoint/bar/event rows.
8. Injected exception after bar writes, checkpoint update, and receipt insert rolls back all three.
9. Restart after pre-commit interruption yields old complete state; after commit yields new complete state.
10. Gateway factory rejects callback digest that differs from durable receipt even if it is valid SHA-256 syntax.
11. Gateway factory rejects receipt source/replica/generation/cursor/manifest mismatch before Redis client creation.
12. Publisher verifier rejects missing gateway, duplicate gateway, stale receipt, wrong authenticated identity, wrong key ID or revoked key.
13. Receipt is unchanged after subsequent event cursor advances.
14. Receipt query returns consistent data during concurrent event application.

## Gate 25 status and external acceptance

Gate 25 remains OPEN. Local code and unit tests cannot prove:
- owner-host callback authentication and transfer-channel security;
- durable receipt custody and tamper-evident audit;
- owner-host Redis CA/ACL and persistence policy;
- Redis restart/failover and gateway process recovery;
- receipt retention/backup/restore under actual owner-operated conditions.

Do not claim these based on local SQLite tests or container-volume smoke tests.

## Project indicators

No indicator code/tests/formulas/hooks/renderers/UI changed; no indicator implementation credit.

| Indicator | Status |
|---|---|
| SMA20, EMA20, RSI14 Wilder | 🟨 Foundation |
| MACD12/26/9, Bollinger20,2 | 🟨 Foundation |
| Shared Indicator Hook | 🟨 Foundation; not chart-integrated |
| Footprint | 🟧 Synthetic prototype; user reference + reviewed blueprint required |
| Heatmap | 🟥 Not implemented; user reference + reviewed blueprint required |
| Liquidation Maps | 🟥 Not implemented |

Maintain warm-up nulls, source-index alignment, no future-candle repaint, invalid/gapped-bar rejection, stale-output clearing on identity/timeframe changes, and Footprint OFF standard candle spacing. No aggregate indicator percentage without approved weights/denominator.

Stage 1: 30/40 = 75% provisional. Stages 2–6 NOT SCORED/not officially opened. Overall project NOT SCORED. Gate 10: 0/10 external criteria formally closed. WebSocket Gates 25, 36 and 38 remain OPEN.

## IP3S — Indicator Proses Peningkatan Proyek Signifikan

Batch 62J-137 is PENDING exact-HEAD CI. Do not award a numeric score until the exact commit checks complete. The contribution is a refined trust boundary and additive migration/test contract; no runtime gate is closed.

ZERO COST. No paid services, deployment, accounts, credentials, device or Termux work. `main` untouched.
