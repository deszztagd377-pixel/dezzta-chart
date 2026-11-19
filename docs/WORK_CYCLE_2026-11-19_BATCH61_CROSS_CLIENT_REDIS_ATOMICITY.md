# Batch 61 — Cross-client Redis atomicity regression

- Parent: `1253d592a490247c081d326118a331da8e156592`
- Branch: `phase-2/market-data-foundation`
- Scope: test coverage + progress documentation; no production source behavior change.

## Change set

1. Added `test_redis_ticket_and_lease_guards_share_atomic_state_across_clients` in `backend/tests/test_shared_guard.py`.
   - Two independent Redis client connections share one CI Redis instance.
   - Concurrent consumption of one ticket must return the account subject exactly once.
   - Per-account lease cap is enforced across clients.
   - Global lease cap is enforced across clients.
   - Lease renewal/release from the second client affects state created by the first client.
2. Appended the Batch 61 evidence and complete indicator ledger to `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`.
3. Updated the current SVG dashboard to Batch 61 and corrected Stage 4's NOT SCORED card to neutral grey.
4. Reviewed the Batch 60 Trivy artifact: the exact CI image report had zero HIGH/CRITICAL findings under the configured filter.

## Acceptance boundary

This closes a **local CI coverage gap**, not Gate 25. Two independent Redis client connections do not equal two independently deployed owner application instances. Owner-managed Redis, production ACL/TLS, multi-instance outage/recovery and owner acknowledgement remain required.

Gate 10 remains 0/10 closed. Stage 1 remains 75% provisional (30/40 criteria; 300/400 ticks). Stages 2–6 are unscored; overall project progress is not established. Indicator visual work remains parked until the Stage 4 gate and user references/blueprint conditions are met.

## Validation

Exact-head Automated Tests, CodeQL and Full Git History Secret Audit are required after commit. No test result is pre-claimed. Zero-cost only; no deployment, no Termux, and `main` untouched.
