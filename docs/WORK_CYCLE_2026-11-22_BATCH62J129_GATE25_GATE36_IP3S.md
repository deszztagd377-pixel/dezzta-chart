# Batch 62J-129 — Gate 25 checkpoint-integrity correction, Gate 36 continuation and IP3S

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audited source baseline:** `c3a882be9b389e31ca4bee334d0a02992983ba02`  
**Scope:** read-only source/test audit and documentation reconciliation. No runtime code or tests changed.

## Exact-head CI

All workflows on the audited baseline `c3a882be9b389e31ca4bee334d0a02992983ba02` are SUCCESS:
- Automated Tests: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44988316167
- CodeQL: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44988316151
- Full Git History Secret Audit: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44988316147

Branch HEAD was verified as `c3a882be9b389e31ca4bee334d0a02992983ba02`; parent is `54f0d1c9908b19e3b3a04974e52c4e84500db57d`. `main` is untouched.

## Gate 25 — important precision correction

Files reviewed:
- `backend/app/ohlcv_redis_runtime.py`
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/ohlcv_store.py`
- `backend/tests/test_ohlcv_redis_runtime.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`

### What is verified

1. Source snapshot export uses a pinned SQLite read transaction, a versioned manifest, source ID, generation, retention floor, high-water cursor, row count and canonical SHA-256.
2. `verify_global_snapshot` recomputes the digest and validates manifest, ordering, row count and bounds.
3. Gateway installation uses `install_global_snapshot()`; the local replica checkpoint persists source ID, replica ID, applied cursor, snapshot generation, retention floor and schema/protocol versions.
4. Gateway runtime compares returned source/generation/high-water metadata to that durable checkpoint before creating Redis client/consumer.
5. Source publisher evidence requires a lowercase SHA-256 digest and a metadata-matching receipt for every configured gateway before Redis construction.

### Newly isolated boundary

The durable `ohlcv_replica_checkpoint` schema does **not** persist the snapshot SHA-256. The gateway runtime validates the callback's returned digest format and returns it as evidence, but it cannot compare that digest to a digest stored in the checkpoint because no such checkpoint field exists. The gateway unit test asserts the returned digest equals the source export metadata; it does not independently prove the durable checkpoint stores or authenticates that digest.

Therefore prior shorthand saying the gateway compares the snapshot hash *against its durable checkpoint* is too strong. Accurate statement: the gateway verifies the snapshot file during `install_global_snapshot()` and matches source/generation/cursor metadata to the durable checkpoint; the installer-returned digest is propagated, but is not independently anchored in that checkpoint.

This is a **documentation/evidence gap and a potential integrity-hardening design item**, not yet a proven exploitable defect: the trusted installer callback is required to call the verified store installer. Before changing schema or runtime, define whether the checkpoint should persist snapshot digest, how it migrates existing replicas, and how subsequent stream updates affect the meaning of a snapshot-only digest. No blind patch was made.

### Gate 25 status: OPEN

- [x] Consistent snapshot export and canonical SHA-256 verification.
- [x] Atomic local snapshot install and durable source/generation/cursor checkpoint.
- [x] Publisher evidence field matching for each configured gateway.
- [x] Gateway source/generation/cursor checkpoint matching before Redis construction.
- [ ] Durable checkpoint anchoring of snapshot digest (design decision; current checkpoint has no digest column).
- [ ] Authenticated owner-host snapshot transfer and independently authenticated per-gateway receipts.
- [ ] Owner-host Redis TLS CA/hostname/ACL, persistence, restart/failover and disk-pressure evidence.

## Gate 36 — current acceptance boundary

Browser client and supervisor source/test coverage exists for authenticated ticket exchange, subscribe, snapshot/update, replay, renewal acknowledgement, heartbeat, reconnect/backoff, fresh Firebase ID token acquisition, cursor resume and resnapshot on gaps. Chart lifecycle tests simulate online/offline and document visibility changes.

Still not accepted:
- verified public HTTPS ticket endpoint and WSS reverse-proxy route with trusted TLS;
- live Firebase project, real token revocation and entitlement grant/revoke/renew E2E;
- real browser and Android WebView background/foreground/process-death/network-handover;
- real network interruption, replay/resnapshot and duplicate suppression;
- operator-visible external alert delivery and human acknowledgement.

The short-lived single-use ticket currently binds subject and purpose; series authorization is separate, and Origin is checked at handshake. Whether series and Origin should also be cryptographically bound into ticket claims remains a threat-model decision for review, not an assumed defect or implemented fix.

**Gate 36 remains OPEN.** CI and simulated browser tests do not prove public deployment or real-device acceptance.

## Indicator implementation reconciliation

No indicator source, tests, hooks, renderers or chart UI changed in this batch. No implementation credit:
- SMA20 🟨 foundation — 20-close mean; first valid index 19.
- EMA20 🟨 foundation — SMA-seeded; alpha 2/21; first valid index 19.
- RSI14 Wilder 🟨 foundation — 14 close changes; first valid index 14.
- MACD12/26/9 🟨 foundation — MACD index 25; signal/histogram index 33.
- Bollinger20,2 🟨 foundation — 20-close mean ±2 population SD; first valid index 19.
- Shared Indicator Hook 🟨 foundation — validated, candle-index-aligned calculation output; not chart-integrated.
- Footprint 🟧 simulated educational accumulator only; visual work waits for user reference image(s) and reviewed blueprint.
- Heatmap 🟥 not implemented.
- Liquidation Maps 🟥 not implemented.

Common acceptance: warm-up `null`, exact source-candle alignment, no future-candle repaint, stale clearing on identity/timeframe change, renderer/UI toggles and legends/current values, lifecycle and rendering tests. Footprint OFF preserves ordinary candle spacing; explicit ON alone switches to spaced cluster layout. Do not start Footprint/Heatmap visual work before references and blueprint review. No aggregate indicator percentage without an approved denominator and weights.

## New project indicator — Indicator Proses Peningkatan Proyek Signifikan (IP3S)

IP3S is a **per-work-cycle delivery-quality indicator**, not the overall project completion percentage.

| Dimension | Weight | Full-credit condition |
|---|---:|---|
| Verified engineering delta | 25 | Tested source/runtime improvement or independently verified acceptance evidence |
| Test/CI evidence | 20 | Exact-HEAD relevant tests/checks pass; limitations are explicit |
| Blocker reduction | 20 | A real acceptance blocker is closed or its exact owner/action is isolated |
| Canonical documentation | 20 | Source-backed findings, status, and next acceptance criteria are reconciled |
| Scope and cost integrity | 15 | Correct branch, no regressions claimed, ZERO COST and authorization boundaries respected |

Scoring rules:
- Score each dimension 0–100%, then apply its weight.
- Documentation-only work cannot score engineering-delta points for runtime implementation.
- CI cannot close owner-host or real-device gates.
- A discovered blocker earns blocker-reduction credit only for precision/decision-readiness, not as a closed gate.
- Report IP3S per batch and keep overall project completion separate.

**Batch 62J-129 IP3S: 58/100 (documentation/audit delivery only).**
- Verified engineering delta: 0/25 — no runtime source/test implementation changed.
- Test/CI evidence: 20/20 — three exact-HEAD workflows succeeded.
- Blocker reduction: 8/20 — isolated the missing durable digest anchor and clarified Gate 36 owner evidence; no production gate closed.
- Canonical documentation: 15/20 — this batch report plus canonical ledger/current-status updates.
- Scope/cost integrity: 15/15 — branch, no-main, no-deployment and ZERO COST boundaries held.

Total: 0 + 20 + 8 + 15 + 15 = **58/100**. This score reflects a substantial audit/documentation cycle, not a 58% project completion claim.

## Project acceptance status (unchanged)

- Gate 10: 0/10 formally closed.
- Stage 1: 30/40 = 75% provisional.
- Stage 2: blocked pending formal Stage 1 exit and open gates.
- Gates 25 and 36: OPEN.
- No deployment, hosting, domain, account, production credential, device/Termux action or paid service.
- ZERO COST maintained; `main` untouched.

## Next engineering sequence

1. Decide whether snapshot digest must be durably anchored in replica checkpoint; define migration and digest lifecycle before implementation.
2. Continue Gate 36 reverse-proxy/TLS and ticket threat-model review from existing repository configuration; do not invent a proxy config or public hostname.
3. Keep owner-host and real-device acceptance items open until independently evidenced.
4. Keep indicator implementation stage-gated; next eligible work is blueprint/reference preparation only when the required user image(s) are supplied.
