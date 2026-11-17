# DEZZTA CHART — Gate 10 Batch 5: Vercel WebSocket build-context verification

Date: 2026-11-17  
Branch: `phase-2/market-data-foundation`  
Base HEAD: `2733c80f6958f4599a92365db4e753c2264e45e2`  
Scope: read-only Vercel project/deployment/build-log audit plus documentation updates

## Findings

- Vercel team context: `deszztagd377-pixel's projects`, plan **Hobby**.
- Dedicated FastAPI POC project: `dezzta-chart-ws-poc`, ID `prj_yVSD5vtqiPxpSYBGE6hxXDRCIWs2`.
- Latest deployment observed: `dpl_39dRJ6Ki9gU1PrXcN8YU4kQ7zCzW`, **READY**, branch `phase-2/market-data-foundation`, source commit `b789e229290290c91143077449a83ec94098162f`.
- SSO protection: **enabled for all deployment targets**.
- Build log explicitly confirms Python 3.12 was loaded from `poc/vercel_ws/.python-version` and dependencies from `poc/vercel_ws/requirements.txt`. The expected Root Directory/build context is now **verified** by actual build evidence.
- Project settings response does not include effective `resourceConfig.fluid`. The repository's `fluid: true` declaration is not treated as runtime read-back. Effective Fluid Compute remains **unverified**.
- Latest-deployment runtime-log query over the preceding 50 minutes returned no records. No log records are not evidence of a failed connection or a successful WSS test.

## Gate 36 disposition

The root build-context sub-check is now PASS, and all-target SSO is verified. Gate 36 overall remains OPEN pending maximum-duration behavior, independent effective Fluid Compute verification, Android Capacitor WebView WSS against a compatible authenticated backend, production cross-instance fan-out, and cost/operational acceptance.

No Stage 1 ticks are awarded for this partial sub-check.

## Repository updates

- Updated the top-level progress snapshot and project status.
- Added the latest deployment/build evidence to the WebSocket POC guide and Gate 36 audit.
- Updated the colored ten-gate dashboard to distinguish verified build context from unresolved Fluid Compute/Android WSS.

## Stage and cost accounting

- Stage 1: **300/400 = 75% provisional**.
- Gate 10: **0/10 formally closed**; open criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: **NOT SCORED**.
- ZERO COST preserved. No settings were changed, no deployment was created, no paid service/billing was activated, no credentials were accessed, and no Termux change was made.
- Protected `main` untouched.
