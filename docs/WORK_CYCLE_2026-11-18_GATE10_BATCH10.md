# DEZZTA CHART — Work Cycle 2026-11-18 — Gate 10 Batch 10

## Scope

Continue Stage 1 Gate 10 on `phase-2/market-data-foundation`, prioritizing WebSocket correctness, regression protection, accurate progress documentation and zero-cost operation.

## Work completed

### 1. WebSocket idle-timeout lifecycle race corrected

A fresh source audit found that the browser handler immediately called `setState("Server closed idle session", false)` upon receiving the server's `idle_timeout` message. The server sends that message before its close frame; therefore the UI could report disconnected before the browser's actual `close` event.

Correction in `poc/vercel_ws/index.py`:
- Keep the socket in its current in-flight state after the `idle_timeout` message.
- Display **“Idle timeout — waiting for close”**.
- Let the existing `close` event handler be the authoritative state transition.

This aligns idle-timeout handling with the already-corrected transport-error handling and prevents premature UI state changes.

### 2. Regression contract strengthened

In `backend/tests/test_vercel_ws_probe_contract.py`:
- Assert the idle-timeout handler does not call the old premature disconnected-state transition.
- Assert it reports the waiting-for-close status.
- Make the source-block extraction deterministic rather than relying on a fragile escaped regex.

The test is committed and read back, but has **not** been executed in a verified exact-head CI run. No pass is claimed.

## Exact changed files

1. `poc/vercel_ws/index.py`
2. `backend/tests/test_vercel_ws_probe_contract.py`

## Commit chain

- `8e43e8f0975130a96f4858df69d4d487a5bf97d8` — source correction.
- `b804a23147316483589883d66d6cd2c1c13c7274` — initial idle-timeout regression assertion.
- `84d30fdb81e13dc16083b60346b8cdba83d2956e` — deterministic block extraction.
- `21e76a2a2c45e0462a9c6e99d3c1c42b17b5eed7` — corrected block boundary.

## Gate 10 and Stage 1 accounting

No external acceptance criterion was closed by this repository-only change.

- Stage 1: **300/400 ticks = 75% provisional**.
- Stage 1 provisional criteria: **30/40**.
- Gate 10: **0/10 formally closed**.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- No fresh overall-project percentage is asserted.

## Deployment and CI boundary

- Latest READY WSS preview remains an older source revision; this Batch 10 correction is not deployment-verified.
- Latest READY frontend preview is also an older source revision.
- No new Vercel deployment was triggered in this source-only cycle.
- The current npm audit High `picomatch@4.0.7` blocker remains unresolved; no suppression, unsafe override or forced downgrade was used.
- Exact-head push-triggered GitHub Actions evidence is unavailable through the currently exposed connector route; test execution is therefore unverified.
- The 330-second synthetic probe remains unobserved end-to-end.

## Zero-cost / safety ledger

- No paid service, upgrade, billing activation or data provider.
- No production deployment or promotion.
- No SSO/security weakening.
- No Termux installation or command.
- `main` untouched.
- No code or document repair delegated to the owner.

## Current progress artifacts

- [Current colored project progress indicator](PROJECT_PROGRESS_INDICATOR_CURRENT.md)
- [Stage 1 Gate 10 acceptance addendum](STAGE_1_GATE10_BATCH10_ACCEPTANCE_ADDENDUM.md)
- Dashboard SVG: [project-progress-dashboard-batch10.svg](assets/project-progress-dashboard-batch10.svg)
