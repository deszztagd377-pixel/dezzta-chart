# Latest verified checkpoint — 24 November 2026 (Batch 62J-201)

**Branch:** `phase-2/market-data-foundation`  
**Exact code/test HEAD:** `b71bf86c31fadd2895a2b4f18991b6742847e1a1`  
**Documentation base HEAD for Batch 62J-202:** `1e5aac317c5714fbe554f0daf380c9dad53a27e4`  
**Exact-head CI:** Automated Tests [45321594594](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594594) SUCCESS (1/1 job, 40/40 steps) • CodeQL [45321594526](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594526) SUCCESS (2/2 jobs) • OCI ARM64 [45321594556](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594556) SUCCESS • Secret Audit [45321594499](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594499) SUCCESS. All four exact `head_sha` values match `b71bf86c31fadd2895a2b4f18991b6742847e1a1`.  
**Cost:** ZERO COST • **main:** untouched • **delivery target:** approximately 24 December 2026 (planning target only)

## Latest documentation maintenance — Batch 62J-202

The duplicate current indicator/accounting block was removed; historical checkpoints remain preserved. See [Batch 62J-202](WORK_CYCLE_2026-11-24_BATCH62J202_INDICATOR_LEDGER_DEDUPLICATION_AND_STATUS_SYNC.md). Code/test evidence remains on the separately identified Batch 62J-201 source HEAD.

## Batch 62J-201 — Redis 7 ACL selector fix

Gateway stream-consumer permissions now remain at the root ACL scope for the stream key. Lease lifecycle commands `SET`, `EVAL`, `GET`, `PEXPIRE`, `DEL` are isolated in a Redis 7 ACL selector restricted to one exact literal lease key. The real Redis integration test denies gateway SET/DEL/PEXPIRE/EVAL against the stream key while allowing lease acquisition, renewal and token-fenced release. Out-of-scope keys, publisher lease access, XTRIM/XDEL/XGROUP DESTROY and database switching remain denied.

Changed files: `backend/app/ohlcv_redis_config.py`, `backend/tests/test_ohlcv_redis_acl_integration.py`, `backend/tests/test_ohlcv_redis_config.py`. Backend tests, Redis TLS fixture, dependency audit, container build/smoke, image scan and report export passed. No production credentials or runtime relay startup wiring changed; relay remains disabled/unwired pending owner-controlled snapshot transport and dedicated credentials.

## Project progress
| Meter | Verified state | Status |
|---|---:|---|
| Stage 1 | 30/40 criteria • 300/400 ticks • 75% provisional | 🟨 Active |
| Gate 10 | 0/10 formally closed; open 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 | 🟥 Open |
| Stages 2–6 | Not officially opened/scored | 🟦 / ⬜ Parked |
| Overall project | No approved weighted denominator | ⚪ NOT SCORED |
| Aggregate indicator progress | No approved indicator denominator | ⚪ NOT SCORED |

## Complete indicator ledger
| Indicator / layer | Verified calculation foundation | Visible chart state | Status |
|---|---|---|---|
| SMA 20 | 20-close mean; first valid index 19; tests | No overlay/toggle/legend | 🟨 Foundation |
| EMA 20 | SMA-seeded; alpha 2/21; first valid index 19; tests | No overlay/toggle/legend | 🟨 Foundation |
| RSI 14 (Wilder) | Wilder smoothing; first valid index 14; tests | No pane, 0–100 scale, 30/70 guides or toggle | 🟨 Foundation |
| MACD 12/26/9 | MACD index 25; signal/histogram index 33; tests | No dedicated pane/visible histogram/zero guide | 🟨 Foundation |
| Bollinger 20,2 | Mean ± 2 population SD; first valid index 19; tests | No bands/fill/toggle | 🟨 Foundation |
| Shared indicator hook | Identity-bound validated backend snapshot; trust-state suppression | Hook only; not chart-integrated | 🟨 Foundation |
| Footprint | Deterministic synthetic/offline aggregation + fixtures | Wait for owner reference + scoped blueprint; OFF normal candles, ON spaced clusters | 🟧 Gated |
| Heatmap | No implementation verified | Not implemented; wait for owner reference | 🟥 Open |
| Liquidation Maps | No implementation verified | Not implemented; wait for owner reference | 🟥 Open |

No aggregate indicator percentage is invented. Calculation foundations are not finished visible features. Stage 4 remains parked; Footprint and Heatmap visual work waits for owner references and scoped blueprint review.

## WebSocket and retention blockers

WebSocket/OHLCV repository foundations include authenticated delivery boundaries, snapshot/replay recovery, durable SQLite source outbox, per-replica checkpoints and Redis Stream relay components. Owner-host WSS, actual Android/browser reconnect, cross-instance and platform-lifetime proof remain open.

SQLite source/outbox retention uses a 100,000-event bounded window and transactional monotonic floor advancement. Redis Stream retention remains NOT IMPLEMENTED pending durable gateway inventory, retirement semantics, authenticated snapshot receipts, per-gateway floor acknowledgements, PEL policy and crash-safe intent/commit/trim/reconcile tests. Runtime users must not receive destructive stream permissions.


---

# Latest verified checkpoint — 24 November 2026 (Batch 62J-190)

**Branch:** `phase-2/market-data-foundation`  
**Latest source/test HEAD:** `8606cb460f641b0b831081aeed8aae6a6149c91d`.  
**Latest code work:** [Batch 62J-189 replay checkpoint floor](WORK_CYCLE_2026-11-24_BATCH62J189_REPLAY_CHECKPOINT_FLOOR_INTEGRITY.md) and [Batch 62J-190 resnapshot reconnect cursor recovery](WORK_CYCLE_2026-11-24_BATCH62J190_RESNAPSHOT_RECONNECT_CURSOR_RECOVERY.md).  
**Exact-HEAD CI:** Automated Tests [45304034616](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034616), CodeQL [45304034690](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034690), OCI ARM64 [45304034703](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034703), Secret Audit [45304034693](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034693), Android APK Build [45304034582](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034582) — **5/5 SUCCESS**. Frontend 320 tests passed; backend 1,348 passed, 1 skipped, 6 non-failing warnings.
**Significant WebSocket delta:** backend now rejects replay checkpoints older than immutable snapshot cursor; client propagates server resnapshot instructions to the supervisor; supervisor clears stale resume cursor and requests a full snapshot before adopting a new cursor.
**Android artifact:** debug APK artifact [14880166595](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034582/artifacts/14880166595), SHA-256 `39a6b0a97b3d55bfa44e5dea390d8d8b2a506fb23e7b4de68cfaca830a47e562`. Debug artifact only; no real-device acceptance.
**Provider / ZERO COST:** fixed-symbol Databento subscription remains configuration-scoped; no verified dynamic add/remove API or recurring-$0 redistribution entitlement. No provider activated.
**main:** untouched (`e3841681bc69b73619058deaf939df82ae5116a1`). **Stage 1:** 30/40 = 75% provisional 🟨. **Stages 2–6:** not scored. **Gate 10:** 0/10 formally closed 🟥. **Overall:** NOT SCORED; weighted denominator unavailable. **Delivery target:** 24 December 2026, planning target only. **Cost:** ZERO COST.

---

# Latest verified checkpoint — 24 November 2026 (Batch 62J-189)

**Branch:** `phase-2/market-data-foundation`  
**Latest source/test HEAD:** `713449822022e555b6fe98964952814b012f3520`.  
**Batch report:** [WORK_CYCLE_2026-11-24_BATCH62J189_REPLAY_CHECKPOINT_FLOOR_INTEGRITY.md](WORK_CYCLE_2026-11-24_BATCH62J189_REPLAY_CHECKPOINT_FLOOR_INTEGRITY.md).  
**Exact-HEAD CI at report creation:** Automated Tests [45302691457](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45302691457) RUNNING; CodeQL [45302691477](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45302691477) SUCCESS; OCI ARM64 [45302691475](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45302691475) SUCCESS; Secret Audit [45302691440](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45302691440) SUCCESS. Automated Tests had completed frontend tests/build and was executing backend tests; do not award full CI credit until it completes.
**Batch 62J-189:** immutable `snapshot_cursor` is now tracked separately from moving `durable_cursor`. Replay handoff fails closed if its checkpoint predates the snapshot watermark. Regression coverage includes both in-memory and externally consistent replica snapshot registration paths, and verifies the live queue is not drained on rejection.
**Provider / ZERO COST:** fixed-symbol Databento subscription remains configuration-scoped; no verified dynamic add/remove API or recurring-$0 redistribution entitlement. No provider activated and no disconnected reference counter added.
**main:** untouched (`e3841681bc69b73619058deaf939df82ae5116a1`). **Stage 1:** 30/40 = 75% provisional 🟨. **Stages 2–6:** not scored. **Gate 10:** 0/10 formally closed 🟥. **Overall:** NOT SCORED; weighted denominator unavailable. **Delivery target:** 24 December 2026, planning target only. **Cost:** ZERO COST.

---

# Latest verified checkpoint — 24 November 2026 (Batch 62J-188)

**Branch:** `phase-2/market-data-foundation`  
**Latest exact-HEAD source/test commit:** `22c9ab4a0e97383520670a9af42a2f9ef35f6d62`.  
**Batch report:** [WORK_CYCLE_2026-11-24_BATCH62J188_WEBSOCKET_RESNAPSHOT_CURSOR_INTEGRITY.md](WORK_CYCLE_2026-11-24_BATCH62J188_WEBSOCKET_RESNAPSHOT_CURSOR_INTEGRITY.md).  
**Exact-HEAD CI:** Automated Tests [45301177675](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45301177675) SUCCESS (frontend 319/319 across 34 files; backend 1,347 passed / 1 skipped / 6 warnings); CodeQL [45301177661](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45301177661) SUCCESS; OCI ARM64 [45301177705](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45301177705) SUCCESS; Android APK [45301177667](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45301177667) SUCCESS; Secret Audit [45301177685](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45301177685) SUCCESS.

**WebSocket Batch 62J-188:** client now requires the replacement snapshot cursor to exactly match the server's `snapshotCursor`; mismatched and missing cursor regression tests pass. Runtime fix commit `af9020ba6bbc98110a237b18caac9920570cf1ed`; regression-test commit `22c9ab4a0e97383520670a9af42a2f9ef35f6d62`.

**Android debug APK:** artifact ID `14878467608`; SHA-256 `24491a9022b769f60db771a29c1b2b061a9d2b37a39186af0f4dc56300e500c2`. [Artifact](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45301177667/artifacts/14878467608). CI build only, not real-device/release acceptance.

**main:** untouched. **Stage 1:** 30/40 = 75% provisional 🟨. **Stages 2–6:** not scored. **Gate 10:** 0/10 external criteria formally closed 🟥. **Overall:** NOT SCORED; weighted denominator unavailable. **Delivery target:** 24 December 2026, planning target only. **Cost:** ZERO COST.

---

# Latest verified checkpoint — 24 November 2026 (Batch 62J-187)

**Branch:** `phase-2/market-data-foundation`  
**Latest verified source HEAD:** `1b3f39ea8f3a6cfd56425fc799b58ee8e0d0991b`.  
**Latest documentation report commit:** `2b40035b76276ad76ff94c5cb2c2681c7390e652` (report: [Batch 62J-187](WORK_CYCLE_2026-11-24_BATCH62J187_EXACT_HEAD_CI_APK_INDICATOR_RECONCILIATION.md)).  
**Exact-HEAD CI:** five workflows SUCCESS on source HEAD `1b3f39ea8f3a6cfd56425fc799b58ee8e0d0991b`:
- Automated Tests [45215527228](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215527228)
- CodeQL [45215526929](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215526929)
- OCI ARM64 Image Readiness [45215526908](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215526908)
- Android APK Build [45215527101](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215527101)
- Full Git History Secret Audit [45215526995](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215526995)

**Android artifact:** debug APK uploaded; artifact ID `14838496390`; APK SHA-256 `978da27dedc506a7b3060d89deef4639d6b3dc19862628e3fa86324a998295a1`. [Artifact](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215527101/artifacts/14838496390). Debug CI artifact only; not device or release acceptance.

**Latest source change:** commit `1b3f39ea8f3a6cfd56425fc799b58ee8e0d0991b` changes only `package.json`, applying a scoped Miniflare `undici@7.30.1` override. No WebSocket or indicator runtime/UI source changed.

**Protected branch `main`:** unchanged.  
**Stage 1:** 30/40 = 75% provisional 🟨. **Stages 2–6:** not scored. **Gate 10:** 0/10 external criteria formally closed 🟥. **Overall project:** NOT SCORED; approved weighted denominator unavailable.  
**Indicators:** SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 Foundation; Footprint 🟧 synthetic prototype only; Heatmap and Liquidation Maps 🟥 not implemented. No aggregate indicator percentage is approved.  
**Delivery target:** 24 December 2026 (planning target, not guaranteed). **Cost:** ZERO COST.

---

# Latest verified checkpoint — 23 November 2026

**Branch:** `phase-2/market-data-foundation`  
**Current documentation checkpoint before this refresh:** `1121f227db79174361125f7f8ce5f4e0e17baee8`  
**Latest source/test HEAD:** `d2057e9997b50cb6aab04258fd90de37d35a6816`.  
**Exact-HEAD verification:** four workflows SUCCESS on `4a87b90e08da04cd22faf74d578a5ce2f2734c15`:
- Automated Tests [45199096612](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45199096612)
- Full Git History Secret Audit [45199096630](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45199096630)
- CodeQL [45199096621](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45199096621)
- OCI ARM64 Image Readiness [45199096646](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45199096646)

**Protected branch `main`:** unchanged.

**Accepted verification totals:** frontend 315/315 across 34 files; backend 1,347 passed / 1 skipped / 6 non-failing warnings; synthetic Worker Node 25/25; Miniflare/workerd 1/1; Durable Object runtime 10/10. Frontend production build, credential scans, backend dependency audit, container build/smoke/image scan and Redis TLS/AOF CI fixture passed.

**Latest engineering work:** Batch 62J-184 adds four Durable Object concurrency/lifecycle regressions; Batches 62J-185/186 add two indicator-hook trust/revision regressions. The four new Durable Object cases and both hook regressions are now CI-verified. No production provider, public WSS, paid service, or order-execution feature was enabled.

**Project score:** overall **NOT SCORED** (approved weighted denominator unavailable). Official current stage: Stage 1, 30/40 = 75% provisional 🟨. Stage 2 is not officially opened/scored; provider-demand lifecycle, recurring-zero-cost data entitlement, public WSS and production identity remain unresolved. Stages 3–6: not scored. Gate 10: 0/10 external criteria formally closed 🟥.

**Delivery target:** 24 December 2026 (planning target, not guaranteed).

---

# CURRENT PROJECT PROGRESS — Batch 62J-182 (23 November 2026)

**Target date corrected by project owner: 24 December 2026.** This is a delivery target, not a guaranteed completion claim.

**Active branch:** `phase-2/market-data-foundation`  
**Latest fully CI-verified code/test HEAD:** `07186190e98a4e9418664990a1a84acbc6fb3e13`  
**Latest implementation checkpoint (exact-HEAD CI not yet verified):** `af3746fc39ac75a842a0199ad09304b008f19107`  
**WebSocket test correction commit:** `cb708c3e6357c59ef7a61fcb5fc5c304b014d62a`  
**Batch 62J-148 test commit:** `79d88d9aa5261dde3f2e31d1e742d45f461e43c2`  
**Batch 62J-149 WebSocket test commit:** `ed7f22a00b71223d0dd7ed280aadddd8a30cf6e1`  
**Main:** untouched.

## Batch 62J-148 — indicator numerical regression coverage

Runtime indicator formulas were not changed. Added two deterministic regression tests to `src/indicators/indicatorCalculations.test.ts`: (1) mixed up/down closes verify Wilder RSI period-2 output exactly as `[null, null, 50, 75, 37.5]`; (2) the shared multi-indicator entry point rejects a non-finite close at source index 7. These strengthen regression coverage but do not complete chart rendering, controls, panes or lifecycle acceptance. Exact-HEAD CI for the new test commit must be checked separately.

## Latest prior exact-HEAD CI — `1d8667fc5d6810bbde88b6a596214cdedc5fc80f`

- Automated Tests [45016825555](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016825555): SUCCESS. Frontend tests/build, Android preflight and preview publisher tests, backend tests, isolated Redis TLS enforcement, synthetic SQLite outbox/metrics benchmarks, backend container build/smoke and image scan passed.
- CodeQL [45016825571](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016825571): SUCCESS for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [45016825575](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016825575): SUCCESS.
- OCI ARM64 Image Readiness [45016825580](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016825580): SUCCESS; native ARM64 build and unprivileged/persistent-volume smoke passed.

OCI qualification: CI image/build/runtime smoke evidence only, not an OCI tenancy, cloud deployment, public endpoint, TLS certificate or owner-host acceptance.

## Batch 62J-149 — WebSocket subscriber isolation

Added `backend/tests/test_ohlcv_stream.py::test_same_series_subscribers_are_isolated_when_one_disconnects`. Two clients subscribe to the same exact series; both receive the first update; after client A unsubscribes, client B continues receiving the next update; A remains closed and receives no more events. Subscriber count is verified across 2 → 1 → 0.

This is a downstream per-client fan-out regression test, not proof of upstream dynamic provider subscription or reference counting. The existing real WSS multi-user test also covers client disconnect isolation at the API boundary.

### Exact-HEAD CI — failing tested HEAD 041da77cb9ce95e083f8851614928d0de0994ad4

- Automated Tests [45018172626](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018172626): FAILURE — 1,297 passed, 1 failed, 1 skipped. Sole failure was the same-series subscriber isolation test: subscriber A's first already-enqueued event was not consumed before unsubscribe, but the test then asserted its queue was empty. This was an incorrect test precondition; unsubscribe closes future delivery and does not erase an event already queued.
- CodeQL [45018172635](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018172635): SUCCESS for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [45018172621](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018172621): SUCCESS.
- OCI ARM64 [45018172647](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018172647): SUCCESS; native ARM64 build and unprivileged/persistent-volume smoke passed.

### Batch 62J-150 correction

Test-only change at cb708c3e6357c59ef7a61fcb5fc5c304b014d62a: consume and verify subscriber A's first delivered event before unsubscribe, then verify no subsequent update is delivered to A while subscriber B continues. No production runtime code changed.

Correction verified on exact CI HEAD 754e1d9edc270e110161662aad83b6fac4a792bc:
- Automated Tests [45018667056](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018667056): SUCCESS — backend 1,298 passed, 1 skipped; frontend tests/build, Android preflight/publisher, SQLite benchmarks, dependency audits, backend container build/smoke and vulnerability scan succeeded.
- CodeQL [45018667061](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018667061): SUCCESS.
- Full Git History Secret Audit [45018667128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018667128): SUCCESS.
- OCI ARM64 [45018667069](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018667069): SUCCESS.

OCI qualification: image build/smoke only, not an OCI tenancy/VM deployment, public hostname, TLS/WSS endpoint or real Android acceptance.
## Stage and Gate accounting

| Stage | Verified status |
|---|---:|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional 🟨 |
| 2. Market Data Infrastructure | Not scored / not officially opened ⬜ |
| 3. Chart Engine & Timeframe | Not scored ⬜ |
| 4. Indicators & Analytics | Not scored ⬜ |
| 5. Professional UI & Interactive Tools | Not scored ⬜ |
| 6. Hardening, Validation & APK Release | Not scored ⬜ |

**Overall project: NOT SCORED.** Approved stage weights and total denominator do not exist; do not fabricate a whole-project percentage.

**Gate 10: 0/10 external criteria formally closed.** Green CI does not close owner-host, public-network, Android-device or production-provider gates. Open criteria include 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.

## Full indicator dashboard

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; mixed gain/loss recurrence test added | 0–100 pane, 30/70 guides, toggle/legend/latest value, identity/lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Pane, lines, histogram, zero guide, toggle/legend and lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Three-line overlay, toggle/values, identity/lifecycle/render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | Exact validated backend snapshot; null for demo/loading/unavailable/error | Hook tests, chart binding, stale clearing, render and identity lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, valid bid/ask source contract, cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted runtime/render implementation | User reference image(s), validated order-book/depth/liquidity contract, blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance/calculation contract, blueprint, renderer and tests |

Indicator invariants: warm-up nulls; candle-index alignment; prefix causality/no future repaint; reject invalid/gapped data; clear stale output on identity changes. Footprint OFF keeps standard candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visuals remain gated on user references and reviewed blueprint. Aggregate indicator percentage remains NOT SCORED because study weights/denominator are not approved.

## Stage 2 — mandatory On-demand Market Subscription

Still OPEN and not implemented end-to-end. Frontend supervisor is singleton-owned; backend provider ingestion is process/configuration scoped; downstream WebSocket fan-out does not prove upstream demand pooling. Databento's fixed-symbol adapter is not a verified dynamic demand API. Official source review found CME's real-time API is a monthly subscription/order product, public delayed quotes are a web display rather than a proven app redistribution API, and the delayed REST feed requires OAuth entitlement plus a Public Website (Delayed) Redistribution license. Databento's usage-based tier is historical-only and live plans are paid. No recurring-$0 feed with exact CME instrument coverage and app redistribution rights has been approved. References: [CME API ordering](https://www.cmegroup.com/tools-information/webhelp/data-services-portal/Content/Ordering-CME-Group-Market-Data-APIs.html), [CME delayed quotes](https://www.cmegroup.com/market-data/browse-data/delayed-quotes.html), [CME delayed REST licensing](https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/1892122625/Distribution+Trades+and+Settlements+REST+API), [Databento pricing](https://databento.com/pricing/). Do not add a disconnected reference counter or scrape a public quote page as an API.

Required: approve recurring-$0 compatible feed and rights; verify provider API/version semantics; implement idempotent per-series ownership/reference counts; connect chart open/switch/close/background; prove two-user isolation and shared upstream lifecycle; preserve unsupported series as unavailable rather than substituting unlicensed data.

## ZERO COST and release boundary

No paid provider, account, credential, cloud resource, deployment, payment method, device/Termux operation or main-branch modification was introduced. OCI CI readiness is not cloud installation. A fully featured production platform cannot be guaranteed by 24 December while recurring-$0 data, external hosting and device acceptance remain unresolved.

---
# CURRENT PROJECT PROGRESS — Batch 62J-147 (22 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Pre-cycle exact documentation HEAD:** `0004fd4bbc1a768079e9474aa0bbdd1b954cbc45`  
**Batch 62J-147 commits:** ADR `85e262004444130cab7af09efae7ec995b8d7269`; indicator ledger `8ce4762ba9ebe5933757e0a7057b13ce2bb71908`; work-cycle report `96b0c2ea4bf05c07359ee00032cff2f598ad8d16`.  
**This progress snapshot:** pending final documentation commit.  
**Main:** untouched.

## Batch 62J-147 — On-demand provider capability / ZERO COST audit

New report: `docs/WORK_CYCLE_2026-11-22_BATCH62J147_ON_DEMAND_PROVIDER_ZERO_COST_AUDIT.md`.

Confirmed:
- The chart client currently has one singleton supervisor owner and exact-series WebSocket subscription; not yet a general multi-chart manager.
- Backend `OhlcvStreamHub` fans out validated bars to per-client queues but is not a provider upstream demand pool.
- `ProviderManager` starts configured provider ingestion with application lifecycle.
- `DatabentoLiveSource` subscribes once to a fixed symbol tuple; no dynamic chart-demand API is wired.
- The adapter labels real SDK signatures/behavior unverified; tests use a fake SDK.
- Dependency range `databento>=0.88,<1` is not an exact SDK pin.
- Repository ZERO COST policy excludes Databento from recurring-$0 live baseline; trial credits are finite and live requires paid entitlement.
- Existing public data candidates are not automatically equivalent to the CME futures target and require feed/rights verification.

**Decision:** no runtime code changed. A disconnected demand-counter helper would not stop fixed-symbol provider ingestion and would create false progress. Stage 2 On-demand remains mandatory and open. Need a recurring-$0 compatible data source or mark unsupported data unavailable; verify provider dynamic-subscription semantics before implementing the coordinator.

## Exact-HEAD CI — pre-cycle HEAD `0004fd4bbc1a768079e9474aa0bbdd1b954cbc45`

All four workflows completed SUCCESS:
- Automated Tests [45016264628](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016264628)
- CodeQL [45016264675](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016264675)
- Full Git History Secret Audit [45016264627](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016264627)
- OCI ARM64 Image Readiness [45016264696](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016264696)

This CI result applies only to the exact pre-cycle HEAD above. The new Batch 62J-147 documentation commits trigger new runs; do not transfer the green status to the final documentation HEAD until all exact-HEAD workflows complete.

## Stage allocation and project progress

On-demand Market Data Subscription belongs primarily to **Stage 2 — Market Data Infrastructure**. Stage 1 provides authentication, session isolation, foreground/background lifecycle, safe disconnect and reconnect/snapshot/replay prerequisites. Do not award Stage 1 credit for Stage 2 upstream demand management.

| Stage | Progress | Status |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 |
| 2. Market Data Infrastructure | Not scored | ⬜ Not officially opened |
| 3. Chart Engine & Timeframe | Not scored | ⬜ |
| 4. Indicators & Analytics | Not scored | ⬜ |
| 5. Professional UI & Interactive Tools | Not scored | ⬜ |
| 6. Hardening, Validation & APK Release | Not scored | ⬜ |

Overall project: **NOT SCORED**. Stage weights and total denominator are not approved. Gate 10 remains **0/10 external criteria formally closed**. Open gates include 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. CI does not close owner-host/public-device acceptance gates.

## Full indicator status

| Indicator/component | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 | 20-close arithmetic mean; first index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render tests |
| EMA20 | 🟨 | SMA-seeded EMA, alpha 2/21; first index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render tests |
| RSI14 Wilder | 🟨 | Wilder smoothing; first index 14 | 0–100 pane, 30/70 guides, toggle/legend and render tests |
| MACD12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle/legend and render tests |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population SD; first index 19 | Three-line overlay, toggle/values and render tests |
| Shared Indicator Hook | 🟨 | Exact backend snapshot/aligned calculation | Hook tests, chart binding, stale clearing and renderer |
| Footprint | 🟧 | Synthetic educational accumulator only | User reference, reviewed blueprint, valid bid/ask source and cluster acceptance |
| Heatmap | 🟥 | Not implemented | User reference, validated depth/liquidity contract, blueprint and renderer |
| Liquidation Maps | 🟥 | Not implemented | Valid provenance/calculation contract, reviewed blueprint and renderer |

No indicator code or tests changed in Batch 62J-147; zero indicator implementation credit. Preserve warm-up nulls, candle-index alignment, prefix causality/no future repaint, invalid/gapped-bar rejection, stale-output clearing and Footprint OFF standard candle spacing. Footprint/Heatmap visual implementation remains reference-gated. Full mathematical and visual acceptance audit: `docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md`.

## Deadline realism

Target: 31 December 2026. From 22 November there are 39 calendar days through year end. Full six-stage completion, public hosting, source licensing, real-device acceptance and all advanced indicators cannot be guaranteed within that window while the recurring-$0 data source remains unresolved. Prioritize a verified installable ZERO COST MVP; do not mislabel unsupported or unlicensed data as production-ready.

## ZERO COST / integrity

No paid provider, cloud resource, deployment, account, production credential, payment method, runtime code, schema, dependency or device/Termux action was added. No main-branch modification. Full cycle report: `docs/WORK_CYCLE_2026-11-22_BATCH62J147_ON_DEMAND_PROVIDER_ZERO_COST_AUDIT.md`.

---

# CURRENT PROJECT PROGRESS — Batch 62J-146 (22 November 2026)

## Batch 62J-146 source-audit addendum — on-demand gap confirmed

Source review of `src/components/CandlestickChart.tsx`, `src/services/ohlcvStreamSupervisor.ts`, `src/services/ohlcvWebSocketClient.ts`, `backend/app/main.py`, `backend/app/provider.py` and `backend/app/ohlcv_stream.py` found:

- The chart component starts one exact-series supervisor for the selected contract/timeframe and ties it to visibility/network lifecycle.
- The frontend supervisor has a module-level singleton owner; a new chart selection stops the previous owner. This is not yet a multi-chart subscription manager.
- The WebSocket client sends one exact-series subscribe after authentication and handles ticket renewal, heartbeat, replay and sequence validation.
- The backend starts its configured `ProviderManager` during application lifespan in non-replica mode. Provider ingestion is process-scoped/configuration-scoped, not currently driven by active chart subscriber demand.
- `OhlcvStreamHub` maintains bounded per-client subscriptions and fans accepted bars to matching exact-series subscribers. It is downstream fan-out, not provider upstream pooling or reference-counted upstream activation.

**Result:** current code provides single-chart exact-series subscription and per-client fan-out foundations, but does not prove that unopened pairs consume zero upstream provider data or that equivalent users share one upstream connection. This is a confirmed Stage 2 gap. No runtime changes were made; provider-demand ownership, multi-chart support scope and upstream SDK subscription semantics need a dedicated implementation design and tests first.


This is the latest project snapshot. Verify the live branch ref and exact-HEAD workflows before using this record as a new implementation baseline.

**Active branch:** `phase-2/market-data-foundation`  
**Verified source/test HEAD before documentation-only Batch 62J-146:** `06a3c3c9e5b5ecd2ff4c8c29e0e472972c1c6e7e`  
**Batch 62J-146 documentation commits:** ADR `e21fd8ea7e7d956a507044dee97ba4b179189f62`; indicator ledger `4a4932924cb80afd44925dc50af91a15aae9e74e`; this progress snapshot is the final documentation update in this batch.  
**Main:** untouched.

## Exact-HEAD source/test CI — verified SUCCESS

All four workflows below completed successfully on exact source/test HEAD `06a3c3c9e5b5ecd2ff4c8c29e0e472972c1c6e7e`:
- Automated Tests [45006546194](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45006546194): **SUCCESS**.
- CodeQL [45006545959](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45006545959): **SUCCESS**.
- Full Git History Secret Audit [45006545947](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45006545947): **SUCCESS**.
- OCI ARM64 Image Readiness [45006545965](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45006545965): **SUCCESS**.

The Automated Tests workflow completed frontend dependency audit, unit tests and build; Android host preflight/publisher tests; backend tests; isolated Redis TLS CA/hostname fixture; bounded synthetic SQLite outbox and metrics checks; backend container build/smoke; and image scan. These are repository CI and isolated synthetic tests, not public-host/device acceptance. The source/test commit changed only `backend/tests/test_api.py` to test HTTPS one-time WebSocket ticket issuance, ticket-authenticated real loopback WSS, renewal, and two-user disconnect isolation.

**Documentation-head qualification:** Batch 62J-146 adds documentation commits after the green source/test HEAD. The final documentation HEAD triggers its own workflows; do not transfer the source/test SHA's green status to a later documentation SHA until those exact-HEAD runs complete.

## Batch 62J-146 — on-demand market-data architecture

Created [ADR_ON_DEMAND_MARKET_DATA_SUBSCRIPTIONS.md](ADR_ON_DEMAND_MARKET_DATA_SUBSCRIPTIONS.md).

Decision:
- On-demand subscription is primarily a **Stage 2 — Market Data Infrastructure** capability.
- Stage 1 provides prerequisites only: verified identity/ticket, per-user isolation, entitlement, foreground/background lifecycle, safe disconnect and reconnect/snapshot/replay.
- Catalogue/search/watchlist views must not start pair streams or polling.
- Only chart surfaces actively viewed may subscribe to their exact canonical series.
- Pair switch/close/background must release that user's subscription.
- Equivalent subscribers should share one provider upstream where the provider contract supports it; reference counting stops it only after the final subscriber leaves.
- One user's disconnect must not stop another user's stream or the independent backend.
- Mobile data and host free-tier budgets are separate; heartbeat/auth/reconnect may still use some network data.
- No claim of upstream deduplication or quota savings without direct tests.

**Implementation status:** accepted requirement/design direction; end-to-end implementation and acceptance are NOT YET PROVEN. The existing real-WSS test proves TLS/Origin/ticket renewal and per-client disconnect isolation, not chart-driven subscription ownership or shared provider upstream.

## Official stage progress

| Stage | Progress | Status |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 |
| 2. Market Data Infrastructure | Not scored | ⬜ Not officially opened |
| 3. Chart Engine & Timeframe | Not scored | ⬜ Not officially opened |
| 4. Indicators & Analytics | Not scored | ⬜ Not officially opened |
| 5. Professional UI & Interactive Tools | Not scored | ⬜ Not officially opened |
| 6. Hardening, Validation & APK Release | Not scored | ⬜ Not officially opened |

**Overall project: NOT SCORED.** Six-stage weights and total acceptance denominator are not approved. Do not calculate an aggregate percentage. Stage 1's provisional 75% is not overall completion.

**Gate 10: 0/10 external criteria formally closed.** Open criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Gate 25 (snapshot provenance/replica receipt and owner-host recovery), Gate 36 (public WSS/live Firebase/Android lifecycle), and Gate 38 (durable operational metrics/alerts/recovery) remain OPEN.

## Complete indicator status

| Indicator/component | Status | Verified scope |
|---|---|---|
| SMA20 | 🟨 | 20-close mean; first valid index 19 |
| EMA20 | 🟨 | SMA-seeded EMA, alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 | Wilder smoothing; first valid index 14 |
| MACD12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population SD; first valid index 19 |
| Shared Indicator Hook | 🟨 | Backend snapshot/aligned output; not fully chart-integrated |
| Footprint | 🟧 | Synthetic educational accumulator only; not exchange-native bid/ask truth |
| Heatmap | 🟥 | Not implemented |
| Liquidation Maps | 🟥 | Not implemented |

No indicator implementation changed in this batch. No indicator credit is awarded. Preserve warm-up nulls, candle-index alignment, prefix causality/no future repaint, invalid/gapped-bar rejection, stale-series clearing, and Footprint OFF standard candle spacing. Footprint/Heatmap visuals require user reference images and a reviewed blueprint. Full ledger: [INDICATOR_PROGRESS_LEDGER.md](INDICATOR_PROGRESS_LEDGER.md).

## Hosting and cost status

Cloudflare Workers + Durable Objects remains an architecture candidate only, not selected or deployed. Render Free remains a limited sleeping proof-of-concept candidate. OCI is not selected because card verification conflicts with the current constraint. No provider account, resource, deployment, payment method, production credential or paid service was created. Any provider account must be owned/managed by a parent or guardian.

## ZERO COST and branch integrity

No paid resource, provider signup, deployment, production credential, payment method, device/Termux operation or schema/runtime change was made in Batch 62J-146. Active branch remains `phase-2/market-data-foundation`; `main` remains untouched.

# CURRENT PROJECT PROGRESS — Batch 62J-143 (22 November 2026)

This snapshot supersedes earlier dated summaries below.

**Branch:** `phase-2/market-data-foundation`  
**Latest source HEAD:** `bd83d40bdf58262922462d67cde3da6c1f4a4387`  
**Latest documentation commit:** `c8e216ff362289f8d05fd276b71e102672e16006`  
**Main:** untouched.

## Latest product behavior change

- Account UI now exposes Google sign-in only; signed-in users see account identity and Sign out. Email/password fields and account creation are no longer exposed by the panel.
- WebSocket pauses on hidden/offline and explicit `pagehide`; it resumes on `pageshow`/visible/online with fresh Firebase ID token and one-time ticket.
- App is foreground-only. No background keep-alive or paid server is required by this client lifecycle.
- Exact-HEAD CI on source HEAD `bd83d40...` was pending when recorded; see [Batch 62J-143 work cycle](WORK_CYCLE_2026-11-22_BATCH62J143_GOOGLE_ONLY_FOREGROUND_WEBSOCKET.md). Do not transfer earlier green status to this HEAD.

## Hosting status

Cloudflare Durable Objects remains a candidate architecture only, not selected/deployed. Render Free is a sleeping proof-of-concept only. OCI is blocked on card verification. No provider signup, cloud resource or deployment occurred. Any cloud account must be owned/managed by a parent/guardian.

## Stage and Gate progress

| Stage | Progress | State |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 |
| 2. Market Data Infrastructure | Not scored | ⬜ Not officially opened |
| 3. Chart Engine & Timeframe | Not scored | ⬜ Not officially opened |
| 4. Indicators & Analytics | Not scored | ⬜ Not officially opened |
| 5. Professional UI & Interactive Tools | Not scored | ⬜ Not officially opened |
| 6. Hardening, Validation & APK Release | Not scored | ⬜ Not officially opened |

**Gate 10: 0/10 external criteria formally closed.** Open: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.  
**Overall project: NOT SCORED** because six-stage weights and total acceptance denominator are not approved.

## Indicator snapshot

SMA20 🟨; EMA20 🟨; RSI14 Wilder 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; Shared Indicator Hook 🟨; Footprint 🟧 (synthetic educational prototype only); Heatmap 🟥; Liquidation Maps 🟥. No indicator code changed in Batch 62J-143. Full details and mathematical invariants remain in [INDICATOR_PROGRESS_LEDGER.md](INDICATOR_PROGRESS_LEDGER.md).

**IPS35:** pending exact-HEAD CI. No numeric score assigned.

ZERO COST: no paid service, cloud account/resource, deployment, payment method, production credential, or device/Termux operation.

---

# CURRENT PROJECT PROGRESS — Batch 62J-142 (22 November 2026)

This verified snapshot supersedes older dated summaries below.

**Branch:** `phase-2/market-data-foundation`  
**Starting HEAD:** `ad3fa4413cdc827d49e6ec05731f0cd90360c75d`  
**Documentation update commit:** `ddc3d169359bab366fbcede6bee6dd64b1552181`  
**Main:** untouched.

## Exact-HEAD CI on starting HEAD

- Automated Tests [45001169602](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45001169602): **SUCCESS**.
- CodeQL [45001169566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45001169566): **SUCCESS**.
- Full Git History Secret Audit [45001169507](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45001169507): **SUCCESS**.
- OCI ARM64 Image Readiness [45001169506](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45001169506): **SUCCESS**.

These four workflows are green on the exact starting HEAD. The new documentation commit has triggered a new CI cycle and must not inherit those pass claims until its own exact-HEAD runs finish.

## WebSocket / hosting assessment

The supervisor ownership and delayed-callback regression changes are accepted by the starting-HEAD CI. OCI ARM64 readiness is CI-only, not an OCI deployment.

Hosting decision:
- Cloudflare Workers + SQLite-backed Durable Objects: strongest architecture candidate for stateful WebSocket coordination, but it is not a drop-in runtime for the existing Python/container backend. Provider signup/payment verification is **UNVERIFIED**; no account or deployment.
- Render Free Web Service: supports WebSockets and Docker, but spins down after 15 minutes without inbound traffic, can take about one minute to wake, has ephemeral local filesystem, and its free Postgres expires after 30 days. Temporary POC only, not continuous authoritative market-data hosting.
- OCI Always Free: blocked by required card-based identity verification for the current situation; no bypass or borrowed card.
- No provider is assumed to offer Google-only signup. Any cloud account must be owned and managed by a parent/guardian.

Detailed evaluation: [Batch 62J-142 work cycle](WORK_CYCLE_2026-11-22_BATCH62J142_ZERO_COST_WEBSOCKET_HOSTING_OPTIONS.md).

## Stage and Gate progress

| Stage | Progress | State |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 Active |
| 2. Market Data Infrastructure | Not scored | ⬜ Not officially opened |
| 3. Chart Engine & Timeframe | Not scored | ⬜ Not officially opened |
| 4. Indicators & Analytics | Not scored | ⬜ Not officially opened |
| 5. Professional UI & Interactive Tools | Not scored | ⬜ Not officially opened |
| 6. Hardening, Validation & APK Release | Not scored | ⬜ Not officially opened |

**Gate 10: 0/10 external criteria formally closed.** Open tracks: 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.  
**Overall project: NOT SCORED** because stage weights and the total acceptance denominator are not approved.

## Indicator status

SMA20 🟨; EMA20 🟨; RSI14 Wilder 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; Shared Indicator Hook 🟨; Footprint 🟧 (synthetic educational prototype only); Heatmap 🟥; Liquidation Maps 🟥. No indicator code changed; no indicator implementation credit. Full details and mathematical invariants are in [INDICATOR_PROGRESS_LEDGER.md](INDICATOR_PROGRESS_LEDGER.md).

**IPS35:** pending exact-HEAD CI on documentation commit `ddc3d169359bab366fbcede6bee6dd64b1552181`. No numeric score assigned.

ZERO COST: no paid service, account, resource, deployment, production credential, payment method, device or Termux operation.

---

# CURRENT PROJECT PROGRESS — Batch 62J-141 (22 November 2026)

This section is the latest verified snapshot and supersedes older dated entries below.

**Branch:** `phase-2/market-data-foundation`  
**Source/test baseline:** `f0c55e37998c2c32c3ba0aeab743bbe02e0c72d7`  
**Main:** untouched.

## Exact-source CI

- Automated Tests [45000228409](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45000228409): **SUCCESS**.
- CodeQL [45000228422](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45000228422): **SUCCESS**.
- Full Git History Secret Audit [45000228438](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45000228438): **SUCCESS**.

## Stage and Gate progress

| Stage | Progress | State |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 Active |
| 2. Market Data Infrastructure | Not scored | ⬜ Not officially opened |
| 3. Chart Engine & Timeframe | Not scored | ⬜ Not officially opened |
| 4. Indicators & Analytics | Not scored | ⬜ Not officially opened |
| 5. Professional UI & Interactive Tools | Not scored | ⬜ Not officially opened |
| 6. Hardening, Validation & APK Release | Not scored | ⬜ Not officially opened |

**Gate 10: 0/10 external criteria formally closed.** Open tracks: 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.  
**Overall project: NOT SCORED** because the six-stage weights and overall acceptance denominator have not been approved.

## WebSocket and OCI

The supervisor now enforces one active owner of the shared market-data store. Regression tests cover a pending Firebase token request during replacement and a delayed native WebSocket close/late message after timeframe replacement.

OCI ARM64 workflow: <badge>PASS</badge> Native ARM64 image build, backend health, PID 1 UID 10001, mounted-volume write and restart persistence all passed in run [45000816460](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45000816460) on exact HEAD `0372d488e1fd803343a06234105295b9675a3e0b`. This is CI readiness evidence only; no OCI account/resource was created or deployed.

Gates 25, 36 and 38 remain OPEN for authenticated snapshot receipts, owner-host Redis, public WSS/Firebase/Android lifecycle, and durable monitoring/recovery evidence.

## Technical indicator status

SMA20 🟨; EMA20 🟨; RSI14 Wilder 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; Shared Indicator Hook 🟨 (backend alignment foundation, not fully chart-integrated); Footprint 🟧 (synthetic educational prototype only); Heatmap 🟥; Liquidation Maps 🟥. No indicator code changed and no indicator progress credit is awarded. See [INDICATOR_PROGRESS_LEDGER.md](INDICATOR_PROGRESS_LEDGER.md).

**IPS35:** pending final documentation-HEAD CI and corrected ARM64 smoke workflow. It measures cycle delivery quality, not project completion.

ZERO COST: no paid service, cloud account/resource, deployment, production credential, payment method, device or Termux operation. OCI account ownership/verification must be handled by a parent/guardian as lawful account owner. Full report: [WORK_CYCLE_2026-11-22_BATCH62J141_WEBSOCKET_SUPERVISOR_OCI_ARM64.md](WORK_CYCLE_2026-11-22_BATCH62J141_WEBSOCKET_SUPERVISOR_OCI_ARM64.md).

---

# Batch 62J-135 — Gate 25 source audit, exact-head CI acceptance and IP3S reconciliation
Date: 22 November 2026
Branch: `phase-2/market-data-foundation`
Starting HEAD: `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`
Scope: documentation and acceptance design only; no runtime/schema/test source changes.

## Verified repository and CI state

Branch ref was verified at starting HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`; `main` was not touched.

Exact-HEAD workflows at the time of this final documentation update:
- Automated Tests [44991805066](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991805066): **SUCCESS**, exact HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`.
- CodeQL [44991805111](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991805111): **SUCCESS**, exact HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`.
- Full Git History Secret Audit [44992252234](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992252234): **SUCCESS** on the final documentation HEAD when checked.
- Automated Tests [44992252218](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992252218): **IN PROGRESS** on the final documentation HEAD at report finalization.
- CodeQL [44992252244](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992252244): **PENDING** on the final documentation HEAD at report finalization.
- Android debug APK workflow [44991640574](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640574): **SUCCESS** on source/test commit `ecf7decb8e823effe09a6be8a9973bb98619ae92`; this is CI debug-build evidence, not a production release and not a build on the later docs-only HEAD.

The exact-HEAD Automated Tests job completed successfully. The workflow job's completed steps include frontend dependency audit/unit tests/build, backend dependency installation/tests, isolated Redis TLS CA/hostname enforcement fixture, bounded synthetic SQLite outbox and metrics checks, backend container build/smoke, vulnerability scan/report and dependency audit enforcement. Earlier exact HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b` had Automated Tests, CodeQL and Secret Audit SUCCESS. After this batch's docs-only commits, only Secret Audit had completed on the final documentation HEAD; Automated Tests and CodeQL remained pending/in progress. CI success does not prove owner-host Redis persistence/failover or public WSS.

## Gate 25 — source-backed installation receipt audit

Files inspected at the starting HEAD:
- `backend/app/ohlcv_store.py`
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/ohlcv_redis_runtime.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`
- `backend/tests/test_ohlcv_replica_bridge.py`
- `docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md`

Confirmed behavior:
1. `SQLiteOhlcvReplicaStore.install_global_snapshot()` preflights the snapshot, then opens a write transaction, re-reads the snapshot and validates its manifest/content while inserting rows. Snapshot replacement and checkpoint update commit or roll back together.
2. The replica checkpoint persists source ID, replica ID, applied cursor, snapshot generation, retention metadata and schema/protocol versions. It does not persist the snapshot SHA-256 or an immutable installation receipt.
3. `build_gateway_replica_runtime_factory()` checks installer status, source ID, generation, high-water cursor, digest syntax and checkpoint alignment before creating the Redis client. The digest is returned as runtime `snapshot_evidence`; the code does not compare it to a durable receipt because no such receipt is currently stored.
4. Source-side `_validate_snapshot_evidence()` validates the snapshot manifest and requires a matching receipt for each configured gateway, including source, stream, generation, cursor and SHA-256. The callback is explicitly responsible for authenticating/reading those owner-host receipts. This validator does not itself contact or authenticate remote gateways.
5. Existing tests prove snapshot-before-Redis construction, source mismatch rejection, unverified installer rejection, production plaintext Redis rejection, and cleanup on consumer-construction failure. They do not prove durable gateway receipt persistence, signature verification, immutable receipt conflict semantics, crash/restart receipt consistency, or owner-host custody.

### Gate 25 status: OPEN

The missing feature is not simply a hash column. The acceptance contract must bind:
- authenticated authoritative source identity;
- exact snapshot generation, high-water cursor and canonical digest;
- replica identity and receipt schema;
- authenticated installer/attestation identity;
- durable immutable receipt history;
- atomicity between snapshot rows, checkpoint replacement and receipt insertion.

A SHA-256 digest establishes content identity only when compared against a trusted value. It does not independently establish who supplied the snapshot.

### Required implementation acceptance matrix (design only)

| Case | Expected result |
|---|---|
| Valid authenticated manifest and matching content | Install and persist receipt atomically |
| Altered bytes or recomputed digest mismatch | Reject; preserve prior rows/checkpoint/receipts |
| Unknown signer, wrong key or invalid signature | Reject before accepting snapshot |
| Source or replica identity mismatch | Reject |
| Same source/replica/generation and same digest | Idempotent; preserve original receipt |
| Same generation with different digest | Hard conflict; fail closed |
| New generation with valid cursor progression | Add a new immutable receipt |
| Failure before transaction commit | No partial snapshot/checkpoint/receipt state |
| Process interruption around commit then restart | Recover to either prior complete state or new complete state |
| Legacy checkpoint without receipt | Mark LEGACY_UNATTESTED; never fabricate provenance |
| Normal event cursor advancement | Preserve historical installation receipt |
| Repeated migration/rollback | Idempotent and backward-compatible; never downgrade verified provenance |

### Recommended implementation sequence — no implementation performed

1. Approve the trust model: owner-pinned public key and signed manifest, or equivalent authenticated owner-controlled transfer. Decide signature format, key ID, rotation and revocation policy.
2. Define immutable receipt schema and uniqueness key `(source_id, replica_id, generation_id)`; define explicit legacy state and retention/archival policy.
3. Add transactional receipt insertion to the same SQLite transaction as snapshot rows/checkpoint replacement.
4. Add read-only receipt query and bind gateway runtime evidence to the persisted receipt, not only the installer return value.
5. Make source-side verification consume authenticated receipt records with explicit gateway identity and custody.
6. Add failure-injection tests for tampering, signer/key errors, generation conflicts, transaction rollback, process termination, restart, migration and retention.
7. Re-run full CI on exact branch HEAD. Owner-host transfer, key custody, Redis persistence/restart/failover remain separately required external acceptance.

No runtime/schema implementation was started because the ADR is design-only and the trust/key lifecycle decisions are not yet approved.

## WebSocket acceptance gates

- Gate 25: **OPEN** — durable immutable replica installation receipt, authenticated transfer provenance and owner-host Redis persistence/restart/failover.
- Gate 36: **OPEN** — public WSS/reverse proxy/certificate lifecycle, live Firebase project, production browser session, Android WebView lifecycle and real network handover.
- Gate 38: **OPEN** — owner-host metrics persistence, disk-pressure/restart/backup/retention, operator dashboard, external alert delivery and recovery drill.
- Gate 10: **0/10 external criteria formally closed**.

The 4403 close-reason diagnostic correction from Batch 62J-134 is CI-accepted; it does not close Gate 36 or Gate 25.

## Technical indicator progress ledger

No indicator runtime, test, calculation, hook, renderer or UI source changed in this batch. No indicator implementation credit is awarded.

| Indicator/component | Current status | Verified scope / limitation |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19 |
| EMA20 | 🟨 Foundation | SMA-seeded, alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram index 33 |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; not chart-integrated |
| Footprint | 🟧 Prototype/foundation only | Synthetic educational accumulator; not exchange-native bid/ask truth |
| Heatmap | 🟥 Not implemented | Visual implementation blocked pending user reference image and reviewed blueprint |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence |

Shared requirements remain: warm-up nulls, candle-index alignment, prefix causality/no future-candle repaint, invalid/gapped bars not silently converted to zero, stale-output clearing on symbol/venue/dataset/chart/timeframe changes, and renderer/lifecycle validation. Footprint OFF must preserve ordinary candlestick spacing; only explicit ON enables the dedicated spaced cluster layout. Footprint and Heatmap visual implementation must wait for the user's reference image(s) and reviewed blueprint.

No aggregate indicator completion percentage is assigned because indicator weights and denominator are not approved.

## Project-wide progress indicator

| Stage | State |
|---|---|
| 1. Foundation, Security & Data Integrity | 30/40 criteria = **75% provisional** |
| 2. Market Data Infrastructure | **NOT SCORED / not officially opened** |
| 3. Chart Engine & Timeframe | **NOT SCORED / not officially opened** |
| 4. Indicators & Analytics | **NOT SCORED / not officially opened** |
| 5. Professional UI & Interactive Tools | **NOT SCORED / not officially opened** |
| 6. Hardening, Validation & APK Release | **NOT SCORED / not officially opened** |

Overall project: **NOT SCORED**. Six-stage weights and the overall acceptance denominator have not been approved. Do not derive an overall percentage from Stage 1 alone.

## IP3S — Indicator Proses Peningkatan Proyek Signifikan

IP3S measures this work cycle's verified delivery quality, not project completion.

| Dimension | Score | Rationale |
|---|---:|---|
| Verified engineering delta | 18/25 | Batch 62J-134 corrected a real false WebSocket 4403 diagnostic and added regression coverage; this batch completed source-backed Gate 25 acceptance analysis, but made no new runtime change |
| Exact-HEAD test/CI evidence | 14/20 | Automated Tests, CodeQL and Secret Audit all SUCCESS on exact HEAD |
| Blocker reduction | 12/20 | Gate 25 trust/receipt gap and implementation acceptance cases are now isolated; gate remains open |
| Canonical documentation | 20/20 | Gate 25 source audit, matrix, indicator ledger and project-stage state reconciled |
| Scope/cost integrity | 15/15 | ZERO COST; correct branch; no credentials, deployment, device work or main changes |
| **IP3S total** | **79/100** | Cycle delivery score only; not overall completion |

## Cost, safety and branch integrity

ZERO COST. No paid service, hosting, domain, API, cloud resource, account, deployment, production credential, secret, Android device or Termux action. No runtime/schema/test source edits in Batch 62J-135. `main` untouched.


---

## Batch 62J-134 — WebSocket close-reason accuracy fix (22 November 2026)

Source/test commit: `ecf7decb8e823effe09a6be8a9973bb98619ae92` on `phase-2/market-data-foundation`.

### Engineering change
Backend source uses WebSocket close code 4403 for both:
- Origin policy rejection: reason `Origin not allowed` before authentication.
- Canonical instrument/series entitlement denial: reason such as `Instrument access denied` or `Instrument access revoked`.

Previously the client supervisor mapped every 4403 to an entitlement failure. That produced a false diagnosis for a frontend Origin configuration error. The supervisor now classifies 4403 by the server-provided close reason:
- Origin rejection → “WebSocket Origin is not allowlisted” diagnostic.
- Other 4403 reasons → entitlement denial/revocation diagnostic.
Both remain terminal and do not trigger an automatic reconnect loop.

Regression tests cover both branches, verify the error and snapshot detail, and verify no retry. Files changed:
- `src/services/ohlcvStreamSupervisor.ts`
- `src/services/ohlcvStreamSupervisor.test.ts`

This is a diagnostic correctness fix only; it does not weaken authentication, authorization, Origin enforcement, or reconnect policy.

### Exact-commit CI status
- Automated Tests run [44991640588](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640588): **IN PROGRESS** at documentation time; frontend unit tests and frontend build passed, Redis TLS fixture passed, backend tests still running.
- CodeQL run [44991640593](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640593): **SUCCESS** (JavaScript/TypeScript and Python).
- Full Git History Secret Audit run [44991640577](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640577): **SUCCESS**.
- Zero-cost Android debug APK workflow [44991640574](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640574): **IN PROGRESS**; web build and Android wrapper setup passed, APK assembly still running.

Do not call the new regression tests accepted until Automated Tests completes successfully. No APK artifact is claimed until its workflow reports success.

### Remaining WebSocket acceptance
- Gate 25 OPEN: immutable snapshot installation digest/provenance receipt, owner-authenticated transfer and owner-host Redis acceptance.
- Gate 36 OPEN: public WSS/reverse proxy/certificate lifecycle, live Firebase project, production browser session and Android WebView foreground/background/process-death/network handover.
- Gate 38 OPEN: owner-host metrics persistence, disk pressure/restart/backup/retention and operator dashboard/alert/recovery.
- Redis TLS/AOF restart: isolated CI fixture PASS on the preceding exact-head docs baseline; owner-host failover/backup/restore remains untested.

### Indicator and project indicators
No indicator source or tests changed; indicator implementation status receives no credit:
- SMA20 🟨 foundation (first valid index 19).
- EMA20 🟨 SMA-seeded alpha 2/21 (first valid index 19).
- RSI14 Wilder 🟨 foundation (first valid index 14).
- MACD12/26/9 🟨 foundation (MACD index 25; signal/histogram index 33).
- Bollinger20,2 🟨 foundation (first valid index 19).
- Shared Indicator Hook 🟨 backend snapshot/alignment only; not chart-integrated.
- Footprint 🟧 synthetic educational accumulator only; wait for user visual reference and reviewed blueprint.
- Heatmap 🟥 not implemented; wait for user visual reference and reviewed blueprint.
- Liquidation Maps 🟥 not implemented.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 remain NOT SCORED; Gate 10 remains 0/10 external criteria formally closed. Overall project remains NOT SCORED until stage weights and acceptance denominator are approved.

IP3S for this batch is **PENDING** until exact-commit Automated Tests completes. This prevents unverified source changes from receiving CI-evidence credit. ZERO COST; no deployment, paid service, production credentials, device/Termux operations or `main` changes.

---

## Batch 62J-132 — exact-baseline CI acceptance and indicator reconciliation (22 November 2026)

**Source/test baseline:** `d549d99318abbeb156f716a4e2cf749eef226ca9` on `phase-2/market-data-foundation`. This is the commit tested by the three successful workflows; the documentation follow-up commit is a separate HEAD and must receive its own CI check.

- Automated Tests [44989988543](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988543): **SUCCESS**.
- CodeQL [44989988481](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988481): **SUCCESS** for JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44989988510](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988510): **SUCCESS**.
- Automated Tests include backend tests, real Redis TLS fixture, synthetic outbox/metrics benchmarks, backend dependency audit, backend container build, persistent-volume/shared-Redis-guard smoke test, image scan and frontend dependency audit enforcement.
- Trivy 0.76.2 scan of backend image digest `sha256:2943078f07ff217aedcdea4577b1edfed2c0355abbef37fa68d558110a71b643`: **0 OS vulnerabilities, 0 Python package vulnerabilities, 0 reported misconfigurations** in the exported CI report. Point-in-time CI image evidence only.
- Synthetic outbox: 1,000 bars; persist p95 4.155 ms / p99 5.943 ms; two replay readers p95 1.659 ms / p99 1.910 ms. Not a WebSocket or production SLO test.
- Synthetic metrics collector (899 logical series): four-process p95 flush 139.854 ms, p99 277.444 ms, 3 retries; 16-worker staggered-process p95 287.759 ms, p99 524.206 ms, 44 retries; 16-thread p95 594.880 ms, p99 844.445 ms, 213 retries. SQLite integrity remained `ok`; writer-lock contention is material at high fan-out. This is operational telemetry storage, not OHLCV WebSocket delivery.
- **Correction:** backend container persistent-volume smoke test does not prove Redis AOF durability/restart/failover. Those remain open.

### WebSocket acceptance
- Gate 25: **OPEN** — snapshot digest is not anchored in an immutable receipt; authenticated owner-host transfer/receipt custody and owner-host Redis persistence/restart/failover remain unproven. Proposed ADR: `docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md`.
- Gate 36: **OPEN** — public hostname/reverse proxy/WSS certificate lifecycle, live Firebase, production browser and Android WebView/network-handover acceptance remain unproven. Series/Origin ticket binding remains a threat-model item.
- Real TLS fixture covers trusted CA, wrong CA, hostname mismatch, plaintext downgrade rejection and shared-guard ticket/lease operations; CI-only evidence.

### Technical indicator ledger — unchanged implementation status
SMA20 🟨 foundation (first index 19); EMA20 🟨 SMA-seeded alpha 2/21 (first index 19); RSI14 Wilder 🟨 (first index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram index 33); Bollinger20,2 🟨 (first index 19); Shared Indicator Hook 🟨 backend alignment only; Footprint 🟧 synthetic educational accumulator and reference-gated; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. No indicator code/test changed, so no implementation credit.

Preserve warm-up nulls, candle alignment, no future-candle repaint, stale clearing on identity/timeframe changes and standard candle spacing while Footprint is OFF. Footprint/Heatmap visual work remains gated on user reference images and reviewed blueprint.

### Project progress and IP3S
- Stage 1: 30/40 = **75% provisional**. Stages 2–6 NOT SCORED. Gate 10 = 0/10 formally closed. Overall project = **NOT SCORED** because approved stage weights/denominator do not exist.
- **IP3S Batch 62J-132: 67/100** (cycle quality only): engineering delta 0/25; exact-baseline CI 20/20; blocker/evidence reduction 12/20; documentation 20/20; ZERO COST/scope integrity 15/15. Not overall completion.
- ZERO COST, docs/evidence only; no runtime/test source, no deployment, no paid services, no secrets, no device/Termux and no `main` changes.

## Batch 62J-131 — WebSocket replica recovery, exact-head CI and project progress (22 November 2026)

**Verified branch HEAD:** `5be3cff9c19064cbcc9ad686aaf359efb4e5c03d` on `phase-2/market-data-foundation`.

**Exact-head CI — all SUCCESS:**
- Automated Tests [44989326413](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326413)
- CodeQL [44989326466](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326466)
- Full Git History Secret Audit [44989326442](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326442)

### New source-to-test acceptance evidence

- Publisher: 21 named tests cover deterministic cursor IDs, canonical payloads, ambiguous XADD/lost-reply recovery, conflict rejection, checkpoint fencing, retention and snapshot rebase. The publisher advances its durable checkpoint only after confirmed append or exact read-back.
- Consumer: 20 named tests cover SQLite apply-before-ACK, callback retry/idempotence, own-pending-first recovery, XAUTOCLAIM, independent gateway groups, multi-process broadcast, lease-loss-before-ACK, ACL separation and snapshot-generation convergence.
- Worker: 5 tests cover bounded retry/backoff, terminal resnapshot and ownership-loss behavior, and bounded shutdown.
- Replay: 11 tests cover global cursor scanning, fixed replica watermark, history gaps, retention/cursor-ahead, series validation and bounded all-or-resnapshot behavior.
- Stream hub: 10 tests cover atomic snapshot/live boundary, exact-series isolation, slow-consumer resnapshot and replay merge.
- Browser supervisor: 22 tests cover ticket/token retries, bounded reconnect, cursor replay, sequence-gap resnapshot, terminal auth/entitlement/policy rejection and close/stop races.
- A real TCP-path interruption test launches two ASGI gateway processes behind independent fault proxies, severs their Redis TCP paths, rejects reconnects during outage, restores connectivity, and verifies both clients receive the same cursor and both replica checkpoints converge. This is CI-local/ephemeral evidence, not public WSS or owner-host acceptance.

### Production boundary

Gate 25 remains OPEN: the installer is owner-supplied; its digest is format-checked and propagated but not anchored in the durable replica checkpoint. Authenticated owner-host snapshot transfer/receipts, Redis TLS/ACL/persistence/restart/failover remain unproven.

Gate 36 remains OPEN: ticket auth, series authorization, reconnect/replay and local TCP fault recovery are covered in repository tests. Public hostname/reverse proxy/TLS, live Firebase, real browser production session, Android WebView lifecycle and real public network handover remain unproven. Series/Origin ticket binding remains a threat-model decision, not an assumed defect.

### Indicator ledger

No indicator source/test changed; no implementation credit:
- SMA20 🟨 foundation, first valid index 19.
- EMA20 🟨 SMA-seeded, alpha 2/21, first valid index 19.
- RSI14 Wilder 🟨 foundation, first valid index 14.
- MACD12/26/9 🟨 foundation, MACD index 25; signal/histogram index 33.
- Bollinger20,2 🟨 foundation, first valid index 19.
- Shared Indicator Hook 🟨 backend snapshot/alignment foundation, not chart-integrated.
- Footprint 🟧 synthetic educational only; reference-image and reviewed-blueprint gate.
- Heatmap 🟥 not implemented.
- Liquidation Maps 🟥 not implemented.

Preserve warm-up nulls, candle-index alignment, no future-candle repaint, stale clearing on identity/timeframe changes and Footprint OFF normal candle spacing. Do not assign aggregate indicator percentage without approved weights/denominator.

### Project progress

Stage 1 = 30/40 = **75% provisional**. Stage 2–6 remain NOT SCORED/not officially opened. Gate 10 = **0/10 formally closed**. Overall project = **NOT SCORED** until six-stage weights and denominator are approved.

### IP3S — Indicator Proses Peningkatan Proyek Signifikan

Batch 62J-131 = **61/100** (cycle delivery quality only): engineering delta 0/25; exact-head CI 20/20; blocker reduction 8/20; canonical documentation 18/20; scope/cost integrity 15/15. This is not project completion.

**ZERO COST:** documentation-only; no runtime/test change, paid resource, deployment, credential, device/Termux work or main-branch change.

Full report: [WORK_CYCLE_2026-11-22_BATCH62J131_WEBSOCKET_REPLICA_ACCEPTANCE_IP3S.md](WORK_CYCLE_2026-11-22_BATCH62J131_WEBSOCKET_REPLICA_ACCEPTANCE_IP3S.md).

---

## Batch 62J-125 — WebSocket test-evidence mapping and production acceptance gap review (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Reviewed documentation/source baseline:** 4cb91f518b14cff2b6d7ee1af3c53ed836dd6b5d  
**CI on this baseline:** Automated Tests run [44986546422](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986546422), CodeQL [44986546414](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986546414), and Full Git History Secret Audit [44986546413](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986546413) all SUCCESS on exact SHA `4cb91f518b14cff2b6d7ee1af3c53ed836dd6b5d`.

### New source/test evidence mapped

- Redis ticket issuance stores only a SHA-256 digest-keyed ticket record with account subject and purpose, 90-second TTL and create-only `SET NX`. Lua consume performs GET+DEL atomically. Tests cover digest-keying, subject binding, exact TTL, malformed/corrupt/wrong-purpose rejection, one-use consume, Redis TTL/consume integration, and a multi-process ticket+account-lease test.
- HTTPS ticket endpoint requires a verified principal and returns ticket, expiry and purpose. WebSocket handshake rejects disallowed non-empty Origin, consumes ticket before accepting its subject as principal, and applies separate exact-series/canonical-instrument entitlement authorization. Ticket does not itself bind the requested series or Origin; retain this as a threat-model review item.
- Firebase verifier tests require revoked-token checking and validate subject/claims using test doubles. These are not live Firebase-project credential, revocation, entitlement grant/revoke/renew E2E tests.
- Redis gateway tests verify snapshot installation precedes Redis client construction and installed source/generation/high-water cursor metadata matches the durable local checkpoint. The installer-returned SHA-256 is format-checked and propagated, but the replica checkpoint does not persist a snapshot digest; therefore the digest is not compared against a digest anchored in that checkpoint. Source mismatch fails before Redis construction, and production plaintext Redis is rejected. The callback is still owner-supplied; repository tests do not authenticate remote transfer receipts or prove independent gateway receipt custody.
- Replay tests verify global cursor advancement across unrelated series, missing cursor/history-gap fail-closed behavior, fixed checkpoint watermark, retention expiry/cursor-ahead rejection, and bounded scan/event limits with resnapshot response.
- Browser WebSocket tests cover ticket auth, exact-series subscribe, snapshot/update, durable cursor replay before live updates, renewal acknowledgement, heartbeat/error cleanup and reconnect supervisor recovery. These are simulated browser-socket tests, not public reverse-proxy or real browser/network deployment evidence.
- Server source checks Origin allowlist, performs periodic entitlement recheck and Redis lease renewal, and closes fail-closed on Redis/lease failure. Backend tests cover Redis outage and lease renewal failure. CI Redis is ephemeral.
- Android host preflight and immutable preview-publisher tests run in CI; they do not constitute Android device/WebView foreground-background, process-death, network handover or reconnect acceptance.

### Acceptance status — unchanged

Gate 25 remains OPEN pending owner-host snapshot transport authentication, independently authenticated per-gateway installation receipts, byte/hash custody and exact generation/high-water alignment under real Redis persistence/restart/failover.

Gate 36 remains OPEN pending verified public HTTPS/WSS endpoint, reverse proxy/TLS, real Firebase project, browser and Android WebView lifecycle tests, reconnect/replay/resnapshot and duplicate suppression across real network interruption, plus operator logs/alerts. Subject/purpose ticket binding and separate series authorization remain as implemented; adding series/Origin into ticket claims is a threat-model decision requiring explicit design review, not an assumed code change.

Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional. CI/source tests do not close production owner-host gates.

### Indicator reconciliation — no implementation credit

No indicator implementation or test changed. Canonical statuses remain:
- SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2, and Shared Indicator Hook: 🟨 foundation, not fully chart-integrated.
- Footprint: 🟧 synthetic educational accumulator only; visual implementation waits for user reference image(s) and reviewed blueprint.
- Heatmap and Liquidation Maps: 🟥 not implemented.

Warm-up null semantics, source-index alignment, no future-candle repaint, stale-series clearing and Footprint OFF normal candle spacing remain requirements. No aggregate percentage is assigned without approved weights/denominator.

### Cost and scope

ZERO COST. No source changes, external services, paid hosting, domains, deployment, cloud resource, account, production credentials, Android device action or Termux work. `main` untouched. This batch is documentation-only.

---

## Batch 62J-124 — exact-head CI, SQLite contention and WebSocket acceptance reconciliation (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Exact source/test HEAD:** 332fd0dacdcd383a27744ea4b9f76d7cbe418cdc  
**Automated Tests #1962 [run 44986046696](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696): SUCCESS**; **CodeQL [run 44986046674](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046674): SUCCESS**; **Full Git History Secret Audit [run 44986046694](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046694): SUCCESS**. All three workflows target the same exact SHA.

### Exact-head CI and artifact evidence
- Automated Tests job completed successfully: frontend dependency audit/tests/build and bundle secret scans; Android host preflight and preview publisher tests; backend dependency installation and tests; isolated Redis TLS CA/hostname fixture; synthetic SQLite outbox and metrics benchmarks; backend container build; shared-Redis-guard/persistent-CI-volume smoke; Trivy scan/report; dependency audit enforcement. All 30 main job steps completed successfully.
- Synthetic metrics artifact [14739229002](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696/artifacts/14739229002) was downloaded and independently inspected. Full 899 logical-series envelope; 1 worker: 32/32 flushes, 0 retries, p95 flush 8.19 ms, SQLite integrity ok; 4 threads: 128/128, 2 retries, p95 flush 110.61 ms, p95 writer-lock wait 79.22 ms; 16 simultaneous threads: 512/512, 82 retries, p95 flush 371.19 ms, p95 writer-lock wait 314.04 ms; 4 independent processes: 128/128, 2 retries, p95 flush 84.23 ms, integrity ok. All synthetic flushes succeeded and integrity was ok. The 16-thread case still shows material lock contention; jitter improved the exact benchmark compared with the immediately preceding run's 187 retries / 627.74 ms p95 flush, but the runs are CI-runner-specific and not a controlled performance comparison or production SLO.
- Metrics artifact records synthetic operational counters only, not market data. It explicitly excludes production persistent-volume and multi-host claims. Do not infer production capacity or supported worker count from it.
- Trivy artifact [14739587046](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696/artifacts/14739587046) was inspected. Image dezzta-chart-backend:ci, Alpine 3.24.4, linux/amd64, digest sha256:274264c0115b75b9c538a9c383140f393c9c8545eb73b4b1d48269384ab240ff, size 571,353,088 bytes. The report lists zero vulnerabilities and zero misconfigurations in the scanned Alpine OS and Python package result groups. This is point-in-time scanner evidence for this exact amd64 image/database only; it is not an ongoing guarantee or ARM64 evidence.
- Synthetic outbox artifact [14739104428](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696/artifacts/14739104428) was generated by CI but is not used here to make additional performance claims.

### Source change and scope boundary
Commit 332fd0dacdcd383a27744ea4b9f76d7cbe418cdc changes exactly backend/app/metrics_collector.py and backend/tests/test_metrics_collector.py. It raises bounded BEGIN-lock retry attempts to 16 and adds randomized backoff to desynchronize concurrent SQLite writers. The exact-head backend tests and synthetic benchmark passed. This is a metrics-collector resilience change only: no WebSocket transport, Firebase authentication, ticket, Redis market-data publisher/consumer, snapshot/replay, cursor, browser client, Android client, indicator formula, hook, renderer or indicator test was changed.

### WebSocket acceptance — repository evidence versus production evidence
- The source publisher and gateway replica runtime factories remain separate injected ASGI roles. The source publisher checkpoint/outbox and gateway replica consumer remain repository-side components; the gateway worker uses an ownership lease, sequential consumption, bounded retry on callback errors, and terminal resnapshot-required/ownership-lost states.
- The gateway snapshot installer is an owner-supplied authenticated transfer callback. The code validates installed metadata against its durable local checkpoint before Redis consumer construction; this does not independently authenticate remote snapshot bytes or receipts. The source activation verifier similarly remains an owner-supplied trust boundary.
- WebSocket tickets are short-lived (90 seconds) and single-use in the reviewed ticket path. Firebase ID-token exchange is over HTTPS; the Firebase token is not placed in a WSS URL or raw authentication frame. The ticket currently binds account subject and purpose; canonical series and Origin are not embedded in the ticket itself. Series authorization is performed separately. Retain series/Origin binding as an explicit threat-model and owner-review item before production exposure, not as a claim that this commit fixed it.
- Production gates remain unclosed: owner-host secret injection/rotation and redaction; real Firebase project token and entitlement E2E; owner-host Redis TLS/CA/hostname/ACL/persistence/failover and authenticated snapshot installation receipts; live database backup/restore; encrypted off-host backup/key custody; persistent volume ownership/restart/disk-pressure; verified public hostname/TLS; public HTTPS ticket exchange and WSS reverse proxy with real browser and Android WebView lifecycle/replay/resnapshot/duplicate-suppression evidence; real dashboards/retention/alerts and human acknowledgement.
- **Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional.** CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. No stage transition is authorized.

### Indicator progress reconciliation — no credit
No indicator source or tests changed in this commit. Keep the canonical matrix unchanged:
- SMA20 — 🟨 foundation; 20-close mean, first valid index 19.
- EMA20 — 🟨 foundation; SMA-seeded EMA, alpha 2/21, first valid index 19.
- RSI14 Wilder — 🟨 foundation; 14 close changes, first valid index 14.
- MACD12/26/9 — 🟨 foundation; MACD first valid index 25; signal/histogram index 33.
- Bollinger20,2 — 🟨 foundation; 20-close mean ±2 population standard deviations, first valid index 19.
- Shared Indicator Hook — 🟨 foundation; validated backend snapshot and candle-index-aligned calculation output, not chart-integrated.
- Footprint — 🟧 synthetic educational accumulator only; visual work remains blocked on user reference image(s) and reviewed blueprint.
- Heatmap — 🟥 not implemented.
- Liquidation Maps — 🟥 not implemented.

Warm-up values remain null, never zero; outputs align to source candle indices; no future-candle repaint; identity/timeframe changes clear stale series. Footprint OFF must preserve standard candlestick spacing; only explicit ON uses spaced cluster layout. No aggregate indicator percentage without approved weights and denominator. CI, benchmarks and documentation award zero indicator implementation progress.

### Cost and change boundary
ZERO COST maintained: no paid service, hosting, deployment, domain, cloud resource, account, production credential, device/Termux operation or external endpoint was created. No main-branch change. This batch is documentation-only after the already-tested source commit.

**Next safe sequence:** preserve this green exact-head CI; continue the read-only WebSocket owner-evidence audit and ARM64 build feasibility review without provisioning; keep all owner-host production gates open until real evidence and authorized adult account-owner review exist. Do not respond to remaining SQLite contention by blindly increasing retry limits; a single-writer/queue design would require a separate scoped architecture decision and measured acceptance criteria.

---

# Current project and indicator progress — Batch 62J-123

## Batch 62J-122 — exact-head WebSocket CI, artifact and runtime-boundary audit (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Audited exact HEAD:** 4c3e9f9f4cd8317c5cd03357b51aae06d289a804  
**Automated Tests [run 44984396895](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895): SUCCESS**; **CodeQL [run 44984396918](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396918): SUCCESS**; **Full Git History Secret Audit [run 44984396926](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396926): SUCCESS**. All three runs target the exact audited HEAD.

### CI evidence and limitations
- Frontend: 29 Vitest files, 255 tests passed.
- Backend: 1,294 passed, 1 skipped. The skipped test was the real Redis TLS/shared-guard integration test because REDIS_TEST_URL was not configured. The workflow's separate container smoke did exercise a CI Redis instance; this does not turn the skipped integration case into a pass.
- Container smoke passed: health endpoint, Redis ACL authentication, AOF data surviving Redis restart, fail-closed API behavior during Redis outage, backend reconnection, non-root UID/GID 10001, mounted-volume ownership, SQLite integrity and restart persistence, and HTTP rate-limit rejection.
- Trivy report artifact [14739352623](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14739352623) was independently inspected. Exact image dezzta-chart-backend:ci, Alpine 3.24.4, linux/amd64, image digest sha256:28fc78838f596968e3825ac2f46ffd3a1c7b688e029c62b53fcad2cd8bc09f85, reported **0 vulnerabilities** in Alpine OS and Python package result groups. Image size: 571,350,016 bytes (~571 MB). This is point-in-time scanner output for this exact amd64 image and database, not a permanent guarantee and not ARM64 evidence.
- Synthetic outbox artifact [14738863888](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14738863888): 1,000 synthetic bars/events; persist p95 2.655 ms; concurrent replay-page p95 1.305 ms with two reader threads. Local single-process SQLite microbenchmark only, not a real provider or WebSocket load/SLO test.
- Synthetic metrics collector artifact [14739436712](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14739436712): 899 logical series; one thread 32/32 flushes, 0 retries, p95 flush 8.10 ms; four threads 128/128, 2 retries, p95 flush 112.97 ms and writer-lock p95 105.38 ms; 16 threads 512/512, 65 retries, p95 flush 350.53 ms and writer-lock p95 315.97 ms; four independent processes 128/128, 1 retry, p95 flush 60.23 ms; staggered 16-worker case 512/512, 0 retries. SQLite integrity was ok in all reported cases. This demonstrates contention in concurrent same-host SQLite workloads, but is not a production host or multi-host benchmark. Do not infer multi-worker capacity or SLO from it.

### WebSocket runtime boundary audit
- Source and gateway runtime factories remain explicitly injected into separate ASGI app roles. The app rejects simultaneously injecting both roles into one instance.
- Production settings require Redis TLS URL and Firebase project ID; the shared guard is mandatory in production. The non-production in-memory ticket store is not production acceptance.
- Source publisher activation requires a host-supplied snapshot verifier callback. Its evidence must bind source ID, stream key, generation, cursor, SHA-256 and one matching installation receipt per required gateway. The callback remains a trust boundary: the owner must independently verify snapshot bytes and authenticate each receipt; repository shape validation cannot probe remote gateways.
- Gateway activation requires an owner-supplied snapshot installer and validates its returned metadata against the durable local replica checkpoint before creating the Redis client/consumer. This does not independently establish remote source authenticity; owner transport and evidence custody remain external.
- Replica worker obtains a generation-scoped lease before group access, ensures group readiness before serving, and runs one sequential consumer per replica identity. Existing lease and consumer code fail closed on unverifiable/lost ownership, apply-before-ACK, reclaim pending messages, and require resnapshot on history gaps.
- No source change was made in this batch. These are source-review findings, not new runtime acceptance tests.

### Production disposition
Public hostname/TLS/reverse proxy, real Firebase signed-token and entitlement E2E, owner-host Redis ACL/secret rotation/persistence/failover, authenticated global snapshot receipts, public browser WSS and Android WebView lifecycle evidence remain absent. Gate 10 remains **0/10 formally closed**; Stage 1 remains **30/40 = 75% provisional**. CI container Redis and ephemeral volume evidence does not close owner-host gates.

### Indicator ledger reconciliation
Compare from indicator implementation baseline 0074f1d0b0e421f32800294742f92d9bc9c8a2c6 through 4c3e9f9f4cd8317c5cd03357b51aae06d289a804 contains documentation paths only; no indicator calculation, hook, renderer, UI, formula or indicator test implementation changed. Therefore this batch awards **zero indicator implementation progress**. Keep SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook at 🟨 foundation; Footprint 🟧 simulated/reference-gated; Heatmap and Liquidation Maps 🟥 not implemented. No aggregate percentage without approved weights/denominator. Footprint/Heatmap visual work remains blocked on user references and reviewed blueprint; Footprint OFF preserves ordinary candle spacing.

### Cost and change boundary
Documentation-only update. No deployment, host, resource, provider, paid service, account or credential was created or used. No main-branch changes, no device/Termux work, and no runtime or test files modified. ZERO COST maintained.

**Next safe sequence:** finish exact-head evidence review; design a zero-cost ARM64 build/smoke verification separately from amd64; retain the SQLite concurrency warning; and keep production gates open until owner-controlled evidence exists.
---
## Batch 62J-121 — exact-head WebSocket CI completion and indicator reconciliation (22 November 2026)

**Verified branch:** `phase-2/market-data-foundation`  
**Exact tested HEAD before this documentation update:** `524e78ff032f759d4475f3d396a58aa60f17b40b`  
**Exact-head CI:** Automated Tests [run 44983903576](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576) — **SUCCESS** (Test and Build job and all reported steps completed successfully); CodeQL [run 44983903708](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903708) — **SUCCESS**; Full Git History Secret Audit [run 44983903634](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903634) — **SUCCESS**.

The Automated Tests job completed frontend dependency audit, frontend unit tests and build, production bundle secret scans, Android preview-host preflight, backend dependency audit and tests, isolated Redis TLS CA/hostname enforcement fixture, synthetic SQLite outbox and metrics collector benchmarks, backend container build, container smoke with shared Redis guard and persistent CI volume, Trivy scan/report export and upload, and final dependency-audit enforcement. Artifacts produced by this exact run: synthetic outbox benchmark [14739336684](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14739336684), synthetic metrics collector benchmark [14738972814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738972814), and container vulnerability report [14738408566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738408566). The report was generated and uploaded; this note does not claim a zero-vulnerability result because the current artifact contents were not independently inspected in this batch.

**WebSocket source/test review:** the source-side publisher, per-gateway Redis Stream consumer, durable replica apply-before-ACK flow, snapshot/replay recovery and scoped single-use ticket/client transport remain present at the audited source baseline. The consumer design uses independent groups per gateway, pending-message reclaim, idempotent replica application and explicit resnapshot on stream-history gaps. The client rejects production non-HTTPS base URLs, uses WSS, exchanges Firebase credentials over HTTPS for a short-lived ticket, and validates snapshot watermarks and stream sequence. These are repository implementation facts; CI confirms covered automated paths, not production service behavior.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS hostname/certificate/reverse-proxy route; no real Firebase project token, revocation and entitlement evidence; no owner-host Redis TLS/ACL/rotation/persistence/failover evidence; no independently verified global snapshot digest and per-gateway installation receipts; and no real browser plus Android WebView lifecycle evidence. CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition is authorized.

**Indicator exact-head reconciliation:** GitHub compare from indicator implementation baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` to `524e78ff032f759d4475f3d396a58aa60f17b40b` reports six commits and only documentation paths changed (13 documentation files; no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source). Therefore this CI/documentation batch awards **zero indicator progress**. Current statuses remain: SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook — 🟨 foundation; Footprint — 🟧 simulated/reference-gated; Heatmap and Liquidation Maps — 🟥 not implemented. Keep the formula/warm-up definitions, candle identity and alignment rules, stale-series clearing, renderer/UI acceptance, and Footprint OFF standard-candle-spacing invariant unchanged. Footprint and Heatmap visual work remains blocked until user-provided reference images and a reviewed blueprint exist. No aggregate indicator percentage is assigned without an approved denominator and weights.

**ZERO COST and scope:** documentation-only reconciliation. No runtime source, tests, workflows, formulas, renderer, UI or deployment configuration changed. No host, account, resource, endpoint or paid service was created; no credentials were requested; no device/Termux work occurred; `main` was not touched. No trial-credit or paid-service dependency is introduced.

**Next sequence:** (1) preserve the green exact-head CI; (2) keep Gate 8/20/25/30/31/34/35/36/38/39 open until the listed owner-host/operator evidence is supplied; (3) pursue only zero-cost, non-provisioning checks until adult account-owner review and explicit authorization exist; (4) continue indicator implementation only within its existing approved scope and reference gates. Do not count CI, documentation or synthetic benchmarks as production acceptance.

---

## Batch 62J-120 — exact-head CI and artifact inspection (22 November 2026)

**Tested HEAD:** `c6cd331c5f9293093418bda31f93960f5aed1600`. Automated Tests #1954, CodeQL and Full Git History Secret Audit all completed SUCCESS. The Trivy JSON artifact was inspected: zero reported vulnerabilities in the scanned Alpine OS and Python package groups for the `linux/amd64` CI image. Synthetic outbox replay passed; the 899-series metrics collector benchmark exposed increasing SQLite writer-lock retries under higher concurrency. These are CI-only measurements, not production SLOs. ARM64 remains unverified; public WSS, production Redis/Firebase and browser/Android E2E remain open. No indicator source or test changed; indicator statuses and Stage 1 accounting remain unchanged. Full evidence and limitations: [Batch 62J-120](WORK_CYCLE_2026-11-22_BATCH62J120_EXACT_HEAD_CI_ARTIFACT_AND_ACCEPTANCE_AUDIT.md).

## Batch 62J-119 — WebSocket acceptance and indicator ledger exact-head reconciliation (22 November 2026)

**Verified parent HEAD:** `6d5a05d611615972d5826002442a65e74c179750` on `phase-2/market-data-foundation`. This checkpoint was created only after all three workflows for that exact SHA completed successfully.

**Exact-head CI:**
- Automated Tests #1954 — [run 44982930281](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281): **SUCCESS**. Frontend unit tests/build, backend tests, isolated Redis TLS/CA/hostname enforcement fixture, synthetic SQLite outbox and metrics benchmarks, backend container build, container smoke test using shared Redis guard and persistent volume, Trivy image scan/report export/upload, and dependency-audit enforcement all completed successfully.
- CodeQL [run 44982930379](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930379): **SUCCESS**.
- Full Git History Secret Audit [run 44982930324](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930324): **SUCCESS**.
- Trivy report artifact: [container-vulnerability-reports](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281/artifacts/14739265202). The workflow completed the configured HIGH/CRITICAL scan and uploaded the JSON report. Do not infer a zero-vulnerability result without reviewing the artifact contents.

These results verify the repository workflow and its CI service topology only. The CI Redis instance, ephemeral runner volume, and container smoke are not the intended OCI host or production Redis service.

**WebSocket repository evidence:** source-side publisher and gateway runtime factories, durable SQLite outbox, atomic snapshot/watermark primitives, Redis Streams publisher/consumer, per-gateway consumer groups, replica snapshot installation checks, fail-closed runtime construction, ticket authentication/renewal, reconnect/replay and client failure-matrix tests are present in the audited source. The latest CI validates the covered repository paths. The default FastAPI app intentionally does not invent owner-specific publisher/replica factories or trust snapshot receipts; those must be injected from a verified owner-controlled host setup.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS endpoint, production Firebase token/entitlement evidence, owner-host Redis TLS/ACL/persistence/rotation/failover, authenticated global snapshot manifest and per-gateway installation receipts, or real browser + Android WebView lifecycle evidence has been supplied. A successful CI container smoke cannot close those host/client gates.

**ZERO COST boundary:** no OCI account or resource was created, no deployment or public endpoint was started, no paid resource or trial-credit dependency was introduced, no credentials were requested, no device/Termux operation occurred, and `main` was not touched. OCI remains a conditional candidate subject to actual Always Free eligibility and adult account-owner approval.

**Indicator disposition — no source change and no progress credit:** the source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains the calculation baseline. The comparison through parent HEAD `6d5a05d611615972d5826002442a65e74c179750` is documentation-only; no indicator formula, hook, chart renderer, UI, or indicator test source changed. SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps remain 🟥 not implemented. Formula definitions, warm-up indices, numerical safeguards, data identity, stale-series invariants, UI acceptance and reference prerequisites remain in the canonical audit and ledger. Aggregate indicator percentage remains unscored without approved weights and denominator.

**Project accounting:** Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI or documentation-only checkpoint. No progress is awarded from CI alone.

**Next zero-cost sequence:** preserve the green exact-head CI; finish ARM64 build/configuration readiness without provisioning; have the adult account owner verify OCI eligibility, capacity and all possible charges; only then, with explicit authorization, consider an Always Free-only host. Collect actual host and client evidence for Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Close Gate 10 only after evidence review and operator sign-off.

---

## Batch 62J-117 — exact-head WebSocket CI and indicator progress reconciliation (22 November 2026)

## Batch 62J-117 — exact-head CI and indicator ledger reconciliation (22 November 2026)

**Verified branch HEAD:** `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02` (`phase-2/market-data-foundation`). The source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains valid: GitHub comparison from that baseline to this HEAD contains documentation-only changes, with no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source changes.

**Exact-head workflows on `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02`:**
- Automated Tests [run #1952 / 44981803844](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803844): **SUCCESS**; all 61 reported workflow steps completed successfully, including frontend tests/build, backend tests, Redis TLS CA/hostname fixture, backend container build, persistent-volume Redis smoke test, image scan/report and dependency audits.
- CodeQL [44981803808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803808): **SUCCESS**.
- Full Git History Secret Audit [44981803851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803851): **SUCCESS**.
- These are exact-head repository CI/security results. They do not constitute production Firebase, owner-host Redis, public WSS, browser or Android WebView acceptance.

**Indicator disposition — unchanged, zero progress credit:** SMA20 🟨, EMA20 🟨, RSI14 Wilder 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧 (synthetic/reference-gated), Heatmap 🟥, Liquidation Maps 🟥. The five calculation foundations and their first-valid indices remain as recorded in the canonical audit; none is accepted as a finished visible chart feature. The chart integration, controls, legends/current values, pane/overlay rendering, stale-series clearing and lifecycle/render acceptance remain outstanding as listed per study. Footprint OFF must preserve ordinary candle spacing; only explicit ON may switch to spaced clusters. Footprint, Heatmap and Liquidation Maps visual work remains gated by user-provided reference image(s) and reviewed blueprint.

**Accounting:** no indicator or project completion credit is awarded by WebSocket CI or this documentation reconciliation. Aggregate indicator percentage remains unscored without approved weights and denominator. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed. Gates 20, 25 and 36 remain open for real Firebase/entitlement evidence, owner-host Redis TLS/ACL/persistence/recovery and public HTTPS/WSS proxy plus browser/Android acceptance. No deployment or production readiness is claimed.

**Cost/scope:** ZERO COST. No paid hosting/provider, OCI provisioning, credentials, deployment, Termux/device action or `main` modification.

Full source-backed formula, numerical-safety, data-lineage and UI acceptance matrix: [INDICATOR_PROGRESS_AUDIT_2026-11-22.md](INDICATOR_PROGRESS_AUDIT_2026-11-22.md). WebSocket production blockers and evidence matrix: [WORK_CYCLE_2026-11-22_BATCH62J117_EXACT_HEAD_WEBSOCKET_AND_INDICATOR_RECONCILIATION.md](WORK_CYCLE_2026-11-22_BATCH62J117_EXACT_HEAD_WEBSOCKET_AND_INDICATOR_RECONCILIATION.md).

---

## Batch 62J-115 — complete source-backed indicator progress audit (22 November 2026)

- Audited baseline: `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` on `phase-2/market-data-foundation`.
- Added `docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md` as the canonical detailed audit; refreshed the current checkpoint in `docs/INDICATOR_PROGRESS_LEDGER.md` and this current project-progress file.
- Verified: SMA20, EMA20, Wilder RSI14, MACD12/26/9 and Bollinger20,2 have tested calculation foundations; none is a completed visible chart feature. The shared backend-only hook exists but is not wired into `CandlestickChart.tsx`. The chart still creates only one candlestick series.
- Calculation suite contains 15 cases. Baseline frontend CI passed 255/255 tests across 29 files; backend passed 1,294 with 1 skipped. Automated Tests, CodeQL and Full Git History Secret Audit passed on baseline.
- Footprint remains a synthetic offline educational accumulator; no real order-flow source or visual cluster renderer. Heatmap and Liquidation Maps are not implemented.
- Documented formula definitions, first-valid indices, numerical safety, exact data identity, stale-series rules, prefix-causality, proposed overlay/pane scope, UI acceptance, reference prerequisites and roadmap gates.
- No formula, hook, chart, visual UI, runtime or test source changed. **No indicator progress credit.**
- Official project remains Stage 1, 30/40 = 75% provisional. Stage 4 visual implementation is not authorized during Stage 1. Aggregate indicator percentage remains unscored without approved weights/denominator.
- ZERO COST; no deployment, paid service, production credential, Termux/device action or `main` modification.
- Exact-head CI for this documentation commit must be checked before declaring this docs batch CI-accepted.

Full detail: [INDICATOR_PROGRESS_AUDIT_2026-11-22.md](INDICATOR_PROGRESS_AUDIT_2026-11-22.md).

---

## Batch 62J-104 — five remaining Gate 10 tracks and exact-head CI acceptance (22 November 2026)

- Audited source/test HEAD: `a18e963d4cd067fe22ec8d03c653418e003c7fde`.
- Exact-head Automated Tests [44970436441](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436441): **SUCCESS**; frontend 255/255 across 29 files; backend **1,289 passed in 51.98 s**. The five new Batch 62J-103 tests are individually visible as PASSED in the workflow log.
- Exact-head CodeQL [44970436417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436417): **SUCCESS** (Python + JavaScript/TypeScript). Full Git History Secret Audit [44970436377](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436377): **SUCCESS**.
- Automated Tests also passed frontend/backend dependency audits, frontend source/bundle secret scans, backend container build, shared Redis guard/persistent-volume smoke, configured container scan and report export.
- Gate 20: repository identity/ticket/entitlement failure matrix verified; live Firebase signed-token E2E and threat-model owner review remain.
- Gate 25: Redis TLS/ACL guards, atomic ticket/lease operations, exact ticket TTL/NX/digest semantics and CI shared Redis smoke verified; owner-host Redis TLS/ACL, snapshot receipt and persistent failover remain.
- Gate 31: encrypted SQLite backup, AES-256-GCM/PBKDF2, fresh-path restore, content/schema hashes, wrong-key/tamper/truncation and full application restore drill tests verified; off-host copy, offline key custody and owner-host key-recovery restore remain.
- Gate 36: WebSocket lifecycle/auth/replay/renewal and frontend client tests verified; public HTTPS/WSS, reverse proxy, live Redis, cross-instance and browser/Android WebView acceptance remain.
- Gate 38: 899-series/900 cap, same-host SQLite collector, failure isolation and CI benchmark verified; owner-host volume/perimeter/token lifecycle/dashboard/notification/recovery drill remain. Latest synthetic 16-worker startup-staggered benchmark: 512/512 flushes, 899/899 series, 0 retries, SQLite integrity `ok`; peak DB+WAL+SHM 5,744,952 bytes; post-checkpoint 1,126,400 bytes. CI-runner only, not production SLO/host evidence.
- Gate 10 remains **0/10 formally closed**. 🟨🟩 host/operator-only: Gates 8, 30, 34, 35, 39. 🟧 integration/acceptance: Gates 20, 25, 31, 36, 38.
- Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- Indicator implementations unchanged; no indicator progress credit. Full current formulas, warm-up indices, prerequisites and remaining visible work are in `docs/INDICATOR_PROGRESS_LEDGER.md`.
- Full five-track evidence and remaining acceptance requirements: `docs/WORK_CYCLE_2026-11-22_BATCH62J104_FIVE_REMAINING_GATES_EXACT_HEAD_AUDIT.md`.
- ZERO COST. No deployment, paid service, production credential, Termux/device operation or `main` modification.

---

## Batch 62J-103 — WebSocket ticket renewal failure matrix (22 November 2026)

- Active branch: `phase-2/market-data-foundation`; final source/test HEAD: `a18e963d4cd067fe22ec8d03c653418e003c7fde`.
- Test-only change set relative to checkpoint `d45290b8b95e5bbe73e2a993cd3fdaf497a8afc3`: `backend/tests/test_api.py` +86 lines; `backend/tests/test_shared_guard.py` +47 lines; zero deletions in the final diff. Total +133 lines.
- Two new FastAPI/WebSocket renewal tests: invalid/expired renewal ticket closes 4401; ticket-store/Redis outage during renewal closes 1013 without exposing internal error or credential text.
- Three new shared-guard ticket tests: SHA-256 digest-only key with exact 90-second TTL and NX write; corrupt stored JSON is consumed and rejected; two concurrent in-memory consumers yield exactly one subject and one `None`.
- Existing real-Redis single-use integration test now checks `PTTL`: remaining ticket TTL must be positive and no greater than 90,000 ms. Existing tests already covered cross-subject renewal rejection and entitlement revocation during renewal; duplicate candidate tests were removed rather than duplicating coverage.
- No production source, WebSocket protocol, Firebase identity, Redis runtime or market-data code changed.
- **CI acceptance was subsequently verified for this exact source/test HEAD** by Batch 62J-104: Automated Tests [44970436441](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436441) SUCCESS (frontend 255/255; backend 1,289 passed), CodeQL [44970436417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436417) SUCCESS, and Full Git History Secret Audit [44970436377](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436377) SUCCESS. All five new tests were individually PASSED.
- Gate 20 repository evidence improved (renewal invalid-ticket and store-outage handling); Gate 25 improved (ticket TTL, digest key, NX and corrupt-payload behavior); Gate 36 improved (renewal transport failure closure). No gate is closed.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/operator-only: Gates 8, 30, 34, 35, 39. 🟧 integration/acceptance: Gates 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- No indicator formula, calculation, data contract, shared hook, renderer, chart UI or indicator test changed. No indicator progress credit is awarded; see the full matrix in `docs/INDICATOR_PROGRESS_LEDGER.md`.
- ZERO COST: no deployment, Vercel/Cloudflare operation, paid provider, production credential, Termux/device operation or `main` modification.

---

## Batch 62J-98 — WebSocket + Gate 25 gateway runtime + Gate 38 + Gate 36 (21 November 2026)

- Verified source/test HEAD: `b4325216d1293d3c747978fc45218bfe1fd1d79f` on `phase-2/market-data-foundation`.
- Added `backend/app/ohlcv_redis_gateway_runtime.py`, six regression tests in `backend/tests/test_ohlcv_redis_gateway_runtime.py`, and gateway env placeholders in `backend/.env.example`.
- Gateway builder validates authenticated installer result, durable replica checkpoint, source ID, snapshot generation, high-water cursor and SHA-256 before Redis client creation. Production requires rediss TLS certificate and hostname verification. Runtime is opt-in and requires an owner-supplied authenticated snapshot installer.
- Exact-head Automated Tests [44916614912](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912): SUCCESS; 255 frontend tests across 29 files, 1,277 backend tests in 42.72s. Container build, Redis ACL/AOF persistent-volume smoke, frontend build/secret scans and dependency audits succeeded.
- Exact-head CodeQL [44916614959](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614959): SUCCESS. Full Git History Secret Audit [44916614967](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614967): SUCCESS.
- Trivy artifact [14711468367](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912) was downloaded and parsed: 0 HIGH/CRITICAL vulnerabilities in Alpine OS and Python package targets.
- Gate 38 artifact [14712222307](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912): 899/899 series, 512/512 staggered flushes, 16/16 workers, SQLite integrity ok, 0 retries. Staggered p95 18.34ms / p99 88.57ms / max 259.74ms. Simultaneous 16-thread p95 376.08ms / p99 796.15ms / max 1,406.30ms / 78 retries. Synthetic staggered reductions: p95 95.12%, p99 88.88%, max 81.53%. CI model only, not production SLO.
- Four-process benchmark: 128/128 flushes, 899 series, integrity ok, one retry; p95 40.43ms, p99 239.10ms. Cross-host SQLite is not claimed.
- WebSocket source/consumer failure-matrix scope remains complete for repository CI. Production WSS still requires owner-host Redis TLS/ACL, snapshot receipts, public HTTPS/WSS reverse proxy and browser/Android WebView acceptance.
- Gate 25 source-side gateway runtime readiness improved; Gate 25 remains 🟧 pending live Redis, host credentials, ACL/network, persistence/failover and authenticated snapshot distribution. Gate 36 remains 🟧 pending public HTTPS/WSS and device acceptance. Gate 38 remains 🟧 pending central monitoring, host volume, retention/backup and operator recovery.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/operator only: Gates 8, 30, 34, 35, 39. 🟧 integration/acceptance: Gates 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored.
- Indicators unchanged; no credit: SMA20 🟨 (index 19), EMA20 🟨 (index 19), RSI14 🟨 (index 14), MACD12/26/9 🟨 (MACD index 25, signal/histogram 33), Bollinger20,2 🟨 (index 19), Shared Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
- Initial candidate `7bf14593ddfa5d776245bb632896a8277635f9e0` had a syntax error caught by CI; it was corrected in `b4325216d1293d3c747978fc45218bfe1fd1d79f`. The final exact-head workflow passed.
- ZERO COST. No deployment, paid service, production credentials, Vercel/Cloudflare operation, Termux/device operation or `main` modification.

---

## Batch 62J-97 — production-staggered metrics benchmark (21 November 2026)

- Source/test HEAD: `8deeba557f7be6ea5cb66fb0bfb55955aafc5a41` on `phase-2/market-data-foundation`; docs-only descendants now carry the ledger update.
- Exact-head Automated Tests [44914991306](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991306): **SUCCESS**. CodeQL [44914991295](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991295): **SUCCESS**. Full Git History Secret Audit [44914991439](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991439): **SUCCESS**.
- Trivy artifact [14710634254](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991306) was downloaded and parsed: **0 vulnerabilities** in Alpine OS and Python package targets, including zero HIGH/CRITICAL.
- The benchmark mirrors production's UUID-prefix modulo-15 startup phase and 15-second flush cadence. Staggered 16-thread profile: **512/512 flushes**, **899/899 series**, 16/16 workers, SQLite integrity `ok`, **0 retries**, p95 **19.98 ms**, p99 **86.72 ms**, max **120.73 ms**.
- Simultaneous 16-thread stress: 512/512 flushes, p95 371.91 ms, p99 610.31 ms, max 1,922.15 ms, 68 retries. Staggered profile reduced p95 94.63%, p99 85.79%, max 93.72% in this synthetic CI comparison. Tail latency is not eliminated; the staggered p99 remains 86.72 ms.
- Separate four-process profile: 128/128 flushes, 899 series, integrity `ok`, p95 85.67 ms, p99 237.86 ms, one retry. Cross-host SQLite is not claimed.
- Staggered peak DB+WAL+SHM was 3,169,952 bytes; post-checkpoint total 1,126,400 bytes. Snapshot payload 105,586/262,144 bytes (40.28%). CI-runner measurements are not production capacity/SLO guarantees.
- Gate 38 remains 🟧 OPEN pending owner-host volume/retention/backup, access control, dashboard visibility and recovery acceptance.
- WebSocket repository-side automated protocol/failure-matrix scope remains complete; production WSS remains host-gated. No WebSocket protocol/relay/auth/replay code changed in this batch.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/operator verification only: Gates 8, 30, 34, 35, 39. 🟧 additional integration: Gates 20, 25, 31, 36, 38.
- Indicators unchanged; no progress credit. SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6, overall project percentage and aggregate indicator percentage remain unscored.
- ZERO COST; no deployment, Vercel/Cloudflare operation, paid service, production credentials, Termux/device operation or `main` modification.

---

## Batch 62J-87 — bounded SQLite writer-lock acquisition (21 November 2026)

- Exact source/test predecessor `73a19e5db54b44d1d07caa038ec567d31d19a0a8`: Automated Tests [44902861326](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902861326) **FAILED** at the 16-worker benchmark during `BEGIN IMMEDIATE` with `sqlite3.OperationalError: database is locked`. This was a writer-transaction contention failure, distinct from the earlier schema-bootstrap collision. CodeQL [44902861325](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902861325) and Full Git History Secret Audit [44902861332](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902861332) passed on that predecessor.
- Added bounded retry/backoff around SQLite writer-lock acquisition before transaction work. It retries only lock errors, for at most eight attempts, retaining the existing 250 ms busy timeout. Corruption, integrity errors and other non-lock failures are not suppressed. The transaction body remains atomic.
- `flush()` now reports the number of internal lock retries; benchmark aggregates those retries into its evidence output.
- Added a regression test that holds a write lock, releases it after 350 ms, verifies the flush succeeds, verifies at least one retry was recorded, and confirms the counter delta was applied once.
- Source/test commit: `c95a9a19091a5881136144491937073ba7fcb767`. Documentation commit follows; exact-head Automated Tests, CodeQL and secret-history audit are pending. No pass is claimed yet.
- The benchmark remains 899 logical series, 1/4/16 concurrent Python worker threads, 32 flushes per worker, and 256 KiB payload cap. Separate OS-process contention remains untested.
- Gate 38 remains 🟧 OPEN. Disk-full/read-only failure behavior, app-level HTTP/WebSocket isolation, retention/backup and owner-host/operator acceptance remain.
- WebSocket wire protocol, auth, replay, snapshot and Redis data path unchanged; production WSS remains host-gated.
- Indicator formula/hook/renderer/UI unchanged; no indicator progress credit. Gate 10 remains 0/10 formally closed; Stage 1 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST. No deployment, Vercel/Cloudflare operation, paid service, production credential, Termux/device operation or `main` modification.

---

## Batch 62J-86 — SQLite schema-bootstrap contention hardening (21 November 2026)

- Prior full-cardinality attempt at exact HEAD `c2f9b99fc05dd17050674a39317bd5aa601e6182`: Automated Tests run [44902446746](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902446746) **FAILED** in the metrics benchmark because concurrent worker connections collided during repeated SQLite schema initialization (`database is locked`). This failure is retained as evidence; it is not reported as a pass.
- CodeQL [44902446747](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902446747) and Full Git History Secret Audit [44902446769](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902446769) completed SUCCESS on that prior exact head.
- Hardened `SQLiteMetricsCollector._connect()`: schema initialization now runs once per collector instance behind a thread lock, and transient SQLite lock errors during initialization receive bounded retry/backoff. Non-lock errors and corruption still fail closed. Subsequent connections no longer repeat the DDL script.
- Changed the 1/4/16-thread benchmark so each simulated worker owns its own collector instance against the shared SQLite file, matching the per-process collector lifecycle more closely.
- Added a regression test in which four independent collector instances initialize and write to the same database concurrently; the test verifies all worker deltas aggregate without loss.
- Current source/test HEAD: `2c584fcef5a20b21ec2850692ab51e28341c4eff`. Exact-head Automated Tests, CodeQL and secret-history audit are pending; no pass is claimed yet.
- The 899-series target, 256 KiB payload limit, 250 ms SQLite busy timeout, 650,000 aggregate-row ceiling and zero-cost scope are unchanged. The full-cardinality benchmark is not considered accepted until the new exact-head run passes.
- Gate 38 remains 🟧 OPEN. Separate OS-process benchmark, physical read-only/disk-full behavior, app-level HTTP/WebSocket isolation and owner-host acceptance remain.
- WebSocket protocol/auth/replay/snapshot/Redis code remains unchanged. Production WSS acceptance remains host-gated.
- Indicator calculations and renderers remain unchanged; no indicator credit. Gate 10 remains 0/10 formally closed; Stage 1 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST. No deployment, Vercel/Cloudflare operation, paid service, production credential, Termux/device operation or `main` modification.

---

## Batch 62J-85 — full-cardinality Gate 38 benchmark (21 November 2026)

- Source/test HEAD: `de104f388a4dd5c214567e911933d4c341bff570` on `phase-2/market-data-foundation`; exact-head CI is pending and is not claimed as passing.
- Replaced the previous 12-logical-series fixture with 899: 127 routes × 6 HTTP status classes = 762 request series; 127 latency histograms; 10 WebSocket counters/classes.
- Benchmark still covers 1/4/16 concurrent Python threads. It now verifies the full 899-series aggregate, exact worker/request totals, serialized payload size against 256 KiB, and SQLite integrity.
- Added a SQLite write-rejection rollback/retry regression. This is a transaction failure simulation, not a physical disk-full or read-only-volume test.
- Capacity arithmetic: 899 × 672 fifteen-minute buckets = 604,128 aggregate rows; 650,000-row cap leaves 45,872 rows (7.06% of cap). This excludes worker/checkpoint rows and SQLite/WAL/index/filesystem overhead; it is not a byte budget.
- Separate-process contention, read-only/disk-full, app-level traffic-isolation and owner-host acceptance remain open. Gate 38 remains 🟧.
- WebSocket wire protocol, authentication, replay, snapshot and Redis behavior unchanged. Production WSS host acceptance remains open.
- Indicators unchanged; no progress credit. Gate 10 remains 0/10 formally closed; Stage 1 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST; no deployment, paid service, production credentials, Termux/device operation or `main` modification.

---

## Batch 62J-84 — Gate 38 failure-path tests and SQLite worker benchmark (21 November 2026)

- Source/test HEAD: `92119a8dc05690e6492aab160662c9e36c839cad` on `phase-2/market-data-foundation`; `main` untouched.
- Exact-head Automated Tests [44900892637](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892637): **SUCCESS, 35/35 workflow steps**. Backend pytest: **1,265 passed in 36.46s**. The workflow also completed frontend tests/build, backend dependency audit, container build, Redis ACL/persistent-volume smoke, Trivy scan and report upload.
- Exact-head CodeQL [44900892567](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892567): **SUCCESS**. Full Git History Secret Audit [44900892606](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892606): **SUCCESS**.
- Added collector regression tests for concurrent worker commits, bounded recovery after SQLite lock contention, and safe rejection of a corrupt metrics database. Existing transaction rollback, idempotence, stale-worker, retention, generation/tombstone and monotonic timestamp tests remain.
- Added `backend/scripts/benchmark_metrics_collector.py`, a local-only synthetic 1/4/16-worker thread benchmark, plus a CI artifact. At 32 flushes per worker, observed p99 flush latency was 2.145ms / 19.108ms / 78.978ms; no retries occurred. Peak total DB+WAL+SHM bytes were 81,920 / 1,293,232 / 4,284,304.
- **Benchmark boundary:** this initial profile has only 12 logical series, not the collector's 899-series full budget; worker concurrency is Python threads, not separate OS processes. It is a baseline only, not a maximum-cardinality capacity test, a production-host estimate or a justified byte ceiling. No database byte limit is set from it.
- Gate 38 remains 🟧 OPEN. Exact-head repository CI is verified; full-cardinality benchmark, disk-full/read-only isolation, owner-host persistence/restore/retention, operator access and recovery acceptance remain.
- WebSocket protocol, authentication, replay, snapshot ordering, Redis guard and market-data payloads were not modified.
- Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**; Stages 2–6 and overall percentage remain unscored.
- Complete indicator ledger: SMA20 🟨 (20-close mean, first valid index 19); EMA20 🟨 (SMA-seeded, α=2/21, index 19); RSI14 🟨 (Wilder, index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram index 33); Bollinger20,2 🟨 (mean ±2 population SD, index 19); Shared Indicator Hook 🟨; Footprint 🟧 (reference image/approved blueprint and ON-only cluster renderer pending); Heatmap 🟥; Liquidation Maps 🟥. No indicator source or renderer changed; no indicator credit awarded.
- Invariants: warm-up `null`, candle-index alignment, no future-candle repaint, stale-series clearing on identity/timeframe changes, and Footprint OFF preserving ordinary candle spacing.
- ZERO COST: no deployment, Vercel/Cloudflare operation, paid provider, production credential request, Termux/device operation or `main` modification.

---

## Batch 62J-83 — Gate 38 collector hardening and CI baseline (21 November 2026)

- Active branch remains `phase-2/market-data-foundation`; pre-change HEAD `b1e21f552182a720400cd9a2d276705834a41358`.
- Exact-head Automated Tests run [44898947136](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44898947136) completed SUCCESS (33/33 steps); CodeQL [44898947150](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44898947150) SUCCESS; Full Git History Secret Audit [44898947186](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44898947186) SUCCESS.
- Source review found a worker-generation capacity edge case: 256 historical process checkpoints could block a replacement worker before the seven-day retention expired. The hardening change evicts only the oldest stale checkpoints under capacity pressure, records seven-day retired-worker tombstones to reject a resumed evicted process ID, and keeps active worker limits enforced.
- Snapshot reads now hide buckets outside the seven-day window even when no new flush has occurred. Aggregate-capacity evictions are counted and exposed to the protected metrics response; timestamp regressions are rejected.
- New tests cover stale-generation eviction/tombstones, the 16-live-worker limit, retention filtering without a subsequent flush, and worker timestamp regression. Exact-head CI for source commit `e98bf7acda841ae4045d258b6d3b2fe774205239` completed SUCCESS: Automated Tests [44899788672](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44899788672), CodeQL [44899788812](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44899788812), and Full Git History Secret Audit [44899788701](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44899788701).
- Gate 38 remains 🟧 OPEN: repository implementation is present, but host volume behavior, measured database byte budget, operator access/retention and incident recovery acceptance remain outstanding. No cross-host support is claimed.
- WebSocket protocol, auth, replay, snapshots and market-data payload behavior are unchanged. The collector remains best-effort telemetry and cannot delay/fail market-data request paths.
- Indicator formulas, renderers, UI and tests are unchanged; no indicator progress credit. Stage 1 remains 30/40 = 75% provisional. Gate 10 remains 0/10 formally closed.
- ZERO COST: no deploy, Vercel/Cloudflare operation, Termux, paid service, production credential request or `main` modification.

---



## Batch 62J-82 — exact-head CI reconciliation and Gate 38 capacity review (21 November 2026)

- Exact HEAD `c3577d7174ce5873502ebd8df7a57f27447a296b` has all three workflows completed SUCCESS: Automated Tests [44897164887](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44897164887), CodeQL [44897164916](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44897164916), and Full Git History Secret Audit [44897164908](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44897164908).
- Automated Tests included frontend tests/build, backend tests, SQLite outbox benchmark/report, backend dependency audit, container build, Redis persistent-volume smoke, Trivy scan and report export/upload; workflow conclusion is SUCCESS.
- Gate 38 blueprint clarified the crash-loss window (up to one nominal 15-second flush interval plus scheduler delay), fixed series budget, 672-bucket retention math, and 650,000 logical-row ceiling. The byte ceiling remains benchmark-derived, not guessed.
- Corrected interpretation: 1,500x compares periodic snapshots with a hypothetical per-request persistence design. Current metrics are in-memory and do not persist each request.
- No runtime source changed. Gate 38 remains 🟧 pending explicit blueprint approval, implementation/tests, host volume and operator acceptance. Gate 10 remains 0/10 formally closed.
- Indicator formulas, visual states and data contracts are unchanged. No indicator progress credit is awarded.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project remain unscored. ZERO COST; no deploy, paid service, Termux, production credential or `main` modification.

---
## Latest work cycle — Batch 62J-81 (21 November 2026)

- Reconciled exact branch head: 3eadda21f795abe5af195eedf0c81727d31f6436; branch compare reports identical (0 ahead / 0 behind).
- Exact-head Automated Tests run 44895224507, CodeQL run 44895224465 and Full Git History Secret Audit run 44895224498 all completed SUCCESS.
- Gate 38 architecture blueprint added: dedicated local SQLite metrics DB, worker-scoped 15-second snapshots, transactional delta checkpoints, 15-minute aggregates, 90-second live-worker expiry, and 7-day age retention plus hard capacity ceiling. Supports multiple workers on one host/local persistent volume only; no cross-host claim.
- No runtime source changed. Implementation is held behind the required blueprint review/approval gate. Existing Redis security-guard client and market-data registry DB are not repurposed for telemetry.
- Gate 38 remains 🟧 OPEN. Gate 10 remains 0/10 closed; Gate 8/30/34/35/39 remain 🟨🟩 host/owner verification only; Gate 20/25/31/36/38 remain 🟧.
- Complete indicator ledger remains unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Hook 🟨, Footprint 🟧 simulated/gated, Heatmap 🟥, Liquidation Maps 🟥. No indicator credit is awarded.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project remain unscored. ZERO COST; no deployment, paid service, Termux/device operation, production credential or main modification.

---

## Latest work cycle — Batch 62J-80 (21 November 2026)

- Corrected WebSocket lifecycle telemetry so accept/close events are counted only after downstream ASGI send succeeds.
- Added regression coverage for accept-send and close-send transport failures; the finally path must return active connections to zero and must not count unsent frames.
- This is observability correctness, not a WebSocket protocol/data-path change. Gate 38 remains 🟧 because metrics remain process-local without central aggregation, durable retention or independent operator notification.
- Indicator status is unchanged; the complete indicator ledger and formulas remain in INDICATOR_PROGRESS_LEDGER.md. No visual progress is credited.
- Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35, 39 remain 🟨🟩 host/owner verification only; Gates 20, 25, 31, 36, 38 remain 🟧.
- ZERO COST; no deploy, paid service, production credentials, Termux/device operation, Vercel/Cloudflare operation or main modification.

---

## Latest work cycle — Batch 62J-79 (21 November 2026)

- Added bounded process-local WebSocket lifecycle metrics for the exact `/ws/market-data` ASGI route: starts, active, completed, accepted, peer disconnects, five close-code classes and cumulative duration.
- The observer records lifecycle metadata only. It does not inspect payloads, auth tickets, authorization headers, account IDs, IP addresses, symbols or query strings. It is returned only through the existing bearer-token-protected `/internal/metrics` endpoint.
- New tests cover accepted/closed lifecycle, peer disconnect and route isolation. WebSocket wire protocol and data path are unchanged.
- Source/test HEAD: `2274f9adc5ac9907ea508800a2d962d9a7c14a84`. Frontend tests, backend tests and CodeQL have passed in exact-head run [44894262277](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262277) / [44894262276](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262276); full workflow still has container/build/audit steps pending. Secret-history audit [44894262301](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262301) passed. Do not claim full CI acceptance yet.
- Gate 38 improves at repository level but remains 🟧 OPEN: telemetry is process-local; central collector, multi-worker aggregation, dashboard, durable retention and independent operator notification remain absent.
- WebSocket automated protocol/failure-matrix scope remains complete for the defined CI scope. Production acceptance remains blocked by missing owner-controlled host, production Redis topology, snapshot receipts, public HTTPS/WSS and real browser/Android WebView acceptance.
- Indicator formulas and visual completion are unchanged. Full indicator status is in `INDICATOR_PROGRESS_LEDGER.md`; no renderer credit is awarded by this observability batch.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/owner verification only: Gates 8, 30, 34, 35, 39. 🟧 additional integration: Gates 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project remain unscored. ZERO COST; no deployment, Termux/device command, production credentials or `main` modification.

---

## Latest work cycle — Batch 62J-78 (21 November 2026)

- SMA numeric audit found and corrected a second-order cancellation case after Batch 62J-77: a small representable residual between `MAX_VALUE` and `-MAX_VALUE` was lost by ordinary normalized reduction.
- The feature branch now uses an error-free floating-point expansion only for materially cancelling normalized windows, preserving the fast path for ordinary price windows. SMA and Bollinger middle-band means share the stable helper; forward/reverse-order regression tests cover the residual case.
- First exact-head CI (run [44893124624](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44893124624)) caught a missing normalized vector used by the Bollinger variance pass. The vector is restored in source/test HEAD f70f0bcfe2208b4fbfb37440fe8dc3b740e8fbcc. Frontend unit tests/build, CodeQL and full Git-history secret audit have passed on that exact HEAD; backend suite and APK build are still running. This is not yet a verified release.
- No visual indicator credit is awarded: SMA20 stays 🟨 foundation; all other indicator statuses remain as shown in the full ledger below.
- WebSocket repository-side failure-matrix scope remains complete; public WSS/production acceptance remains externally blocked.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/owner verification only: 8, 30, 34, 35, 39. 🟧 additional integration: 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project remain unscored. ZERO COST; no deploy, no paid service, no Termux/device command, and `main` remains untouched.

## Latest engineering checkpoint — Batch 62J-77 (21 November 2026)

**Branch:** phase-2/market-data-foundation  
**Source/test HEAD:** e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8

- Exact-head Automated Tests [44877470829](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470829): **SUCCESS** — frontend **253/253 tests across 29 files**; backend **1,249 passed in 48.11s**. Frontend build, frontend source/bundle secret scans, npm audit (0 vulnerabilities), backend dependency audit (no known vulnerabilities), bounded outbox benchmark, backend container build, Redis shared-guard/persistent-volume smoke, Trivy container scan and report export/upload all completed.
- Exact-head CodeQL [44877470826](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470826): **SUCCESS**.
- Exact-head Full Git History Secret Audit [44877470841](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470841): **SUCCESS**.
- Exact-head Android debug APK build [44877470773](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470773): **SUCCESS**. Artifact ID 14696311954, expires 28 November 2026. APK size 3,877,454 bytes; SHA-256 cc7288ac77fa0c28f2cfeebba7f9703003f15a970b1575618e1998548887ed7a. CI build does not equal physical-device acceptance.
- Batch 62J-77 fixes SMA intermediate overflow: each rolling window uses scale-normalized mean calculation. Representable averages such as mean(MAX_VALUE, MAX_VALUE) now return MAX_VALUE instead of throwing because a raw sum overflowed. Regression coverage includes extreme same-sign values and cancellation. Calculation remains candle-index aligned and warm-up nulls unchanged.
- CI caught two issues in the first attempt: an old test still expected the prior SMA overflow failure, and a relative-large-value assertion used an absolute tolerance inappropriate at MAX_VALUE scale. Both tests were corrected; the exact final source/test commit passed all checks.
- Gate 31 remains 🟧 OPEN: encrypted local backup exists, but no independent no-cost off-host destination or separate recovery-key custody is configured.
- Gate 38 remains 🟧 OPEN: bounded process-local HTTP metrics and local incident journal exist; central multi-worker collector/dashboard, WebSocket metric aggregation, durable metric/log retention and independent operator notification remain absent.
- Gate 10: **0/10 formally closed**. 🟨🟩 host/owner-verification-only: Gates 8, 30, 34, 35 and 39. 🟧 additional integration remains: Gates 20, 25, 31, 36 and 38. No gate is marked passed.
- Stage 1 remains **30/40 criteria = 300/400 ticks = 75% provisional**. Stages 2–6 and overall project percentage remain unscored because approved weights/denominators are absent.
- Indicator statuses: SMA20 🟨; EMA20 🟨; RSI14 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; shared indicator hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥. Numerical correctness work is not visual completion.
- ZERO COST: no paid hosting, deployment, production credentials, Vercel/Cloudflare operation, Termux/device operation or main modification.




---

# DEZZTA CHART — CURRENT PROJECT CONTROL DASHBOARD

**Checkpoint:** 21 November 2026 — Batch 62J-77, normalized SMA overflow correction and exact-head CI acceptance  
**Active branch:** `phase-2/market-data-foundation`  
**Latest source/test HEAD:** `e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8`

## Project stage dashboard

| Stage | State | Verified progress |
|---|---|---:|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 ACTIVE / provisional | **75%** — 30/40 criteria |
| Stage 2 — Market Data & Provider Integration | ⬜ NOT SCORED | No approved denominator |
| Stage 3 — Advanced Trading & Order Flow | ⬜ NOT SCORED | No approved denominator |
| Stage 4 — Charting & Technical Indicators | ⬜ NOT SCORED | No approved denominator |
| Stage 5 — Alerts, Automation & Workspace | ⬜ NOT SCORED | No approved denominator |
| Stage 6 — Release, Operations & Scale | ⬜ NOT SCORED | No approved denominator |

**Overall project:** NOT SCORED. M1–M8 weights and the overall acceptance denominator have not been approved. The historical 20.9% figure is not a current weighted result.

## Stage 1 / Gate 10

**Stage 1:** 30/40 criteria = 300/400 ticks = **75% provisional**. Remaining: 10 criteria / 100 ticks. Source changes, documentation and CI alone do not award production-acceptance ticks.

**Gate 10:** <badge color="warning">0/10 formally closed</badge> — Gates 8, 30, 34, 35 and 39 are 🟨🟩 host/owner-verification-only; Gates 20, 25, 31, 36 and 38 remain 🟧 OPEN for additional provider/host/device integration. A gate turns 🟩 only after complete acceptance evidence is reviewed.

**Meaning of host/owner verification only:** this is not the same as opening the Android APK. It means the repository-side implementation and CI checks are complete for that gate, but evidence must be collected from the real owner-controlled server, storage, certificate/provider account or operator process. For Gate 36, a separate Android/browser acceptance test will be needed only after a real public HTTPS/WSS endpoint exists. No APK test can substitute for Redis TLS, host secrets, backup storage, persistent volumes or operator recovery evidence.

| Gate | State | Remaining acceptance evidence |
|---:|---|---|
| 8 — Secrets | 🟨🟩 HOST VERIFICATION ONLY | Actual host secret injection, owner/mode, process exposure and runtime review |
| 20 — Firebase | 🟧 OPEN | Verified no-billing real Firebase auth/revocation/entitlement and browser/Android flow |
| 25 — Redis | 🟧 OPEN | Real host TLS, ACL, credential lifecycle, persistence and failover |
| 30 — Restore | 🟨🟩 HOST VERIFICATION ONLY | Restore drill against actual live database path on owner-controlled runtime |
| 31 — Off-host backup | 🟧 OPEN | Independent destination/key custody and restore; constrained by one-device boundary |
| 34 — Persistent volume | 🟨🟩 HOST VERIFICATION ONLY | Actual host mount, ownership, restart persistence and disk-pressure recovery |
| 35 — HTTPS | 🟨🟩 HOST VERIFICATION ONLY | Real HTTPS endpoint, certificate/hostname and renewal path |
| 36 — WSS | 🟧 OPEN | Public reverse proxy plus real browser and Android WebView acceptance |
| 38 — Monitoring | 🟧 OPEN | Collector/dashboard, retention, access control and disk-pressure acceptance |
| 39 — Incident response | 🟨🟩 HOST/OPERATOR VERIFICATION ONLY | Real operator visibility, acknowledgement/escalation and recovery drill |

## Exact-head CI

- Automated Tests [44863517983](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863517983): **SUCCESS** — frontend 247/247; backend 1,238 passed in 49.89s; 32/32 workflow steps. CodeQL [44863518025](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863518025) and Full Git History Secret Audit [44863517962](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863517962): **SUCCESS**.
- Frontend dependency audit: 0 vulnerabilities. Backend dependency audit: no known vulnerabilities. Trivy scanned Alpine and Python package targets with 0 vulnerabilities.
- Backend container build and Redis ACL/AOF + persistent-volume smoke: **SUCCESS**.

## WebSocket status

**Automated failure matrix: COMPLETE for the defined repository scope.** Verified work includes two independent ASGI processes, separate replicas/consumer groups, authenticated live delivery, reconnect replay, process restart continuity, Redis read-failure recovery, independent Redis TCP interruption/recovery, and coordinated snapshot-generation replacement. External production snapshot distribution/rotation/rollback, production Redis TLS/ACL/network/failover, public HTTPS/WSS, and browser/Android acceptance remain open.

## Complete indicator status

| Indicator / subsystem | State | Formula / first valid candle | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Mean of 20 closes; index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; alpha = 2/21; index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| RSI14 | 🟨 FOUNDATION | Wilder smoothing over 14 close changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 FOUNDATION | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, MACD/signal lines, histogram, zero guide, toggle, legend |
| Bollinger20,2 | 🟨 FOUNDATION | Mean ± 2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 FOUNDATION | Validated backend snapshot; no DEMO fallback; candle-index aligned | Identity/timeframe binding, loading/error, stale clearing, series isolation |
| Footprint | 🟧 SIMULATED / GATED | Educational simulated accumulator; not exchange-native bid/ask truth | Owner reference image, approved blueprint, ON-only spaced clusters, bid/ask cells, performance tests |
| Heatmap | 🟥 NOT IMPLEMENTED | Data source/calculation contract not approved | Reference image, source feasibility, validated data contract, blueprint and renderer |
| Liquidation Maps | 🟥 NOT IMPLEMENTED | No validated liquidation dataset/calculation contract | Zero-cost source feasibility, validated calculation, blueprint/reference and renderer |

**Indicator correctness invariants:** warm-up slots are null, never fabricated zeroes; every series aligns to candle indices; appending future candles cannot change earlier outputs; symbol/venue/dataset/chart/timeframe changes invalidate stale series. Footprint OFF preserves standard candle spacing; only explicit ON activates the spaced cluster layout. Footprint and Heatmap visual work waits for the user's reference images and reviewed blueprints. No aggregate indicator percentage is assigned.

**Cost/device boundary:** ZERO COST. No Vercel/Cloudflare deployment, paid service, Termux/device command, production credential, or `main` modification.

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

### Remaining WebSocket acceptance blockers — current position (reconciled 21 Nov 2026)

The earlier 62J-15 failure-matrix gap is **superseded** by the verified dual-ASGI and real-Redis evidence in Batches 62J-25, 62J-28 and 62J-31. Batch 62J-69 then removed four synchronous test-client deprecation warnings without changing runtime behavior.

1. **Production snapshot lifecycle:** owner-provisioned distribution, rotation, rollback, retention and authorized cleanup of verified replica snapshots.
2. **Production Redis operations:** real-host TLS certificate validation, least-privilege ACL provisioning/rotation, network policy, persistence, supervision and failover/recovery evidence.
3. **External client path:** accepted public HTTPS/WSS endpoint plus browser and Android WebView handshake, auth/entitlement, reconnect/replay and resnapshot acceptance.
4. **Operator acceptance:** target-host runbook, observed incident/recovery drill and evidence retention.

**Automated failure matrix:** COMPLETE for its defined scope. Do not reopen already-passed two-ASGI live delivery, replay, gateway restart, independent TCP-path interruption/recovery or generation-replacement tests as if they were unimplemented. Do not infer production deployment or close Gates 25/34/35/36 from CI-only evidence.

### Exact-head CI evidence — Batch 62J-69

At branch HEAD `96bfea52d9920b7d5d49ed85c0536610a6afd037`, Automated Tests run `44849892717` completed **SUCCESS**. Frontend: 245/245 tests across 29 files. Backend: 1,218 passed in 48.17 seconds; pytest emitted no warnings summary. All 31 listed job steps completed successfully, including frontend build/scans, backend tests, synthetic SQLite outbox benchmark, dependency audits, backend image build, Redis ACL/AOF + mounted-volume smoke test, Trivy scan and vulnerability report export.

The four changed lines are confined to `backend/tests/test_ohlcv_redis_consumer.py`: synchronous WebSocket test clients now explicitly pass `legacy=True` alongside `ping_interval=None`. This resolves the legacy-client deprecation warnings shown by the previous test run. No production WebSocket code, API contract, chart, indicator or database behavior changed. The separately recorded CodeQL and full-history audit successes remain at prior code/test HEAD `56317eff2b71886040acb998bf692814622feedf`; they are not mislabeled as exact-head checks for this test-only commit.


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
- Two-ASGI process/WebSocket acceptance is already CI-verified (Batch 62J-25); transient Redis read recovery and process restart continuity (62J-28), TCP-path interruption/recovery and coordinated snapshot-generation replacement (62J-31) are also CI-verified. The automated WebSocket E failure matrix is complete for its defined repository scope. Production snapshot artifact distribution/rotation/rollback, production Redis TLS/ACL/topology, public WSS and browser/Android acceptance remain open. Do not claim production readiness.
- Exact docs HEAD `290c4fe1b4a125e9a41b410d942e807db22c58aa`: Test and Build, CodeQL JavaScript/TypeScript, CodeQL Python, and full reachable Git-history secret audit all SUCCESS. Frontend 245/245 across 29 files; backend 1,218 passed, 6 warnings. This is CI evidence, not production acceptance.
- No runtime/indicator code changed. Indicator status remains unchanged; no indicator percentage is assigned. Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; overall project and aggregate indicator percentages remain unestablished.
- Next WebSocket batch: do not repeat the passing two-ASGI CI harness. Progress only through approved owner-side snapshot artifact lifecycle, production Redis TLS/ACL/topology evidence, and then public WSS/browser/Android acceptance. Keep production replica mode opt-in.
- ZERO COST. No Termux/device command, deployment, Vercel/Cloudflare operation, paid service, or `main` modification.


## Batch 62J-69 progress reconciliation — 21 November 2026

- WebSocket source publisher lifecycle: 🟨🟩 host-factory / snapshot-verification pending. Exact-head CI passed on 6f49951c253a7e7b995b4bdd52eba8153edaef77. FastAPI validates source-store identity, checkpoint/source ID, dedicated Redis client and stream key; then performs startup PING, bounded background relay, persisted-bar wake-up, 1-second backlog polling, bounded retry, terminal resnapshot-required handling and guarded shutdown. Owner-host snapshot watermark, ACL and durable-volume checks remain open.
- WebSocket production acceptance: 🟧 OPEN. This batch does not close public WSS, production Redis TLS/ACL topology, snapshot distribution/rotation/rollback, browser or Android WebView acceptance.
- Indicator implementation unchanged. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 FOUNDATION; Footprint remains 🟧 SIMULATED / GATED; Heatmap and Liquidation Maps remain 🟥 NOT IMPLEMENTED. No indicator progress percentage is awarded by a backend-only change.
- Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional. Overall project percentage and aggregate indicator percentage remain unscored because approved denominators/weights are not established.
- ZERO COST maintained: no deployment, paid service, production credential, Termux/device operation, or `main` modification.


## Batch 62J-72 — snapshot artifact SHA-256 receipt binding (21 November 2026)

**Source/test checkpoint:** `0a8e28e0ae9b8e63f800cf4ff643a057c942ee90` (CI result must be read from this exact commit before any pass claim).

- Hardened `backend/app/ohlcv_redis_runtime.py`: the host verifier contract now requires the verified global snapshot's canonical lowercase SHA-256 digest (`snapshot_sha256`).
- Every required gateway installation receipt must carry the exact same digest in addition to matching source ID, stream key, snapshot generation and cursor.
- Missing/malformed manifest digests and per-gateway digest mismatches fail closed **before Redis client creation**.
- The runtime returns the verified digest as part of its non-secret snapshot evidence summary.
- This binds the receipts to the exact exported snapshot bytes. It does not authenticate receipts by itself: the owner-host verifier must still call the repository's `SQLiteOhlcvStore.verify_global_snapshot()` against the actual artifact and authenticate the authoritative receipt source. The repository cannot attest to remote host state.
- Added regressions for per-gateway digest mismatch and malformed manifest digest, alongside the existing cursor mismatch and successful TLS factory path.
- No indicator formula, hook, renderer or UI changed. No Gate 10 acceptance tick is awarded by this repository-side hardening.
- ZERO COST. No production Redis connection, deployment, Vercel/Cloudflare operation, production credential, Termux/device action or `main` modification.

**Acceptance boundary:** Gate 25 remains 🟧 OPEN pending live Redis TLS/ACL, persistence/failover and host credential lifecycle. Gate 36 remains 🟧 OPEN pending public HTTPS/WSS proxy and browser/Android runtime acceptance. Source publisher stays 🟨🟩 HOST VERIFICATION PENDING.


## Latest engineering checkpoint — Batch 62J-75 (21 November 2026)

**Verified CI head:** `3e3428910e3226f3d4365808f3a36a3138674231` — Automated Tests run [44874341856](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341856), CodeQL run [44874341916](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341916), and full Git-history secret audit run [44874341885](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341885) all SUCCESS. The CI run executed the Redis ACL integration test and finished with **1,249 backend tests passed in 57.10 seconds**. The Docker smoke step, image scan and vulnerability-report export/upload also succeeded.

**Batch 62J-73 correction — least privilege:** review of the real-Redis ACL tests showed that redis-py uses database 0 as its default without issuing `SELECT 0`. Granting `+select` was therefore unnecessary and broader than required. Batch 62J-74 removes `+select` from both publisher and gateway allow-lists. The integration test now proves both roles can PING and perform their allowed operations while explicit `SELECT 1` is denied. URL validation continues to reject every non-zero database path. This is a security-scope tightening; the earlier claim that `+select` was needed is superseded.

**Verified zero-cost CI simulation:**
- Redis 7 service-backed ACL integration: publisher and gateway identities authenticate with disposable runtime-only passwords; allowed stream/lease operations succeed and prohibited command/key access is denied.
- Existing end-to-end Redis tests also pass: source publisher deterministic cursor append/read-back, per-gateway consumer groups, durable apply-before-ACK, snapshot generation reset, event replay, callback retry, lease ownership and ACL role separation.
- Backend container smoke: authenticated Redis ACL; rejects unauthenticated, wrong-password and unrelated SET access; AOF data and ACL file survive Redis container restart; backend returns fail-closed 503 while Redis is down and recovers after Redis returns; non-root UID/GID and mounted-volume ownership are verified; SQLite integrity and backend restart persistence are verified; rate-limit enforcement is verified.
- Backend image vulnerability scan and vulnerability report artifact export/upload: SUCCESS.
- Frontend tests/build/secret scans, backend dependency audit, Gitleaks full-history audit and CodeQL: SUCCESS.
- The synthetic outbox benchmark uses 1,000 synthetic bars, 250-event pages and two concurrent readers. It is explicitly synthetic and is not market-data performance evidence.

**Important scope boundary:** the CI smoke Redis is a temporary guard-service container with an AOF volume. It does not establish production persistence/failover for the dedicated OHLCV stream, nor a live production Redis TLS endpoint. The CI ACL test is real Redis command/key enforcement but remains ephemeral. No production host exists.

**WebSocket status:** repository-side automated WebSocket E/failure-matrix acceptance is complete for its defined CI scope. Production WebSocket acceptance is not complete: real snapshot distribution and installation receipts, production Redis TLS/ACL topology, host secret rotation, stream persistence/failover/retention, public HTTPS/WSS reverse proxy and browser/Android WebView acceptance remain external.

**Gate 10:** 0/10 formally closed. Gate 8 remains 🟨🟩 host-verification-only. Gates 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain 🟧 OPEN; this batch provides repository/CI evidence but does not award a formal gate tick. Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored because approved denominators/weights are not established.

**Complete indicator ledger — unchanged by this backend batch:**
- SMA20 — 🟨 foundation; arithmetic mean of the last 20 closes; first valid candle index 19. Remaining: overlay rendering, visibility toggle, legend/current value, stale-series clearing and renderer tests.
- EMA20 — 🟨 foundation; SMA-seeded EMA, alpha = 2/21; first valid index 19. Remaining: overlay rendering, visibility toggle, legend/current value, stale-series clearing and renderer tests.
- RSI14 — 🟨 foundation; Wilder smoothing; first valid index 14. Remaining: dedicated 0–100 pane, 30/70 guides, toggle, legend and renderer tests.
- MACD 12/26/9 — 🟨 foundation; EMA12−EMA26 first valid index 25; signal and histogram first valid index 33. Remaining: dedicated pane, signal lines, histogram, zero guide, toggle, legend and renderer tests.
- Bollinger20,2 — 🟨 foundation; mean ± 2 × population standard deviation; first valid index 19. Remaining: three-line overlay, toggle, displayed values, stale-series clearing and renderer tests.
- Shared Indicator Hook — 🟨 foundation; validated, candle-index-aligned snapshot. Remaining: full identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation.
- Footprint — 🟧 simulated/gated; requires the user's visual reference, approved blueprint, ON-only spaced candle/cluster layout, bid/ask cells and performance acceptance.
- Heatmap — 🟥 not implemented; requires user's visual reference, zero-cost source feasibility, validated data contract, approved blueprint and renderer.
- Liquidation Maps — 🟥 not implemented; requires zero-cost source feasibility, validated calculation/data contract, approved blueprint/reference and renderer.

Indicator invariants: warm-up values are `null`, never zero; all values align to candle indices; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves ordinary candle spacing; only explicit ON enables spaced cluster layout. No indicator implementation credit is awarded by backend-only work.

**Cost/device:** ZERO COST. No paid hosting, deployment, Vercel/Cloudflare operation, production credential request, Termux command, device action or `main` modification.


## Batch 62J-88 — exact-head metrics and process contention hardening (21 November 2026)

- Exact-head Automated Tests on `8424e5eefeecbd06c6534bc34d166f4749ba4055`: [44903581963](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581963) SUCCESS, 35/35 steps; frontend 255/255 across 29 files; backend 1,268 passed in 46.21 seconds. CodeQL [44903581995](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581995) SUCCESS; Full Git History Secret Audit [44903581971](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581971) SUCCESS.
- Full-cardinality benchmark verified 899/899 series at 1, 4 and 16 threads. All integrity checks `ok`; 16-thread p95 562.43 ms, p99 982.13 ms and 196 retries. This indicates contention remains; Gate 38 stays OPEN.
- Batch 62J-88 removes benchmark/test outer retries, adds four-process SQLite contention measurement and read-only failure/recovery coverage. These additions require exact-head CI before acceptance.
- Gate 38 remains 🟧 OPEN pending process benchmark CI, disk-full test, app-level HTTP/WebSocket isolation, owner-host persistence/retention/backup and operator acceptance.
- WebSocket repository-side automated matrix remains complete; production WSS acceptance remains host-gated. No WebSocket data-path change.
- Indicator progress unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, shared hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. No indicator credit from backend work.
- Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35, 39 🟨🟩; Gates 20, 25, 31, 36, 38 🟧. Stage 1 remains 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST; no deployment, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.


## Batch 62J-89 — remove stray assertion from thread regression (21 November 2026)

- Initial CI for commit `002517f778bed20bcb9e7fe7eed7946893c9763f`: Automated Tests [44904630244](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630244) failed one test; frontend 255/255 passed, backend 1,268 passed and one failed.
- Root cause was a test-edit residue: after the intended single `collector.flush(...)` call, the thread test still contained an unconditional `raise AssertionError("bounded SQLite retry loop exhausted")`. The flush completed; the test then deliberately failed. This was not evidence of collector retry exhaustion.
- In the same run, the new read-only recovery test passed, and the benchmark contract test—including the four spawned OS-process/899-series case—passed.
- CodeQL [44904630257](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630257) SUCCESS; Full Git History Secret Audit [44904630302](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630302) SUCCESS.
- Correction removes only the stray assertion. It does not restore benchmark/test outer retries and does not change production collector code.
- Exact-head CI must rerun before the process/read-only additions are accepted. Gate 38 remains 🟧 OPEN.
- Indicator state unchanged; Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST; no deployment, Termux/device action, or `main` modification.

## Batch 62J-90 — process benchmark and corrected exact-head acceptance (21 November 2026)

Exact-head source/test commit `2650c70e977b22a4c70a5e0e292dcc3a8a59082c` passed Automated Tests [44904944196](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944196): 35/35 workflow steps, frontend 255/255 tests across 29 files, backend 1,269 passed in 53.67 seconds. CodeQL [44904944207](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944207) SUCCESS; Full Git History Secret Audit [44904944202](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944202) SUCCESS.

Artifact `synthetic-metrics-collector-benchmark`, ID `14707137707`, verifies all 899 series and SQLite integrity for thread and process cases.

| Workload | Flushes | p50 ms | p95 ms | p99 ms | Max ms | Retries |
|---|---:|---:|---:|---:|---:|---:|
| 1 thread | 32 | 15.198 | 15.997 | 17.820 | 17.820 | 0 |
| 4 threads | 128 | 14.024 | 192.993 | 290.086 | 354.538 | 2 |
| 16 threads | 512 | 120.955 | 654.798 | 921.534 | 2,769.913 | 251 |
| 4 OS processes | 128 | 14.403 | 243.724 | 278.107 | 415.647 | 4 |

All four cases verified 899 logical series; process case verified four separate workers and 128/128 flushes. The 16-thread contention tail remains high and is not hidden by benchmark-only retries. Process case post-checkpoint DB+WAL+SHM = 487,424 bytes; not a peak-size or production-volume estimate.

Batch 62J-90 adds a genuine SQLite page-limit/disk-full rollback-and-recovery test plus an app-level test that forces metrics flush failure while verifying HTTP health, operator metrics status and authenticated WebSocket status remain responsive. These additions are pending exact-head CI. No production collector behavior changes in this batch.

- Batch 62J-90 adds a genuine SQLite `max_page_count` exhaustion test and application-level collector-failure isolation test. They are pending exact-head CI; Gate 38 remains 🟧 until passed and owner-host checks are complete.


## Batch 62J-91 — disk-full test liveness assertion timing correction

Automated Tests [44905465144](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905465144) reported 1,270 passed / 1 failed. The SQLite `SQLITE_FULL` exception and aggregate rollback assertions passed. The only failure was the test expecting one live worker at snapshot time 1801 although the last successful checkpoint was 900 and the stale threshold is 90 seconds; the collector correctly reported zero live workers. The test now checks at timestamp 901 (checkpoint age 1 second). The app-level HTTP/WebSocket failure-isolation test and read-only recovery test passed. CodeQL [44905465128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905465128) and Full Git History Secret Audit [44905464959](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905464959) passed. Exact-head Automated Tests rerun pending. No collector code or indicator implementation changed.

## Batch 62J-92 — exact-head acceptance: process, disk-full and traffic isolation (21 November 2026)

**Accepted exact HEAD:** `427e5952d2f209ae1f40405223d8d0a4c7d8408c`

- Automated Tests [44905839386](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839386): **SUCCESS**, 35/35 workflow steps.
- Frontend: **255/255 tests across 29 files**.
- Backend: **1,271 passed in 39.80 seconds**.
- CodeQL [44905839403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839403): **SUCCESS**, Python and JavaScript/TypeScript.
- Full Git History Secret Audit [44905839442](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839442): **SUCCESS**.
- Backend container build, ephemeral Redis shared-guard/persistent-volume smoke, Trivy scan and report export: **SUCCESS**.

### Gate 38 repository-side evidence
- Full 899-series benchmark: 1/4/16 Python threads and 4 independent OS processes; exact series counts, worker counts, aggregation and SQLite integrity verified.
- 4-process case: 128/128 flushes; 899/899 series; p95 243.724 ms; p99 278.107 ms; 4 internal retries; SQLite integrity `ok`.
- 16-thread case: 512/512 flushes; 899/899 series; p95 654.798 ms; p99 921.534 ms; max 2,769.913 ms; 251 internal retries. The contention tail remains visible and is not concealed by benchmark-only retries.
- Read-only storage failure/recovery test passed.
- Real SQLite `SQLITE_FULL` page-limit test passed: second full-cardinality bucket rejected; transaction and checkpoint rolled back; later writable flush recovered without double counting.
- App-level failure-isolation test passed: collector entered degraded state while HTTP health, authenticated metrics scrape and authenticated WebSocket status remained responsive.
- These are repository/CI results, not owner-host persistence or production operator acceptance.

### Remaining Gate 38 host/operator acceptance
Actual owner-host persistent volume and permissions; restart persistence; measured disk pressure/retention; backup/restore; reverse-proxy/firewall isolation; operator-token injection/rotation; operator dashboard visibility/access review; independent notification, acknowledgement/escalation and recovery drill. Multi-host SQLite remains unsupported.

### Indicator and project status
No indicator calculation, hook, renderer or UI changed. SMA20 🟨 (first valid index 19); EMA20 🟨 (SMA-seeded, alpha 2/21, index 19); RSI14 🟨 (Wilder, index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram 33); Bollinger20,2 🟨 (population SD, index 19); Shared Indicator Hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥. Warm-up null, candle-index aligned, no future-candle repaint and stale clearing remain invariants.

Gate 10 remains **0/10 formally closed**. Gates 8, 30, 34, 35 and 39 remain 🟨🟩 host/owner-verification-only. Gates 20, 25, 31, 36 and 38 remain 🟧 OPEN; Gate 38 is not yellow-green because operator dashboard/notification/recovery and owner-host acceptance remain. Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.

ZERO COST. No deployment, paid service, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.

## Batch 62J-93 — SQLite metrics batch-read optimization and exact-head acceptance (21 November 2026)

**Source/test HEAD:** `a62e7423a5d36d3fdbc003e0e56d86c3a9e6ecbb`

- Automated Tests [44911391436](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391436): **SUCCESS**, 35/35 steps.
- Frontend: **255/255 tests across 29 files**.
- Backend: **1,271 passed in 55.86 seconds**.
- CodeQL [44911391400](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391400): **SUCCESS** for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [44911391397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391397): **SUCCESS**.
- Frontend npm audit: 0 vulnerabilities; backend dependency audit: no known vulnerabilities; Trivy reported 0 vulnerabilities in the scanned Alpine and Python package targets.
- Backend container build, shared-Redis/SQLite persistent-volume smoke, full-cardinality metrics benchmark, image scan and report export: **SUCCESS**.

### What changed
`backend/app/metrics_collector.py` now reads the existing rows for the active 15-minute bucket once per flush, computes deltas in memory, and submits non-zero aggregate updates through `executemany`. The existing `BEGIN IMMEDIATE` transaction boundary, per-worker checkpoint, JSON value schema, retention cleanup, capacity enforcement and rollback behavior remain intact. This removes one bucket SELECT per logical series without changing the metric schema or WebSocket data path.

At 899 active logical series and 512 flushes, bucket reads are reduced from 460,288 per-key SELECTs to 512 batched SELECTs: **99.8888% fewer bucket-read statements**. This is a query-count calculation from the old/new code paths; the benchmark independently measures resulting wall-clock behavior.

### Full-cardinality benchmark — before versus after
The prior baseline is exact-head commit `2650c70e977b22a4c70a5e0e292dcc3a8a59082c`; the optimized result is exact-head `a62e7423a5d36d3fdbc003e0e56d86c3a9e6ecbb`. Both use synthetic 899-series payloads on CI runners, not production hardware.

| Workload | p95 before → after | p99 before → after | Max before → after | Retries before → after |
|---|---:|---:|---:|---:|
| 1 thread, 32 flushes | 15.997 → 13.172 ms | 17.820 → 14.003 ms | 17.820 → 14.003 ms | 0 → 0 |
| 4 threads, 128 flushes | 192.993 → 190.979 ms | 290.086 → 405.913 ms | 354.538 → 441.050 ms | 2 → 3 |
| 16 threads, 512 flushes | 654.798 → 600.947 ms | 921.534 → 944.797 ms | 2,769.913 → 1,727.381 ms | 251 → 154 |
| 4 OS processes, 128 flushes | 243.724 → 114.703 ms | 278.107 → 280.654 ms | 415.647 → 378.409 ms | 4 → 2 |

Relative changes:
- 16-thread p95 **−8.22%**, p99 **+2.52%**, max **−37.64%**, retries **−38.65%**.
- Four-process p95 **−52.94%**, p99 **+0.92%**, max **−8.96%**, retries **−50%**.
- Four-thread p95 **−1.04%**, but p99 **+39.93%** and max **+24.40%**. This tail regression is retained explicitly, not hidden.
- One-thread p95 **−17.66%** and p99 **−21.42%**.

All cases verified 899/899 logical series and SQLite `integrity_check=ok`; all expected flushes completed. The 16-thread case still has measurable lock contention. No latency SLA has been approved, so these results are comparative evidence, not a production performance guarantee.

### Gate 38 disposition
Repository-side full-cardinality benchmark, separate-process contention, read-only recovery, SQLite `SQLITE_FULL` rollback/recovery and app-level HTTP/WebSocket failure isolation are CI-verified. Gate 38 remains 🟧 OPEN pending actual owner-host volume/permissions/restart/retention/backup/disk-pressure, firewall/reverse-proxy and operator-token controls, dashboard visibility/access review, independent notification, acknowledgement/escalation and recovery drill. Same-host SQLite only; multi-host remains unsupported.

### Project and indicator accounting
Gate 10 remains **0/10 formally closed**. Gates 8, 30, 34, 35 and 39 are 🟨🟩 host/owner-verification-only; Gates 20, 25, 31, 36 and 38 remain 🟧. Stage 1 remains **30/40 = 75% provisional**; no tick is awarded by this optimization. Stages 2–6 and overall project percentage remain unscored.

No indicator formula, hook, renderer, UI or market-data contract changed. SMA20 🟨 (first valid index 19); EMA20 🟨 (SMA seed, alpha 2/21, index 19); RSI14 🟨 (Wilder, index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram index 33); Bollinger20,2 🟨 (population SD, index 19); Shared Hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥. Warm-up nulls, candle-index alignment, no future-candle repaint and stale-series clearing remain required.

ZERO COST. No deployment, paid service, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.


## Batch 62J-94 — Gate 38 tail-latency phase diagnostics (21 November 2026)

The collector now reports internal writer-lock wait and transaction-body/commit durations. Full-cardinality 1/4/16-thread and four-process benchmark output includes phase percentiles alongside end-to-end latency. This is diagnostic instrumentation, not an optimization or host/SLA result; exact-head CI is required. WebSocket paths and indicator implementation are unchanged; no indicator credit. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 closed; overall project remains unscored. ZERO COST; no deployment, Termux, device operation or `main` change.


## Batch 62J-95 — SQLite retry de-synchronization (21 November 2026)

The prior benchmark separated lock wait from transaction time and showed lock wait dominated the 16-thread p99 (617.533 ms of 625.336 ms) and remained significant in the four-process case (103.635 ms of 275.777 ms). Identical deterministic retry delays could synchronize contending workers. The collector now uses stable BLAKE2s-derived per-worker jitter (factor 0.5–1.0) while preserving the explicit-backoff ceiling: 0.81 s. With eight 250 ms SQLite busy-timeout attempts, the theoretical lock-acquisition wait remains ≤2.81 s. This is an optimization hypothesis pending exact-head CI and a fresh benchmark; no improvement is claimed yet. Indicators and WebSocket data path unchanged; no indicator credit. Stage 1 30/40 = 75% provisional; Gate 10 0/10 closed; overall project unscored. ZERO COST; no deploy/Termux/device operation.


## Batch 62J-96 — revert of regressive retry-jitter experiment (21 November 2026)

The 62J-95 per-worker retry-jitter experiment failed the comparison gate and was reverted. Against the immediately preceding 62J-94 benchmark on the same CI workflow shape, the 16-thread case regressed: p95 390.277 → 599.624 ms (+53.6%), p99 625.336 → 1,125.048 ms (+79.9%), max 878.721 → 2,042.702 ms (+132.4%), retries 105 → 181 (+72.4%). Four-thread p95 rose 120.249 → 190.787 ms (+58.7%); four-process p95 rose 62.234 → 139.278 ms (+123.8%). These are synthetic CI-runner results, not host performance guarantees. The jitter source/test changes were reverted; Batch 62J-94 phase instrumentation remains. No optimization benefit is claimed. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 closed; overall project unscored.


## Batch 62J-99 — Gate 25/36, Gate 38, Gate 20/31 three-workstream audit (21 November 2026)

Audited branch baseline `ae1ff4ada7977239b6970cd5bef02335ece29f08`. Repository-side review covered the gateway runtime and WSS guards (Gate 25/36), the bounded 899-series same-host SQLite collector and its disk-full/read-only/isolation tests (Gate 38), Firebase Admin revocation-aware identity verification plus deny-by-default per-instrument entitlements (Gate 20), and AES-256-GCM encrypted SQLite backup/fresh-path restore tests (Gate 31). No code-level defect was established, so no runtime source change was made. Host-side blockers remain real: Redis TLS/ACL and installed snapshot receipts; public HTTPS/WSS and Android WebView; metrics volume/dashboard/operator drill; real Firebase signed-token E2E; independent off-host backup and key-recovery restore. Gate 10 remains 0/10 formally closed; Gates 8/30/34/35/39 🟨🟩 host-only; Gates 20/25/31/36/38 🟧. Stage 1 remains 30/40 = 75% provisional; overall project remains unscored. Full indicator matrix and formulas recorded in the Batch 62J-99 work-cycle document; no indicator implementation changed and no indicator credit awarded. No CI was triggered for docs-only changes. ZERO COST; no deployment, Termux/device operation, production credentials or `main` modification.


## Batch 62J-100 — Gate 38 cold-start retry, Gate 39 escalation integration, WebSocket cancellation accounting (21 November 2026)

Accepted source/test HEAD `9e9a3d099f30faa2b641b8c991187394de783960`. The 16-worker standalone SQLite metrics benchmark previously failed in `SQLiteMetricsCollector._connect()` during cold-start schema bootstrap. The bounded bootstrap retry increased from 7 to 12 attempts while retaining 250 ms busy timeout and capped backoff. Conservative wait bound: 12 × 0.25 s + 1.81 s backoff = 4.81 s. A 16-independent-collector cold-start regression test now passes. Exact-head CI [44918802298](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802298): frontend 255 tests/29 files; backend 1,280 passed; full-cardinality 899-series metrics benchmark success; container build and shared Redis guard/persistent-volume smoke success. CodeQL [44918802275](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802275) and Full Git History Secret Audit [44918802271](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802271) succeeded. Trivy artifact 14713530156: zero HIGH/CRITICAL vulnerabilities in scanned Alpine OS and Python package targets. Gate 39 lifespan escalation and WebSocket cancellation cleanup now have integration tests; remote operator notification and production WSS remain unverified. Gate 10 remains 0/10 closed; Gates 8/30/34/35/39 🟨🟩; Gates 20/25/31/36/38 🟧. Stage 1 remains 30/40 = 75% provisional; overall project remains unscored. No indicator implementation changed and no indicator credit is awarded; full matrix and invariants are recorded in the Batch 62J-100 work-cycle document and indicator ledger. ZERO COST; no deployment, Termux/device operation, production credentials or `main` modification.



## Batch 62J-101 — WebSocket accepted-counter lifecycle correction + Gate 10 continuation (21 November 2026)

- Active branch: `phase-2/market-data-foundation`; source/test commit: `db010cf76d6da2b1e950156f05bb18606b4fff2d`.
- Corrected `WebSocketMetrics` semantics: `connections_accepted` now increments immediately after a downstream ASGI `websocket.accept` send succeeds, not later when the connection finishes. A failed accept send does not increment it; duplicate accept frames within one connection are counted once. Completion still decrements active and records completed/peer-disconnect/close-code/duration.
- Added an authenticated FastAPI application integration test that checks started/active/accepted while the socket is open and active/completed/accepted after closure. Existing unit tests cover send failure and cancellation paths.
- CI on exact source/test commit: Automated Tests run [44923590787](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590787) is **IN PROGRESS** at documentation time; no pass is claimed. CodeQL [44923590774](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590774): SUCCESS. Full Git History Secret Audit [44923590739](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590739): SUCCESS.
- Failed diagnostic candidate `0857936d9129e51fad37dc921e895c79219f2108`: backend 1,280 passed, 1 failed because the new test exposed the accepted-counter semantic issue. Intermediate candidate `13924cca3b3edff5e6fe41b43df6489924bf3a7b` is not accepted; its temporary test expectation was superseded by the runtime correction in `db010cf...`.
- WebSocket repository evidence is stronger, but Gate 36 remains 🟧 until owner-host TLS/reverse proxy, live Redis gateway, public HTTPS/WSS and browser/Android WebView acceptance. No live host or device verification is claimed.
- Gate 10 remains **0/10 formally closed**. 🟨🟩 host/operator verification only: Gates 8, 30, 34, 35, 39. 🟧 integration/acceptance still open: Gates 20, 25, 31, 36, 38.
- Gate 20: repository identity/entitlement/ticket tests exist; real Firebase signed-token E2E (valid/expired/revoked/wrong project) and final ticket-scope threat-model decision remain external.
- Gate 25: source-side Redis gateway/snapshot validation exists; owner-host TLS/ACL, authenticated snapshot transfer/receipt and persistence/failover remain external.
- Gate 31: encrypted backup and fresh-path restore tests exist; independent off-host destination, offline key custody and key-recovery restore remain external.
- Gate 38: 899-series same-host SQLite collector/benchmark and failure-isolation tests exist; owner-host persistent volume, private access perimeter, dashboard, notification and operator recovery drill remain external.
- Gate 39: lifespan escalation and sanitized event tests exist; external independent notification and operator receipt/drill remain external.
- Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored because approved denominators/weights do not exist.
- Indicator implementation is unchanged; no indicator progress credit is awarded in this backend work cycle. Complete indicator matrix and formulas remain in `docs/INDICATOR_PROGRESS_LEDGER.md`.
- ZERO COST. No Vercel/Cloudflare deployment, paid service, Termux, device action, production credential or `main` modification.



## Batch 62J-101 CI completion — exact source/test HEAD verified (21 November 2026)

- Source/test HEAD `db010cf76d6da2b1e950156f05bb18606b4fff2d`: Automated Tests [44923590787](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590787) **SUCCESS**; frontend 255/255 tests across 29 files; backend 1,281 passed in 48.87 s.
- Synthetic outbox and 899-series SQLite metrics benchmarks, backend dependency audit, backend container build, shared Redis guard/persistent-volume smoke and configured HIGH/CRITICAL Trivy scan all succeeded.
- CodeQL [44923590774](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590774): **SUCCESS**. Full Git History Secret Audit [44923590739](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590739): **SUCCESS**.
- The accepted-counter fix is now CI-verified. This does not close Gate 36: production WSS, owner-host TLS/reverse proxy, live Redis and browser/Android WebView acceptance remain external.
- Gate 10 remains 0/10 formally closed; host/operator-only Gates 8/30/34/35/39 🟨🟩; integration/acceptance Gates 20/25/31/36/38 🟧.
- No indicator source or tests changed; no indicator progress credit. Stage 1 remains 30/40 = 75% provisional; overall project remains unscored.


## Batch 62J-102 — Gate 20 ticket failure boundaries + Gate 10 evidence reconciliation (22 November 2026)

- Source/test HEAD `140df3f33fcebb9154f8ad26f40986ec73e2336f`; Automated Tests, CodeQL and Full Git History Secret Audit all SUCCESS.
- Three FastAPI ticket-endpoint integration tests added: missing Bearer identity → 401; unavailable ticket store → 503; ticket-store exception → sanitized 503 without internal/credential leakage.
- Production Redis policy audited and found already correct: production requires REDIS_URL, rediss TLS and ACL username/password. No unnecessary configuration change.
- Backend 1,284 passed in 46.77 s; frontend 255 passed across 29 files.
- Trivy artifact 14732364657: zero HIGH/CRITICAL findings in scanned Alpine OS and Python package targets, within configured scope.
- Gate 38 synthetic benchmark artifact 14732279593: 899/900 series (99.89%); all profiles passed data/integrity checks; 16-thread contention remains visible (67 retries, p99 595.76 ms, max 1,258.36 ms). CI-runner synthetic only, not production SLA.
- Gate 20 repository evidence improved but no gate closed. Gate 10 remains 0/10; host/operator-only Gates 8/30/34/35/39 🟨🟩; integration/acceptance Gates 20/25/31/36/38 🟧.
- Stage 1 remains 30/40 = 75% provisional; overall project percentage remains unscored.
- No indicator implementation changes; no indicator credit. Complete formula, warm-up, rendering and remaining-work matrix recorded in the indicator ledger.
- No deployment, paid service, Termux, production credential or main-branch change.

## Batch 62J-106 — Production WebSocket acceptance reconciliation (22 November 2026)

### WebSocket production-acceptance disposition

The repository already has CI-verified two-process ASGI/WebSocket fan-out, cursor replay, dual-gateway TCP-path interruption recovery without process restart, and coordinated snapshot-generation replacement. These are repository/CI passes, not public-host acceptance.

The source and gateway runtime factories are implemented with fail-closed validation for production TLS, separate ACL identities, snapshot source/generation/cursor/SHA-256 and gateway installation receipts. FastAPI activation remains owner-injected because authenticated snapshot transfer and receipt verification must be supplied by the actual operator. No production host, public WSS endpoint, real dedicated Redis failover evidence or physical Android WebView session is available in this checkpoint.

Accordingly, WebSocket production acceptance remains **OPEN**. No production pass or gate closure is inferred from CI. The exact outstanding evidence is public HTTPS/WSS and certificate/reverse-proxy acceptance; dedicated production OHLCV Redis TLS/ACL/secret rotation/persistence/failover; authenticated global snapshot distribution and receipts; and browser plus Android WebView acceptance.

### Gate 10

Gate 10 remains **0/10 formally closed**:
- 🟨🟩 Host/operator verification-only: Gates 8, 30, 34, 35 and 39.
- 🟧 Integration/acceptance still open: Gates 20, 25, 31, 36 and 38.

Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored because approved denominators/weights are absent.

### Indicator progress

No indicator source, formula, data contract, hook, renderer, chart UI or indicator test changed. No indicator progress credit is awarded. The full formula, warm-up, status and remaining-work matrix is recorded in `docs/INDICATOR_PROGRESS_LEDGER.md`; statuses remain SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥 and Liquidation Maps 🟥. Warm-up nulls, candle-index alignment, no future-candle repaint and stale-series clearing remain mandatory.

ZERO COST. No deployment, paid service, production credential, Termux/device action, Vercel/Cloudflare operation or `main` modification.


## Batch 62J-107 — WebSocket ticket documentation and indicator reconciliation (22 November 2026)

- Corrected stale `backend/README.md`: production clients exchange Firebase Bearer ID tokens at `POST /v1/auth/websocket-ticket`, then authenticate WebSocket using the purpose-bound single-use ticket (90-second TTL). Direct Firebase-token frame authentication is non-production only.
- Source, client, test and indicator implementation unchanged; no CI run for this documentation-only batch. Existing CI evidence remains tied to its previously recorded source/test HEAD.
- Gate 20/25/36 production acceptance remains open: real Firebase-project E2E; owner-host shared Redis TLS/ACL, snapshot receipts and failover; public HTTPS/WSS, reverse proxy, browser and Android WebView.
- Gate 10 remains 0/10 formally closed: 🟨🟩 host/operator-only Gates 8, 30, 34, 35, 39; 🟧 integration/acceptance Gates 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- Indicator matrix unchanged; no progress credit: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. Full formulas, first-valid indices, invariants and remaining work are documented in `docs/WORK_CYCLE_2026-11-22_BATCH62J107_WEBSOCKET_AUTH_DOC_RECONCILIATION.md` and `docs/INDICATOR_PROGRESS_LEDGER.md`.
- ZERO COST; no deployment, Vercel/Cloudflare operation, paid service, production credential, Termux/device action, or `main` modification.


## Batch 62J-108 — WebSocket documentation contract regression guard (22 November 2026)

- Added `backend/tests/test_websocket_documentation_contract.py` to keep the README aligned with the implemented single-use WebSocket-ticket endpoint, source-defined TTL, auth frame and production legacy-auth rejection.
- No runtime, client, or indicator source changed. No indicator progress credit.
- Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored.
- Gate 20/25/36 production acceptance still requires real Firebase-project E2E, owner-host Redis TLS/ACL/persistence/failover/snapshot receipts, and public HTTPS/WSS plus browser/Android WebView acceptance.
- CI result must be checked against this exact batch commit; no pass is claimed in advance.
- ZERO COST. No deployment, Vercel/Cloudflare operation, paid service, production credential, Termux/device action, or `main` modification.


## Batch 62J-109 — exact-head CI acceptance (22 November 2026)

- Commit: `81b741946f1512fb264936e37406d7560f24456f` on `phase-2/market-data-foundation`.
- Corrected one case-normalization inconsistency in `backend/tests/test_websocket_documentation_contract.py`; README contract itself was already correct.
- Exact-head Automated Tests [44973890901](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890901): **SUCCESS**, all steps completed, no failures. Includes frontend tests/build, backend tests/dependency audit, container build, shared Redis persistent-volume smoke, image scan/report and synthetic SQLite/metrics benchmarks.
- Exact-head CodeQL [44973890847](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890847): **SUCCESS** (Python + JavaScript/TypeScript). Full Git History Secret Audit [44973890902](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890902): **SUCCESS**.
- Gate 10 remains **0/10 formally closed**. Host/operator-only Gates 8, 30, 34, 35, 39; integration/acceptance Gates 20, 25, 31, 36, 38.
- Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- WebSocket production acceptance remains open: public HTTPS/WSS/proxy, owner-host Redis TLS/ACL/persistence/failover, authenticated snapshot transport/receipts, real Firebase E2E, browser and Android WebView acceptance. No production gate closed.
- No indicator implementation changed. Full matrix unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD 12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. Formulas, warm-up indices, invariants and remaining tasks are in this ledger; no indicator progress credit.
- ZERO COST. No deployment, paid service, production credential, Vercel/Cloudflare operation, Termux/device action or `main` modification.


---

## Batch 62J-110 — real Redis TLS integration acceptance (22 November 2026)

- Baseline: `ec8566a2d34e693283b0fa18421aaf3d4d01ef45`; branch `phase-2/market-data-foundation`.
- Adds an ephemeral Redis 7 TLS-only CI fixture with a generated test CA, DNS SAN certificate, separate untrusted CA, ACL-restricted user and disabled plaintext listener.
- Adds real redis-py/RedisSharedGuard handshake tests: trusted CA + correct hostname succeeds; wrong hostname, wrong CA and plaintext protocol are rejected.
- The valid TLS session exercises HTTP rate-limit Lua, one-time WebSocket tickets and WebSocket lease acquire/renew/release.
- Test keys, passwords, certificates and private keys are generated at runtime only; Redis is loopback-bound and removed by the workflow trap.
- No production runtime behavior, indicator code, market-data source or WebSocket protocol changed.
- No indicator progress credit. SMA20 🟨 (index 19); EMA20 🟨 (index 19); RSI14 🟨 (index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram 33); Bollinger20,2 🟨 (index 19); Shared Indicator Hook 🟨; Footprint 🟧 reference-gated; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. Formulas, warm-up rules and remaining visual acceptance are documented in `docs/WORK_CYCLE_2026-11-22_BATCH62J110_REDIS_TLS_INTEGRATION.md`.
- Gate 10 remains 0/10 formally closed; Gate 25 and Gate 36 remain 🟧 OPEN for owner-host/public endpoint evidence. Stage 1 remains 30/40 = 75% provisional; overall project percentage remains unscored.
- Exact-head CI is required before declaring this batch accepted. ZERO COST; no deployment, paid services, Termux/device operation, Vercel/Cloudflare operation or `main` modification.


---

## Batch 62J-111 — Redis TLS fixture permission correction (22 November 2026)

- Parent candidate: `fc13d6ed302c8eccd1fc4cf18102b2c50b66fd5c`.
- Automated CI exposed a concrete fixture startup failure: Redis 7.4.12 runs under its unprivileged `redis` account and could not read the host-owned, mode-0600 `/tls/users.acl` file from the read-only bind mount.
- Corrective change: derive UID/GID from the exact `redis:7-alpine` image at runtime; assign only the Redis server private key and ACL file to that account; retain mode 0600 for private files; make only public certificates readable to the runner/client. CA private key and wrong-CA private key remain unreadable to the container process and are not mounted for Redis use beyond the containing read-only directory.
- No production source/configuration or runtime security behavior changes. TLS verification requirements and negative tests remain intact.
- Acceptance status: pending a new exact-head CI run. No TLS pass is claimed until the fixture starts and all positive/negative tests pass.
- Cost Rp0; no deployment, Termux/device work, paid services or `main` changes.


---

## Batch 62J-112 — separate TLS configuration rejection from plaintext handshake rejection (22 November 2026)

- Parent: `59013f1d9a65e08aef6392f489aca3f3367da072`.
- CI confirmed the Redis TLS-only container starts successfully after Batch 62J-111 permission correction.
- The first real integration execution then failed because the test expected a network `ConnectionError` for plaintext Redis URL while also supplying a custom CA. Production guard correctly rejects that invalid configuration immediately with `ValueError` (`REDIS_TLS_CA_CERTS` requires `rediss://`), before any socket is opened.
- Corrected the integration test to exercise the two distinct protections separately: (1) existing unit test asserts custom CA + plaintext URL is rejected at configuration time; (2) real integration test attempts plaintext against the TLS-only Redis listener without a custom CA and requires connection failure.
- No production code or runtime security behavior changed. CI must rerun on the new exact commit before acceptance.
- Gate 10 remains open; no public WSS or OCI deployment claim. ZERO COST, no Termux/device action, no paid resources, no `main` changes.


# Work cycle — Redis AOF persistence across TLS restart (22 November 2026)

- Branch: `phase-2/market-data-foundation`; parent HEAD: `5b165e5efbcf1fe2ff32592161f4cbc660aedee5`.
- Scope: strengthen the isolated CI Redis TLS fixture; no production Redis configuration or application runtime changes.
- The fixture now mounts a dedicated ephemeral Docker volume at `/data`, enables Redis AOF with `appendfsync always`, and removes the volume during CI cleanup.
- After the TLS/CA/hostname/plaintext integration suite, CI writes a canary under the permitted ACL keyspace, restarts the actual Redis container, reconnects using the trusted CA and ACL identity, and verifies the canary value survived.
- This is a repository-level restart/persistence integration test only. It does not prove OCI block-volume durability, host reboot recovery, encrypted off-host backup, production failover, or public WSS.
- Test-only password and CA remain ephemeral; no production secrets are added. Redis remains TLS-only and no public Redis port is exposed.
- Exact-head CI is pending. Do not mark the batch accepted until Automated Tests, CodeQL, and Full Git History Secret Audit all complete successfully.
- ZERO COST; no cloud resource, paid service, deployment, Termux/device operation, or `main` modification.

## Batch 62J-123 — exact-head SQLite concurrency fix, CI artifacts and acceptance reconciliation (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Exact tested source/test HEAD:** 589aceadd40b3b3e10e950566081101b2dd49003  
**Automated Tests [run 44985059074](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074): SUCCESS**; **CodeQL [run 44985059102](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059102): SUCCESS**; **Full Git History Secret Audit [run 44985059070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059070): SUCCESS**. All three workflows target the exact tested HEAD. Automated Tests completed all 36 job steps with no failed steps.

### CI and artifact evidence
- Frontend unit tests/build, source and production-bundle credential scans, Android host preflight, backend dependency audit/tests, isolated Redis TLS CA/hostname fixture, synthetic SQLite outbox and metrics benchmarks, backend image build, shared-Redis/persistent-volume container smoke, Trivy scan/report export and dependency-audit enforcement all completed successfully.
- Synthetic metrics artifact [14739815366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739815366): full 899-series envelope. One worker: 32/32 flushes, 0 retries, p95 flush 14.34 ms. Four threads: 128/128, 4 retries, p95 flush 46.92 ms. Sixteen simultaneous threads: 512/512, 187 retries, p95 flush 627.74 ms and writer-lock p95 572.23 ms. Four independent processes: 128/128, 3 retries, p95 flush 141.71 ms. Startup-staggered 16-worker case: 512/512, 26 retries, p95 flush 266.53 ms and writer-lock p95 250.93 ms. SQLite integrity reported ok for every case.
- The benchmark confirms no lost flushes in these synthetic cases and exposes material same-file SQLite writer contention at higher concurrency. It is runner/filesystem-specific, uses synthetic operational counters, and is not production load, persistent-volume, multi-host or SLO evidence. Do not infer production capacity from it.
- Synthetic outbox artifact [14739423041](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739423041) is attached to this exact run; it remains local synthetic benchmark evidence, not live provider/WebSocket load acceptance.
- Trivy artifact [14739224531](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739224531) was independently inspected. Image dezzta-chart-backend:ci, Alpine 3.24.4, architecture amd64, digest sha256:5240158d55f11863aa41a49fbf4d00705d437519fcbdb0659164efc435ee58c0, size 571,352,064 bytes (~571.35 MB). The report contains 0 vulnerabilities in the scanned Alpine OS and Python package result groups. This is a point-in-time result for this exact amd64 image and scanner database, not a permanent guarantee, not a scan of every possible target, and not ARM64 evidence.
- Backend and frontend exact-head CI success proves the repository's configured tests and CI service topology only. The CI Redis fixture and ephemeral runner volume do not constitute owner-host acceptance.

### SQLite corrective change and remaining risk
- Commit 529031d3a6ae0d07cfcd2f38a5d7e02fffd81063 adds bounded retry for lock-only errors while applying connection-local PRAGMA synchronous=NORMAL to fresh SQLite connections. Commit 589aceadd40b3b3e10e950566081101b2dd49003 adds a 16-independent-collector, eight-round repeated concurrent-flush regression test.
- Exact-head backend tests and full CI pass. The prior fatal database-is-locked failure at connection PRAGMA setup was not reproduced in this run.
- The benchmark still shows substantial contention at 16 simultaneous workers (187 retries). Keep the collector classified as bounded same-host best-effort telemetry; do not claim high-concurrency production readiness. A single-writer queue/aggregation redesign would be a separate scoped architecture change, not silently bundled into this fix.

### WebSocket production acceptance disposition
- Source/gateway separation, Redis Streams consumer/replay, generation-scoped leases, apply-before-ACK, pending reclaim, fail-closed ownership and snapshot/replay recovery remain repository implementation evidence. Owner-supplied source snapshot verification and gateway installation callbacks remain trust boundaries requiring independent authentication of snapshot bytes, SHA-256, generation, cursor and per-gateway receipts.
- Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI result.
- Still missing owner-controlled evidence: Gate 8 secret injection/permissions/rotation/log redaction; Gate 20 real Firebase signed-token and entitlement grant/revoke/renew E2E; Gate 25 owner-host Redis TLS/CA/hostname, ACL, persistence/restart/failover, secret rotation and authenticated global snapshot/receipt alignment; Gate 30 live DB backup/restore; Gate 31 encrypted off-host backup and independent recovery-key custody; Gate 34 persistent volume UID/GID 10001/restart/disk-pressure; Gate 35 public hostname/trusted TLS/renewal; Gate 36 public HTTPS ticket exchange/WSS proxy, browser and Android WebView lifecycle/replay/resnapshot/duplicate-suppression; Gate 38 real dashboards/retention/alerts/disk pressure; Gate 39 external alert delivery, human acknowledgement and escalation.
- No public HTTPS/WSS endpoint, production Firebase project, owner-host Redis or production storage has been provisioned or verified. CI must not be used to close these gates.

### Architecture and zero-cost constraints
- Current workflow uses plain docker build on GitHub-hosted ubuntu-latest; Dockerfile base is python:3.12-alpine3.24. Exact artifact metadata is linux/amd64. ARM64 build and runtime smoke remain unverified; no multi-platform claim is made.
- Keep Redis private with strict TLS CA/hostname verification and least-privilege ACLs. Keep HTTPS ticket exchange before WSS; Firebase ID tokens must not be put in WSS URLs or raw WebSocket auth frames. Preserve separate source publisher and gateway replica roles and exact global snapshot/watermark alignment.
- ZERO COST: no deployment, host, account, resource, paid service, trial-credit dependency, production credential, Vercel/Cloudflare operation or device/Termux action. main remains untouched.

### Current indicator matrix — unchanged at 589aceadd40b3b3e10e950566081101b2dd49003

- SMA20 🟨 foundation — mean of 20 closes, first valid index 19; chart overlay/toggle/legend/latest value/stale clearing/render tests remain.
- EMA20 🟨 foundation — SMA-seeded EMA, alpha 2/21, first valid index 19; overlay/toggle/legend/latest value/stale clearing/render tests remain.
- RSI14 Wilder 🟨 foundation — 14 close changes, first valid index 14; 0–100 pane, 30/70 guides/toggle/legend/stale clearing/render tests remain.
- MACD12/26/9 🟨 foundation — MACD first valid index 25; signal/histogram index 33; pane/lines/histogram/zero guide/toggle/legend/stale clearing/render tests remain.
- Bollinger20,2 🟨 foundation — population SD, first valid index 19; upper/middle/lower overlay/toggle/values/stale clearing/render tests remain.
- Shared Indicator Hook 🟨 foundation — validated aligned snapshot; chart identity/timeframe binding/loading-error lifecycle/stale clearing/series isolation/renderer integration remain.
- Footprint 🟧 simulated/reference-gated — offline educational accumulator only; reference + reviewed blueprint required; OFF keeps ordinary candle spacing, explicit ON alone enables spaced clusters.
- Heatmap 🟥 and Liquidation Maps 🟥 — not implemented; source/data/calculation feasibility, reference/blueprint and visual implementation remain outstanding.

No indicator source/test change is included in this backend metrics correction. No indicator progress is credited; no aggregate indicator percentage is assigned without approved weights and denominator.

---
## Batch 62J-121 — exact-head WebSocket CI completion and indicator reconciliation (22 November 2026)

**Verified branch:** `phase-2/market-data-foundation`  
**Exact tested HEAD before this documentation update:** `524e78ff032f759d4475f3d396a58aa60f17b40b`  
**Exact-head CI:** Automated Tests [run 44983903576](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576) — **SUCCESS** (Test and Build job and all reported steps completed successfully); CodeQL [run 44983903708](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903708) — **SUCCESS**; Full Git History Secret Audit [run 44983903634](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903634) — **SUCCESS**.

The Automated Tests job completed frontend dependency audit, frontend unit tests and build, production bundle secret scans, Android preview-host preflight, backend dependency audit and tests, isolated Redis TLS CA/hostname enforcement fixture, synthetic SQLite outbox and metrics collector benchmarks, backend container build, container smoke with shared Redis guard and persistent CI volume, Trivy scan/report export and upload, and final dependency-audit enforcement. Artifacts produced by this exact run: synthetic outbox benchmark [14739336684](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14739336684), synthetic metrics collector benchmark [14738972814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738972814), and container vulnerability report [14738408566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738408566). The report was generated and uploaded; this note does not claim a zero-vulnerability result because the current artifact contents were not independently inspected in this batch.

**WebSocket source/test review:** the source-side publisher, per-gateway Redis Stream consumer, durable replica apply-before-ACK flow, snapshot/replay recovery and scoped single-use ticket/client transport remain present at the audited source baseline. The consumer design uses independent groups per gateway, pending-message reclaim, idempotent replica application and explicit resnapshot on stream-history gaps. The client rejects production non-HTTPS base URLs, uses WSS, exchanges Firebase credentials over HTTPS for a short-lived ticket, and validates snapshot watermarks and stream sequence. These are repository implementation facts; CI confirms covered automated paths, not production service behavior.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS hostname/certificate/reverse-proxy route; no real Firebase project token, revocation and entitlement evidence; no owner-host Redis TLS/ACL/rotation/persistence/failover evidence; no independently verified global snapshot digest and per-gateway installation receipts; and no real browser plus Android WebView lifecycle evidence. CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition is authorized.

**Indicator exact-head reconciliation:** GitHub compare from indicator implementation baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` to `524e78ff032f759d4475f3d396a58aa60f17b40b` reports six commits and only documentation paths changed (13 documentation files; no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source). Therefore this CI/documentation batch awards **zero indicator progress**. Current statuses remain: SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook — 🟨 foundation; Footprint — 🟧 simulated/reference-gated; Heatmap and Liquidation Maps — 🟥 not implemented. Keep the formula/warm-up definitions, candle identity and alignment rules, stale-series clearing, renderer/UI acceptance, and Footprint OFF standard-candle-spacing invariant unchanged. Footprint and Heatmap visual work remains blocked until user-provided reference images and a reviewed blueprint exist. No aggregate indicator percentage is assigned without an approved denominator and weights.

**ZERO COST and scope:** documentation-only reconciliation. No runtime source, tests, workflows, formulas, renderer, UI or deployment configuration changed. No host, account, resource, endpoint or paid service was created; no credentials were requested; no device/Termux work occurred; `main` was not touched. No trial-credit or paid-service dependency is introduced.

**Next sequence:** (1) preserve the green exact-head CI; (2) keep Gate 8/20/25/30/31/34/35/36/38/39 open until the listed owner-host/operator evidence is supplied; (3) pursue only zero-cost, non-provisioning checks until adult account-owner review and explicit authorization exist; (4) continue indicator implementation only within its existing approved scope and reference gates. Do not count CI, documentation or synthetic benchmarks as production acceptance.

---

## Batch 62J-120 — exact-head CI and artifact inspection (22 November 2026)

**Tested HEAD:** `c6cd331c5f9293093418bda31f93960f5aed1600`. Automated Tests #1954, CodeQL and Full Git History Secret Audit all completed SUCCESS. The Trivy JSON artifact was inspected: zero reported vulnerabilities in the scanned Alpine OS and Python package groups for the `linux/amd64` CI image. Synthetic outbox replay passed; the 899-series metrics collector benchmark exposed increasing SQLite writer-lock retries under higher concurrency. These are CI-only measurements, not production SLOs. ARM64 remains unverified; public WSS, production Redis/Firebase and browser/Android E2E remain open. No indicator source or test changed; indicator statuses and Stage 1 accounting remain unchanged. Full evidence and limitations: [Batch 62J-120](WORK_CYCLE_2026-11-22_BATCH62J120_EXACT_HEAD_CI_ARTIFACT_AND_ACCEPTANCE_AUDIT.md).

## Batch 62J-119 — WebSocket acceptance and indicator ledger exact-head reconciliation (22 November 2026)

**Verified parent HEAD:** `6d5a05d611615972d5826002442a65e74c179750` on `phase-2/market-data-foundation`. This checkpoint was created only after all three workflows for that exact SHA completed successfully.

**Exact-head CI:**
- Automated Tests #1954 — [run 44982930281](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281): **SUCCESS**. Frontend unit tests/build, backend tests, isolated Redis TLS/CA/hostname enforcement fixture, synthetic SQLite outbox and metrics benchmarks, backend container build, container smoke test using shared Redis guard and persistent volume, Trivy image scan/report export/upload, and dependency-audit enforcement all completed successfully.
- CodeQL [run 44982930379](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930379): **SUCCESS**.
- Full Git History Secret Audit [run 44982930324](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930324): **SUCCESS**.
- Trivy report artifact: [container-vulnerability-reports](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281/artifacts/14739265202). The workflow completed the configured HIGH/CRITICAL scan and uploaded the JSON report. Do not infer a zero-vulnerability result without reviewing the artifact contents.

These results verify the repository workflow and its CI service topology only. The CI Redis instance, ephemeral runner volume, and container smoke are not the intended OCI host or production Redis service.

**WebSocket repository evidence:** source-side publisher and gateway runtime factories, durable SQLite outbox, atomic snapshot/watermark primitives, Redis Streams publisher/consumer, per-gateway consumer groups, replica snapshot installation checks, fail-closed runtime construction, ticket authentication/renewal, reconnect/replay and client failure-matrix tests are present in the audited source. The latest CI validates the covered repository paths. The default FastAPI app intentionally does not invent owner-specific publisher/replica factories or trust snapshot receipts; those must be injected from a verified owner-controlled host setup.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS endpoint, production Firebase token/entitlement evidence, owner-host Redis TLS/ACL/persistence/rotation/failover, authenticated global snapshot manifest and per-gateway installation receipts, or real browser + Android WebView lifecycle evidence has been supplied. A successful CI container smoke cannot close those host/client gates.

**ZERO COST boundary:** no OCI account or resource was created, no deployment or public endpoint was started, no paid resource or trial-credit dependency was introduced, no credentials were requested, no device/Termux operation occurred, and `main` was not touched. OCI remains a conditional candidate subject to actual Always Free eligibility and adult account-owner approval.

**Indicator disposition — no source change and no progress credit:** the source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains the calculation baseline. The comparison through parent HEAD `6d5a05d611615972d5826002442a65e74c179750` is documentation-only; no indicator formula, hook, chart renderer, UI, or indicator test source changed. SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps remain 🟥 not implemented. Formula definitions, warm-up indices, numerical safeguards, data identity, stale-series invariants, UI acceptance and reference prerequisites remain in the canonical audit and ledger. Aggregate indicator percentage remains unscored without approved weights and denominator.

**Project accounting:** Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI or documentation-only checkpoint. No progress is awarded from CI alone.

**Next zero-cost sequence:** preserve the green exact-head CI; finish ARM64 build/configuration readiness without provisioning; have the adult account owner verify OCI eligibility, capacity and all possible charges; only then, with explicit authorization, consider an Always Free-only host. Collect actual host and client evidence for Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Close Gate 10 only after evidence review and operator sign-off.

---

## Batch 62J-117 — exact-head WebSocket CI and indicator progress reconciliation (22 November 2026)

## Batch 62J-117 — exact-head CI and indicator ledger reconciliation (22 November 2026)

**Verified branch HEAD:** `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02` (`phase-2/market-data-foundation`). The source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains valid: GitHub comparison from that baseline to this HEAD contains documentation-only changes, with no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source changes.

**Exact-head workflows on `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02`:**
- Automated Tests [run #1952 / 44981803844](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803844): **SUCCESS**; all 61 reported workflow steps completed successfully, including frontend tests/build, backend tests, Redis TLS CA/hostname fixture, backend container build, persistent-volume Redis smoke test, image scan/report and dependency audits.
- CodeQL [44981803808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803808): **SUCCESS**.
- Full Git History Secret Audit [44981803851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803851): **SUCCESS**.
- These are exact-head repository CI/security results. They do not constitute production Firebase, owner-host Redis, public WSS, browser or Android WebView acceptance.

**Indicator disposition — unchanged, zero progress credit:** SMA20 🟨, EMA20 🟨, RSI14 Wilder 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧 (synthetic/reference-gated), Heatmap 🟥, Liquidation Maps 🟥. The five calculation foundations and their first-valid indices remain as recorded in the canonical audit; none is accepted as a finished visible chart feature. The chart integration, controls, legends/current values, pane/overlay rendering, stale-series clearing and lifecycle/render acceptance remain outstanding as listed per study. Footprint OFF must preserve ordinary candle spacing; only explicit ON may switch to spaced clusters. Footprint, Heatmap and Liquidation Maps visual work remains gated by user-provided reference image(s) and reviewed blueprint.

**Accounting:** no indicator or project completion credit is awarded by WebSocket CI or this documentation reconciliation. Aggregate indicator percentage remains unscored without approved weights and denominator. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed. Gates 20, 25 and 36 remain open for real Firebase/entitlement evidence, owner-host Redis TLS/ACL/persistence/recovery and public HTTPS/WSS proxy plus browser/Android acceptance. No deployment or production readiness is claimed.

**Cost/scope:** ZERO COST. No paid hosting/provider, OCI provisioning, credentials, deployment, Termux/device action or `main` modification.

Full source-backed formula, numerical-safety, data-lineage and UI acceptance matrix: [INDICATOR_PROGRESS_AUDIT_2026-11-22.md](INDICATOR_PROGRESS_AUDIT_2026-11-22.md). WebSocket production blockers and evidence matrix: [WORK_CYCLE_2026-11-22_BATCH62J117_EXACT_HEAD_WEBSOCKET_AND_INDICATOR_RECONCILIATION.md](WORK_CYCLE_2026-11-22_BATCH62J117_EXACT_HEAD_WEBSOCKET_AND_INDICATOR_RECONCILIATION.md).

---

## Batch 62J-115 — complete source-backed indicator progress audit (22 November 2026)

- Audited baseline: `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` on `phase-2/market-data-foundation`.
- Added `docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md` as the canonical detailed audit; refreshed the current checkpoint in `docs/INDICATOR_PROGRESS_LEDGER.md` and this current project-progress file.
- Verified: SMA20, EMA20, Wilder RSI14, MACD12/26/9 and Bollinger20,2 have tested calculation foundations; none is a completed visible chart feature. The shared backend-only hook exists but is not wired into `CandlestickChart.tsx`. The chart still creates only one candlestick series.
- Calculation suite contains 15 cases. Baseline frontend CI passed 255/255 tests across 29 files; backend passed 1,294 with 1 skipped. Automated Tests, CodeQL and Full Git History Secret Audit passed on baseline.
- Footprint remains a synthetic offline educational accumulator; no real order-flow source or visual cluster renderer. Heatmap and Liquidation Maps are not implemented.
- Documented formula definitions, first-valid indices, numerical safety, exact data identity, stale-series rules, prefix-causality, proposed overlay/pane scope, UI acceptance, reference prerequisites and roadmap gates.
- No formula, hook, chart, visual UI, runtime or test source changed. **No indicator progress credit.**
- Official project remains Stage 1, 30/40 = 75% provisional. Stage 4 visual implementation is not authorized during Stage 1. Aggregate indicator percentage remains unscored without approved weights/denominator.
- ZERO COST; no deployment, paid service, production credential, Termux/device action or `main` modification.
- Exact-head CI for this documentation commit must be checked before declaring this docs batch CI-accepted.

Full detail: [INDICATOR_PROGRESS_AUDIT_2026-11-22.md](INDICATOR_PROGRESS_AUDIT_2026-11-22.md).

---

## Batch 62J-104 — five remaining Gate 10 tracks and exact-head CI acceptance (22 November 2026)

- Audited source/test HEAD: `a18e963d4cd067fe22ec8d03c653418e003c7fde`.
- Exact-head Automated Tests [44970436441](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436441): **SUCCESS**; frontend 255/255 across 29 files; backend **1,289 passed in 51.98 s**. The five new Batch 62J-103 tests are individually visible as PASSED in the workflow log.
- Exact-head CodeQL [44970436417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436417): **SUCCESS** (Python + JavaScript/TypeScript). Full Git History Secret Audit [44970436377](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436377): **SUCCESS**.
- Automated Tests also passed frontend/backend dependency audits, frontend source/bundle secret scans, backend container build, shared Redis guard/persistent-volume smoke, configured container scan and report export.
- Gate 20: repository identity/ticket/entitlement failure matrix verified; live Firebase signed-token E2E and threat-model owner review remain.
- Gate 25: Redis TLS/ACL guards, atomic ticket/lease operations, exact ticket TTL/NX/digest semantics and CI shared Redis smoke verified; owner-host Redis TLS/ACL, snapshot receipt and persistent failover remain.
- Gate 31: encrypted SQLite backup, AES-256-GCM/PBKDF2, fresh-path restore, content/schema hashes, wrong-key/tamper/truncation and full application restore drill tests verified; off-host copy, offline key custody and owner-host key-recovery restore remain.
- Gate 36: WebSocket lifecycle/auth/replay/renewal and frontend client tests verified; public HTTPS/WSS, reverse proxy, live Redis, cross-instance and browser/Android WebView acceptance remain.
- Gate 38: 899-series/900 cap, same-host SQLite collector, failure isolation and CI benchmark verified; owner-host volume/perimeter/token lifecycle/dashboard/notification/recovery drill remain. Latest synthetic 16-worker startup-staggered benchmark: 512/512 flushes, 899/899 series, 0 retries, SQLite integrity `ok`; peak DB+WAL+SHM 5,744,952 bytes; post-checkpoint 1,126,400 bytes. CI-runner only, not production SLO/host evidence.
- Gate 10 remains **0/10 formally closed**. 🟨🟩 host/operator-only: Gates 8, 30, 34, 35, 39. 🟧 integration/acceptance: Gates 20, 25, 31, 36, 38.
- Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- Indicator implementations unchanged; no indicator progress credit. Full current formulas, warm-up indices, prerequisites and remaining visible work are in `docs/INDICATOR_PROGRESS_LEDGER.md`.
- Full five-track evidence and remaining acceptance requirements: `docs/WORK_CYCLE_2026-11-22_BATCH62J104_FIVE_REMAINING_GATES_EXACT_HEAD_AUDIT.md`.
- ZERO COST. No deployment, paid service, production credential, Termux/device operation or `main` modification.

---

## Batch 62J-103 — WebSocket ticket renewal failure matrix (22 November 2026)

- Active branch: `phase-2/market-data-foundation`; final source/test HEAD: `a18e963d4cd067fe22ec8d03c653418e003c7fde`.
- Test-only change set relative to checkpoint `d45290b8b95e5bbe73e2a993cd3fdaf497a8afc3`: `backend/tests/test_api.py` +86 lines; `backend/tests/test_shared_guard.py` +47 lines; zero deletions in the final diff. Total +133 lines.
- Two new FastAPI/WebSocket renewal tests: invalid/expired renewal ticket closes 4401; ticket-store/Redis outage during renewal closes 1013 without exposing internal error or credential text.
- Three new shared-guard ticket tests: SHA-256 digest-only key with exact 90-second TTL and NX write; corrupt stored JSON is consumed and rejected; two concurrent in-memory consumers yield exactly one subject and one `None`.
- Existing real-Redis single-use integration test now checks `PTTL`: remaining ticket TTL must be positive and no greater than 90,000 ms. Existing tests already covered cross-subject renewal rejection and entitlement revocation during renewal; duplicate candidate tests were removed rather than duplicating coverage.
- No production source, WebSocket protocol, Firebase identity, Redis runtime or market-data code changed.
- **CI acceptance was subsequently verified for this exact source/test HEAD** by Batch 62J-104: Automated Tests [44970436441](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436441) SUCCESS (frontend 255/255; backend 1,289 passed), CodeQL [44970436417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436417) SUCCESS, and Full Git History Secret Audit [44970436377](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436377) SUCCESS. All five new tests were individually PASSED.
- Gate 20 repository evidence improved (renewal invalid-ticket and store-outage handling); Gate 25 improved (ticket TTL, digest key, NX and corrupt-payload behavior); Gate 36 improved (renewal transport failure closure). No gate is closed.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/operator-only: Gates 8, 30, 34, 35, 39. 🟧 integration/acceptance: Gates 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- No indicator formula, calculation, data contract, shared hook, renderer, chart UI or indicator test changed. No indicator progress credit is awarded; see the full matrix in `docs/INDICATOR_PROGRESS_LEDGER.md`.
- ZERO COST: no deployment, Vercel/Cloudflare operation, paid provider, production credential, Termux/device operation or `main` modification.

---

## Batch 62J-98 — WebSocket + Gate 25 gateway runtime + Gate 38 + Gate 36 (21 November 2026)

- Verified source/test HEAD: `b4325216d1293d3c747978fc45218bfe1fd1d79f` on `phase-2/market-data-foundation`.
- Added `backend/app/ohlcv_redis_gateway_runtime.py`, six regression tests in `backend/tests/test_ohlcv_redis_gateway_runtime.py`, and gateway env placeholders in `backend/.env.example`.
- Gateway builder validates authenticated installer result, durable replica checkpoint, source ID, snapshot generation, high-water cursor and SHA-256 before Redis client creation. Production requires rediss TLS certificate and hostname verification. Runtime is opt-in and requires an owner-supplied authenticated snapshot installer.
- Exact-head Automated Tests [44916614912](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912): SUCCESS; 255 frontend tests across 29 files, 1,277 backend tests in 42.72s. Container build, Redis ACL/AOF persistent-volume smoke, frontend build/secret scans and dependency audits succeeded.
- Exact-head CodeQL [44916614959](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614959): SUCCESS. Full Git History Secret Audit [44916614967](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614967): SUCCESS.
- Trivy artifact [14711468367](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912) was downloaded and parsed: 0 HIGH/CRITICAL vulnerabilities in Alpine OS and Python package targets.
- Gate 38 artifact [14712222307](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912): 899/899 series, 512/512 staggered flushes, 16/16 workers, SQLite integrity ok, 0 retries. Staggered p95 18.34ms / p99 88.57ms / max 259.74ms. Simultaneous 16-thread p95 376.08ms / p99 796.15ms / max 1,406.30ms / 78 retries. Synthetic staggered reductions: p95 95.12%, p99 88.88%, max 81.53%. CI model only, not production SLO.
- Four-process benchmark: 128/128 flushes, 899 series, integrity ok, one retry; p95 40.43ms, p99 239.10ms. Cross-host SQLite is not claimed.
- WebSocket source/consumer failure-matrix scope remains complete for repository CI. Production WSS still requires owner-host Redis TLS/ACL, snapshot receipts, public HTTPS/WSS reverse proxy and browser/Android WebView acceptance.
- Gate 25 source-side gateway runtime readiness improved; Gate 25 remains 🟧 pending live Redis, host credentials, ACL/network, persistence/failover and authenticated snapshot distribution. Gate 36 remains 🟧 pending public HTTPS/WSS and device acceptance. Gate 38 remains 🟧 pending central monitoring, host volume, retention/backup and operator recovery.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/operator only: Gates 8, 30, 34, 35, 39. 🟧 integration/acceptance: Gates 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored.
- Indicators unchanged; no credit: SMA20 🟨 (index 19), EMA20 🟨 (index 19), RSI14 🟨 (index 14), MACD12/26/9 🟨 (MACD index 25, signal/histogram 33), Bollinger20,2 🟨 (index 19), Shared Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
- Initial candidate `7bf14593ddfa5d776245bb632896a8277635f9e0` had a syntax error caught by CI; it was corrected in `b4325216d1293d3c747978fc45218bfe1fd1d79f`. The final exact-head workflow passed.
- ZERO COST. No deployment, paid service, production credentials, Vercel/Cloudflare operation, Termux/device operation or `main` modification.

---

## Batch 62J-97 — production-staggered metrics benchmark (21 November 2026)

- Source/test HEAD: `8deeba557f7be6ea5cb66fb0bfb55955aafc5a41` on `phase-2/market-data-foundation`; docs-only descendants now carry the ledger update.
- Exact-head Automated Tests [44914991306](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991306): **SUCCESS**. CodeQL [44914991295](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991295): **SUCCESS**. Full Git History Secret Audit [44914991439](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991439): **SUCCESS**.
- Trivy artifact [14710634254](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991306) was downloaded and parsed: **0 vulnerabilities** in Alpine OS and Python package targets, including zero HIGH/CRITICAL.
- The benchmark mirrors production's UUID-prefix modulo-15 startup phase and 15-second flush cadence. Staggered 16-thread profile: **512/512 flushes**, **899/899 series**, 16/16 workers, SQLite integrity `ok`, **0 retries**, p95 **19.98 ms**, p99 **86.72 ms**, max **120.73 ms**.
- Simultaneous 16-thread stress: 512/512 flushes, p95 371.91 ms, p99 610.31 ms, max 1,922.15 ms, 68 retries. Staggered profile reduced p95 94.63%, p99 85.79%, max 93.72% in this synthetic CI comparison. Tail latency is not eliminated; the staggered p99 remains 86.72 ms.
- Separate four-process profile: 128/128 flushes, 899 series, integrity `ok`, p95 85.67 ms, p99 237.86 ms, one retry. Cross-host SQLite is not claimed.
- Staggered peak DB+WAL+SHM was 3,169,952 bytes; post-checkpoint total 1,126,400 bytes. Snapshot payload 105,586/262,144 bytes (40.28%). CI-runner measurements are not production capacity/SLO guarantees.
- Gate 38 remains 🟧 OPEN pending owner-host volume/retention/backup, access control, dashboard visibility and recovery acceptance.
- WebSocket repository-side automated protocol/failure-matrix scope remains complete; production WSS remains host-gated. No WebSocket protocol/relay/auth/replay code changed in this batch.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/operator verification only: Gates 8, 30, 34, 35, 39. 🟧 additional integration: Gates 20, 25, 31, 36, 38.
- Indicators unchanged; no progress credit. SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6, overall project percentage and aggregate indicator percentage remain unscored.
- ZERO COST; no deployment, Vercel/Cloudflare operation, paid service, production credentials, Termux/device operation or `main` modification.

---

## Batch 62J-87 — bounded SQLite writer-lock acquisition (21 November 2026)

- Exact source/test predecessor `73a19e5db54b44d1d07caa038ec567d31d19a0a8`: Automated Tests [44902861326](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902861326) **FAILED** at the 16-worker benchmark during `BEGIN IMMEDIATE` with `sqlite3.OperationalError: database is locked`. This was a writer-transaction contention failure, distinct from the earlier schema-bootstrap collision. CodeQL [44902861325](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902861325) and Full Git History Secret Audit [44902861332](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902861332) passed on that predecessor.
- Added bounded retry/backoff around SQLite writer-lock acquisition before transaction work. It retries only lock errors, for at most eight attempts, retaining the existing 250 ms busy timeout. Corruption, integrity errors and other non-lock failures are not suppressed. The transaction body remains atomic.
- `flush()` now reports the number of internal lock retries; benchmark aggregates those retries into its evidence output.
- Added a regression test that holds a write lock, releases it after 350 ms, verifies the flush succeeds, verifies at least one retry was recorded, and confirms the counter delta was applied once.
- Source/test commit: `c95a9a19091a5881136144491937073ba7fcb767`. Documentation commit follows; exact-head Automated Tests, CodeQL and secret-history audit are pending. No pass is claimed yet.
- The benchmark remains 899 logical series, 1/4/16 concurrent Python worker threads, 32 flushes per worker, and 256 KiB payload cap. Separate OS-process contention remains untested.
- Gate 38 remains 🟧 OPEN. Disk-full/read-only failure behavior, app-level HTTP/WebSocket isolation, retention/backup and owner-host/operator acceptance remain.
- WebSocket wire protocol, auth, replay, snapshot and Redis data path unchanged; production WSS remains host-gated.
- Indicator formula/hook/renderer/UI unchanged; no indicator progress credit. Gate 10 remains 0/10 formally closed; Stage 1 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST. No deployment, Vercel/Cloudflare operation, paid service, production credential, Termux/device operation or `main` modification.

---

## Batch 62J-86 — SQLite schema-bootstrap contention hardening (21 November 2026)

- Prior full-cardinality attempt at exact HEAD `c2f9b99fc05dd17050674a39317bd5aa601e6182`: Automated Tests run [44902446746](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902446746) **FAILED** in the metrics benchmark because concurrent worker connections collided during repeated SQLite schema initialization (`database is locked`). This failure is retained as evidence; it is not reported as a pass.
- CodeQL [44902446747](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902446747) and Full Git History Secret Audit [44902446769](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902446769) completed SUCCESS on that prior exact head.
- Hardened `SQLiteMetricsCollector._connect()`: schema initialization now runs once per collector instance behind a thread lock, and transient SQLite lock errors during initialization receive bounded retry/backoff. Non-lock errors and corruption still fail closed. Subsequent connections no longer repeat the DDL script.
- Changed the 1/4/16-thread benchmark so each simulated worker owns its own collector instance against the shared SQLite file, matching the per-process collector lifecycle more closely.
- Added a regression test in which four independent collector instances initialize and write to the same database concurrently; the test verifies all worker deltas aggregate without loss.
- Current source/test HEAD: `2c584fcef5a20b21ec2850692ab51e28341c4eff`. Exact-head Automated Tests, CodeQL and secret-history audit are pending; no pass is claimed yet.
- The 899-series target, 256 KiB payload limit, 250 ms SQLite busy timeout, 650,000 aggregate-row ceiling and zero-cost scope are unchanged. The full-cardinality benchmark is not considered accepted until the new exact-head run passes.
- Gate 38 remains 🟧 OPEN. Separate OS-process benchmark, physical read-only/disk-full behavior, app-level HTTP/WebSocket isolation and owner-host acceptance remain.
- WebSocket protocol/auth/replay/snapshot/Redis code remains unchanged. Production WSS acceptance remains host-gated.
- Indicator calculations and renderers remain unchanged; no indicator credit. Gate 10 remains 0/10 formally closed; Stage 1 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST. No deployment, Vercel/Cloudflare operation, paid service, production credential, Termux/device operation or `main` modification.

---

## Batch 62J-85 — full-cardinality Gate 38 benchmark (21 November 2026)

- Source/test HEAD: `de104f388a4dd5c214567e911933d4c341bff570` on `phase-2/market-data-foundation`; exact-head CI is pending and is not claimed as passing.
- Replaced the previous 12-logical-series fixture with 899: 127 routes × 6 HTTP status classes = 762 request series; 127 latency histograms; 10 WebSocket counters/classes.
- Benchmark still covers 1/4/16 concurrent Python threads. It now verifies the full 899-series aggregate, exact worker/request totals, serialized payload size against 256 KiB, and SQLite integrity.
- Added a SQLite write-rejection rollback/retry regression. This is a transaction failure simulation, not a physical disk-full or read-only-volume test.
- Capacity arithmetic: 899 × 672 fifteen-minute buckets = 604,128 aggregate rows; 650,000-row cap leaves 45,872 rows (7.06% of cap). This excludes worker/checkpoint rows and SQLite/WAL/index/filesystem overhead; it is not a byte budget.
- Separate-process contention, read-only/disk-full, app-level traffic-isolation and owner-host acceptance remain open. Gate 38 remains 🟧.
- WebSocket wire protocol, authentication, replay, snapshot and Redis behavior unchanged. Production WSS host acceptance remains open.
- Indicators unchanged; no progress credit. Gate 10 remains 0/10 formally closed; Stage 1 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST; no deployment, paid service, production credentials, Termux/device operation or `main` modification.

---

## Batch 62J-84 — Gate 38 failure-path tests and SQLite worker benchmark (21 November 2026)

- Source/test HEAD: `92119a8dc05690e6492aab160662c9e36c839cad` on `phase-2/market-data-foundation`; `main` untouched.
- Exact-head Automated Tests [44900892637](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892637): **SUCCESS, 35/35 workflow steps**. Backend pytest: **1,265 passed in 36.46s**. The workflow also completed frontend tests/build, backend dependency audit, container build, Redis ACL/persistent-volume smoke, Trivy scan and report upload.
- Exact-head CodeQL [44900892567](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892567): **SUCCESS**. Full Git History Secret Audit [44900892606](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892606): **SUCCESS**.
- Added collector regression tests for concurrent worker commits, bounded recovery after SQLite lock contention, and safe rejection of a corrupt metrics database. Existing transaction rollback, idempotence, stale-worker, retention, generation/tombstone and monotonic timestamp tests remain.
- Added `backend/scripts/benchmark_metrics_collector.py`, a local-only synthetic 1/4/16-worker thread benchmark, plus a CI artifact. At 32 flushes per worker, observed p99 flush latency was 2.145ms / 19.108ms / 78.978ms; no retries occurred. Peak total DB+WAL+SHM bytes were 81,920 / 1,293,232 / 4,284,304.
- **Benchmark boundary:** this initial profile has only 12 logical series, not the collector's 899-series full budget; worker concurrency is Python threads, not separate OS processes. It is a baseline only, not a maximum-cardinality capacity test, a production-host estimate or a justified byte ceiling. No database byte limit is set from it.
- Gate 38 remains 🟧 OPEN. Exact-head repository CI is verified; full-cardinality benchmark, disk-full/read-only isolation, owner-host persistence/restore/retention, operator access and recovery acceptance remain.
- WebSocket protocol, authentication, replay, snapshot ordering, Redis guard and market-data payloads were not modified.
- Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**; Stages 2–6 and overall percentage remain unscored.
- Complete indicator ledger: SMA20 🟨 (20-close mean, first valid index 19); EMA20 🟨 (SMA-seeded, α=2/21, index 19); RSI14 🟨 (Wilder, index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram index 33); Bollinger20,2 🟨 (mean ±2 population SD, index 19); Shared Indicator Hook 🟨; Footprint 🟧 (reference image/approved blueprint and ON-only cluster renderer pending); Heatmap 🟥; Liquidation Maps 🟥. No indicator source or renderer changed; no indicator credit awarded.
- Invariants: warm-up `null`, candle-index alignment, no future-candle repaint, stale-series clearing on identity/timeframe changes, and Footprint OFF preserving ordinary candle spacing.
- ZERO COST: no deployment, Vercel/Cloudflare operation, paid provider, production credential request, Termux/device operation or `main` modification.

---

## Batch 62J-83 — Gate 38 collector hardening and CI baseline (21 November 2026)

- Active branch remains `phase-2/market-data-foundation`; pre-change HEAD `b1e21f552182a720400cd9a2d276705834a41358`.
- Exact-head Automated Tests run [44898947136](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44898947136) completed SUCCESS (33/33 steps); CodeQL [44898947150](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44898947150) SUCCESS; Full Git History Secret Audit [44898947186](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44898947186) SUCCESS.
- Source review found a worker-generation capacity edge case: 256 historical process checkpoints could block a replacement worker before the seven-day retention expired. The hardening change evicts only the oldest stale checkpoints under capacity pressure, records seven-day retired-worker tombstones to reject a resumed evicted process ID, and keeps active worker limits enforced.
- Snapshot reads now hide buckets outside the seven-day window even when no new flush has occurred. Aggregate-capacity evictions are counted and exposed to the protected metrics response; timestamp regressions are rejected.
- New tests cover stale-generation eviction/tombstones, the 16-live-worker limit, retention filtering without a subsequent flush, and worker timestamp regression. Exact-head CI for source commit `e98bf7acda841ae4045d258b6d3b2fe774205239` completed SUCCESS: Automated Tests [44899788672](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44899788672), CodeQL [44899788812](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44899788812), and Full Git History Secret Audit [44899788701](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44899788701).
- Gate 38 remains 🟧 OPEN: repository implementation is present, but host volume behavior, measured database byte budget, operator access/retention and incident recovery acceptance remain outstanding. No cross-host support is claimed.
- WebSocket protocol, auth, replay, snapshots and market-data payload behavior are unchanged. The collector remains best-effort telemetry and cannot delay/fail market-data request paths.
- Indicator formulas, renderers, UI and tests are unchanged; no indicator progress credit. Stage 1 remains 30/40 = 75% provisional. Gate 10 remains 0/10 formally closed.
- ZERO COST: no deploy, Vercel/Cloudflare operation, Termux, paid service, production credential request or `main` modification.

---



## Batch 62J-82 — exact-head CI reconciliation and Gate 38 capacity review (21 November 2026)

- Exact HEAD `c3577d7174ce5873502ebd8df7a57f27447a296b` has all three workflows completed SUCCESS: Automated Tests [44897164887](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44897164887), CodeQL [44897164916](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44897164916), and Full Git History Secret Audit [44897164908](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44897164908).
- Automated Tests included frontend tests/build, backend tests, SQLite outbox benchmark/report, backend dependency audit, container build, Redis persistent-volume smoke, Trivy scan and report export/upload; workflow conclusion is SUCCESS.
- Gate 38 blueprint clarified the crash-loss window (up to one nominal 15-second flush interval plus scheduler delay), fixed series budget, 672-bucket retention math, and 650,000 logical-row ceiling. The byte ceiling remains benchmark-derived, not guessed.
- Corrected interpretation: 1,500x compares periodic snapshots with a hypothetical per-request persistence design. Current metrics are in-memory and do not persist each request.
- No runtime source changed. Gate 38 remains 🟧 pending explicit blueprint approval, implementation/tests, host volume and operator acceptance. Gate 10 remains 0/10 formally closed.
- Indicator formulas, visual states and data contracts are unchanged. No indicator progress credit is awarded.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project remain unscored. ZERO COST; no deploy, paid service, Termux, production credential or `main` modification.

---
## Latest work cycle — Batch 62J-81 (21 November 2026)

- Reconciled exact branch head: 3eadda21f795abe5af195eedf0c81727d31f6436; branch compare reports identical (0 ahead / 0 behind).
- Exact-head Automated Tests run 44895224507, CodeQL run 44895224465 and Full Git History Secret Audit run 44895224498 all completed SUCCESS.
- Gate 38 architecture blueprint added: dedicated local SQLite metrics DB, worker-scoped 15-second snapshots, transactional delta checkpoints, 15-minute aggregates, 90-second live-worker expiry, and 7-day age retention plus hard capacity ceiling. Supports multiple workers on one host/local persistent volume only; no cross-host claim.
- No runtime source changed. Implementation is held behind the required blueprint review/approval gate. Existing Redis security-guard client and market-data registry DB are not repurposed for telemetry.
- Gate 38 remains 🟧 OPEN. Gate 10 remains 0/10 closed; Gate 8/30/34/35/39 remain 🟨🟩 host/owner verification only; Gate 20/25/31/36/38 remain 🟧.
- Complete indicator ledger remains unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Hook 🟨, Footprint 🟧 simulated/gated, Heatmap 🟥, Liquidation Maps 🟥. No indicator credit is awarded.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project remain unscored. ZERO COST; no deployment, paid service, Termux/device operation, production credential or main modification.

---

## Latest work cycle — Batch 62J-80 (21 November 2026)

- Corrected WebSocket lifecycle telemetry so accept/close events are counted only after downstream ASGI send succeeds.
- Added regression coverage for accept-send and close-send transport failures; the finally path must return active connections to zero and must not count unsent frames.
- This is observability correctness, not a WebSocket protocol/data-path change. Gate 38 remains 🟧 because metrics remain process-local without central aggregation, durable retention or independent operator notification.
- Indicator status is unchanged; the complete indicator ledger and formulas remain in INDICATOR_PROGRESS_LEDGER.md. No visual progress is credited.
- Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35, 39 remain 🟨🟩 host/owner verification only; Gates 20, 25, 31, 36, 38 remain 🟧.
- ZERO COST; no deploy, paid service, production credentials, Termux/device operation, Vercel/Cloudflare operation or main modification.

---

## Latest work cycle — Batch 62J-79 (21 November 2026)

- Added bounded process-local WebSocket lifecycle metrics for the exact `/ws/market-data` ASGI route: starts, active, completed, accepted, peer disconnects, five close-code classes and cumulative duration.
- The observer records lifecycle metadata only. It does not inspect payloads, auth tickets, authorization headers, account IDs, IP addresses, symbols or query strings. It is returned only through the existing bearer-token-protected `/internal/metrics` endpoint.
- New tests cover accepted/closed lifecycle, peer disconnect and route isolation. WebSocket wire protocol and data path are unchanged.
- Source/test HEAD: `2274f9adc5ac9907ea508800a2d962d9a7c14a84`. Frontend tests, backend tests and CodeQL have passed in exact-head run [44894262277](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262277) / [44894262276](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262276); full workflow still has container/build/audit steps pending. Secret-history audit [44894262301](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262301) passed. Do not claim full CI acceptance yet.
- Gate 38 improves at repository level but remains 🟧 OPEN: telemetry is process-local; central collector, multi-worker aggregation, dashboard, durable retention and independent operator notification remain absent.
- WebSocket automated protocol/failure-matrix scope remains complete for the defined CI scope. Production acceptance remains blocked by missing owner-controlled host, production Redis topology, snapshot receipts, public HTTPS/WSS and real browser/Android WebView acceptance.
- Indicator formulas and visual completion are unchanged. Full indicator status is in `INDICATOR_PROGRESS_LEDGER.md`; no renderer credit is awarded by this observability batch.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/owner verification only: Gates 8, 30, 34, 35, 39. 🟧 additional integration: Gates 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project remain unscored. ZERO COST; no deployment, Termux/device command, production credentials or `main` modification.

---

## Latest work cycle — Batch 62J-78 (21 November 2026)

- SMA numeric audit found and corrected a second-order cancellation case after Batch 62J-77: a small representable residual between `MAX_VALUE` and `-MAX_VALUE` was lost by ordinary normalized reduction.
- The feature branch now uses an error-free floating-point expansion only for materially cancelling normalized windows, preserving the fast path for ordinary price windows. SMA and Bollinger middle-band means share the stable helper; forward/reverse-order regression tests cover the residual case.
- First exact-head CI (run [44893124624](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44893124624)) caught a missing normalized vector used by the Bollinger variance pass. The vector is restored in source/test HEAD f70f0bcfe2208b4fbfb37440fe8dc3b740e8fbcc. Frontend unit tests/build, CodeQL and full Git-history secret audit have passed on that exact HEAD; backend suite and APK build are still running. This is not yet a verified release.
- No visual indicator credit is awarded: SMA20 stays 🟨 foundation; all other indicator statuses remain as shown in the full ledger below.
- WebSocket repository-side failure-matrix scope remains complete; public WSS/production acceptance remains externally blocked.
- Gate 10 remains 0/10 formally closed. 🟨🟩 host/owner verification only: 8, 30, 34, 35, 39. 🟧 additional integration: 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project remain unscored. ZERO COST; no deploy, no paid service, no Termux/device command, and `main` remains untouched.

## Latest engineering checkpoint — Batch 62J-77 (21 November 2026)

**Branch:** phase-2/market-data-foundation  
**Source/test HEAD:** e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8

- Exact-head Automated Tests [44877470829](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470829): **SUCCESS** — frontend **253/253 tests across 29 files**; backend **1,249 passed in 48.11s**. Frontend build, frontend source/bundle secret scans, npm audit (0 vulnerabilities), backend dependency audit (no known vulnerabilities), bounded outbox benchmark, backend container build, Redis shared-guard/persistent-volume smoke, Trivy container scan and report export/upload all completed.
- Exact-head CodeQL [44877470826](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470826): **SUCCESS**.
- Exact-head Full Git History Secret Audit [44877470841](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470841): **SUCCESS**.
- Exact-head Android debug APK build [44877470773](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470773): **SUCCESS**. Artifact ID 14696311954, expires 28 November 2026. APK size 3,877,454 bytes; SHA-256 cc7288ac77fa0c28f2cfeebba7f9703003f15a970b1575618e1998548887ed7a. CI build does not equal physical-device acceptance.
- Batch 62J-77 fixes SMA intermediate overflow: each rolling window uses scale-normalized mean calculation. Representable averages such as mean(MAX_VALUE, MAX_VALUE) now return MAX_VALUE instead of throwing because a raw sum overflowed. Regression coverage includes extreme same-sign values and cancellation. Calculation remains candle-index aligned and warm-up nulls unchanged.
- CI caught two issues in the first attempt: an old test still expected the prior SMA overflow failure, and a relative-large-value assertion used an absolute tolerance inappropriate at MAX_VALUE scale. Both tests were corrected; the exact final source/test commit passed all checks.
- Gate 31 remains 🟧 OPEN: encrypted local backup exists, but no independent no-cost off-host destination or separate recovery-key custody is configured.
- Gate 38 remains 🟧 OPEN: bounded process-local HTTP metrics and local incident journal exist; central multi-worker collector/dashboard, WebSocket metric aggregation, durable metric/log retention and independent operator notification remain absent.
- Gate 10: **0/10 formally closed**. 🟨🟩 host/owner-verification-only: Gates 8, 30, 34, 35 and 39. 🟧 additional integration remains: Gates 20, 25, 31, 36 and 38. No gate is marked passed.
- Stage 1 remains **30/40 criteria = 300/400 ticks = 75% provisional**. Stages 2–6 and overall project percentage remain unscored because approved weights/denominators are absent.
- Indicator statuses: SMA20 🟨; EMA20 🟨; RSI14 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; shared indicator hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥. Numerical correctness work is not visual completion.
- ZERO COST: no paid hosting, deployment, production credentials, Vercel/Cloudflare operation, Termux/device operation or main modification.




---

# DEZZTA CHART — CURRENT PROJECT CONTROL DASHBOARD

**Checkpoint:** 21 November 2026 — Batch 62J-77, normalized SMA overflow correction and exact-head CI acceptance  
**Active branch:** `phase-2/market-data-foundation`  
**Latest source/test HEAD:** `e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8`

## Project stage dashboard

| Stage | State | Verified progress |
|---|---|---:|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 ACTIVE / provisional | **75%** — 30/40 criteria |
| Stage 2 — Market Data & Provider Integration | ⬜ NOT SCORED | No approved denominator |
| Stage 3 — Advanced Trading & Order Flow | ⬜ NOT SCORED | No approved denominator |
| Stage 4 — Charting & Technical Indicators | ⬜ NOT SCORED | No approved denominator |
| Stage 5 — Alerts, Automation & Workspace | ⬜ NOT SCORED | No approved denominator |
| Stage 6 — Release, Operations & Scale | ⬜ NOT SCORED | No approved denominator |

**Overall project:** NOT SCORED. M1–M8 weights and the overall acceptance denominator have not been approved. The historical 20.9% figure is not a current weighted result.

## Stage 1 / Gate 10

**Stage 1:** 30/40 criteria = 300/400 ticks = **75% provisional**. Remaining: 10 criteria / 100 ticks. Source changes, documentation and CI alone do not award production-acceptance ticks.

**Gate 10:** <badge color="warning">0/10 formally closed</badge> — Gates 8, 30, 34, 35 and 39 are 🟨🟩 host/owner-verification-only; Gates 20, 25, 31, 36 and 38 remain 🟧 OPEN for additional provider/host/device integration. A gate turns 🟩 only after complete acceptance evidence is reviewed.

**Meaning of host/owner verification only:** this is not the same as opening the Android APK. It means the repository-side implementation and CI checks are complete for that gate, but evidence must be collected from the real owner-controlled server, storage, certificate/provider account or operator process. For Gate 36, a separate Android/browser acceptance test will be needed only after a real public HTTPS/WSS endpoint exists. No APK test can substitute for Redis TLS, host secrets, backup storage, persistent volumes or operator recovery evidence.

| Gate | State | Remaining acceptance evidence |
|---:|---|---|
| 8 — Secrets | 🟨🟩 HOST VERIFICATION ONLY | Actual host secret injection, owner/mode, process exposure and runtime review |
| 20 — Firebase | 🟧 OPEN | Verified no-billing real Firebase auth/revocation/entitlement and browser/Android flow |
| 25 — Redis | 🟧 OPEN | Real host TLS, ACL, credential lifecycle, persistence and failover |
| 30 — Restore | 🟨🟩 HOST VERIFICATION ONLY | Restore drill against actual live database path on owner-controlled runtime |
| 31 — Off-host backup | 🟧 OPEN | Independent destination/key custody and restore; constrained by one-device boundary |
| 34 — Persistent volume | 🟨🟩 HOST VERIFICATION ONLY | Actual host mount, ownership, restart persistence and disk-pressure recovery |
| 35 — HTTPS | 🟨🟩 HOST VERIFICATION ONLY | Real HTTPS endpoint, certificate/hostname and renewal path |
| 36 — WSS | 🟧 OPEN | Public reverse proxy plus real browser and Android WebView acceptance |
| 38 — Monitoring | 🟧 OPEN | Collector/dashboard, retention, access control and disk-pressure acceptance |
| 39 — Incident response | 🟨🟩 HOST/OPERATOR VERIFICATION ONLY | Real operator visibility, acknowledgement/escalation and recovery drill |

## Exact-head CI

- Automated Tests [44863517983](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863517983): **SUCCESS** — frontend 247/247; backend 1,238 passed in 49.89s; 32/32 workflow steps. CodeQL [44863518025](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863518025) and Full Git History Secret Audit [44863517962](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863517962): **SUCCESS**.
- Frontend dependency audit: 0 vulnerabilities. Backend dependency audit: no known vulnerabilities. Trivy scanned Alpine and Python package targets with 0 vulnerabilities.
- Backend container build and Redis ACL/AOF + persistent-volume smoke: **SUCCESS**.

## WebSocket status

**Automated failure matrix: COMPLETE for the defined repository scope.** Verified work includes two independent ASGI processes, separate replicas/consumer groups, authenticated live delivery, reconnect replay, process restart continuity, Redis read-failure recovery, independent Redis TCP interruption/recovery, and coordinated snapshot-generation replacement. External production snapshot distribution/rotation/rollback, production Redis TLS/ACL/network/failover, public HTTPS/WSS, and browser/Android acceptance remain open.

## Complete indicator status

| Indicator / subsystem | State | Formula / first valid candle | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Mean of 20 closes; index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; alpha = 2/21; index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| RSI14 | 🟨 FOUNDATION | Wilder smoothing over 14 close changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 FOUNDATION | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, MACD/signal lines, histogram, zero guide, toggle, legend |
| Bollinger20,2 | 🟨 FOUNDATION | Mean ± 2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 FOUNDATION | Validated backend snapshot; no DEMO fallback; candle-index aligned | Identity/timeframe binding, loading/error, stale clearing, series isolation |
| Footprint | 🟧 SIMULATED / GATED | Educational simulated accumulator; not exchange-native bid/ask truth | Owner reference image, approved blueprint, ON-only spaced clusters, bid/ask cells, performance tests |
| Heatmap | 🟥 NOT IMPLEMENTED | Data source/calculation contract not approved | Reference image, source feasibility, validated data contract, blueprint and renderer |
| Liquidation Maps | 🟥 NOT IMPLEMENTED | No validated liquidation dataset/calculation contract | Zero-cost source feasibility, validated calculation, blueprint/reference and renderer |

**Indicator correctness invariants:** warm-up slots are null, never fabricated zeroes; every series aligns to candle indices; appending future candles cannot change earlier outputs; symbol/venue/dataset/chart/timeframe changes invalidate stale series. Footprint OFF preserves standard candle spacing; only explicit ON activates the spaced cluster layout. Footprint and Heatmap visual work waits for the user's reference images and reviewed blueprints. No aggregate indicator percentage is assigned.

**Cost/device boundary:** ZERO COST. No Vercel/Cloudflare deployment, paid service, Termux/device command, production credential, or `main` modification.

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

### Remaining WebSocket acceptance blockers — current position (reconciled 21 Nov 2026)

The earlier 62J-15 failure-matrix gap is **superseded** by the verified dual-ASGI and real-Redis evidence in Batches 62J-25, 62J-28 and 62J-31. Batch 62J-69 then removed four synchronous test-client deprecation warnings without changing runtime behavior.

1. **Production snapshot lifecycle:** owner-provisioned distribution, rotation, rollback, retention and authorized cleanup of verified replica snapshots.
2. **Production Redis operations:** real-host TLS certificate validation, least-privilege ACL provisioning/rotation, network policy, persistence, supervision and failover/recovery evidence.
3. **External client path:** accepted public HTTPS/WSS endpoint plus browser and Android WebView handshake, auth/entitlement, reconnect/replay and resnapshot acceptance.
4. **Operator acceptance:** target-host runbook, observed incident/recovery drill and evidence retention.

**Automated failure matrix:** COMPLETE for its defined scope. Do not reopen already-passed two-ASGI live delivery, replay, gateway restart, independent TCP-path interruption/recovery or generation-replacement tests as if they were unimplemented. Do not infer production deployment or close Gates 25/34/35/36 from CI-only evidence.

### Exact-head CI evidence — Batch 62J-69

At branch HEAD `96bfea52d9920b7d5d49ed85c0536610a6afd037`, Automated Tests run `44849892717` completed **SUCCESS**. Frontend: 245/245 tests across 29 files. Backend: 1,218 passed in 48.17 seconds; pytest emitted no warnings summary. All 31 listed job steps completed successfully, including frontend build/scans, backend tests, synthetic SQLite outbox benchmark, dependency audits, backend image build, Redis ACL/AOF + mounted-volume smoke test, Trivy scan and vulnerability report export.

The four changed lines are confined to `backend/tests/test_ohlcv_redis_consumer.py`: synchronous WebSocket test clients now explicitly pass `legacy=True` alongside `ping_interval=None`. This resolves the legacy-client deprecation warnings shown by the previous test run. No production WebSocket code, API contract, chart, indicator or database behavior changed. The separately recorded CodeQL and full-history audit successes remain at prior code/test HEAD `56317eff2b71886040acb998bf692814622feedf`; they are not mislabeled as exact-head checks for this test-only commit.


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
- Two-ASGI process/WebSocket acceptance is already CI-verified (Batch 62J-25); transient Redis read recovery and process restart continuity (62J-28), TCP-path interruption/recovery and coordinated snapshot-generation replacement (62J-31) are also CI-verified. The automated WebSocket E failure matrix is complete for its defined repository scope. Production snapshot artifact distribution/rotation/rollback, production Redis TLS/ACL/topology, public WSS and browser/Android acceptance remain open. Do not claim production readiness.
- Exact docs HEAD `290c4fe1b4a125e9a41b410d942e807db22c58aa`: Test and Build, CodeQL JavaScript/TypeScript, CodeQL Python, and full reachable Git-history secret audit all SUCCESS. Frontend 245/245 across 29 files; backend 1,218 passed, 6 warnings. This is CI evidence, not production acceptance.
- No runtime/indicator code changed. Indicator status remains unchanged; no indicator percentage is assigned. Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; overall project and aggregate indicator percentages remain unestablished.
- Next WebSocket batch: do not repeat the passing two-ASGI CI harness. Progress only through approved owner-side snapshot artifact lifecycle, production Redis TLS/ACL/topology evidence, and then public WSS/browser/Android acceptance. Keep production replica mode opt-in.
- ZERO COST. No Termux/device command, deployment, Vercel/Cloudflare operation, paid service, or `main` modification.


## Batch 62J-69 progress reconciliation — 21 November 2026

- WebSocket source publisher lifecycle: 🟨🟩 host-factory / snapshot-verification pending. Exact-head CI passed on 6f49951c253a7e7b995b4bdd52eba8153edaef77. FastAPI validates source-store identity, checkpoint/source ID, dedicated Redis client and stream key; then performs startup PING, bounded background relay, persisted-bar wake-up, 1-second backlog polling, bounded retry, terminal resnapshot-required handling and guarded shutdown. Owner-host snapshot watermark, ACL and durable-volume checks remain open.
- WebSocket production acceptance: 🟧 OPEN. This batch does not close public WSS, production Redis TLS/ACL topology, snapshot distribution/rotation/rollback, browser or Android WebView acceptance.
- Indicator implementation unchanged. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 FOUNDATION; Footprint remains 🟧 SIMULATED / GATED; Heatmap and Liquidation Maps remain 🟥 NOT IMPLEMENTED. No indicator progress percentage is awarded by a backend-only change.
- Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional. Overall project percentage and aggregate indicator percentage remain unscored because approved denominators/weights are not established.
- ZERO COST maintained: no deployment, paid service, production credential, Termux/device operation, or `main` modification.


## Batch 62J-72 — snapshot artifact SHA-256 receipt binding (21 November 2026)

**Source/test checkpoint:** `0a8e28e0ae9b8e63f800cf4ff643a057c942ee90` (CI result must be read from this exact commit before any pass claim).

- Hardened `backend/app/ohlcv_redis_runtime.py`: the host verifier contract now requires the verified global snapshot's canonical lowercase SHA-256 digest (`snapshot_sha256`).
- Every required gateway installation receipt must carry the exact same digest in addition to matching source ID, stream key, snapshot generation and cursor.
- Missing/malformed manifest digests and per-gateway digest mismatches fail closed **before Redis client creation**.
- The runtime returns the verified digest as part of its non-secret snapshot evidence summary.
- This binds the receipts to the exact exported snapshot bytes. It does not authenticate receipts by itself: the owner-host verifier must still call the repository's `SQLiteOhlcvStore.verify_global_snapshot()` against the actual artifact and authenticate the authoritative receipt source. The repository cannot attest to remote host state.
- Added regressions for per-gateway digest mismatch and malformed manifest digest, alongside the existing cursor mismatch and successful TLS factory path.
- No indicator formula, hook, renderer or UI changed. No Gate 10 acceptance tick is awarded by this repository-side hardening.
- ZERO COST. No production Redis connection, deployment, Vercel/Cloudflare operation, production credential, Termux/device action or `main` modification.

**Acceptance boundary:** Gate 25 remains 🟧 OPEN pending live Redis TLS/ACL, persistence/failover and host credential lifecycle. Gate 36 remains 🟧 OPEN pending public HTTPS/WSS proxy and browser/Android runtime acceptance. Source publisher stays 🟨🟩 HOST VERIFICATION PENDING.


## Latest engineering checkpoint — Batch 62J-75 (21 November 2026)

**Verified CI head:** `3e3428910e3226f3d4365808f3a36a3138674231` — Automated Tests run [44874341856](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341856), CodeQL run [44874341916](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341916), and full Git-history secret audit run [44874341885](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341885) all SUCCESS. The CI run executed the Redis ACL integration test and finished with **1,249 backend tests passed in 57.10 seconds**. The Docker smoke step, image scan and vulnerability-report export/upload also succeeded.

**Batch 62J-73 correction — least privilege:** review of the real-Redis ACL tests showed that redis-py uses database 0 as its default without issuing `SELECT 0`. Granting `+select` was therefore unnecessary and broader than required. Batch 62J-74 removes `+select` from both publisher and gateway allow-lists. The integration test now proves both roles can PING and perform their allowed operations while explicit `SELECT 1` is denied. URL validation continues to reject every non-zero database path. This is a security-scope tightening; the earlier claim that `+select` was needed is superseded.

**Verified zero-cost CI simulation:**
- Redis 7 service-backed ACL integration: publisher and gateway identities authenticate with disposable runtime-only passwords; allowed stream/lease operations succeed and prohibited command/key access is denied.
- Existing end-to-end Redis tests also pass: source publisher deterministic cursor append/read-back, per-gateway consumer groups, durable apply-before-ACK, snapshot generation reset, event replay, callback retry, lease ownership and ACL role separation.
- Backend container smoke: authenticated Redis ACL; rejects unauthenticated, wrong-password and unrelated SET access; AOF data and ACL file survive Redis container restart; backend returns fail-closed 503 while Redis is down and recovers after Redis returns; non-root UID/GID and mounted-volume ownership are verified; SQLite integrity and backend restart persistence are verified; rate-limit enforcement is verified.
- Backend image vulnerability scan and vulnerability report artifact export/upload: SUCCESS.
- Frontend tests/build/secret scans, backend dependency audit, Gitleaks full-history audit and CodeQL: SUCCESS.
- The synthetic outbox benchmark uses 1,000 synthetic bars, 250-event pages and two concurrent readers. It is explicitly synthetic and is not market-data performance evidence.

**Important scope boundary:** the CI smoke Redis is a temporary guard-service container with an AOF volume. It does not establish production persistence/failover for the dedicated OHLCV stream, nor a live production Redis TLS endpoint. The CI ACL test is real Redis command/key enforcement but remains ephemeral. No production host exists.

**WebSocket status:** repository-side automated WebSocket E/failure-matrix acceptance is complete for its defined CI scope. Production WebSocket acceptance is not complete: real snapshot distribution and installation receipts, production Redis TLS/ACL topology, host secret rotation, stream persistence/failover/retention, public HTTPS/WSS reverse proxy and browser/Android WebView acceptance remain external.

**Gate 10:** 0/10 formally closed. Gate 8 remains 🟨🟩 host-verification-only. Gates 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain 🟧 OPEN; this batch provides repository/CI evidence but does not award a formal gate tick. Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored because approved denominators/weights are not established.

**Complete indicator ledger — unchanged by this backend batch:**
- SMA20 — 🟨 foundation; arithmetic mean of the last 20 closes; first valid candle index 19. Remaining: overlay rendering, visibility toggle, legend/current value, stale-series clearing and renderer tests.
- EMA20 — 🟨 foundation; SMA-seeded EMA, alpha = 2/21; first valid index 19. Remaining: overlay rendering, visibility toggle, legend/current value, stale-series clearing and renderer tests.
- RSI14 — 🟨 foundation; Wilder smoothing; first valid index 14. Remaining: dedicated 0–100 pane, 30/70 guides, toggle, legend and renderer tests.
- MACD 12/26/9 — 🟨 foundation; EMA12−EMA26 first valid index 25; signal and histogram first valid index 33. Remaining: dedicated pane, signal lines, histogram, zero guide, toggle, legend and renderer tests.
- Bollinger20,2 — 🟨 foundation; mean ± 2 × population standard deviation; first valid index 19. Remaining: three-line overlay, toggle, displayed values, stale-series clearing and renderer tests.
- Shared Indicator Hook — 🟨 foundation; validated, candle-index-aligned snapshot. Remaining: full identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation.
- Footprint — 🟧 simulated/gated; requires the user's visual reference, approved blueprint, ON-only spaced candle/cluster layout, bid/ask cells and performance acceptance.
- Heatmap — 🟥 not implemented; requires user's visual reference, zero-cost source feasibility, validated data contract, approved blueprint and renderer.
- Liquidation Maps — 🟥 not implemented; requires zero-cost source feasibility, validated calculation/data contract, approved blueprint/reference and renderer.

Indicator invariants: warm-up values are `null`, never zero; all values align to candle indices; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves ordinary candle spacing; only explicit ON enables spaced cluster layout. No indicator implementation credit is awarded by backend-only work.

**Cost/device:** ZERO COST. No paid hosting, deployment, Vercel/Cloudflare operation, production credential request, Termux command, device action or `main` modification.


## Batch 62J-88 — exact-head metrics and process contention hardening (21 November 2026)

- Exact-head Automated Tests on `8424e5eefeecbd06c6534bc34d166f4749ba4055`: [44903581963](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581963) SUCCESS, 35/35 steps; frontend 255/255 across 29 files; backend 1,268 passed in 46.21 seconds. CodeQL [44903581995](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581995) SUCCESS; Full Git History Secret Audit [44903581971](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581971) SUCCESS.
- Full-cardinality benchmark verified 899/899 series at 1, 4 and 16 threads. All integrity checks `ok`; 16-thread p95 562.43 ms, p99 982.13 ms and 196 retries. This indicates contention remains; Gate 38 stays OPEN.
- Batch 62J-88 removes benchmark/test outer retries, adds four-process SQLite contention measurement and read-only failure/recovery coverage. These additions require exact-head CI before acceptance.
- Gate 38 remains 🟧 OPEN pending process benchmark CI, disk-full test, app-level HTTP/WebSocket isolation, owner-host persistence/retention/backup and operator acceptance.
- WebSocket repository-side automated matrix remains complete; production WSS acceptance remains host-gated. No WebSocket data-path change.
- Indicator progress unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, shared hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. No indicator credit from backend work.
- Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35, 39 🟨🟩; Gates 20, 25, 31, 36, 38 🟧. Stage 1 remains 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST; no deployment, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.


## Batch 62J-89 — remove stray assertion from thread regression (21 November 2026)

- Initial CI for commit `002517f778bed20bcb9e7fe7eed7946893c9763f`: Automated Tests [44904630244](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630244) failed one test; frontend 255/255 passed, backend 1,268 passed and one failed.
- Root cause was a test-edit residue: after the intended single `collector.flush(...)` call, the thread test still contained an unconditional `raise AssertionError("bounded SQLite retry loop exhausted")`. The flush completed; the test then deliberately failed. This was not evidence of collector retry exhaustion.
- In the same run, the new read-only recovery test passed, and the benchmark contract test—including the four spawned OS-process/899-series case—passed.
- CodeQL [44904630257](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630257) SUCCESS; Full Git History Secret Audit [44904630302](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630302) SUCCESS.
- Correction removes only the stray assertion. It does not restore benchmark/test outer retries and does not change production collector code.
- Exact-head CI must rerun before the process/read-only additions are accepted. Gate 38 remains 🟧 OPEN.
- Indicator state unchanged; Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST; no deployment, Termux/device action, or `main` modification.

## Batch 62J-90 — process benchmark and corrected exact-head acceptance (21 November 2026)

Exact-head source/test commit `2650c70e977b22a4c70a5e0e292dcc3a8a59082c` passed Automated Tests [44904944196](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944196): 35/35 workflow steps, frontend 255/255 tests across 29 files, backend 1,269 passed in 53.67 seconds. CodeQL [44904944207](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944207) SUCCESS; Full Git History Secret Audit [44904944202](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944202) SUCCESS.

Artifact `synthetic-metrics-collector-benchmark`, ID `14707137707`, verifies all 899 series and SQLite integrity for thread and process cases.

| Workload | Flushes | p50 ms | p95 ms | p99 ms | Max ms | Retries |
|---|---:|---:|---:|---:|---:|---:|
| 1 thread | 32 | 15.198 | 15.997 | 17.820 | 17.820 | 0 |
| 4 threads | 128 | 14.024 | 192.993 | 290.086 | 354.538 | 2 |
| 16 threads | 512 | 120.955 | 654.798 | 921.534 | 2,769.913 | 251 |
| 4 OS processes | 128 | 14.403 | 243.724 | 278.107 | 415.647 | 4 |

All four cases verified 899 logical series; process case verified four separate workers and 128/128 flushes. The 16-thread contention tail remains high and is not hidden by benchmark-only retries. Process case post-checkpoint DB+WAL+SHM = 487,424 bytes; not a peak-size or production-volume estimate.

Batch 62J-90 adds a genuine SQLite page-limit/disk-full rollback-and-recovery test plus an app-level test that forces metrics flush failure while verifying HTTP health, operator metrics status and authenticated WebSocket status remain responsive. These additions are pending exact-head CI. No production collector behavior changes in this batch.

- Batch 62J-90 adds a genuine SQLite `max_page_count` exhaustion test and application-level collector-failure isolation test. They are pending exact-head CI; Gate 38 remains 🟧 until passed and owner-host checks are complete.


## Batch 62J-91 — disk-full test liveness assertion timing correction

Automated Tests [44905465144](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905465144) reported 1,270 passed / 1 failed. The SQLite `SQLITE_FULL` exception and aggregate rollback assertions passed. The only failure was the test expecting one live worker at snapshot time 1801 although the last successful checkpoint was 900 and the stale threshold is 90 seconds; the collector correctly reported zero live workers. The test now checks at timestamp 901 (checkpoint age 1 second). The app-level HTTP/WebSocket failure-isolation test and read-only recovery test passed. CodeQL [44905465128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905465128) and Full Git History Secret Audit [44905464959](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905464959) passed. Exact-head Automated Tests rerun pending. No collector code or indicator implementation changed.

## Batch 62J-92 — exact-head acceptance: process, disk-full and traffic isolation (21 November 2026)

**Accepted exact HEAD:** `427e5952d2f209ae1f40405223d8d0a4c7d8408c`

- Automated Tests [44905839386](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839386): **SUCCESS**, 35/35 workflow steps.
- Frontend: **255/255 tests across 29 files**.
- Backend: **1,271 passed in 39.80 seconds**.
- CodeQL [44905839403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839403): **SUCCESS**, Python and JavaScript/TypeScript.
- Full Git History Secret Audit [44905839442](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839442): **SUCCESS**.
- Backend container build, ephemeral Redis shared-guard/persistent-volume smoke, Trivy scan and report export: **SUCCESS**.

### Gate 38 repository-side evidence
- Full 899-series benchmark: 1/4/16 Python threads and 4 independent OS processes; exact series counts, worker counts, aggregation and SQLite integrity verified.
- 4-process case: 128/128 flushes; 899/899 series; p95 243.724 ms; p99 278.107 ms; 4 internal retries; SQLite integrity `ok`.
- 16-thread case: 512/512 flushes; 899/899 series; p95 654.798 ms; p99 921.534 ms; max 2,769.913 ms; 251 internal retries. The contention tail remains visible and is not concealed by benchmark-only retries.
- Read-only storage failure/recovery test passed.
- Real SQLite `SQLITE_FULL` page-limit test passed: second full-cardinality bucket rejected; transaction and checkpoint rolled back; later writable flush recovered without double counting.
- App-level failure-isolation test passed: collector entered degraded state while HTTP health, authenticated metrics scrape and authenticated WebSocket status remained responsive.
- These are repository/CI results, not owner-host persistence or production operator acceptance.

### Remaining Gate 38 host/operator acceptance
Actual owner-host persistent volume and permissions; restart persistence; measured disk pressure/retention; backup/restore; reverse-proxy/firewall isolation; operator-token injection/rotation; operator dashboard visibility/access review; independent notification, acknowledgement/escalation and recovery drill. Multi-host SQLite remains unsupported.

### Indicator and project status
No indicator calculation, hook, renderer or UI changed. SMA20 🟨 (first valid index 19); EMA20 🟨 (SMA-seeded, alpha 2/21, index 19); RSI14 🟨 (Wilder, index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram 33); Bollinger20,2 🟨 (population SD, index 19); Shared Indicator Hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥. Warm-up null, candle-index aligned, no future-candle repaint and stale clearing remain invariants.

Gate 10 remains **0/10 formally closed**. Gates 8, 30, 34, 35 and 39 remain 🟨🟩 host/owner-verification-only. Gates 20, 25, 31, 36 and 38 remain 🟧 OPEN; Gate 38 is not yellow-green because operator dashboard/notification/recovery and owner-host acceptance remain. Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.

ZERO COST. No deployment, paid service, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.

## Batch 62J-93 — SQLite metrics batch-read optimization and exact-head acceptance (21 November 2026)

**Source/test HEAD:** `a62e7423a5d36d3fdbc003e0e56d86c3a9e6ecbb`

- Automated Tests [44911391436](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391436): **SUCCESS**, 35/35 steps.
- Frontend: **255/255 tests across 29 files**.
- Backend: **1,271 passed in 55.86 seconds**.
- CodeQL [44911391400](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391400): **SUCCESS** for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [44911391397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391397): **SUCCESS**.
- Frontend npm audit: 0 vulnerabilities; backend dependency audit: no known vulnerabilities; Trivy reported 0 vulnerabilities in the scanned Alpine and Python package targets.
- Backend container build, shared-Redis/SQLite persistent-volume smoke, full-cardinality metrics benchmark, image scan and report export: **SUCCESS**.

### What changed
`backend/app/metrics_collector.py` now reads the existing rows for the active 15-minute bucket once per flush, computes deltas in memory, and submits non-zero aggregate updates through `executemany`. The existing `BEGIN IMMEDIATE` transaction boundary, per-worker checkpoint, JSON value schema, retention cleanup, capacity enforcement and rollback behavior remain intact. This removes one bucket SELECT per logical series without changing the metric schema or WebSocket data path.

At 899 active logical series and 512 flushes, bucket reads are reduced from 460,288 per-key SELECTs to 512 batched SELECTs: **99.8888% fewer bucket-read statements**. This is a query-count calculation from the old/new code paths; the benchmark independently measures resulting wall-clock behavior.

### Full-cardinality benchmark — before versus after
The prior baseline is exact-head commit `2650c70e977b22a4c70a5e0e292dcc3a8a59082c`; the optimized result is exact-head `a62e7423a5d36d3fdbc003e0e56d86c3a9e6ecbb`. Both use synthetic 899-series payloads on CI runners, not production hardware.

| Workload | p95 before → after | p99 before → after | Max before → after | Retries before → after |
|---|---:|---:|---:|---:|
| 1 thread, 32 flushes | 15.997 → 13.172 ms | 17.820 → 14.003 ms | 17.820 → 14.003 ms | 0 → 0 |
| 4 threads, 128 flushes | 192.993 → 190.979 ms | 290.086 → 405.913 ms | 354.538 → 441.050 ms | 2 → 3 |
| 16 threads, 512 flushes | 654.798 → 600.947 ms | 921.534 → 944.797 ms | 2,769.913 → 1,727.381 ms | 251 → 154 |
| 4 OS processes, 128 flushes | 243.724 → 114.703 ms | 278.107 → 280.654 ms | 415.647 → 378.409 ms | 4 → 2 |

Relative changes:
- 16-thread p95 **−8.22%**, p99 **+2.52%**, max **−37.64%**, retries **−38.65%**.
- Four-process p95 **−52.94%**, p99 **+0.92%**, max **−8.96%**, retries **−50%**.
- Four-thread p95 **−1.04%**, but p99 **+39.93%** and max **+24.40%**. This tail regression is retained explicitly, not hidden.
- One-thread p95 **−17.66%** and p99 **−21.42%**.

All cases verified 899/899 logical series and SQLite `integrity_check=ok`; all expected flushes completed. The 16-thread case still has measurable lock contention. No latency SLA has been approved, so these results are comparative evidence, not a production performance guarantee.

### Gate 38 disposition
Repository-side full-cardinality benchmark, separate-process contention, read-only recovery, SQLite `SQLITE_FULL` rollback/recovery and app-level HTTP/WebSocket failure isolation are CI-verified. Gate 38 remains 🟧 OPEN pending actual owner-host volume/permissions/restart/retention/backup/disk-pressure, firewall/reverse-proxy and operator-token controls, dashboard visibility/access review, independent notification, acknowledgement/escalation and recovery drill. Same-host SQLite only; multi-host remains unsupported.

### Project and indicator accounting
Gate 10 remains **0/10 formally closed**. Gates 8, 30, 34, 35 and 39 are 🟨🟩 host/owner-verification-only; Gates 20, 25, 31, 36 and 38 remain 🟧. Stage 1 remains **30/40 = 75% provisional**; no tick is awarded by this optimization. Stages 2–6 and overall project percentage remain unscored.

No indicator formula, hook, renderer, UI or market-data contract changed. SMA20 🟨 (first valid index 19); EMA20 🟨 (SMA seed, alpha 2/21, index 19); RSI14 🟨 (Wilder, index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram index 33); Bollinger20,2 🟨 (population SD, index 19); Shared Hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥. Warm-up nulls, candle-index alignment, no future-candle repaint and stale-series clearing remain required.

ZERO COST. No deployment, paid service, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.


## Batch 62J-94 — Gate 38 tail-latency phase diagnostics (21 November 2026)

The collector now reports internal writer-lock wait and transaction-body/commit durations. Full-cardinality 1/4/16-thread and four-process benchmark output includes phase percentiles alongside end-to-end latency. This is diagnostic instrumentation, not an optimization or host/SLA result; exact-head CI is required. WebSocket paths and indicator implementation are unchanged; no indicator credit. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 closed; overall project remains unscored. ZERO COST; no deployment, Termux, device operation or `main` change.


## Batch 62J-95 — SQLite retry de-synchronization (21 November 2026)

The prior benchmark separated lock wait from transaction time and showed lock wait dominated the 16-thread p99 (617.533 ms of 625.336 ms) and remained significant in the four-process case (103.635 ms of 275.777 ms). Identical deterministic retry delays could synchronize contending workers. The collector now uses stable BLAKE2s-derived per-worker jitter (factor 0.5–1.0) while preserving the explicit-backoff ceiling: 0.81 s. With eight 250 ms SQLite busy-timeout attempts, the theoretical lock-acquisition wait remains ≤2.81 s. This is an optimization hypothesis pending exact-head CI and a fresh benchmark; no improvement is claimed yet. Indicators and WebSocket data path unchanged; no indicator credit. Stage 1 30/40 = 75% provisional; Gate 10 0/10 closed; overall project unscored. ZERO COST; no deploy/Termux/device operation.


## Batch 62J-96 — revert of regressive retry-jitter experiment (21 November 2026)

The 62J-95 per-worker retry-jitter experiment failed the comparison gate and was reverted. Against the immediately preceding 62J-94 benchmark on the same CI workflow shape, the 16-thread case regressed: p95 390.277 → 599.624 ms (+53.6%), p99 625.336 → 1,125.048 ms (+79.9%), max 878.721 → 2,042.702 ms (+132.4%), retries 105 → 181 (+72.4%). Four-thread p95 rose 120.249 → 190.787 ms (+58.7%); four-process p95 rose 62.234 → 139.278 ms (+123.8%). These are synthetic CI-runner results, not host performance guarantees. The jitter source/test changes were reverted; Batch 62J-94 phase instrumentation remains. No optimization benefit is claimed. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 closed; overall project unscored.


## Batch 62J-99 — Gate 25/36, Gate 38, Gate 20/31 three-workstream audit (21 November 2026)

Audited branch baseline `ae1ff4ada7977239b6970cd5bef02335ece29f08`. Repository-side review covered the gateway runtime and WSS guards (Gate 25/36), the bounded 899-series same-host SQLite collector and its disk-full/read-only/isolation tests (Gate 38), Firebase Admin revocation-aware identity verification plus deny-by-default per-instrument entitlements (Gate 20), and AES-256-GCM encrypted SQLite backup/fresh-path restore tests (Gate 31). No code-level defect was established, so no runtime source change was made. Host-side blockers remain real: Redis TLS/ACL and installed snapshot receipts; public HTTPS/WSS and Android WebView; metrics volume/dashboard/operator drill; real Firebase signed-token E2E; independent off-host backup and key-recovery restore. Gate 10 remains 0/10 formally closed; Gates 8/30/34/35/39 🟨🟩 host-only; Gates 20/25/31/36/38 🟧. Stage 1 remains 30/40 = 75% provisional; overall project remains unscored. Full indicator matrix and formulas recorded in the Batch 62J-99 work-cycle document; no indicator implementation changed and no indicator credit awarded. No CI was triggered for docs-only changes. ZERO COST; no deployment, Termux/device operation, production credentials or `main` modification.


## Batch 62J-100 — Gate 38 cold-start retry, Gate 39 escalation integration, WebSocket cancellation accounting (21 November 2026)

Accepted source/test HEAD `9e9a3d099f30faa2b641b8c991187394de783960`. The 16-worker standalone SQLite metrics benchmark previously failed in `SQLiteMetricsCollector._connect()` during cold-start schema bootstrap. The bounded bootstrap retry increased from 7 to 12 attempts while retaining 250 ms busy timeout and capped backoff. Conservative wait bound: 12 × 0.25 s + 1.81 s backoff = 4.81 s. A 16-independent-collector cold-start regression test now passes. Exact-head CI [44918802298](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802298): frontend 255 tests/29 files; backend 1,280 passed; full-cardinality 899-series metrics benchmark success; container build and shared Redis guard/persistent-volume smoke success. CodeQL [44918802275](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802275) and Full Git History Secret Audit [44918802271](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802271) succeeded. Trivy artifact 14713530156: zero HIGH/CRITICAL vulnerabilities in scanned Alpine OS and Python package targets. Gate 39 lifespan escalation and WebSocket cancellation cleanup now have integration tests; remote operator notification and production WSS remain unverified. Gate 10 remains 0/10 closed; Gates 8/30/34/35/39 🟨🟩; Gates 20/25/31/36/38 🟧. Stage 1 remains 30/40 = 75% provisional; overall project remains unscored. No indicator implementation changed and no indicator credit is awarded; full matrix and invariants are recorded in the Batch 62J-100 work-cycle document and indicator ledger. ZERO COST; no deployment, Termux/device operation, production credentials or `main` modification.



## Batch 62J-101 — WebSocket accepted-counter lifecycle correction + Gate 10 continuation (21 November 2026)

- Active branch: `phase-2/market-data-foundation`; source/test commit: `db010cf76d6da2b1e950156f05bb18606b4fff2d`.
- Corrected `WebSocketMetrics` semantics: `connections_accepted` now increments immediately after a downstream ASGI `websocket.accept` send succeeds, not later when the connection finishes. A failed accept send does not increment it; duplicate accept frames within one connection are counted once. Completion still decrements active and records completed/peer-disconnect/close-code/duration.
- Added an authenticated FastAPI application integration test that checks started/active/accepted while the socket is open and active/completed/accepted after closure. Existing unit tests cover send failure and cancellation paths.
- CI on exact source/test commit: Automated Tests run [44923590787](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590787) is **IN PROGRESS** at documentation time; no pass is claimed. CodeQL [44923590774](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590774): SUCCESS. Full Git History Secret Audit [44923590739](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590739): SUCCESS.
- Failed diagnostic candidate `0857936d9129e51fad37dc921e895c79219f2108`: backend 1,280 passed, 1 failed because the new test exposed the accepted-counter semantic issue. Intermediate candidate `13924cca3b3edff5e6fe41b43df6489924bf3a7b` is not accepted; its temporary test expectation was superseded by the runtime correction in `db010cf...`.
- WebSocket repository evidence is stronger, but Gate 36 remains 🟧 until owner-host TLS/reverse proxy, live Redis gateway, public HTTPS/WSS and browser/Android WebView acceptance. No live host or device verification is claimed.
- Gate 10 remains **0/10 formally closed**. 🟨🟩 host/operator verification only: Gates 8, 30, 34, 35, 39. 🟧 integration/acceptance still open: Gates 20, 25, 31, 36, 38.
- Gate 20: repository identity/entitlement/ticket tests exist; real Firebase signed-token E2E (valid/expired/revoked/wrong project) and final ticket-scope threat-model decision remain external.
- Gate 25: source-side Redis gateway/snapshot validation exists; owner-host TLS/ACL, authenticated snapshot transfer/receipt and persistence/failover remain external.
- Gate 31: encrypted backup and fresh-path restore tests exist; independent off-host destination, offline key custody and key-recovery restore remain external.
- Gate 38: 899-series same-host SQLite collector/benchmark and failure-isolation tests exist; owner-host persistent volume, private access perimeter, dashboard, notification and operator recovery drill remain external.
- Gate 39: lifespan escalation and sanitized event tests exist; external independent notification and operator receipt/drill remain external.
- Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored because approved denominators/weights do not exist.
- Indicator implementation is unchanged; no indicator progress credit is awarded in this backend work cycle. Complete indicator matrix and formulas remain in `docs/INDICATOR_PROGRESS_LEDGER.md`.
- ZERO COST. No Vercel/Cloudflare deployment, paid service, Termux, device action, production credential or `main` modification.



## Batch 62J-101 CI completion — exact source/test HEAD verified (21 November 2026)

- Source/test HEAD `db010cf76d6da2b1e950156f05bb18606b4fff2d`: Automated Tests [44923590787](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590787) **SUCCESS**; frontend 255/255 tests across 29 files; backend 1,281 passed in 48.87 s.
- Synthetic outbox and 899-series SQLite metrics benchmarks, backend dependency audit, backend container build, shared Redis guard/persistent-volume smoke and configured HIGH/CRITICAL Trivy scan all succeeded.
- CodeQL [44923590774](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590774): **SUCCESS**. Full Git History Secret Audit [44923590739](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590739): **SUCCESS**.
- The accepted-counter fix is now CI-verified. This does not close Gate 36: production WSS, owner-host TLS/reverse proxy, live Redis and browser/Android WebView acceptance remain external.
- Gate 10 remains 0/10 formally closed; host/operator-only Gates 8/30/34/35/39 🟨🟩; integration/acceptance Gates 20/25/31/36/38 🟧.
- No indicator source or tests changed; no indicator progress credit. Stage 1 remains 30/40 = 75% provisional; overall project remains unscored.


## Batch 62J-102 — Gate 20 ticket failure boundaries + Gate 10 evidence reconciliation (22 November 2026)

- Source/test HEAD `140df3f33fcebb9154f8ad26f40986ec73e2336f`; Automated Tests, CodeQL and Full Git History Secret Audit all SUCCESS.
- Three FastAPI ticket-endpoint integration tests added: missing Bearer identity → 401; unavailable ticket store → 503; ticket-store exception → sanitized 503 without internal/credential leakage.
- Production Redis policy audited and found already correct: production requires REDIS_URL, rediss TLS and ACL username/password. No unnecessary configuration change.
- Backend 1,284 passed in 46.77 s; frontend 255 passed across 29 files.
- Trivy artifact 14732364657: zero HIGH/CRITICAL findings in scanned Alpine OS and Python package targets, within configured scope.
- Gate 38 synthetic benchmark artifact 14732279593: 899/900 series (99.89%); all profiles passed data/integrity checks; 16-thread contention remains visible (67 retries, p99 595.76 ms, max 1,258.36 ms). CI-runner synthetic only, not production SLA.
- Gate 20 repository evidence improved but no gate closed. Gate 10 remains 0/10; host/operator-only Gates 8/30/34/35/39 🟨🟩; integration/acceptance Gates 20/25/31/36/38 🟧.
- Stage 1 remains 30/40 = 75% provisional; overall project percentage remains unscored.
- No indicator implementation changes; no indicator credit. Complete formula, warm-up, rendering and remaining-work matrix recorded in the indicator ledger.
- No deployment, paid service, Termux, production credential or main-branch change.

## Batch 62J-106 — Production WebSocket acceptance reconciliation (22 November 2026)

### WebSocket production-acceptance disposition

The repository already has CI-verified two-process ASGI/WebSocket fan-out, cursor replay, dual-gateway TCP-path interruption recovery without process restart, and coordinated snapshot-generation replacement. These are repository/CI passes, not public-host acceptance.

The source and gateway runtime factories are implemented with fail-closed validation for production TLS, separate ACL identities, snapshot source/generation/cursor/SHA-256 and gateway installation receipts. FastAPI activation remains owner-injected because authenticated snapshot transfer and receipt verification must be supplied by the actual operator. No production host, public WSS endpoint, real dedicated Redis failover evidence or physical Android WebView session is available in this checkpoint.

Accordingly, WebSocket production acceptance remains **OPEN**. No production pass or gate closure is inferred from CI. The exact outstanding evidence is public HTTPS/WSS and certificate/reverse-proxy acceptance; dedicated production OHLCV Redis TLS/ACL/secret rotation/persistence/failover; authenticated global snapshot distribution and receipts; and browser plus Android WebView acceptance.

### Gate 10

Gate 10 remains **0/10 formally closed**:
- 🟨🟩 Host/operator verification-only: Gates 8, 30, 34, 35 and 39.
- 🟧 Integration/acceptance still open: Gates 20, 25, 31, 36 and 38.

Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored because approved denominators/weights are absent.

### Indicator progress

No indicator source, formula, data contract, hook, renderer, chart UI or indicator test changed. No indicator progress credit is awarded. The full formula, warm-up, status and remaining-work matrix is recorded in `docs/INDICATOR_PROGRESS_LEDGER.md`; statuses remain SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥 and Liquidation Maps 🟥. Warm-up nulls, candle-index alignment, no future-candle repaint and stale-series clearing remain mandatory.

ZERO COST. No deployment, paid service, production credential, Termux/device action, Vercel/Cloudflare operation or `main` modification.


## Batch 62J-107 — WebSocket ticket documentation and indicator reconciliation (22 November 2026)

- Corrected stale `backend/README.md`: production clients exchange Firebase Bearer ID tokens at `POST /v1/auth/websocket-ticket`, then authenticate WebSocket using the purpose-bound single-use ticket (90-second TTL). Direct Firebase-token frame authentication is non-production only.
- Source, client, test and indicator implementation unchanged; no CI run for this documentation-only batch. Existing CI evidence remains tied to its previously recorded source/test HEAD.
- Gate 20/25/36 production acceptance remains open: real Firebase-project E2E; owner-host shared Redis TLS/ACL, snapshot receipts and failover; public HTTPS/WSS, reverse proxy, browser and Android WebView.
- Gate 10 remains 0/10 formally closed: 🟨🟩 host/operator-only Gates 8, 30, 34, 35, 39; 🟧 integration/acceptance Gates 20, 25, 31, 36, 38.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- Indicator matrix unchanged; no progress credit: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. Full formulas, first-valid indices, invariants and remaining work are documented in `docs/WORK_CYCLE_2026-11-22_BATCH62J107_WEBSOCKET_AUTH_DOC_RECONCILIATION.md` and `docs/INDICATOR_PROGRESS_LEDGER.md`.
- ZERO COST; no deployment, Vercel/Cloudflare operation, paid service, production credential, Termux/device action, or `main` modification.


## Batch 62J-108 — WebSocket documentation contract regression guard (22 November 2026)

- Added `backend/tests/test_websocket_documentation_contract.py` to keep the README aligned with the implemented single-use WebSocket-ticket endpoint, source-defined TTL, auth frame and production legacy-auth rejection.
- No runtime, client, or indicator source changed. No indicator progress credit.
- Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored.
- Gate 20/25/36 production acceptance still requires real Firebase-project E2E, owner-host Redis TLS/ACL/persistence/failover/snapshot receipts, and public HTTPS/WSS plus browser/Android WebView acceptance.
- CI result must be checked against this exact batch commit; no pass is claimed in advance.
- ZERO COST. No deployment, Vercel/Cloudflare operation, paid service, production credential, Termux/device action, or `main` modification.


## Batch 62J-109 — exact-head CI acceptance (22 November 2026)

- Commit: `81b741946f1512fb264936e37406d7560f24456f` on `phase-2/market-data-foundation`.
- Corrected one case-normalization inconsistency in `backend/tests/test_websocket_documentation_contract.py`; README contract itself was already correct.
- Exact-head Automated Tests [44973890901](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890901): **SUCCESS**, all steps completed, no failures. Includes frontend tests/build, backend tests/dependency audit, container build, shared Redis persistent-volume smoke, image scan/report and synthetic SQLite/metrics benchmarks.
- Exact-head CodeQL [44973890847](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890847): **SUCCESS** (Python + JavaScript/TypeScript). Full Git History Secret Audit [44973890902](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890902): **SUCCESS**.
- Gate 10 remains **0/10 formally closed**. Host/operator-only Gates 8, 30, 34, 35, 39; integration/acceptance Gates 20, 25, 31, 36, 38.
- Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- WebSocket production acceptance remains open: public HTTPS/WSS/proxy, owner-host Redis TLS/ACL/persistence/failover, authenticated snapshot transport/receipts, real Firebase E2E, browser and Android WebView acceptance. No production gate closed.
- No indicator implementation changed. Full matrix unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD 12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. Formulas, warm-up indices, invariants and remaining tasks are in this ledger; no indicator progress credit.
- ZERO COST. No deployment, paid service, production credential, Vercel/Cloudflare operation, Termux/device action or `main` modification.


---

## Batch 62J-110 — real Redis TLS integration acceptance (22 November 2026)

- Baseline: `ec8566a2d34e693283b0fa18421aaf3d4d01ef45`; branch `phase-2/market-data-foundation`.
- Adds an ephemeral Redis 7 TLS-only CI fixture with a generated test CA, DNS SAN certificate, separate untrusted CA, ACL-restricted user and disabled plaintext listener.
- Adds real redis-py/RedisSharedGuard handshake tests: trusted CA + correct hostname succeeds; wrong hostname, wrong CA and plaintext protocol are rejected.
- The valid TLS session exercises HTTP rate-limit Lua, one-time WebSocket tickets and WebSocket lease acquire/renew/release.
- Test keys, passwords, certificates and private keys are generated at runtime only; Redis is loopback-bound and removed by the workflow trap.
- No production runtime behavior, indicator code, market-data source or WebSocket protocol changed.
- No indicator progress credit. SMA20 🟨 (index 19); EMA20 🟨 (index 19); RSI14 🟨 (index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram 33); Bollinger20,2 🟨 (index 19); Shared Indicator Hook 🟨; Footprint 🟧 reference-gated; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. Formulas, warm-up rules and remaining visual acceptance are documented in `docs/WORK_CYCLE_2026-11-22_BATCH62J110_REDIS_TLS_INTEGRATION.md`.
- Gate 10 remains 0/10 formally closed; Gate 25 and Gate 36 remain 🟧 OPEN for owner-host/public endpoint evidence. Stage 1 remains 30/40 = 75% provisional; overall project percentage remains unscored.
- Exact-head CI is required before declaring this batch accepted. ZERO COST; no deployment, paid services, Termux/device operation, Vercel/Cloudflare operation or `main` modification.


---

## Batch 62J-111 — Redis TLS fixture permission correction (22 November 2026)

- Parent candidate: `fc13d6ed302c8eccd1fc4cf18102b2c50b66fd5c`.
- Automated CI exposed a concrete fixture startup failure: Redis 7.4.12 runs under its unprivileged `redis` account and could not read the host-owned, mode-0600 `/tls/users.acl` file from the read-only bind mount.
- Corrective change: derive UID/GID from the exact `redis:7-alpine` image at runtime; assign only the Redis server private key and ACL file to that account; retain mode 0600 for private files; make only public certificates readable to the runner/client. CA private key and wrong-CA private key remain unreadable to the container process and are not mounted for Redis use beyond the containing read-only directory.
- No production source/configuration or runtime security behavior changes. TLS verification requirements and negative tests remain intact.
- Acceptance status: pending a new exact-head CI run. No TLS pass is claimed until the fixture starts and all positive/negative tests pass.
- Cost Rp0; no deployment, Termux/device work, paid services or `main` changes.


---

## Batch 62J-112 — separate TLS configuration rejection from plaintext handshake rejection (22 November 2026)

- Parent: `59013f1d9a65e08aef6392f489aca3f3367da072`.
- CI confirmed the Redis TLS-only container starts successfully after Batch 62J-111 permission correction.
- The first real integration execution then failed because the test expected a network `ConnectionError` for plaintext Redis URL while also supplying a custom CA. Production guard correctly rejects that invalid configuration immediately with `ValueError` (`REDIS_TLS_CA_CERTS` requires `rediss://`), before any socket is opened.
- Corrected the integration test to exercise the two distinct protections separately: (1) existing unit test asserts custom CA + plaintext URL is rejected at configuration time; (2) real integration test attempts plaintext against the TLS-only Redis listener without a custom CA and requires connection failure.
- No production code or runtime security behavior changed. CI must rerun on the new exact commit before acceptance.
- Gate 10 remains open; no public WSS or OCI deployment claim. ZERO COST, no Termux/device action, no paid resources, no `main` changes.


# Work cycle — Redis AOF persistence across TLS restart (22 November 2026)

- Branch: `phase-2/market-data-foundation`; parent HEAD: `5b165e5efbcf1fe2ff32592161f4cbc660aedee5`.
- Scope: strengthen the isolated CI Redis TLS fixture; no production Redis configuration or application runtime changes.
- The fixture now mounts a dedicated ephemeral Docker volume at `/data`, enables Redis AOF with `appendfsync always`, and removes the volume during CI cleanup.
- After the TLS/CA/hostname/plaintext integration suite, CI writes a canary under the permitted ACL keyspace, restarts the actual Redis container, reconnects using the trusted CA and ACL identity, and verifies the canary value survived.
- This is a repository-level restart/persistence integration test only. It does not prove OCI block-volume durability, host reboot recovery, encrypted off-host backup, production failover, or public WSS.
- Test-only password and CA remain ephemeral; no production secrets are added. Redis remains TLS-only and no public Redis port is exposed.
- Exact-head CI is pending. Do not mark the batch accepted until Automated Tests, CodeQL, and Full Git History Secret Audit all complete successfully.
- ZERO COST; no cloud resource, paid service, deployment, Termux/device operation, or `main` modification.


## Batch 62J-126 — owner-host acceptance evidence boundary audit (22 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Parent HEAD:** `5b0cc02be04efbef3971aa313836eb171e877117`  
**Exact-parent CI:** Automated Tests [44986957808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986957808) SUCCESS; CodeQL [44986957788](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986957788) SUCCESS; Full Git History Secret Audit [44986957739](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986957739) SUCCESS. The first two were polled to completed jobs; all three target `5b0cc02be04efbef3971aa313836eb171e877117`.

### Additional owner-host evidence review

- **Gate 30 — live backup/restore:** repository implementation includes SQLite Online Backup API, integrity and foreign-key checks, encrypted backup with ciphertext-integrity authentication, restore to a new database path rather than overwriting the active database, and hash/schema/row-count/domain validation. The restore drill can validate registry, entitlement, alert, coverage, OHLCV and outbox records. This is repository/test evidence only; no owner-host backup artifact or live production restore/readback has been supplied.
- **Gate 31 — off-host backup/key custody:** encryption and fresh-path restore checks do not prove an independently controlled off-host destination, separate recovery-key custody, or successful recovery using that separately held key. Gate remains open.
- **Gate 38 — observability:** current metrics are process-local and measured since process start. No evidence of a central retained dashboard, external notification route, or operator-facing disk-pressure dashboard was found in the reviewed implementation. Same-process counters and synthetic benchmarks do not establish cross-restart retention or production monitoring.
- **Gate 39 — alert delivery:** observed operational alert sink is local logging. No evidence of remote delivery, named human acknowledgement, escalation receipt or a completed operator recovery drill. Keep lifecycle/logging tests separate from real notification acceptance.
- **Android acceptance:** CI exercises host-side preflight and immutable preview-publisher contracts only. It does not launch an Android device/WebView or prove foreground/background, process death, network handover, reconnect/replay or duplicate suppression on a real device.
- **Architecture build coverage:** the reviewed backend container workflow builds `linux/amd64`. No multi-platform Buildx manifest or ARM64 build/smoke evidence was established. ARM64 remains unverified; do not claim support based on the amd64 Trivy report.

### WebSocket gate disposition

These findings do not close any production gate. Gate 25 remains open for authenticated owner-host snapshot transfer, independently authenticated gateway receipts, byte/hash custody and exact generation/high-water alignment under real Redis persistence/restart/failover. Gate 36 remains open for verified public HTTPS/WSS, trusted TLS/reverse proxy, real Firebase and entitlement E2E, real browser/Android lifecycle tests, network-interruption recovery, replay/resnapshot/duplicate suppression and production operator evidence. Gate 38 and Gate 39 remain open for real retained dashboards/alerting and externally delivered, acknowledged/escalated alerts.

**Gate 10: 0/10 formally closed. Stage 1: 30/40 = 75% provisional.** No Stage 2 transition. CI green is not owner-host production acceptance.

### Safe next sequence

1. Continue source/test audit of backup key lifecycle and alert/event boundaries; do not request or expose secrets.
2. Define a zero-cost, local-only acceptance harness for restore and monitoring contracts if it can run entirely in CI without new external accounts or services.
3. Keep real off-host recovery, public WSS, Firebase project and device acceptance as owner-operated gates; do not provision a host or create accounts.
4. Review ARM64 feasibility from workflow and dependency constraints before changing CI. Do not add paid runners or services.

### Indicator reconciliation

No indicator source, tests, formulas, hook, renderer or chart UI changed. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps remain 🟥 unimplemented. No indicator progress credit or aggregate percentage is assigned. Preserve warm-up nulls, source-index alignment, no future-candle repaint, stale-series clearing and Footprint OFF standard candle spacing.

### Cost and change boundary

ZERO COST. Documentation-only; no runtime source, tests, workflows, deployment, cloud resource, domain, account, production credential, Android device action or Termux work. `main` untouched.

## Batch 62J-127 — operator escalation and notification-boundary audit (22 November 2026)

**Parent:** b7d0482ff8fa5906c006460583ad3b175f4c282c  
**Exact-parent CI:** Automated Tests [44987388625](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987388625) SUCCESS; CodeQL [44987388511](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987388511) SUCCESS; Full Git History Secret Audit [44987388505](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987388505) SUCCESS.

### Corrected notification and operator-response boundary

- **User price-alert push is implemented as a distinct path:** owner-scoped FCM registration and fan-out use the durable price-alert trigger outbox. Device tokens are encrypted at rest with AES-256-GCM and owner/installation associated data; startup requires an owner-injected 32-byte key from a protected absolute-path regular file with group/other permissions denied. Production sender initialization uses Firebase Admin Application Default Credentials (ADC). Delivery is at-least-once, not exactly-once; Android event-ID deduplication remains required. These are code-path/test findings, not proof of successful delivery to the owner's live Firebase project or real devices.
- **Operational incident response is separate:** LocalAlertReporter writes sanitized local logs and an optional persistent SQLite incident journal. The journal deduplicates active fingerprints, retains resolved rows for 30 days, bounds capacity, and supports open/acknowledged/resolved state. Acknowledgement currently records the generic actor "operator", not a verified individual operator identity.
- **Escalation exists but is not notification delivery:** the application runs an escalation loop every 15 seconds and escalate_due advances up to three levels; the loop emits a local structured log event. It does not send an email, SMS, FCM operator push, webhook or paging event. Thus no external receipt, human acknowledgement or escalation chain is proven.
- **Internal operator endpoints exist:** incident list/acknowledge/resolve routes are gated by an injected bearer token. Their presence does not constitute an operator dashboard, authenticated individual attribution, remote alert delivery or an on-call response drill.
- **Metrics nuance:** /internal/metrics exposes process-local HTTP/WebSocket counters and can additionally include a same-host SQLite collector aggregation. The collector is bounded, uses 15-minute buckets and 7-day retention, and is best-effort local telemetry. There is no verified central dashboard, independent off-host metrics retention, external alert sink or operator paging integration. The separate alert-delivery status endpoint explicitly reports process-local-since-start scope.

### Acceptance implications

- Gate 20 still requires real Firebase project token validation/revocation and entitlement grant/revoke/renew E2E. The code's ADC initialization and test doubles do not close it.
- Gate 38 remains open for owner-host operational visibility, retained dashboard, disk-pressure behavior and monitoring across restart/failure.
- Gate 39 remains open for a real externally delivered operator alert, verified recipient, human acknowledgement, escalation receipt and documented response drill. Local escalation log entries are not external alerts.
- Gate 8 remains open for owner-host secret injection, permissions, rotation and log-redaction acceptance, including the FCM key and runtime ADC identity. A protected file loader is a source control, not owner-host evidence.
- Gate 10 remains **0/10 formally closed**; Stage 1 remains **30/40 = 75% provisional**. No Stage 2 transition.

### Scope and indicator reconciliation

No WebSocket runtime code, FCM runtime code, operator routes, tests or workflows changed. No indicator implementation, formula, hook, renderer, UI or tests changed. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps 🟥 unimplemented. No indicator progress credit or aggregate percentage. Preserve warm-up nulls, source-index alignment, no future-candle repaint, stale-series clearing and Footprint OFF standard candle spacing.

ZERO COST; documentation-only; main untouched.


## Batch 62J-129 reconciliation — 22 November 2026

No indicator source, tests, calculations, hook, renderer or chart UI changed. No indicator implementation progress is credited. Current matrix remains: SMA20 🟨 (20-close mean, first valid index 19); EMA20 🟨 (SMA-seeded, alpha 2/21, index 19); RSI14 Wilder 🟨 (14 close changes, index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram 33); Bollinger20,2 🟨 (20-close mean ±2 population SD, index 19); Shared Indicator Hook 🟨 (validated aligned output, not chart-integrated); Footprint 🟧 (simulated educational accumulator, visual work gated on user reference and reviewed blueprint); Heatmap 🟥; Liquidation Maps 🟥.

Shared acceptance remains: warm-up nulls, candle-index alignment, prefix causality/no future-candle repaint, stale-series clearing on identity/timeframe changes, visible toggles/legends/current values, chart renderer/lifecycle tests. Footprint OFF preserves normal candle spacing; only explicit ON enables spaced clusters. Footprint/Heatmap visuals remain blocked until the user supplies reference image(s) and reviews the scoped blueprint. No aggregate indicator percentage without approved weights and denominator.

## IP3S — Indicator Proses Peningkatan Proyek Signifikan (introduced 22 November 2026)

IP3S is a per-work-cycle delivery-quality score, **not** an overall project completion percentage. Weights and full-credit rules:

| Dimension | Weight | Full-credit condition |
|---|---:|---|
| Verified engineering delta | 25 | Tested runtime/source improvement or independently verified acceptance evidence |
| Test/CI evidence | 20 | Relevant checks pass on exact HEAD; limitations are explicit |
| Blocker reduction | 20 | A real acceptance blocker is closed or its exact owner/action is isolated |
| Canonical documentation | 20 | Source-backed findings, status and next acceptance criteria are reconciled |
| Scope/cost integrity | 15 | Correct branch, honest evidence claims, ZERO COST and authorization boundaries respected |

Score each dimension from 0–100% and apply its weight. Documentation alone earns no runtime implementation points; CI cannot close owner-host or real-device gates. A newly clarified blocker earns only decision-readiness credit, not gate-closure credit.

**Batch 62J-129: 58/100** (0/25 engineering delta + 20/20 exact-head CI + 8/20 blocker reduction + 15/20 canonical documentation + 15/15 scope/cost integrity). This is a work-cycle quality score, not project completion. Keep it separate from Stage 1 30/40 = 75% provisional and Gate 10 0/10 formally closed.


## Batch 62J-137 — current WebSocket acceptance and project indicators (22 November 2026)

### Gate 25 — receipt trust and migration

The gateway runtime binds callback-returned source ID, generation ID and high-water cursor to the durable replica checkpoint, but it only checks callback-returned SHA-256 syntax. No immutable digest receipt is stored in the replica database. The source publisher runtime validates the global snapshot envelope and required gateway installation mappings, but actual gateway receipt authentication and authoritative retrieval are delegated to the owner-host callback. Thus local validation proves metadata consistency, not independent remote receipt authenticity/custody.

The proposed next schema is a separate append-only receipt table, not extra mutable checkpoint columns. It must use a source/replica/generation identity tuple, canonical digest, immutable manifest/cursor metadata, non-secret attestation/key identifiers, authenticated transfer correlation and installation timestamp. Same tuple/same digest is idempotent; same tuple/conflicting digest or metadata is rejected. Rows, checkpoint and receipt commit atomically. Legacy checkpoints without receipts are LEGACY_UNATTESTED, never backfilled with invented provenance. Generation progression follows an approved cursor/source policy, not lexical UUID ordering. Design remains pending owner approval; no runtime or schema change.

Required tests: atomic persistence; idempotent replay; conflicting digest/manifest; generation progression; legacy migration/reopen; transaction fault injection; pre/post-commit restart; gateway durable-digest binding; gateway identity/cursor mismatch; publisher missing/duplicate/stale/revoked gateway receipt; receipt immutability after event advancement; concurrent read consistency. See [Batch 62J-137 report](WORK_CYCLE_2026-11-22_BATCH62J137_GATE25_RECEIPT_TRUST_AND_MIGRATION.md).

### Current indicator matrix

| Indicator | Status | Evidence boundary |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19 |
| EMA20 | 🟨 Foundation | SMA-seeded; alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 Foundation | First valid index 14 |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33 |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 |
| Shared Indicator Hook | 🟨 Foundation | Validated aligned backend output; not chart-integrated |
| Footprint | 🟧 Prototype | Synthetic accumulator only; user reference and reviewed blueprint gate visual implementation |
| Heatmap | 🟥 Not implemented | User reference and reviewed blueprint required |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence |

No indicator runtime, calculation, tests, hook, renderer or UI changed in Batch 62J-137. No indicator progress credit. Shared invariants: warm-up nulls, candle-index alignment, no future-candle repaint, invalid/gapped bars not silently coerced to zero, stale-output clearing on identity/timeframe changes. Footprint OFF preserves standard candle spacing; explicit ON alone activates spaced cluster layout. No aggregate indicator percentage without approved weights/denominator.

### Overall project progress

- Stage 1 Foundation, Security & Data Integrity: 30/40 criteria = 75% provisional.
- Stages 2–6: NOT SCORED / not officially opened.
- Overall project: NOT SCORED (stage weights and total denominator not approved).
- Gate 10: 0/10 external criteria formally closed.
- WebSocket Gates 25, 36 and 38: OPEN.
- IP3S Batch 62J-137: PENDING exact-HEAD CI; no numeric score yet.

ZERO COST. No paid hosting/API/domain, deployment, account, production credential, device or Termux work. main untouched.


## Batch 62J-138 — WebSocket Gate 25 executable acceptance sequence (22 November 2026)

### Source-backed runtime boundary

Gateway runtime calls the owner-provided snapshot installer, validates installed status, then reads the durable replica checkpoint. It binds callback source/generation/high-water cursor to checkpoint source/generation/applied cursor and validates SHA-256 syntax. There is no durable immutable digest receipt in the replica store to independently compare with callback metadata. The owner callback is explicitly trusted to transfer/install the verified snapshot. Publisher runtime validates source, stream, generation, cursor, digest syntax and complete unique gateway mapping consistency, while authenticated retrieval of actual gateway receipts is delegated to the owner-host callback. This is a missing independent receipt-binding acceptance test, not evidence of an unauthenticated remote exploit.

### Ordered Gate 25 execution plan

A. Legacy SQLite migration: preserve checkpoint, identity, bars and applied events; classify old checkpoint LEGACY_UNATTESTED; repeat open/migration without synthetic receipt or invented provenance.

B. Receipt transaction: atomically commit snapshot bars + mutable checkpoint + immutable receipt; same identity tuple and digest is idempotent; conflicting digest/manifest fails closed; injected exceptions and process restart prove old-complete/new-complete states only; event cursor advancement cannot mutate receipt.

C. Gateway binding: reconstruct evidence from durable receipt after restart; compare source, replica, generation, cursor, digest, row count and manifest version; reject valid-looking but incorrect callback digest or wrong replica before Redis client creation.

D. Publisher/owner-host boundary: authenticate gateway identity; retrieve authoritative durable receipts; verify approved attestation/key lifecycle; reject missing/duplicate/stale/replayed/revoked/wrong-gateway/mismatched receipts; test restart, backup/restore, retention and audit evidence.

No crypto scheme, key custody, receipt schema, generation progression or retention policy is silently selected. Owner approval is required before runtime/schema implementation. Never store private keys or shared secrets in receipts, logs, fixtures or source control. Gate 25 closure requires both local transaction evidence and owner-host authenticated receipt/recovery evidence. See [Batch 62J-138 report](WORK_CYCLE_2026-11-22_BATCH62J138_GATE25_EXECUTABLE_ACCEPTANCE_SEQUENCE.md).

### Indicator matrix — unchanged

| Indicator | Status | Evidence boundary |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19 |
| EMA20 | 🟨 Foundation | SMA-seeded; alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 Foundation | First valid index 14 |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33 |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 |
| Shared Indicator Hook | 🟨 Foundation | Validated aligned backend output; not chart-integrated |
| Footprint | 🟧 Prototype | Synthetic accumulator only; user reference + reviewed blueprint required |
| Heatmap | 🟥 Not implemented | User reference + reviewed blueprint required |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence |

No indicator source, calculation, test, hook, renderer or UI changed in Batch 62J-138. No implementation credit. Shared invariants remain warm-up nulls, candle-index alignment, no future-candle repaint, invalid/gapped bars not silently converted to zero, stale-output clearing on identity/timeframe changes. Footprint OFF preserves standard candle spacing; explicit ON alone enables spaced clusters. No aggregate indicator percentage without approved weights/denominator.

### Overall project indicator

- Stage 1 Foundation, Security & Data Integrity: 30/40 = 75% provisional.
- Stages 2–6: NOT SCORED / not officially opened.
- Overall project: NOT SCORED (stage weights/total denominator not approved).
- Gate 10: 0/10 external criteria formally closed.
- WebSocket Gates 25, 36 and 38: OPEN.
- IP3S Batch 62J-138: PENDING exact-HEAD CI; no numeric score until complete.

ZERO COST. No paid hosting/API/domain, deployment, account creation, production credentials, device or Termux work. main untouched.


---

## Batch 62J-140 — WebSocket shutdown race hardening (22 November 2026)

Source/test HEAD: `90fd29cbf7d98ee80ff6ba477bc4f016ec729fd5` on `phase-2/market-data-foundation`.

A source-backed lifecycle defect was corrected in `src/services/ohlcvWebSocketClient.ts`: if ticket renewal rejected after an intentional connection close, the renewal catch path could still report a transport error. The catch branch now returns when connection state is no longer `subscribed`, preserving active-session 401 handling while suppressing false post-shutdown errors.

Regression tests:
- `src/services/ohlcvWebSocketClient.test.ts`: pending ticket-renewal rejection after intentional close does not invoke `onError`.
- `src/services/ohlcvStreamSupervisor.test.ts`: late snapshot/update messages after supervisor stop cannot repopulate the market-data store.

The Batch 62J-139 tests remain included: stop during pending ticket issuance, and rapid browser lifecycle transitions without overlapping supervisors.

Changed source/test files in Batch 62J-140:
- `src/services/ohlcvWebSocketClient.ts`
- `src/services/ohlcvWebSocketClient.test.ts`
- `src/services/ohlcvStreamSupervisor.test.ts`

CI on source/test HEAD `90fd29cbf7d98ee80ff6ba477bc4f016ec729fd5` at the time of this record:
- Automated Tests [44994083255](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44994083255): IN PROGRESS.
- CodeQL [44994083173](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44994083173): IN PROGRESS.
- Secret Audit [44994083185](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44994083185): SUCCESS.
- Zero-cost Android debug APK [44994083097](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44994083097): IN PROGRESS.

No new test is CI-accepted until Automated Tests completes successfully on the exact source/test commit. No final IPS35/IP3S score is assigned while CI is pending.

WebSocket acceptance:
- Gate 36 remains OPEN for public WSS, live Firebase project and physical Android WebView lifecycle/network acceptance.
- Gate 25 remains OPEN for authenticated immutable snapshot installation receipts, key lifecycle and owner-host Redis durability.
- Gate 38 remains OPEN for owner-host metrics persistence, backup/retention, alert and recovery acceptance.
- Gate 10 remains 0/10 external criteria formally closed.

Indicator ledger unchanged by this WebSocket fix:
- SMA20 🟨 foundation, first valid index 19.
- EMA20 🟨 SMA-seeded alpha 2/21, first valid index 19.
- RSI14 Wilder 🟨 foundation, first valid index 14.
- MACD12/26/9 🟨 MACD first valid index 25; signal/histogram index 33.
- Bollinger20,2 🟨 20-close mean ±2 population SD, first valid index 19.
- Shared Indicator Hook 🟨 backend snapshot/aligned output; not chart-integrated.
- Footprint 🟧 synthetic educational accumulator only; wait for user reference images and reviewed blueprint.
- Heatmap 🟥 not implemented; wait for user reference images and reviewed blueprint.
- Liquidation Maps 🟥 not implemented.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 remain NOT SCORED. Overall project remains NOT SCORED because stage weights and total acceptance denominator are not approved.

ZERO COST preserved: no paid services, deployment, account creation, production secrets, device/Termux work, dependencies or schema changes. `main` untouched.


## Batch 62J-144 — multi-user WebSocket lifecycle and indicator reconciliation (22 November 2026)

### WebSocket multi-user ownership

The app's connection lifecycle is per client, not per backend process. Backend source creates a unique connection ID and unique subscription stream/queue for each accepted client. Disconnect cleanup removes only that client's subscription and shared connection lease. Other users' active subscriptions are not stopped when one user closes the app. The FastAPI process and lifespan-owned publisher/replica workers are service resources, not children of a mobile client connection.

A global zero-active-client policy to pause optional upstream ingestion after a grace period is NOT implemented. If approved later, it must use an aggregate active-connection/lease view and a grace period; it must never stop the backend because one particular user closes their app. Provider live-feed remains disabled/unprovisioned by default. The Redis cross-process relay is opt-in and still subject to Gate 25 host receipt and recovery acceptance.

Source audit: backend/app/main.py WebSocket route creates/releases unique connection leases and unsubscribes only its own stream in finally; backend/app/ohlcv_stream.py creates a unique stream ID and bounded queue per subscription. Slow-client overflow is isolated to that client and requires reconnect/resnapshot.

### Exact-HEAD test repair and client lifecycle coverage

The prior docs HEAD 36ae4c01f7e09e084a31b8a62f785e13e270f6ac had a malformed JSX role="alert" attribute in AuthPanel, causing two suites to fail during transform. The Google-only test also had an over-escaped button matcher. Both were corrected. Added a browser lifecycle regression test proving pagehide stops the current supervisor and pageshow creates a fresh supervisor when visible/online. Commits: 43fb860b74544030432b51b035de288547e69cb2, ee6c21da678db11b8c1d9c6dd93c84970f915e27, and 78044a3b2419a6b38ecc251fa408f10b97608c54. Latest exact-HEAD CI must finish before acceptance is claimed.

See [Batch 62J-144](WORK_CYCLE_2026-11-22_BATCH62J144_MULTI_USER_WEBSOCKET_LIFECYCLE.md).

### Indicator ledger — unchanged

| Indicator/component | Status | Verified foundation / boundary |
|---|---|---|
| SMA20 | 🟨 | 20-close mean; first valid index 19 |
| EMA20 | 🟨 | SMA-seeded, alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 | Wilder smoothing; first valid index 14 |
| MACD12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population SD; first valid index 19 |
| Shared Indicator Hook | 🟨 | Validated aligned backend output; not fully chart-integrated |
| Footprint | 🟧 | Synthetic educational accumulator only; not exchange-native bid/ask; reference + reviewed blueprint required |
| Heatmap | 🟥 | Not implemented; reference + reviewed blueprint required |
| Liquidation Maps | 🟥 | Not implemented |

No indicator implementation credit. Shared invariants: warm-up nulls; source-index alignment; prefix causality/no future repaint; invalid/gapped bars not silently converted to zero; stale output cleared on identity/timeframe changes; Footprint OFF standard candle spacing, explicit ON spaced clusters. No aggregate indicator % without approved weights/denominator.

### Project-wide progress

- Stage 1 Foundation, Security & Data Integrity: 30/40 = 75% provisional 🟨.
- Stage 2 Market Data Infrastructure: ⬜ NOT SCORED / not officially opened.
- Stage 3 Chart Engine & Timeframe: ⬜ NOT SCORED / not officially opened.
- Stage 4 Indicators & Analytics: ⬜ NOT SCORED / not officially opened.
- Stage 5 Professional UI & Interactive Tools: ⬜ NOT SCORED / not officially opened.
- Stage 6 Hardening, Validation & APK Release: ⬜ NOT SCORED / not officially opened.
- Overall project: NOT SCORED; six-stage weights and denominator remain unapproved.
- Gate 10: 0/10 external criteria formally closed.
- Gates 25, 36 and 38: OPEN; external owner-host and device evidence remains outstanding.
- IP3S Batch 62J-144: PENDING exact-HEAD CI.

ZERO COST; no cloud deployment, payment method, provider credentials, device/Termux work, or main branch changes.


## Batch 62J-145 — real TLS/WSS and multi-user disconnect regression (22 November 2026)

### Verified engineering delta

Added a real loopback Uvicorn TLS/WSS integration test in backend/tests/test_api.py:
- Ephemeral test CA/server certificate, TLS handshake and SAN verification.
- Real WebSocket HTTP Upgrade.
- Allowed HTTPS Origin accepted; disallowed Origin rejected with HTTP 403.
- Untrusted CA rejected.
- Authenticated test-mode exact-series subscription and OHLCV snapshot.
- Application text ping/pong.
- Two distinct test identities with separate entitlements and simultaneous subscriptions.
- Closing User B removes only B's subscription after bounded ASGI cleanup; User A remains connected and receives pong.

The harness uses a fake identity verifier and the backend's non-production legacy token path. Production Firebase HTTPS token exchange, one-time ticket authentication/renewal over WSS, public reverse proxy and real Android WebView remain separate acceptance work.

### Exact-HEAD CI

Final source/test HEAD: f8e41ad68656e82a82d30cf40f720f3ec98ac337.

- Automated Tests 45005536779: SUCCESS — 1,297 passed, 1 skipped, 6 warnings.
- CodeQL 45005536789: SUCCESS.
- Full Git History Secret Audit 45005537134: SUCCESS.
- OCI ARM64 readiness 45005536741: SUCCESS.
- Frontend tests/build and dependency audit passed.
- Backend pip-audit reported no known vulnerabilities.
- Redis TLS/CA/hostname/ACL/AOF fixture passed.
- Synthetic SQLite outbox and metrics benchmarks passed.
- Backend container build and Redis/persistent-volume smoke passed.
- Container UID/GID 10001 and persistent volume/SQLite integrity/restart verified.
- Redis outage fail-closed behavior and recovery passed.
- Trivy HIGH/CRITICAL scan reported zero vulnerabilities in scanned Alpine 3.24.4 OS and Python package targets.

These are CI/local synthetic results. No public WSS, real Firebase project, OCI deployment, owner-host Redis, production provider feed or Android WebView acceptance is claimed.

### Indicator progress — unchanged

| Indicator/component | Status | Verified foundation / boundary |
|---|---|---|
| SMA20 | 🟨 | 20-close mean; first valid index 19 |
| EMA20 | 🟨 | SMA-seeded, alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 | Wilder smoothing; first valid index 14 |
| MACD12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population SD; first valid index 19 |
| Shared Indicator Hook | 🟨 | Backend snapshot/aligned output; not fully chart-integrated |
| Footprint | 🟧 | Synthetic educational prototype only; reference + reviewed blueprint required |
| Heatmap | 🟥 | Not implemented; reference + reviewed blueprint required |
| Liquidation Maps | 🟥 | Not implemented |

No indicator implementation credit. Preserve warm-up nulls, source-index alignment, prefix causality/no repaint, invalid/gapped-bar rejection, stale-output clearing and Footprint OFF normal candle spacing. No aggregate indicator percentage without approved weights/denominator.

### Project-wide progress

- Stage 1 Foundation, Security & Data Integrity: 30/40 = 75% provisional 🟨.
- Stage 2 Market Data Infrastructure: ⬜ NOT SCORED / not officially opened.
- Stage 3 Chart Engine & Timeframe: ⬜ NOT SCORED / not officially opened.
- Stage 4 Indicators & Analytics: ⬜ NOT SCORED / not officially opened.
- Stage 5 Professional UI & Interactive Tools: ⬜ NOT SCORED / not officially opened.
- Stage 6 Hardening, Validation & APK Release: ⬜ NOT SCORED / not officially opened.
- Overall project: NOT SCORED; approved six-stage weights and denominator remain unavailable.
- Gate 10: 0/10 external criteria formally closed.
- Gates 25, 36 and 38: OPEN; owner-host and production/device evidence remains outstanding.
- IPS35/IP3S Batch 62J-145: pending final canonical documentation HEAD CI.

ZERO COST; active branch remains phase-2/market-data-foundation; main untouched; no deployment, payment method, production credentials, device or Termux work.

## Batch 62J-149 — WebSocket downstream subscriber isolation regression

Added `backend/tests/test_ohlcv_stream.py::test_same_series_subscribers_are_isolated_when_one_disconnects`.

The test creates two subscribers for the same exact series, verifies both receive the first accepted update, unsubscribes the first, then verifies the remaining subscriber continues receiving the next update while the disconnected subscriber is closed and receives nothing further. It also verifies subscriber count transitions 2 → 1 → 0.

This proves downstream per-client fan-out isolation only. It does **not** prove dynamic upstream provider subscribe/unsubscribe, shared upstream reference counting, or the mandatory on-demand market subscription feature. Exact-HEAD CI for this new commit is pending.



---

# Batch 62J-164 — Transactional Redis worker startup (23 November 2026)

Source baseline: `36447981ae4d8c3535a47c391c5140f72abe6ac2` on `phase-2/market-data-foundation`.  
Change scope: Redis replica worker lifecycle; no indicator formulas, calculations, hooks, renderers, UI, provider contracts, or deployment changes.

**Finding:** `RedisOhlcvGatewayWorker.start()` previously changed state to `starting` before lease-heartbeat initialization. A startup exception could leave a phantom `starting` state; a later thread-start failure could also leave an orphaned heartbeat.

**Correction:** startup is now transactional. On exception it signals stop, best-effort stops a heartbeat that had started, clears the thread reference, records the exception type, and restores `stopped` or preserves terminal `ownership_lost`. Two regression tests cover temporary Redis/lease unavailability and lost ownership before the consumer thread starts.

**Changed source/test:** `backend/app/ohlcv_redis_worker.py`; `backend/tests/test_ohlcv_redis_worker_lifecycle.py`.  
**New work-cycle report:** `docs/WORK_CYCLE_2026-11-23_BATCH62J164_TRANSACTIONAL_WORKER_STARTUP.md`.

**Exact-HEAD CI:** pending after commit. The predecessor Batch 62J-163 exact HEAD passed Automated Tests, CodeQL, OCI ARM64 image readiness, and full Git-history secret audit. OCI readiness is not an actual cloud deployment.

**Project accounting:** Stage 1 remains 30/40 = 75% provisional; Stages 2–6 remain NOT SCORED; Gate 10 remains 0/10 external criteria formally closed; overall project remains NOT SCORED. No indicator implementation credit is awarded by this backend lifecycle change. Preserve the detailed indicator ledger and its reference-image/blueprint gates. ZERO COST preserved; `main` untouched.


---

## Batch 62J-165 — overall project progress reconciliation (23 November 2026)


- Stage 1 Foundation, Security & Data Integrity: **30/40 = 75% provisional** 🟨.
- Stages 2–6: **NOT SCORED / not officially opened** ⬜.
- Gate 10: **0/10 external acceptance criteria formally closed** 🟥.
- WebSocket Gate 25: **OPEN** 🟧 — local durable digest binding strengthened; authenticated cross-host receipt/key lifecycle still outstanding.
- WebSocket Gate 36: **OPEN** 🟥 — public production WSS, real Firebase project, reverse-proxy and physical Android WebView/network acceptance remain outstanding.
- WebSocket Gate 38: **OPEN** 🟥 — owner-host metrics persistence, backup/retention, alerting and recovery acceptance remain outstanding.
- Overall project: **NOT SCORED**; six-stage weights and total denominator are not approved.
- Significant verified engineering delta: snapshot digest is now intended to be durably bound to the installed checkpoint, and callback mismatch is rejected before Redis startup. This is not Gate 25 closure.

ZERO COST preserved. No paid services, cloud account, hosting, domain, external market-data entitlement, device operation, or publication fee. `main` untouched.


---

## Batch 62J-166 — project progress reconciliation (23 November 2026)


- Stage 1: 30/40 = 75% provisional 🟨.
- Stages 2–6: NOT SCORED / not officially opened ⬜.
- Gate 10: 0/10 external acceptance criteria formally closed 🟥.
- Gate 25: OPEN 🟧 — local digest binding improved by Batch 165; cross-host authenticated receipt and key lifecycle remain.
- Gate 36: OPEN 🟥 — public production WSS, real Firebase, reverse proxy and physical Android WebView acceptance remain.
- Gate 38: OPEN 🟥 — owner-host metrics persistence, backup/retention, alert and recovery acceptance remain.
- Overall project: NOT SCORED; stage weights and denominator are not approved.

ZERO COST. No paid services or external resources. `main` untouched.


---

## Batch 62J-167 — project progress reconciliation (23 November 2026)


- Stage 1: 30/40 = 75% provisional 🟨.
- Stages 2–6: NOT SCORED / not officially opened ⬜.
- Gate 10: 0/10 external acceptance criteria formally closed 🟥.
- Gate 25: OPEN 🟧 — local digest binding and receipt-set validation strengthened; authenticated cross-host receipt/key lifecycle still outstanding.
- Gate 36: OPEN 🟥 — public production WSS, real Firebase, reverse proxy and physical Android WebView acceptance remain.
- Gate 38: OPEN 🟥 — owner-host metrics persistence, backup/retention, alert and recovery acceptance remain.
- Overall project: NOT SCORED; approved stage weights and denominator are not available.

ZERO COST. No paid service, deployment, external credential, device operation or publication fee. `main` untouched.


---

## Batch 62J-168 — project progress reconciliation (23 November 2026)


- Stage 1: 30/40 = 75% provisional 🟨.
- Stages 2–6: NOT SCORED / not officially opened ⬜.
- Gate 10: 0/10 external acceptance criteria formally closed 🟥.
- Gate 25: OPEN 🟧 — local digest binding and receipt-set validation improved; authenticated cross-host receipt/key lifecycle remains.
- Gate 36: OPEN 🟥 — public production WSS, real Firebase, reverse proxy and physical Android WebView acceptance remain.
- Gate 38: OPEN 🟥 — owner-host metrics persistence, backup/retention, alert and recovery acceptance remain.
- Overall project: NOT SCORED; approved stage weights and denominator are unavailable.

ZERO COST. No paid service, deployment, credentials, physical device or publication fee. `main` untouched.


---

## Batch 62J-169 — project progress reconciliation (23 November 2026)


- Stage 1: 30/40 = 75% provisional 🟨.
- Stages 2–6: NOT SCORED / not officially opened ⬜.
- Gate 10: 0/10 external acceptance criteria formally closed 🟥.
- Gate 25: OPEN 🟧 — local digest, receipt-set and pending-recovery safety strengthened; authenticated cross-host receipt/key lifecycle remains.
- Gate 36: OPEN 🟥 — public production WSS, real Firebase, reverse proxy and physical Android WebView acceptance remain.
- Gate 38: OPEN 🟥 — owner-host metrics persistence, backup/retention, alert and recovery acceptance remain.
- Overall project: NOT SCORED; approved stage weights and denominator are unavailable.

ZERO COST. No paid service, deployment, credentials, physical device or publication fee. `main` untouched.


---

# Batch 62J-170 — Gateway checkpoint contract hardening (23 November 2026)

**Base HEAD:** `56f9fb3e034f837fa3cc59f75de9960b46b5f09f` on `phase-2/market-data-foundation`.  
**Scope:** Gate 25 local replica startup validation; no indicator/UI/provider/deployment change.

The gateway runtime now validates the durable checkpoint's replica identity against the replica identity table, exact schema/protocol compatibility, retention-floor range, and complete per-timeframe retention map before constructing a Redis client. Five parameterized regression cases assert that malformed checkpoint state is rejected before Redis client creation. Existing source/generation/cursor/digest checks remain.

**Changed files:** `backend/app/ohlcv_store.py`, `backend/app/ohlcv_redis_gateway_runtime.py`, `backend/tests/test_ohlcv_redis_gateway_runtime.py`, `docs/WORK_CYCLE_2026-11-23_BATCH62J170_GATEWAY_CHECKPOINT_CONTRACT.md`, `docs/INDICATOR_PROGRESS_LEDGER.md`, `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`.

## Progress dashboard

| Area | Verified progress | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 |
| Stage 2 — Market Data Infrastructure | Not scored / not officially opened | ⬜ |
| Stage 3 — Chart Engine & Timeframe | Not scored / not officially opened | ⬜ |
| Stage 4 — Indicators & Analytics | Not scored / not officially opened | ⬜ |
| Stage 5 — Professional UI & Interactive Tools | Not scored / not officially opened | ⬜ |
| Stage 6 — Hardening, Validation & APK Release | Not scored / not officially opened | ⬜ |
| Gate 10 external acceptance | 0/10 formally closed | 🟥 |
| Gate 25 — authenticated snapshot/replica trust | OPEN; local validation improved, cross-host receipts and key lifecycle remain | 🟧 |
| Gate 36 — production WSS/Firebase/device | OPEN; public endpoint, real Firebase, reverse proxy and Android WebView evidence remain | 🟥 |
| Gate 38 — metrics durability/operations | OPEN; owner-host persistence, backup, retention, alerts and recovery remain | 🟥 |
| Overall project | NOT SCORED; weights and denominator not approved | ⬜ |

**Significant verified engineering delta:** the gateway now rejects five additional classes of inconsistent durable checkpoint before opening Redis. This is a local safety improvement, not external gate closure.

## Indicator dashboard — no status promotion

| Indicator | Status | Foundation | Remaining |
|---|---|---|---|
| SMA20 | 🟨 | 20-close mean; index 19 | Overlay, toggle, legend/value, lifecycle/render/performance |
| EMA20 | 🟨 | SMA seed, alpha 2/21; index 19 | Overlay, toggle, legend/value, lifecycle/render/performance |
| RSI14 Wilder | 🟨 | Wilder smoothing; index 14 | Pane, 30/70 guides, toggle, legend/value, lifecycle/render |
| MACD12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, controls and lifecycle |
| Bollinger20,2 | 🟨 | Mean ±2 population SD; index 19 | Three-line overlay, controls, values, lifecycle/render |
| Shared Indicator Hook | 🟨 | Backend aligned snapshot output | Hook tests, chart binding, stale clearing, settings/legend |
| Footprint | 🟧 | Synthetic prototype only | User references, reviewed blueprint, verified bid/ask contract, cluster renderer |
| Heatmap | 🟥 | Not implemented | User references, depth contract, reviewed blueprint, renderer |
| Liquidation Maps | 🟥 | Not implemented | Data provenance, calculation contract, blueprint, renderer |

No aggregate indicator percentage is reported without approved weights/denominator. Footprint/Heatmap references remain mandatory before visual implementation.

## ZERO COST and external acceptance boundary

No paid hosting, provider feed, subscription, domain, deployment, account, production credential, publication fee, or physical-device operation was introduced. OCI CI readiness is not an actual OCI deployment. Public production WSS/Firebase/Android acceptance and owner-host Redis/metrics durability remain unproven. Target remains **24 December 2026**, not a guaranteed completion claim. `main` untouched.


---

# Batch 62J-171 — Gate 38 metrics timestamp contract hardening (23 November 2026)

**Base HEAD:** `0d1ef247aa68fd0946293b91f76e3af3fd608086` on `phase-2/market-data-foundation`.  
**Scope:** local metrics collector validation; no market-data provider, WebSocket wire protocol, indicator formula, UI, or deployment change.

Both metrics collector entry points previously converted caller-supplied timestamps directly with `float()`. This accepted booleans and numeric strings, potentially shifting bucket selection, stale-worker visibility and retention cutoffs. A shared validator now accepts only finite non-negative integer/float epoch seconds, rejects bool/string/NaN/infinity/negative values, and preserves `None` as system time. Validation occurs before opening SQLite. The flush return annotation now accurately includes floating-point timing measurements.

Regression coverage adds 14 cases (7 invalid values × 2 entry points) and asserts malformed input raises `invalid_timestamp` without creating the database file.

## Current progress and acceptance

- Stage 1 Foundation, Security & Data Integrity: **30/40 = 75% provisional** 🟨.
- Stages 2–6: **NOT SCORED / not officially opened** ⬜.
- Gate 10: **0/10 external criteria formally closed** 🟥.
- Gate 25: **OPEN** 🟧 — local snapshot/checkpoint validation improved; authenticated cross-host receipt/key lifecycle and owner-host Redis acceptance remain.
- Gate 36: **OPEN** 🟥 — public production WSS, real Firebase, reverse proxy/certificate lifecycle and physical Android WebView/network acceptance remain.
- Gate 38: **OPEN** 🟧 — local metrics collector validation improved; owner-host persistent volume, backup/restore, retention operations, external alert delivery and recovery drill remain.
- Gate 39: **OPEN** 🟥 — alert acknowledgement and operational recovery acceptance remain.
- Overall project: **NOT SCORED**; approved stage weights and denominator are unavailable.
- Significant verified engineering delta: malformed metrics timestamps are now rejected before any SQLite I/O; 14 regression cases added. This is a local reliability improvement, not external Gate 38 closure.

## Complete indicator dashboard

| Indicator / subsystem | Status | Foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 | 20-close mean; first valid index 19 | Overlay, toggle, legend/value, identity invalidation, lifecycle/render/performance |
| EMA20 | 🟨 | SMA seed, alpha 2/21; first valid index 19 | Overlay, toggle, legend/value, identity invalidation, lifecycle/render/performance |
| RSI14 Wilder | 🟨 | Wilder seed/recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/value, lifecycle/render |
| MACD12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend/values, lifecycle/render |
| Bollinger20,2 | 🟨 | Mean ±2 population SD; first valid index 19 | Three-line overlay, toggle, values, identity invalidation, lifecycle/render/performance |
| Shared Indicator Hook | 🟨 | Backend aligned multi-study snapshot | Hook tests, chart binding, stale clearing, settings/legend, identity/lifecycle |
| Footprint | 🟧 | Synthetic educational prototype only | User reference, reviewed blueprint, verified bid/ask contract, spaced-cluster renderer and acceptance |
| Heatmap | 🟥 | Not implemented | User reference, depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 | Not implemented | Defensible data provenance/calculation contract, blueprint, renderer and tests |

Invariants: warm-up nulls; exact candle alignment; prefix causality/no future repaint; reject invalid/gapped data; clear stale output on identity changes. Footprint OFF keeps standard candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visuals remain gated on user reference images and blueprint review. Aggregate indicator percentage remains NOT SCORED without approved weights/denominator.

## ZERO COST / branch integrity

No paid hosting, provider feed, subscription, domain, deployment, production credential, publication fee, or physical-device action. OCI CI readiness is not deployment. `main` untouched. Target remains **24 December 2026**.


---

# Batch 62J-172 — WebSocket replica relay wire-format hardening (23 November 2026)

**Base HEAD:** `d5cd1418a3a0b449d503803da6527bd3a4c982bc` on `phase-2/market-data-foundation`.  
**Scope:** Gate 25/36 local replica-to-WebSocket event validation; ZERO COST.

Source audit found that `_bar_from_event()` used permissive `int()` and `Decimal()` coercions for untrusted event JSON. The frontend snapshot/stream parser already requires decimal-string timestamps and canonical decimal-string OHLCV values. The backend relay now enforces the same wire representation before constructing an `OhlcvBar`:

- Nanosecond fields must be unsigned ASCII decimal strings; optional provider-output timestamp may remain null.
- OHLCV prices and volume must match the canonical decimal-string grammar; numeric JSON values, booleans, exponent notation, NaN and non-canonical decimal forms are rejected.
- New regression matrix covers malformed timestamp and decimal fields, plus a valid provider-output timestamp.

Batch 62J-171 exact-HEAD CI was fully successful: Automated Tests [45161627257](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45161627257), CodeQL [45161627265](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45161627265), Secret Audit [45161627305](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45161627305), and OCI ARM64 readiness [45161627212](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45161627212) all SUCCESS. Backend tests: 1,336 passed, 1 skipped, 6 warnings; frontend tests: 306 passed.

## Project status

- Stage 1: **30/40 = 75% provisional** 🟨.
- Stages 2–6: **NOT SCORED / not officially opened** ⬜.
- Gate 10: **0/10 external criteria formally closed** 🟥.
- Gate 25: **OPEN** 🟧 — local checkpoint and relay validation improved; authenticated cross-host immutable receipt/key lifecycle and owner-host Redis acceptance remain.
- Gate 36: **OPEN** 🟥 — local relay contract improved; public production WSS, real Firebase, reverse proxy/certificate lifecycle and Android WebView/network acceptance remain.
- Gate 38: **OPEN** 🟧 — local metrics collector hardened; owner-host persistence, backup/restore, retention operations, external alert delivery and recovery drill remain.
- Gate 39: **OPEN** 🟥 — alert acknowledgement and operational recovery acceptance remain.
- Overall project: **NOT SCORED**; approved stage weights and denominator unavailable.
- Significant verified engineering delta: backend replica relay now rejects malformed timestamp/decimal representations consistently with frontend protocol parsing. This does not establish a public production endpoint or external gate closure.

## Complete indicator status

SMA20 🟨 Foundation; EMA20 🟨 Foundation; RSI14 Wilder 🟨 Foundation; MACD12/26/9 🟨 Foundation; Bollinger20,2 🟨 Foundation; Shared Indicator Hook 🟨 Foundation; Footprint 🟧 synthetic prototype; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. Full formulas, first-valid indices, invariants and remaining acceptance are recorded in `docs/INDICATOR_PROGRESS_LEDGER.md`.

ZERO COST. No paid hosting, market-data entitlement, subscription, domain, deployment, production credential, publication fee or physical-device action. `main` untouched. Target remains **24 December 2026**.


---

# Batch 62J-173 — CI acceptance and project reconciliation (23 November 2026)

Batch 62J-172 corrected final source/test HEAD `a9d001885b0b524bc33427add30584e1984680bf` passed all four exact-HEAD workflows:

- Automated Tests [45162694296](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45162694296): **SUCCESS** — 1,347 backend tests passed, 1 skipped, 6 warnings; 306 frontend tests passed; Redis TLS, SQLite outbox/metrics benchmarks, backend container smoke, dependency audit and image scan passed.
- CodeQL [45162694141](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45162694141): **SUCCESS**.
- Full Git History Secret Audit [45162694099](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45162694099): **SUCCESS**.
- OCI ARM64 Image Readiness [45162694385](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45162694385): **SUCCESS**.

## Project indicators

- Stage 1 Foundation, Security & Data Integrity: **30/40 = 75% provisional** 🟨.
- Stage 2 Market Data Infrastructure: **NOT SCORED / not officially opened** ⬜.
- Stage 3 Chart Engine & Timeframe: **NOT SCORED / not officially opened** ⬜.
- Stage 4 Indicators & Analytics: **NOT SCORED / not officially opened** ⬜.
- Stage 5 Professional UI & Interactive Tools: **NOT SCORED / not officially opened** ⬜.
- Stage 6 Hardening, Validation & APK Release: **NOT SCORED / not officially opened** ⬜.
- Gate 10: **0/10 external acceptance criteria formally closed** 🟥.
- Gate 25: **OPEN** 🟧 — local checkpoint/relay contract stronger; cross-host authenticated receipt/key lifecycle and owner-host Redis acceptance remain.
- Gate 36: **OPEN** 🟥 — public WSS, real Firebase, reverse proxy/certificate lifecycle and Android WebView/network acceptance remain.
- Gate 38: **OPEN** 🟧 — local metrics timestamp contract hardened; owner-host persistence, backup/restore, retention operations, external alerts and recovery drill remain.
- Gate 39: **OPEN** 🟥 — alert acknowledgement and operational recovery acceptance remain.
- Overall project: **NOT SCORED**; approved weights and denominator remain unavailable.

## Complete indicator dashboard

SMA20 🟨 Foundation; EMA20 🟨 Foundation; RSI14 Wilder 🟨 Foundation; MACD12/26/9 🟨 Foundation; Bollinger20,2 🟨 Foundation; Shared Indicator Hook 🟨 Foundation; Footprint 🟧 synthetic prototype; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. Detailed formulas, first-valid indices, invariants and remaining acceptance are maintained in `docs/INDICATOR_PROGRESS_LEDGER.md`.

ZERO COST preserved. OCI readiness is not deployment. No paid provider, hosting, domain, production credential, publication fee or physical-device action. `main` untouched. Target remains **24 December 2026**.


---

## Batch 62J-176 — synthetic-only Worker/DO proof (23 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Latest code/test HEAD with exact-HEAD CI:** `f9a6242c83c065799d1ed02f8c8870d8c9ef5ffe`  
**Documentation commits after code/test HEAD:** Batch 62J-176 report and indicator/dashboard reconciliation only; no runtime source changed after the verified code/test HEAD.  
**Main:** untouched.

### Significant engineering progress

An isolated synthetic-only Cloudflare Worker + per-series Durable Object proof was added:
- Worker health, synthetic status and bounded 50-bar OHLCV snapshot endpoints.
- Local proof-token gate, allow-listed local Origin, bounded JSON requests.
- Hashed, purpose-bound, series-bound single-use ticket with 90-second expiry.
- Durable sequence gate with contiguous cursor enforcement.
- Hibernation API acceptance and serialized WebSocket attachment code.
- Authorized same-series synthetic fan-out; no provider socket, polling loop, timer or alarm.
- Local Wrangler configuration with workers.dev and preview URLs disabled.
- Local secret files ignored by Git.
- 16 Node proof tests, separate from Vitest discovery.

**Proof limitation:** the Node suite tests pure ticket/sequence behavior and Worker request boundary. It does not execute a real Cloudflare Durable Object runtime, WebSocketPair handshake, forced hibernation/rehydration, or Android/browser end-to-end session. No Wrangler runtime smoke or deployment occurred. This proof is not production-ready and is not wired into the FastAPI backend or the main app.

### Exact-HEAD verification

For code/test HEAD `f9a6242c83c065799d1ed02f8c8870d8c9ef5ffe`:

- Automated Tests [45168168543](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45167249268): SUCCESS.
  - Synthetic proof tests: 15 passed, 0 failed.
  - Frontend: 306 passed across 34 test files.
  - Backend: 1,347 passed, 1 skipped, 6 warnings.
  - npm audit: 0 vulnerabilities.
  - pip-audit: no known vulnerabilities.
  - Dedicated Redis TLS fixture, synthetic SQLite outbox benchmark, metrics benchmark, backend container build/smoke and HIGH/CRITICAL image scan passed.
- CodeQL [45168168621](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45167249876): SUCCESS for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [45168168356](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45167250254): SUCCESS.
- OCI ARM64 Image Readiness [45168168447](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45167249525): SUCCESS.

The skipped backend pytest TLS integration case is run separately by the dedicated isolated Redis TLS fixture step. The CI results are not a deployed Worker or production WSS acceptance.

### Stage and gate indicators — no speculative score increase

| Project area | Current indicator | Decision |
|---|---|---|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 30/40 = 75% provisional | Unchanged |
| Stage 2 — Market Data Infrastructure | 🟨 Synthetic proof source/test added; not scored | Runtime integration, auth parity, replay, provider demand and external host acceptance still open |
| Stage 3 — Chart Engine & Timeframe | ⬜ Not scored | Unchanged |
| Stage 4 — Indicators & Analytics | ⬜ Not scored | Unchanged |
| Stage 5 — Professional UI & Interactive Tools | ⬜ Not scored | Unchanged |
| Stage 6 — Hardening, Validation & APK Release | ⬜ Not scored | Unchanged |
| Gate 10 external acceptance | 🟥 0/10 closed | Unchanged |
| Overall project | NOT SCORED | No approved weighted denominator |

### Indicator status — unchanged

- SMA20: 🟨 Foundation.
- EMA20: 🟨 Foundation.
- RSI14 Wilder: 🟨 Foundation.
- MACD 12/26/9: 🟨 Foundation.
- Bollinger20,2: 🟨 Foundation.
- Shared Indicator Hook: 🟨 Foundation.
- Footprint: 🟧 Synthetic prototype only.
- Heatmap: 🟥 Not implemented.
- Liquidation Maps: 🟥 Not implemented.

No indicator calculation, hook, chart binding, pane, renderer, UI setting or indicator-specific test changed. No indicator credit is awarded.

### Remaining red gates

1. Real local Wrangler/Miniflare runtime smoke and pinned toolchain review.
2. Actual DO WebSocket handshake and ticket consumption.
3. Two-client same-series fan-out and two-series isolation.
4. Forced hibernation/rehydration and attachment restoration.
5. Unauthenticated socket capacity timeout/cleanup and slow-consumer tests.
6. Snapshot-to-live cursor continuity and durable replay.
7. Firebase production auth parity.
8. Public HTTPS/WSS and Android-device acceptance.
9. Provider-side demand coordination and recurring-$0 lawful provider source.
10. Production persistence, backup and restore acceptance.

### Zero-cost and target-date controls

No deployment, Cloudflare account, billing activation, payment method, domain, production credential, provider key, or live market-data connection was used. No paid service or package dependency was added. Target date remains **24 December 2026**, not a guaranteed completion claim.

**Batch 62J-176 decision:** meaningful isolated synthetic infrastructure increment; Stage 2 remains unscored and production acceptance remains open. No project-wide or indicator percentage is increased from this batch.


---

## Batch 62J-177 — latest project and indicator reconciliation (23 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Latest code/test HEAD at this reconciliation:** `b752d6ca4b2317e8a7ab9f71e2bc23ff937eb4aa`  
**Main:** untouched. **ZERO COST:** preserved.  
**Exact-HEAD CI:** pending; no CI success is claimed for this new code/test HEAD yet.

### Significant engineering progress

The isolated synthetic-only Worker/DO proof received:
- Atomic snapshot watermark initialization to prevent a concurrent first event from rewinding cursor 51 back to 50.
- Fail-closed validation of persisted cursor values and incoming sequence bounds [51, 1,000,000,000].
- Strict serialized WebSocket attachment validation on constructor restoration and message handling.
- Regression coverage for both initialization/update orderings, corrupt/out-of-range cursors, one-time ticket consumption, snapshot delivery, exact-series fan-out, contiguous event sequencing, malformed attachment restoration and attachment-deserialization exceptions.
- Synthetic Node proof suite increased from 16 to **20 tests**. No new dependency or hosted resource was added.

This is local proof/test-double evidence. It is not an actual Cloudflare runtime, browser WebSocket, production authentication or deployed WSS acceptance.

### Full indicator dashboard

| Indicator / subsystem | Status | Foundation | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Chart overlay, toggle, legend/current value, identity/lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19 | Overlay, toggle, legend/current value, identity/lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean; Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33 | Dedicated pane, lines, histogram, zero line, toggle/legend/latest values, lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/lifecycle/render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | Exact-snapshot aligned multi-study output | Hook tests, chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator, not exchange-native volume | User reference image(s), reviewed blueprint, verified data contract, cluster layout and renderer |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), reviewed blueprint, validated data contract, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render/data contract | Defensible provenance/methodology, reviewed blueprint, renderer and tests |

**Indicator invariants:** warm-up `null`; exact source-index alignment; prefix causality; reject invalid/gapped data; clear stale output on identity/timeframe changes; no future-candle leakage; test calculation/rendering/lifecycle/accessibility/performance separately; Footprint OFF keeps normal candle spacing; Footprint/Heatmap visuals require user reference images and blueprint review. Aggregate indicator completion remains **NOT SCORED**.

### Project-wide progress indicators

- Stage 1 Foundation, Security & Data Integrity: 🟨 **30/40 = 75% provisional**, unchanged.
- Stage 2 Market Data Infrastructure: 🟨 synthetic-only proof hardened; **NOT SCORED** until real local runtime integration and its acceptance tests are complete.
- Stage 3 Chart Engine & Timeframe: ⬜ **NOT SCORED**.
- Stage 4 Indicators & Analytics: ⬜ **NOT SCORED**.
- Stage 5 Professional UI & Interactive Tools: ⬜ **NOT SCORED**.
- Stage 6 Hardening, Validation & APK Release: ⬜ **NOT SCORED**.
- Gate 10 external acceptance: 🟥 **0/10 formally closed**.
- Gate 25 snapshot/replica custody: 🟧 **OPEN**.
- Gate 36 public WSS/Firebase/Android network lifecycle: 🟥 **OPEN**.
- Gate 38 owner-host telemetry persistence/restore/operations: 🟧 **OPEN**.
- Gate 39 operational alert acknowledgement/recovery: 🟥 **OPEN**.
- Overall project: **NOT SCORED**; approved stage weights and denominator remain unavailable.
- Target date: **24 December 2026**, planning target only.

### Remaining WebSocket work, ordered by dependency

1. Pinned local Wrangler runtime smoke with hosted deployment disabled.
2. Actual Durable Object WebSocketPair handshake and one-time ticket consumption.
3. Real-runtime same-series two-client fan-out and cross-series isolation.
4. Hibernation/eviction and serialized attachment restoration.
5. Unauthenticated socket cleanup/timeout and slow-consumer behavior.
6. Snapshot-to-live cursor continuity and bounded durable replay.
7. Production authentication, public WSS and Android acceptance remain external gates; no real market-data provider or transaction service is connected.

**Decision:** the cursor race and attachment-validation gaps are addressed in source/tests. Stage and project percentages remain unchanged pending verified acceptance evidence.


---

## Batch 62J-178 — WebSocket unauthenticated-session lifecycle (23 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Latest code/test HEAD:** `264b54fbb87b96133d13dd7f82089bde4cd9d47f`  
**Main:** untouched. **ZERO COST:** preserved.  
**CI for this exact code/test HEAD:** no completed status was returned; pending verification.  
**Real Cloudflare runtime acceptance:** pending.

### Significant progress
- Unauthenticated WebSocket sessions now have a fixed 15-second deadline.
- Durable Object storage alarms schedule the earliest pending deadline.
- Expired unauthenticated sockets close with code 4408.
- Alarm processing preserves later pending sessions and removes the alarm when no unauthenticated session remains.
- Expired authentication attempts are rejected before ticket consumption and checked again after asynchronous ticket consumption.
- Three new regression tests cover alarm expiry/scheduling, authorized-socket alarm cleanup and expired authentication without ticket consumption.
- Synthetic Node proof suite now declares **23 tests**, up from 20. CI execution has not yet been confirmed for the current code/test HEAD.

### Full indicator dashboard — unchanged
| Indicator | Status | Foundation | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value, lifecycle/render/performance tests |
| EMA20 | 🟨 | SMA seed; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 | Initial 14-change mean; Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value |
| MACD12/26/9 | 🟨 | EMA12−EMA26; first valid index 25; signal/histogram index 33 | Dedicated pane, lines, histogram, zero line, toggle/legend/latest values |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population standard deviations; first valid index 19 | Three-line overlay, toggle, latest values, lifecycle/render/performance tests |
| Shared Indicator Hook | 🟨 | Exact-snapshot aligned multi-study output | Hook tests, chart binding, stale-output clearing, settings/legend integration |
| Footprint | 🟧 | Synthetic prototype only | User reference image(s), blueprint review, verified data contract and renderer |
| Heatmap | 🟥 | Not implemented | User reference image(s), blueprint review, data contract and renderer |
| Liquidation Maps | 🟥 | Not implemented | Methodology/provenance, blueprint, data contract and renderer |

Indicator invariants remain: warm-up null, exact candle-index alignment, prefix causality, invalid/gap rejection, stale-output clearing on identity/timeframe changes, no future-candle leakage, and separate calculation/render/lifecycle/accessibility/performance acceptance. Footprint OFF preserves normal candle spacing; ON alone enables spaced clusters. Footprint/Heatmap visuals wait for user references and blueprint review. Indicator aggregate remains **NOT SCORED**.

### Project progress indicators
- Stage 1 Foundation, Security & Data Integrity: 🟨 **30/40 = 75% provisional**, unchanged.
- Stage 2 Market Data Infrastructure: 🟦 **Synthetic-only proof increment; NOT SCORED** until local runtime acceptance.
- Stage 3 Chart Engine & Timeframe: ⬜ **NOT SCORED**.
- Stage 4 Indicators & Analytics: ⬜ **NOT SCORED**.
- Stage 5 Professional UI & Interactive Tools: ⬜ **NOT SCORED**.
- Stage 6 Hardening, Validation & APK Release: ⬜ **NOT SCORED**.
- Gate 10 external acceptance: 🟥 **0/10 formally closed**.
- Gate 25 snapshot/replica custody: 🟧 **OPEN**.
- Gate 36 public WSS/Firebase/Android lifecycle: 🟥 **OPEN**.
- Gate 38 owner-host telemetry persistence/restore/operations: 🟧 **OPEN**.
- Gate 39 operational alert acknowledgement/recovery: 🟥 **OPEN**.
- Overall project: **NOT SCORED**; approved weighted denominator remains unavailable.
- Target: **24 December 2026**, planning target only.

### Remaining WebSocket acceptance queue
1. Pinned local Wrangler/Miniflare runtime smoke; no hosted deployment.
2. Actual WebSocketPair handshake and one-time ticket consumption.
3. Runtime same-series fan-out and cross-series isolation.
4. Hibernation/eviction and attachment restoration.
5. Alarm expiry and close-code verification in runtime.
6. Slow-consumer/backpressure tests using documented runtime support.
7. Snapshot-to-live cursor continuity and bounded durable replay.
8. Production authentication, public WSS and Android acceptance remain external gates.

**Decision:** unauthenticated-session retention is addressed in synthetic source and test coverage. CI and real runtime acceptance remain pending; project/indicator percentages do not increase from this batch.


---

## Batch 62J-179 — WebSocket restored-socket validation (23 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Worker commit:** `90a9a05cd5a9b105608ebba27f0d80b1ed3efa3e`  
**Regression-test commit:** `253faf401a03e6441a3842f1403aae82835d8118`  
**Work-cycle documentation:** `docs/WORK_CYCLE_2026-11-23_BATCH62J179_WEBSOCKET_RESTORED_SOCKET_HARDENING.md`  
**Main:** untouched. **ZERO COST:** preserved.

### Significant progress
- Constructor restoration now tolerates a malformed/closed socket whose `close()` throws; valid restored sockets continue through initialization.
- Synthetic fan-out validates the complete serialized attachment before a socket can be treated as an authorized recipient.
- Send-failure cleanup is defensive and cannot escape the fan-out loop merely because `close()` also throws.
- Two regression test definitions added. Synthetic Node proof suite now declares 25 cases; execution/pass status is not asserted by the definition count.
- Runtime acceptance remains open; no public deployment or paid service was used.

### Project progress indicators — unchanged
- Stage 1 Foundation, Security & Data Integrity: 🟨 **30/40 = 75% provisional**.
- Stage 2 Market Data Infrastructure: 🟦 **Synthetic-only proof increment; NOT SCORED** until local runtime acceptance.
- Stage 3 Chart Engine & Timeframe: ⬜ **NOT SCORED**.
- Stage 4 Indicators & Analytics: ⬜ **NOT SCORED**.
- Stage 5 Professional UI & Interactive Tools: ⬜ **NOT SCORED**.
- Stage 6 Hardening, Validation & APK Release: ⬜ **NOT SCORED**.
- Gate 10 external acceptance: 🟥 **0/10 formally closed**.
- Gate 25 snapshot/replica custody: 🟧 **OPEN**.
- Gate 36 public WSS/Firebase/Android lifecycle: 🟥 **OPEN**.
- Gate 38 owner-host telemetry persistence/restore/operations: 🟧 **OPEN**.
- Gate 39 operational alert acknowledgement/recovery: 🟥 **OPEN**.
- Overall project: **NOT SCORED**; approved weighted denominator remains undefined.
- Target date: **24 December 2026**, planning target only.

### Full indicator ledger — unchanged
- SMA20 🟨 Foundation; 20-close mean, first valid index 19.
- EMA20 🟨 Foundation; SMA seed, alpha 2/21, first valid index 19.
- RSI14 Wilder 🟨 Foundation; initial 14-change average, Wilder recurrence, first valid index 14.
- MACD 12/26/9 🟨 Foundation; EMA12−EMA26, first MACD index 25, signal/histogram index 33.
- Bollinger20,2 🟨 Foundation; 20-close mean ±2 population standard deviations, first valid index 19.
- Shared Indicator Hook 🟨 Foundation; exact-snapshot alignment foundation only.
- Footprint 🟧 Synthetic prototype only; visual work waits for user reference image(s) and blueprint review.
- Heatmap 🟥 Not implemented; visual work waits for user reference image(s) and blueprint review.
- Liquidation Maps 🟥 Not implemented; methodology/provenance and blueprint outstanding.

Indicator invariants remain warm-up null, exact index alignment, prefix causality/no future leakage, invalid/gap rejection, stale-output clearing on identity/timeframe changes, and separate calculation/render/interaction/lifecycle/accessibility/performance acceptance. Footprint OFF preserves standard candle spacing; ON alone enables spaced clusters. Indicator aggregate remains **NOT SCORED**.

**Decision:** Batch 62J-179 closes two source-level WebSocket defensive gaps. It does not change indicator readiness, stage scores, Gate 10, or overall project score. CI exact-head and real local runtime results must be independently verified before any acceptance status changes.


### Batch 62J-179 verification note
The root package manifest/lockfile currently contain no Wrangler or Miniflare dependency, so a pinned local Cloudflare runtime smoke remains an explicit toolchain task rather than an assumed pass. The existing push workflow is configured for this branch and runs Node syntax plus the synthetic Worker test file. The available connector returned no combined status entries or workflow-run records for the current commits; because its workflow-run helper filters to pull-request-triggered runs, push-run completion remains **unverified**, not declared absent or successful. See the Batch 62J-179 work-cycle record for the full verification boundary.


### Batch 62J-180 — CI failure repaired
The push CI failure at `2591e6071ba966114895256e51aa3fb99ea8001f` was isolated to a syntax error in the malformed-attachment regression test: its callback contained `await` but was not declared `async`. The callback is now asynchronous in commit `ae9a6368f824e4c2fac2b1c9d18ad2fba9fc41ca`. This is a test-harness correction, not a production Worker logic change. A fresh push-triggered CI run must confirm the fix. Indicator implementation/progress remains unchanged; see the indicator ledger for the complete mathematical contract.


### Batch 62J-180 — alarm test expectation corrected
The first test-harness syntax issue was corrected, allowing all 25 synthetic Worker tests to execute. CI then exposed one incorrect expected value in the alarm test: it expected the pending socket's deadline even though another unauthenticated socket had an earlier, already-overdue deadline. The production scheduler intentionally selects the earliest deadline. The assertion now checks the overdue deadline first, then verifies the pending deadline after alarm processing. Commit: `b0cc4682156e65ce94f8f4203899f3e7baee3070`. This correction changes only the test assertion; no project or indicator score is increased until the new CI run completes.


### Batch 62J-180 — final CI verified

Latest corrected checkpoint `07186190e98a4e9418664990a1a84acbc6fb3e13` is green across all configured workflows: Automated Tests `45173027719`, Full Git History Secret Audit `45173027724`, CodeQL `45173027753`, and OCI ARM64 Image Readiness `45173027840`. Synthetic Worker tests: **25/25 passed**. Frontend unit tests/build and backend tests/container smoke checks also succeeded. This confirms the test-harness fixes and existing project CI scope, but does not replace a local Cloudflare runtime WebSocket acceptance test. Project stage scores, indicator status and overall NOT SCORED decision remain unchanged.


---

## Batch 62J-181/182 — CME session identity frontend integration (23 November 2026)

The frontend now accepts the backend's versioned `CME_SESSION_V1` identity for `1d`, `1w`, `1M`, and `3M` only when both the canonical calendar ID and exact loaded version are present. REST parsing, market-data identity validation, keyed store isolation, and WebSocket event validation use the same rules. The instrument catalog now exposes the canonical instrument's session calendar and only a uniquely loaded release version. `CandlestickChart` selects the CME policy only when the exact release is available; incomplete metadata falls back to the existing UTC policy. Regression coverage was added across backend catalog, frontend parser/store/protocol, bucket selection, and chart lifecycle.

Implementation checkpoint: `af3746fc39ac75a842a0199ad09304b008f19107`. Exact-HEAD CI is **NOT YET VERIFIED**. Previous verified CI checkpoint remains `07186190e98a4e9418664990a1a84acbc6fb3e13`; its green result must not be transferred to this new implementation. Full technical record: `docs/WORK_CYCLE_2026-11-23_BATCH62J181_CME_SESSION_FRONTEND_INTEGRATION.md`.

No indicator formula, calculation hook, renderer, or visual UI changed. All indicator statuses and project scores remain unchanged. The calendar fixture `test-only-2024.01` is synthetic-only and is not an official CME schedule.
