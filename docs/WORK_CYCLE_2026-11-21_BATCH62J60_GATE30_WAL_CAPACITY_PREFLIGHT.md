# DEZZTA CHART — Work Cycle 62J-60: Gate 30 WAL-aware capacity preflight

**Date:** 21 November 2026
**Branch:** phase-2/market-data-foundation
**Parent source/test HEAD:** 56dd8a3a9ebd9fb635357af5285980c461a5de0f
**Scope:** Gate 30 restore-runbook safety correction and exact-head evidence reconciliation
**Cost:** zero; documentation only; no host operation or deployment

## 1. Defect identified

The previous Gate 30 runbook defined S as the main SQLite database file size alone. That can understate the size of a consistent backup when SQLite is using WAL mode: committed pages may still be present in the -wal sidecar and visible to a read-only SQLite connection even when they are not yet reflected in the main database file.

## 2. Corrected sizing calculation

Define S_main as the main database file bytes, S_wal as the current WAL sidecar bytes (zero if absent), and S_logical as PRAGMA page_count multiplied by PRAGMA page_size from a read-only connection that sees committed WAL state.

Use S = max(S_main + S_wal, S_logical). For two destinations on the same filesystem, require at least 3*S plus max(64 MiB, 10% of 3*S). For separate destination filesystems, independently require S plus max(64 MiB, 10% of S) on each destination filesystem.

An unresolved rollback journal or recovery state is a stop condition. Do not delete or manipulate SQLite sidecars to make the preflight pass.

## 3. Files changed

- docs/GATE30_OWNER_HOST_RESTORE_DRILL_RUNBOOK.md — replaced main-file-only sizing with WAL-aware logical snapshot sizing and per-filesystem bounds.
- docs/STAGE_1_ZERO_COST_GATE_PLAN.md — added the WAL-aware preflight requirement to Gate 30.
- docs/INDICATOR_PROGRESS_LEDGER.md — recorded exact-head indicator test and CI evidence.
- docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md — reconciled exact-head CI, Android build, and Gate 10 dashboard.
- docs/WORK_CYCLE_2026-11-21_BATCH62J59_INDICATOR_PREFIX_CAUSALITY.md — replaced pending CI language with verified results.

## 4. Acceptance boundary

Gate 30 remains OPEN. This is a safer capacity-planning document, not a real owner-host restore. The active backend host, process working directory, actual database path, filesystem capacity and persistent volume are still unverified runtime facts.

Stage 1 remains 30/40 = 75% provisional. Gate 10 remains 0/10 formally closed. No Stage 1 tick is awarded.

## 5. ZERO COST / safety

No database was opened, copied, restored, or modified. No Termux command, production credential, cloud service, Vercel/Cloudflare deployment, paid service, or main-branch change occurred.

## 6. Parent exact-head evidence

Parent source/test HEAD 56dd8a3a9ebd9fb635357af5285980c461a5de0f passed Automated Tests (247 frontend tests; 1,218 backend tests), CodeQL, Full Git History Secret Audit, and Android debug APK CI. See the current dashboard for exact run IDs.