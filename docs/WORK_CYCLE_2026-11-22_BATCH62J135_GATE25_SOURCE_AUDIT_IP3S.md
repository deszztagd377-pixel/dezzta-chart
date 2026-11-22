# Batch 62J-135 — Gate 25 source audit, exact-head CI acceptance and IP3S reconciliation
Date: 22 November 2026
Branch: `phase-2/market-data-foundation`
Starting HEAD: `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`
Scope: documentation and acceptance design only; no runtime/schema/test source changes.

## Verified repository and CI state

Branch ref was verified at starting HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`; `main` was not touched.

Exact-HEAD workflows:
- Automated Tests [44991805066](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991805066): **SUCCESS**, exact HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`.
- CodeQL [44991805111](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991805111): **SUCCESS**, exact HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`.
- Full Git History Secret Audit [44991805060](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991805060): **SUCCESS**, exact HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`.
- Android debug APK workflow [44991640574](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640574): **SUCCESS** on source/test commit `ecf7decb8e823effe09a6be8a9973bb98619ae92`; this is CI debug-build evidence, not a production release and not a build on the later docs-only HEAD.

The exact-HEAD Automated Tests job completed successfully. The workflow job's completed steps include frontend dependency audit/unit tests/build, backend dependency installation/tests, isolated Redis TLS CA/hostname enforcement fixture, bounded synthetic SQLite outbox and metrics checks, backend container build/smoke, vulnerability scan/report and dependency audit enforcement. CI success does not prove owner-host Redis persistence/failover or public WSS.

## Gate 25 — source-backed installation receipt audit

Files inspected at the starting HEAD:
- `backend/app/ohlcv_store.py`
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/ohlcv_redis_runtime.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`
- `backend/tests/test_ohlcv_replica_bridge.py`
- `docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md`

Confirmed behavior:
1. `SQLiteOhlcvReplicaStore.install_global_snapshot()` preflights the snapshot, then opens a write transaction, re-reads the snapshot and validates its manifest/content while inserting rows. Snapshot replacement and checkpoint update commit or roll back together.
2. The replica checkpoint persists source ID, replica ID, applied cursor, snapshot generation, retention metadata and schema/protocol versions. It does not persist the snapshot SHA-256 or an immutable installation receipt.
3. `build_gateway_replica_runtime_factory()` checks installer status, source ID, generation, high-water cursor, digest syntax and checkpoint alignment before creating the Redis client. The digest is returned as runtime `snapshot_evidence`; the code does not compare it to a durable receipt because no such receipt is currently stored.
4. Source-side `_validate_snapshot_evidence()` validates the snapshot manifest and requires a matching receipt for each configured gateway, including source, stream, generation, cursor and SHA-256. The callback is explicitly responsible for authenticating/reading those owner-host receipts. This validator does not itself contact or authenticate remote gateways.
5. Existing tests prove snapshot-before-Redis construction, source mismatch rejection, unverified installer rejection, production plaintext Redis rejection, and cleanup on consumer-construction failure. They do not prove durable gateway receipt persistence, signature verification, immutable receipt conflict semantics, crash/restart receipt consistency, or owner-host custody.

### Gate 25 status: OPEN

The missing feature is not simply a hash column. The acceptance contract must bind:
- authenticated authoritative source identity;
- exact snapshot generation, high-water cursor and canonical digest;
- replica identity and receipt schema;
- authenticated installer/attestation identity;
- durable immutable receipt history;
- atomicity between snapshot rows, checkpoint replacement and receipt insertion.

A SHA-256 digest establishes content identity only when compared against a trusted value. It does not independently establish who supplied the snapshot.

### Required implementation acceptance matrix (design only)

| Case | Expected result |
|---|---|
| Valid authenticated manifest and matching content | Install and persist receipt atomically |
| Altered bytes or recomputed digest mismatch | Reject; preserve prior rows/checkpoint/receipts |
| Unknown signer, wrong key or invalid signature | Reject before accepting snapshot |
| Source or replica identity mismatch | Reject |
| Same source/replica/generation and same digest | Idempotent; preserve original receipt |
| Same generation with different digest | Hard conflict; fail closed |
| New generation with valid cursor progression | Add a new immutable receipt |
| Failure before transaction commit | No partial snapshot/checkpoint/receipt state |
| Process interruption around commit then restart | Recover to either prior complete state or new complete state |
| Legacy checkpoint without receipt | Mark LEGACY_UNATTESTED; never fabricate provenance |
| Normal event cursor advancement | Preserve historical installation receipt |
| Repeated migration/rollback | Idempotent and backward-compatible; never downgrade verified provenance |

### Recommended implementation sequence — no implementation performed

1. Approve the trust model: owner-pinned public key and signed manifest, or equivalent authenticated owner-controlled transfer. Decide signature format, key ID, rotation and revocation policy.
2. Define immutable receipt schema and uniqueness key `(source_id, replica_id, generation_id)`; define explicit legacy state and retention/archival policy.
3. Add transactional receipt insertion to the same SQLite transaction as snapshot rows/checkpoint replacement.
4. Add read-only receipt query and bind gateway runtime evidence to the persisted receipt, not only the installer return value.
5. Make source-side verification consume authenticated receipt records with explicit gateway identity and custody.
6. Add failure-injection tests for tampering, signer/key errors, generation conflicts, transaction rollback, process termination, restart, migration and retention.
7. Re-run full CI on exact branch HEAD. Owner-host transfer, key custody, Redis persistence/restart/failover remain separately required external acceptance.

No runtime/schema implementation was started because the ADR is design-only and the trust/key lifecycle decisions are not yet approved.

## WebSocket acceptance gates

- Gate 25: **OPEN** — durable immutable replica installation receipt, authenticated transfer provenance and owner-host Redis persistence/restart/failover.
- Gate 36: **OPEN** — public WSS/reverse proxy/certificate lifecycle, live Firebase project, production browser session, Android WebView lifecycle and real network handover.
- Gate 38: **OPEN** — owner-host metrics persistence, disk-pressure/restart/backup/retention, operator dashboard, external alert delivery and recovery drill.
- Gate 10: **0/10 external criteria formally closed**.

The 4403 close-reason diagnostic correction from Batch 62J-134 is CI-accepted; it does not close Gate 36 or Gate 25.

## Technical indicator progress ledger

No indicator runtime, test, calculation, hook, renderer or UI source changed in this batch. No indicator implementation credit is awarded.

| Indicator/component | Current status | Verified scope / limitation |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19 |
| EMA20 | 🟨 Foundation | SMA-seeded, alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram index 33 |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; not chart-integrated |
| Footprint | 🟧 Prototype/foundation only | Synthetic educational accumulator; not exchange-native bid/ask truth |
| Heatmap | 🟥 Not implemented | Visual implementation blocked pending user reference image and reviewed blueprint |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence |

Shared requirements remain: warm-up nulls, candle-index alignment, prefix causality/no future-candle repaint, invalid/gapped bars not silently converted to zero, stale-output clearing on symbol/venue/dataset/chart/timeframe changes, and renderer/lifecycle validation. Footprint OFF must preserve ordinary candlestick spacing; only explicit ON enables the dedicated spaced cluster layout. Footprint and Heatmap visual implementation must wait for the user's reference image(s) and reviewed blueprint.

No aggregate indicator completion percentage is assigned because indicator weights and denominator are not approved.

## Project-wide progress indicator

| Stage | State |
|---|---|
| 1. Foundation, Security & Data Integrity | 30/40 criteria = **75% provisional** |
| 2. Market Data Infrastructure | **NOT SCORED / not officially opened** |
| 3. Chart Engine & Timeframe | **NOT SCORED / not officially opened** |
| 4. Indicators & Analytics | **NOT SCORED / not officially opened** |
| 5. Professional UI & Interactive Tools | **NOT SCORED / not officially opened** |
| 6. Hardening, Validation & APK Release | **NOT SCORED / not officially opened** |

Overall project: **NOT SCORED**. Six-stage weights and the overall acceptance denominator have not been approved. Do not derive an overall percentage from Stage 1 alone.

## IP3S — Indicator Proses Peningkatan Proyek Signifikan

IP3S measures this work cycle's verified delivery quality, not project completion.

| Dimension | Score | Rationale |
|---|---:|---|
| Verified engineering delta | 18/25 | Batch 62J-134 corrected a real false WebSocket 4403 diagnostic and added regression coverage; this batch completed source-backed Gate 25 acceptance analysis, but made no new runtime change |
| Exact-HEAD test/CI evidence | 20/20 | Automated Tests, CodeQL and Secret Audit all SUCCESS on exact HEAD |
| Blocker reduction | 12/20 | Gate 25 trust/receipt gap and implementation acceptance cases are now isolated; gate remains open |
| Canonical documentation | 20/20 | Gate 25 source audit, matrix, indicator ledger and project-stage state reconciled |
| Scope/cost integrity | 15/15 | ZERO COST; correct branch; no credentials, deployment, device work or main changes |
| **IP3S total** | **85/100** | Cycle delivery score only; not overall completion |

## Cost, safety and branch integrity

ZERO COST. No paid service, hosting, domain, API, cloud resource, account, deployment, production credential, secret, Android device or Termux action. No runtime/schema/test source edits in Batch 62J-135. `main` untouched.

