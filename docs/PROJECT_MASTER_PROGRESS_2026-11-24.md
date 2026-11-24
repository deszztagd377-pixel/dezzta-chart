# DEZZTA CHART — Master Project Progress & Evidence Ledger

**Document date:** 24 November 2026  
**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Official active stage:** Stage 1 — Foundation, Security & Data Integrity  
**Active branch:** `phase-2/market-data-foundation`  
**Latest exact-head code checkpoint:** `b71bf86c31fadd2895a2b4f18991b6742847e1a1`  
**Protected branch:** `main` — untouched  
**Delivery target:** approximately **24 December 2026** (planning target, not a guarantee)  
**Cost rule:** **ZERO COST / ZERO INCREMENTAL SPEND**  
**Purpose:** canonical, consolidated progress record. This document summarizes the evidence ledger; it does not replace the detailed work-cycle reports linked below.

## Latest verified code checkpoint — Batch 62J-201

Automated Tests [45321594594](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594594) SUCCESS (1/1 job, 40/40 steps) • CodeQL [45321594526](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594526) SUCCESS (2/2 jobs) • OCI ARM64 [45321594556](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594556) SUCCESS • Secret Audit [45321594499](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594499) SUCCESS. All four exact `head_sha` values match `b71bf86c31fadd2895a2b4f18991b6742847e1a1`.

Automated Tests completed 1/1 job and 40/40 steps. The Redis 7 ACL selector confines lease lifecycle commands to the exact lease key; real Redis tests deny SET/DEL/PEXPIRE/EVAL against the stream key and preserve lease operations. Source/test files changed: `backend/app/ohlcv_redis_config.py`, `backend/tests/test_ohlcv_redis_acl_integration.py`, `backend/tests/test_ohlcv_redis_config.py`. Stage 1 remains 30/40 (75% provisional), Gate 10 0/10 closed; overall project and aggregate indicator progress remain NOT SCORED. ZERO COST; `main` untouched.

Detailed report: [Batch 62J-201](WORK_CYCLE_2026-11-24_BATCH62J201_REDIS_ACL_SELECTOR_FIX_AND_INDICATOR_RECONCILIATION.md).

---

## 1. Executive project status

DEZZTA CHART is an Android-first charting application with a web frontend and Python backend. The current engineering work has established substantial repository foundations for authenticated market-data delivery, OHLCV persistence, WebSocket recovery, Redis-backed cross-process relay, security controls, and numerical indicator calculations.

The project is **not yet production-complete**. The largest remaining acceptance gap is not simply missing source code: it is proof on the actual zero-cost owner-controlled runtime and Android device. CI and synthetic/local tests cannot prove a public authenticated WSS endpoint, Firebase account behavior, persistent owner-host Redis, encrypted off-host backup, real operational alerting, or Android background/network recovery.

### Evidence-based headline

| Meter | Current result | Interpretation |
|---|---:|---|
| Official stage | Stage 1 of 6 | Stage sequence has not advanced |
| Stage 1 acceptance | **30/40 criteria = 300/400 ticks = 75% provisional** | Internal acceptance meter only; ten external criteria remain open |
| Gate 10 | **0/10 formally closed** | Repository-side improvements are not external gate closure |
| Stages 2–6 | **NOT SCORED** | No approved stage denominators/acceptance score |
| Overall project | **NOT SCORED** | No approved weighted denominator; do not substitute Stage 1's 75% |
| Indicator aggregate | **NOT SCORED** | No approved per-study weights/denominator |
| Exact-head CI before this document | **4/4 SUCCESS** | All four configured workflows terminal on pre-documentation HEAD |
| Runtime production acceptance | Partial / externally open | Owner-host and owner-device evidence is still required |

**Accounting rule:** 30/40 is the current provisional Stage 1 criterion meter. It is not a claim that the entire product is 75% finished. The historical 20.9% figure recorded in older roadmap history is not a current recalculated overall score.

---

## 2. Official six-stage map

The official roadmap is fixed. The technical branch name does not move the official project stage.

| Stage | Official name | Scope | Current status |
|---:|---|---|---|
| 1 | Foundation, Security & Data Integrity | Application/backend foundation, identity, authorization, data contracts, persistence, security, integrity and acceptance | 🟨 ACTIVE — 30/40 provisional; ten external criteria open |
| 2 | Market Data Infrastructure | Provider-neutral ingestion, instrument definitions, validated OHLCV, stream reliability, coverage and freshness | 🟦 Some foundation work exists; stage not officially opened/scored |
| 3 | Chart Engine & Timeframe | Rendering engine, timeframe behavior, synchronized chart lifecycle, viewport and core interactions | 🟦 Existing chart foundations; stage not officially opened/scored |
| 4 | Indicators & Analytics | Visible overlays/panes, controls, mathematical correctness, timeframe compatibility and performance | 🟦 Calculation foundations exist; visible integration remains parked |
| 5 | Professional UI & Interactive Tools | Broader professional chart experience, drawing/measurement and advanced visual systems | ⬜ Not officially opened/scored |
| 6 | Hardening, Validation & APK Release | End-to-end regression, security/performance, device acceptance, release packaging and delivery | ⬜ Not officially opened/scored |

### Stage-transition guard

Stage 1 remains the official active stage until its acceptance requirements are satisfied. Some Stage 2 market-data infrastructure code and documentation has been built early on the working branch, but it does not waive Stage 1 gates or authorize skipping stages. Stage transitions require the preceding stage's evidence and acceptance.

The 40% overall-project blueprint gate for broader UI expansion does not move indicator implementation into Stage 1 and does not override the stage sequence.

---

## 3. Stage 1 — ten remaining external acceptance criteria

**Gate 10: 0/10 formally closed.** The current open criterion IDs are 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.

| Criterion | Required acceptance evidence | Current status |
|---:|---|---|
| 8 | Owner-controlled no-billing secret injection; verify secrets are absent from repository, history, bundles, build output, logs and process exposure; ownership/mode and rotation | 🟨 Repository hardening exists; owner-host proof open |
| 20 | Real no-billing Firebase sign-in, token expiry/revocation, entitlement denial, scoped WebSocket ticket exchange and browser/Android reconnect | 🟥 External project/device E2E open |
| 25 | Owner-host Redis TLS, ACL, private binding/firewall, persistence, restart/failure/recovery and credential separation | 🟥 CI Redis proof exists; owner-host acceptance open |
| 30 | Restore drill against the actual application database and a fresh destination on the target host/device; source must remain intact | 🟨 Restore implementation and CI failure tests exist; owner-target drill open |
| 31 | Encrypted off-host backup, separate key custody, retention/access policy and verified key-recovery restore | 🟥 Off-host/key-custody and device crypto path constrained |
| 34 | Persistent owner-controlled volume, mount/ownership/permissions, restart, disk pressure and recovery | 🟨 CI mounted-volume smoke exists; owner-host proof open |
| 35 | Backend on existing owner hardware, health/startup/secret injection and public route only if no incremental cost | 🟨 Repository/container readiness exists; owner-host route open |
| 36 | Authenticated public WSS through owner-controlled reverse proxy, real browser and Android clients, reconnect/resnapshot and cross-instance behavior | 🟥 Production WSS/device proof open |
| 38 | Durable owner-host metrics, retention, backup/restore, disk pressure, dashboard, independent alert/acknowledgement and recovery | 🟧 Collector/source hardening exists; host operations open |
| 39 | No-incremental-cost local alert path, incident ownership/escalation, acknowledgement and recovery drill | 🟨 Source-level bounded alert handling exists; operator drill open |

No CI pass, synthetic test, documentation commit or source-only change closes one of these external criteria by itself. The Stage 1 meter remains 30/40 until a criterion's full acceptance evidence is present.

---

## 4. Workstream status

### 4.1 Identity, security and application boundary

Repository foundations include:
- Firebase client/server adapter boundaries and fail-closed authentication behavior.
- Auth observer lifecycle, principal UID/claim consistency, token validation and error-disclosure regression tests.
- HTTP and WebSocket origin/authentication boundaries, single-use WebSocket ticket contract, entitlement and revalidation paths.
- Strict CORS/environment validation, response/cache/security headers, request correlation and sanitized 500 responses.
- Rate limiting and Redis-backed shared guard behavior with fail-closed behavior when the shared guard is unavailable.
- Secret-file loader hardening, Docker build-context exclusion, environment examples without real credentials, source/bundle/history scans.
- Dependency audit enforcement, CodeQL, Trivy container scanning and full reachable Git-history secret audit.

**Boundary:** source and CI evidence does not prove owner-host secret injection, actual Firebase project billing state, real account sign-in/revocation, or deployed endpoint behavior. Firebase must remain on a verified no-billing configuration; if that cannot be guaranteed, the integration stays disabled/deferred.

### 4.2 OHLCV persistence, outbox and data integrity

Verified source-level foundations include:
- Canonical OHLCV and market-data contracts, instrument/series identity and timeframe-aware validation.
- SQLite-backed OHLCV history and a transactional outbox.
- Per-timeframe bounded bar history.
- A global outbox window of **100,000 events** with a monotonic retention floor. Event insertion, high-water advancement, row deletion and floor advancement share the SQLite transaction.
- Consistent outbox read snapshots for high-water, retention floor and replay rows.
- Requests below the retained floor or across a cursor gap fail closed and require a fresh snapshot.
- SQLite batch-read optimization, schema/bootstrap contention tests, writer-lock retry, multi-process contention and disk-full rollback/recovery coverage.

**Boundary:** these are repository/CI and synthetic benchmark results. They are not a measured production-host capacity guarantee or service-level objective.

### 4.3 WebSocket and Redis relay

The repository-side WebSocket work has advanced through multiple engineering batches. The current foundation covers:
- Authenticated ticket issuance/validation and strict client URL/protocol construction.
- Origin and entitlement checks, token/ticket deadlines, heartbeat, ticket renewal and reconnect lifecycle.
- Snapshot plus fixed watermark, deterministic global cursor IDs, cursor-contiguous replay, deduplication and replay/live handoff.
- Resnapshot-required behavior for expired, malformed, non-monotonic, missing or non-contiguous cursors.
- Clearing stale resume cursors after a server-directed resnapshot and reconnecting from a fresh snapshot.
- Per-series supervisor/ownership boundaries, keyed market-data stores, React subscriptions, panel leases and subscriber isolation.
- Bounded subscriber queues, slow-consumer handling, observer isolation, close/failure cleanup and shutdown-race hardening.
- Redis publisher append/read-back, gateway consumer/replica, snapshot installation and digest/receipt validation.
- Generation-scoped Redis consumer groups, durable apply-before-ACK, leases and checkpoint integrity.
- Dedicated publisher/gateway ACL identities, TLS configuration, fail-closed behavior and CI Redis persistence/restart tests.
- Multi-process/two-ASGI-process and synthetic cross-gateway acceptance in repository tests.

**Important distinction:** durable transport replay is not the same as the future TradingView-style historical candle replay UI. The latter belongs to Stage 3 and is not active.

**Production WSS remains open:** no claim is made that the owner-controlled public HTTPS/WSS endpoint, live Firebase ticket exchange, production cross-instance relay, browser/Android trust and reconnect behavior have all been accepted on the target host/device.

### 4.4 Redis retention — newly clarified critical gap

There are two different retention layers:

**SQLite source/outbox retention — 🟩 implemented**
- Bar history is bounded by timeframe caps.
- Global outbox is capped at 100,000 events.
- Retention-floor advancement and row deletion are transactional and monotonic.
- Old cursors and gaps fail closed with resnapshot-required.

**Redis Stream retention — 🟥 not implemented**
- Publisher uses deterministic XADD and exact-ID XRANGE read-back; no XTRIM/XDEL controller exists.
- Publisher ACL is intentionally append/read-back only.
- Gateway ACL is read/group/ack/lease scoped; it does not have trim/delete/group-destroy authority.
- Replay validates retention floor and cursor continuity; trimmed/missing history forces a full resnapshot.
- Generation-scoped consumer groups and pending entries are retained for a separately authorized cleanup path.
- No project-owned retention janitor/controller or group/PEL cleanup worker was found.

**Why no quick XTRIM patch:** a fixed MAXLEN can delete events still needed by a lagging gateway, an old generation or a reconnecting client. It can also leave a checkpoint claiming history that Redis no longer contains. A crash between floor publication and trim can corrupt the recovery contract.

**Safe implementation requirement:** a separate least-privilege retention controller, durable intent/committed-floor protocol, authoritative SQLite high-water/floor, acknowledgement/snapshot-generation coordination for all required gateways, explicit Redis 7.x PEL reference policy, idempotent trim/reconciliation, crash/restart tests, concurrent replay tests and ACL-negative tests. Do not grant XTRIM to publisher or gateway identities. Until the contract is implemented and proven, retaining more Redis history is safer than deleting it.

### 4.5 Market-data sources and session/instrument foundations

Repository work includes provider-neutral market-data architecture, canonical instrument identity/metadata, OHLCV stream protocol, timeframe contracts, CME session calendar/engine artifacts, session-aware aggregation design and provider inventory/zero-cost source policy.

**Hard constraint:** Databento paid API/data is not authorized. No provider should be activated unless access is genuinely free, lawful for the intended display/redistribution, and adequate for the claimed instruments, history and latency. No fake/live-looking prices may be substituted. When no permitted feed is available, the app must explicitly show unavailable, delayed, demo or degraded state.

### 4.6 Indicators and analytics — complete technical ledger

Indicator calculations and their shared data hook have foundations and automated tests, but the visible chart integration is not complete. Status colors represent evidence state, not an invented percentage.

| Indicator/subsystem | Status | Verified mathematical/data foundation | First valid output | Remaining visible acceptance |
|---|---|---|---:|---|
| SMA20 | 🟨 Foundation | Arithmetic mean of the latest 20 closes | Index 19 | Candlestick overlay, independent toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; multiplier \(2/(20+1)=2/21\) | Index 19 | Overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change average then Wilder-smoothed gain/loss recurrence | Index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD index 25; signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values, lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations | Index 19 | Upper/middle/lower overlay, toggle, latest values, identity clearing, lifecycle, render/performance |
| Shared `useMarketIndicators()` | 🟨 Foundation | Immutable identity-bound backend OHLCV snapshot, shared aligned calculations, trust-state suppression and revision-cache regression coverage | Per-study warm-up | Actual chart binding, stale clearing on identity/timeframe changes, settings, legend, accessibility and performance |
| Footprint | 🟧 Synthetic prototype | Educational synthetic accumulator only; not exchange-native bid/ask truth | N/A | Owner visual reference, approved blueprint, verified bid/ask data contract, dedicated spaced-cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | N/A | Owner visual reference, validated depth/liquidity contract, approved blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted calculation/runtime renderer | N/A | Defensible data provenance and calculation contract, approved blueprint, renderer and tests |

#### Indicator invariants

1. Warm-up values remain null; never fabricate zero values.
2. Outputs align exactly to source candle indices/timestamps.
3. Prefix causality: appending future candles must not rewrite prior outputs.
4. Reject invalid, non-finite or unsupported/gapped input rather than emitting misleading values.
5. Instrument, venue, dataset, chart identity or timeframe changes clear stale output.
6. Calculations and tests do not equal chart integration, toggles, legends, accessibility or mobile rendering acceptance.
7. The CandlestickChart currently does not bind the shared indicator hook for visible overlays/panes; visible integration is parked for Stage 4.
8. Footprint OFF must preserve ordinary candle spacing. Only explicit Footprint ON may switch to the dedicated spaced candle/cluster layout.
9. Footprint and Heatmap visual implementation must not begin before the owner provides reference image(s) and reviews/approves a scoped blueprint.

**Aggregate indicator completion: NOT SCORED.** Do not calculate an overall indicator percentage until the study weights and acceptance denominator are approved.

### 4.7 Android / APK / device readiness

Verified historical progress includes Android build/preflight and APK packaging workflows, and a debug APK build was produced in an earlier checkpoint (4.23 MB, November 13). The owner reported installing that APK. This is not equivalent to release acceptance.

Current boundaries:
- APK packaging workflow is frontend-focused; it does not bundle or supervise the Python backend and Redis.
- No release-ready or end-to-end device-integrated backend claim is made.
- Real Android WebView WSS hostname trust, offline/online handover, background/foreground recovery, force-stop/relaunch, reboot and sustained stream behavior remain unverified in this checkpoint.
- The known Google Play Termux repository/keyring signature mismatch remains a hard constraint for the encrypted off-host backup path. Do not bypass APT signature checks, switch repositories, import unverified keys, downgrade cryptography, uninstall or clear app data.
- No device action is requested by this report.
- Google Play publication is deferred. Direct installable APK is the current delivery direction; Play Store publication is not a current requirement.

---

## 5. Exact-head CI and security evidence — pre-documentation HEAD

**Audited HEAD:** `a537e43f6e9ec3c9c6f190126bd462d8cb938f2b`  
All four workflows reached terminal SUCCESS on this exact SHA:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45311790830](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45311790830) | 🟩 SUCCESS — 40/40 steps |
| CodeQL Security Analysis | [45311790858](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45311790858) | 🟩 SUCCESS — Python and JavaScript/TypeScript |
| Full Git History Secret Audit | [45311790861](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45311790861) | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | [45311790883](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45311790883) | 🟩 SUCCESS |

Automated Tests details:
- Backend pytest: **1,359 passed, 1 skipped, 6 warnings** in 58.29 seconds.
- Frontend unit tests: **320 passed across 34 test files**.
- Synthetic Cloudflare Durable Object runtime proof: **11 passed**.
- Frontend dependency audit: zero reported vulnerabilities in this run.
- Backend `pip-audit`: **No known vulnerabilities found**.
- Frontend build and source/bundle credential scans: passed.
- Backend container build and smoke acceptance: passed.
- Trivy HIGH/CRITICAL enforcement step and JSON report export: passed. Artifact ID **14882809351**, 19,044 bytes.
- Redis TLS dedicated fixture: **1 passed in 0.10 seconds** against a TLS-only Redis listener. It tests CA/hostname validation and rejection paths. The later general pytest run skips the same test because the isolated TLS environment variables are scoped to the dedicated workflow step. This expected skip is not a failed TLS test.
- TLS-only Redis AOF data and ACL survived a real container restart in CI.
- Container smoke also verified health, Redis ACL rejection/persistence, AOF persistence, fail-closed API behavior during Redis outage, backend reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence and HTTP rate-limit rejection.
- Six warnings are non-failing WebSocket/Uvicorn deprecation warnings.

**Evidence boundary:** CI uses isolated workflow services and synthetic/local tests. It does not prove owner-host runtime, public internet WSS, provider data entitlements, or physical Android lifecycle.

---

## 6. Historical work-cycle progression — consolidated index

The repository contains detailed batch reports. The sequence below summarizes the engineering themes and links the most relevant reports. Individual batch reports remain the source of truth for exact files, test results and commits.

### Stage 1 foundation and Gate 10 remediation
- Gate 10 execution batches established backup/restore hardening, encrypted backup design, secret boundaries, Firebase auth lifecycle, Redis shared-guard controls, container/runtime hardening, dependency/security gates, monitoring/metrics and alerting.
- Criteria 8/20/25/30/31/34/35/36/38/39 have repeated source audits and acceptance evidence reconciliation. No external gate has been formally closed in the latest ledger.
- Relevant reports: `WORK_CYCLE_2026-11-18_GATE10_BATCH10.md`, `WORK_CYCLE_2026-11-18_GATE10_BATCH15.md`, `WORK_CYCLE_2026-11-18_GATE10_BATCH20.md`, `WORK_CYCLE_2026-11-19_BATCH60_GATE10_ZERO_COST_ACCEPTANCE_MATRIX.md`, `WORK_CYCLE_2026-11-20_BATCH62J34_GATE8_38_39_OPERATIONAL_HARDENING.md`.

### WebSocket protocol and lifecycle hardening
- Batches 30–50 addressed protocol/auth boundaries, heartbeat, browser lifecycle, retry guards, supervisor/observer isolation, failure/close cleanup and preview/runtime audits.
- Batches 52–58 reconciled WSS acceptance, Gate 10 evidence and indicators.
- Batches 61–63 and 62B–62J established global outbox relay, Redis publisher, replica consumer, snapshot export/install, deterministic cursor and gateway bridge foundations.
- Batches 62J-22 through 62J-48 covered atomic replica hydration, opt-in runtime, two-ASGI-process acceptance, dual-gateway recovery, WebSocket ticket lifecycle, Android update readiness and cross-account renewal.
- Batches 62J-53 through 62J-99 hardened Redis ownership, checkpoints, cursor receipts, WSS, metrics, alerting, browser lifecycle and owner-host acceptance boundaries.
- Batches 62J-100 through 62J-162 expanded metrics, ticket boundaries, replay/resnapshot, Redis ACL/TLS, subscriber isolation, canonical series identity, keyed stores, React subscriptions, per-series supervisors and indexed WebSocket fan-out.
- Batches 62J-164 through 62J-186 addressed transactional worker startup, snapshot digest/receipt, leases, pending recovery, metrics timestamp/wire format, zero-cost host feasibility, synthetic Worker proof, cursor integrity, auth timeout, snapshot continuity, session frontend integration, concurrent WebSocket regressions and indicator trust/cache regressions.
- Latest WebSocket reports: [Batch 62J-188](WORK_CYCLE_2026-11-24_BATCH62J188_WEBSOCKET_RESNAPSHOT_CURSOR_INTEGRITY.md), [Batch 62J-189](WORK_CYCLE_2026-11-24_BATCH62J189_REPLAY_CHECKPOINT_FLOOR_INTEGRITY.md), [Batch 62J-190](WORK_CYCLE_2026-11-24_BATCH62J190_RESNAPSHOT_RECONNECT_CURSOR_RECOVERY.md), [Batch 62J-191](WORK_CYCLE_2026-11-24_BATCH62J191_WEBSOCKET_CROSS_PATH_AUDIT.md), [Batch 62J-193](WORK_CYCLE_2026-11-24_BATCH62J193_REPLAY_LIVE_HANDOFF_REGRESSION.md).

### Indicator and data foundations
- Indicator calculations, numerical safeguards, warm-up alignment, prefix causality, shared snapshot hook, trust-state suppression and revision-cache regressions are documented in the indicator ledger and batches 62J-76 through 62J-80, 62J-148, 62J-155, 62J-185 and 62J-186.
- Instrument identity, provider-neutral OHLCV contracts, CME session calendar and timeframe/session-aware aggregation are documented in the market-data and calendar architecture files.
- The calculation foundation is real repository work; the visible indicator interface remains intentionally parked until Stage 4.

### Storage, metrics and operational resilience
- Batches 62J-60 through 62J-98 include restore preflight, SQLite WAL/capacity, encrypted restore, metrics collection, disk-full rollback, process contention, batch-read optimization and measured synthetic tail-latency diagnostics.
- The retry-jitter experiment was rejected after regression and reverted; do not claim it improved tail latency.
- Synthetic benchmarks are not production SLOs or host-capacity guarantees.

### Latest November 24 audit sequence
- [Batch 62J-195 — exact-head CI acceptance](WORK_CYCLE_2026-11-24_BATCH62J195_EXACT_HEAD_CI_ACCEPTANCE.md)
- [Batch 62J-196 — Stage 1 retention/host/indicator audit](WORK_CYCLE_2026-11-24_BATCH62J196_STAGE1_RETENTION_HOST_AND_INDICATOR_AUDIT.md)
- [Batch 62J-197 — exact-head CI and Stage 1 evidence](WORK_CYCLE_2026-11-24_BATCH62J197_EXACT_HEAD_CI_AND_STAGE1_EVIDENCE.md)
- [Batch 62J-198 — Redis retention lifecycle and safe trim design](WORK_CYCLE_2026-11-24_BATCH62J198_REDIS_RETENTION_LIFECYCLE_AUDIT.md)

---

## 7. Current blockers and red/yellow/green dashboard

| Workstream | Status | What is genuinely complete | Remaining blocker |
|---|---|---|---|
| Repository automated regression | 🟩 | Exact-head backend/frontend suites and smoke tests pass | Keep exact-head CI green after each new commit |
| CodeQL / secret audit / ARM64 | 🟩 | All three workflows pass on audited HEAD | Re-run on every subsequent HEAD |
| SQLite source outbox retention | 🟩 | Transactional 100,000-event floor and fail-closed replay | Owner-host capacity/recovery evidence |
| Redis TLS/ACL CI | 🟩 | Dedicated TLS fixture, ACL and AOF restart proof in CI | Owner-host Redis topology and rotation |
| Redis stream append/replay | 🟩 | Deterministic append/read-back, checkpoint validation, contiguous replay | Stream trim lifecycle absent |
| Redis retention controller | 🟥 | Safety contract documented | Implementation, dedicated role, gateway floor coordination, PEL cleanup, crash tests |
| WebSocket repository protocol | 🟩 | Auth, lifecycle, heartbeat, cursor, snapshot, reconnect and isolation regression coverage | Public owner-host WSS and real multi-instance acceptance |
| Firebase production auth | 🟨/🟥 | Adapter and fail-closed source/test coverage | Real no-billing project E2E, expiry/revocation and ticket exchange |
| Android packaging | 🟨 | Debug APK pipeline/build proof | Integrated backend delivery and current release acceptance |
| Android WebSocket lifecycle | 🟥 | Repository preflight/lifecycle tests | Real phone network/background/force-stop/reboot acceptance |
| SMA/EMA/RSI/MACD/Bollinger | 🟨 | Calculation foundations and tests | Chart binding, controls, panes/overlays, legend, lifecycle/performance |
| Shared indicator hook | 🟨 | Shared snapshot and trust boundary | Visible chart integration and user controls |
| Footprint | 🟧 | Synthetic educational accumulator | Reference image, reviewed blueprint, valid bid/ask contract, renderer |
| Heatmap | 🟥 | No accepted renderer | Reference image, depth contract, blueprint and renderer |
| Liquidation Maps | 🟥 | No accepted runtime | Provenance/calculation contract, blueprint and renderer |
| Public market-data feed | 🟥/🟨 | Provider-neutral contracts and source inventory | Truly free, lawful, suitable provider; paid Databento disabled |
| Owner-host backup/metrics/alerts | 🟨/🟥 | Source/CI workflows and runbooks | Actual host, off-host custody, dashboard and operator drill |

---

## 8. ZERO COST — mandatory operating policy

No payment obligation may be introduced. This prohibits:
- Paid hosting, managed Redis/databases, metered compute or storage, paid market-data feeds, paid backup/monitoring/alerting, paid email/SMS, paid domains/CDN/add-ons, paid CI runners or publication fees.
- Firebase Blaze upgrade, billing activation, payment-card attachment, free trials with auto-conversion, automatic upgrades or unclear overage behavior.
- Databento paid API/data and the superseded Fly.io deployment plan.

Allowed path:
- Existing owner hardware and local/open-source components where practical.
- No-billing plans only after verifying current terms, quotas, expiry/pausing and the absence of automatic charges.
- Provider-neutral market-data contracts and only legally permitted, genuinely free data.
- Explicit unavailable/delayed/demo state when a free lawful source is not available.
- If zero-cost operation cannot meet a requirement, mark it constrained/deferred. Do not weaken TLS, ACL, authentication or persistence to pretend a free service is equivalent.

The zero-cost policy is architecture and release acceptance, not merely a budget preference.

---

## 9. Delivery plan toward 24 December 2026

The date is a planning target, not a promise. Work should proceed by evidence and risk, not by inflating percentages.

### Priority 1 — complete Stage 1 acceptance safely
1. Implement a Redis retention-controller design only after the owner/gateway floor registry, snapshot generation, PEL policy and crash-safe ordering are fully specified.
2. Add real Redis 7.x trim-boundary, crash/restart, replay-race and ACL-negative integration tests before enabling trim.
3. Resolve owner-host WSS/Redis architecture using only a verified zero-cost topology. If no such topology can meet durable shared state, certificates and runtime requirements, record a no-go rather than introduce billing.
4. Complete owner-host secret, persistent-volume, restore, backup/key custody, metrics and alert/acknowledgement evidence.
5. Complete real no-billing Firebase and browser/Android authenticated WSS acceptance.
6. Reconcile each of the ten Stage 1 criteria individually; only then update the 30/40 meter.

### Priority 2 — advance stages in order
- Stage 2: free/legal provider selection, source reliability/freshness, instrument coverage and validated live/historical OHLCV.
- Stage 3: chart engine/timeframe lifecycle, chart interactions and historical candle replay blueprint/implementation.
- Stage 4: owner-reviewed indicator blueprint, chart integration for standard studies, then separately gated advanced studies.
- Stage 5: professional UI and interactive tools under the owner's 40% blueprint/review rule.
- Stage 6: end-to-end security/performance/device acceptance and installable APK release.

### Schedule risk
The 24 December target is at risk if Stage 1 external acceptance remains unresolved, especially public WSS/Redis host, Android lifecycle and encrypted off-host recovery. No schedule shortcut may bypass zero-cost, TLS, ACL, data integrity or stage-transition requirements.

---

## 10. Engineering change and safety policy

1. Work only on `phase-2/market-data-foundation`; never touch `main`.
2. Inspect current source, tests, workflows and exact HEAD before editing.
3. Preserve working features; no speculative API, provider or repository structure.
4. Do not claim a test, workflow, deployment or device result that was not observed.
5. A running CI job must be polled to a terminal state for the exact HEAD. If a later commit supersedes a run, mark the older run superseded/cancelled; do not misreport it as success.
6. No broken documents, code or commands should be handed to the owner as a manual repair task. Validate generated docs and source changes in CI.
7. No source/runtime changes are justified solely to make a dashboard greener.
8. No external host/device operation is implied by repository commits.
9. Keep the user's indicator references and Footprint spacing rule intact.
10. Any material scope or outcome change requires owner review before implementation.

---

## 11. Canonical documentation index

- [Official six-stage roadmap](PROJECT_STAGE_ROADMAP.md)
- [Stage 1 acceptance matrix](STAGE_1_ACCEPTANCE_MATRIX.md)
- [Stage 1 zero-cost gate plan](STAGE_1_ZERO_COST_GATE_PLAN.md)
- [Zero-cost policy](ZERO_COST_POLICY.md)
- [Project progress history](PROJECT_PROGRESS.md)
- [Current project progress indicator](PROJECT_PROGRESS_INDICATOR_CURRENT.md)
- [Project milestone ledger](PROJECT_MILESTONE_LEDGER.md)
- [Indicator progress ledger](INDICATOR_PROGRESS_LEDGER.md)
- [Indicator data architecture](INDICATOR_DATA_ARCHITECTURE.md)
- [Indicator UI blueprint — parked for Stage 4](INDICATOR_UI_BLUEPRINT.md)
- [WebSocket authentication design](WEBSOCKET_AUTH_DESIGN.md)
- [WebSocket reliability design](WEBSOCKET_RELIABILITY_DESIGN.md)
- [WebSocket production wiring audit](WEBSOCKET_PRODUCTION_WIRING_AUDIT.md)
- [OHLCV stream protocol](OHLCV_STREAM_PROTOCOL.md)
- [OHLCV persistence](OHLCV_PERSISTENCE.md)
- [Market-data contract](MARKET_DATA_CONTRACT.md)
- [Zero-cost market-data source policy](FREE_MARKET_DATA_SOURCE_POLICY.md)
- [Android backend host audit](ANDROID_BACKEND_HOST_AUDIT.md)
- [Operations runbook — zero cost](OPERATIONS_RUNBOOK_ZERO_COST.md)
- [Batch 62J-195](WORK_CYCLE_2026-11-24_BATCH62J195_EXACT_HEAD_CI_ACCEPTANCE.md)
- [Batch 62J-196](WORK_CYCLE_2026-11-24_BATCH62J196_STAGE1_RETENTION_HOST_AND_INDICATOR_AUDIT.md)
- [Batch 62J-197](WORK_CYCLE_2026-11-24_BATCH62J197_EXACT_HEAD_CI_AND_STAGE1_EVIDENCE.md)
- [Batch 62J-198](WORK_CYCLE_2026-11-24_BATCH62J198_REDIS_RETENTION_LIFECYCLE_AUDIT.md)
- [Batch 62J-199](WORK_CYCLE_2026-11-24_BATCH62J199_REDIS_ACL_DESTRUCTIVE_BOUNDARY_AND_INDICATOR_AUDIT.md)

---

## 12. Final checkpoint statement

As of the latest verified source/test HEAD `23bf2da93ec8b4c935d2898a993f4d1c80ce9a7d`, all four configured CI workflows reached terminal SUCCESS: Automated Tests [45313574302](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45313574302), CodeQL [45313574375](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45313574375), Full Git History Secret Audit [45313574338](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45313574338), and OCI ARM64 [45313574445](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45313574445). Automated Tests recorded 1,359 backend tests passed, 1 skipped, 6 non-failing deprecation warnings, 320 frontend tests across 34 files, the dedicated Redis TLS fixture passed, npm audit reported zero vulnerabilities, pip-audit reported no known vulnerabilities, and container persistence/fail-closed smoke tests passed. The real Redis ACL integration test passed with explicit denial of publisher/gateway XTRIM/XDEL and gateway XGROUP DESTROY.

The project remains officially in Stage 1 at 30/40 criteria (75% provisional), with Gate 10 at 0/10 formally closed. Overall project progress and aggregate indicator completion remain NOT SCORED. The most important unresolved repository-side gap is the Redis Stream retention controller and durable gateway inventory/retirement contract; the most important external gaps are owner-host WSS/Redis, backup/key custody, operations and Android lifecycle.

The latest source/test change is a test-only Redis ACL hardening change; no production runtime code, dependency, deployment or paid service was changed. ZERO COST remains mandatory, `main` remains untouched, and the target delivery date remains approximately 24 December 2026. See [Batch 62J-199](WORK_CYCLE_2026-11-24_BATCH62J199_REDIS_ACL_DESTRUCTIVE_BOUNDARY_AND_INDICATOR_AUDIT.md) for the full exact-head evidence and indicator ledger.
