# DEZZTA CHART — Progress Record

Last verified snapshot: 2026-11-05  
Repository: https://github.com/deszztagd377-pixel/dezzta-chart  
Working branch: `phase-2/market-data-foundation`  
Snapshot HEAD before this documentation update: `8ae99f5c5a11cdfb8b5d52acc1455a47259f194b`  
Main HEAD: `e3841681bc69b73619058deaf939df82ae5116a1`

## Current percentage record

| Record | Value | Meaning |
|---|---:|---|
| Last formally weighted estimate in `PROJECT_STATUS.md` | **19.60%** | Historical formal estimate; last documented increment was +0.20 percentage points from 19.40% |
| Owner-recalled conversational checkpoint | **20.9%** | Preserved as the owner's recollection; no matching reproducible weight calculation has been located |
| Freshly reconciled overall percentage | **Not yet established** | Do not present either historical value as a newly recalculated current percentage |

The project percentage is a weighted milestone estimate toward the intended full application. It is **not** the percentage of files written, lines of code, commits, or CI jobs completed. A documentation-only commit or a passing CI run does not automatically increase overall project completion.

## Why the discrepancy remains open

The repository contains milestone and change-history notes, but does not yet contain a consolidated, reproducible ledger that:
1. Defines the complete project milestone groups and their total weights (100%).
2. Defines objective acceptance criteria for each milestone.
3. Assigns completion credit only to verified deliverables, avoiding duplicate credit for the same capability across commits.
4. Separates implemented code, automated tests, user-visible behavior, deployment verification, and owner-approved design.
5. Records evidence links and the calculation used for each percentage change.

Until that ledger is built and reviewed, **19.60% and 20.9% remain historical references**, not competing freshly verified measurements. Do not choose one by guesswork and do not increase the percentage merely because more commits exist.

## Verified evidence at this snapshot

- Working branch HEAD: `8ae99f5c5a11cdfb8b5d52acc1455a47259f194b`.
- Main HEAD: `e3841681bc69b73619058deaf939df82ae5116a1`; main was not modified by the audited work.
- GitHub Actions run [42053572558](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42053572558) completed successfully on the exact working-branch HEAD.
- The CI job passed frontend dependency installation, frontend unit tests, frontend production build, backend dependency installation, backend pytest, and backend container-image build.
- The repository has no root `package-lock.json`; the current CI uses `npm install`. Reproducible frontend dependency installation remains an open quality task.
- The latest verified code audit confirms code-level authenticated frontend stream integration. It does not establish deployed backend operation, live provider delivery, synchronized exchange time, or production performance.

## Product expansion gate — owner clarification (2026-11-05)

The owner has clarified that major UI reconstruction and broad feature expansion may begin at **40% overall project progress**, rather than 50%.

At the 40% gate:
1. Reconcile and publish the weighted milestone ledger.
2. Prepare a scoped UI/feature blueprint using the owner's visual preferences.
3. Review scope and priorities with the owner before large implementation.
4. Implement incrementally with tests and acceptance checks.

Before 40%, prioritize foundation quality, reliability, documentation, secure configuration, dependency hygiene, accessibility, responsive behavior, and regression coverage. The 40% gate is a planning checkpoint, not a promise that all planned features will be complete.

## Next progress-accounting work

- Rebuild the milestone weight model from the actual product scope.
- Map each verified implementation to exactly one primary milestone to prevent double counting.
- Separate completed, partial, blocked, planned, and unverified work.
- Reconcile the historical 19.60% and owner-recalled 20.9% values with evidence.
- Publish a new percentage only after the calculation is reproducible and the owner has reviewed the model.
