# DEZZTA CHART — CURRENT PROJECT CONTROL DASHBOARD

**Checkpoint:** 20 November 2026 — Batch 62J-31 dual-gateway TCP outage recovery + snapshot generation acceptance  
**Active branch:** `phase-2/market-data-foundation`  
**Latest source/test checkpoint:** `cf6219a1f0fbea5a0daf8378ef47af386f8446fa`  
**Dashboard revision:** Batch 62J-29 documentation-only evidence reconciliation; no runtime behavior changed.  
**Current audit batch:** 62J-31 — dual-ASGI TCP outage recovery and dual-replica snapshot-generation acceptance passed exact-head CI  
**Cost policy:** ZERO COST. Existing Redis 7 CI service and temporary SQLite fixtures only; no paid providers, hosting, deployment, Vercel/Cloudflare action, or Termux requirement.

> This document is the current concise dashboard. Historical work-cycle reports remain the evidence trail. Do not infer that a docs-only commit has rerun or revalidated code CI.

## 0G. Batch 62J-28 — dual-gateway transient Redis read recovery (20 November 2026)

**Code/test HEAD:** ea19ce5ae6623ac09b23d36069960a5368dab3b0  
**Exact-head CI:** Automated Tests run [44704944924](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44704944924) SUCCESS • CodeQL run [44704944956](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44704944956) SUCCESS • Full Git History Secret Audit run [44704944887](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44704944887) SUCCESS.  
**Backend tests:** 1,164 passed in 40.74 seconds.

### New cross-process evidence

The real two-ASGI-process Redis 7 integration test now injects one transient xreadgroup connection failure independently into each gateway process. It records both fault triggers and waits for each gateway's subsequent successful Redis read before starting WebSocket status assertions. It then verifies:

- Both independent gateways recover without restarting their processes.
- Both WebSocket clients receive the same new durable event at cursor 1.
- Both replica SQLite checkpoints advance to cursor 1.
- Reconnect replay still returns cursor 1 with the replay handshake.
- One ASGI gateway can restart while retaining its replica database, then continue at cursor 2.
- Both surviving/restarted replica checkpoints converge at cursor 2.

The existing real-Redis snapshot-generation test also remains in the same passing backend suite: a replacement snapshot switches the consumer to a generation-scoped group, leaves the old pending group non-destructively isolated, starts the new group at the installed snapshot watermark, and applies the next cursor without mixing generations.

### Evidence boundary — E is not complete

The new test is deterministic client-boundary fault injection, **not** a shutdown or network partition of the Redis server. It proves two independent ASGI workers retry a transient Redis read error and restore cursor parity. It does not yet prove:

- A real Redis service/network outage and recovery while both gateways remain running.
- Snapshot-generation replacement and parity across both gateway replicas in one cross-process scenario.
- The production snapshot distribution/rotation contract.
- Production Redis TLS, ACL, credential rotation and host-level recovery.
- Public WSS acceptance from browser and Android WebView clients.

Therefore WebSocket failure/recovery matrix E remains **PARTIALLY VERIFIED**, not complete. No production readiness or Gate 10 closure is inferred from this CI evidence.

### Project controls

- Stage 1 remains 30/40 criteria = 300/400 ticks = **75% provisional**.
- Gate 10 remains **10/10 🟧 ORANGE; 0/10 formally closed**.
- Stages 2–6 remain unscored; overall project percentage remains unestablished.
- Indicator progress is unchanged. No visual indicator work was started.
- ZERO COST maintained. No deployment, paid service, main-branch modification, or Termux requirement.


## 0. Batch 62J-21 — documentation integrity + exact-head CI reconciliation (20 November 2026)

**Audited branch HEAD before this documentation update:** `99bc549e95341310945b987ab4ae11a86c962ea9`  
**Runtime code checkpoint:** `468d0aa4a348d997dc7affb71374bc8712cfc39d`  
**CI on exact branch HEAD `99bc549e95341310945b987ab4ae11a86c962ea9`:** Automated Tests run `44680830387` SUCCESS • CodeQL run `44680830205` SUCCESS • Full Git History Secret Audit run `44680830208` SUCCESS.

This is a documentation/evidence refresh and integrity repair. No runtime source or test code changed in this cycle. The runtime code checkpoint remains `468d0aa4a348d997dc7affb71374bc8712cfc39d`; `99bc549...` is a docs-only descendant. All three workflows completed successfully on exact HEAD `99bc549...`.

### Documentation integrity repair

The previous documentation update accidentally replaced the opening contents of `docs/INDICATOR_PROGRESS_LEDGER.md` with an object-string placeholder. This batch restores the complete ledger from its verified parent revision and appends the exact-head CI reconciliation. No indicator status or percentage is increased by this repair.

### WebSocket integration audit — supersedes the 62J-21 snapshot

The older 62J-21 statement that the replica worker and WebSocket route were not wired into FastAPI is historical and is superseded by batches 62J-22 through 62J-26. Current branch evidence at `5c5205ebc5d6b58b8e177854edb79f93ba9ea118` confirms:

- **A — Replica read model:** atomic replica bars/checkpoint snapshot, verified snapshot hydration, durable cursor checkpoint and bounded Redis replay are implemented.
- **B — FastAPI lifecycle:** explicit injected `replica_runtime_factory`, runtime identity validation, Redis consumer-group readiness, pipeline hydration before worker start, one managed sequential worker per app instance, provider suppression in replica mode, and bounded worker shutdown are implemented.
- **C — WebSocket route:** source SQLite remains the default; opt-in replica mode uses replica snapshot/checkpoint and Redis replay. The route does not combine source and replica cursor domains. Existing authentication, exact-series entitlement checks, lease refresh and queue handling remain in the shared route.
- **D — Independent ASGI acceptance:** Redis 7 CI launches two independent Uvicorn/FastAPI processes with separate replica SQLite files and consumer identities. Both clients receive the same live event/cursor and both durable checkpoints advance.
- **E — Failure/recovery matrix:** unit/integration coverage exists for pending reclaim, callback failure and retry, ACK-reply loss, consumer-group generation reset, cursor gaps/trim requiring resnapshot, worker retry/backoff and bounded shutdown, exact-series replay, and live/replay handoff. The two-ASGI test additionally reconnects with cursor 0 and verifies replay of cursor 1 through the actual route.

**Important boundary:** this is opt-in repository/CI integration, not production activation. Snapshot distribution remains owner-provisioned/local-artifact responsibility; production TLS/ACL credentials and public WSS/browser/Android acceptance are not supplied by CI. Do not enable replica mode in production or mark external gates closed from these tests alone.

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
- FastAPI now has an explicit opt-in replica runtime path with verified-snapshot hydration and managed worker lifecycle. Source-backed mode remains the default; production activation remains separately gated.

### Remaining WebSocket acceptance blockers — current position

1. **Production snapshot transport and lifecycle:** the runtime factory expects an owner-provisioned verified local replica snapshot. No production artifact distribution/rotation contract is selected.
2. **Failure matrix completion:** add real process-level restart/recovery scenarios for ASGI gateway restart, Redis outage/recovery, snapshot-generation replacement and post-recovery cursor parity. Existing lower-level tests cover several component failures, but not every scenario across two live ASGI processes.
3. **Production Redis security:** owner-provisioned TLS, least-privilege per-instance ACL credentials, credential rotation and target-environment verification.
4. **External acceptance:** public WSS endpoint, browser client and Android device end-to-end tests.
5. **Operational governance:** retention/stream trimming policy, authorized cleanup procedure, runbook and owner-side recovery drill.

The opt-in route/lifecycle and two-process ASGI proof are implemented. Do not repeat those as unstarted tasks. Do not mix cursor domains, enable production mode without verified snapshot/TLS/ACL prerequisites, or close Gate 25/34/36 based on CI-only evidence.

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


## 0F. Batch 62J-27 — exact-head integration and indicator reconciliation (20 November 2026)

**Audited branch HEAD:** `5c5205ebc5d6b58b8e177854edb79f93ba9ea118`  
**Exact-head CI:** Automated Tests run `44686658866` SUCCESS • CodeQL run `44686658770` SUCCESS • Full Git History Secret Audit run `44686658757` SUCCESS.

The latest commit adds the reconnect replay assertion to the real two-ASGI-process test. The test now verifies both independent gateway replicas receive live cursor 1, then a reconnecting WebSocket client supplies cursor 0 and receives replay_started (0→1), the replayed event at cursor 1, and replay_complete at cursor 1. This is an actual FastAPI/WebSocket route test, not only a helper-level simulation.

**A–D status:** implemented and CI-verified for the opt-in repository path. **E status:** partially complete; cross-process restart, Redis outage/recovery, snapshot-generation replacement and full recovery parity still need dedicated acceptance scenarios. Production snapshot transport, TLS/ACL provisioning and public WSS/browser/Android acceptance remain external prerequisites.

**Indicator progress — unchanged by transport work:** SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨; Footprint 🟧 SIMULATED/gated; Heatmap 🟥; Liquidation Maps 🟥. Formula and warm-up contracts remain unchanged. Do not award indicator completion for WebSocket CI.

**Project control:** Stage 1 remains 30/40 criteria = 300/400 ticks = 75% provisional. Gate 10 remains 10/10 🟧 ORANGE and 0/10 formally closed. Overall project percentage and aggregate indicator percentage remain unscored because their approved weights/denominators are absent.

No runtime source code was changed in this reconciliation. No deployment, paid infrastructure, Vercel/Cloudflare action, `main` modification or Termux work was performed.


## 0H. Batch 62J-29 — exact-head CI, Gate 10 and indicator reconciliation (20 November 2026)

**Audited branch HEAD:** `ea3626cd9e174d0f9a06af2b0fe2550c830e0559`  
**Automated Tests:** [44705774297](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44705774297) — SUCCESS; backend pytest passed (1,164 tests), frontend tests/build, dependency checks, container build and container smoke completed successfully.  
**CodeQL:** [44705774202](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44705774202) — SUCCESS (JavaScript/TypeScript and Python).  
**Full Git History Secret Audit:** [44705774189](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44705774189) — SUCCESS.

This verifies the exact current branch HEAD. The immediately preceding runtime/test behavior checkpoint remains Batch 62J-28; the 62J-29 documentation reconciliation does not claim new WebSocket behavior.

### WebSocket E — remaining acceptance work

- 🟩 A–D: repository/CI evidence remains verified for the explicit opt-in replica path, FastAPI lifecycle, source/replica route handoff and independent ASGI gateways.
- 🟨 E: partially verified. The dual-ASGI test injects a transient failure at the Redis client's `xreadgroup` boundary and proves recovery, replay, restart and cursor parity.
- Outstanding: a real TCP/network interruption affecting both gateway processes; a coordinated two-replica snapshot-generation replacement test; post-recovery parity for that combined scenario; production snapshot distribution/rotation; production TLS/ACL/credential rotation; browser and Android WSS acceptance; retention/cleanup governance and recovery drill.

Do not label the current client-boundary fault injection as a Redis server outage. Do not close Gates 25, 34 or 36 from CI alone.

### Gate 10 — ten-gate control board

| Gate | Status | Remaining independent acceptance |
|---:|---|---|
| 8 | 🟧 OPEN | Actual owner-host secret injection, permissions and runtime leakage review |
| 20 | 🟧 OPEN | Real no-billing Firebase sign-in/revocation/entitlement plus browser and Android flow |
| 25 | 🟧 OPEN | Owner-controlled Redis TLS/ACL, persistence, outage and recovery |
| 30 | 🟧 OPEN | Restore drill on the intended owner-controlled target |
| 31 | 🟧 OPEN | Off-host encrypted artifact and separately controlled recovery key |
| 34 | 🟧 OPEN | Actual host volume, restart, disk-pressure and recovery evidence |
| 35 | 🟧 OPEN | Owner-host HTTPS endpoint and certificate validation |
| 36 | 🟧 OPEN | Browser/Android WSS, platform lifetime, effective runtime configuration and cross-instance acceptance |
| 38 | 🟧 OPEN | Protected host collector/dashboard, bounded retention and disk-pressure evidence |
| 39 | 🟧 OPEN | Responsible adult operator, verified escalation channel and observed acknowledgement/recovery drill |

**Gate 10: 10/10 ORANGE, 0/10 formally closed.** ORANGE means active/open, not passed. Several items require an owner-controlled host, provider or operator that CI cannot manufacture. ZERO COST remains mandatory; if a safe no-cost path is unavailable, defer rather than enable billing or weaken controls.

### Indicator progress — full status unchanged

| Indicator / subsystem | Status | Verified foundation | Remaining work |
|---|---|---|---|
| SMA 20 | 🟨 | Rolling mean; first valid index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| EMA 20 | 🟨 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| RSI 14 | 🟨 | Wilder smoothing; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend, stale clearing and render tests |
| MACD 12/26/9 | 🟨 | MACD first valid index 25; signal/histogram index 33 | Dedicated pane, lines, histogram, zero guide, toggle, legend and render tests |
| Bollinger 20,2 | 🟨 | SMA20 ± 2 population standard deviations; first valid index 19 | Three-line overlay, toggle, legend/value, stale clearing and render tests |
| Shared indicator hook | 🟨 | Validated backend snapshot only; no DEMO fallback | Active chart identity/timeframe binding, loading/error states and cross-series isolation |
| Footprint | 🟧 | Deterministic educational accumulator, explicitly SIMULATED | Owner reference image + reviewed blueprint; ON-only spaced cluster layout; OFF keeps standard candles |
| Heatmap | 🟥 | No implementation verified | Owner reference, reviewed blueprint, source/calculation contract, renderer and tests |
| Liquidation Maps | 🟥 | No validated source/calculation contract | Source feasibility, reference/blueprint, calculations, renderer and tests |

**Indicator progress is not assigned a fabricated percentage.** WebSocket CI does not count as indicator UI progress. Visible indicator implementation remains Stage 4 work; current official stage remains Stage 1. No indicator rendering work was started.

### Project accounting

- Stage 1: **30/40 criteria = 300/400 ticks = 75% provisional**.
- Gate 10: **10/10 🟧 ORANGE; 0/10 closed**.
- Stages 2–6: not scored.
- Overall project percentage: not established; M1–M8 weights are not approved.
- ZERO COST: no paid service, deployment, production activation or main-branch modification.
- Termux: not required for this CI/documentation cycle. Native Termux backend acceptance remains incomplete in the existing device-readiness record; no installation command is being issued.


## 0I. Batch 62J-31 — dual-gateway TCP outage + snapshot-generation acceptance (20 November 2026)

**Exact source/test HEAD:** `cf6219a1f0fbea5a0daf8378ef47af386f8446fa`

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44708222353](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708222353) | SUCCESS |
| CodeQL | [44708222403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708222403) | SUCCESS — Python + JavaScript/TypeScript |
| Full Git History Secret Audit | [44708222417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708222417) | SUCCESS |

**Test totals:** backend **1,166 passed** (6 warnings); frontend **236 passed across 28 files**. Backend container build, smoke test, image scan and report export also completed successfully.

### New WebSocket failure-matrix evidence

1. **Real TCP path interruption across two ASGI gateways:** each gateway has its own local TCP proxy to Redis. The test waits for established gateway-to-Redis sockets, severs both connections, rejects reconnect attempts during the controlled outage, restores both paths, then publishes cursor 1. Both original ASGI processes remain alive, both WebSocket clients receive cursor 1, and both durable replica checkpoints advance to 1. This is a controlled TCP network-path interruption, not a Redis server shutdown.
2. **Snapshot-generation replacement across two independent gateway replicas:** both replicas apply cursor 1; cursor 2 is left pending in each old generation group; the same verified snapshot at watermark 2 is installed in both durable replica databases; two separately spawned gateway consumer processes start with the new generation, apply cursor 3, and converge at checkpoint 3. Old pending entries remain isolated and are not destroyed.

**Failure-matrix disposition:** the two previously missing automated acceptance scenarios—dual-gateway TCP interruption/recovery and cross-process two-replica generation replacement with post-install cursor parity—are now covered and passed in CI. The automated repository/CI failure matrix E is **COMPLETE FOR THE DEFINED TEST SCOPE**.

**Production WebSocket readiness is still NOT accepted.** Snapshot distribution/rotation, production TLS/ACL/credential rotation, external browser/Android WSS acceptance, stream retention/cleanup governance and owner-operated recovery drills remain independent operational requirements. Do not claim production readiness or close Gate 25/34/36 from CI alone.

### Gate 10 follow-through

The new tests strengthen repository evidence relevant to Gate 25 (Redis connection interruption/recovery, per-gateway consumer groups and cursor parity). Gate 25 remains 🟧 OPEN until the owner-controlled Redis host, TLS, ACL, persistence and recovery environment is independently verified. Gate 36 remains 🟧 OPEN until authenticated public WSS, browser/Android client behavior and platform/runtime lifetime are accepted.

All ten gates remain 🟧 ORANGE / OPEN: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39. No external gate is closed by CI.

### Indicator and project accounting

Indicator implementation status remains unchanged: SMA20 🟨 (first index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (MACD 25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧 (SIMULATED; owner reference/blueprint required), Heatmap 🟥, Liquidation Maps 🟥. No indicator UI work or percentage credit is awarded for WebSocket tests.

Stage 1 remains 30/40 = 300/400 = **75% provisional**. Stages 2–6 remain unscored. Overall project percentage remains unestablished. ZERO COST maintained; no deploy, paid service, Termux action or main-branch change.
