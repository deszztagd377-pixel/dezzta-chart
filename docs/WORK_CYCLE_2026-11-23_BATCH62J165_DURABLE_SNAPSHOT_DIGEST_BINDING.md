# WORK CYCLE — Batch 62J-165: Durable Snapshot Digest Binding

Date: 23 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent/source HEAD: `16160a5a6cd73684659b9bee118fcce1adddd670`  
Scope: WebSocket gateway snapshot integrity and durable replica checkpoint. No provider API, indicator runtime/UI, cloud deployment, paid service, or `main` changes.

## Finding

The snapshot installer already verifies the complete JSONL snapshot, canonical bars, row count and SHA-256 manifest before committing replica bars and checkpoint atomically. However, the digest was not persisted in `ohlcv_replica_checkpoint`. The gateway runtime validated callback digest syntax and matched source ID, generation and cursor to the durable checkpoint, but could not independently bind that callback digest to durable local evidence.

This was a callback-to-checkpoint verification gap, not evidence of a remote unauthenticated exploit. The owner-provided installer remains a trusted transfer boundary; this change does not create an authenticated cross-host receipt protocol.

## Implementation

- Add nullable `snapshot_sha256` to the replica checkpoint schema.
- Migrate existing databases by adding the column when absent. Existing legacy rows remain `NULL` (unattested); no digest is fabricated.
- Persist the exact digest verified by the installer in the same SQLite transaction as full bar replacement and checkpoint advancement.
- Expose the digest through `checkpoint()` and the consistent `load_snapshot()` read view.
- Bump replica schema compatibility marker from 3 to 4. Existing version-3 checkpoints require a current verified snapshot before event replay.
- Gateway runtime now requires callback digest to exactly match the durable checkpoint digest before constructing a Redis client.
- Add regression coverage for durable/restart persistence, legacy migration and re-attestation by verified reinstall, and a callback reporting a forged but well-formed SHA-256. The forged callback must fail before Redis client creation.

## Integrity model and limitations

The stored digest is provenance for the installed base snapshot. Subsequent contiguous outbox events advance the applied cursor but do not rewrite the base snapshot digest. This is not an immutable historical receipt ledger, a digital signature, a gateway identity attestation, or proof of who transferred the snapshot. Gate 25 still requires owner-approved authenticated gateway receipts, key lifecycle and host-side recovery evidence.

## Test and CI status

The regression tests are submitted to exact-HEAD GitHub Actions. No local test execution is claimed. Acceptance remains pending until Automated Tests, CodeQL, OCI ARM64 readiness and full Git-history Secret Audit all succeed on this exact commit. Any failure must be inspected and corrected before acceptance.

## Changed files

1. `backend/app/ohlcv_store.py`
2. `backend/app/ohlcv_redis_gateway_runtime.py`
3. `backend/tests/test_ohlcv_store.py`
4. `backend/tests/test_ohlcv_redis_gateway_runtime.py`
5. `docs/WORK_CYCLE_2026-11-23_BATCH62J165_DURABLE_SNAPSHOT_DIGEST_BINDING.md`
6. `docs/INDICATOR_PROGRESS_LEDGER.md`
7. `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`

## Indicator progress — full reconciliation

No indicator formula, numeric kernel, shared hook, chart binding, renderer, UI, or indicator-specific test changed. Indicator implementation credit: **0**.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 | 0–100 pane, 30/70 guides, toggle/legend/value and lifecycle |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33 | Pane, MACD/signal lines, histogram, zero guide and lifecycle |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Three-line overlay, toggle/values, identity/lifecycle/render/performance |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot and aligned calculation output | Hook tests, chart binding, stale clearing, settings/legend and identity lifecycle |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, valid bid/ask source contract, cluster renderer |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer/tests |
| Liquidation Maps | 🟥 Not implemented | No accepted data/renderer contract | Defensible provenance/calculation contract, reviewed blueprint, renderer/tests |

Shared invariants: warm-up nulls; exact candle-index alignment; prefix causality/no future repaint; reject invalid/gapped data; clear stale outputs on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone activates spaced clusters. Footprint/Heatmap visual work remains gated on user references and reviewed blueprint. Aggregate indicator progress remains NOT SCORED because approved weights and denominator do not exist.

## Overall project progress and significant delta

- Stage 1 Foundation, Security & Data Integrity: **30/40 = 75% provisional** 🟨.
- Stages 2–6: **NOT SCORED / not officially opened** ⬜.
- Gate 10: **0/10 external acceptance criteria formally closed** 🟥.
- WebSocket Gate 25: **OPEN** 🟧 — local durable digest binding strengthened; authenticated cross-host receipt/key lifecycle still outstanding.
- WebSocket Gate 36: **OPEN** 🟥 — public production WSS, real Firebase project, reverse-proxy and physical Android WebView/network acceptance remain outstanding.
- WebSocket Gate 38: **OPEN** 🟥 — owner-host metrics persistence, backup/retention, alerting and recovery acceptance remain outstanding.
- Overall project: **NOT SCORED**; six-stage weights and total denominator are not approved.
- Significant verified engineering delta: snapshot digest is now intended to be durably bound to the installed checkpoint, and callback mismatch is rejected before Redis startup. This is not Gate 25 closure.

ZERO COST preserved. No paid services, cloud account, hosting, domain, external market-data entitlement, device operation, or publication fee. `main` untouched.
