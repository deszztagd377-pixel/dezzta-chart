# DEZZTA CHART — Official Six-Stage Roadmap

Status: owner-agreed project sequence  
Working branch: `phase-2/market-data-foundation`  
Current official stage: **Stage 1 — Foundation, Security & Data Integrity**

## Stage sequence

| Stage | Name | Scope boundary |
|---:|---|---|
| 1 | Foundation, Security & Data Integrity | Application/backend foundations, identity and authorization, data contracts, persistence, security controls, integrity and acceptance evidence |
| 2 | Market Data Infrastructure | Provider-neutral market-data ingestion, instrument definitions, validated OHLCV delivery, stream reliability, coverage and freshness |
| 3 | Chart Engine & Timeframe | Chart rendering engine, timeframe behavior, synchronized chart data lifecycle, viewport and core chart interactions |
| 4 | Indicators & Analytics | Indicator calculations and their visible chart integration, analytics panes/overlays, timeframe compatibility, mathematical correctness and performance |
| 5 | Professional UI & Interactive Tools | Broader professional chart experience, drawing/measurement tools, advanced visual systems and owner-directed interface expansion |
| 6 | Hardening, Validation & APK Release | End-to-end regression, security/performance validation, device acceptance, release packaging and delivery |

## Current stage and branch naming

- Stage 1 remains the active official project stage until its acceptance requirements are satisfied.
- Stage 1 has **30/40 criteria = 300/400 ticks = 75% provisional**. Its ten external acceptance criteria remain open: **8, 20, 25, 30, 31, 34, 35, 36, 38 and 39**.
- The working branch name `phase-2/market-data-foundation` is a technical branch/workstream label. It does **not** by itself mean the official six-stage roadmap has advanced to Stage 2.
- Some Stage 2 market-data foundation code and documentation already exist on this branch. That work must not be used to silently waive Stage 1 acceptance or reorder the official roadmap.
- The overall project figure **20.9%** is a historical owner-confirmed checkpoint, not a newly recalculated weighted score. The proposed weighted ledger still needs owner review and reproducible scoring.

## Candle Replay — owner-requested future chart feature

- **Requested feature:** a TradingView-style historical candle replay mode in the Android app.
- **Roadmap placement:** Stage 3 — Chart Engine & Timeframe, as a chart interaction built on validated historical OHLCV. It is not the Redis/WebSocket durable event-replay mechanism already implemented for transport recovery.
- **Planned behavior for a future scoped blueprint:** choose a historical starting candle, hide all later candles from the visible chart, advance playback by one candle or at a bounded selectable speed, pause/resume, step backward/forward, seek along the historical timeline, and exit replay to restore the live chart without mixing replay and live cursors.
- **Data contract:** replay must use the same canonical instrument, venue/provider, dataset, timeframe, bucket/calendar identity and validated historical OHLCV contract as the normal chart. The playback cutoff is authoritative; no future candle may leak into chart, indicators or derived studies while replay is active.
- **Lifecycle:** switching instrument/timeframe or losing the historical dataset must stop or explicitly invalidate the replay session. Leaving replay must resynchronize from a fresh live snapshot/watermark rather than append live events onto a stale historical cursor.
- **Mobile/performance:** controls must be touch-usable on narrow Android screens; playback must be deterministic, bounded and cancellable. No per-tick network polling or paid service is assumed.
- **Safety/scope:** chart playback only. No broker connection, order execution, automated trading, signal generation or recommendation.
- **Authorization:** **NOT ACTIVE / NOT IMPLEMENTED** during Stage 1. Prepare and review the detailed interaction/data/performance blueprint when Stage 3 is reached and prerequisite historical-data capability is accepted. This request does not reorder the six-stage roadmap or award progress ticks.

## Indicator placement

- SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9 and Bollinger Bands 20,2 have calculation foundations and automated tests. This is groundwork only.
- **Visible indicator controls, overlays and oscillator panes belong to Stage 4 — Indicators & Analytics. They are not Stage 1 work.**
- Footprint, Heatmap and Liquidation Maps remain separately gated by their owner-provided visual references, a scoped blueprint and owner review. Footprint must remain explicitly `SIMULATED` unless a separately validated real-data source is implemented.
- No indicator UI implementation is authorized while Stage 1 is active. The existing indicator UI blueprint is parked as a Stage 4 preparation draft.
- The separate **40% overall-project gate** applies to broader professional UI/feature expansion and its blueprint/review process. It does not move indicator implementation into Stage 1, waive the stage sequence, or count as Stage 1 acceptance.
- Stage transitions require the preceding stage's acceptance evidence. A branch name, documentation draft, passing unrelated CI run or partial implementation does not advance a stage.

## Non-negotiable project constraints

- Preserve existing working features; do not solve blockers by removing or weakening functionality.
- Zero-cost operation: no paid hosting, data, subscriptions, trials that can bill, or publication fees unless the owner explicitly changes this constraint.
- Do not claim production/live delivery from local tests or CI-only evidence.
- Do not ask the owner to run unverified or error-prone commands. Inspect first and provide only verified, necessary actions.
- Keep `main` untouched; work only on the active feature branch unless the owner explicitly approves otherwise.
