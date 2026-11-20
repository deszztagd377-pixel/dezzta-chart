# Work Cycle 62J-24 — replica runtime readiness hardening

**Date:** 20 November 2026  
**Branch:** phase-2/market-data-foundation  
**Parent code:** 491c50198620b290e1a7ef9d0f5e5d8a0410e6f1  
**Scope:** Redis consumer-group startup readiness and exact series test fixture.

## Changes

1. Replica consumer contract now requires ensure_group().
2. FastAPI awaits ensure_group() after atomic snapshot hydration and before dispatcher/worker startup. This verifies Redis connectivity and consumer group readiness before the app accepts traffic.
3. A Redis group-bootstrap failure aborts lifespan startup; the injected Redis client is closed during cleanup and no worker is started.
4. Added regression coverage for successful group bootstrap and fail-closed behavior during a simulated Redis outage.
5. Corrected the 1-second replica snapshot fixture to UTC_FIXED_V1, the policy selected by bucket_policy_for_timeframe('1s').
6. Removed duplicate replay-state initialization introduced during the previous integration patch.

## CI failure analysis

Batch 62J-23 Automated Tests reported 1,160 passed and one failure. The failed assertion expected one snapshot bar but the test fixture stored it under UTC_LEGACY while the WebSocket request canonicalized 1s to UTC_FIXED_V1. The exact-series query correctly returned zero rows. The fixture now uses the canonical policy; the runtime was not changed to weaken exact-series matching.

## Safety

- Source SQLite remains the default; replica mode remains explicit factory injection only.
- Startup now fails closed if the verified snapshot or Redis consumer group is unavailable.
- No mixed source/replica cursor domain.
- No paid infrastructure, deploy, main branch modification or Termux.
- All ten gates remain 🟧 ORANGE / OPEN, 0/10 closed.
- Indicator implementation statuses unchanged.

CI must pass on the exact resulting commit before this batch is considered verified.
