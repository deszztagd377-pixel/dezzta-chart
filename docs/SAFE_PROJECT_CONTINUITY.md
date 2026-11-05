# DEZZTA CHART — Safe Project Continuity Checkpoint

Checkpoint date: 2026-11-05
Repository: https://github.com/deszztagd377-pixel/dezzta-chart
Working branch: `phase-2/market-data-foundation`
Last verified working-branch HEAD at checkpoint: `4ca3243957991a9da4d22b2c8674b661dd456c55`
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
- The frontend has an authenticated WebSocket transport module, but it is not yet connected end-to-end to Firebase token lifecycle, chart lifecycle, and shared chart state.
- The backend broadcaster is not a durable event log and does not replay missed updates.
- No live provider session, real provider delivery, synchronized exchange clock, or production feed freshness has been verified.
- CI workflow runs frontend tests, frontend production build, backend pytest, and backend container image build.
- Last known successful run on the current branch head: run 42050582571, commit `4ca3243957991a9da4d22b2c8674b661dd456c55`.
- CME session calendar document is an accepted design only. Calendar implementation and related migrations have not started.

## Progress accounting discrepancy — do not silently overwrite

- The user recalls the latest conversational checkpoint as **20.9%**.
- `PROJECT_STATUS.md` currently records **19.60%**, with last audited date 2026-11-04.
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
