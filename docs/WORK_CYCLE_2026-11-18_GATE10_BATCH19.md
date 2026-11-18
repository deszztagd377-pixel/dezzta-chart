# Work Cycle Batch 19 — WebSocket protocol coverage and full progress accounting

**Date:** 18 November 2026  
**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Parent:** `362ff6ed2a492383fc0d9ee2ce2f284146004b3d`  
**Zero cost:** maintained • no Termux • no billing • no production promotion

## 1. WebSocket work

Added `backend/tests/test_vercel_ws_protocol.py`, using FastAPI TestClient to exercise the synthetic POC through an actual ASGI WebSocket session. Five contracts:
- handshake, ready/session ID and ping/pong sequence round-trip;
- invalid message => error and close 1003;
- oversized message => error and close 1009;
- 12 messages/10 seconds accepted, next message rate-limited and closed 1013;
- health endpoint => HTTP 200 and explicit synthetic-only / production-data-disconnected result.

This is a stronger executable protocol contract than source-regex assertions. It is still not a public Vercel browser WSS observation. Gate 36 remains open until deployment-level and Android evidence exists.

## 2. CI read-back before this commit

Run [44288721128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721128) was still in progress at last read. Backend pytest and earlier frontend, credential scans, Android checks, outbox benchmark, backend dependency audit had passed; Docker image build was running. CodeQL [44288721099](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721099) passed. Full history secret scan [44288721127](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721127) passed.

## 3. Root dependency analysis

Lockfile confirms:
- `picomatch@4.0.7` is `dev: true`;
- transitive parents: `tinyglobby@0.2.17`, `vite@6.4.5`, `vitest@4.1.12`, all development-only.
- GHSA-fc5q-39xc-vjpf still says High and no patched version is listed. The upstream issue #247 remains open.

No safe override exists to apply. Downgrading to 4.0.4 is not a valid fix for this distinct later advisory. npm audit enforcement remains fail-closed; no suppressions or fake patched version.

## 4. Vercel blocker

Commit `362ff6e` has both Vercel status contexts fail with “Deployment rate limited — retry in 24 hours.” No retry loop, paid upgrade, billing, SSO change, or production promotion. Preview URLs from older source commits are not represented as current-head READY deployments.

## 5. Project progress

- Stage 1: 75% provisional, 300/400 ticks, 30/40 provisional criteria.
- Gate 10: 0/10 formally closed; open criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: not scored.
- Overall current percentage: not established. M1–M8 weighting and criterion mapping are not approved/scored. Historical 20.9% is displayed as historical only.

No Gate closure or tick increase is claimed from these tests. `main` untouched. No Termux required.
