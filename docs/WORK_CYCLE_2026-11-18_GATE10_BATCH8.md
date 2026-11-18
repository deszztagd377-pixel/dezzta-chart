# DEZZTA CHART — Gate 10 Work Cycle Batch 8

Date: 2026-11-18  
Branch: `phase-2/market-data-foundation`  
Source/test checkpoint: `2a20201ccd5730a5f09765bb01677846cdfb3eca`  
Cost policy: **ZERO COST**

## Objective

Remove the CI fail-fast diagnostic blind spot while preserving the frontend dependency audit as a mandatory security gate.

## Root cause

The workflow ran `npm audit --audit-level=high` before frontend tests/build and backend checks. The currently unresolved High advisory in dev-only transitive `picomatch@4.0.7` caused the job to stop at that step. As a result, unrelated test/build/security diagnostics were skipped.

## Changes

1. `.github/workflows/ci.yml`
   - Added stable step ID `frontend_dependency_audit`.
   - Added `continue-on-error: true` to the audit step only, allowing independent diagnostics to proceed.
   - Added a final `if: always()` enforcement step after the diagnostic and artifact steps.
   - The final step reads `steps.frontend_dependency_audit.outcome` and fails the job unless the audit outcome is exactly `success`.
   - No `npm audit` removal, ignore list, advisory suppression, force fix, or security waiver was introduced.

2. `backend/tests/test_ci_dependency_audit_order.py`
   - Added static regression coverage for the audit step ID and command.
   - Verifies the audit continues diagnostics but is still enforced at the end.
   - Verifies frontend unit tests, frontend build, backend tests, and container image scanning occur between audit and final enforcement.
   - Verifies the final enforcement step is ordered after the container vulnerability report upload.
   - Strengthened by follow-up commit `0e92295918a46dbb741b27d1bbd60618e8f7bc85`.

3. `docs/PROJECT_PROGRESS_INDICATOR.md`
   - Updated audit date and added Batch 8 evidence/status.
   - Preserved Stage 1 and Gate 10 accounting.

4. `docs/STAGE_1_ACCEPTANCE_MATRIX.md`
   - Recorded the workflow correction and the fact that the upstream dependency advisory remains open.

5. `docs/assets/project-progress-dashboard.svg`
   - Refreshed the six-stage colored progress dashboard status line.

6. `docs/assets/stage-1-gate-dashboard.svg`
   - Refreshed the Gate 10 dashboard status line.

## Verification boundary

The source/workflow/test changes are committed. The new exact-head CI run has not yet been read back in this report. The expected result is:
- Frontend unit tests and build execute despite the npm audit finding.
- Backend tests and later diagnostics execute if their own prerequisites pass.
- The final audit enforcement step fails while npm audit still reports the High advisory.

This expected behavior is not yet claimed as observed. CI is not green until a run proves all checks and the dependency audit passes. The upstream advisory is not fixed by this workflow change.

## WebSocket POC status

- The isolated synthetic WSS preview remains the previously confirmed READY deployment.
- The bounded heartbeat probe is deployed but has not been run for 330 seconds.
- A client close at 330 seconds is not evidence of a Vercel 300-second platform close.
- No production data, credentials, or fan-out is connected.
- No paid deployment retry or production promotion was attempted.

## Gate 10 accounting

| Criterion | State |
|---:|---|
| 8 | OPEN — owner-host secret injection |
| 20 | OPEN — Firebase external acceptance |
| 25 | OPEN — owner-host Redis TLS/ACL/persistence |
| 30 | OPEN — target restore drill |
| 31 | OPEN — off-host backup/key custody |
| 34 | OPEN — target persistent volume |
| 35 | OPEN — target HTTPS/backend secret injection |
| 36 | OPEN — WSS maximum lifetime, Android, fan-out and operational acceptance |
| 38 | OPEN — durable self-hosted metrics/logs/dashboard |
| 39 | OPEN — host alert collection/escalation/recovery drill |

**Stage 1:** 30/40 provisional criteria = 300/400 ticks = **75% provisional**.  
**Gate 10:** 0/10 formally closed.  
**Stages 2–6:** NOT SCORED.  
**Overall project:** 20.9% remains historical only; no fresh overall score is asserted.

No progress ticks are awarded for workflow refactoring, CI diagnostics, or documentation alone.

## Zero-cost and device impact

- No paid plan, billing activation, external data provider, or subscription.
- No Termux install or command required.
- No command or code edit required from the owner.
- `main` remains untouched.


## Additional Vercel read-back (2026-11-18)

The team plan was read back as Hobby. Two latest listed branch previews are READY:
- WSS POC deployment `dpl_7HQmpEAPpxnvcSQFz8umK7u1kf71`, source `001e142d3981cea99bed5da957d266af6261b2dc`, Python 3.12 build completed, preview URL `https://dezzta-chart-ws-8pyssexdc-deszztagd377-pixel.vercel.app`.
- Vite frontend deployment `dpl_Ejcq4EaG2dWnFoeDLza8s8wqeUcB`, source `9e654a842f4e320d775fd8cb3489af65eb700376`, Vite 6.4.5 build completed with 1,526 modules, preview URL `https://dezzta-chart-eg6ipi7za-deszztagd377-pixel.vercel.app`.

These successful deployments supersede the blanket impression that every current preview is blocked by build-rate-limit, but their source commits predate the latest Batch 8 workflow/test changes. They are previews, not production. No new deployment was initiated, no plan upgrade/billing occurred, and they do not close Gate 36.
