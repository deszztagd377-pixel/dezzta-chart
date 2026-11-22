# Batch 62J-136 — Gate 25 generation-conflict and receipt-boundary audit
Date: 22 November 2026
Branch: `phase-2/market-data-foundation`
Audited HEAD: `613bb97e1c2529297f808ff936f150bd77e872b5`
Scope: source-backed acceptance refinement and documentation only. No runtime, schema, test, infrastructure or credential changes.

## Verified exact-HEAD CI snapshot

All three workflows target the audited HEAD `613bb97e1c2529297f808ff936f150bd77e872b5`:
- Automated Tests [44992346001](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992346001): IN PROGRESS at audit time. Frontend dependency audit, unit tests, frontend build, backend tests, Redis TLS fixture and synthetic OHLCV outbox benchmark had completed successfully. Metrics benchmark was running; container build/smoke and image scan steps were still pending.
- CodeQL [44992346021](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992346021): PENDING at audit time.
- Full Git History Secret Audit [44992346023](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992346023): PENDING at audit time.

Do not mark exact-HEAD CI complete until all workflows finish. The prior HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b` had passing evidence; that does not substitute for the newer HEAD.

## Additional source finding — generation conflict is not enforced by the replica installer

Source reviewed:
- `backend/app/ohlcv_store.py`, `SQLiteOhlcvReplicaStore.checkpoint()` (around line 1354)
- `backend/app/ohlcv_store.py`, `SQLiteOhlcvReplicaStore.install_global_snapshot()` (around line 1737)
- `backend/app/ohlcv_redis_gateway_runtime.py`, `build_gateway_replica_runtime_factory()`
- `backend/app/ohlcv_redis_runtime.py`, `_validate_snapshot_evidence()`

Observed installer behavior:
1. The current checkpoint read inside `install_global_snapshot()` selects only `source_id` and `applied_cursor`.
2. It rejects a different source and rejects a snapshot whose high-water cursor is lower than the existing applied cursor.
3. It does not compare the incoming generation ID with the stored generation ID, and it does not compare a trusted digest against an immutable prior receipt.
4. The checkpoint upsert is keyed by `source_id` and updates `snapshot_generation`, cursor and retention fields.
5. The snapshot digest is recomputed from the bytes installed and checked against the manifest/preflight metadata. This protects against file mutation during installation, but does not establish signer identity or prevent an authenticated callback from presenting a conflicting artifact for an already-installed generation.

### Acceptance implication

The existing implementation guarantees transactional replacement and rejects stale cursor rollback, but it does not yet guarantee immutable generation identity. In particular, the source/replica/generation uniqueness and same-generation/same-digest idempotency contract from the proposed ADR is not enforced by a durable receipt table.

This is an additional Gate 25 acceptance gap, not a claim that an unauthenticated remote attacker can currently bypass the owner's transfer callback. The trust boundary remains delegated to that callback and must be explicitly specified and tested.

## Refined acceptance contract

Before schema/runtime implementation, approve these invariants:

- **Identity tuple:** authoritative source ID + stable replica ID + snapshot generation ID.
- **Content identity:** canonical SHA-256 recomputed from the exact installed bytes.
- **Authenticity:** authenticated source/installer identity anchored to an owner-controlled trust mechanism; a digest alone is insufficient.
- **Immutable receipt:** exactly one durable receipt per identity tuple; it records digest, high-water cursor, row count, schema/manifest version, attestation key ID or authenticated transfer identity, and installation metadata. No secrets/private keys are stored.
- **Idempotent replay:** same tuple and same digest returns the existing receipt without rewriting its provenance.
- **Conflict fail-closed:** same tuple with a different digest or incompatible cursor/manifest is rejected; no bar/checkpoint/receipt mutation.
- **Generation progression:** new generation is accepted only under an explicit cursor and source policy; historical receipts remain immutable.
- **Atomic commit:** snapshot rows, checkpoint and new receipt commit in one SQLite transaction.
- **Legacy state:** old checkpoint without a receipt is explicitly LEGACY_UNATTESTED; never fabricate historical provenance.
- **Recovery:** interruption before commit leaves old complete state; after commit leaves new complete state. Restart can never observe a mixed state.
- **Receipt query:** gateway runtime evidence is read back from durable local receipt state after installation, not trusted solely from a callback return object.
- **Retention:** receipt retention/archival is explicit and independent of ordinary bar retention or live cursor advancement.

## Required failure-injection tests

| Scenario | Required postcondition |
|---|---|
| Same tuple + same digest repeated | Same receipt identity and original installation timestamp |
| Same tuple + different digest | Hard conflict; prior bars, checkpoint and receipt unchanged |
| Same generation + higher cursor but changed content | Rejected unless protocol explicitly defines a new generation |
| New generation + valid cursor progression | New receipt; previous receipt remains queryable |
| Snapshot file changes between preflight and locked read | Rejected; old complete state preserved |
| Failure after bar insertion but before checkpoint/receipt | Transaction rollback restores old state |
| Failure after receipt insert but before commit | Transaction rollback removes new receipt and restores old state |
| Process killed before commit / after commit | Restart yields old complete state / new complete state respectively |
| Legacy checkpoint migration repeated | Stable LEGACY_UNATTESTED state; no synthetic receipt |
| Event cursor advances after snapshot install | Immutable receipt remains unchanged and queryable |

## Implementation sequence — still gated

1. Approve the trust model, signature/attestation format, key ID, rotation and revocation policy.
2. Freeze receipt schema and unique identity tuple.
3. Add migration and read/query APIs with legacy classification.
4. Add transaction-bound receipt insertion and conflict checks.
5. Bind runtime startup evidence to the persisted receipt.
6. Add the failure-injection matrix above.
7. Run all CI workflows on the exact resulting commit and separately plan owner-host acceptance.

No code/schema change is authorized by this report. Do not silently choose an authentication scheme or create key material on behalf of the owner.

## Project and indicator status

No indicator source, calculation, hook, renderer, UI or test changed. No indicator implementation progress is awarded.

| Indicator | Status | Verified boundary |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19 |
| EMA20 | 🟨 Foundation | SMA-seeded, alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 Foundation | First valid index 14 |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33 |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; not chart-integrated |
| Footprint | 🟧 Prototype/foundation | Synthetic accumulator only; user visual reference and reviewed blueprint required before visual work |
| Heatmap | 🟥 Not implemented | User visual reference and reviewed blueprint required |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence |

Shared indicator acceptance remains warm-up nulls, candle-index alignment, prefix causality/no future-candle repaint, invalid/gapped bars not silently converted to zero, stale-output clearing on symbol/venue/dataset/chart/timeframe changes, and renderer/lifecycle validation. Footprint OFF must preserve normal candlestick spacing; explicit ON alone enables the spaced cluster layout. No aggregate indicator percentage is assigned because weights/denominator are not approved.

### Project-wide stage indicator

| Stage | State |
|---|---|
| 1. Foundation, Security & Data Integrity | 30/40 criteria = **75% provisional** |
| 2. Market Data Infrastructure | **NOT SCORED / not officially opened** |
| 3. Chart Engine & Timeframe | **NOT SCORED / not officially opened** |
| 4. Indicators & Analytics | **NOT SCORED / not officially opened** |
| 5. Professional UI & Interactive Tools | **NOT SCORED / not officially opened** |
| 6. Hardening, Validation & APK Release | **NOT SCORED / not officially opened** |

Overall project: **NOT SCORED**. Stage weights and the total acceptance denominator are not approved. Gate 10 remains **0/10 external criteria formally closed**. WebSocket Gate 25 remains **OPEN**; Gates 36 and 38 also remain **OPEN**.

### IP3S — Indicator Proses Peningkatan Proyek Signifikan

**Batch 62J-136: PENDING exact-HEAD CI.** No numeric score is awarded until CI finishes. This batch's verified contribution is a newly isolated installer generation-conflict gap and a more precise failure-injection contract; it is not an implementation completion claim.

ZERO COST maintained. No paid hosting, API, domain, cloud resource, deployment, account, production credentials, device or Termux work. `main` untouched.
