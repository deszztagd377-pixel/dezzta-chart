# DEZZTA CHART — CURRENT PROJECT CONTROL DASHBOARD

**Checkpoint:** 20 November 2026 — Batch 62J-23 opt-in replica runtime integration  
**Active branch:** `phase-2/market-data-foundation`  
**Latest fully CI-verified code HEAD:** `468d0aa4a348d997dc7affb71374bc8712cfc39d`  
**Latest documentation checkpoint before this refresh:** `99bc549e95341310945b987ab4ae11a86c962ea9`  
**Current audit batch:** 62J-21 documentation integrity repair + exact-head CI reconciliation  
**Cost policy:** ZERO COST. No paid providers, hosting, deployments, Vercel/Cloudflare actions, or Termux requirement.

> This document is the current concise dashboard. Historical work-cycle reports remain the evidence trail. Do not infer that a docs-only commit has rerun or revalidated code CI.


## 0. Batch 62J-21 — documentation integrity + exact-head CI reconciliation (20 November 2026)

**Audited branch HEAD before this documentation update:** `99bc549e95341310945b987ab4ae11a86c962ea9`  
**Runtime code checkpoint:** `468d0aa4a348d997dc7affb71374bc8712cfc39d`  
**CI on exact branch HEAD `99bc549e95341310945b987ab4ae11a86c962ea9`:** Automated Tests run `44680830387` SUCCESS • CodeQL run `44680830205` SUCCESS • Full Git History Secret Audit run `44680830208` SUCCESS.

This is a documentation/evidence refresh and integrity repair. No runtime source or test code changed in this cycle. The runtime code checkpoint remains `468d0aa4a348d997dc7affb71374bc8712cfc39d`; `99bc549...` is a docs-only descendant. All three workflows completed successfully on exact HEAD `99bc549...`.

### Documentation integrity repair

The previous documentation update accidentally replaced the opening contents of `docs/INDICATOR_PROGRESS_LEDGER.md` with an object-string placeholder. This batch restores the complete ledger from its verified parent revision and appends the exact-head CI reconciliation. No indicator status or percentage is increased by this repair.

### WebSocket source audit — concrete integration boundary

- `backend/app/main.py` still creates `SQLiteOhlcvStore`, `OhlcvPipeline` and `OhlcvStreamHub` as its live WebSocket read path.
- `/ws/market-data` obtains its snapshot cursor from the source SQLite outbox and subscribes to the in-memory source pipeline/hub.
- The Redis publisher, per-gateway consumer, replica SQLite, replica bridge and worker lifecycle are implemented/tested as separate foundations, but are not wired into FastAPI lifespan or the production route.
- Existing two-process tests prove independent Redis consumers and durable replica files. They do not start two independent ASGI servers.
- Snapshot installation still requires a local verified artifact. No production snapshot distribution transport is selected.
- Therefore do not combine source-SQLite snapshot reads with Redis-replica live events. That would mix cursor domains and risk missing/duplicate updates.

**Next safe technical sequence:** (1) settle owner-approved snapshot transport/topology, (2) implement a replica-backed read adapter while preserving source mode as default, (3) add opt-in fail-closed lifespan ownership, (4) start two real ASGI processes in existing Redis 7 CI with distinct replica SQLite files, (5) add restart/outage/re-snapshot/cursor-parity acceptance, and only then (6) consider production enablement after owner-provisioned TLS/ACL proof. No new Redis service or paid infrastructure is needed for the CI harness.

### Indicator source audit

- `indicatorCalculations.ts` contains SMA20, SMA-seeded EMA20, Wilder RSI14, MACD12/26/9 and Bollinger20,2 calculations.
- `useMarketIndicators.ts` consumes the shared validated backend snapshot and suppresses DEMO/loading/unavailable/error values.
- `CandlestickChart.tsx` currently creates only the candlestick series; it does not import/use the indicator hook or render indicator overlays/panes.
- `docs/INDICATOR_UI_BLUEPRINT.md` remains PARKED for Stage 4 and explicitly does not authorize visible indicator implementation during Stage 1.
- No indicator status or percentage is increased by this audit or by WebSocket CI.

### Current control totals

- Stage 1: 30/40 criteria = 300/400 ticks = **75% provisional**.
- Gate 10: **10/10 ORANGE, 0/10 formally closed** — IDs 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: not scored.
- Overall project percentage: not established; M1–M8 weights are not approved.
- Indicator aggregate percentage: not established; no approved weighted acceptance denominator.
- Cost: ZERO COST. No Vercel/Cloudflare deployment, no paid service, no `main` changes, no Termux requirement.


## 1. Project-level progress

| Measure | Verified position | Status |
|---|---:|---|
| Stage 1 | 30/40 criteria = 300/400 ticks | 🟨 75% provisional |
| Gate 10 | 0/10 formally closed | 🟧 All ten remain OPEN; acceptance in progress |
| Stages 2–6 | No approved scored acceptance denominator | ⬜ Not scored |
| Overall project | M1–M8 weighting not approved | ⬜ Not established |
| Indicator aggregate | No approved weighted denominator | ⬜ Not established |

Do not publish a guessed overall percentage. Stage 1's provisional score is not the overall project score.

## 2. Ten-gate control board

All ten tracked gates remain formally OPEN (0/10 closed). Their project-control status is 🟧 ORANGE (active/in progress), not 🔴 RED (blocked/untouched). OPEN is the closure state; ORANGE is the work-state color. A gate becomes 🟩 only after its own acceptance evidence is recorded. Repository code and CI cannot substitute for credentials, target-environment operation, restore drills, or production access evidence.

| Gate | Status | Closure evidence still required |
|---|---|---|
| 8 | 🟧 OPEN | Owner-controlled environment/operational acceptance evidence |
| 20 | 🟧 OPEN | Target environment integration and acceptance evidence |
| 25 | 🟧 OPEN | Redis TLS/ACL credentials, independent gateway instances, outage/recovery and parity evidence |
| 30 | 🟧 OPEN | Owner-side infrastructure/security acceptance |
| 31 | 🟧 OPEN | Operational recovery/restore evidence |
| 34 | 🟧 OPEN | WSS/client integration and target-device acceptance |
| 35 | 🟧 OPEN | Collector/provider operational evidence |
| 36 | 🟧 OPEN | Multi-instance Redis relay and end-to-end gateway acceptance |
| 38 | 🟧 OPEN | Operator runbook and operational drill evidence |
| 39 | 🟧 OPEN | Final owner sign-off and evidence completeness |

The ten tracked gate IDs above are the current open set: 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Their display color is 🟧 ORANGE as requested; none is marked closed. No gate has been closed by documentation-only work.

## 3. WebSocket / Redis engineering status

### Implemented library foundations

- Global source SQLite snapshot export with bounded JSONL streaming, manifest row count and SHA-256 verification.
- Isolated replica snapshot installation with atomic transaction/checkpoint update and replica identity.
- Incremental replica event apply with strict event contract, cursor continuity, dedupe and retention handling.
- Source-SQLite publisher checkpoint with fenced lease and deterministic Redis Stream IDs.
- Redis append retry/read-back validation and bounded publisher loop.
- Per-gateway consumer groups, pending reclaim via XAUTOCLAIM, durable SQLite apply before XACK, and generation-scoped group reset.
- Independent publisher/consumer process tests against the Redis 7 CI service.
- Durable replica-to-pipeline/hub bridge, cursor-aware duplicate suppression, callback dispatch onto the owning event loop, and managed worker lifecycle.
- Source-SQLite WebSocket replay/live boundary merge; replay completion is emitted only after successful merge. Handoff failure emits sanitized resnapshot-required and closes with 1013.

### 62J-15 audit findings

Reviewed the Redis consumer, managed worker, event-loop dispatcher, replica bridge, stream hub and corresponding real-Redis tests.

- Consumer applies the event to durable replica SQLite before callback and ACK.
- Callback failure leaves the event pending; same-consumer pending entries are retried before newer entries.
- Restart recovery uses XAUTOCLAIM; deleted pending entries require a fresh snapshot.
- Dispatcher marshals work to the owning event loop and waits up to its configured deadline; callback errors/timeouts prevent ACK.
- Managed worker has bounded exponential retry, terminal resnapshot-required state and bounded synchronous/asynchronous shutdown.
- Snapshot/replay/live merge validates exact series identity, monotonic replay cursors, queued live cursor ordering and queue capacity; covered live events are discarded and newer events are resequenced.
- The consumer worker is deliberately not wired into FastAPI startup. That is a safety boundary, not a completed production integration.

### Remaining WebSocket acceptance blockers

1. Separate independently started ASGI backend instances/containers with real shared Redis and independent replica SQLite files.
2. End-to-end publisher restart, consumer restart, Redis outage/recovery, snapshot reinstallation and cursor parity under process/container failure.
3. Owner-provisioned Redis TLS and least-privilege ACL credentials, including credential rotation and target-environment verification.
4. Startup/shutdown orchestration and ownership proving exactly one sequential consumer worker per gateway replica group.
5. Public WSS/browser/Android end-to-end verification.
6. Retention/stream trimming policy and operational cleanup authorization. Runtime gateway ACL must not receive destructive group-destroy permissions.

Do not wire publisher/consumer into `main.py` until these prerequisites and lifecycle tests pass. No production secrets or ACL changes have been performed.

### CI evidence boundary

At code HEAD `407d2b38882e92cdf6db5b7df6c44350b6cd746d`, the previously recorded exact-head workflows passed:
- Automated Tests: run `44564212673` — backend 1,153 passed; frontend 236 passed across 28 test files; build, scans, dependency audit, container and Redis/persistent-volume checks passed.
- CodeQL Python and JavaScript/TypeScript: run `44564212707` — SUCCESS.
- Full Git History Secret Audit: run `44564212714` — SUCCESS.

The later docs-only checkpoint does not change code and does not imply a new code CI run.


## 62J-16 — Worker lifecycle and callback deadline regression coverage

**Code checkpoint:** `3131284cae1971740d1845b196ec3d972dc4479b`  
**Scope:** tests only; production runtime behavior unchanged.

Added `backend/tests/test_ohlcv_redis_worker_lifecycle.py`:
- A blocked `consume_once()` must make bounded `stop()` return `False` and expose `stopping/thread_alive`, rather than falsely reporting a stopped worker.
- After the blocked call is released, the worker must terminate cleanly.
- A transient Redis-like connection failure must recover through retry/backoff.
- `ReplicaResnapshotRequired` must be terminal; worker restart is rejected until a verified snapshot is rebuilt.

Extended `backend/tests/test_ohlcv_event_loop.py`:
- Async callback deadline expiry raises `TimeoutError`.
- The pending async callback is cancelled before dispatcher return is accepted as complete.
- Existing tests continue to cover owner-loop execution, callback completion, callback exceptions, closed loops and callback-raised timeout distinction.

**Verification boundary (corrected 20 Nov 2026):** the subsequent documentation HEAD `468d0aa4a348d997dc7affb71374bc8712cfc39d` ran the complete CI successfully. The 62J-16 code commit `3131284cae1971740d1845b196ec3d972dc4479b` is an ancestor of that tested HEAD; the docs-only commit changed no runtime or test source. No source runtime change, deployment, paid service or Termux use.

## 4. Complete indicator progress ledger

### Color legend
- 🟩 Verified implementation and required tests for the stated scope.
- 🟨 Calculation/data foundation exists; visible chart integration or lifecycle acceptance remains.
- 🟧 Gated by required reference, blueprint or owner input.
- 🟥 Not implemented / no validated implementation.
- ⬜ Not assessed.

| Indicator / subsystem | Status | Formula / contract | First valid output | Remaining work |
|---|---|---|---:|---|
| SMA 20 | 🟨 Foundation | Arithmetic mean of 20 closes | Index 19 | Chart overlay, independent toggle, legend/latest value, stale clearing, render/lifecycle tests |
| EMA 20 | 🟨 Foundation | SMA-seeded EMA; alpha = 2/21 | Index 19 | Overlay, toggle, legend/latest value, stale clearing, render/lifecycle tests |
| RSI 14 | 🟨 Foundation | Wilder-smoothed gains/losses | Index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend, stale clearing, render tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD index 25; signal/histogram index 33 | Dedicated pane, two lines, histogram, zero guide, toggle, legend, render tests |
| Bollinger 20,2 | 🟨 Foundation | SMA20 ± 2 population standard deviations | Index 19 | Upper/middle/lower overlay, toggle, current values, stale clearing, render tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot only; no DEMO fallback | Depends on snapshot | Active chart identity/timeframe binding, loading/error states, stale clearing, cross-series isolation |
| Footprint | 🟧 Gated | Deterministic educational accumulator; explicitly SIMULATED | Depends on selected candle/price levels | User reference image, reviewed blueprint, ON-only cluster renderer, bid/ask cells, tests/performance |
| Heatmap | 🟥 Not implemented | Source and calculation contract not approved | N/A | User reference, reviewed blueprint, data contract, calculations, renderer, controls and tests |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract | N/A | Source feasibility, reference/blueprint, calculation, renderer, controls and tests |

### Indicator correctness rules

1. Indicator arrays remain aligned to candle indexes.
2. Warm-up positions are null/unavailable, never fabricated zeros.
3. SMA20 first output is index 19.
4. EMA20 uses SMA seed and alpha 2/21; first output index 19.
5. RSI14 uses 14 close-to-close changes for initialization and Wilder smoothing; first output index 14.
6. MACD12/26 first output index 25; signal and histogram first output index 33.
7. Bollinger20 uses population standard deviation, not sample deviation; first output index 19.
8. Symbol, venue, dataset, timeframe and chart identity changes must invalidate stale indicator values.
9. Each indicator needs an independent visibility control, correct overlay/pane, current value and render/lifecycle tests.
10. Calculation tests do not prove visual rendering, provider correctness or live synchronization.

### Visual feature gates

- Footprint is SIMULATED and must never be labelled exchange-native order flow.
- Footprint OFF preserves ordinary candlestick spacing. Only explicit ON switches to spaced candle/cluster layout.
- Do not implement Footprint or Heatmap visuals until the user supplies the relevant reference image and reviews the scoped blueprint.
- Heatmap and Liquidation Maps must not be represented as live market-derived data without validated source and calculation contracts.

## 5. Immediate engineering work order

1. Complete isolated ASGI/container lifecycle and failure-matrix tests for the WebSocket relay.
2. Verify dispatcher timeout/cancellation behavior under a deliberately blocked event loop and ensure no ACK or cursor-order corruption.
3. Verify worker shutdown during idle polling, pending retry, callback execution and Redis disconnect.
4. Complete owner-side Gate 25/36 acceptance only with real TLS/ACL and independent-instance evidence.
5. Return to indicator implementation in the ledger order: shared hook lifecycle, SMA/EMA overlays, RSI/MACD panes, Bollinger overlay, then render-level regression tests.
6. Keep Footprint/Heatmap visual work gated on the user's references and blueprint review.

## 6. Cost, deployment and device policy

- ZERO COST remains mandatory.
- No paid data provider, hosting, subscription or publication fee is assumed.
- No Vercel or Cloudflare deployment/promotion is authorized.
- No deployment is needed to run repository CI.
- No Termux is currently required.
- `main` must remain untouched; all work stays on `phase-2/market-data-foundation`.

**Accounting rule:** Only verified code/tests change implementation status. Only owner-controlled evidence closes external gates. Documentation updates never manufacture implementation progress.


## CI verification correction — 20 November 2026

The exact current branch HEAD before this documentation refresh was `468d0aa4a348d997dc7affb71374bc8712cfc39d`. GitHub Actions reported all three workflows completed successfully for that exact SHA:

- Automated Tests — run `44642566787`: SUCCESS. Backend tests, frontend tests/build, dependency audits, synthetic SQLite outbox benchmark, backend container build, Redis/persistent-volume smoke test and Trivy scan all completed successfully.
- CodeQL Security Analysis — run `44642566989`: SUCCESS.
- Full Git History Secret Audit — run `44642566911`: SUCCESS.

This verifies the repository code and tests at that SHA. It does **not** prove multi-ASGI deployment, production Redis TLS/ACL provisioning, public WSS, Android/browser end-to-end acceptance, or any owner-controlled Gate closure. The earlier 62J-16 exact-code workflow attempts were cancelled by subsequent pushes; the full successful workflow ran on descendant SHA `468d0aa...`, which includes the 62J-16 code unchanged. Do not describe cancelled runs as failures or as successful runs.

## Next WebSocket engineering batch

Prioritize a reproducible two-ASGI-instance test harness over another isolated worker unit test. It must start two independently bound ASGI processes, share only the test Redis service, use distinct replica SQLite files, prove each gateway receives the same ordered event stream, and exercise restart/outage/re-snapshot paths. Inspect existing CI service orchestration before adding infrastructure. Do not wire workers into FastAPI startup until lifecycle ownership, snapshot provisioning, and TLS/ACL prerequisites are accepted.


## 62J-18 — Gate color and CI state reconciliation (20 November 2026)

The project owner clarified that all ten gates are ORANGE, not RED. The dashboard now uses 🟧 ORANGE to mean active/in progress and OPEN to mean not yet accepted/closed. These are separate dimensions: all ten remain OPEN (0/10 closed), but are not represented as abandoned or untouched. Gate IDs: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.

Latest branch HEAD at start of this batch: `ce4a88f24a4372a0e44c9797ef9a462d9fd81365`. Workflow runs on this SHA: Automated Tests `44643559339` was running backend tests; CodeQL `44643559332` had JavaScript/TypeScript successful and Python finishing; Full Git History Secret Audit `44643559363` succeeded. Do not report this SHA fully green until both running workflows finish successfully. The prior fully verified code HEAD remains `468d0aa4a348d997dc7affb71374bc8712cfc39d`.

Next technical acceptance batch remains two independently started ASGI processes, shared ephemeral Redis 7, separate replica SQLite files, then restart/outage/re-snapshot/cursor parity. The existing CI already provisions Redis 7 and a Docker network/volumes for container smoke; inspect and reuse those facilities rather than adding paid services or redundant infrastructure. No production startup wiring before ownership and recovery evidence.


## 62J-19 — Multi-ASGI integration boundary and CI reconciliation (20 November 2026)

Exact tested HEAD before this batch: 585132150a59ce7b3f2847007c9c5259ec5b2ef6.
- Automated Tests run 44643799617: SUCCESS.
- CodeQL run 44643799293: SUCCESS (Python and JavaScript/TypeScript).
- Full Git History Secret Audit run 44643799053: SUCCESS.

### Runtime integration inspection

Reviewed backend/app/main.py, ohlcv_redis_worker.py, ohlcv_redis_consumer.py, ohlcv_redis_publisher.py, ohlcv_replica_bridge.py, Settings validation and real-Redis process tests.

Confirmed:
- FastAPI lifespan starts the shared security guard and provider, but does not construct or own a Redis OHLCV replica worker.
- Existing WebSocket handlers still read the local source SQLiteOhlcvStore, OhlcvPipeline and OhlcvStreamHub.
- Redis consumer requires an already-installed verified replica snapshot before construction.
- Consumer callback is synchronous from the worker thread; EventLoopCallbackDispatcher is required to marshal replica updates onto the owning ASGI event loop.
- Existing process test proves two independent consumer processes and separate durable replica DBs, not two independently started ASGI servers.
- Snapshot installer currently consumes a local snapshot artifact. A production multi-host snapshot distribution contract is not established.

### Concrete blockers

1. Snapshot bootstrap/distribution: define how each gateway obtains the exact source snapshot artifact, verifies source identity/generation/hash/high-water, and safely installs it before accepting WebSocket traffic.
2. Runtime read path: add an explicit replica-backed WebSocket read adapter; do not silently mix local source-store snapshots with Redis-fed replica updates.
3. Lifecycle ownership: FastAPI lifespan must own exactly one worker and its Redis client per gateway instance, start only after verified snapshot install, and stop dispatcher/worker/client in a bounded order.
4. Multi-ASGI proof: run two actual ASGI processes on separate ports, same ephemeral Redis, different replica SQLite files; prove both clients observe identical ordered cursors and snapshot/replay/live boundary.
5. Failure matrix: restart one ASGI process, restart consumer worker, stop/restart Redis, reinstall a new snapshot generation, and verify no missing/duplicate/out-of-order cursor after recovery.
6. Production security: owner-provisioned Redis TLS, least-privilege per-instance ACL, credential rotation and target verification.
7. External acceptance: public WSS and browser/Android client checks; not reproducible from repository CI alone.

### Safe implementation order

A. Approve snapshot transport and artifact lifecycle.
B. Implement/test the replica-backed WebSocket adapter in isolation, preserving existing source-backed mode as default.
C. Add opt-in lifespan ownership with fail-closed startup and bounded shutdown.
D. Add two-process ASGI tests using the existing Redis 7 CI service and isolated SQLite files.
E. Add restart/outage/re-snapshot/cursor-parity scenarios.
F. Enable production mode only after TLS/ACL and owner-side evidence are available.

No runtime code was changed in 62J-19. The missing snapshot distribution contract is an architectural decision; choosing paid object storage, a Redis blob convention, or shared filesystem without owner approval would violate ZERO COST or multi-host assumptions. No production wiring is safe until this is decided. See docs/WEBSOCKET_MULTI_ASGI_INTEGRATION_BLUEPRINT.md.

## 0A. Batch 62J-22 — replica hydration consistency fix

**Audited branch base:** 3d93cbcd9a73a9d901b0407094e8bed462401b16  
**Scope:** replica SQLite snapshot consistency; source-backed WebSocket remains default; no production Redis startup wiring or deployment.

A race was found in hydrate_replica_pipeline(): checkpoint and bars were read through separate SQLite transactions. If the consumer committed between reads, the pipeline could hydrate bars newer than its recorded cursor. The fix adds SQLiteOhlcvReplicaStore.load_snapshot(), which reads checkpoint plus all retained bars in one explicit SQLite read transaction, then makes the bridge hydrate only from that atomic result.

Regression tests prove hydration does not use the old split-read methods and that missing verified snapshots fail closed. Exact-head CI is required before this change is considered verified.

**No production route switch was made in this batch.** The source SQLite route remains the default because the replica runtime still requires an explicit snapshot bootstrap contract and owner-provisioned dedicated Redis ACL/TLS credentials. Mixing source and replica cursor domains remains prohibited.

## 0B. Batch 62J-23 — opt-in FastAPI replica runtime

FastAPI now supports an explicit injected replica runtime factory. On startup, the app validates the replica store and matching consumer/client/stream, hydrates from the atomic SQLite snapshot, and only then starts one sequential worker on the owning app instance. In replica mode, the provider is not started, preventing competing source ingestion.

The WebSocket snapshot and replay paths now select a single cursor domain: source SQLite remains the default; explicitly injected replica mode reads snapshot/checkpoint and reconnect replay from the replica/Redis stream. No mixed cursor domain is permitted. Existing auth and entitlement checks remain in the shared route.

Two startup/snapshot regression tests were added, including fail-closed behavior for an unverified replica. The factory is not environment-enabled. Production snapshot distribution, dedicated TLS/ACL credentials, and independent multi-ASGI acceptance remain outstanding; no production secrets or paid services were introduced.

## 0C. Batch 62J-24 — Redis readiness and exact series fixture

Replica startup now verifies Redis consumer-group creation before the ASGI app becomes ready. If Redis group bootstrap fails, startup aborts, the dedicated client is closed, and no worker starts. The replica snapshot test fixture was aligned with the canonical 1-second timeframe policy (UTC_FIXED_V1).

## 0D. Batch 62J-25 — independent ASGI process acceptance

A new Redis 7 CI integration test launches two independent Uvicorn/FastAPI processes with separate replica SQLite files and consumer identities. Both subscribe through the real WebSocket route; one published event must reach both clients at cursor 1 and advance both durable replica checkpoints. This is the first acceptance test spanning the complete opt-in app lifecycle, replica consumer, event-loop dispatch and WebSocket route across two OS processes.

62J-25 exact series fixture note: process-level WebSocket subscription explicitly sets UTC_LEGACY to match the existing make_bar() fixture. No runtime series-matching relaxation is introduced.

62J-25 harness correction: child process imports for CanonicalInstrument and ProviderInstrumentMapping now target their actual modules (app.instrument_identity and app.instrument_registry).

## 0E. Batch 62J-26 — replica reconnect replay

The two-ASGI integration test now also reconnects a client with durable cursor 0 after both replicas have applied cursor 1. The route must replay the Redis event with cursor 1, mark it replayed, and report replay completion at cursor 1. This adds end-to-end repository evidence for the replica-backed reconnect/replay handoff; it does not close the external WSS Gate 36.
