# DEZZTA CHART — Batch 35: WebSocket client/server heartbeat contract tests

**Date:** 18 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Parent exact HEAD:** `62678abfa16b59c7927f94ad19fe4f8552982f15`  
**Scope:** server route integration tests for client heartbeat, unsupported control-frame rejection, protocol documentation, full progress indicator  
**Cost:** ZERO COST  
**Deployment:** none  
**Main:** untouched

## 1. Batch 34 exact-head CI result

The prior commit `62678abfa16b59c7927f94ad19fe4f8552982f15` has terminal CI results:
- Automated Tests [44310352740](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310352740): **FAILURE only at final step** `Enforce frontend dependency audit result`. All preceding steps passed, including frontend unit tests/build, credential scans, Android host preflight/publisher tests, backend tests, synthetic SQLite outbox benchmark, backend dependency audit, backend container build, Redis/persistent-volume smoke, Trivy scan and report export.
- Android debug APK Build [44310351406](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310351406): **SUCCESS**. The workflow assembled and verified a debug APK artifact in CI; no immutable preview release was published.
- CodeQL [44310351525](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310351525): **SUCCESS**.
- Full Git History Secret Audit [44310351555](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310351555): **SUCCESS**.

The Automated Tests failure remains the five High dev-tool dependency paths through `picomatch@4.0.7` (GHSA-fc5q-39xc-vjpf / CVE-2026-112366). No audit waiver, suppression, forced downgrade, speculative override, or hand-patched package is introduced.

## 2. Additional gap found and test coverage added

Batch 34 covered the frontend heartbeat timer and timeout, but the backend route did not yet have an integration test exercising the literal client text frame against the actual FastAPI WebSocket handler.

This batch adds two backend route integration tests:
- Authenticated subscription → initial snapshot → literal text `ping` → exact JSON `market_data.pong` version 1.
- Authenticated subscription → unsupported text control frame → server closes with policy code 1008.

These tests validate the actual in-process route handler, not merely the isolated rate-limit helper. No production route behavior was changed.

## 3. Heartbeat rate calculation

- Client default: 1 ping / 20 seconds = 0.05 ping/second.
- Server ceiling: 20 pings / 10 seconds = 2 pings/second.
- Relative rate: 0.05 / 2 = 0.025 = **2.5%** of the server ceiling.
- Client pong deadline: 10 seconds, half the send interval.
- The client stops heartbeat timers on failure, remote close, and explicit stop.

The low steady-state rate leaves substantial margin below the server's rolling-window limit.

## 4. Gate 36 acceptance boundary

Source-level heartbeat behavior is now covered on both sides of the contract. Gate 36 remains OPEN because repository tests do not establish:
- real public WSS Upgrade and ping/pong on the target host;
- Android WebView acceptance and foreground/background/network transitions;
- owner-observed 330-second session and platform close attribution;
- effective Fluid Compute configuration read-back;
- cross-instance live fan-out (subscriber queues remain process-local).

No deployment or hosting change was performed.

## 5. Progress accounting — unchanged

- Stage 1: **75% provisional** = 300/400 ticks = 30/40 criteria.
- Gate 10: **0/10 formally closed**.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; approved M1–M8 weights and criterion mapping remain absent.
- Historical overall checkpoint: **20.9% — historical only, not recomputed**.

No Stage 1 tick or gate closure is awarded by adding tests alone.

## 6. Zero-cost and owner-device boundary

No Vercel deployment/retry, Cloudflare resource, paid broker, provider, database, host, storage, billing/plan change, or publication action. Termux is not required for these source and CI tests. If future Android-native WSS acceptance genuinely requires Termux, explain why before asking for owner action.

## 7. Files in this batch

- `backend/tests/test_api.py` — actual FastAPI WebSocket heartbeat round-trip and unsupported control-frame rejection tests.
- `docs/OHLCV_STREAM_PROTOCOL.md` — client/server heartbeat contract, rate calculation, and remaining external acceptance.
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md` — exact parent CI outcomes and unchanged conservative progress.
- `docs/assets/project-progress-dashboard-batch35.svg` — colored six-stage project dashboard.
- `docs/WORK_CYCLE_2026-11-18_BATCH35_WEBSOCKET_HEARTBEAT_INTEGRATION.md` — this audit record.
