# DEZZTA CHART — Safe Project Continuity Checkpoint

Checkpoint date: 2026-11-05
Repository: https://github.com/deszztagd377-pixel/dezzta-chart
Working branch: `phase-2/market-data-foundation`
Last verified working-branch HEAD before this documentation update: `8ae99f5c5a11cdfb8b5d52acc1455a47259f194b`
Main branch HEAD at checkpoint: `e3841681bc69b73619058deaf939df82ae5116a1`

## Why this file exists

Preserve the verified project state and safe next steps across chat changes. This file supplements, and does not replace, `PROJECT_STATUS.md` or technical design records. It is not a claim that unimplemented features work.

## Branch and change-control rules

- Never commit to or modify `main`.
- Continue only on `phase-2/market-data-foundation` unless the project owner explicitly approves a different branch.
- Inspect current files and their actual imports/callers before changing them.
- Keep changes small, reviewable, and reversible.
- Preserve existing working chart behavior; do not replace working systems wholesale.
- Do not claim tests passed unless the latest branch-head CI run confirms it.
- Report exact changed paths, commit SHA, CI result, and remaining limitations at each checkpoint.
- Do not expose API keys, service-account JSON, passwords, or private credentials in chat or frontend files.

## Verified repository state

- Frontend: React 18, TypeScript 5, Vite 4, Lightweight Charts 5.
- Backend: FastAPI/Python 3.12 CI, SQLite persistence, OHLCV pipeline and authenticated transport components.
- Existing chart uses a clearly labelled local DEMO fixture unless a trusted backend snapshot is available.
- The frontend authenticated WebSocket path is now integrated at code level: `CandlestickChart` starts/stops `startOhlcvStreamSupervisor`, obtains Firebase ID tokens through `AuthProvider`, and consumes validated snapshots/updates from `marketDataStore`. This does not prove a deployed backend or live provider delivery.
- The backend broadcaster is not a durable event log and does not replay missed updates.
- No live provider session, real provider delivery, synchronized exchange clock, or production feed freshness has been verified.
- CI workflow runs frontend tests, frontend production build, backend pytest, and backend container image build.
- Latest verified successful run before this documentation update: run `42053572558`, exact commit `8ae99f5c5a11cdfb8b5d52acc1455a47259f194b`; frontend dependency installation, frontend tests/build, backend dependency installation/tests, and backend container-image build all passed.
- CME session calendar document is an accepted design only. Calendar implementation and related migrations have not started.

## Progress accounting discrepancy — do not silently overwrite

**Owner correction (2026-11-05):** The historical conversational sequence was **20.3% → 20.9%**. Preserve 20.9% as the latest owner-confirmed conversational checkpoint; 19.60% is an older formally documented estimate, not proof of a regression. No reproducible formula for the 20.3%/20.9% sequence has yet been recovered. 19.9% is not verified and must not be used as a current figure.

- The user recalls the latest conversational checkpoint as **20.9%**.
- `PROJECT_STATUS.md` records **19.60%** as the last formally weighted historical estimate; the dedicated `docs/PROJECT_PROGRESS.md` now preserves this alongside the owner's recalled **20.9%** and explains why no fresh reconciled percentage is yet justified.
- These are inconsistent records. Do not state either as a freshly verified current percentage until the milestone weights and completed deliverables are reconciled.
- Do not reduce the user's remembered checkpoint merely because the status file is stale; equally, do not inflate the official estimate without evidence.
- Next progress audit must compare milestone definitions, verified commits, test evidence, and actual user-visible deliverables, then update the canonical status document with an explanation of the discrepancy.

## Preserved UI/product preferences

These are design preferences for a general educational chart interface, not a promise that every feature is implemented:

- Compact DEZZTA branding; avoid an oversized title/header.
- Dark visual theme, restrained gradients, clear chart prominence, compact controls, and bottom navigation.
- Preserve the current chart's zoom, scroll, crosshair, touch, and responsive lifecycle behavior.
- Normal candles retain normal spacing in the default chart.
- Candle countdown, if ever added to a general chart, must derive from the selected interval boundary and clearly identify whether it uses device time; never imply synchronized exchange time without evidence.
- Avoid decorative controls that do not work. Every visible control must have a real, tested behavior or be clearly marked unavailable.
- Prioritize mobile layout and regression checks, including safe-area handling and touch interactions.
- User has Android-only development access; instructions and verification steps should be usable from GitHub mobile.

## Safe development scope for future work

Continue only with general educational charting and software quality work that does not facilitate real-money trading or speculative futures activity. Suitable work includes:

1. Audit and reconcile the project progress ledger.
2. Improve chart layout, responsive behavior, touch interaction, accessibility, and error/loading states.
3. Improve the clearly labelled offline/demo chart fixture and its validation; never represent demo values as live.
4. Add neutral chart navigation and drawing/measurement utilities using demo data, with tests.
5. Improve frontend/backend-independent data-contract validation using fixtures only, without connecting to a live trading feed.
6. Improve app reliability, test coverage, build reproducibility, documentation, and secure configuration handling.

Do not implement or activate live futures market feeds, real-time order-flow features, brokerage/order execution, trade recommendations/signals, or other functionality that directly facilitates speculative trading. Do not claim zero latency, zero lag, manipulation-free execution, or production readiness. Do not add credentials or enable provider flags.

## Next safe stage

**Stage A — Progress and regression audit (documentation/tests only):**
- Reconcile the 20.9% conversational checkpoint against the 19.60% status-file value.
- Inspect the current branch head and recent commits rather than relying on old chat snippets.
- Confirm the current CI result for the exact HEAD.
- Produce a verified inventory of working frontend features, missing UI behavior, and known limitations.
- Make no chart architecture or backend provider changes during this audit.
- After the audit, choose one small, user-visible educational-chart improvement and implement it behind tests.

## Required checkpoint report format

- Branch and HEAD SHA
- Main SHA (confirm unchanged)
- Files changed
- Tests/CI status tied to exact commit
- Verified behavior added or corrected
- Known limitations and unverified assumptions
- Progress estimate and explicit evidence for any change


## UI and feature expansion gate — owner clarification (2026-11-05)

The owner has revised the major UI reconstruction and broad feature-expansion gate to **40% overall project progress**. Do not begin the large phase before that checkpoint.

At the 40% gate, first prepare a scoped UI/feature blueprint and review it with the owner before large implementation. The target direction is a polished, mobile-first educational chart application with compact DEZZTA branding, dark palette, restrained gradients, chart prominence, compact navigation/toolbars, and genuinely working controls. Feature work must be incremental, testable, and based on the verified capabilities of the existing code.

The current stage must not prematurely redesign the whole UI or add a large indicator catalogue. It should establish a reliable, clearly labelled demo/educational foundation, audit existing modules, close regressions, and improve maintainability. The 40% milestone is a project planning gate, not a promise that every feature will be complete at that percentage.

Existing-code audit findings from branch HEAD 7d6b8bac58a8e344055cc9605199bca998c84ae8:

- `src/App.tsx` currently wires Chart, Watchlist, and Settings navigation; timeframe state; and the grid-visibility preference.
- `src/components/TimeframeSelector.tsx` intentionally enables only the daily sample interval. Other displayed intervals are disabled because matching verified datasets are unavailable.
- `src/indicators/indicatorCalculations.ts` contains tested SMA, EMA, RSI, MACD, and Bollinger calculations. These calculations are not evidence of a completed indicator UI.
- `src/indicators/useMarketIndicators.ts` returns no indicator series for DEMO/loading/unavailable/error states and only calculates when a validated backend snapshot is ready/degraded. It is not currently wired into `src/App.tsx` or the visible chart component.
- `src/components/CandlestickChart.tsx` creates the Lightweight Charts candlestick chart and preserves chart lifecycle/resize handling; the visible default dataset remains a labelled demo fixture unless a validated backend snapshot is accepted.
- `src/components/BottomNav.tsx` provides Watchlist, Chart, and Settings navigation.
- The current verified CI workflow has one combined job covering frontend unit tests, frontend production build, backend tests, and backend container-image build.

Safe indicator/UI direction: any later educational indicator display must be explicitly identified as an educational visualization, use clearly labelled sample/demo data unless a separately reviewed safe data source is available, include explanatory context, and avoid buy/sell signals, trade recommendations, brokerage execution, or claims of predictive accuracy. Do not activate live speculative futures/order-flow feeds or implement Footprint/Heatmap/Liquidation Maps as trading tools.

## Latest audit checkpoint — 2026-11-05

- Working branch HEAD: `7d6b8bac58a8e344055cc9605199bca998c84ae8`.
- Main HEAD: `e3841681bc69b73619058deaf939df82ae5116a1` (unchanged).
- CI run `42051373564` completed successfully on the exact working-branch HEAD. Its Test and Build job passed frontend unit tests, frontend production build, backend tests, and backend container-image build.
- No source-code files were changed during this audit.
- Progress remains unreconciled: the status file's 19.60% and the owner's remembered 20.9% remain historical claims until the weighted milestone ledger is checked against actual commits and deliverables. Do not invent a new percentage from this audit alone.
- Next work: reconcile milestone accounting and audit frontend behavior/tests; make one small, reversible educational-chart improvement only after selecting a clearly testable issue. Preserve the revised 40% gate for the major UI/feature expansion.


## Stage audit — 2026-11-05 (10-minute focused work cadence)

- User preference: organize work into focused stages of approximately 10 minutes. Before each stage, explain the intended work; afterward report changed files, evidence, commit, CI, limitations, and any decisions requiring owner input. Do not claim exact elapsed time if not measured.
- User clarified that major UI reconstruction and broad feature expansion may begin at the 40% project-progress gate. Until then, focus on foundation quality, security, dependency hygiene, tests, performance, accessibility, Android responsiveness, architecture, error handling, and documentation.
- Source audit found that the old status statement saying frontend WebSocket was not connected had become stale. Current `CandlestickChart` integrates Firebase token retrieval, `startOhlcvStreamSupervisor`, shared `marketDataStore`, validated snapshot/update handling, and effect cleanup.
- `ohlcvStreamSupervisor` obtains a fresh token on reconnect and routes validated stream events into the store; `ohlcvWebSocketClient` validates the snapshot/watermark handshake and stream sequence.
- CI run `42051868901` passed on commit `551ae8da92175ca96d8a947fe35fcf782a698a87`. It passed frontend unit tests, frontend production build, backend tests, and backend container-image build.
- Updated `PROJECT_STATUS.md` in commit `1cb643d98818651c3a0adb1fc19fe113f8a18465` to correct the stale integration statement and record the verification boundary.
- Progress discrepancy remains open: repository's last formally weighted estimate is 19.60%; the user recalls 20.9%. The repository does not yet expose a reproducible milestone-weight ledger to justify either as a newly verified current percentage. Do not change the percentage until deliverables and weights are reconciled.
- No source-code or runtime behavior changed in this audit. No live provider, production deployment, real-time freshness, synchronized exchange clock, or zero-latency claim is verified.
- Current working branch after the status update: `1cb643d98818651c3a0adb1fc19fe113f8a18465`; `main` remains `e3841681bc69b73619058deaf939df82ae5116a1`.
- Next stage: reconcile the weighted progress ledger and review the frontend regression-test inventory. Select a small, safe educational-chart quality improvement only after identifying a concrete gap. Preserve the revised 40% gate.


## Focused-stage cadence update — 2026-11-05
- User expects each work stage to contain approximately 5–10 minutes of focused, substantive work, rather than stopping after one tiny action. Do not claim exact elapsed time unless measured.
- Before each stage, explain the objective and intended scope. Afterward, report the verified result, changed paths, commit SHA, exact CI status, remaining limitations, and progress-accounting impact.
- Latest confirmed CI at the previous HEAD: run `42053572558` passed on `8ae99f5c5a11cdfb8b5d52acc1455a47259f194b`.
- A dedicated progress record is now being added at `docs/PROJECT_PROGRESS.md`; it preserves 19.60% as the last formal historical estimate and 20.9% as the owner's recalled conversational checkpoint until a reproducible ledger is reconciled.
- The owner-approved major UI/feature expansion gate is now 40%, subject to a scoped blueprint and owner review.
