## Cloudflare deployment boundary — Batch 72 (25 November 2026)

Cloudflare is an intended platform component and the repository contains a tested synthetic Worker/SQLite Durable Object proof. That proof is not a deployed production service: its Wrangler config disables Workers.dev and preview URLs, sets synthetic-only mode, and the Worker source explicitly excludes FastAPI, Firebase, live providers and UI integration. The currently connected Cloudflare account inventory returned no deployed Worker, Pages project, Tunnel, Durable Object namespace, Queue, D1, KV, Zone or Worker domain. Do not treat this as Stage 1 acceptance.

For ZERO COST, evaluate Workers Free + SQLite-backed Durable Objects within the documented quotas. Exclude Cloudflare Containers because they require Workers Paid. Cloudflare Tunnel is available on all plans and supports WebSockets, but it only forwards to an existing owner-operated origin; it does not host the Python FastAPI container. Route selection (Cloudflare-native backend port vs Tunnel to an existing owner origin) requires exact account/project confirmation and a reviewed blueprint before resource creation or deployment. See `docs/WORK_CYCLE_2026-11-25_BATCH72_CLOUDFLARE_INVENTORY_ZERO_COST_WEBSOCKET_PATH.md`.

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

## Stage 1 / Gate 10 / Stage 2 boundary clarification (Batch 71)

Gate 10 is the ten-item Stage 1 acceptance roll-up: criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. These criteria remain assigned to Stage 1 until their required acceptance evidence is complete; they are not automatically transferred into Stage 2.

Some Stage 2 market-data foundation engineering is present on the technical branch as preparatory/parallel groundwork. This does not mean Stage 2 is the official active stage. The official roadmap remains at Stage 1 until Stage 1 exit acceptance is satisfied. The branch name `phase-2/market-data-foundation` is not a stage-transition signal.

Do not confuse Stage 1 criterion #25 (owner-host Redis TLS/ACL/persistence acceptance) with Project Gate 25 (Ed25519 snapshot transfer, immutable receipt retrieval and durable high-water ACK). Both remain separate and open.

The separate 40% overall-project threshold authorizes preparation/review of broader feature blueprints only; it does not override Stage 1 exit criteria or the Stage 4 indicator UI gate.

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


---

## Batch 79 — Production WebSocket runtime wiring audit (25 November 2026)

Source audit report: [Batch 79 production runtime wiring and Gate 25 composition](WORK_CYCLE_2026-11-25_BATCH79_PRODUCTION_WEBSOCKET_RUNTIME_WIRING_AUDIT.md). Audited documentation HEAD before this report: `114d8464e085977aba2d95b3581ee49a95990c18`; last source/test SHA: `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`.

**Newly isolated root cause:** the individual publisher, Redis replica consumer, SQLite replica store, Ed25519 snapshot attestation, Firebase identity, single-use ticket and WebSocket route primitives exist. However, the stock Docker command starts `uvicorn app.main:app`, and module-level `app = create_app()` supplies neither `replica_runtime_factory` nor `publisher_runtime_factory`. With no replica factory, lifespan starts the provider manager instead of the replica consumer/worker; with no publisher factory, the source relay is not started. The WebSocket handler falls back to the local source SQLite/in-memory pipeline when no replica store is injected. This is the concrete production runtime-composition gap. Source and gateway factories are intentionally mutually exclusive and must remain separate roles.

**Gate 25:** Ed25519 signed snapshot verification and atomic replica installation primitives exist, but the default app does not assemble owner-pinned trusted keys, expected source identity, signed snapshot transfer/install, dedicated gateway DB, consumer, lease and runtime lifecycle. The production runtime contract and owner-host evidence remain OPEN. Local replica cursor and Redis XACK must not be mislabeled as the owner-accepted per-gateway durable high-water receipt/ACK.

**CI boundary:** exact source/test SHA `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` has recorded Automated Tests 41/41 (1,426 passed, 1 skipped, 6 warnings), CodeQL 16/16, OCI ARM64 7/7, Secret Audit 6/6 and dedicated Redis TLS 1 passed. Documentation HEAD `114d8464e085977aba2d95b3581ee49a95990c18` has six documentation-only commits ahead of that source SHA and no source/runtime diff; the docs-only commit has no CI runs/status because of `[skip ci]`. No new source CI is claimed.

**Progress:** Stage 1 30/40 = 75% provisional 🟨; Gate 10 0/10 formally closed 🟥 (8, 20, 25, 30, 31, 34, 35, 36, 38, 39). Stage 2 🟦 preparatory only; Stage 3 ⚪ not scored; Stage 4 🟪 gated; Stages 5–6 ⚪ not scored. Overall project and IP3S ⚪ NOT SCORED. Indicator inventory unchanged: SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Hook 🟨 FOUNDATION; Footprint PRO 2GD 🟧 GATED; Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps 🟥 OPEN. Focused declarations 28 (21 calculation + 7 hook), not completion. No indicator source/UI changes.

**Next order:** define strict source/gateway role configuration; implement source factory; implement gateway factory with signed snapshot install before Redis initialization; add multi-process source-to-two-gateway integration and restart/fencing tests; prove per-gateway durable receipt/high-water ACK; then public Cloudflare WSS/browser/Android E2E; then owner-host backup/restore/monitoring acceptance. Keep Redis destructive retention blocked until ACK acceptance.

Controls unchanged: ZERO COST, `main` untouched, Vercel deferred, no duplicate Cloudflare resources, no paid data/hosting/monitoring/backup, planning target around 24 December 2026.
