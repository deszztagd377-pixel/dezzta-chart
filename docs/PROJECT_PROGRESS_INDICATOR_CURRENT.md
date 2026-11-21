# DEZZTA CHART — CURRENT PROJECT CONTROL DASHBOARD

**Checkpoint:** 21 November 2026 — Batch 62J-55 WebSocket exact-head integration reconciliation
**Active branch:** `phase-2/market-data-foundation`
**Latest runtime/source-test HEAD:** `56317eff2b71886040acb998bf692814622feedf` (Redis consumer lease, worker/lifespan integration, ACL and regression tests). **Current documentation branch HEAD before this refresh:** `0251e5b7d2915bee723dc47895b950250c26e50c`.
**Exact-head CI:** Automated Tests [44774049019](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44774049019) **SUCCESS** — frontend **245/245 across 29 files**; backend **1,218 passed, 6 warnings in 35.76s**. CodeQL [44774050265](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44774050265) **SUCCESS** • Full Git History Secret Audit [44774048914](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44774048914) **SUCCESS**.
**Audit evidence:** frontend dependency audit 0 vulnerabilities; backend dependency audit no known vulnerabilities; frontend source/bundle secret scan, backend container build, Redis ACL/AOF + mounted-volume smoke test, Trivy scan/report export all completed successfully.
**WebSocket E:** COMPLETE FOR THE DEFINED AUTOMATED FAILURE-MATRIX SCOPE. This is distinct from Gate 20's real Firebase identity and browser/Android acceptance.
**Gate 20:** repository regression coverage strengthened for single-use/expiry/purpose, cross-account renewal rejection, and entitlement revocation during renewal. Real Firebase project signed-token/session acceptance and browser/Android reconnect remain OPEN.
**Gate 10:** **10/10 🟧 OPEN; 0/10 formally closed** — gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.
**Stage 1:** 30/40 criteria = 300/400 ticks = **75% provisional**; no new acceptance tick awarded by this cycle.
**Stages 2–6:** not scored. **Overall project percentage:** not established; M1–M8 weighting/acceptance denominator remains unapproved.
**Indicator aggregate:** not scored; no approved weights/denominator. Individual status remains in the complete indicator ledger below.
**Cost/device boundary:** ZERO COST. No paid provider, hosting, subscription, deployment, Vercel or Cloudflare action. No Termux/device operation was run in this cycle. `main` remains untouched.

> This document is the current concise dashboard. Historical work-cycle reports remain the evidence trail. Distinguish the latest source/test HEAD from a documentation-only branch HEAD, and cite CI only for the exact SHA shown by each run.



## Batch 62J-54 — Gate 31 / 38 / 39 source audit (21 November 2026)

- **Gate 31:** encrypted SQLite backup code and AES-256-GCM artifact support are present, but off-host storage, independent key custody, retention/access controls and owner-host key-recovery restore remain unverified.
- **Gate 38:** bounded process-local metrics and a token-protected endpoint are implemented; collector, dashboard, cross-process aggregation, retention and owner-host access verification remain open.
- **Gate 39:** persistent incident journal, bounded escalation and sanitized local logging are implemented; verified alert receiver, log operations, named operator and real escalation/recovery drill remain open.
- No repository-level defect was established and no source code changed. All Gate 10 criteria remain open; Stage 1 stays 30/40 = 75% provisional. No acceptance tick is awarded.
- Owner-host tasks must be handled by a responsible adult owner/authorized maintainer. Do not share production credentials or encryption keys in chat. No Termux/device command is required for this source audit.
## Batch 62J-53 — Redis consumer ownership guard (21 November 2026)

- A token-fenced, generation-scoped Redis lease now enforces one active consumer process per local replica group. Startup acquires the lease before Redis group initialization; another process using the same replica identity fails closed.
- Lease renewal, ownership checks and release are token-checked. The consumer verifies ownership before applying each event and before ACK. Transient Redis transport uncertainty pauses processing/ACK and retries verification; a successor token is never overwritten.
- A missing ephemeral lease key may be reacquired only with `SET NX`; generation-scoped keys allow a new snapshot generation to proceed independently of the old one.
- Restricted gateway ACL adds the lease namespace and `SET/EVAL/GET/PEXPIRE/DEL`; publisher ACL remains unchanged. No `XGROUP DESTROY` permission is added.
- CI exercises two-process contention, independent replica identities, TTL takeover, stale-owner fencing, lease-loss-before-ACK, Redis interruption/recovery, and generation separation.
- Exact-head CI is 3/3 successful; see run links in the checkpoint above. This closes the identified **repository-level WebSocket consumer-exclusivity defect**, not Gate 20/25 production acceptance.
- Gate 10 remains **0/10 closed**. Stage 1 remains **30/40 = 75% provisional**. Indicator implementation is unchanged; no indicator score is awarded.
- No production Redis, deployment, paid service, Termux/device action, or `main` change.

## Batch 62J-47 — cross-account WebSocket ticket renewal regression (20 November 2026)

**Exact source/test HEAD:** `826bae749f48e844f5fddb82dfec396bb3f9baa7`

- Added `test_websocket_ticket_renewal_rejects_ticket_for_different_subject` in `backend/tests/test_api.py`.
- The test authenticates a socket as account A, then attempts renewal using a valid single-use ticket issued to account B. It verifies the server rejects the mismatched subject and closes with code `4401`.
- This is regression coverage for an existing server-side subject comparison; no production runtime code or protocol changed.
- Exact-head Automated Tests & Build [44751619536](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44751619536): **SUCCESS** — frontend 245/245 across 29 files; backend 1,198 passed with 6 warnings. Frontend dependency audit reported 0 vulnerabilities; backend dependency audit reported no known vulnerabilities. Container build, Redis ACL/AOF + mounted-volume smoke test, Trivy HIGH/CRITICAL scan and report export passed.
- Exact-head CodeQL [44751619516](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44751619516): **SUCCESS**. Full Git History Secret Audit [44751619621](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44751619621): **SUCCESS**.
- Detailed evidence: [WORK_CYCLE_2026-11-20_BATCH62J47_CROSS_ACCOUNT_WEBSOCKET_RENEWAL.md](WORK_CYCLE_2026-11-20_BATCH62J47_CROSS_ACCOUNT_WEBSOCKET_RENEWAL.md).
- Gate 20 remains 🟧 OPEN pending real Firebase project and client acceptance. Gate 10 remains 0/10 closed. Stage 1 remains 30/40 criteria = 300/400 ticks = 75% provisional; no tick awarded. No Termux operation, deployment, paid service, or `main` modification.

## Batch 62J-46 — bounded Firebase ID-token acquisition (20 November 2026)

**Exact source/test HEAD:** `4af91275f4830006934bc765671c92a80e51733a`

- The frontend OHLCV stream supervisor now bounds Firebase ID-token acquisition to 10 seconds by default (configurable, maximum 60 seconds) for both initial connection and WebSocket ticket renewal.
- Pending token acquisition is cancelled when the supervisor is explicitly stopped. Existing terminal authentication and entitlement behavior is unchanged.
- Added two regression tests: a token provider promise that never settles during initial connection, and one that never settles during ticket renewal.
- Exact-head Automated Tests & Build [44748261197](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44748261197): **SUCCESS**. Frontend: **245 tests across 29 files passed**. Backend: **1,197 passed, 6 warnings in 55.67 seconds**. Frontend dependency audit, source/bundle secret scans, Android preflight/publisher tests, synthetic outbox benchmark, backend dependency audit, backend container build, Redis/persistent-volume smoke test, container scan and vulnerability-report export all completed successfully.
- Exact-head CodeQL [44748261632](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44748261632): **SUCCESS** for JavaScript/TypeScript and Python.
- Exact-head Full Git History Secret Audit [44748261135](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44748261135): **SUCCESS**.
- Android debug APK build [44748261425](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44748261425): **SUCCESS**. Short-lived artifact `dezzta-chart-android-debug-apk` (artifact ID `14633533477`, 3,877,408 bytes) expires 27 November 2026. This is a CI artifact only; no preview release was published.
- Two intermediate test runs exposed and then isolated test-timing defects; the final exact-head run above passed all checks. No failed intermediate result is represented as current acceptance.
- Stage 1 remains **30/40 = 75% provisional**; no tick is awarded for this transport hardening. Gate 10 remains **0/10 formally closed**. The ten external criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.
- No Termux/device command, live Firebase credential, provider feed, production host, public WSS, DNS, tunnel, paid service, deployment or `main` modification was used.


## Remote access architecture decision — 20 November 2026

- Added `docs/REMOTE_ACCESS_ARCHITECTURE.md` to record the target clients, network model, zero-cost boundary, and the difference between sideloading an APK and operating a reachable backend.
- No server has been purchased or provisioned. No external tunnel, VPN, public DNS, paid domain, Vercel, Cloudflare, or deployment was configured.
- Current practical baseline: Android local/LAN host for controlled tests; public cross-network service remains blocked by lack of an always-on owner-controlled host and verified inbound/reverse-tunnel path. A phone-hosted service is not 24/7 reliable because Android background limits, power, network changes and carrier NAT remain operational constraints.
- Stage 1 and Gate 10 accounting unchanged. Architecture documentation earns no acceptance tick.

## Batch 62J-45 — Gate 30 restore-drill preparation (20 November 2026)

- Added `docs/GATE30_OWNER_HOST_RESTORE_DRILL_RUNBOOK.md` after inspecting the actual restore-drill implementation, backup helper, runtime configuration and regression tests.
- Confirmed the live database path is selected by `INSTRUMENT_REGISTRY_DB_PATH`, with `./data/instrument_registry.sqlite3` as a fallback relative to backend process working directory. GitHub source cannot reveal the live process environment or host.
- Capacity planning uses `3 × source database size + max(64 MiB, 10% of 3 × size)` additional free space, accounting conservatively for backup temporary + retained backup + restore temporary allocations and safety margin.
- The existing drill is read-only against source, refuses existing output destinations, verifies integrity/foreign keys/schema/table row hashes/application-domain readback/outbox uniqueness and a committed write → fresh read → cleanup probe.
- Gate 30 remains 🟧 OPEN. No device command was run; permission to use Termux does not provide this chat with a remote device shell. The drill must run on the actual backend host, not an unrelated phone-side copy. No Stage 1 tick is awarded for documentation.

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

### Historical evidence boundary — superseded by Batch 62J-31

At Batch 62J-28, the test covered only client-boundary transient read-failure injection. That limitation was resolved by Batch 62J-31, whose exact-head CI added two further acceptance scenarios:

- Two live ASGI gateways use separate local TCP proxies; both established Redis paths are severed, reconnects are rejected during the controlled outage, and both paths are restored without restarting either gateway. Both WebSocket clients then receive cursor 1 and both durable checkpoints converge at cursor 1. This is a controlled TCP-path interruption, not a Redis server shutdown.
- Two independent gateway replicas install the same verified snapshot at watermark 2 after leaving cursor 2 pending in the old generation groups. New-generation consumers apply cursor 3 and both durable checkpoints converge at 3; old pending entries remain isolated.

**WebSocket E is COMPLETE FOR THE DEFINED AUTOMATED FAILURE-MATRIX SCOPE.** Production snapshot distribution/rotation, owner-host Redis TLS/ACL/credential rotation, retention/cleanup governance, public WSS, browser/Android acceptance and operator recovery remain separate open requirements. E completion does not close Gate 25 or Gate 36.

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
| 8 | 🟧 OPEN | Actual host secret injection, file ownership/mode, process exposure, log and crash-report redaction |
| 20 | 🟧 OPEN | Real Firebase sign-in, expiry/revocation, entitlement denial, browser/Android reconnect against an accepted backend |
| 25 | 🟧 OPEN | Owner-host Redis TLS certificate, ACL/network policy, credential rotation, persistence and recovery; relay snapshot contract |
| 30 | 🟧 OPEN | Owner-device fresh-path SQLite backup/restore report, application-domain readback, integrity and recovery timing |
| 31 | 🟧 OPEN | Encrypted off-host artifact, separate recovery-key custody, independent restore and retention/deletion evidence |
| 34 | 🟧 OPEN | Actual persistent mount/path, UID/GID and permissions, process-restart persistence, disk-pressure and recovery |
| 35 | 🟧 OPEN | Owner-controlled HTTPS backend, certificate/hostname verification, health/startup and secret-injection checks |
| 36 | 🟧 OPEN | Authenticated public WSS reverse-proxy, browser and Android acceptance, reconnect/replay and proxy restart |
| 38 | 🟧 OPEN | Bounded metrics/log retention, dashboard access control, disk-pressure behavior and credential redaction |
| 39 | 🟧 OPEN | Induced-failure alert, operator acknowledgement/escalation and tested incident recovery |

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


## 0J. Batch 62J-32 — Gate 25/36 source and CI evidence audit

### Gate 25 — Redis

<badge color="warning">OPEN — owner-host acceptance pending</badge>

**Verified in source/CI**
- Production configuration requires an authenticated `rediss://` URL.
- Redis TLS client requires CA-chain validation and hostname verification.
- Disposable Redis 7 CI test: default user disabled; ephemeral ACL; exact key scope; restricted commands; AOF enabled; ACL file persisted on temporary volume.
- Negative tests deny anonymous access, wrong password and unrelated key writes.
- Redis stop produces fail-closed HTTP 503; Redis restart preserves AOF canary and ACL; backend restart recovers.
- Separate publisher/gateway relay ACL permissions are covered by Redis 7 integration tests.

**Not yet evidenced**
- Live TLS handshake/certificate identity against the owner host.
- Owner-host ACL and network/firewall provisioning.
- Publisher/gateway secret injection and rotation on target host.
- Production relay activation; its config is deliberately not wired until snapshot transport and owner credentials are approved.

### Gate 36 — public WSS

<badge color="warning">OPEN — public endpoint and client acceptance pending</badge>

Backend WebSocket authentication and entitlement rechecks exist in source. Public reverse-proxy handshake, browser, Android WebView and deployed cross-instance acceptance remain unverified. The purpose-bound ticket exchange is implemented: Firebase Bearer over HTTPS obtains a 90-second single-use ticket; the WebSocket client renews it over HTTPS and uses an acknowledged same-subject renewal frame. Current tickets are not series/Origin-bound; exact-series entitlement is checked separately. No deployment was triggered.

### Status controls

Gate 10 remains **10/10 🟧 ORANGE / 0/10 closed**. Stage 1 remains **75% provisional**; Stages 2–6 unscored; overall project percentage not established. Indicator dashboard is unchanged; no WebSocket or Gate 25 evidence is credited as indicator progress. ZERO COST maintained.


## 20 November 2026 — Batch 62J-34 Gate 8/38/39 operational hardening

**Branch:** `phase-2/market-data-foundation`  
**Parent:** `3d3f3c7a481e78bc9c09b966c1fbf1f70091517d`

### Scope and changes
- Gate 38: `/internal/metrics` and `/internal/alert-delivery` remain disabled unless an owner-injected operator token is configured, and both require an exact Bearer token validated with constant-time comparison.
- Gate 38: both internal scrape endpoints now stay out of their own request counters and HTTP request logs. This prevents monitoring scrapes from contaminating application traffic metrics.
- Gate 8: regression coverage verifies unauthenticated and wrong-token requests are denied, successful operator requests are no-store, and neither query sentinels nor the operator token appear in returned metrics/status payloads.
- Gate 39: regression coverage verifies capped exponential retry timing, due-time boundaries, durable attempt counts, and safe terminal handling when a retry timestamp would exceed SQLite signed-int64.
- No notification provider, hosted monitoring service, external alerting SaaS, paid service, or deployment was added.

### Evidence boundary
These are repository-level regression tests. They do not prove owner-host secret injection, process/log access controls, dashboard access policy, disk retention, operator acknowledgement/escalation, or an actual production incident drill. Gates 8, 38 and 39 remain ORANGE / OPEN pending their external acceptance criteria.

### Indicator status (unchanged)
- SMA 20 🟨 — rolling arithmetic mean; first valid candle index 19; chart overlay/lifecycle acceptance remains.
- EMA 20 🟨 — SMA-seeded EMA, alpha 2/21; first valid index 19; chart overlay/lifecycle acceptance remains.
- RSI 14 🟨 — Wilder smoothing; first valid index 14; oscillator pane/lifecycle acceptance remains.
- MACD 12/26/9 🟨 — MACD first valid index 25; signal and histogram index 33; pane/render acceptance remains.
- Bollinger 20,2 🟨 — population standard deviation; first valid index 19; overlay/render acceptance remains.
- Shared Indicator Hook 🟨 — validated backend snapshot; chart identity/timeframe binding and stale-state lifecycle remain.
- Footprint 🟧 — SIMULATED only; waits for owner reference image and reviewed blueprint; OFF preserves standard candle spacing.
- Heatmap 🟥 — not implemented; waits for reference image, approved blueprint and validated data contract.
- Liquidation Maps 🟥 — no validated data/calculation contract.

No indicator implementation changed in this batch; no indicator completion credit is awarded.

### Project accounting
- Stage 1: 30/40 = 75% provisional (unchanged).
- Stages 2–6: unscored.
- Gate 10: 10/10 ORANGE, 0 formally CLOSED.
- Overall project percentage: not established; M1–M8 weights remain unapproved.
- Indicator aggregate percentage: not established; no approved weighted acceptance denominator.

### Validation plan
Run the exact-head Automated Tests, CodeQL (JavaScript/TypeScript and Python), and Full Git History Secret Audit workflows. A workflow failure blocks this batch from being reported as verified. No Vercel/Cloudflare deployment is needed.

## 20 November 2026 — Batch 62J-35 Gate 39 partial fan-out retry contract

Added a regression test for the multi-device delivery boundary: when recipient A accepts an alert and recipient B returns a retryable provider failure, the durable event remains retryable and the next attempt may send to A again. Every attempt carries the same immutable event_id, which is the client-side deduplication key. This explicitly tests the documented at-least-once behavior rather than incorrectly claiming exactly-once provider delivery.

This is adapter-level evidence with a deterministic fake sender. It does not prove Firebase production delivery, Android notification deduplication, bounded provider latency, operator acknowledgement/escalation, or an owner-host incident drill. Gate 39 remains 🟧 OPEN. No indicator implementation changed; indicator statuses and formula warm-up contracts remain unchanged. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall project percentage not established. Gate 10 remains 10/10 🟧 ORANGE / 0 closed. ZERO COST; no deployment, paid service, Termux action or main-branch change.


## 20 November 2026 — Batch 62J-36 Gate 39 FCM timeout/shutdown audit

The Batch 62J-35 exact-head CI suite passed all three workflows. A source audit then identified an unresolved delivery bound: Firebase Admin initialization does not set `httpTimeout`, so the SDK default is 120 seconds per HTTP request; the event sender fans out sequentially to as many as 10 active installations; and lifespan shutdown awaits the worker after setting its stop event, which is observed only after the current batch returns. This means neither total event time nor graceful shutdown has a strict application-level bound. The SDK's retry policy can extend elapsed time beyond one request timeout.

No `asyncio.wait_for` cancellation patch was applied: cancelling the await on `asyncio.to_thread` does not terminate its running thread and could allow provider sends to continue after lease expiry, creating a reclaim/duplicate-delivery race. A safe follow-up must define and test provider request/retry bounds, calculate a lease budget for the maximum recipient fan-out plus acknowledgement margin, and specify shutdown semantics. Gate 39 remains 🟧 OPEN. Indicator statuses/formula warm-up indices unchanged; no indicator credit. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall percentage unestablished. Gate 10 remains 10/10 ORANGE / 0 closed. ZERO COST; no deployment, Termux, dependency change, or main-branch modification. See `WORK_CYCLE_2026-11-20_BATCH62J36_GATE39_FCM_TIMEOUT_SHUTDOWN_AUDIT.md` for full evidence and calculations.


## Batch 62J-37 — Gate 38 metrics audit and Gate 39 bounded-worker proposal (20 November 2026)

The source audit confirms that request metrics are bounded to 127 process-local route/method series including overflow, with fixed latency buckets, sanitized labels/status/durations, detached snapshots and lock-protected recording. Private scrape routes require constant-time Bearer authentication, no-store headers and are excluded from application request logs/counters. This does not provide cross-replica aggregation, a dashboard, host log retention/rotation or disk-pressure acceptance. Gate 38 remains 🟧 OPEN.

Gate 39 remains 🟧 OPEN. A design proposal has been recorded in docs/WORK_CYCLE_2026-11-20_BATCH62J37_GATE38_METRICS_GATE39_BOUNDED_WORKER_DESIGN.md. It recommends parent-supervised child-process isolation for one event's synchronous FCM fan-out, with a monotonic hard deadline, parent-owned token revocation/acknowledgement and explicit at-least-once semantics. Candidate timing arithmetic is documented but is not accepted production configuration. This is a major runtime architecture decision: **no implementation is authorized until the owner reviews and approves the proposal**.

Exact starting HEAD: 04139cf0b43812c4afd09e8b5114d15df1aa2be9. This batch is documentation-only; exact-head CI for the starting revision was still running at the time of the audit. Gate 10 remains 10/10 ORANGE / 0 CLOSED. Indicator states unchanged. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall percentage not established. ZERO COST; no deployment, paid service, Termux or main branch change.


## 20 November 2026 — Batch 62J-38 WebSocket ticket deadline and Android update-readiness

The WebSocket ticket client now enforces a 10-second AbortController deadline across both fetch and JSON body parsing. Six focused tests cover the request policy, 401 preservation, header/body timeout, payload validation and invalid credentials. Exact source/test HEAD `734cd20d7525e9d67f6a045dc13a98410e26cdd0` passed Automated Tests & Build, CodeQL, full-history Secret Audit and Android debug APK build. Frontend: 242 tests / 29 files; backend: 1,172 passed / 6 warnings. Container build, shared Redis/persistent-volume smoke and image scan/report export passed.

Android workflow remains a debug APK pipeline with short-lived artifact retention and opt-in preview release. It is not yet a production update system. Stable owner-controlled signing, protected CI secrets, signed update manifest, SHA-256 verification, version/schema migration, offline key backup and user-confirmed Android installer handoff are required. Public GitHub Releases are the proposed zero-cost distribution path. A normal Android app cannot silently install sideloaded updates. No 100-year guarantee is possible; maintainability is pursued through open data formats, migration tests, dependency/security maintenance, signed release artifacts and reproducible build records. Termux was not needed in this batch; any future phone-side signing operation will be announced and approved first.

WebSocket E is complete for defined automated CI scope; public WSS/owner-host acceptance remains open. Gate 10 remains 10/10 ORANGE / 0 closed. Indicator statuses unchanged: SMA20/EMA20 🟨 index 19; RSI14 🟨 index 14; MACD12/26/9 🟨 index 25, signal/histogram 33; Bollinger20,2 🟨 index 19; Shared Hook 🟨; Footprint 🟧 SIMULATED; Heatmap 🟥; Liquidation Maps 🟥. No indicator credit. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall percentage unestablished.


## 20 November 2026 — Batch 62J-39 WebSocket ticket-endpoint retry regression

Added an end-to-end supervisor regression test for a transient HTTPS ticket-endpoint failure. The first ticket request now has an explicit test outcome: no WebSocket is constructed, supervisor enters reconnecting state, the bounded reconnect delay is observed, a fresh Firebase ID token is obtained, and the second ticket request succeeds before the WebSocket is constructed. This complements the existing transient identity-token acquisition test and the 10-second abortable ticket request tests from Batch 62J-38.

This batch does not alter WebSocket production runtime code or the wire protocol. It adds regression coverage only. The exact resulting commit's CI is the acceptance authority; do not mark it green until Automated Tests/Build, CodeQL and full-history secret audit all finish successfully.

Gate 39 bounded FCM child-process isolation remains a reviewed design proposal, not an implementation. No unsafe thread cancellation or guessed provider timeout/lease multiplication was introduced. Gate 30 repository-side SQLite restore drill remains extensively tested but owner Android database acceptance remains external. Gate 38 remains process-local bounded metrics with host retention/dashboard acceptance open. Gate 10 remains 10/10 🟧 ORANGE / 0 closed.

Indicator dashboard remains unchanged: SMA20 🟨 (first valid index 19); EMA20 🟨 (alpha 2/21, first index 19); RSI14 Wilder 🟨 (first index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram 33); Bollinger20,2 🟨 (population standard deviation, first index 19); Shared Indicator Hook 🟨; Footprint 🟧 SIMULATED and gated on owner reference plus reviewed blueprint; Heatmap 🟥; Liquidation Maps 🟥. No indicator code changed and no indicator completion credit is awarded. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall project and indicator aggregate percentages remain unestablished.

ZERO COST: no paid service, deployment, Vercel/Cloudflare action, Termux operation, dependency change, or main branch modification.


### Batch 62J-39 CI correction note

The first exact-head Automated Tests run caught an incorrect regression-test timing assumption. The supervisor's full-jitter formula produces a 50 ms first retry when `minReconnectDelayMs=100` and `random()=0`; the test incorrectly assumed 100 ms. The test is corrected to assert no retry at 49 ms and retry at 50 ms. This does not change production backoff behavior. The corrected exact-head CI is pending and remains the acceptance authority.


### Batch 62J-39 exact-head CI closure

Source/test HEAD `13d0b48adf8fbd040b22689e83160b2945f07a5c` passed all four exact-head workflows:
- Automated Tests & Build: run 44719780403 SUCCESS.
- CodeQL JavaScript/TypeScript + Python: run 44719780163 SUCCESS.
- Full Git History Secret Audit: run 44719780242 SUCCESS.
- Android debug APK build: run 44719780305 SUCCESS; preview publication skipped.

Frontend: 243 tests across 29 files. Backend: 1,172 passed, 6 warnings in 43.42 seconds. Frontend build and secret scans, backend dependency audit, backend container build, shared Redis guard/persistent-volume smoke, container image scan and vulnerability-report export all passed. This validates repository/CI scope only; it does not close owner-host Gate 25/30/31/34/35/36/38/39 acceptance.


## Batch 62J-40 — FCM bounded child-process isolation

Source implementation adds a disposable `spawn` child for one alert event's maximum-10-device fan-out, with a 60-second total deadline and terminate/kill cleanup. Firebase ADC initialization and token decryption remain inside the child; decrypted FCM tokens do not cross IPC. Timeouts return a sanitized retryable outbox error. Existing stable `event_id` semantics remain at-least-once, not exactly-once.

Lease calculation: 60 s event deadline + 4 s maximum process cleanup (2 s terminate grace + 2 s kill/reap) + 10 s acknowledgement allowance = 74 s; configured minimum is rounded up to 90 s when the worker is enabled. The default 120 s lease leaves 46 s nominal reserve (120 - 60 - 4 - 10 = 46). Batch size remains 1. Tests cover spawned-child result, timeout termination, IPC data boundary, sanitized timeout classification, invalid-token classification and incomplete-event rejection.

This is source-level Gate 39 progress only. Exact-head CI must pass before acceptance. Owner-host induced-failure alert, operator acknowledgement/escalation and incident recovery remain open. No indicator code changed; all indicator statuses remain unchanged.


## Batch 62J-40 exact-head CI reconciliation

Source/test HEAD `54ff8d29db51c87c3b5e3d0a2105e780a9287087` passed:
- Automated Tests & Build: [44722147998](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44722147998) SUCCESS.
- CodeQL JavaScript/TypeScript + Python: [44722148055](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44722148055) SUCCESS.
- Full Git History Secret Audit: [44722148046](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44722148046) SUCCESS.

Backend: **1,180 passed, 6 warnings in 36.91 seconds**. Frontend tests/build/secret scans, backend dependency audit, backend image build, shared Redis/persistent-volume smoke test, container image scan and vulnerability report export all passed. This is repository CI evidence only; Gate 39 still requires owner-host incident response and recovery acceptance. No indicator code changed.


## Batch 62J-41 — Gate 39 deadline accounting correction

A source audit identified that synchronous `Process.start()` latency was not deducted from the 60-second event deadline. The implementation now establishes the monotonic deadline before process startup and gives IPC polling only the remaining budget; a regression test covers startup exceeding the deadline and verifies child termination. The Python wrapper cannot preempt a `Process.start()` call that itself blocks inside the host/OS, and the report explicitly preserves this limitation. Gate 39 remains 🟧 OPEN pending exact-head CI plus owner-host induced-failure alert, operator acknowledgement/escalation and incident-recovery acceptance. No indicator implementation changed or completion credit was awarded.

## Batch 62J-42 — Gate 39 persistent incident journal and operator acknowledgement

Approved scope implemented on `phase-2/market-data-foundation`:

- Added a bounded SQLite incident journal in the existing owner-configured durable database. Only fixed operational fingerprints, categories, severity, summary codes, timestamps and state are accepted; free-form payloads and identifiers are rejected.
- Active incidents deduplicate by fingerprint. Repeated occurrences increment a capped counter; a new occurrence after acknowledgement reopens the incident and resets escalation.
- Lifecycle states are `open`, `acknowledged`, and `resolved`. Acknowledgement stops escalation; worker recovery resolves the active alert-delivery category.
- Capacity is capped at 1,000 rows. Resolved rows older than 30 days are pruned when a new incident is recorded. If all rows are unresolved at capacity, writes fail closed without deleting active incidents.
- Added a separate `OPERATOR_INCIDENT_TOKEN` (32–256 non-whitespace characters, redacted from settings representations), distinct from `OBSERVABILITY_METRICS_TOKEN`.
- Added internal routes: `GET /internal/incidents?limit=...`, `POST /internal/incidents/{id}/acknowledge`, and `POST /internal/incidents/{id}/resolve`. They use constant-time Bearer-token comparison and no-store responses, and are not registered unless the operator token is configured.
- Added a local escalation loop polling every 15 seconds. Open incidents escalate after 5, 10, and 15-minute successive waits (three bounded levels) via sanitized structured logs. No hosted monitoring, email, SMS or paid service is used.
- Alert-worker degradation/error transitions create incidents; a healthy transition resolves the category. Journal failures do not stop delivery.

Security boundary: the token is an application-level control, not a network perimeter. Owner-host firewall/reverse-proxy policy must restrict these routes to trusted operator access. Replicas have independent local SQLite journals unless a supported shared database is deliberately configured; no cross-replica aggregation is claimed. Acknowledgement attribution is the shared operator role, not individual identity. Host restart, access-control and incident recovery drills remain required, so Gate 39 stays 🟧 OPEN pending exact-head CI and owner-host acceptance.

Indicator statuses and calculations are unchanged. SMA20/EMA20/RSI14/MACD/Bollinger/Shared Hook remain 🟨; Footprint remains 🟧 SIMULATED pending owner reference and blueprint; Heatmap and Liquidation Maps remain 🟥. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall project and indicator aggregate percentages remain unestablished. No Termux, device operation, deployment, paid service or `main` change occurred.


## CI evidence refresh — Batch 62J-42 source verification

The source commit `417276d2838a9a93f1306d05efe5a1cdc8df66a9` completed all three exact-head GitHub Actions workflows successfully:

- Automated Tests & Build: run `44726505742` — SUCCESS. Frontend tests/build, backend tests, backend dependency audit, synthetic outbox benchmark, backend container build, persistent-volume/shared-Redis smoke test, and container scan/report steps completed without failure.
- CodeQL Security Analysis: run `44726505502` — SUCCESS.
- Full Git History Secret Audit: run `44726505520` — SUCCESS.

This closes the source/CI verification portion of Batch 62J-42 only. Gate 39 remains 🟧 OPEN for owner-host validation: restrict internal routes at the network boundary, inject and rotate the separate operator token, verify journal persistence across the actual host restart, and perform a controlled incident → escalation → acknowledgement → recovery drill. No live host access or real operator acceptance is inferred from CI.


## Batch 62J-43 — Gate 39 incident journal edge-case hardening (20 November 2026)

Source/test HEAD: `b576bbaa6e8b22af2f11e1e3f06565250ac193a1`.

Three additional tests now cover: (1) journal capacity exhaustion fails closed without deleting an unresolved incident, (2) only resolved incidents older than the 30-day retention threshold are pruned, and (3) sanitized worker exceptions are journaled and resolved after recovery without persisting raw exception messages.

A pre-fix CI run `44739073900` exposed one regression: Python exception class names contain uppercase letters while the journal fingerprint grammar is lowercase-only. The reporter now lowercases only the fingerprint component while preserving the sanitized error code in logs. The failed intermediate run had 1,195 passed and 1 failed; it is superseded by the exact-head passing run below.

Exact-head CI for `b576bbaa6e8b22af2f11e1e3f06565250ac193a1`:
- Automated Tests: run `44739362168` — SUCCESS; 1,196 backend tests passed, 6 warnings in 43.97 seconds.
- CodeQL Security Analysis: run `44739362102` — SUCCESS.
- Full Git History Secret Audit: run `44739362274` — SUCCESS.
- Backend container build, shared Redis/persistent-volume smoke test, container scan and vulnerability report export: SUCCESS.

Lease arithmetic correction: 120 - 60 - 4 - 10 = **46 seconds** default reserve; at the 90-second minimum, reserve = **16 seconds**. The dashboard and ledger now use the corrected values.

Gate 39 remains 🟧 OPEN because CI does not prove owner-host route isolation, operator-token injection/rotation, journal survival on the actual host restart, or a real induced-failure → escalation → acknowledgement → recovery drill. No live Firebase delivery or external notification channel is claimed. No indicator formula or visual implementation changed.


## Batch 62J-44 — Gate 38 bounded metrics hardening (20 November 2026)

**Source commit:** `040c479bb01fd3d6d8f293aab7831164343ecac8`  
**Regression-test commit / latest source-test HEAD:** `a6acf605a44fe356602f92e8bc8e31d1f8e547b6`  
**Exact-head CI:** PENDING / not verified at this documentation checkpoint. The previous verified code checkpoint is `b576bbaa6e8b22af2f11e1e3f06565250ac193a1` with 1,196 backend tests passed and all three recorded workflows SUCCESS.

The Gate 38 source audit found that metric series cardinality was bounded but scalar accumulators had no explicit saturation ceilings. Request counters, histogram counts and bucket counts now saturate at `2^53 - 1`; accumulated duration saturates at `86,400,000 × (2^53 - 1)` ms. A regression test seeds the accumulators at their limits and verifies that a further observation cannot exceed them. Existing 127-series limit, overflow series, route/method normalization, process-local scope, token-gated endpoint, constant-time Bearer comparison, no-store headers and omission of raw request data remain intact.

**Gate 38 remains 🟧 OPEN.** Host firewall/reverse-proxy restriction, operator-token injection/rotation, bounded host-log/collector retention, disk-pressure recovery, real credential-redaction review and dashboard access acceptance still require owner-host evidence. The application metrics are process-local and are not a durable host-log retention mechanism.

**Project accounting:** Stage 1 remains 30/40 = 75% provisional; no tick is credited without approved criterion mapping. Gate 10 remains 10/10 🟧 ORANGE / 0 closed. Stages 2–6 and overall project percentage remain unscored. No indicator calculation or UI work changed; indicator statuses and warm-up boundaries remain unchanged. WebSocket E remains complete for the defined automated CI matrix only; production WSS and host operations remain open. ZERO COST; no deployment, paid service, main change, Termux or device operation.

## Batch 62J-55 — WebSocket exact-head integration reconciliation (21 November 2026)

- Verified FastAPI lifespan owns the injected opt-in Redis replica worker; it validates the runtime bindings, acquires a generation-scoped consumer lease before group startup, dispatches events onto the ASGI loop, and releases the lease only after confirmed worker shutdown.
- Verified `/ws/market-data` selects replica-backed atomic snapshot registration and bounded exact-series Redis replay when replica runtime is injected. The source-store path remains default when no replica runtime is supplied.
- Corrected the older multi-ASGI blueprint statements that described lifespan ownership and route selection as not yet implemented.
- Full two-independent-ASGI-process/WebSocket-client acceptance is still not present in the inspected test inventory. Snapshot transport/installation and real owner-approved topology also remain open. Do not claim production cross-instance fan-out.
- Exact docs HEAD `290c4fe1b4a125e9a41b410d942e807db22c58aa`: Test and Build, CodeQL JavaScript/TypeScript, CodeQL Python, and full reachable Git-history secret audit all SUCCESS. Frontend 245/245 across 29 files; backend 1,218 passed, 6 warnings. This is CI evidence, not production acceptance.
- No runtime/indicator code changed. Indicator status remains unchanged; no indicator percentage is assigned. Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; overall project and aggregate indicator percentages remain unestablished.
- Next technical batch: build the two-ASGI CI harness on existing Redis 7 CI with separate temporary replica databases/groups and verify snapshot watermark, ordered dual delivery, replay/live handoff, restart/outage/retention and lease-loss behavior.
- ZERO COST. No Termux/device command, deployment, Vercel/Cloudflare operation, paid service, or `main` modification.
