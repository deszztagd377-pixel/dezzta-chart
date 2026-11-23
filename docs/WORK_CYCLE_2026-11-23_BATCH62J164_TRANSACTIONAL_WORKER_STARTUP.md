# WORK CYCLE — Batch 62J-164: Transactional Redis Worker Startup

Date: 23 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent/source HEAD: `36447981ae4d8c3535a47c391c5140f72abe6ac2`  
Scope: WebSocket replica worker lifecycle only. No provider/API contract, indicator formula, UI, deployment, paid service, or main-branch changes.

## Verified predecessor

Batch 62J-163 commit `36447981ae4d8c3535a47c391c5140f72abe6ac2` passed all four exact-HEAD workflows:
- Automated Tests: SUCCESS — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45105218629
- CodeQL Security Analysis: SUCCESS — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45105218575
- OCI ARM64 Image Readiness: SUCCESS — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45105218600
- Full Git History Secret Audit: SUCCESS — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45105218539

This proves CI for the source commit only; it does not prove public WSS, an OCI tenancy/VM deployment, production market-data entitlement, or Android-device acceptance.

## Finding

The worker previously set state to `starting` and invoked `ownership_lease.start_heartbeat()` before creating its consumer thread. If lease initialization raised (for example, temporary Redis unavailability), the exception propagated while the worker remained in a misleading `starting` state. If thread startup failed after heartbeat startup, the lease heartbeat could remain active without a consumer thread.

## Change

- Make worker startup transactional.
- On startup exception, signal stop, stop an already-started heartbeat on a best-effort basis, clear the thread reference, retain the exception type, and restore a truthful terminal state.
- Preserve `ownership_lost` when the startup exception is `RedisOhlcvConsumerLeaseLost`; ordinary startup infrastructure failures return to `stopped` with the diagnostic error type.
- Add regression tests for temporary lease unavailability and terminal ownership loss before consumer thread startup.

## Acceptance and safety

- No event consumption begins if lease heartbeat startup fails.
- No phantom `starting` state remains after startup failure.
- An already-started heartbeat is cleaned up if later thread startup fails.
- Ownership loss remains distinguishable from a clean stop.
- Existing bounded retry, resnapshot-required, stop timeout, and lease-loss behavior remains unchanged.
- No external network/service or paid resource is introduced.

## Test evidence

Two focused regression tests were added. Their status is PENDING exact-HEAD CI until GitHub Actions reports the resulting commit successful. No local test execution is claimed in this report.

## Changed files

1. `backend/app/ohlcv_redis_worker.py`
2. `backend/tests/test_ohlcv_redis_worker_lifecycle.py`
3. `docs/WORK_CYCLE_2026-11-23_BATCH62J164_TRANSACTIONAL_WORKER_STARTUP.md`
4. `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
5. `docs/INDICATOR_PROGRESS_LEDGER.md`

## Indicator and project accounting

No indicator implementation, calculation, hook, renderer, or UI changed. Indicator implementation credit: **0**. Keep SMA20, EMA20, RSI14 Wilder, MACD12/26/9 and Bollinger20,2 at 🟨 foundation; shared indicator hook 🟨; Footprint 🟧 prototype/reference-gated; Heatmap 🟥; Liquidation Maps 🟥. Aggregate indicator progress remains NOT SCORED.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 remain NOT SCORED/not officially opened. Gate 10 remains 0/10 external criteria formally closed. Overall project remains NOT SCORED because approved stage weights and a denominator are unavailable.

## ZERO COST / scope

No paid provider, credential, cloud resource, hosting, domain, TLS certificate, payment method, or device operation was used. `main` remains untouched. Active branch only: `phase-2/market-data-foundation`.

## Required follow-up

After exact-HEAD CI, inspect failures and repair before acceptance. Next WebSocket work remains snapshot distribution integrity and two independent ASGI gateway end-to-end replay/fan-out acceptance. Dynamic upstream market-data demand remains blocked on a verified recurring-$0 provider API and redistribution rights. OCI ARM64 image readiness must not be represented as cloud deployment.
