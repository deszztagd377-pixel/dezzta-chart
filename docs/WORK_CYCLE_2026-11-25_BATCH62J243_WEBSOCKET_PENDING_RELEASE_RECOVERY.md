# Work Cycle 62J-243 — Offline WebSocket pending-release recovery

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Exact source/test HEAD: `b60a9d375a9b3d9742c0c4e1c107aff593ad7ebc`  
Previous source checkpoint: `65bf9203b2521846ddbac6206202d302a9fc81b8`

## Problem

A failed final adapter stop deliberately retained the last demand lease. The previous bounded three-attempt retry recovered transient errors, but a persistent failure left a disconnected subscriber's lease registered with no automatic retry path.

## Source changes

- `backend/app/provider_demand.py`
  - bounded retry policy (1–10 attempts; finite non-negative delay);
  - pending-release ID queue for failed final release;
  - pending reconciliation method;
  - cancellation during adapter stop or backoff queues the retained lease;
  - successful release clears the pending marker.
- `backend/app/main.py`
  - FastAPI lifespan starts a one-second pending-release reconciliation task;
  - graceful shutdown signals and joins the worker with a two-second deadline;
  - WebSocket disconnect path uses bounded retry.
- `backend/tests/test_provider_demand.py`
  - transient and persistent stop failures;
  - retry policy validation;
  - recovery after persistent failure;
  - persistent failure remains queued;
  - cancellation during adapter stop;
  - cancellation during retry backoff.
- `backend/tests/test_api.py`
  - authenticated route/lifespan test verifies persistent disconnect cleanup failure is queued and later recovered by the app-lifespan worker.

## Exact-HEAD CI evidence

All four workflows completed successfully on the exact source/test SHA `b60a9d375a9b3d9742c0c4e1c107aff593ad7ebc`:

- Automated Tests run 45536261384: 41/41 steps SUCCESS.
- CodeQL run 45536261374: Python 8/8 and JavaScript/TypeScript 8/8 SUCCESS.
- OCI ARM64 run 45536261564: 7/7 steps SUCCESS.
- Full Git History Secret Audit run 45536261385: 6/6 steps SUCCESS.

Backend pytest: 1,419 passed, 1 skipped, 6 warnings in 64.27s. The one skipped test is `tests/test_shared_guard_tls_integration.py:22` because its isolated Redis TLS fixture was not configured in that pytest invocation. The separate CI Redis TLS CA/hostname enforcement step passed.

The workflow also passed frontend tests/build, backend dependency audit, container build, container smoke tests and generated/uploaded the container vulnerability report. The report was not interpreted as a clean scan without inspection.

## Acceptance boundary

This is in-process recovery for the explicitly offline-fixture adapter only. Pending state is not durable across process restart. It does not prove external provider lifecycle, dynamic provider ACK, production multi-host ownership, Gate 25, public Gate 36 or Android device E2E. No paid service or live market-data provider was enabled.

## Indicator status

No indicator source was changed. Calculation foundations and chart-integration gaps remain exactly as recorded in `INDICATOR_PROGRESS_LEDGER.md`. `INDICATOR_UI_BLUEPRINT.md` remains parked for official Stage 4.

ZERO COST maintained. No deployment, Vercel action or main-branch update.
