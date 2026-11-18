# DEZZTA CHART — Work Cycle 2026-11-18 — Gate 10 Batch 12

## Objective

Advance the WebSocket POC with stronger measurement integrity, strengthen protocol regression checks, and update the process progress indicator using exact-head CI and Vercel evidence. Zero cost; active branch only.

## WebSocket engineering changes

Files changed:
- poc/vercel_ws/index.py
- backend/tests/test_vercel_ws_probe_contract.py
- backend/tests/test_vercel_ws_poc.py

Changes:
- The 330-second probe now explicitly invalidates itself if the browser page becomes hidden while the probe is running.
- The invalidation stops both probe timers and closes the active socket with a dedicated reason. This avoids treating a background-tab timer-throttled interval as a valid platform-duration observation.
- The page explains that the probe must remain visible.
- WebSocket protocol tests now assert close codes for oversized messages (1009), invalid message shapes (1003), rate limiting (1013), and idle timeout (1000).

Safety boundary:
- Synthetic-only; no market data, credentials, production worker, Redis, or database is connected to the POC.
- The 330-second probe remains opt-in.
- No actual platform-originated 300-second close is claimed.
- Native Android WebView WSS remains untested.

## Exact-head CI evidence

Run [44270272294](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44270272294) completed FAILURE, but only the final frontend dependency audit enforcement step failed.

Successful:
- Frontend tests/build and secret scans.
- Android preflight and release publisher tests.
- All backend pytest tests.
- Synthetic SQLite outbox benchmark and artifact upload.
- Backend dependency audit.
- Docker build and Redis ACL/persistent-volume smoke test.
- Trivy scan: zero HIGH and zero CRITICAL findings in the uploaded backend image report.
- CodeQL [44270272422](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44270272422).
- Full Git History Secret Audit [44270272360](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44270272360).

Still blocked:
- Five High npm audit findings through dev-only picomatch@4.0.7. The published advisory has no fixed version and npm still lists 4.0.7 as latest. The forced downgrade suggestion is not a verified security fix. No suppression, waiver, override, or forced downgrade was made.

## Deployment evidence

For source commit 9feb6cca8a51f563cae199eb33a6f57402eb3237:
- WSS POC preview dpl_EFLLSev63hRMKu9FEbrVTCUtR8Vg: READY.
- Frontend preview dpl_9vazakEetH3VW4Qht3T5ymknWFdo: READY.
- WSS Vercel config sets fluid: true; effective runtime and platform duration still need observation.
- No production promotion.

## Gate 10 accounting

- Stage 1: 300/400 = 75% provisional, 30/40 criteria.
- Gate 10: 0/10 formally closed.
- Still open: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: NOT SCORED.
- No ticks awarded for code or CI improvements without the specified external acceptance evidence.

## Zero-cost and branch controls

- Active branch: phase-2/market-data-foundation.
- main untouched.
- No paid plan, billing activation, paid hosting, market-data subscription, or production promotion.
- No Termux required.
- No repair delegated to the project owner.