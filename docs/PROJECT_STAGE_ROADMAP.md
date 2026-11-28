# AUTHORITATIVE OWNER CHECKPOINT — 28 November 2026, Batch 98

**Official stage:** Stage 1 — Foundation, Security & Data Integrity. Stage 2 remains preparatory and is not authorized until Stage 1 reaches 40/40 and the owner explicitly approves transition.

**Stage 1:** 30/40 = 75% provisional; Gate 10 = 0/10 formally closed. Owner-controlled acceptance criteria **8, 20, 25, 30, 31, 34, 35, 36, 38 and 39** remain open pending production/owner evidence. No score is added by CI, documentation, synthetic fixtures or preview builds.

**Branch / PR:** `work/batch95-websocket-ack-protocol`; PR #13 remains open and unmerged. Branch head at this checkpoint: `f5b48995705e10b32bc6d4c44bb24f60b6ea0cd2` (documentation-only Heatmap reference receipt). The authoritative source/test HEAD remains `e29040d4f3e9e5da5c9dd1400e102f5139b9ba41`, as recorded in the Stage 1 acceptance matrix. `main` remains untouched; no merge or production deployment performed.

**Exact source/test HEAD CI: 4/4 terminal SUCCESS**
- Automated Tests [46107071181](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071181) — SUCCESS; 41/41 steps; frontend 339/339, backend 1,437 passed / 1 skipped, Worker runtime 26/26.
- CodeQL [46107071199](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071199) — SUCCESS.
- OCI ARM64 Image Readiness [46107071235](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071235) — SUCCESS.
- Full Git History Secret Audit [46107071288](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46107071288) — SUCCESS.

**Five independent workstream reconciliation — 28 November**
1. **CI / test integrity:** exact source/test HEAD above has all four required workflows terminal SUCCESS. The later docs-only commit `f5b4899` is not represented as a new source/test CI run.
2. **WebSocket / backend:** ACK session ledger and SQLite receipt primitives exist with unit tests, but `backend/app/main.py` does not yet receive `market_data.ack`, resolve it against the socket ledger, commit the durable receipt, or emit an ACK confirmation. Production ACK remains YELLOW / not advertised. Do not call WebSocket production-complete.
3. **Indicators / chart:** `CandlestickChart.tsx` does not import or invoke the indicator hook. Existing calculation declarations are foundations, not chart-visible indicators. Footprint remains synthetic/offline; Volume Profile and Heatmap remain open and Stage 4-gated. The Heatmap reference receipt is recorded in the indicator ledger only.
4. **Android / release:** `.github/workflows/android-apk.yml` builds an installable debug APK on workflow dispatch or relevant pushes, uploads a 7-day CI artifact, and defaults preview-release publication to false. This is not a final signed/release APK; no new APK build is claimed by this checkpoint.
5. **Hosting / deployment:** Vercel has READY historical preview deployments for older commits, alongside canceled attempts. No deployment for current branch head `f5b4899` was verified, and no production deployment was made. Preserve ZERO COST; avoid unnecessary deployment churn and free-tier quota consumption.

**Production boundaries still open:** Firebase-verified stable consumer identity, durable owner/fence-bound receipt enforcement, restart reconciliation, public WSS/TLS, browser/Android E2E, lawful market-data redistribution, owner-host backup/restore and monitoring/incident evidence. SHA-256 event digest validation is integrity checking, not a digital signature or provider authenticity proof.

**Deadline:** 24 December 2026 — 26 calendar days remain from 28 November. This is a delivery target, not a basis for bypassing Stage 1 acceptance or release gates.

**Controls:** ZERO COST; no paid services, billing changes, new Cloudflare resources, production deployment, PR merge or `main` modification. No autonomous background/10-minute coding is running. CI status was checked during this active session only.

---


**Official stage:** Stage 1 — Foundation, Security & Data Integrity. Stage 2 is preparatory only and cannot officially start until Stage 1 reaches 100% and the owner explicitly authorizes the transition.

**Stage 1 accounting:** 30/40 = 75% provisional. The ten remaining external acceptance criteria are 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Gate 10 remains 0/10 formally closed. These are not ten missing source-code functions: each requires owner-host, real Firebase, backup/key custody, deployment, public WSS/device, monitoring or incident evidence. Repository CI cannot truthfully close them. No ticks are added by documentation or synthetic tests.

**Exact source/test HEAD:** `96cb3d505b7f70d70147f6773d879632d71e9a58`. PR #13 remains OPEN and unmerged; branch `work/batch95-websocket-ack-protocol`; `main` untouched. The exact source/test SHA has all four required workflows terminal SUCCESS:
- Automated Tests [46011891943](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46011891943) — **41/41 steps SUCCESS**.
- CodeQL [46011891956](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46011891956) — **SUCCESS**.
- OCI ARM64 [46011892089](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46011892089) — **SUCCESS**.
- Full Git History Secret Audit [46011892151](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46011892151) — **SUCCESS**.

Automated Tests passed Worker/DO runtime tests, frontend tests and build, Android read-only preflight, Redis TLS CA/hostname fixture, backend tests, SQLite outbox/metrics benchmarks, dependency audit, backend image build, persistent-volume/Redis-guard smoke test, image scan/report and audit enforcement. This is repository/synthetic evidence, not a production deployment or owner-host acceptance.

**Batch 96B change:** schema v5 migration now deactivates legacy consumer rows without valid owner/fence/lease metadata. Regression test added for v4-to-v5 migration. The change is included in the exact SHA above and therefore has full four-workflow CI success.

**Remaining WebSocket lifecycle work:** implement atomic lease acquisition/renewal/release; monotonic fencing on expired takeover; owner+fence+expiry validation on ACK; expiry-aware compaction; socket lifecycle integration; stale owner/duplicate owner/takeover/restart/eviction/concurrency tests. These are still open. Do not claim WebSocket lifecycle complete.

**Project status:** Stage 1 75% provisional; Stage 2 preparatory; Stage 3/5/6 unscored; Stage 4 gated; overall project percentage not scored. ZERO COST. No paid trials, new resources, deployments or billing changes. Delivery target 24 December 2026: 27 calendar days remain from 27 November. No autonomous background AI coding is claimed; the 10-minute relay runs preflight only.

---

# OFFICIAL SIX-STAGE ROADMAP

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


---

## Batch 80–86 unified runtime and acceptance work package (25 November 2026)

Authoritative work package: [WORK_CYCLE_2026-11-25_BATCH80_86_UNIFIED_RUNTIME_AND_ACCEPTANCE_PLAN.md](WORK_CYCLE_2026-11-25_BATCH80_86_UNIFIED_RUNTIME_AND_ACCEPTANCE_PLAN.md). Starting HEAD: `fd756cee2bf3e427a628c3089c37d07d9f75ada7`; source/test baseline: `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`.

**Scope/accuracy:** this package is the detailed engineering blueprint and acceptance matrix for Batches 80–86. It does not claim runtime implementation, production deployment, public WSS, owner-host verification, or indicator completion. No source code, secrets, production data, Cloudflare resources, or deployments were changed. The major runtime composition review gate remains in force; implementation is sequenced after the scoped blueprint review. This preserves the user's no-broken-code requirement.

**Batch sequence:** 80 strict source/gateway role config and fail-closed validation; 81 source publisher factory and signed snapshot/checkpoint startup; 82 gateway replica factory with owner-pinned Ed25519 verification and install-before-Redis; 83 real Redis two-gateway process/restart/fault tests; 84 immutable per-gateway durable receipt and monotonic high-water ACK; 85 existing Cloudflare route/origin mapping and public WSS/browser/Android acceptance; 86 zero-cost recovery, monitoring, backup/restore and incident acceptance. Full test matrices, security boundaries, startup/shutdown rules, Redis ACL boundaries, and acceptance gates are in the linked package.

**Critical safeguards:** source and gateway remain separate app roles; no shared DB; gateway never receives source private key; Redis destructive `XTRIM`, `XDEL`, and consumer-group destruction remain blocked until every required gateway has an owner-accepted durable high-water ACK and restart reconciliation proof. XACK/local applied cursor are not owner acceptance. Do not create duplicate Cloudflare resources or introduce paid providers.

**Engineering parameter review:** current defaults observed in source are publisher lease 30,000 ms, publisher batch 100, consumer pending-idle 30,000 ms, consumer batch 100, gateway lease 15,000 ms with 5,000 ms default renewal, WebSocket ticket TTL 90 seconds, entitlement recheck 60 seconds. These are existing defaults, not production SLOs; validate against measured p99 latency, host scheduling and Redis RTT before acceptance.

**CI:** source/test SHA `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` has prior exact-source evidence: Automated Tests 41/41, 1,426 passed, 1 skipped, 6 warnings; CodeQL 16/16; OCI ARM64 7/7; Secret Audit 6/6; dedicated Redis TLS 1 passed. Current documentation HEAD `fd756cee2bf3e427a628c3089c37d07d9f75ada7` is 12 commits ahead, zero behind, documentation-only by compare; no new source CI is claimed. The documentation commit uses `[skip ci]` and has no run/status. Previously recorded source jobs are terminal success; no running jobs left.

**Progress unchanged:** Stage 1 30/40 = 75% provisional 🟨; Gate 10 0/10 closed 🔴 (8, 20, 25, 30, 31, 34, 35, 36, 38, 39); Stage 2 🟦 preparatory; Stage 3 ⚪ not scored; Stage 4 🟪 gated; Stages 5–6 ⚪ not scored. Overall project/IP3S ⚪ NOT SCORED. WebSocket runtime, Gate 25 durable ACK, public Cloudflare WSS/device E2E and owner-host recovery remain 🔴 OPEN.

**Indicator ledger unchanged:** SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook 🟨 FOUNDATION; Footprint PRO 2GD 🟧 GATED; Volume Profile, Complete Volume Profile, Movable-range VP, Heatmap and Liquidation Maps 🔴 OPEN. 28 focused declarations (21 calculation + 7 hook) are not a completion percentage. No indicator source/UI changes. Keep warm-up nulls, prefix causality, no lookahead/repaint, timestamp alignment, stale-output clearing and no calculations on unavailable/demo/error/empty snapshots. Footprint OFF remains normal spacing; Footprint ON alone uses spaced clusters. Footprint references are available; Heatmap reference is still required before visual work.

Controls: ZERO COST; `main` untouched; Vercel deferred; no new/duplicate Cloudflare resources; no paid data/hosting/monitoring/backup; delivery target around 24 December 2026.


---

## Batch 80 — strict runtime role and fail-closed app binding (25 November 2026)

**Status: IMPLEMENTED + VERIFIED 🟩.** This is a bounded Batch 80 completion, not a claim that the complete source/gateway production relay is deployed.

### Implemented controls

- OHLCV_REDIS_ROLE must explicitly be source or gateway whenever OHLCV_REDIS_ENABLED=true; missing, unknown, or mismatched roles fail closed.
- create_app() validates that the declared role has its matching injected factory: source requires publisher_runtime_factory; gateway requires replica_runtime_factory. A crossed factory or enabled relay with no injected factory is rejected before application startup.
- Source and gateway factories remain mutually exclusive.
- Source and replica SQLite database targets must be absolute file paths; relative paths, symbolic-link targets, and directory targets are rejected.
- backend/.env.example now documents the role selector. Relay remains disabled by default.
- Added focused tests for missing/invalid/mismatched roles, factory-role binding, fail-closed app creation, absolute database paths, directories and symlinks.

### Changed files

- backend/app/ohlcv_redis_config.py
- backend/app/ohlcv_redis_runtime.py
- backend/app/ohlcv_redis_gateway_runtime.py
- backend/app/main.py
- backend/tests/test_ohlcv_redis_config.py
- backend/tests/test_ohlcv_redis_runtime.py
- backend/tests/test_ohlcv_redis_gateway_runtime.py
- backend/tests/test_ohlcv_redis_publisher_lifecycle.py
- backend/.env.example

### Exact verification — final source commit

Commit: 66d4c6a812d5ce2570345e1108e813b5067f5248

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [2457](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188191) | 🟩 41/41 steps; 1,433 passed, 1 skipped, 6 warnings |
| CodeQL Python | [1814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188170) | 🟩 8/8 |
| CodeQL JavaScript/TypeScript | [1814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188170) | 🟩 8/8 |
| Full Git History Secret Audit | [1396](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188184) | 🟩 6/6 |
| OCI ARM64 Image Readiness | [443](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188277) | 🟩 7/7 |

Automated Tests also completed the Redis TLS fixture step, backend dependency audit, backend container build, container smoke test with shared Redis guard/persistent volume, and container scan. All four workflows are terminal success; no CI job remains running. An earlier run exposed one legacy gateway fixture missing the new role; that fixture was corrected before the final successful run.

### Boundary — what is still not complete

The module-level production ASGI app does not invent owner-specific snapshot callbacks. Source publisher activation still requires an owner-provided snapshot_verifier that verifies the exact snapshot and every required gateway's durable installation receipt. Gateway activation still requires an authenticated snapshot_installer and owner-pinned Ed25519 trust keys. These callbacks are not guessed or fabricated. Therefore production publisher/gateway runtime wiring, Gate 25 owner-accepted durable high-water ACK, public Cloudflare WSS, browser/Android E2E and owner-host recovery remain 🔴 OPEN. No production deployment or Cloudflare resource was changed.

### Next ordered work

1. **Batch 81:** source publisher runtime integration, contingent on the authoritative owner snapshot-verifier and durable gateway-receipt source.
2. **Batch 82:** gateway replica runtime integration, contingent on the authenticated snapshot-transfer/install callback and owner-pinned key configuration.
3. **Batch 83:** two-gateway Redis process/restart/fencing/fault acceptance.
4. **Batch 84:** durable owner-accepted high-water ACK and restart reconciliation.
5. **Batch 85:** existing Cloudflare route/origin plus public WSS/browser/Android acceptance.
6. **Batch 86:** owner-host backup/restore, local observability and incident drills.

Do not trim/delete Redis stream entries or destroy consumer groups until every required gateway has a durable owner-accepted high-water ACK and restart reconciliation proof.

### Project and indicator progress — no percentage inflation

- Stage 1: **30/40 = 75% provisional 🟨** (unchanged; Batch 80 does not auto-close Stage 1 criteria).
- Gate 10: **0/10 formally closed 🔴**; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stage 2: 🟦 preparatory, not officially entered/scored.
- Stage 3: ⚪ not scored.
- Stage 4: 🟪 gated.
- Stages 5–6: ⚪ not scored.
- Overall project: ⚪ NOT SCORED; approved weighted denominator is still absent.
- Significant project index/IP3S: ⚪ NOT SCORED for the same reason.

### Complete indicator ledger — source/UI unchanged in Batch 80

| Indicator | Status | Current implementation/evidence | Mathematical/acceptance boundary |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Calculation foundation only | First valid index 19; arithmetic mean of 20 closes |
| EMA20 | 🟨 FOUNDATION | Calculation foundation only | First valid index 19; alpha 2/21; recursive seed contract tested |
| RSI14 Wilder | 🟨 FOUNDATION | Calculation foundation only | First valid index 14; Wilder smoothing; no divide-by-zero NaN leak |
| MACD12/26/9 | 🟨 FOUNDATION | Calculation foundation only | MACD line first valid index 25; signal and histogram index 33 |
| Bollinger20,2 | 🟨 FOUNDATION | Calculation foundation only | First valid index 19; population standard deviation per current contract |
| Shared Indicator Hook | 🟨 FOUNDATION | 7 focused declarations | Chart integration into CandlestickChart.tsx remains open |
| Footprint PRO 2GD | 🟧 GATED | Synthetic/offline accumulator only | Visual work must match both saved Footprint references; OFF keeps normal candle spacing, ON alone enables spaced clusters |
| Volume Profile | 🟥 OPEN | Not accepted | Price-bin volume conservation, range semantics and timestamp boundaries |
| Complete Volume Profile | 🟥 OPEN | Not accepted | Full-session completeness, POC/VA derivation and conservation |
| Movable-range Volume Profile | 🟥 OPEN | Not accepted | User-selected range bounds and deterministic recomputation |
| Heatmap | 🟥 OPEN | Visual implementation not started | Must wait for the user's Heatmap reference image |
| Liquidation Maps | 🟥 OPEN | Not accepted | Data provenance and methodology remain unapproved |

Focused declaration inventory remains **28 total = 21 calculation + 7 shared-hook declarations**. This is not an indicator completion percentage or count of accepted indicators. Batch 80 changed no indicator calculation or chart UI; indicator progress credit is therefore unchanged.

Cross-indicator acceptance remains mandatory: warm-up values null until mathematically valid; prefix causality; no future-candle lookahead/repaint; exact timestamp/series identity alignment; stale-output clearing on identity change; deterministic repeated results; bounded computation; no mutation of source candle data; no calculations for demo/loading/unavailable/error/empty snapshots.

**Controls:** ZERO COST; active branch only phase-2/market-data-foundation; main untouched; no Vercel; no paid market data, hosting, monitoring, backup, subscription or publication; no duplicate Cloudflare infrastructure. Planning target remains around **24 December 2026**.


---

## Authoritative checkpoint — Batch 96A CI terminal verification (27 November 2026)

**This section supersedes older CI/SHA snapshots above for the current checkpoint.** Older dated entries remain historical evidence and must not be read as the latest branch state.

- Official stage remains **Stage 1 — Foundation, Security & Data Integrity**.
- Stage 1 remains **30/40 criteria = 75% provisional 🟨**. No score increase is claimed for Batch 96A.
- Ten external Stage 1 acceptance criteria remain open and awaiting evidence: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No active item is presented as accepted without owner-host evidence.
- Stage 2 remains preparatory only. Stage 2 cannot officially begin until Stage 1 reaches 100% and the owner explicitly authorizes the transition.
- PR #13 remains OPEN and unmerged. Branch: `work/batch95-websocket-ack-protocol`. Latest PR/documentation HEAD at this checkpoint: `f9ddd7f62951fd48471cbb7ece12594702f1407b`. Application `main` remains untouched.
- Latest source/test SHA with exact-head CI: `7dcf148b772d37c4321122a1c45d49bae0e43868`. The documentation HEAD is later than the tested source/test SHA; do not conflate them.
- Four workflows on source/test SHA `7dcf148b772d37c4321122a1c45d49bae0e43868` are now terminal SUCCESS:
  - Automated Tests [46010599247](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46010599247)
  - CodeQL Security Analysis [46010599101](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46010599101)
  - OCI ARM64 Image Readiness [46010599133](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46010599133)
  - Full Git History Secret Audit [46010599070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46010599070)
- Automated Tests job completed SUCCESS with all steps successful, including Worker proof, pinned workerd/DO runtime, frontend tests/build, Android read-only preflight, Redis TLS CA/hostname enforcement, backend tests, SQLite benchmarks, backend container build/smoke test and image scan/report.
- Batch 96A source work adds Durable Object SQLite schema v5 fields to `required_consumers`: `owner_token`, `fence_token`, and `lease_expires_at_ms`, plus the lease-expiry index. Runtime migration tests assert v5 columns, migration history and eviction persistence.
- **Scope boundary:** this is schema/migration groundwork only. Lease acquire/renew/expire/fencing enforcement, owner-bound ACK and close validation, safe deregistration, expiry-aware compaction and lifecycle race/restart acceptance are not implemented or claimed complete. Production FastAPI/Redis runtime wiring, Firebase owner identity, public WSS and browser/Android E2E remain unaccepted.
- Next implementation order: (1) make legacy ownerless consumer rows fail closed; (2) implement atomic lease acquire/renew/release with monotonic fencing; (3) bind ACK and socket close to owner + fence + unexpired lease; (4) make compaction evaluate only valid active leases and reject unsafe stale owners; (5) add expiry, takeover, duplicate-owner, stale-fence, restart/eviction and concurrent ACK/compaction tests; (6) run all four exact-source CI workflows to terminal state.
- CI success is synthetic proof/repository evidence, not production acceptance and not closure of any external Stage 1 gate.
- Delivery target remains **24 December 2026**; from 27 November, **27 calendar days** remain. ZERO COST. Do not merge PR #13 or modify `main` without explicit owner authorization. No autonomous 10-minute AI coding is claimed; the configured relay runs preflight only.


## Automation reality audit — 27 November 2026 (read-only Cloudflare + GitHub verification)

The Cloudflare account currently contains one Worker script, `dezzta-chart-runner-relay`; the account has **zero** Durable Object namespaces, Pages projects, zones, and Worker custom domains. The Worker account subdomain exists, but that does not mean the DEZZTA CHART application Worker is deployed.

- The relay's Cron Trigger schedules endpoint returns an empty schedule list. No 10-minute Cron Trigger is configured.
- The relay Worker has a `fetch` handler only; its health endpoint reports `mode: standby`. Its authenticated `POST /trigger` route dispatches GitHub workflow `preflight.yml` in `dezzta-chart-runner`. It does not invoke ChatGPT or edit application code.
- The runner workflow has only `workflow_dispatch`, checks out application branch `phase-2/market-data-foundation` (not the active PR branch `work/batch95-websocket-ack-protocol`), verifies branch/package metadata, and explicitly performs **no install, build, tests, edits, or pushes**.
- Therefore the prior description of an autonomous 10-minute AI coding loop was inaccurate. Do not represent the relay as an AI agent, scheduled build/test runner, or autonomous coding system. Do not add a Cron Trigger that only repeats a no-op preflight or would consume free CI minutes without delivering code progress.

This audit used read-only account/resource queries and source inspection. No Cloudflare resource, secret, schedule, billing setting, deployment, or repository application code was changed by this audit.

## Current exact-head CI — documentation-only head

After the checkpoint above, three documentation-only commits updated the owner dashboard, roadmap, and acceptance matrix. Latest PR HEAD is `7a5255a9935ccdf728f91bfc71ad98aaf67bc08d`. Four workflows on this exact HEAD are terminal SUCCESS: Automated Tests [46012847491] (41/41 steps), CodeQL [46012847240], OCI ARM64 [46012847230], and Full Git History Secret Audit [46012847260]. The latest source/test implementation remains `96cb3d505b7f70d70147f6773d879632d71e9a58`; documentation-only changes do not change its application behavior.
