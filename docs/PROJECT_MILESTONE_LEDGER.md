# DEZZTA CHART — Proposed Weighted Milestone Ledger

Status: **proposed accounting model; owner review required before publishing a newly calculated overall percentage**  
Last audited: 2026-11-05  
Branch audited: `phase-2/market-data-foundation`  
Main HEAD at audit: `e3841681bc69b73619058deaf939df82ae5116a1`

## Purpose and calculation rule

This ledger defines the complete milestone groups used to measure progress toward the agreed educational chart application. The weights total exactly 100%. A milestone receives credit only for verified, working deliverables. A design document, planned feature, code stub, passing unrelated CI job, or duplicate implementation reference does not count as a completed user-visible capability.

For each milestone group:

`earned points = group weight × verified completion fraction`

Overall progress is the sum of earned points across all groups. Each group must list acceptance criteria and evidence. Partial completion must be justified criterion-by-criterion; no automatic credit is given for code volume or commit count.

**Important:** this is a proposed weight model, not yet an approved or recalculated current percentage. It does not retrospectively prove the 20.3% or 20.9% conversational checkpoints. Those remain preserved historical checkpoints until the previous calculation can be recovered.

## Milestone groups (100% total)

| ID | Milestone group | Weight | Acceptance boundary |
|---|---|---:|---|
| M1 | Application shell and core chart rendering | 15% | App boots reliably; chart renders clearly labelled demo data; navigation and chart lifecycle behave correctly |
| M2 | Data contracts, validation, and persistence foundation | 20% | Versioned DTOs, exact series identity, validated snapshots, durable local storage semantics, restart and gap-state tests; no claim of external/live delivery |
| M3 | Authentication and application security foundation | 10% | Secure sign-in/session handling, server-side identity verification, authorization boundaries, secret hygiene, and tested failure paths |
| M4 | Chart interaction and educational drawing/measurement tools | 15% | Timeframe behavior is honest, chart navigation/touch interactions work, measurement and annotation tools have undo/redo and tests |
| M5 | Educational indicator and mathematical visualization layer | 15% | Approved non-predictive educational calculations are visibly integrated, explained, timeframe-tested, and do not produce buy/sell advice |
| M6 | Responsive UX, accessibility, and visual design | 10% | Mobile-first layouts, accessible controls/states, orientation/viewport behavior, and owner-approved visual acceptance |
| M7 | Watchlist, settings, and user preference persistence | 5% | User-facing settings and watchlist behaviors work and persist with clear offline/demo states |
| M8 | Quality engineering, reproducible builds, and release readiness | 10% | Regression coverage, deterministic dependency installation, CI, error handling, documentation, security checks, and verified Android/web release packaging |
|  | **Total** | **100%** |  |

## Evidence inventory at the 2026-11-05 audit

| Group | Verified evidence | Missing / not yet accepted | Ledger treatment |
|---|---|---|---|
| M1 | React/TypeScript/Vite shell; Lightweight Charts v5; Chart/Watchlist/Settings navigation; labelled demo candles; chart lifecycle and interaction configuration | Full user-facing chart workflow and broader visual acceptance | Partial; criterion-level score not assigned |
| M2 | Versioned OHLCV DTOs; exact-series validation; backend snapshot and stream contracts; SQLite instrument/metadata/OHLCV/coverage persistence; restart and gap-recovery tests; protocol documentation reconciled with the verified frontend integration boundary | Deployed end-to-end operation and external source delivery are not verified | Partial; count implemented contracts and persistence only |
| M3 | Firebase token flow in frontend; server-side identity and entitlement checks; authenticated stream integration at code level | Deployed auth configuration, operational security review, and production behavior not verified | Partial |
| M4 | Zoom/scroll/pinch/crosshair behavior; timeframe selector; component-level selector tests | Most intervals are disabled because current visible fixture is daily; drawing/measurement tools not implemented | Early partial |
| M5 | Pure SMA, EMA, RSI, MACD, and Bollinger calculation functions with tests | Indicator hook is not wired to visible chart UI; no approved visible educational indicator panel | Calculation groundwork only |
| M6 | Responsive chart lifecycle and some viewport/touch foundations | Physical Android device acceptance, complete accessibility review, and final visual redesign | Partial / unverified |
| M7 | Offline read-only ES/NQ/GC catalog fixture; grid preference and reset behavior | Persistent layouts, expanded settings, editable watchlist behavior | Partial |
| M8 | GitHub Actions frontend tests/build, backend tests, and container build; latest audited commit `e19a3e3a8f926bdb68f0b2eb2fa59be5a5318c19` passed workflow run [#42056143166](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42056143166) | Root package lockfile and clean-install migration; dependency/security scanning; Android packaging and release validation | Partial |

## Non-duplication rules

1. One deliverable is assigned to one primary milestone group only.
2. A backend contract and its frontend adapter may be separate acceptance criteria only when each independently provides a distinct verified capability.
3. Tests increase confidence in the implementation criterion; they do not count as a second copy of the feature.
4. A design/ADR records intent, not implementation completion.
5. Deployment, external data delivery, device validation, and production performance receive no credit without direct evidence.
6. A feature that exists only as a calculation helper does not receive visible-UI completion credit.
7. DEMO fixtures must remain explicitly labelled and never be counted as external/live data.

## Historical checkpoint reconciliation

- **19.60%**: older formally recorded weighted estimate in `PROJECT_STATUS.md`; not a verified regression.
- **20.30% → 20.90%**: owner-confirmed historical conversational sequence; 20.90% is the latest such checkpoint.
- **19.90%**: no reproducible calculation located; do not use as a current estimate.
- **Current recalculated percentage**: pending owner review of this proposed weighting model and criterion-level scoring. Do not silently substitute any historical value.

## Approval and next scoring procedure

1. Owner reviews/approves the 8 group weights, or requests adjustments.
2. Audit each criterion against the branch-head source and exact CI run.
3. Mark each criterion: complete, partial, blocked, planned, or unverified.
4. Assign a completion fraction with a short evidence note and no double counting.
5. Calculate earned points with the formula above.
6. Record the result and exact HEAD/CI evidence in `docs/PROJECT_PROGRESS.md` and `PROJECT_STATUS.md`.

Major UI/feature expansion gate: **40%**. At that gate, prepare a scoped blueprint and obtain owner review before large implementation.
