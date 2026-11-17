# DEZZTA CHART — Gate 10 Batch 6: encrypted application restore integration

Date: 2026-11-17  
Branch: `phase-2/market-data-foundation`  
Source commit: `cfc56b7ba050201823952ea1b67dd38182dc9bfb`  
Scope: one end-to-end repository regression for criteria 30 and 31, plus project progress documentation

## Problem addressed

Existing tests covered SQLite backup/restore and authenticated encryption separately. The project did not yet have one CI test proving that an application-domain backup can pass through the complete encrypted artifact cycle and then satisfy the full application restore drill.

## Change

Added `test_encrypted_application_backup_round_trip_feeds_full_restore_drill` to `backend/tests/test_sqlite_restore_drill.py`.

The test chains:
1. Build an isolated SQLite database using actual DEZZTA CHART application stores (instrument registry, entitlements, price-alert zones, coverage, OHLCV and outbox).
2. Create a transactionally consistent SQLite Online Backup snapshot.
3. Encrypt the snapshot with the existing AES-256-GCM / PBKDF2-HMAC-SHA256 backup implementation.
4. Authenticate and decrypt the encrypted artifact into a fresh path.
5. Run the complete existing restore drill against the decrypted snapshot, including schema, integrity, foreign-key, row-content, domain read-back, outbox identity and post-restore write/read/cleanup checks.

It additionally verifies source-file immutability, decrypted/snapshot SHA-256 equality, report redaction, and temporary-file cleanup.

## Safety and acceptance boundary

- The passphrase is a test-only constant used only inside CI; no production secret is introduced.
- The test is isolated and synthetic. It does not access a real owner database.
- It does not prove off-host backup storage, separate key custody, retention/access controls, or restoration on the intended production host.
- Criteria 30 and 31 remain externally OPEN. No Stage 1 ticks are awarded.
- Exact source commit `cfc56b7ba050201823952ea1b67dd38182dc9bfb`: Automated Tests & Build [44112080352](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44112080352) **SUCCESS**, all **32/32 workflow steps** passed. Backend pytest: **1,009 passed in 36.34s**, including the new encrypted application backup → authenticated decrypt → full restore-drill test.
- CodeQL [44112080772](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44112080772): **SUCCESS**.
- Full Git History Secret Audit [44112080446](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44112080446): **SUCCESS**.
- Vercel FastAPI WSS POC preview status: **SUCCESS**. Main Vite preview status: **FAILURE — Vercel build-rate limit**. No retry loop or plan upgrade; this test-only source change does not modify frontend code, and the last known frontend preview remains the earlier READY deployment.

## Verification and platform blocker

The exact-head repository checks passed as listed above. The Vercel FastAPI WSS POC preview context passed. The main Vite preview context was blocked by a Vercel build-rate limit; no paid upgrade, bypass, or retry loop was attempted. The previous known-good frontend preview remains the last known READY frontend build.

## Files changed
- `backend/tests/test_sqlite_restore_drill.py`
- `docs/BACKUP_ENCRYPTION.md`
- `docs/STAGE_1_ACCEPTANCE_MATRIX.md`
- `docs/PROJECT_PROGRESS_INDICATOR.md`
- `PROJECT_STATUS.md`
- `docs/assets/stage-1-gate-dashboard.svg`
- `docs/assets/project-progress-dashboard.svg`

## Progress and cost
- Stage 1 remains 300/400 = 75% provisional.
- Gate 10 remains 0/10 formally closed; open criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6 remain NOT SCORED.
- ZERO COST maintained. No cloud storage, paid service, billing activation, Termux command/package, Android app change, or production credential is used.
- Protected `main` untouched.
