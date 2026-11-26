# Latest implementation checkpoint — Batch 91 (26 November 2026)

**Status:** IMPLEMENTATION IN PROGRESS — not accepted.  
**Active branch:** `phase-2/market-data-foundation`; application `main` remains untouched.  
**Latest source/test SHA:** `2d0d7e9a2bf1190961126105d65f77d9926e6789`.  
**Implemented:** provider-neutral protocol metadata and validators; canonical cursor and SHA-256 format validation; fixed-position canonical event digest encoding and stable vector; additive snapshot and stream metadata parsing; optional canonical series identity propagation; synthetic-only canonical bar/snapshot/update envelope builders; REST `/v1/ohlcv` exact-series identity path; WebSocket status-first auth, explicit subscribe, canonical snapshot/update, and versioned text-ping/pong; Worker Node, Miniflare and Durable Object regression coverage updated to the new contract.  
**Latest exact-head CI:** 4/4 terminal SUCCESS on source/test SHA `2d0d7e9a2bf1190961126105d65f77d9926e6789`: Automated Tests run 45746150652; CodeQL 45746150693; Full Git History Secret Audit 45746150657; OCI ARM64 45746150726. Logs confirm frontend 35 files / 331 tests, Worker Node 33/33, Miniflare 1/1, Durable Object 15/15, backend pytest 1,435 passed / 1 skipped / 6 warnings, frontend build success, and backend container smoke success. These checks apply to the exact source/test SHA, not later documentation-only HEAD. Formal Batch 91 acceptance still requires owner review; do not mark accepted yet.  
**Snapshot/live boundary hardening:** Worker now serializes snapshot establishment with event persistence/fan-out through a Durable Object-local operation queue; the subscription reads the latest sequence watermark inside that queue before computing the digest and activating fan-out. Added a Durable Object runtime regression test for queue ordering. This is synthetic-proof coordination only, not durable replay/ACK storage. Durable event persistence, replay reads, ACK receipt persistence, and resume recovery remain Batch 92 scope, not claimed complete here.  
**Cron relay:** Worker `dezzta-chart-runner-relay` exists at `https://dezzta-chart-runner-relay.deszztagd377.workers.dev`; `CRON_SECRET` and `GITHUB_TOKEN` are not configured. Runner repository contains `preflight.yml` and the manual Batch89 workflow. The cron-job.org 10-minute schedule remains inactive until both secrets are configured and manual dispatch returns HTTP 202. Never schedule Batch89 every 10 minutes.  
**Controls:** ZERO COST; no provider/live feed, Firebase production auth, broker/order endpoint, production secret, or deployment added; no application `main` changes. Batch 92/93 remain gated behind Batch 91 acceptance.  
**Detailed reconciliation:** `docs/WORK_CYCLE_2026-11-26_BATCH91_IMPLEMENTATION_RECONCILIATION.md` records the 43-commit implementation diff, exact-head 4/4 CI evidence, test counts, explicit Batch 92/93 boundaries and owner acceptance gate.

---

# Superseded design-only snapshot — Batch 91 (26 November 2026)

The earlier design-only note below is retained as historical context and is superseded by the implementation checkpoint above. Batch 91 source changes are present at source/test SHA `2d0d7e9a2bf1190961126105d65f77d9926e6789`, with exact-head required CI 4/4 SUCCESS. The implementation reconciliation and remaining owner-review gate are documented in `docs/WORK_CYCLE_2026-11-26_BATCH91_IMPLEMENTATION_RECONCILIATION.md`. Do not interpret the historical statement "No Batch 91 source files have been changed" as current status.

---

# Latest verified update — Batch 90 (26 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Exact source/test SHA:** `9a2f2b9faebdcaf1e97e93c6dfe85a2c93319fbb`  
**Batch 90:** PASS — additive SQLite schema migration, version ledger, local Miniflare SQLite runtime, schema constraints, event uniqueness, legacy KV preservation, and DO eviction persistence verified.  
**Exact-head CI:** 4/4 terminal SUCCESS — Automated Tests run 45742201070; CodeQL 45742201040; Full Git History Secret Audit 45742201069; OCI ARM64 45742201064. Backend pytest: 1,435 passed, 1 skipped, 6 warnings; frontend Vitest: 34 files / 325 tests passed; Worker Node proof 31/31; Miniflare 1/1; Durable Object runtime 12/12; frontend build and backend container smoke test passed.  
**Batch 91:** NEXT — provider-neutral API contract; inspect and reconcile the existing OHLCV snapshot/update contracts before adding any envelope.  
**Batch 92–93:** OPEN — atomic durable event payload/digest/high-water, bounded replay, ACK, durable receipts and RESUME.  
**Batch 94–95:** OPEN/BLOCKED — lawful zero-cost provider gate and public WSS/browser/Android E2E.  
**Stage accounting:** Stage 1 remains official active at 30/40 criteria = 75% provisional; Gate 10 0/10 formally closed. No stage transition or overall progress score is inferred from this backend batch.  
**Controls:** ZERO COST; `main` untouched; no Cloudflare resources created/deployed; no live provider enabled; synthetic proof remains synthetic-only; delivery target ~24 December 2026.

Detailed evidence: `docs/WORK_CYCLE_2026-11-26_BATCH90_SQLITE_SCHEMA_MIGRATION.md`.

---

# Latest verified project status — Batch 72 (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Audited source/test SHA:** `6a6e9e82ed2de725bef94e8ed1fa7f28c60e0a49`; Batch 71 CI 4/4 terminal SUCCESS.  
**Cloudflare:** repo contains a synthetic-only Worker/SQLite DO proof; it is not deployed or wired to production FastAPI/Firebase/live provider/UI. Connected account inventory currently has no Worker, Pages project, Tunnel, DO namespace, Zone or Worker domain. Workers Free + SQLite DO are candidate zero-cost edge components within quota; Containers are paid-only and excluded.  
**Stage:** Stage 1 official active, 30/40 = 75% provisional 🟨; Gate 10 0/10 🟥. Stage 2 preparatory; Stage 4 gated. Overall and IP3S remain not scored.  
**Indicators:** 6 foundation (SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2, Shared Hook); Footprint PRO 2GD gated; 5 advanced studies open. 28 declarations are not completion.  
**Gate 25 / WebSocket:** production transport, Firebase identity, live-provider provenance, durable per-gateway ACK/receipt and Gate 36 browser/Android WSS remain open. Redis destructive retention remains blocked.  
**Controls:** ZERO COST; `main` untouched; no paid hosting/data; no Cloudflare resources created/deployed; target ~24 December 2026.

Full Batch 72 evidence: `docs/WORK_CYCLE_2026-11-25_BATCH72_CLOUDFLARE_INVENTORY_ZERO_COST_WEBSOCKET_PATH.md`.

---

# Latest verified CI closure — Batch 62J-233 (25 November 2026)

**Active branch:** phase-2/market-data-foundation  
**Code/test SHA:** bd4904b52d29b3ec456da91014e90922fec35f21  
**Code/test CI:** 4/4 terminal SUCCESS on that exact SHA:
- Automated Tests run 45520805106 — 41/41 steps, backend pytest 1,394 passed / 1 skipped / 6 warnings in 66.76s. FIFO non-blocking regression test PASSED.
- CodeQL run 45520805120 — Python 8/8 + JavaScript/TypeScript 8/8 steps.
- OCI ARM64 run 45520805221 — 7/7 steps.
- Full Git History Secret Audit run 45520805267 — 6/6 steps.
All workflows are terminal; no active run remains for the code/test SHA.

**Source change:** POSIX private-key loader now uses O_NOFOLLOW + O_NONBLOCK before fstat; FIFO/device paths cannot block before regular-file validation. Permission error wording reflects the true no-group/world-access invariant.
**Gate 25:** repository-side file boundary hardened. Owner-host custody, authenticated remote snapshot transfer, persisted receipt retrieval from every gateway, restart re-verification, and durable per-gateway high-water ACK remain 🟥 OPEN.
**WebSocket:** Gate 36 public HTTPS/WSS, reverse proxy/TLS, production runtime, Firebase production sign-in/entitlement/revocation E2E and real browser/Android lifecycle/multi-instance acceptance remain 🟥 OPEN. Redis destructive retention remains 🟧 BLOCKED.
**Indicators:** 28 focused indicator declarations = 21 calculation + 7 shared-hook; no new indicator tests or UI integrations in this batch. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook 🟨 foundation-only; Footprint PRO 2GD 🟧 synthetic/reference-gated; Volume Profile variants, Heatmap and Liquidation Maps 🟥 incomplete/not integrated. Aggregate completion ⚪ NOT SCORED.
**Project:** Stage 1 30/40 = 75% provisional 🟨 (inherited); Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 0/10 🟥; overall ⚪ NOT SCORED; IP3S ⚪ NOT SCORED.
**Controls:** ZERO COST; main untouched; no Vercel deployment; no destructive Redis action; APK target around 24 December 2026.

---

# Latest verified update — Batch 62J-232 (25 November 2026)

**Branch:** phase-2/market-data-foundation  
**Parent:** 821b3b6602fa2568bf2e103bb725651b1a60de6c  
**Change:** POSIX key loading adds O_NONBLOCK beside O_NOFOLLOW so FIFO/device paths cannot block before fstat rejects non-regular files. Added POSIX FIFO regression test. Permission diagnostic now accurately describes owner-only/no group-world access rather than implying exactly 0600.  
**CI:** pending exact new SHA; parent CI is not inherited.  
**Gate 25:** repository file-open boundary hardened; owner-host custody, authenticated remote transfer, per-gateway receipt retrieval, restart re-verification and durable high-water ACK remain 🟥 OPEN.  
**Indicator inventory:** 28 focused declarations = 21 calculation + 7 shared-hook; FIFO regression is backend security coverage and excluded. SMA20/EMA20/RSI14/MACD/Bollinger/Shared Hook 🟨 foundation; Footprint 🟧 gated; Volume Profile variants/Heatmap/Liquidation Maps 🟥 incomplete/not integrated. Aggregate ⚪ NOT SCORED.  
**Project:** Stage 1 30/40 = 75% provisional 🟨; Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 0/10 🟥; overall ⚪ NOT SCORED; IP3S ⚪ NOT SCORED.  
**Controls:** ZERO COST; main untouched; no Vercel deployment; no destructive Redis action; APK target around 24 December 2026.

---

# Latest verified checkpoint — Batch 62J-231 (24 November 2026)

**Active branch:** phase-2/market-data-foundation  
**Exact code/test HEAD:** 1b7096566030f7c7775958c1fb60fbe628a3b7f1  
**Latest code/test batch:** Batch 62J-230 added three explicit Gate 25 private-key loader regression tests: POSIX symlink rejection, non-regular path rejection and 64 KiB size-bound rejection.  
**Exact-HEAD CI:** 4/4 required workflows terminal SUCCESS on this exact SHA. Automated Tests 41/41 steps; CodeQL Python 8/8 + JavaScript/TypeScript 8/8; OCI ARM64 7/7; Full Git History Secret Audit 6/6. Backend pytest summary: 1,393 passed, 1 skipped, 6 warnings in 61.36 seconds. The single skip is the separately configured Redis TLS integration fixture; it is not one of the three new key-loader tests. All three new key-loader tests explicitly PASSED.  
**Security source/test:** backend/app/snapshot_attestation.py; backend/tests/test_snapshot_attestation.py. The source uses a verified no-follow descriptor on POSIX, requires a regular file and effective-service-user ownership, rejects group/world permissions and caps PEM input at 64 KiB.  
**Gate 25:** repository-side Ed25519 verification, immutable receipt and private-key file boundary have verified foundations. Real owner-host key custody, authenticated remote snapshot transfer, every gateway's persisted receipt retrieval, restart re-verification and durable per-gateway high-water ACK remain 🟥 OPEN.  
**Gate 36 / production WebSocket:** public HTTPS/WSS, reverse proxy/TLS, production runtime, Firebase production sign-in/entitlement/revocation E2E and real browser/Android lifecycle plus production multi-instance acceptance remain 🟥 OPEN. Redis destructive retention remains 🟧 BLOCKED until every safety prerequisite is proven.  
**Indicators:** 28 focused indicator declarations = 21 calculation + 7 shared-hook. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook 🟨 foundation only; Footprint PRO 2GD 🟧 synthetic/reference-gated; Volume Profile variants, Heatmap and Liquidation Maps 🟥 incomplete/not integrated. Aggregate indicator completion ⚪ NOT SCORED.  
**Project progress:** Stage 1 30/40 = 75% provisional 🟨 (inherited baseline); Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 0/10 formally closed 🟥; overall project ⚪ NOT SCORED; IP3S ⚪ NOT SCORED.  
**Cost/deployment:** ZERO COST; main untouched; no Vercel deployment; delivery target approximately 24 December 2026 (planning target only).

---

# Latest verified correction — 24 November 2026 (Batch 62J-230)

**Active branch:** phase-2/market-data-foundation  
**Parent HEAD:** af5d30e3f8daa552c1676a16007f73c749c8f2a1  
**Parent CI:** 4/4 workflows terminal SUCCESS on the parent SHA. This correction adds the three security regression test functions that were missing from the prior test-file commit; the parent CI did not exercise those new cases.  
**Change:** adds explicit regression coverage for POSIX symbolic-link rejection, non-regular key paths and PEM files larger than 64 KiB.  
**Changed file:** backend/tests/test_snapshot_attestation.py.  
**Current exact-HEAD CI:** PENDING for the new correction commit; parent CI is not inherited.  
**Gate 25:** source-side private-key file boundary code is hardened, and the missing regression cases are now added. Real owner-host key custody, authenticated remote snapshot transfer, per-gateway receipt retrieval, restart re-verification and durable high-water ACK remain 🟥 OPEN.  
**Indicator status:** no indicator code changed. Focused indicator suite remains 28 named declarations (21 calculation + 7 shared-hook); the three added tests belong to Gate 25 backend security, not indicator inventory. SMA20/EMA20/RSI14/MACD/Bollinger/Shared Hook 🟨 foundation; Footprint 🟧 gated; Volume Profile variants, Heatmap and Liquidation Maps 🟥 open. Aggregate indicator completion ⚪ NOT SCORED.  
**Project meters:** Stage 1 30/40 = 75% provisional 🟨 (inherited, not rescored); Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 0/10 🟥; overall project ⚪ NOT SCORED; IP3S ⚪ NOT SCORED.  
**Cost/deployment:** ZERO COST; main untouched; no Vercel deployment; target approximately 24 December 2026.

---

# Latest verified update — 24 November 2026 (Batch 62J-229)

**Active branch:** phase-2/market-data-foundation  
**Parent HEAD:** 79f93831bd08d1468b8954d2782970309326d46d  
**Current batch:** hardened owner-host Ed25519 private-key file loading; exact-head CI for the resulting commit must be checked independently.  
**Source/test:** backend/app/snapshot_attestation.py; backend/tests/test_snapshot_attestation.py.  
**Security delta:** key loading now uses a no-follow file descriptor on POSIX, verifies a regular file and service-user ownership, enforces owner-only permissions, and caps PEM input at 64 KiB. Regression coverage rejects symlinks, non-regular paths and oversized files.  
**Gate 25:** repository-side key-file boundary hardened; real owner-host custody, authenticated remote transfer, each gateway's persisted receipt retrieval, restart re-verification and durable per-gateway high-water ACK remain 🟥 OPEN. This patch does not close Gate 25.  
**WebSocket:** Gate 25 🟥 OPEN; Gate 36 public HTTPS/WSS and production runtime 🟥 OPEN; Firebase production sign-in/entitlement/revocation E2E 🟥 OPEN; real browser/Android lifecycle and production multi-instance acceptance 🟥 OPEN. Redis destructive retention remains 🟧 BLOCKED pending every safety prerequisite.  
**Indicator ledger:** 21 calculation tests + 7 shared-hook tests = 28 focused named test declarations. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation-only; Footprint PRO 2GD 🟧 synthetic/reference-gated; Volume Profile, Complete Volume Profile, movable-range VP, Heatmap and Liquidation Maps 🟥 incomplete/not integrated. Aggregate indicator completion remains ⚪ NOT SCORED.  
**Project meters:** Stage 1 = 30/40 criteria = 75% provisional 🟨 (inherited baseline; not rescored by this patch); Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated pending stage gate and reviewed blueprint; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 = 0/10 formally closed 🟥; overall project ⚪ NOT SCORED; IP3S/significant progress ⚪ NOT SCORED.  
**Cost/deployment:** ZERO COST; main untouched; no Vercel deployment; delivery target approximately 24 December 2026 (planning target only).

---

# Latest verified work — 24 November 2026 (Batch 62J-223)

**Active branch:** `phase-2/market-data-foundation`  
**Code/test HEAD:** `92b8ef0936d374f81df6d09e67a4752494100d40`  
**Documentation work-cycle:** [Batch 62J-223](WORK_CYCLE_2026-11-24_BATCH62J223_SHARED_SERIES_OWNER_GUARD_AND_INDICATOR_RECONCILIATION.md)  
**Exact-head CI:** PENDING / NOT YET VERIFIED for the new code/test HEAD; earlier parent results are not inherited.  
**Change:** the shared OHLCV supervisor registry now rejects a same-series owner whose transport endpoint or canonical instrument mapping conflicts with the active supervisor. A regression test covers both mismatch paths and confirms the existing owner remains intact.  
**Changed source/test:** `src/services/ohlcvSeriesSupervisorRegistry.ts`; `src/services/ohlcvSeriesSupervisorRegistry.test.ts`.  
**Indicator ledger:** 17 calculation-engine tests + 7 shared-hook tests = 24 focused named cases. SMA20/EMA20/RSI14/MACD12/26/9/Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps 🟥 not implemented. Visible chart integration remains unimplemented; indicator aggregate remains NOT SCORED.  
**WebSocket:** Gate 25 and Gate 36 remain OPEN; Redis destructive retention remains BLOCKED.  
**Progress:** Stage 1 = 30/40 criteria = 75% provisional 🟨; Stage 2 active engineering but NOT SCORED 🟦; Stages 3–6 NOT SCORED ⬜; Gate 10 = 0/10 formally closed 🟥; overall project NOT SCORED ⚪; IP3S for this batch NOT SCORED ⚪.  
**Cost/deployment:** ZERO COST; `main` untouched; no Vercel deployment; target approximately 24 December 2026 (planning target only).

---

# CURRENT AUDITED CHECKPOINT — 24 NOVEMBER 2026 (BATCH 62J-205)

**Active branch:** `phase-2/market-data-foundation`  
**Exact code/test HEAD:** `b71bf86c31fadd2895a2b4f18991b6742847e1a1`  
**Documentation parent HEAD for Batch 62J-204:** `4eef1fe3547d70257a39e00e9d4f49934dc3db2a`  
**Latest documentation maintenance:** [Batch 62J-205](docs/WORK_CYCLE_2026-11-24_BATCH62J205_GATE25_SNAPSHOT_DIGEST_EVIDENCE_CORRECTION.md)  
**Exact-head CI:** Automated Tests [45321594594](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594594) SUCCESS (1/1 job, 40/40 steps) • CodeQL [45321594526](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594526) SUCCESS (2/2 jobs) • OCI ARM64 [45321594556](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594556) SUCCESS • Secret Audit [45321594499](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594499) SUCCESS. All four exact `head_sha` values match `b71bf86c31fadd2895a2b4f18991b6742847e1a1`.  
**Cost:** ZERO COST • **main:** untouched • **delivery target:** approximately 24 December 2026 (planning target only)

## Latest indicator audit — Batch 62J-204 (24 November 2026)

**Source/test checkpoint:** `b71bf86c31fadd2895a2b4f18991b6742847e1a1`  
**Documentation parent:** `4eef1fe3547d70257a39e00e9d4f49934dc3db2a`  
**Indicator code delta:** none. This batch reconciles the current source, exact test inventory, visible chart integration state, and progress records; it does not award implementation credit.

The two indicator-specific suites contain **24 named tests**: 17 calculation-engine tests and 7 shared-hook tests. The count was obtained from the current `it()` declarations in `src/indicators/indicatorCalculations.test.ts` and `src/indicators/useMarketIndicators.test.ts`. It is a focused indicator-suite count, not the total frontend test count and not proof that production chart acceptance has passed.

| Study / subsystem | Verified calculation or data foundation | First valid source index | Visible chart acceptance | Status |
|---|---|---:|---|---|
| SMA 20 | Rolling 20-close arithmetic mean with overflow-resistant normalized summation | 19 | Overlay, toggle, legend/latest value, identity clearing and lifecycle not integrated | 🟨 Foundation |
| EMA 20 | SMA-seeded EMA; multiplier `2/21` | 19 | Overlay, toggle, legend/latest value, identity clearing and lifecycle not integrated | 🟨 Foundation |
| RSI 14 (Wilder) | Seed from first 14 close-to-close changes, then Wilder recurrence; explicit flat/rising/falling edge handling | 14 | Dedicated 0–100 pane, 30/70 guides, toggle and legend not integrated | 🟨 Foundation |
| MACD 12/26/9 | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD 25; signal/histogram 33 | Dedicated pane, lines, histogram, zero guide, toggle and legend not integrated | 🟨 Foundation |
| Bollinger 20,2 | 20-close mean ± 2 population standard deviations | 19 | Upper/middle/lower bands, fill, toggle and latest values not integrated | 🟨 Foundation |
| Shared indicator hook | Exact keyed immutable backend snapshot; shared WeakMap calculation cache per snapshot object; non-backend/untrusted states suppress output | Per study | Hook is not imported or called by `CandlestickChart.tsx` | 🟨 Foundation |
| Footprint | Deterministic synthetic/offline aggregation fixtures only; not exchange-native bid/ask truth | N/A | Visual work requires owner reference image(s) and reviewed blueprint; OFF keeps normal candles, ON alone uses spaced clusters | 🟧 Gated |
| Heatmap | No accepted depth/liquidity renderer verified | N/A | Not implemented; owner reference and validated depth contract required | 🟥 Open |
| Liquidation Maps | No accepted calculation/runtime renderer verified | N/A | Not implemented; data provenance and reviewed blueprint required | 🟥 Open |

### Exact indicator test inventory

**Calculation engine — 17 tests**
1. SMA/EMA source alignment and warm-up nulls.
2. Wilder RSI flat and rising edge cases.
3. MACD signal warm-up separation.
4. Bollinger population standard deviation.
5. Shared multi-indicator calculation entry point.
6. All shared calculations across supported chart timeframes.
7. Invalid periods and non-finite values.
8. Prefix causality (future candles cannot change earlier outputs).
9. Falling-only RSI and period-one moving averages.
10. Fail-closed handling of infinite results from finite extreme inputs.
11. RSI stability for very large finite gain/loss magnitudes.
12. Overflow-resistant representable SMA means.
13. Finite Bollinger deviation for large same-sign prices.
14. Preservation of small residuals between large cancelling SMA inputs.
15. Preservation of small residuals in the Bollinger middle band.
16. Wilder RSI seed and recursive smoothing on alternating gains/losses.
17. Rejection of non-finite close values at the shared calculation boundary.

**Shared hook — 7 tests**
1. No indicator output without a selected backend series.
2. Calculation from the exact selected keyed snapshot.
3. Recalculation from a new immutable snapshot revision after a live update.
4. Isolation of simultaneous panels by canonical series.
5. One frozen calculation result shared across panels on the same snapshot revision.
6. Degraded backend data retained while demo/error snapshots are suppressed.
7. Indicator output cleared when the selected series becomes unavailable.

### Numerical and lifecycle invariants verified in source/tests

- Outputs preserve source-candle indexing; warm-up slots remain `null`.
- SMA20/EMA20/Bollinger20 first become valid at index 19; RSI14 at index 14; MACD line at index 25 and signal/histogram at index 33.
- Prefix-causality tests compare every study's prefix output with the corresponding prefix of the full series.
- Invalid periods and non-finite input are rejected; numerical kernels include large-magnitude/cancellation regression cases.
- The hook calculates only for exact canonical-series snapshots in backend `ready` or `degraded` state; demo/loading/unavailable/error states do not expose indicator output.
- Immutable snapshot identity is used for shared calculation caching; calculated arrays/points are frozen before publication.

### Integration boundary — still red

`CandlestickChart.tsx` currently imports `useMarketDataSeriesSnapshot`, not `useMarketIndicators`, and creates a single `CandlestickSeries`. Consequently, none of SMA/EMA/RSI/MACD/Bollinger is yet a visible, user-toggleable chart feature. No progress credit is awarded for UI integration, accessibility, settings persistence, multi-panel rendering, resize/lifecycle behavior, or production performance until implemented and tested.

Footprint and Heatmap visual work remain gated on owner-provided reference images and a scoped blueprint review. No speculative indicator UI, new dependency, paid provider, hosting, or deployment is introduced in this batch.

**Indicator aggregate progress: NOT SCORED.** There is no approved per-study weighting or acceptance denominator. The 24 focused tests are evidence of calculation/hook foundations, not a completion percentage.



## Latest Gate 25 snapshot-digest correction — Batch 62J-205

Current replica source persists the snapshot SHA-256 in the mutable checkpoint in the same transaction as installed bars and checkpoint replacement. Gateway startup verifies callback digest against that checkpoint before Redis construction. This is not an immutable per-generation installation receipt and does not authenticate owner-host receipt custody; Gate 25 remains OPEN. See [Batch 62J-205](docs/WORK_CYCLE_2026-11-24_BATCH62J205_GATE25_SNAPSHOT_DIGEST_EVIDENCE_CORRECTION.md) and the corrected [snapshot receipt ADR](docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md).

## Latest documentation and WebSocket audit — Batch 62J-203

The Batch 62J-202 documentation commit `490d110eb01a4ea90d38e02a3a9def45efa54c77` has independently completed all four required CI workflows successfully. Batch 62J-203 records a source/test evidence audit; it does not award production acceptance to owner-host WSS, Firebase, Android/browser, or cross-instance hosting.

Automated Tests [45327803885](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45327803885) SUCCESS • CodeQL [45327803964](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45327803964) SUCCESS • OCI ARM64 [45327803882](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45327803882) SUCCESS • Secret Audit [45327804169](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45327804169) SUCCESS. All four runs report exact head `490d110eb01a4ea90d38e02a3a9def45efa54c77`.

The audit mapped 111 named test cases across selected WebSocket/Redis suites: Redis consumer (22), gateway runtime (8), lease (5), worker lifecycle (7), browser supervisor (27), WebSocket client (22), browser lifecycle (5), and protocol validation (15). This is a count of named tests in those inspected files, not a claim that every conditional real-Redis case executed in every CI environment.

Verified repository behavior includes durable snapshot installation checks before gateway Redis client creation; generation-scoped consumer groups and lease fencing; XAUTOCLAIM pending recovery before new-entry reads; durable local apply before ACK; callback-failure retry behavior; replay/live boundary merging; two-gateway and two-ASGI-process test scenarios; TCP interruption recovery; browser cursor resume and server-directed resnapshot; Firebase token/ticket retry bounds; and fail-closed handling for sequence gaps, authentication rejection, entitlement denial, protocol close, and heartbeat timeout.

Still externally unaccepted: public owner-host WSS/TLS and proxy behavior; real Firebase sign-in, revocation and entitlement E2E; production owner-controlled snapshot transport/receipt custody; real Android and browser lifecycle/reconnect acceptance; production cross-instance and platform-lifetime proof. Redis Stream retention remains intentionally unimplemented until durable gateway inventory, retirement, authenticated snapshot receipts, per-gateway floor acknowledgements, PEL policy, dedicated retention identity, and crash-safe trim/reconcile semantics are proven.

No code, tests, dependencies, credentials, hosting, deployment, or provider activation changed in this audit. Cost remains ZERO; `main` remains untouched. Stage 1 stays 30/40 criteria (300/400 ticks, 75% provisional); Gate 10 stays 0/10 closed; overall project and aggregate indicator progress remain NOT SCORED.

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



## Exact-head CI details

- Automated Tests: backend tests, Redis TLS fixture, synthetic outbox/metrics benchmarks, backend dependency audit, container build, persistent-volume smoke, image scan/report export and frontend audit enforcement all passed.
- CodeQL: Python and JavaScript/TypeScript analyses passed.
- OCI ARM64: native ARM64 image build and smoke test passed.
- Full Git History Secret Audit passed.
- No Android APK workflow run was found for this exact HEAD; CI is not real-device/release acceptance.

## Indicator interpretation

SMA/EMA/RSI/MACD/Bollinger calculations and the shared hook are foundations only. No visible overlays/panes/toggles/legends are integrated. Footprint is synthetic/offline only; Heatmap and Liquidation Maps are not implemented. No indicator aggregate percentage is claimed.

Detailed report: [Batch 62J-201](docs/WORK_CYCLE_2026-11-24_BATCH62J201_REDIS_ACL_SELECTOR_FIX_AND_INDICATOR_RECONCILIATION.md).

---

# HISTORICAL CHECKPOINT — 19 NOVEMBER 2026 (BATCH 54)


**Active branch:** `phase-2/market-data-foundation`  
**Audited HEAD:** `fba43a12017e314baeb9e2719a50b441274126c6`  
**Automated Tests & Build:** [44470207284](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207284) — **SUCCESS**.  
**CodeQL:** [44470207308](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207308) — **SUCCESS**.  
**Full Git History Secret Audit:** [44470207366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207366) — **SUCCESS**.

## Batch 54 — artifact-level findings

- Exact-head CI fully completed: frontend **234/234**, backend **1,032/1,032**, frontend npm audit **0 vulnerabilities**, backend dependency audit no known vulnerabilities, container build/smoke/Trivy report export all successful.
- Downloaded and parsed Trivy artifact `14503114420`: `trivy-current.json` reports **0 vulnerabilities** in CI image `dezzta-chart-backend:ci`, digest `sha256:51c3bcf50e62d8e875028debf81d98204697a87e1ef2ed7035c27768b676d27e`.
- Downloaded and parsed synthetic outbox benchmark artifact `14503597322`: 1,000 synthetic bars persisted and replayed; persist p50/p95/p99 = **2.60/10.20/26.99 ms**; concurrent replay page p50/p95/p99 = **0.36/1.62/8.86 ms**. Single-process runner microbenchmark only; not a production capacity claim.
- Gate 8 audit: secret redaction, frontend source/bundle scans, and Git-history scan pass; actual production host secret injection remains unverified.
- Gate 20 audit: Firebase client observer/auth tests and server revocation/issuer/audience checks exist; real project signed-token E2E is absent. Scoped short-lived WSS ticket exchange is not implemented; current client sends Firebase ID token in initial auth frame.
- Gate 25 audit: atomic Redis Lua guards, TLS CA/hostname verification, ACL requirements, fail-closed behavior and CI outage smoke exist; production Redis endpoint/multi-instance proof absent.
- Gate 35 audit: production CORS requires exact HTTPS origins; no accepted owner-host HTTPS backend, certificate renewal, external TLS scan, or Android WebView connection.
- WSS preview remains READY and SSO-protected, project `live=false`; no real browser/device round-trip or 330-second session is claimed.
- Detailed report: [Batch 54 CI artifact forensics + Gate 8/20/25/35 audit](docs/WORK_CYCLE_2026-11-19_BATCH54_CI_ARTIFACT_FORENSICS_GATE8_20_25_35.md).

## Progress — unchanged, no speculative credit

- **Stage 1:** 30/40 criteria; 300/400 ticks; **75% provisional**.
- **Gate 10:** **0/10 formally closed**; open criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- **Stages 2–6:** NOT SCORED.
- **Overall project percentage:** NOT ESTABLISHED; historical 20.9% is not a newly weighted calculation.
- **Indicators:** SMA/EMA/RSI/MACD/Bollinger calculation foundations + shared hook only; visible controls/panes remain Stage 4 parked. Footprint visual waits for owner reference; Heatmap/Liquidation Maps unimplemented/unverified pending references.
- **ZERO COST:** no deploy, paid provider, billing activation, production promotion, or Termux operation.
- **Protected `main`:** untouched.

---

# CURRENT AUDITED CHECKPOINT — 19 NOVEMBER 2026 (BATCH 53)

**Active branch:** `phase-2/market-data-foundation`  
**Batch 53 documentation checkpoint:** pending final dashboard/status commits  
**Exact-head Automated Tests & Build:** [44468970676](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970676) — **SUCCESS, 32/32 steps** on `8f377cfb07b082ce237cf3ac9137efbfbcc4f5d8`.  
**Exact-head CodeQL:** [44468970595](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970595) — **SUCCESS**, Python and JavaScript/TypeScript.  
**Exact-head Full Git History Secret Audit:** [44468970614](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970614) — **SUCCESS**.  
**Latest WSS preview:** `dpl_5VXGuNtmkxzWTDQkcGZgBrrL7WrK` — READY, SSO protected, project `live=false`, synthetic-only.

## Batch 53 — verified work

- Frontend Vitest: **234 passed / 234 across 28 files**; backend pytest: **1,032 passed / 1,032**.
- Frontend npm audit: **0 vulnerabilities**; production build and 77-file credential scan passed.
- Backend container build, dependency audit, Redis ACL/AOF + mounted persistent-volume smoke, SQLite integrity/restart checks, Trivy HIGH/CRITICAL scan and report export passed.
- CI persistent-volume evidence is limited to an ephemeral GitHub runner; it does not close Gate 34 on an owner-controlled host.
- Gate 30/31 source and integrated CI restore path re-audited; owner target-host restore, off-host artifact and separate key custody remain absent.
- WSS deployment read-back confirms READY, SSO for all targets, and `live=false`. Runtime logs show no entries in the available 30-minute window and no errors in the one-hour error query. No actual WSS round-trip is inferred.
- The Vercel project details response did not expose effective `resourceConfig.fluid`; independent Fluid Compute read-back remains unresolved. No SSO bypass, public share link, or deployment was created.
- Full technical indicator inventory was reconciled. SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9 and Bollinger 20,2 calculations/tests plus shared hook exist; visible controls/panes remain parked for Stage 4. Footprint visual work waits for its reference; Heatmap and Liquidation Maps remain unimplemented pending references.
- Detailed report: [docs/WORK_CYCLE_2026-11-19_BATCH53_CI_GATE10_WSS_INDICATOR_AUDIT.md](docs/WORK_CYCLE_2026-11-19_BATCH53_CI_GATE10_WSS_INDICATOR_AUDIT.md).

## Progress — unchanged, no speculative credit

- **Stage 1:** 30/40 criteria; 300/400 ticks; **75% provisional**.
- **Gate 10:** **0/10 formally closed**. Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- **Stages 2–6:** NOT SCORED.
- **Overall project percentage:** NOT ESTABLISHED. Historical 20.9% remains preserved, not a new weighted calculation.
- **ZERO COST:** no deployment, paid plan/provider/storage, billing activation, production promotion, or Termux operation.
- **Protected `main`:** untouched.

---

# CURRENT AUDITED CHECKPOINT — 19 NOVEMBER 2026 (BATCH 52)

**Active branch:** `phase-2/market-data-foundation`  
**Current audit commit before this status update:** `81079dda40e61e01cccc6993ef30ef6703cf666f`  
**Latest verified application-source CI checkpoint:** `b30ce94ca278e527731d86e40ddf06c6dbd16b5b` (Batch 50 exact-head CI).  
**Latest WSS preview:** `dpl_5VXGuNtmkxzWTDQkcGZgBrrL7WrK` — READY, SSO protected, synthetic-only.

## Batch 52 — audit results

- Audited the isolated WebSocket POC source/config and its existing 10-test suite. The suite already covers Fluid Compute config, synthetic health, browser probe headers, ordered ping/pong, fresh sessions, automatic browser ping, oversize rejection, invalid payload rejection, rate limit and idle close. No duplicate test or application change was needed.
- Audited Gate 38 metrics: 127-series cap including overflow, sanitized labels, finite bounded duration, lock-protected updates, detached snapshot and concurrent test. Scope remains process-local; durable/cross-instance collection, retention, host access control and disk-pressure evidence are still missing.
- Audited Gate 39 local alert reporter: transition deduplication, validated counters, sanitized worker exception class, recovery signal and no secret/payload logging. Host log collection, named responsible adult operator, verified escalation channel and isolated acknowledgement/recovery drill remain missing.
- Audited Gate 36 preview boundary: READY + SSO protected + project `live=false`; checked-in `fluid:true` is asserted by the POC test, but effective runtime behavior and authenticated owner-browser WSS/Android WebView/330-second lifetime/cross-instance acceptance are not independently established.
- A duplicate-path test-file attempt was immediately restored from the parent checkpoint. Final file is byte-for-byte identical to the parent file (blob `f3e1c874bb65122e878efa1ccd56d1ae86b9741a`). No application source was changed. Restoration commit: `98b2ac468dd5f616af091ed400f234e3ca46b513`; matching CI result is not yet confirmed.
- Detailed report: [docs/WORK_CYCLE_2026-11-19_BATCH52_WEBSOCKET_GATE10_EVIDENCE_AUDIT.md](docs/WORK_CYCLE_2026-11-19_BATCH52_WEBSOCKET_GATE10_EVIDENCE_AUDIT.md).

## Progress — unchanged, no speculative credit

- **Stage 1:** 30/40 criteria; 300/400 ticks; **75% provisional**.
- **Gate 10:** **0/10 formally closed**. Open external criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- **Stages 2–6:** NOT SCORED.
- **Overall project percentage:** NOT ESTABLISHED. 20.9% remains a historical owner-confirmed checkpoint pending approved, criterion-level M1–M8 scoring.
- **Indicators:** SMA 20, EMA 20, RSI 14 (Wilder), MACD and Bollinger calculations/tests exist; shared hook exists but visible chart controls/panes remain unintegrated. Footprint is simulated/offline only and visual implementation awaits owner reference. Heatmap and Liquidation Maps are unimplemented/unverified and await their references.
- **ZERO COST:** no deployment, paid plan, billing activation, provider, production credential, Termux package/repository/keyring change.
- **Protected `main`:** untouched.

---

# CURRENT AUDITED CHECKPOINT — 19 NOVEMBER 2026 (BATCH 51)

**Active branch:** `phase-2/market-data-foundation`  
**Current documentation checkpoint before this reconciliation:** `c51b62c49539ff3bebcb28f77955c549afd78cfd`  
**Latest application source/test commit:** `b30ce94ca278e527731d86e40ddf06c6dbd16b5b`  
**Deployed preview source:** `9961471f1d72e3d35b4bf3f4314171d7b5fe2b1a`

## Batch 51 — meaningful WSS preview deployment

- Isolated FastAPI WebSocket POC deployment `dpl_5VXGuNtmkxzWTDQkcGZgBrrL7WrK` is **READY** at https://dezzta-chart-ws-n3mvfjv0n-deszztagd377-pixel.vercel.app.
- Exact source SHA: `9961471f1d72e3d35b4bf3f4314171d7b5fe2b1a`, containing the verified Batch 50 transport fix.
- Build selected Python 3.12 and installed `poc/vercel_ws/requirements.txt`; build completed in approximately 4 seconds.
- SSO remains enabled for all deployment targets; project remains `live=false`. No production promotion.
- No matching warning/error/fatal runtime logs were returned for the new deployment in the 30-minute query window. This is not proof of an HTTP health invocation or a live WSS round-trip.
- Only the WSS POC was deployed. The frontend was not redeployed.

## Vercel ignored-build filter correction

The deployment log exposed a missing previous Git object (`fatal: bad object 9873a5f...`) in the old ignored-build command. The deployment still completed, but the filter could not safely distinguish a docs-only change.

The WSS POC project's ignored-build command was updated to check for the previous commit, fetch that exact commit shallowly if absent, then compare only `poc/vercel_ws/**`. If fetch/comparison fails, it safely requests a build rather than skipping. Command length is 254/256 characters. This settings update has not yet been exercised by a subsequent natural deployment; do not trigger a throwaway build to test it.

Detailed record: [docs/WORK_CYCLE_2026-11-19_BATCH51_WEBSOCKET_PREVIEW_DEPLOYMENT_AND_FILTER_FIX.md](docs/WORK_CYCLE_2026-11-19_BATCH51_WEBSOCKET_PREVIEW_DEPLOYMENT_AND_FILTER_FIX.md).

## Progress — unchanged, no speculative credit

- **Stage 1:** 30/40 criteria; 300/400 ticks; **75% provisional**. No ticks awarded for Batch 51.
- **Gate 10:** **0/10 formally closed**. Open external criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- **Gate 36:** remains OPEN. Deployment READY does not prove owner-device WSS, 330-second platform close, Android WebView, effective Fluid Compute read-back, or production cross-instance fan-out.
- **Stages 2–6:** NOT SCORED.
- **Overall project percentage:** NOT ESTABLISHED; 20.9% is historical only pending approved M1–M8 scoring.
- **ZERO COST:** no paid plan, billing activation, paid provider, production credential, or Termux operation.
- **Protected `main`:** untouched.

---

# CURRENT AUDITED CHECKPOINT — 19 NOVEMBER 2026

**Active branch:** `phase-2/market-data-foundation`  
**Current branch HEAD (documentation reconciliation):** `90097fbf05375e7bb9381b2f6a9e5871dc581b2c`  
**Latest verified application source/test commit:** `b30ce94ca278e527731d86e40ddf06c6dbd16b5b`  
**Latest exact-head Automated Tests run:** [44422985332](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985332) — SUCCESS, every listed step completed successfully.

## Latest verified work — WebSocket Batch 50

- Fixed the transport failure path when the socket is already `CLOSED` before its native `close` event is delivered.
- Preserved normal `CLOSING` event ordering and idempotent close notification; a late native event cannot notify the supervisor twice.
- Corrected the fake socket lifecycle in regression tests and repaired the test syntax.
- Frontend Vitest: **234 passed / 234** across 28 files.
- Backend pytest: **1,032 passed / 1,032** in 30.94 seconds.
- Frontend npm audit: **0 vulnerabilities**; frontend production build and 77-file source/bundle credential scans passed.
- Backend dependency audit, container build, Redis ACL + persistent-volume smoke, Trivy image scan/report, and Android preflight/publisher tests passed.
- Android debug APK workflow [44422985353](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985353): SUCCESS; artifact generated, **not published**.
- CodeQL [44422985334](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985334): Python and JavaScript/TypeScript jobs SUCCESS.
- Full Git History Secret Audit [44422985415](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985415): SUCCESS.
- The initial Batch 50 attempt failed due to a test-fixture/syntax issue; the correction is included in the verified source commit. The corrected exact-head run has no failed steps.

## Project progress — no speculative credit

- **Stage 1:** 30/40 criteria; 300/400 ticks; **75% provisional**, not production accepted.
- **Gate 10:** **0/10 formally closed**. Open external criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- **Overall project percentage:** **NOT ESTABLISHED**. The remembered 20.9% is historical only; do not publish a new weighted total until the M1–M8 ledger is approved and scored.
- **Stages 2–6:** NOT SCORED.
- **Gate 36:** Browser reconnect/fresh-session evidence is a verified sub-check; overall gate remains OPEN pending external/public WSS and Android WebView acceptance, measured 330-second foreground lifecycle/close attribution, independent effective Fluid Compute read-back, and production cross-instance fan-out.
- **ZERO COST:** No deployment triggered in this batch; no paid plan, billing activation, paid provider, production credential, or Termux package/repository/keyring change.
- **Protected `main`:** untouched.

The current colored dashboard is [docs/assets/project-progress-dashboard-current.svg](docs/assets/project-progress-dashboard-current.svg). The detailed Batch 50 record is [docs/WORK_CYCLE_2026-11-19_BATCH50_WEBSOCKET_ALREADY_CLOSED_FALLBACK.md](docs/WORK_CYCLE_2026-11-19_BATCH50_WEBSOCKET_ALREADY_CLOSED_FALLBACK.md).

---

# DEZZTA CHART — Current Project Status

**Current checkpoint:** 2026-11-17  
**Active branch:** `phase-2/market-data-foundation`  
**Latest source/test commit:** `cfc56b7ba050201823952ea1b67dd38182dc9bfb`  
**Latest documentation checkpoint before this status refresh:** `0305a7c78146ac2491e424ce9561cda8b6159372`

- **Stage 1:** 30/40 provisional criteria; 300/400 ticks; **75% provisional**, not production accepted.
- **Gate 10:** **0/10 formally closed**. Open external criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- **Automated Tests & Build [44112080352](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44112080352): SUCCESS**, all 32/32 steps; backend pytest **1,009 passed in 36.34s**, including the integrated encrypted application restore test.
- **CodeQL [44112080772](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44112080772): SUCCESS**; **Full Git History Secret Audit [44112080446](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44112080446): SUCCESS**.
- **Vercel status:** isolated FastAPI WSS POC preview context **SUCCESS**; main Vite preview context **FAILURE due to Vercel build-rate limit**. No paid upgrade or repeated deployment was attempted. Existing last-known frontend preview remains a prior READY build; this test-only source change does not alter frontend source.
- **Gate 30/31:** encrypted application snapshot → AES-256-GCM artifact → authenticated decrypt → full fresh-path application restore is now covered by an exact-head passing CI test. External host restore, off-host storage, separate key custody and retention remain OPEN.
- **Gate 36:** browser reconnect/fresh-session pong, POC build context and all-target SSO are verified sub-checks. Gate 36 remains OPEN pending maximum-duration behavior, independent Fluid Compute read-back, Android Capacitor WebView WSS and production fan-out/cost acceptance.
- **Gate 38:** metrics input hardening is CI-verified; durable aggregation, retention, host access controls and dashboard acceptance remain OPEN.
- **Gate 39:** local sanitized operator reporter and zero-cost runbook exist; host collection, escalation and recovery drill remain OPEN.
- **Stages 2–6:** NOT SCORED. Overall 20.90% is historical only.
- **ZERO COST:** no paid plan, provider, subscription, billing activation, Termux package/repository/keyring change or production data connection. No Termux action required in this cycle.
- **Protected `main`:** untouched.

Detailed work cycle: [docs/WORK_CYCLE_2026-11-17_GATE10_BATCH6.md](docs/WORK_CYCLE_2026-11-17_GATE10_BATCH6.md).

---

# DEZZTA CHART — Current Project Status

**Current checkpoint:** 2026-11-17  
**Active branch:** `phase-2/market-data-foundation`  
**Latest source commit:** `cfc56b7ba050201823952ea1b67dd38182dc9bfb`

- **Stage 1:** 30/40 provisional criteria; 300/400 ticks; **75% provisional**, not production accepted.
- **Gate 10:** **0/10 formally closed**. Open external criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- **Latest previously verified source/test HEAD:** `d32645019db6c93532666f691c43cfe87b9fa8d8`: Automated Tests & Build [44107801447](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801447) **SUCCESS**, 32/32 steps; backend pytest **1,008 passed in 26.26s**. CodeQL [44107801732](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801732) and Full Git History Secret Audit [44107801473](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801473) **SUCCESS**.
- **Batch 6:** added an integrated encrypted application-backup → authenticated decrypt → full restore-drill regression test for Gates 30/31. Exact-head CI is pending.
- **Gate 36:** browser reconnect/fresh-session pong, POC build context and all-target SSO are verified sub-checks. Gate 36 remains OPEN pending maximum-duration behavior, independent Fluid Compute read-back, Android Capacitor WebView WSS and production fan-out/cost acceptance.
- **Gate 38:** metrics input hardening is CI-verified; durable aggregation, retention, host access controls and dashboard acceptance remain OPEN.
- **Gate 39:** local sanitized operator reporter and zero-cost runbook exist; host collection, escalation and recovery drill remain OPEN.
- **Stages 2–6:** NOT SCORED. Overall 20.90% is historical only.
- **ZERO COST:** no paid plan, provider, subscription, billing activation, Termux package/repository/keyring change or production data connection. No Termux action required in this cycle.
- **Protected `main`:** untouched.

Detailed work cycle: [docs/WORK_CYCLE_2026-11-17_GATE10_BATCH6.md](docs/WORK_CYCLE_2026-11-17_GATE10_BATCH6.md).

---

# DEZZTA CHART — Current Project Status

**Current checkpoint:** 2026-11-17  
**Active branch:** `phase-2/market-data-foundation`  
**Latest documentation HEAD before current Vercel read-back update:** `2733c80f6958f4599a92365db4e753c2264e45e2`  
**Latest verified source/test HEAD:** `d32645019db6c93532666f691c43cfe87b9fa8d8`

- **Stage 1:** 30/40 provisional criteria; 300/400 ticks; **75% provisional**, not production accepted.
- **Gate 10:** **0/10 formally closed**. Open external criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- **Exact-head CI for source commit:** Automated Tests & Build [44107801447](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801447) **SUCCESS**, all 32 steps passed; backend pytest **1,008 passed in 26.26s**. CodeQL [44107801732](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801732) and Full Git History Secret Audit [44107801473](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801473) **SUCCESS**. Both Vercel preview status contexts passed. These are repository/preview checks, not external production acceptance.
- **Gate 36:** Browser health and manual reconnect/fresh-session ping-pong sub-checks are evidenced. Latest READY Vercel build log confirms Python 3.12 and dependencies were loaded from `poc/vercel_ws/`; SSO is enabled for all targets. Effective Fluid Compute remains unverified. Gate 36 overall remains OPEN.
- **Gate 38:** Metrics collector hardening passed CI; durable aggregation, retention, host access controls and dashboard acceptance remain OPEN.
- **Gate 39:** Local sanitized operator reporter and zero-cost runbook exist; host collection, escalation and recovery drill remain OPEN.
- **Stages 2–6:** NOT SCORED. Overall 20.90% is historical only.
- **ZERO COST:** No paid plan, provider, subscription, billing activation or Termux package/repository/keyring change. No Termux action required in this cycle.
- **Protected `main`:** untouched.

## Latest work cycle — Batch 4 reconciliation

This documentation-only batch corrected the stale Gate 38 CI-pending statement in the progress indicator, made the latest exact-head verification prominent in the status/matrix, and reconciled the 10-gate count across the project documentation. It does not add Stage 1 ticks or close any external gate.

Detailed report: [docs/WORK_CYCLE_2026-11-17_GATE10_BATCH4.md](docs/WORK_CYCLE_2026-11-17_GATE10_BATCH4.md).

---

## Gate 38–39 operations documentation — 2026-11-17

- Added [docs/OPERATIONS_RUNBOOK_ZERO_COST.md](docs/OPERATIONS_RUNBOOK_ZERO_COST.md), covering protected operations routes, bearer-token handling, process-local metrics limits, sanitized alert signals, adult operator ownership, escalation and recovery evidence.
- This is a documentation/control-definition increment only. It does not create host monitoring, durable retention, external alert delivery, or an on-call service.
- Gates 38 and 39 remain OPEN. Stage 1 remains 75% provisional; Gate 10 remains 0/10. No ticks awarded. ZERO COST maintained; no Termux changes; `main` untouched.

---

## Latest Gate 38 repository increment — observability input hardening (2026-11-17)

- Updated `backend/app/observability.py` to safely normalize unhashable method labels, reject boolean status codes and boolean/string/non-finite durations, handle integer conversion overflow, and cap finite duration samples at 86,400,000 ms.
- Added regression tests in `backend/tests/test_observability.py` for NaN, ±infinity, booleans, strings, unhashable labels, boolean status codes and extreme finite samples.
- The existing 127-series cap, overflow series, route sanitization, histogram shape and detached snapshot contract are preserved.
- Exact-head source commit `d32645019db6c93532666f691c43cfe87b9fa8d8` passed Automated Tests & Build [44107801447](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801447): all 32 steps passed and backend pytest reported **1,008 passed in 26.26s**. CodeQL [44107801732](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801732) and Full Git History Secret Audit [44107801473](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801473) also passed; both Vercel preview status contexts passed.
- External Gate 38 remains OPEN pending durable aggregation, bounded retention, self-hosted dashboard and host access-control evidence. Gate 39 remains OPEN pending host log collection, incident escalation and recovery exercise.
- Gate 10 remains 0/10. Stage 1 remains 300/400 = 75% provisional. No ticks awarded. ZERO COST preserved; no Termux changes. `main` untouched.
- Full report: [docs/WORK_CYCLE_2026-11-17_GATE10_BATCH3.md](docs/WORK_CYCLE_2026-11-17_GATE10_BATCH3.md).

---

## Latest Gate 39 repository increment — 2026-11-17

- Code commit `5a0c106d388b78ebb2c7821893d918879c5415da` adds a local-only sanitized operator alert reporter to the existing opt-in alert-delivery worker.
- New files: `backend/app/alert_operations.py` and `backend/tests/test_alert_operations.py`; integration: `backend/app/main.py`.
- Reporter emits transition-based local JSON warnings for retry/degraded states, terminal failures, lease loss and worker exceptions; emits recovery on return to healthy; deduplicates repeated states; validates counters; never logs owner IDs, tokens, provider/event payloads, credentials or raw exception text.
- Automated Tests & Build [44105086185](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44105086185) **SUCCESS**: all 32 job steps passed; backend pytest collected 1,006 tests and all passed in 28.39s, including the new local-alert tests. CodeQL [44105086159](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44105086159) and Full Git History Secret Audit [44105086295](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44105086295) also **SUCCESS**. Both Vercel preview status contexts completed successfully. These are source/CI/preview checks, not production Gate 39 acceptance.
- Dedicated FastAPI POC deployment read-back: **READY**, deployment `dpl_kk7nMRFtTFkRNr5nvYDqxXm9czVx`, URL https://dezzta-chart-ws-erkkeiw0m-deszztagd377-pixel.vercel.app, source commit `5a0c106d388b78ebb2c7821893d918879c5415da`, branch `phase-2/market-data-foundation`. Project read-back reports `live=false` and SSO protection enabled for all deployment targets. The project/deployment read-back did not expose an independently verifiable effective `fluid` or root-directory value; those Gate 36 sub-checks remain OPEN. This preview is the isolated synthetic POC, not the production FastAPI market-data service.
- Gate 39 repository-level local operator logging increment: **implemented and test-step passed**. Gate 39 external acceptance remains **OPEN**: no host log collection, owner escalation, recovery drill, live tick source, or end-user delivery is claimed. FCM worker remains disabled by default.
- Gate 10 remains **0/10**. Stage 1 remains **300/400 = 75% provisional**. No ticks awarded. Open external criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Stages 2–6 remain NOT SCORED; 20.90% remains historical only.
- ZERO COST preserved. No new service, paid resource, credential, provider, FCM activation, or Termux change. `main` untouched.
- Full cycle report: [docs/WORK_CYCLE_2026-11-17_GATE10_BATCH2.md](docs/WORK_CYCLE_2026-11-17_GATE10_BATCH2.md).

---

## Historical Gate 10 follow-up — 2026-11-17 (superseded by newer checkpoints)

- Latest code/test checkpoint: `ee9a68da14001839a1aebc03082187b4b34162ef` includes a bounded metrics-series cardinality correction and three new regression tests. Exact-head Automated Tests & Build, CodeQL, and Full Git History Secret Audit all passed. This commit changes only the backend's internal metrics cap and its tests; it does not enable production integrations.
- Latest dedicated FastAPI POC preview deployment `dpl_GRGdGjm4W9dYuAD9FEFn84rdcHtm` is **READY** at https://dezzta-chart-ws-fyyd5o3ui-deszztagd377-pixel.vercel.app on documentation-only commit `1dbc5a544c294fc74a441158af65ed6d1cb523d0`; SSO is enabled for **all** deployment targets. Latest main Vite frontend preview `dpl_CXHJ9UXKfK4jVQVsLzNumSkbfdex` is **READY** at https://dezzta-chart-la5w28fic-deszztagd377-pixel.vercel.app on the same commit; SSO is enabled for all deployments except custom domains. Both project read-backs report `live=false`; neither is claimed as production market-data delivery.
- Owner-device evidence now confirms protected HTTP `/health` 200, browser WSS ready/pong, owner-confirmed manual Disconnect → Connect, a distinct second session with first pong sequence 1, and idle-timeout on that session. The reconnect sub-check is PASS; Gate 36 overall remains OPEN.
- Gate 36 remaining: maximum-duration close, independent effective Fluid Compute read-back, Android APK Capacitor WebView WSS against the authenticated market-data backend, production cross-instance fan-out, and cost/operational acceptance. The source `fluid: true` setting is not independent runtime evidence; Vercel read-back did not expose the effective setting/root directory.
- Latest source/test checkpoint is `5a0c106d388b78ebb2c7821893d918879c5415da`: Automated Tests & Build [44105086185](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44105086185), CodeQL [44105086159](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44105086159), and Full Git History Secret Audit [44105086295](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44105086295) all completed SUCCESS. Backend pytest: 1,006 passed in 28.39s. The documentation-only follow-ups do not change this source/test result.
- Stage 1 remains **30/40 = 75% provisional**; Gate 10 remains **0/10 formally closed**; external criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39** remain OPEN. No ticks awarded. Stages 2–6 remain NOT SCORED. Overall 20.90% remains historical only.
- ZERO COST preserved; no paid services, plan upgrade, credentials, Termux command/package/repository/keyring change, or APK release. `main` remains untouched.
- Detailed cycle: [docs/WORK_CYCLE_2026-11-17_GATE10_WEBSOCKET_AUDIT.md](docs/WORK_CYCLE_2026-11-17_GATE10_WEBSOCKET_AUDIT.md).

---

## Latest exact-head audit — 2026-11-14 (Gate 10 work cycle)

- Latest exact-HEAD verified source/test checkpoint on `phase-2/market-data-foundation`: `462bca4342d6cb585b6b389ae5996020c4c47dd3` (`fix(security): correct scoped Gitleaks allowlist syntax`). The exact-head Automated Tests #1149, CodeQL #507 and Full Git History Secret Audit #88 all completed successfully.
- Automated Tests run #1141: **success** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43593913966
- CodeQL run #499: **success** for Python and JavaScript/TypeScript — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43593913979. A successful analysis is not a claim of zero alerts.
- Full Git History Secret Audit run #80: **success** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43593913868.
- A prior Automated Tests run #1138 on `02842b97c70bc6ea82841ea62953a406d1205d17` failed in **Run backend tests**; subsequent commits `6c58daea1312e78d51956323ca03a2a9b6375e20` and `b37c69d6aaee2f764c3357834e868a3e53bddbe1` have successful full CI runs. The failed run is retained as history, not hidden or described as a pass.
- The Gate 10 Android-host architecture audit is repository evidence only. It confirms the current APK workflow packages the frontend and does not bundle/supervise FastAPI or Redis. Android/Bionic, Termux package trust, cryptography import, Redis TLS/ACL/persistence, Firebase lifecycle, Android TLS trust, SQLite durability, and Android process recovery remain unproven on the actual phone.
- No Termux command/package/repository/keyring change, backend runtime change, production secret, paid service, provider subscription, or APK release was made in this audit.
- Stage 1 remains **300/400 ticks = 75% provisional**. External criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39** remain OPEN (0/10 externally accepted). Stages 2–6 remain NOT SCORED. Overall **20.90%** remains a historical checkpoint only; no new weighted overall percentage is claimed.
- `main` remains untouched; all work remains on `phase-2/market-data-foundation`.

# DEZZTA CHART — Project Status

> **Progress-history correction (2026-11-05):** The owner clarifies that conversational checkpoints progressed from **20.3% to 20.9%**. The older **19.60%** remains a historical formal estimate, not a later regression. **19.9% is not a verified calculation.** Do not publish a fresh overall percentage until the milestone ledger reconciles these records.

Last audited: 2026-11-17
Repository: deszztagd377-pixel/dezzta-chart
Baseline branch: main
Baseline main HEAD: e3841681bc69b73619058deaf939df82ae5116a1
Working branch: phase-2/market-data-foundation
Latest exact-head source/test checkpoint: 5a0c106d388b78ebb2c7821893d918879c5415da (Automated Tests & Build 44105086185, CodeQL 44105086159, Full Git History Secret Audit 44105086295 passed; backend 1,006 passed)
Audited application-source baseline: 436f8b374b8bf5ef1ef4b51944f0c99603acd12c
`main` remains the protected baseline and is not a work target.

## Latest completed CI checkpoint — 2026-11-10

- Verified working-branch HEAD: `a10414984b78e4782c127b3feb30ae498ddc0c07` on `phase-2/market-data-foundation`; the branch ref resolves to this exact commit. Protected `main` remains `e3841681bc69b73619058deaf939df82ae5116a1`.
- Automated Tests [#811](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42736356065) completed successfully on this exact HEAD. All 25 listed job steps passed, including frontend install/audit/tests/build and bundle-secret scanning; backend install/tests/audit; container build; Redis-backed shared-guard and mounted-volume/restart smoke; Trivy HIGH/CRITICAL scan; report export/upload; and cleanup.
- CodeQL [#169](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42736356177) completed successfully on the same exact HEAD for Python and JavaScript/TypeScript. Successful analysis does not prove zero CodeQL alerts.
- Vercel reported success for this exact commit according to the GitHub combined commit status. This is frontend deployment evidence only; the exact deployment URL was not separately retrieved in this audit.
- No failed CI or CodeQL job step was found in the exact-HEAD run summaries. The successful CI container smoke verifies an isolated ephemeral Redis and test volume; it does not verify the actual production Fly Volume, managed Redis network/failover, external backup/restore, production Firebase project, or deployed Android/web market-data session.
- This checkpoint changes no application runtime code, database schema, production credentials, production infrastructure, or provider configuration. The prior `70f3edc` checkpoint and its CI #810 / CodeQL #168 results remain historical evidence below.
- Stage 1 remains **75.00% provisional** under the historical equal-weight ten-group method. The six production acceptance gates and owner approval of scoring criteria remain open; CI, CodeQL, and Vercel success do not close those gates or justify a percentage increase.

## Previous exact-HEAD follow-up — 2026-11-10 (70f3edc / CI #810)

- Latest verified working-branch commit: `25d46d9ab4699d8924865eaf19680464cfaf691e`, message `docs(stage-1): record latest exact-head CI verification`. Its diff changes only `PROJECT_STATUS.md`; the audited application-source baseline remains `436f8b374b8bf5ef1ef4b51944f0c99603acd12c`.
- Automated Tests [#807](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42646491732) completed successfully for this checkpoint. The Test and Build job completed all 25 listed steps successfully: frontend dependency install/audit, unit tests, production build, bundle-secret scanner tests and production bundle scan; backend dependency install/tests/audit; container build; Redis/shared-guard and persistent-volume/restart smoke; Trivy scan; vulnerability-report export/upload; and cleanup.
- CodeQL [#165](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42646491842) completed successfully for both Python and JavaScript/TypeScript jobs on this checkpoint. Successful analysis does not prove that there are zero CodeQL alerts.
- Vercel commit status for `25d46d9ab4699d8924865eaf19680464cfaf691e` is success: [deployment](https://vercel.com/deszztagd377-pixel/dezzta-chart/HJGV4U5ipcWZoJ3SBditJYZGTY4n). This is frontend deployment status only; it does not validate production backend, Firebase session/revocation behavior, or live market-data delivery.
- The protected `main` baseline remains `e3841681bc69b73619058deaf939df82ae5116a1`; no changes were made to `main`.
- No failing step was present in the completed CI #807 or CodeQL #165 job summaries. No application runtime source, production credentials, production infrastructure, database schema, or provider configuration was changed in this documentation checkpoint.
- Stage 1 remains **75.00% provisional**. The six production acceptance gates and owner approval of scoring criteria remain open. A green CI, CodeQL, or Vercel status does not close those gates or justify a progress increase.

## Latest exact-HEAD follow-up — 2026-11-09

- Active branch HEAD verified: `436f8b374b8bf5ef1ef4b51944f0c99603acd12c`; protected `main` remains `e3841681bc69b73619058deaf939df82ae5116a1`.
- Automated Tests [#806](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42645120887) completed successfully on the exact branch HEAD. All job steps passed, including frontend install/audit/tests/build and bundle-secret scans; backend install/tests/audit and container build; isolated Redis guard and persistent-volume/restart smoke; Trivy HIGH/CRITICAL scan; vulnerability-report export/upload; and cleanup.
- CodeQL [#164](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42645120945) completed successfully on the same exact HEAD for Python and JavaScript/TypeScript. Successful analysis is not evidence of zero CodeQL alerts.
- Vercel commit status for this exact HEAD is success: [deployment](https://vercel.com/deszztagd377-pixel/dezzta-chart/4Ji4ST4ftFsZB1AeiwxgpAJTYP9f). This does not validate backend, Firebase production authentication, or live provider delivery.
- Trivy report artifact [13687016777](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42645120887/artifacts/13687016777) was exported and uploaded. The configured HIGH/CRITICAL image-scan gate passed; the report remains scoped to the CI backend image and configured OS/library scan.
- This follow-up records verification and corrects the previously stale audit HEAD above. No application source, production infrastructure, production credentials, database schema, or `main` branch changed.
- Stage 1 remains **75.00% provisional**. The six production acceptance gates and owner approval of scoring criteria remain open; CI, CodeQL, and Vercel success do not close them.

## Latest verified source/CI checkpoint — 2026-11-09

- Exact source/CI baseline: `9a3a7e8efb80922c0ee67ec4dc795a43cb4ad873` on `phase-2/market-data-foundation`. Two subsequent commits on this branch contain documentation-only audit corrections; the latest workflow run validates that documentation-updated branch head. The protected baseline `main` remains at `e3841681bc69b73619058deaf939df82ae5116a1`.
- Automated Tests [#803](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42643369939) completed successfully on this exact HEAD. The Test and Build job completed all 25 steps successfully, including frontend install/audit/tests/build, frontend bundle-secret scanner tests and production scan, backend install/tests/audit, container build, Redis/shared-guard and persistent-volume/restart smoke, Trivy HIGH/CRITICAL scan, report export/upload, and cleanup.
- CodeQL [#161](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42643369940) completed successfully on the same exact HEAD for Python and JavaScript/TypeScript. Successful analysis does not establish that the repository has zero CodeQL alerts.
- Vercel reported deployment success for this exact HEAD: [deployment](https://vercel.com/deszztagd377-pixel/dezzta-chart/4zgL9ZxuP2VKTHPVcWmCMxCWfyHA). This verifies the Vercel deployment status only; it does not verify the separately deployed backend, Firebase production authentication, or live market-data delivery.
- Authentication source audit correction: `src/main.tsx` wraps `App` in `AuthProvider`; `src/components/SettingsPanel.tsx` renders `AuthPanel`, and `App.tsx` renders `SettingsPanel` when Settings is selected. The sign-in panel is therefore integrated into the Settings screen. `src/auth/AuthProvider.dom.test.tsx` provides React DOM lifecycle coverage. Older statements in this file claiming that AuthProvider is unmounted or that DOM lifecycle tests do not exist are superseded by this audit.
- The backend WebSocket route verifies Firebase ID tokens directly and enforces per-series entitlement. A real Firebase-project signed-token E2E for valid, expired, revoked, and wrong-project tokens has not run. A separate short-lived scoped WebSocket-ticket exchange/signing-key lifecycle is not implemented and must follow an approved threat model and key-management design before production.
- Six Stage 1 production gates remain open: (1) authorized real Firebase signed-token E2E and production session/revocation behavior, plus an approved decision and implementation for any scoped WebSocket-ticket exchange; (2) actual production Fly Volume ownership/permissions and restart verification; (3) encrypted off-host backup, retention, and restore drill; (4) managed Redis TLS/private networking/failover; (5) deployed backend HTTPS/WSS and Android/web smoke tests; (6) production monitoring/observability and fault/recovery verification.
- Stage 1 remains **75.00% provisional** under the historical equal-weight ten-group method. CI, CodeQL, Vercel, and documentation corrections do not close production gates or justify additional percentage credit. Owner approval of the scoring acceptance criteria remains pending.
- No production credentials, runtime configuration, application runtime behavior, database schema, production infrastructure, or `main` branch were changed.

## Previous verified CI checkpoint — 2026-11-09 (95c0dce)

- Automated Tests [#785](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42627632001) and CodeQL [#143](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42627631896) completed successfully on exact commit `95c0dcecd3e929577043a2da3f4764081116bc4a`.
- This was the evidence checkpoint used to reconcile the root lockfile, CI clean install, SQLite backup helper limitations, production configuration requirements, and outstanding Stage 1 gates.

## Previous verified CI checkpoint — 2026-11-08

- Automated Tests [#778](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42450151950) completed successfully on exact commit `a579d291bda6eba3dd1191ff4fc93d6c27db8865`. All 25 job steps succeeded: frontend dependency install/audit/tests/build, bundle secret scanning, backend dependency install/tests/audit, container build, isolated Redis smoke test, SQLite persistence/restart checks, Trivy scan, vulnerability report export/upload, and cleanup.
- Backend pytest result: **517 passed, 1 warning in 16.09s**. The warning is recorded separately for review; the test suite did not fail.
- Container smoke test passed: health JSON, Redis-backed rate limit (200 then 429), non-root runtime UID/GID 10001:10001, mounted volume/database ownership, SQLite integrity, and restart persistence.
- Trivy HIGH/CRITICAL scan completed successfully. The JSON report artifact `container-vulnerability-reports` uploaded successfully (artifact ID `13605158250`). A passing configured scan is not a substitute for reviewing the complete report or assessing severities outside the configured gate.
- CodeQL [#136](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42450151944) completed successfully on the same exact commit, including Python and JavaScript/TypeScript analysis.
- Non-blocking CI warnings observed: Redis service container reports host `vm.overcommit_memory` is disabled; GitHub Actions reports the pinned upload-artifact action targets deprecated Node.js 20 and is being forced to Node.js 24. Neither warning caused this run to fail. Review action upgrade compatibility and host-level Redis settings before production.
- The preceding CI [#776](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42449365067) failed due to shell parsing of the UID/GID diagnostic line, not incorrect volume ownership. The parser correction in commit `2c4f36c...` was validated by #777 and subsequent #778.
- No progress credit is assigned from CI or documentation-only updates. Overall remains **20.90%** and Stage 1 **75% provisional**; proposed milestone weights remain unapproved.
- Remaining Stage 1 gates: real React DOM AuthProvider lifecycle tests; authorized Firebase signed-token E2E (valid, expired, revoked, wrong-project); real Fly Volume permission/restart verification; encrypted off-host backup, retention and restore drill; managed Redis TLS/failover/private networking; deployed HTTPS/WSS smoke tests; monitoring/observability.
- Vercel deployment for this exact HEAD has not been verified in this checkpoint. Do not reuse older deployment status as evidence.

## Overall progress

- Historical progress records: 19.60% older formal estimate; owner-confirmed conversational checkpoints 20.30% → 20.90%. These are not a newly recalculated current score. The proposed 100%-weighted model is in [docs/PROJECT_MILESTONE_LEDGER.md](docs/PROJECT_MILESTONE_LEDGER.md); owner review and criterion scoring remain pending. See [docs/PROJECT_PROGRESS.md](docs/PROJECT_PROGRESS.md).
- Progress is a weighted milestone estimate, not a code-line percentage or a claim of scientific measurement. Decimal precision is recorded to two places for consistent tracking.
- Latest weighted progress increment formally recorded remains +0.20 percentage points (19.40% → 19.60%) for backend WebSocket authorization and entitlement hardening. The frontend stream integration was subsequently wired into the chart and Firebase token lifecycle, but no new overall-progress increment is assigned until the milestone ledger is reconciled. No live provider delivery or deployment credit is included.
- Phase 2 includes the FastAPI backend, verified-definition catalog lifecycle, optional provider adapters, bounded OHLCV ingestion, validated snapshots, and an authenticated backend WebSocket broadcaster with atomic snapshot/watermark handoff. The frontend now starts/stops an authenticated stream supervisor for an eligible selected contract, obtains Firebase ID tokens through the auth provider, validates stream snapshots and sequence-guarded updates, and applies accepted data through the shared market-data store. This is code-level integration only; backend deployment, live provider delivery, synchronized exchange timing, and production freshness remain unverified. Instrument definitions, normalized OHLCV bars, and coverage/gap intervals have durable SQLite storage; bounded explicit historical gap recovery is implemented.

## Current foundation

- React 18, TypeScript 5, Vite 6 (package manifest declares `vite: ^6.4.4`).
- Lightweight Charts 5 is installed.
- Existing candlestick chart currently uses hard-coded sample OHLC values from January 2024.
- Existing chart interaction includes zoom/scroll, pinch scaling, drag scrolling, and crosshair configuration. Interaction options have focused unit coverage.
- A timeframe type and selector exist for second, minute, hour, day, week, and month intervals.
- An OHLCV aggregation utility and Vitest unit tests exist.
- GitHub Actions currently runs `npm ci`, frontend dependency audit, frontend unit tests/build, frontend bundle-secret tests/scanning, backend dependency install/tests/audit, backend container build, Redis-backed container smoke test, Trivy HIGH/CRITICAL scan, and vulnerability-report export/upload. Run [`42053572558`](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42053572558) is an older historical CI run on exact branch HEAD `8ae99f5c5a11cdfb8b5d52acc1455a47259f194b` (2026-11-05), not the current workflow baseline.

## Verified limitations

- No live market-data provider session is configured. Optional Databento source adapters and the provider lifecycle exist behind explicit server-side flags, but the current deployment has no provider credentials/session and no real provider delivery is claimed.
- The selected timeframe is included in the chart's data-series identity. The chart accepts backend bars only after exact-series and payload validation; otherwise the clearly labelled DEMO fixture remains visible. The frontend stream path is wired at code level, but end-to-end operation against a deployed backend/provider has not been verified.
- Watchlist now displays an explicitly offline, read-only supported-product catalog fixture for ES/NQ/GC; no expiry-specific contracts are fabricated.
- The existing sample candles are not real market data.
- Global indicator requirement: every indicator must be designed for compatibility across all supported chart timeframes, including second-based intervals. This is a target to validate per indicator, not a claim that every calculation is automatically valid on every timeframe.
- Performance requirement: minimize avoidable latency, rendering work, memory growth, and UI blocking; test responsiveness under representative data loads. Zero bugs or zero lag cannot be guaranteed, so regression testing and explicit error handling are mandatory.
- Candle timer requirement: show a remaining-time countdown at the right side of the chart, aligned near the price scale. Derive it from candle interval boundaries and a synchronized clock; never hardcode a countdown or imply exchange-synchronized time when only the device clock is available.
- Data freshness requirement: clearly distinguish source-event time, receive time, and display time. Do not label sample, delayed, or unsynchronized data as live/real-time. End-to-end freshness depends on provider, network, backend, and device.
- Watchlist contains a read-only offline ES/NQ/GC catalog fixture. Settings exposes the grid visibility preference and reset behavior; broader account, chart-layout, and indicator settings are not implemented.
- Drawing tools, indicator tier navigation, Volume Profile, Footprint, Heatmap, Liquidation Maps, chart-layout/settings persistence, and Android packaging are not implemented.
- Root `package-lock.json` is present at the audited branch HEAD with `lockfileVersion: 3`; `.github/workflows/ci.yml` uses `npm ci`. The lockfile/clean-install migration is implemented at repository/CI level. React DOM lifecycle coverage is present in `src/auth/AuthProvider.dom.test.tsx`; the latest CI run executes this test suite.

## Phase 2 — Market Data Foundation

Status: provider and initial instrument scope selected; transport contract, backend scaffold, instrument catalog, and pure definition-record adapter added. No live provider session has been configured.

### Selected provider and data requirements

- Primary provider selected for future evaluation: Databento.
- Primary CME dataset target: `GLBX.MDP3`, subject to account entitlement, exchange licensing, and approved use.
- The previously proposed MBO schema is a technical data-format target only; no live feed is configured or being consumed.
- Initial instrument metadata scope: ES, NQ, and GC product identifiers.
- These are futures product roots, not fixed-expiry contracts. Any future instrument metadata must be resolved from verified provider definitions rather than fabricated symbols or hard-coded contract months.
- Databento definition records expose fields such as `raw_symbol`, `instrument_id`, `publisher_id`, `instrument_class`, `expiration`, `min_price_increment`, and `ts_event`. Expiration and fixed-point price values use nanosecond and 1e-9 units respectively. See [Databento instrument definitions](https://databento.com/docs/schemas/instrument-definitions).
- Databento supports raw, instrument-ID, parent, and continuous symbology; these have distinct mapping behavior. See [Databento Live API](https://databento.com/docs/api-live?lang=python).
- Credentials must never be embedded in frontend code or Android packages.

### Completed in this phase

- FastAPI health/status endpoints and authenticated app-facing WebSocket scaffold.
- Provider-neutral `InstrumentCatalog` with outright-futures validation, expiry sorting, root filtering, atomic full-snapshot replacement, timestamp-ordered upserts/deletes, and tombstones against stale resurrection.
- `GET /v1/instruments` endpoint with honest empty-catalog behavior before provider definitions exist.
- Frontend instrument-catalog DTO and offline fixture for ES/NQ/GC, with tests confirming that no unverified contract metadata is invented.
- Read-only Watchlist catalog panel clearly marked OFFLINE FIXTURE; chart tab remains separate.
- Pure `databento_definitions.py` adapter that maps DBN-like definition objects into validated plain mappings without networking or credentials.
- Provider-neutral in-memory OHLCV pipeline with nanosecond timestamps, exact Decimal OHLCV values, timeframe bucket validation, atomic snapshot replacement, duplicate-snapshot replacement, and stale revision protection.
- Versioned frontend OHLCV transport DTO preserving timestamp and decimal precision as strings.
- Frontend OHLCV snapshot runtime validator and chart-boundary adapter: validates the versioned envelope, decimal-string values, nanosecond timestamps, OHLCV invariants, and chronological order per instrument series; converts to chart numbers only at the rendering boundary and requires an exact series identity.
- Read-only `GET /v1/ohlcv` snapshot endpoint; returns an explicit unavailable state while no provider adapter has populated the pipeline.
- Unit tests for catalog normalization, fixed-point values, nanosecond expirations, adapter field mapping, byte-symbol decoding, required-field checks, ordering, update/delete lifecycle, and stale-event rejection.

### Not implemented

- No production live or historical provider session, provider download, or subscription is configured or verified.
- Databento SDK source adapters and the normalized bounded OHLCV ingestion path are implemented, but provider access is disabled by default and no real account/session has been validated. Do not enable provider flags without a separate review of entitlement, exchange licensing, explicit symbols, historical query costs, and operational limits.
- Backend OHLCV WebSocket broadcast and atomic snapshot/watermark handoff are implemented. The frontend transport is now wired at code level into the chart lifecycle and shared market-data store: `CandlestickChart` obtains Firebase ID tokens through `AuthProvider`, starts/stops the stream supervisor, validates snapshots and sequence-guarded updates, and consumes accepted events. This does not verify a deployed backend or live provider delivery. Further operational checks such as deployed end-to-end validation, reconnect behavior under real network transitions, heartbeat policy, and sustained-load performance remain outstanding.
- Historical provider definition refresh now feeds the durable journal/synchronizer when explicitly invoked by the provider lifecycle. There is no periodic refresh scheduler, and no real provider account/session has been validated.
- Databento definition events, canonical instruments, point-in-time provider mappings, and metadata revisions are persisted in SQLite with replay-safe transitions. OHLCV base/derived bars and coverage/gap intervals are also persisted. Bounded manual historical gap recovery is implemented using exact resolver mappings and configured query windows. The instrument catalog and WebSocket event delivery remain process-local; automatic gap-recovery scheduling and frontend stream replay remain unimplemented.
- The authenticated WebSocket supports exact-series OHLCV snapshot subscriptions and bounded in-memory updates for accepted base and derived bars. The underlying bars now survive backend restart in SQLite, but the WebSocket event stream itself is not a durable event log and does not replay missed client updates. It does not provide order-book/MBO events.
- No brokerage or order-execution integration.
- No Footprint, Heatmap, or Liquidation Maps implementation; these three Exclusive Indicators are reserved for one coordinated Claude-assisted workflow after the project owner supplies visual references for each.
- Mid Tier is undecided. Earlier candidates such as VWAP, ATR, ADX/DMI, Stochastic, CCI, OBV, MFI, Ichimoku Cloud, Supertrend, and Keltner Channels are discussion-only and are not approved members. Volume Profile is not in Mid Tier.
- Low Tier must contain exactly 15 common/popular TradingView-style indicators. RSI, MACD, and Bollinger Bands are the only exact names recovered from prior approval; the other 12 names must be confirmed before their implementation. Do not leave the category empty or invent a claimed owner-approved list.
- A separate Tools-menu Volume Profile tool is also planned: it displays a compact profile visualization at the chart side, without the full indicator's data-value presentation; users can move/resize its selected chart range and the profile recalculates for that range.
- Indicator navigation is planned as three categories: Low Tier (exactly 15 common indicators), Mid Tier (owner selection pending), and Exclusive Indicator Pro (Footprint PRO 2GD, Heatmap, Liquidation Maps, and full Volume Profile with detailed values). Tools are a separate entry point, not another indicator category.
- Exclusive Indicators remain owner-controlled: only the project owner can add new members to this tier.
- These are recorded product requirements only; no indicator or Tools UI implementation has started.

## Planned engineering sequence

1. **Completed foundation:** populate the durable canonical instrument registry, point-in-time provider mappings, and versioned metadata from strictly normalized provider definitions; journal source events before processing and recover pending events after restart. Live credentials, provider delivery, and scheduled refresh remain separate validations.
2. Define a trusted, admin-only entitlement grant process for canonical instruments; keep client-facing grant endpoints disabled.
3. Review and verify the approved Firebase app configuration and sign-in/session behavior in a deployed test environment; confirm ID-token refresh and entitlement behavior without exposing credentials or enabling provider delivery.
4. Harden and validate the already-integrated frontend stream lifecycle using controlled test fixtures: reconnect/backoff, heartbeat/timeout behavior, visibility/network transitions, and fresh-snapshot recovery after sequence gaps.
5. Smoke-test the integrated client against a deployed backend with Firebase auth and entitlement configured, with provider features disabled until separately approved and verified.
6. Build the three indicator-tier navigation categories and visible indicator controls/overlays/panes on top of `useMarketIndicators`, with timeframe compatibility and performance tests. Low Tier requires the approved 15-item list; Mid Tier remains pending owner selection.
7. Implement the full Exclusive Volume Profile and the separate compact movable-range Volume Profile Tool as distinct features.
8. Integrate Footprint PRO 2GD, Heatmap, and Liquidation Maps in the coordinated Claude-assisted workflow after the owner supplies the required visual references and the complete source/reference package is available.

## Non-negotiable product constraints

- Preserve normal candlestick spacing when Footprint mode is OFF.
- Only Footprint ON may activate a dedicated spaced-candle/cluster layout.
- Do not implement Footprint, Heatmap, or Liquidation Maps visuals before the project owner supplies reference images; their combined large implementation task is intended for Claude.
- Keep Volume Profile Mid Tier separate from the compact movable-range Volume Profile Tool in the Tools menu.
- All indicator implementations must include timeframe-compatibility tests, including second intervals where supported, plus performance and regression checks.
- Candle countdown belongs on the right edge near the price scale and must use interval-boundary calculations with explicit clock/data freshness semantics.
- Preserve existing working chart interactions and avoid unrelated visual redesign.
- Never fabricate provider data, contract expiry, or feed status.

## Change log

### 2026-11-02 — Frontend OHLCV contract adapter
- Added runtime validation for the versioned OHLCV snapshot envelope and every bar; validates decimal strings, nanosecond timestamps, OHLCV boundaries using exact BigInt decimal comparison (no pre-render floating-point rounding), safe identifiers/sequences, and feed-state values.
- Chronology is validated per series identity (dataset, publisher, instrument, raw symbol, timeframe), because distinct series may legitimately share a bucket timestamp.
- Added an exact-identity chart adapter. Decimal and nanosecond strings are converted to JavaScript numbers only at the chart boundary; bars from other instruments/timeframes are excluded.
- Added regression tests for valid precision-preserving payloads, malformed values, invalid OHLC boundaries including sub-floating-point precision differences, negative volume, duplicate same-series timestamps, mixed-series timestamps, exact identity filtering, and unavailable snapshots.
- GitHub Actions run #98 passed frontend tests, production build, and backend tests.
- This is a tested adapter only: no HTTP request lifecycle, instrument picker, live provider connection, or chart data replacement has been enabled.
- Working branch head for this implementation: `5f8ee7ab78537105d5d51d7c700e41f3ebfcc8a4`.
- Overall estimated progress: 18.20% (+0.20 percentage points from the documented 18.00% baseline).


### 2026-11-02 — Chart interaction and viewport regression coverage
- Extracted chart interaction options into `src/utils/chartOptions.ts`; added tests for drag scrolling, pinch/wheel scaling, grid visibility, and second-display configuration.
- Added `getMeasurableChartSize` to reject zero, negative, or non-finite viewport dimensions before calling the chart resize API.
- Added viewport measurement regression tests. These are pure unit tests; they do not replace physical Android rotation, touch-gesture, or tab-switch validation.
- Latest working-branch commit at this audit: `51edcd05597eb80054a7cb6b2db245af98c75e9c`.
- CI run #91 and Vercel status for this change are being verified separately.


### 2026-11-02 — Mobile layout and chart lifecycle hardening
- Added a chart initialization error state with an accessible alert and a loading status; cleanup disconnects the resize observer and removes the chart instance.
- Preserved the lifecycle guard so queued resize callbacks do not update the chart after teardown.
- Added viewport-fit support and top/bottom device safe-area spacing for the header and bottom navigation.
- Latest audited working-branch commit: `51edcd05597eb80054a7cb6b2db245af98c75e9c` (viewport measurement guard; CI run #91 is being verified).
- GitHub Actions and Vercel checks for that commit were verified successful. Direct visual verification on a physical Android device is still outstanding.
- The overall progress estimate remains 18%; these reliability guards and tests improve foundation quality but do not yet deliver a major user-facing capability.


### Timeframe engine audit — 2026-11-01
- Audited the current timeframe engine, selector, chart component, and app wiring.
- Fixed duplicate source-candle snapshot handling: when multiple valid OHLCV snapshots share a timestamp, aggregation now uses the last supplied snapshot rather than incorrectly summing repeated cumulative volume and mixing revisions.
- Added regression coverage for duplicate-timestamp snapshots and input immutability.
- Important limitation confirmed: the current chart fixture contains daily date-only OHLC values and no volume field. It cannot honestly produce second/minute/hour candles or volume-based calculations. The timeframe selector still does not represent a functional multi-resolution data pipeline; chart integration is deferred until a properly timestamped base-resolution OHLCV fixture/data contract is available. No synthetic or fabricated market data will be presented as live.

### 2026-11-01
- Created the Phase 2 working branch from the audited main branch.
- Added typed frontend market-data contracts and transport documentation.
- Added FastAPI backend scaffold and authenticated status WebSocket.
- Added provider-neutral futures instrument catalog with validation, sorting, filtering, and tests.
- Added pure Databento definition-record adapter and tests; no provider client or network connection was created.

### 2026-11-01 — Instrument lifecycle and indicator product requirements
- Added timestamp-ordered catalog upserts and deletions, plus tombstones to reject stale resurrection events.
- Documented complete-snapshot replacement semantics and added lifecycle regression tests.
- Recorded the planned Low Tier / Mid Tier / Exclusive indicator categories and the separate Tools-menu Volume Profile tool.
- Recorded Footprint, Heatmap, and Liquidation Maps as one Claude-assisted Exclusive Indicators workstream pending user visual references.

### 2026-11-01 — Global indicator, timing, and performance requirements
- Recorded the cross-timeframe compatibility target for all indicators, including second-based intervals, with validation required for each calculation.
- Recorded performance, regression-testing, and explicit error-handling requirements; no absolute zero-lag/zero-bug guarantee is made.
- Recorded right-side candle-expiry countdown placement and synchronized-clock/data-freshness requirements.
- Expanded Mid Tier planning to approximately 10 indicators; Volume Profile is confirmed and the candidate list requires owner approval.
- Recorded common indicators as Low Tier and confirmed that additions to Exclusive Indicators are controlled only by the project owner.

### 2026-11-01 — Frontend instrument catalog fixture
- Added typed frontend catalog snapshot contract and an explicit offline fixture for ES, NQ, and GC product roots.
- Added fixture tests proving that no expiry-specific contract or active contract is fabricated.
- Added a read-only Watchlist catalog panel, clearly marked OFFLINE FIXTURE; chart rendering remains in its own tab.


### 2026-11-01 — OHLCV pipeline foundation
- Added provider-neutral in-memory OHLCV bar validation and ingestion with exact decimal values and nanosecond timestamps.
- Added UTC-aligned second/minute/hour/day/week/month/quarter bucket validation.
- Added atomic snapshot replacement, last-supplied duplicate snapshot semantics, and event-time/sequence stale-revision protection.
- Added a versioned frontend OHLCV DTO and a read-only snapshot API that reports unavailable while no provider adapter is connected.
- Added backend unit and API regression tests. Local isolated OHLCV unit checks: 14 passed; full repository CI remains unverified until the latest GitHub Actions run is confirmed.


### Phase 2 update — OHLCV provider adapter (working copy of phase-2/market-data-foundation)
- Added: multi-dimensional bar identity + local `sequence_origin`, point-in-time instrument resolver,
  Databento OHLCV record adapter (exact fixed-point), tiered UTC aggregation with completeness labels,
  bounded single-writer ingestion with visible overflow/gap handling, provider lifecycle manager,
  bounded historical window backfill, retention + `/v1/ohlcv` filters, root allow-list config.
- Verified by execution (local shim runner, see backend/README): pure-Python unit tests.
- NOT verified: real FastAPI/pytest run, CI, and every call into the real `databento` SDK
  (`databento_sources.py` and the duck-typed record attributes are UNKNOWN until exercised with a key).
- Not done: Databento SymbolMapping ingestion, exchange trading-day sessions, WebSocket broadcast,
  continuous contracts, persistence, MBO/footprint/heatmap.
- Overall progress figure above is intentionally left unchanged; it is the project owner's estimate.

### Audit corrections prepared after Claude patch review
- Databento live close wait uses the documented `block_for_close()` method.
- Instrument definitions are required before live normalization; startup now attempts an explicitly enabled definitions refresh when the resolver is empty.
- Coverage is keyed per provider/dataset/publisher/instrument/series/symbol. Live OHLCV observations no longer imply continuous coverage because no-trade intervals produce no record.
- Overflow gaps are aggregated by instrument identity instead of a bounded 1,024-entry event list; retry budget resets only after a stable session.
- Snapshot replacement rejects conflicting raw symbols for one instrument identity; undefined timestamp sentinel is rejected.
- These changes still require native CI and real SDK verification. Overall progress remains unchanged.


### 2026-11-02 — HTTP OHLCV client foundation
- Added `src/services/ohlcvClient.ts`: read-only GET client for the existing `/v1/ohlcv` endpoint, using the backend's exact snake_case query parameter names.
- Requests require a complete series identity (dataset, publisher ID, instrument ID, raw symbol, timeframe); no contract identity or API URL is fabricated.
- Added request timeout, caller cancellation, no-store caching, HTTP/network/JSON/schema/configuration error classification, and validated conversion through the existing OHLCV adapter.
- Snapshot outcomes distinguish ready, degraded, and unavailable. A non-live feed state is never reported as confirmed ready; a response with no bars matching the exact requested series is unavailable.
- Added `src/services/ohlcvClient.test.ts` with 13 tests covering query construction, exact series isolation, ready/degraded/unavailable states, malformed responses, HTTP/network failures, timeout, cancellation, and invalid configuration.
- GitHub Actions run #101 initially exposed a test-harness unhandled-rejection timing issue in the timeout test. The test was corrected to attach its rejection assertion before advancing fake timers; the corrected latest run is #102.
- Latest implementation commit: `1f8f9fc7075902879cbc27363d1bd9fbe2516ba2`; timeout-test correction commit: `945601c2cee56db39956d174b527e8b8150f24b4`.
- Remaining: no backend base URL or verified selected contract is configured in the frontend; the client is not yet wired into the chart. DEMO candles remain clearly labeled and unchanged. No live data is claimed.


### 2026-11-02 — Verified instrument catalog and selection lifecycle
- Added `src/types/instrumentCatalogApi.ts` for the backend's provider-backed catalog response and outright futures contract metadata.
- Added `src/services/instrumentCatalogClient.ts` to call the existing read-only `GET /v1/instruments?root=...` endpoint with timeout, cancellation, no-store caching, and explicit configuration/network/HTTP/JSON/schema errors.
- Added runtime validation for supported roots, outright futures class, raw-symbol/root consistency, positive safe provider identifiers, ISO expiration dates, decimal tick-size strings, dataset consistency, catalog counts, and duplicate contract identities.
- The catalog validator accounts for backend semantics: `state` describes the global catalog before an optional root filter, so a ready global catalog may legitimately return zero contracts for one selected root.
- Rebuilt Watchlist as a functional ES/NQ/GC filter with contract search (symbol, expiry, instrument ID), explicit contract selection, selected-metadata display, clear selection, loading/empty/error states, and retry. Requests are cancelled when the selected product changes; the App retains the selected metadata while navigating between tabs.
- Added `.env.example` with the non-secret `VITE_MARKET_DATA_API_BASE_URL` setting. No API key or provider credential is exposed to the frontend.
- Added focused parser and HTTP client tests, including invalid calendar dates, state/count consistency, empty root-filtered results, duplicate identities, cancellation, timeout, and request construction.
- The chart deliberately remains on its clearly labelled DEMO fixture. Contract selection is metadata-only until a backend URL, verified OHLCV series, and chart data lifecycle are connected. No live market data is claimed.
- Latest code commits: `eade18471527f9fb9e4cff5733c5de7127676398`, `f8b0c9295ad8937b02e14fa1419db25337e4ec69`, `9e601f68026dee400f3b90698335b0094f364e27`, `5616ca598251320c27f644e3f40f3a99c8bfad67`.
- Final CI and deployment status must be confirmed on the latest documentation commit before this stage is called fully verified.


### 2026-11-02 — Selected contract and timeframe chart data lifecycle
- Connected the selected catalog contract and selected timeframe to the existing validated `fetchOhlcvSnapshot` client.
- Every request carries dataset, publisher ID, instrument ID, raw symbol, and timeframe from the selected verified contract; the client continues to validate the full response before conversion.
- Switching contract or timeframe aborts the previous request. The chart first resets to its explicitly labelled DEMO fixture, so bars from the previous contract cannot remain visible while a new request is pending.
- Validated backend bars replace the demo fixture only when a non-empty exact-series result is available. Degraded feed results are labelled DEGRADED; unavailable and request errors leave the DEMO fixture visible with an explicit reason.
- Added `src/utils/candlestickSeriesData.ts` and tests to convert adapter epoch-second values into Lightweight Charts UTC timestamps without a milliseconds conversion.
- Added a non-secret `VITE_MARKET_DATA_API_BASE_URL` configuration path. The value is currently not configured in the deployed frontend, so production will honestly show the API configuration error and keep the DEMO chart until a backend URL is provided.
- Latest integration commit: `56a265ebc68b72402a3907f0ed644ab8281547b1`. The final branch-head CI and Vercel deployment are being verified.


### 2026-11-02 — Portable backend deployment foundation
- Added `backend/Dockerfile`: Python 3.12 slim image, runtime dependencies installed from the backend manifest, non-root runtime user, platform `PORT` support, and `/health` container health check.
- Added `docs/BACKEND_DEPLOYMENT.md` with reproducible build/run/smoke-test commands, exact-origin CORS guidance, Vercel API-base configuration, and secret-handling boundaries.
- Updated backend documentation to accurately distinguish implemented optional Databento source/provider lifecycle code from an actually configured or verified production provider session. Corrected stale claims that provider adapters did not exist.
- Extended GitHub Actions to build the backend container image after frontend tests/build and backend tests. This validates image construction, not a hosted deployment or external provider connectivity.
- Provider switches remain off by default; no API key, WebSocket token, or other secret was added to the repository.
- Hosting provider intentionally not selected: cost, region, availability/sleep behavior, and account controls must be reviewed before deployment.
- The latest Vercel status for the shared-indicator commit is failure with the platform message `upgradeToPro=build-rate-limit`; this is a hosting/build-rate limit, not evidence of a source compilation error. The latest GitHub Actions run result is not exposed by the available run-status response and is not claimed as passed here.
- Overall estimated progress: 19.05% (+0.20 percentage points for a reproducible backend container foundation and CI build step; no credit for actual backend deployment).


### 2026-11-02 — Shared chart and indicator data foundation
- Added `src/services/marketDataStore.ts` as the single in-memory source of truth for exact-series OHLCV bars, identity, status, detail, and monotonically increasing revision. Snapshots and bar objects are immutable; invalid identities, chronology, OHLCV boundaries, and non-ready bar publication are rejected.
- Connected `CandlestickChart` to publish only validated non-empty backend bars. Contract/timeframe switches synchronously clear old indicator input; DEMO candles remain chart-only and are never exposed to indicator calculations.
- Added `useMarketDataSnapshot()` for React consumers and `useMarketIndicators()` so indicator calculations are derived only from the same backend series selected by the chart.
- Added a reusable calculation foundation for SMA, EMA, Wilder RSI, MACD, and Bollinger Bands. Outputs align to source bars and retain null warm-up values; input validation is applied even when the available history is shorter than the warm-up period.
- Added unit tests for shared-store immutability, subscriber notifications, exact identity, stale-series clearing, invalid bars, calculation alignment, warm-up periods, edge cases, and invalid inputs.
- Added `docs/INDICATOR_DATA_ARCHITECTURE.md` defining the single-source-of-truth flow and future streaming integration contract.
- Important limitation: the current frontend still requests HTTP snapshots. Continuous live streaming, visible indicator UI, provider connectivity, and real-time Android validation are not implemented or claimed. The store is the shared integration point for future validated stream updates.
- Overall estimated progress: 19.40% (+0.35 percentage points for tested shared data architecture and reusable indicator calculations; no credit for visible indicator features or live streaming).

- Latest audited shared-indicator branch head at that earlier checkpoint: `aaed0226b8f55d7526c31b461238b357d05276a0`. The current stream-protocol work is recorded below; `main` remains untouched.

### 2026-11-02 — OHLCV stream protocol foundation (not yet connected)
- Added `src/services/ohlcvStreamProtocol.ts` with a versioned provider-neutral OHLCV update envelope, runtime validation, exact series-to-bar identity checks, and a per-stream sequence guard.
- Stream delivery sequence is deliberately separate from the nested local OHLCV bar revision sequence; the two counters have different scopes and cannot be substituted.
- Sequence decisions explicitly distinguish accepted-next, duplicate, stale/out-of-order, gap, wrong stream, and wrong series. A gap does not advance the watermark; only a verified snapshot watermark may reset it.
- Reuses the existing strict OHLCV snapshot validator so streamed bars inherit decimal-string, nanosecond, timeframe, OHLCV-boundary, and identity checks.
- Added focused tests for envelope/version validation, invalid identity and OHLCV payloads, duplicate/stale/gap handling, snapshot watermark reset, and stream/series isolation.
- Added `docs/OHLCV_STREAM_PROTOCOL.md` with the event shape, sequence semantics, atomic snapshot/watermark handshake requirements, bounded-queue policy, and recovery milestones.
- This is protocol and frontend validation groundwork only. No WebSocket OHLCV broadcast, frontend socket client, atomic snapshot watermark, reconnect loop, or stream-to-store publication is implemented yet. The existing backend WebSocket remains status-only.
- Overall progress remains 19.40% until the new tests/build and branch-head CI are independently verified; no credit is assigned for a live stream or user-visible indicator feature.
- Latest protocol implementation commit: `3b3cdb8eefbde740f8e44435fde6b9ebc96d6edb`; architecture documentation follow-up: `841acb7248e86a78ead0109c25ecd9341c7f4c46`. Immediately before this status refresh, the branch comparison was 149 commits ahead of `main`, 0 behind. The latest visible Vercel status remains a build-rate-limit failure; the available GitHub workflow-run lookup does not expose push-triggered runs, so CI is not claimed as passed.

### 2026-11-02 — Backend OHLCV WebSocket broadcast and snapshot handoff
- Added `backend/app/ohlcv_stream.py`: bounded per-series fan-out with an independent monotonic sequence per subscriber, unique stream/event IDs, exact series filtering, canonical decimal-string serialization, and explicit slow-consumer overflow state.
- Added an authenticated WebSocket subscription message (`market_data.subscribe`, version 1). The server returns a versioned OHLCV snapshot carrying `streamId` and `watermark`, then emits ordered `market_data.ohlcv.update` events.
- Snapshot query and subscription registration are synchronous on the same asyncio event loop, with no await between them. This is an atomic snapshot/watermark boundary relative to the current single-writer in-memory ingestion design.
- Connected accepted base-bar revisions to the stream hub. Updated the aggregation layer so accepted derived timeframe bar revisions are also broadcast to matching subscriptions; this is required for chart timeframes such as 5s/1m that are derived from base 1s data.
- Each client queue is bounded (256 updates). Queue overflow marks the subscriber for close with WebSocket code 1013, requiring a fresh snapshot; updates are not silently dropped while the connection remains active.
- Added backend tests for snapshot/watermark handoff, exact-series isolation, slow-consumer overflow, derived timeframe updates, authenticated snapshot delivery, invalid subscription rejection, and delivery from a fake live-ingestion callback.
- Updated backend README and stream/data architecture documentation.
- Important limitations: frontend WebSocket authentication/subscription/client reconnect is not implemented; the frontend has not yet applied stream updates to `marketDataStore`. Delivery is in-memory only and cannot replay across backend restart. No provider credentials/session or actual market feed are enabled or verified. No MBO/order-book feed is provided.
- Overall progress remains 19.40% until branch-head CI and the new backend tests are independently verified. No live-data or end-to-end frontend streaming credit is assigned.
- Latest code/test commit: `d9c9ed67ca52884247fb293d3adefa77ca010924`; final WebSocket status cleanup: `91284c5789ebb540fb09264b32e4f9a521f50eda`. Branch comparison at this status refresh: 168 commits ahead of `main`, 0 behind; `main` remains untouched. Latest visible Vercel status is failure with `upgradeToPro=build-rate-limit` (platform build-rate limit, not proof of a source compile failure). The available GitHub workflow-run lookup exposes no push-triggered run, so CI is not claimed as passed.


### 2026-11-02 — Backend OHLCV WebSocket broadcast and snapshot handoff audit
- Verified the active working branch is `phase-2/market-data-foundation`; comparison reports 172 commits ahead of `main` and 0 behind. `main` was not modified.
- Verified backend route `/ws/market-data` authenticates, accepts a version 1 exact-series subscription, sends a validated OHLCV snapshot with a stream ID and watermark, and then sends ordered updates.
- Verified `OhlcvStreamHub` uses bounded per-subscriber queues and forces a reconnect/resnapshot after overflow rather than silently skipping updates. Accepted base and derived timeframe revisions are wired into the hub.
- Verified frontend protocol parsing and sequence-guard groundwork exists, but no frontend WebSocket client is connected to the chart or shared store.
- Security gate: the backend currently uses one static server-configured WebSocket token. This is acceptable only as a controlled local/test scaffold; it must not be copied into the browser bundle or Android package. A production client requires a short-lived, narrowly scoped token delivered through a separately authenticated session or server-side gateway. No login/session provider is currently selected.
- CI status: not verified on the current branch head. The available commit-workflow lookup returned no push-triggered run; no test pass is claimed from this audit.
- Backend deployment and provider delivery remain unverified. Databento credentials/session are not configured; no real market feed is claimed.
- Overall progress remains 19.40%; no credit is assigned for frontend streaming, live provider delivery, deployment, or visible indicator UI.


### 2026-11-02 — Frontend streaming and authentication security gate review
- Re-audited the active branch's backend WebSocket route, frontend protocol parser/sequence guard, shared market-data store, HTTP snapshot client, and CI workflow definition.
- Confirmed the frontend has no WebSocket transport client; only protocol parsing and sequence-guard groundwork exists. No live stream integration or tests are claimed.
- Identified an additional production security requirement: the current WebSocket route validates series syntax and configured dataset, but does not authorize the authenticated principal for the requested publisher/instrument/raw-symbol/timeframe tuple. A shared static token is not a user identity or a series entitlement.
- Updated `docs/WEBSOCKET_AUTH_DESIGN.md` to record this authorization gap and require per-subscription entitlement checks backed by verified instrument definitions.
- The existing CI workflow is configured for pushes to this branch, but this audit did not obtain a verified latest-head run result. CI and tests remain unverified.
- Branch comparison after the documentation commits: 172 commits ahead of `main`, 0 behind. `main` remains untouched.
- No overall progress increase: frontend WebSocket transport, secure session/token issuance, per-series authorization, deployment, and live feed are still incomplete.


### 2026-11-02 — Multi-asset product direction and Firebase authentication prototype approval
- Owner confirmed the product direction includes equities, crypto, futures, FX, indices, and further asset classes where a verified source, venue, instrument definition, data schema, and license permit coverage. "All pairs" is a long-term coverage goal, not a claim that every global symbol is automatically available from one provider.
- Added `docs/MULTI_ASSET_MARKET_DATA_ARCHITECTURE.md` defining canonical instrument identity, provider-neutral adapters, asset-specific metadata, venue/session handling, source provenance, exact-series indicator rules, licensing gates, and staged delivery.
- Audited current implementation: `backend/app/instruments.py` and `backend/app/config.py` remain futures-focused, with ES/NQ/GC allow-list defaults; current instrument catalog and resolver are in-memory. The frontend shared store still uses futures-oriented exact series identity. Multi-asset support is therefore **not implemented** yet.
- Owner approved Firebase Authentication as the primary provider for an authentication prototype. Updated `docs/AUTH_PROVIDER_EVALUATION.md` to record the approval and require a provider-neutral identity verifier. No Firebase SDK, service account, credentials, token endpoint, WebSocket ticket, or per-series authorization code has been added yet.
- Firebase's official documentation confirms client ID-token retrieval and Python Admin SDK verification; ID tokens are short-lived (about one hour), while refresh tokens maintain sessions and can be revoked. See https://firebase.google.com/docs/auth/admin/verify-id-tokens and https://firebase.google.com/docs/auth/admin/manage-sessions.
- Databento coverage is dataset/venue-specific. It documents multiple asset classes, including equities, FX, futures, and options, but this does not establish universal global coverage or all crypto spot pairs. Exact availability, entitlements, and redistribution rights must be verified per product.
- No progress increase: these commits document approved architecture and do not implement multi-asset canonical IDs, authentication, live feed, persistence, frontend streaming, or deployment. Overall progress remains 19.40%.
- `main` remains untouched. Latest branch comparison and CI status must be checked separately; no CI pass is claimed by this status note.


### 2026-11-02 — Canonical multi-asset identity schema foundation
- Added an immutable provider-neutral canonical instrument schema for equity, ETF, crypto spot/perpetual, dated futures, options, FX pairs, and indices. The schema validates UUID identity, asset/type compatibility, venue/symbol, currency pairs, expiry, option-underlying relationships, and positive finite decimal metadata.
- Added matching frontend TypeScript contract and backend validation tests. Existing futures catalog, resolver, API routes, and selected-contract flow are intentionally unchanged in this first compatibility-safe step.
- Canonical UUIDs are registry-assigned and must be persisted; they are not derived from symbols or provider IDs. Provider mappings remain a separate identity layer.
- This is schema groundwork only: no durable registry/database, provider coverage, multi-asset catalog endpoint, entitlement system, Firebase integration, or live multi-asset data is implemented.
- Tests and CI must be run against the resulting branch head before claiming verification. Overall project progress remains 19.40% until implementation and test gates are independently verified.


### 2026-11-02 — Persistent instrument registry (SQLite adapter)
- Added a file-backed SQLite registry for immutable canonical instrument records and provider-scoped point-in-time mappings.
- Enabled foreign keys on every connection, WAL, bounded busy timeout, transactional writes with BEGIN IMMEDIATE, canonical-ID idempotency/conflict checks, immutable-row trigger, and database-level overlap triggers for provider mapping validity windows.
- Added bounded/filterable registry reads, exact timestamp mapping resolution, migration-version guard, and tests for restart durability, identity immutability, mapping scope, half-open validity windows, adjacent windows, overlap rejection, and concurrent writers.
- Integrated registry initialization into FastAPI application state with a backend-only database path setting. No public registry write endpoints were exposed; Firebase identity and per-series entitlement checks remain prerequisites.
- SQLite is a single-backend durable adapter only when deployed on a persistent volume. Multi-instance production requires a planned PostgreSQL adapter/migration and backup/restore validation.
- No live provider, exchange licensing, Firebase auth, public multi-asset catalog, or end-to-end real data is claimed by this milestone.
- Project progress remains 19.40% until the new and full regression suites are verified on the resulting branch head.


### 2026-11-02 — Provider metadata versioning design gate
- Audited the canonical identity value object, immutable SQLite registry, futures definition catalog, and in-memory point-in-time resolver before connecting provider refreshes.
- Identified a critical modeling boundary: the canonical value object contains both stable identity and mutable/provider-correctable trading metadata, while the SQLite canonical row is immutable. Directly persisting provider refreshes would either reject legitimate metadata revisions or weaken identity immutability.
- Added docs/INSTRUMENT_METADATA_VERSIONING.md defining three layers: stable canonical identity, append-only effective-time metadata revisions, and provider-scoped point-in-time mappings.
- Defined transaction, idempotency, out-of-order event, authoritative source, venue verification, migration, and unknown-history rules. No provider metadata is inferred and no historical validity is fabricated.
- This is an architecture gate only; no schema migration or provider ingestion integration is claimed. Existing ES/NQ/GC catalog and resolver remain unchanged.
- Project progress remains 19.40% until versioned metadata migration, provider integration, and regression tests are implemented and verified.

### 2026-11-04 — Branch-head verification and indicator-tier correction

- Re-verified the working branch `phase-2/market-data-foundation`. Before this documentation commit it was 302 commits ahead of `main` and 0 behind; this status-documentation commit makes the current comparison 303 ahead and 0 behind. `main` was not changed.
- Verified branch-head commit `65a63f0878476f52b22f9dae7a6f7f25b2888d77` with GitHub Actions run #293 (2026-11-03): frontend unit tests, frontend production build, backend tests, and backend Docker image build all completed successfully. This is CI evidence for that exact commit, not a claim of physical Android testing or live-provider connectivity.
- Audited the durable SQLite instrument registry: current schema version is 4, with sequential migrations v1→v2 (versioned metadata baseline), v2→v3 (relational option-underlying links), and v3→v4 (venue-scoped canonical identity uniqueness). Existing tests cover legacy migration preservation/rollback, unknown historical validity, append-only metadata revisions, half-open validity intervals, idempotent transitions, transaction rollback, out-of-order event rejection, and independent source timelines. The branch-head CI run passed the backend test job.
- The repository contains an educational simulated-footprint event fixture under `src/education/`; this is not the production Footprint engine. The production module directory `src/indicators/footprint/` and its complete engine/test integration are not yet present in the audited branch tree. Simulated educational fixtures must never be represented as real market trades or as the finished Footprint PRO 2GD indicator.
- Owner-confirmed indicator tier structure supersedes earlier planning notes: Low Tier contains exactly 15 common TradingView-style indicators; the exact 15-item selection is to be finalized before implementation. Mid Tier remains undecided until the owner supplies the preferred indicators. Exclusive Indicator Pro contains Footprint PRO 2GD, Heatmap, Liquidation Maps, and the full Volume Profile with detailed data/value presentation. Full Volume Profile is Exclusive, not Mid Tier.
- Any separate compact, movable-range Volume Profile chart tool remains a Tools feature and must not be confused with the full Exclusive Volume Profile indicator.
- Preserve the chart-layout invariant: normal candles and ordinary spacing remain unchanged while Footprint is OFF; only Footprint ON may activate the spaced-candle/cluster layout.
- Overall estimated progress remains 19.40%. No progress credit is assigned for the Footprint engine, visible 15-indicator Low Tier, tier navigation, full Volume Profile, Heatmap, Liquidation Maps, Android packaging, live provider delivery, or on-device verification until those deliverables are implemented and independently tested.
- Next engineering gate: safely persist and integrate the complete Footprint source modules, run its dedicated regression suite alongside existing frontend/backend tests, then implement the indicator-tier UI without disturbing the shared market-data foundation.

### 2026-11-04 — Firebase-authenticated WebSocket and per-instrument authorization

- Replaced the WebSocket route's shared static-token comparison with Firebase ID-token verification through the approved `FirebaseIdentityVerifier`. Verification runs in a worker thread; invalid credentials are rejected and unavailable identity verification fails closed.
- Each subscription now requires a canonical instrument UUID in addition to the exact provider series identity.
- Before snapshot/watermark registration, the backend resolves the current provider/dataset/publisher/instrument mapping, verifies the raw symbol and canonical UUID match, checks that the canonical instrument is active, and checks the verified Firebase principal's explicit SQLite entitlement. Missing or mismatched mapping, inactive instrument, or absent/revoked entitlement is denied by default.
- Active subscriptions recheck the mapping and entitlement every 60 seconds; revoked or changed access closes the connection.
- Added isolated SQLite test fixtures and regression coverage for Firebase authentication, exact-series subscription, deny-by-default entitlement behavior, and authenticated live-update delivery.
- GitHub Actions run #301 on commit `d1a7c9602e59477bcb1e7fc77da58348d9a981aa` passed frontend tests, frontend production build, backend tests (277 passed), and backend Docker image build. The documentation-only follow-up run is checked separately.
- The legacy `MARKET_DATA_WS_TOKEN` setting remains for compatibility but is no longer read by the WebSocket route.
- Remaining gates: frontend Firebase sign-in/session integration, frontend WebSocket client and reconnect/resnapshot logic, canonical identity population from verified provider definitions, token-expiry/re-authentication policy for long-lived connections, backend deployment, and real provider delivery.
- Overall progress: 19.60%. No visible indicator UI, Footprint, Heatmap, Liquidation Maps, full Volume Profile, or Android packaging credit is assigned.
- At this audit checkpoint, `phase-2/market-data-foundation` compared 311 commits ahead of `main` and 0 behind. `main` remains untouched.


### 2026-11-04 — Databento definition metadata capture groundwork

- Expanded `backend/app/databento_definitions.py` to retain authoritative definition fields needed by the upcoming registry synchronizer: exchange, asset/security type, settlement currency, unit-of-measure quantity and unit, contract multiplier fields, activation, security update action, display factor, lot-size metadata, and underlying.
- Null-padded ASCII text fields are normalized; numeric provider values remain unchanged in this low-level adapter so fixed-point scaling is applied exactly once by a typed domain layer.
- Added focused tests for provider metadata preservation, byte decoding, invalid non-ASCII text, and existing record-order behavior.
- Databento's documented schema identifies `unit_of_measure_qty` + `unit_of_measure` as contract-size metadata, `exchange` as the exchange identifier, and definitions as point-in-time records. The adapter now captures these fields but does not yet interpret lifecycle actions or write to SQLite.
- Existing atomic provider-event persistence primitives (`SQLiteProviderDefinitionEventRepository`) remain the intended transaction boundary. Canonical UUID assignment, authoritative metadata normalization, event ordering/action processing, and provider-to-registry synchronization are still pending.
- No overall progress increase: this is metadata-capture groundwork, not durable provider integration or live-feed verification. Overall progress remains 19.60%. GitHub Actions runs for the two code commits are in progress; no pass is claimed yet. `main` remains untouched.


### 2026-11-04 — Databento adapter CI correction

- The first adapter test run failed because the new byte fixtures contained escaped text rather than actual NUL/non-ASCII bytes; the two negative tests therefore did not exercise invalid byte input.
- Corrected the adapter's null-byte trimming and corrected the test fixtures to contain actual binary byte values. The correction is committed in `0cfc3eed15bad9e03a1291345d29efff73652e37` and `d56a39e0b8c911a38a7a3c86e56a2a929357c071`.
- The branch-head workflow run `41819590174` for `d56a39e0b8c911a38a7a3c86e56a2a929357c071` has passed frontend unit tests and the frontend production build. Backend dependency installation is still running; backend tests and Docker build are not yet verified.
- No overall progress increase: Databento provider definitions are not yet synchronized into the persistent canonical registry. Overall progress remains 19.60%. `main` remains untouched.


### 2026-11-04 — Databento definition lifecycle event processing

- Added `InstrumentCatalog.apply_definition_event` for Databento Add (`A`), Modify (`M`), and Delete (`D`) records. Delete records require only provider identity and event timestamp; they no longer depend on expiry metadata.
- The adapter now requires the provider lifecycle action and retains exact provider timestamps/integers.
- `ProviderManager.refresh_definitions` now applies historical definition events in stable ascending `ts_event` order instead of treating a point-in-time event stream as a flat complete snapshot.
- Added exclusive event-time closure to `InstrumentResolver`. Modify transitions close the prior mapping before opening the new one; Delete closes the active mapping. Existing tombstones prevent delayed older Add/Modify events from resurrecting deleted instruments.
- Added regression tests for Add/Modify/Delete ordering, Delete without expiration, stale resurrection prevention, resolver mapping boundaries, and provider refresh integration.
- GitHub Actions run `41820405604` on commit `5338c0df0265515606e8bf942f65b537672d92df` passed frontend unit tests, frontend production build, backend tests, and backend Docker image build.
- This is an in-memory lifecycle-processing milestone only. Canonical UUID assignment and atomic SQLite persistence of provider mappings + metadata revisions remain pending. The canonical model also needs a deliberate distinction between Databento `unit_of_measure_qty` (contract size) and Databento `contract_multiplier` (deliverable multiplier); no field is being overloaded.
- Overall project progress remains 19.60% because durable provider-to-registry synchronization and production verification are not complete. At this checkpoint the branch was 328 commits ahead of `main` and 0 behind. `main` remains untouched.

### 2026-11-04 — SQLite schema v5 foundation (implementation pending CI)

- Working branch only: `phase-2/market-data-foundation`; `main` remains untouched.
- Added schema v5 migration to separate dated-futures identity from the legacy `contract_multiplier` field. Futures identity now uses venue/product, expiry, and settlement currency; perpetuals/options retain their prior multiplier requirements.
- The v5 migration rebuilds the generated identity key and unique index transactionally. Duplicate identities exposed by the revised rule abort and roll back the migration; no UUIDs or histories are merged.
- Added an append-only `provider_definition_events` journal with explicit source ordering, exact payload hash, durable pending/applied/quarantined states, and foreign-key linkage for applied canonical IDs.
- Added `SQLiteProviderDefinitionJournal` for idempotent append, conflict detection, deterministic pending replay, and one-way processing-state transitions. Raw Databento fixed-point values are preserved as received.
- Added regression coverage for futures identity separation and journal durability, idempotency, conflict rejection, equal-timestamp source ordering, quarantine, and immutable payloads.
- This is persistence groundwork only. The journal is not yet connected to the live Databento session or the atomic provider mapping + metadata revision pipeline. No live market data, Footprint readiness, or latency claim is implied.
- Overall progress remains 19.60% until the new migrations and tests pass CI and the provider-to-registry synchronizer is integrated and verified.

### 2026-11-04 — strict Databento definition normalizer

- Added `backend/app/databento_definition_normalizer.py` and focused tests for dated futures definitions, UTC expiry conversion, required authoritative fields, Delete handling, and lossless provider-term preservation.
- Root symbol and venue must come from explicit provider fields; no ticker parsing is used to fill missing identity data.
- Settlement currency uses the provider's explicit settlement override when present and otherwise the provider currency field. Fixed-point source values remain raw with explicit scales; provider-native contract multiplier remains separate from unit-of-measure quantity.
- This adapter is not yet wired to the live provider lifecycle or SQLite synchronizer. Footprint source modules are not present in the current GitHub branch, so no Footprint integration or completion is claimed.
- Overall progress remains 19.60%; CI for the latest branch head and the complete synchronizer are still pending.


### 2026-11-04 — Durable Databento definition synchronization
- Added `backend/app/databento_definition_sync.py` to connect the append-only SQLite provider-definition journal, strict Databento normalizer, canonical instrument registry, atomic mapping/metadata event repository, in-memory catalog, and point-in-time resolver.
- Wired the synchronizer into `ProviderManager.refresh_definitions` and application construction using the same SQLite database as the canonical registry.
- Add/Modify events resolve or allocate a persistent canonical UUID, validate immutable identity, then commit provider mapping and metadata revision together. Delete events close the active mapping and matching metadata interval atomically.
- Journal records are marked applied only after the registry event succeeds. Invalid, stale, unsupported, or ambiguous events are quarantined with the original payload retained. Exact event replay is idempotent.
- Added resolver restoration from persisted canonical instruments and provider mappings so provider identity mapping can survive backend restarts.
- Added integration tests for Add → Modify → Delete point-in-time behavior, exact replay, pending-event recovery, resolver restoration, invalid-event quarantine, and equal-timestamp transition rejection.
- GitHub Actions run [#41827550928](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41827550928) passed frontend unit tests, frontend production build, backend tests, and backend container image build for the replay-hardened code at commit `3e3fcd715d31c00cd2884a7f5ce5510d83daa6ff`. The earlier integration checkpoint also passed in run #41826984399.
- Core synchronizer implementation: `329be1f7df926fadea6a56d24ef2fba502229cdd`; pending-page replay hardening and its regression test: `3e3fcd715d31c00cd2884a7f5ce5510d83daa6ff`. The documentation follow-up is committed separately. `main` was not modified.
- Limitations: provider source order is derived from stable record iteration within equal timestamps because the current adapter does not expose a universal sequence field. Multiple lifecycle transitions for the same provider instrument at the exact same event timestamp cannot form positive-length half-open intervals; later conflicting transitions are quarantined rather than reordered or silently collapsed. No live Databento delivery, scheduled refresh, coverage persistence, or deployment validation is claimed.


### 2026-11-04 — Durable OHLCV persistence and restart restoration

- Added `backend/app/ohlcv_store.py`, a SQLite OHLCV repository sharing the configured instrument-registry database without changing its schema `user_version`.
- Base provider bars are persisted before in-memory pipeline acceptance. Derived timeframe bars pass a persistence gate before the aggregator mutates the in-memory pipeline or broadcasts the update.
- The store preserves exact decimal strings, integer nanosecond event/receive/provider-out timestamps, sequence origin, bar origin, and completeness.
- Persistent identity matches the pipeline's bar identity: provider, dataset, publisher, instrument, series type, timeframe, and bucket start. A conflicting raw symbol for the same identity is rejected.
- Duplicate, stale, provider-precedence, and derived-completeness revision behavior mirrors the in-memory pipeline. Late bars older than a full retained series window are rejected as expired.
- Retention is bounded per exact provider series and timeframe. The local ingest-sequence high-water mark is stored separately so process restarts do not reset sequence ordering after older bars have been pruned.
- Application construction restores retained OHLCV bars into the in-memory pipeline before provider ingestion starts. HTTP snapshots therefore read restored bars immediately after restart.
- Added tests for exact decimal/nanosecond round-trip, revision semantics, retention, late-event expiry, shared-database schema compatibility, sequence high-water recovery, and API-level restart restoration.
- Validation: GitHub Actions run [#41829548364](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41829548364) passed the frontend unit suite (117 tests), frontend production build, backend suite (322 tests), and backend container image build at code commit `9e1f47b4a2a66b478465b1fc9df362462d1e9864`. Documentation follow-up changes are checked by their own branch-head workflow.
- Scope boundary: this does not yet persist coverage intervals, maintain a durable event log for WebSocket client replay, orchestrate historical gap detection/backfill, validate live Databento delivery, or prove production performance under sustained market load. Those remain explicit follow-up work. `main` remains untouched.


### 2026-11-04 — Durable coverage intervals and bounded gap recovery

- Added `backend/app/coverage_store.py` with SQLite-backed covered intervals and explicit gap intervals, sharing the existing instrument-registry database without changing its schema version.
- Successful historical query windows persist coverage and remove only the overlapping portion of prior gaps. Queue overflow persists an explicit gap even when no prior covered interval exists.
- Coverage and gap interval counts are bounded per scope; truncation counters survive restart. Failed persistence rolls back the in-memory tracker mutation.
- The application now constructs `SQLiteCoverageTracker`, so provider backfill coverage and ingestion overflow gaps survive backend process restart.
- Added `ProviderManager.recover_gaps(max_gaps=...)`: an explicit bounded operation that selects persisted gap scopes, requires an exact matching resolver mapping, clips requests to the mapping validity interval, splits requests by the configured maximum historical span, and reuses the existing bounded historical backfill path. Gaps without an active/historical mapping are skipped and retained; they are never silently marked recovered.
- Added tests for covered/gap restart restoration, partial gap refill, unscoped gaps, bounded gap retention, rollback on persistence failure, application restart restoration, and bounded historical recovery with and without an exact mapping.
- GitHub Actions run [#41831095189](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41831095189) passed frontend unit tests, frontend production build, backend tests, and backend container image build for code commit `7fccf693becdeb2002b181787625168660f9babe`. The total-span-budget code and regression test passed backend tests in run [#41832038444](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41832038444). Latest branch-head run [#41832124370](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41832124370) passed all frontend tests, frontend production build, backend tests, and backend container image build at documentation commit `89fd05cd36b0adf41d5607eea290958c833b0f56`.
- Scope boundary: gap recovery is an explicit backend service operation, not an automatic scheduler or public API. No live Databento session, production deployment, WebSocket durable outbox, or sustained-load performance validation is claimed. `main` remains at its pre-work head `e3841681bc69b73619058deaf939df82ae5116a1`.


### 2026-11-04 — WebSocket exact-symbol handoff hardening

- Verified the previously long-running workflow [#41832462822](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41832462822): it completed successfully for commit `93b722cd8a22609cd6697bd38540ff4e672d75b2`. Frontend unit tests, frontend production build, backend tests, and backend container build all passed. This confirms the durable coverage/gap-recovery checkpoint was not lost or left in a failed state.
- Audited the authenticated WebSocket snapshot-to-stream handoff and found a subtle identity mismatch: authorization compared a normalized raw symbol, while snapshot lookup and live fan-out used the unnormalized client string. A lowercase or whitespace-padded symbol could therefore pass authorization but receive an empty snapshot or no live updates.
- Canonicalized the raw symbol and canonical instrument ID once before both snapshot lookup and stream registration. Added an API-level regression test that subscribes with a whitespace-padded lowercase symbol, verifies the canonical snapshot, ingests another accepted bar, and receives the matching live update.
- Validation: workflow [#41841192415](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41841192415) completed successfully for code commit `2a188fdce7841148f12301eb7e8a7bba66811681`; frontend unit tests, frontend production build, backend tests, and backend container build all passed.
- This is stream identity hardening only. It does not claim a frontend WebSocket client, reconnect/replay, Firebase sign-in UI, live Databento delivery, or production deployment. `main` remains untouched.


### 2026-11-04 — Authenticated frontend OHLCV WebSocket transport

- Added `src/services/ohlcvWebSocketClient.ts`: derives WS/WSS from the configured backend origin, sends the caller-supplied Firebase ID token, waits for backend authorization status, subscribes to the exact canonical instrument and OHLCV series, validates the atomic snapshot, initializes the stream watermark, and accepts only validated next-sequence updates.
- Added `src/services/ohlcvWebSocketClient.test.ts` covering authentication/subscription/snapshot/update flow, sequence-gap rejection and socket closure, invalid backend URL rejection, and clean close behavior.
- Added `docs/OHLCV_WEBSOCKET_CLIENT.md` describing the handshake, exact-series validation, recovery boundary, and remaining integration work.
- GitHub Actions workflow [#41841139463](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41841139463) completed successfully: frontend unit tests, frontend production build, backend tests, and backend container image build all passed.
- At the 2026-11-05 branch-head audit, this earlier limitation was superseded: `CandlestickChart` now starts and stops `startOhlcvStreamSupervisor` for the selected catalog contract, obtains Firebase ID tokens through `AuthProvider`, and consumes validated snapshots/updates through `marketDataStore`. The supervisor requests a fresh token on reconnect and the WebSocket client rejects invalid handshakes and sequence gaps. This is code-level frontend integration, not proof of a deployed backend or live provider delivery.
- Remaining limitations: no deployed end-to-end environment, verified live Databento session, synchronized exchange clock, durable WebSocket event replay, or sustained-load production validation is claimed. The last formally weighted estimate is 19.60%; newly integrated work must be assigned milestone weight through a reconciled ledger before changing the overall percentage. `main` remains untouched.


### 2026-11-05 — Security baseline correction and 40% product checkpoint gate

- Corrected `docs/SECURITY_CONFIGURATION.md` to match the inspected implementation: `GET /v1/ohlcv` requires a verified Firebase Bearer identity and per-instrument entitlement checks; the authenticated WebSocket also verifies identity and instrument entitlement.
- Documented the remaining public endpoint classification decision for `/health`, `/v1/market-data/status`, and `/v1/instruments`.
- Recorded release follow-ups for HTTPS/WSS deployment verification, rate limiting, dependency/secret/container scanning, reproducible frontend dependency installation, and operational recovery review.
- Added a firm product-planning gate: before the overall project reaches 40%, prioritize foundation work only—security review, dependency hygiene, tests, performance, accessibility, Android responsiveness, architecture, error handling, and documentation. Major UI/feature expansion may begin at the 40% checkpoint only after the scoped blueprint is reviewed and approved by the owner.
- At the 40% checkpoint, begin a separate design and implementation phase for safe, non-transactional chart-learning features: chart presentation options, drawing/annotation tools (trend/horizontal/vertical lines, rectangles/zones, labels, Fibonacci as an educational measurement tool), undo/redo, persistence, and educational mathematical visualizations. Each feature still requires design review, implementation, tests, and owner acceptance.
- Scope boundary: no brokerage/order execution, buy/sell signals, or speculative order-flow/liquidation features are included. This gate is a planning requirement, not a claim that the future features are already implemented.
- Documentation-only update; weighted overall progress remains 19.60%. No application code changed. The exact branch-head CI run #42043081654 for commit `6a3a27cb127c0b20825a7cdc0224a6ebc9fdc320` subsequently completed successfully: frontend unit tests, frontend production build, backend tests, and backend container image build all passed. This verifies the configured checks for this documentation commit only; it is not a production-security certification. `main` remains untouched.


### 2026-11-05 — CME session-calendar architecture decision

- Added `docs/CME_SESSION_CALENDAR_DESIGN.md` as an accepted design contract for ES/NQ (CME Equity Index) and GC (COMEX Gold).
- Explicitly separated `UTC_LEGACY`, `UTC_FIXED_V1`, and `CME_SESSION_V1`; the design requires additive SQLite migration and policy/calendar-version-aware bar identity so legacy data is preserved and cannot collide with new session bars.
- Specified Chicago timezone/DST handling, Sunday reopen trading-date assignment, daily maintenance, product-specific official schedule provenance, special-session overrides, and fail-closed behavior when schedule data is unknown.
- Defined the intended aggregation contract: 1D from session-contained 1H children (not 4H), with 1W/1M/3M grouped by CME trading dates and no synthetic candles.
- Recorded required migration, rollback, DST, holiday, completeness, API, and intraday-regression tests.
- This is a documentation/design milestone only. No application code, database schema, calendar ingestion, or aggregation behavior changed. No live Databento delivery, real-time latency, raw tick/MBO, or production readiness is claimed.
- Weighted overall progress remains 19.60%; this design document does not justify a code-completion percentage increase. `main` remains untouched.


### 2026-11-05 — Authenticated frontend stream integration audit

- Branch-head source audit confirms `src/components/CandlestickChart.tsx` now starts `startOhlcvStreamSupervisor` when a selected catalog contract has a canonical instrument ID and the user is signed in.
- The chart obtains Firebase ID tokens from `AuthProvider`, handles connecting/authenticated/subscribed/reconnecting/stopped/error states, and stops the supervisor during effect cleanup.
- `src/services/ohlcvStreamSupervisor.ts` owns reconnect lifecycle, requests a fresh ID token for each connection, and bridges validated snapshots/updates into `marketDataStore`.
- `src/services/ohlcvWebSocketClient.ts` performs the authenticated snapshot-plus-watermark handshake, validates stream sequencing, and requires reconnection/resnapshot on sequence gaps.
- `CandlestickChart` consumes the shared store and applies validated snapshots or incremental updates. DEMO candles remain clearly distinguished and are not admitted into the backend market-data store.
- Branch-head CI run [#42051868901](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42051868901) passed frontend unit tests, frontend production build, backend tests, and backend container-image build on commit `551ae8da92175ca96d8a947fe35fcf782a698a87`.
- This verifies the configured automated checks only. It does not verify a deployed backend, Firebase production configuration, provider credentials/session, real provider delivery, exchange-synchronized timestamps, end-to-end latency, or sustained-load behavior.
- Progress accounting: the last formally weighted estimate remains 19.60%; the user recalls a 20.9% conversational checkpoint. A proposed eight-group 100%-weighted ledger is now recorded in docs/PROJECT_MILESTONE_LEDGER.md. Its weights and criterion scoring still require owner review; keep 19.60% and 20.90% as historical references until that review and scoring are complete.
- `main` remains at `e3841681bc69b73619058deaf939df82ae5116a1`; all work remains on `phase-2/market-data-foundation`.


### 2026-11-05 — Progress record and 40% expansion gate
- Added `docs/PROJECT_PROGRESS.md` as the dedicated progress-accounting record.
- Preserved the 19.60% historical formal estimate and owner-confirmed 20.30% → 20.90% conversational sequence. Added the proposed weighted ledger; no new current percentage is claimed.
- Documented why the values cannot yet be reconciled: no consolidated 100%-weighted milestone ledger with non-duplicated acceptance criteria and evidence links exists.
- Updated the major UI/feature expansion gate from 50% to 40%, following the owner's clarification. A scoped blueprint and owner review remain required at that gate.
- Corrected stale frontend WebSocket integration wording and recorded the exact successful CI run for branch HEAD `8ae99f5c5a11cdfb8b5d52acc1455a47259f194b`.
- This is a documentation/accounting update only; no application runtime code changed and no new overall percentage is claimed.


### 2026-11-06 — CME bucket-policy and SQLite migration audit

- Audited the accepted CME session-calendar ADR against the current OHLCV model, SQLite store, and shared instrument registry.
- Found an ambiguity: the ADR distinguished vendor UTC daily bars from CME-session daily bars in prose but did not assign vendor daily bars their own bucket-policy identifier. Added `UTC_PROVIDER_DAILY_V1` so source-defined UTC daily bars cannot collide with or be relabeled as CME-session bars.
- Corrected the migration plan: the OHLCV primary key must be rebuilt transactionally because SQLite cannot add policy identity columns to an existing primary key with a simple additive column migration. The OHLCV store must use its own schema-version table and must not change the shared instrument registry's `PRAGMA user_version`.
- Added explicit acceptance checks for exact legacy-row preservation, rollback, policy-version coexistence, and registry schema-version isolation.
- Documentation-only checkpoint. No runtime code, stored data, provider configuration, calendar behavior, or aggregation policy changed. The next implementation step remains the isolated OHLCV schema migration; calendar aggregation stays disabled until the migration and tests pass.
- Branch base audited: `ca2eca02b857a3d955b4aefbda167efa1db7909c`. The prior provider LIVE-state regression fix is commit `ca2eca02b857a3d955b4aefbda167efa1db7909c`; GitHub Actions run #486 passed the configured frontend and backend checks. This does not verify live provider delivery, real-time latency, or production deployment.
- No new overall progress percentage is assigned; the progress ledger still requires reconciliation. `main` remains untouched.


### 2026-11-06 — Transactional OHLCV policy-key migration

- Implemented an independent ohlcv_schema_meta version table (schema version 2); PRAGMA user_version remains owned by the shared instrument registry and is not changed.
- Added bucket_policy, calendar_id, and calendar_version to the durable OHLCV primary key and series index. The current OhlcvBar contract writes only UTC_LEGACY; policy-aware model and aggregation support remain a later stage.
- Legacy-table migration runs inside BEGIN IMMEDIATE / COMMIT, copies every legacy OHLCV field exactly, assigns UTC_LEGACY with empty-string calendar sentinels, and drops the old table only after the copy succeeds. Exceptions roll the transaction back.
- Used empty strings rather than SQL NULL for no-calendar identity in SQLite: nullable composite-key members do not provide the intended uniqueness guarantee in an ordinary rowid table. API DTOs may translate the sentinel to null in a later contract change.
- Added regression coverage for exact legacy-row restoration, policy-key coexistence, migration idempotency, rejection of unknown future schema versions, and isolation of policy-aware rows from the legacy OhlcvBar read path.
- This migration does not enable CME session aggregation, change provider configuration, or establish live feed delivery. Full end-to-end live 1S and every-indicator support remain unverified.
- No overall progress increase is assigned until branch-head CI and acceptance criteria pass. main remains untouched.

### 2026-11-06 — OHLCV bucket identity transport audit

- Confirmed branch-head CI run [#499](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42215355212) passed all configured checks on `157a6e3ecd2eeeb8dc4e9e45b6b406399f786b66`; Vercel deployment status for the same commit is success.
- Audited REST snapshots, WebSocket snapshot bars, stream update series metadata, stream-hub subscription identity, frontend protocol validation, sequence guard, supervisor identity checks, and shared-store identity checks. Bucket policy/calendar identity is carried in each snapshot bar and update series and is part of backend fan-out and frontend exact-series matching.
- Confirmed the currently enabled policies are `UTC_LEGACY` and `UTC_FIXED_V1`. Calendar identifiers remain rejected; CME session calendar aggregation remains disabled pending authoritative calendar and DST/holiday/early-close validation.
- Corrected backend README statements that incorrectly described the frontend as HTTP-only and OHLCV/coverage persistence as entirely in-memory. The frontend stream path is code-integrated, but deployed backend/provider end-to-end delivery, live freshness, durable WebSocket replay, and sustained-load behavior remain unverified.
- Added explicit bucket identity documentation to the WebSocket subscription example and REST query contract.
- No runtime code changed in this documentation checkpoint. No new overall progress percentage is assigned; the milestone ledger remains unreconciled. All changes remain on `phase-2/market-data-foundation`; `main` remains untouched.


### 2026-11-08 — Stage 1 CI warning remediation and deployment-provider limit

- Verified CI run #779 (run ID 42450511539) completed successfully on commit `8341328c39df5649fd53e7bd9abbf40ddf132c28`. Its configured frontend checks, backend checks (517 passed), backend image build, container smoke checks, Redis guard, non-root UID/GID and volume ownership, SQLite integrity/restart persistence, and Trivy HIGH/CRITICAL gate passed.
- Inspected the pytest warning rather than suppressing it: FastAPI 0.162.2 / Starlette 1.10.0 emitted `StarletteDeprecationWarning` because the TestClient compatibility path uses `httpx` and recommends `httpx2`. It did not fail tests. This dependency-compatibility warning remains open for a deliberate compatibility evaluation; it is not marked resolved.
- Identified the GitHub Actions Node.js 20 deprecation warning as coming from the pinned `actions/upload-artifact` v4 action. Updated only that workflow reference to official `actions/upload-artifact` v7.0.2, pinned to immutable commit SHA `cf430e030ddbb5b0abf93d22962f4752f3646cd9`. The v7.0.2 action metadata declares `node24`.
- The action update is commit `37625c8dd01b274b0520436a80677078bb543e81` on `phase-2/market-data-foundation`. CI run #780 (42450752893) and CodeQL run #138 (42450752885) were triggered for this exact commit and were still in progress at the time of this record; do not treat them as passed until completed.
- Vercel status for commit `37625c8dd01b274b0520436a80677078bb543e81` reported failure with provider target indicating `build-rate-limit`. This is recorded as a deployment-provider/account build limit, not misreported as a source-code build failure. No paid-plan change or quota bypass was attempted.
- CI #779's Trivy JSON artifact was retained by GitHub as artifact ID `13605605903`; the gate passed, but this entry does not claim a full manual review of every report finding.
- Scope: one workflow action reference changed; no application source, dependencies, runtime behavior, database schema, or user-facing features changed. Overall progress remains 20.90%; Stage 1 remains 75% provisional. No acceptance-criteria progress increase is claimed from this CI/workflow maintenance alone. `main` remains at `e3841681bc69b73619058deaf939df82ae5116a1`.


### 2026-11-08 — Stage 1 CI validation closeout — CI #782

- Re-verified the exact branch HEAD `7fd77872f99d9c2890e76b205a36e11adc9e01ee` on `phase-2/market-data-foundation`; the commit changes only `backend/requirements-dev.txt`, adding `httpx2>=2.16,<3`. `main` remains untouched.
- CI run [#782](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42451060048) completed with conclusion `success` for that exact HEAD. Frontend: 25 test files and 190 tests passed; production build and bundle secret scan passed. Backend: all 517 pytest tests passed; dependency audit passed. Docker image build, Redis/shared-guard and persistent-volume smoke test, SQLite integrity/restart smoke test, Trivy scan, report export, and artifact upload all completed successfully.
- Inspected the complete backend test log after adding `httpx2 2.16.0`: no `StarletteDeprecationWarning` or pytest warning summary was emitted. The earlier Starlette TestClient deprecation observed on CI #779 is therefore resolved for the current CI test environment; this is not a blanket claim about every consumer environment.
- Verified the pinned `actions/upload-artifact` v7.0.2 immutable revision was used in CI #782. The earlier Node.js 20 deprecation warning did not recur in the inspected run log.
- Downloaded and manually inspected Trivy artifact [13605796314](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42451060048/artifacts/13605796314), SHA-256 `23a2ab3b710c05c88e79f409000f61cbfa5bd75cfe00677174215e02a09c4fe5`. The report is schema 2 and covers the exact CI image `dezzta-chart-backend:ci`, digest `sha256:f611543e1fb633304fcc853a11f4c04cb4c806ea7540b10d1edf7d687c88f3e8`, Alpine 3.24.4 and Python package targets. It reports zero vulnerabilities in the scanned OS/Python package targets and no secret findings. This finding is scoped to that built image and the scanners/configuration used in this CI run; it is not a production deployment certification.
- CodeQL run [#140](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42451059974) completed successfully for both Python and JavaScript/TypeScript on the same HEAD.
- Remaining warnings are kept visible: Vite emitted a 534.95 kB minified JavaScript bundle warning (151.61 kB gzip) above its 500 kB threshold; Redis emitted the host-level `vm.overcommit_memory` warning in the CI service container; Docker image build emitted pip's root-install warning during image construction. These are non-blocking warnings, not test failures. The Vite bundle needs measured code-splitting analysis; the Redis sysctl is controlled by the hosted runner; the pip warning should not be hidden by a warning-suppression flag.
- Vercel's commit status still reports `failure` with provider target `build-rate-limit`. This is recorded as a deployment-provider/account quota limitation, not a source-code CI failure. No quota bypass or paid-plan change was attempted.
- Scope: dependency-test compatibility change plus this evidence record; no application runtime source, database schema, trading functionality, or UI behavior changed. Overall progress remains 20.90% as the owner-confirmed historical checkpoint; Stage 1 remains 75% provisional. No progress increase is awarded for dependency maintenance or passing CI alone. The remaining Stage 1 gates (real React DOM lifecycle runtime tests, real Firebase signed-token E2E, and production infrastructure/backup/restore verification with authorized adult owner involvement) remain open. `main` remains at `e3841681bc69b73619058deaf939df82ae5116a1`.


### 2026-11-09 — Stage 1 backup hardening and exact-HEAD validation — CI #794

- Supersedes earlier historical statements in this file that React DOM lifecycle integration tests were still missing: `src/auth/AuthProvider.dom.test.tsx` is present and the current CI run includes the seven DOM integration tests.
- Hardened `backend/app/sqlite_backup.py`: on POSIX, failure to apply owner-only mode `0600` now aborts publication instead of being silently ignored. Added regression tests for successful `0600` publication and fail-closed behavior that preserves the previous backup and removes the temporary file.
- Exact branch HEAD: `7b6fa39ab0862e8ed8e436d95f64ff2207a78456` on `phase-2/market-data-foundation`.
- Automated Tests [#794](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42636775435) completed successfully on that exact HEAD. Frontend: 26 test files / 197 tests, `npm ci`, npm audit, production build, bundle-secret scanner tests, and production bundle scan passed. Backend: 519 pytest tests passed, pip-audit reported no known vulnerabilities, Docker build and isolated Redis/persistent-volume/SQLite restart smoke tests passed, and Trivy report export/upload completed.
- The two new backup permission regression tests both passed in the exact-HEAD backend run. CodeQL [#152](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42636775603) completed successfully for Python and JavaScript/TypeScript on the same HEAD. Vercel status is success.
- Manually inspected Trivy artifact [13683362475](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42636775435/artifacts/13683362475): the report covers the CI image `dezzta-chart-backend:ci`, Alpine 3.24.4 and Python package targets; both targets report zero vulnerabilities in the configured OS/library scan. This is not a complete all-severity, misconfiguration, secret, or production-environment certification.
- Remaining Stage 1 production gates are unchanged: real Firebase signed-token E2E; actual Fly Volume permissions/restart; encrypted off-host backup, retention and restore drill; managed Redis TLS/private networking/failover; deployed HTTPS/WSS and Android/web smoke; production monitoring and fault recovery. CI Redis and volume smoke tests do not substitute for those production checks.
- Stage 1 remains **75.00% provisional** under the historical equal-weight method. No percentage increase is awarded from test-count growth or CI success alone. Scoring criteria remain subject to owner approval.
- No production credentials, resources, deployment configuration, database schema, or application runtime behavior were changed. `main` remains at `e3841681bc69b73619058deaf939df82ae5116a1`.


### 2026-11-09 — Stage 1 follow-up audit, CI #796 complete

- Re-verified active branch `phase-2/market-data-foundation`; source HEAD for this audit is `855260b474c686e97b2ae2a744c77540a00c0f94`. `main` remains untouched at `e3841681bc69b73619058deaf939df82ae5116a1`; branch compare reports 804 commits ahead and 0 behind.
- Automated Tests [#796](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42637776798) completed successfully on exact HEAD. All 25 job steps, including cleanup, concluded success. Frontend: 26 test files passed; dependency audit, production build, bundle-secret scanner tests and production bundle scan passed. Backend: 519 pytest tests passed; pip-audit reported no known vulnerabilities. Docker build, isolated Redis shared-guard smoke, non-root UID/GID and persistent-volume ownership, SQLite integrity/restart persistence, and rate-limit rejection all passed.
- CodeQL [#154](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42637776819) completed successfully for Python and JavaScript/TypeScript. Vercel status for the exact HEAD was success.
- Downloaded and inspected Trivy artifact [13682739863](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42637776798/artifacts/13682739863). It is a JSON report for `dezzta-chart-backend:ci`; configured OS (Alpine 3.24.4) and Python package targets each contain zero reported vulnerabilities at the configured HIGH/CRITICAL scan threshold. This is scoped CI-image evidence, not a full production security certification.
- Additional authentication integration audit: `src/App.tsx` does not mount the existing `AuthPanel`, so the current app does not expose the sign-in UI. `docs/AUTH_PROVIDER_EVALUATION.md` records the approved architecture direction of managed Firebase identity plus a short-lived, narrowly scoped WebSocket ticket, but ticket issuance/signing-key lifecycle and its end-to-end flow are not implemented. The existing backend verifier unit tests use injected fake claims/Admin SDK; no real Firebase project signed-token E2E has run. Keep this in the Firebase production acceptance gate; do not describe the current auth prototype as a complete end-user production login flow.
- Production gates remain open: (1) real Firebase valid/expired/revoked/wrong-project E2E plus approved visible sign-in and scoped-ticket flow; (2) actual Fly Volume ownership/restart verification; (3) encrypted off-host backup, retention and restore drill; (4) managed Redis TLS/private networking/failover; (5) deployed HTTPS/WSS and Android/web smoke; (6) production monitoring and fault/recovery verification.
- No production Fly app/Machine/volume, managed Redis, DNS, production credentials, billing resources, or live provider feed were provisioned or modified. These gates require authorized project-owner/admin operation in the appropriate consoles/secret manager; never transfer credentials through chat.
- Stage 1 remains **75.00% provisional** under the historical equal-weight ten-group method. CI completion closes CI evidence only; it does not close the six production gates or authorize a percentage increase. Scoring acceptance criteria still require owner approval.


### 2026-11-09 — Stage 1 exact-HEAD follow-up, CI #799 and CodeQL #157

- Exact audited branch HEAD: `7ce27502e1ef14ca65da79f366272778836ffe6d` on `phase-2/market-data-foundation`. The commit corrects the backend WebSocket README example to describe the current Firebase ID-token prototype and explicitly states that the approved short-lived scoped-ticket exchange and real-provider E2E are not implemented.
- Automated Tests [#799](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42639532618) completed successfully on this exact HEAD. The Test and Build job completed all 39 steps, including cleanup. Frontend install/audit/tests/build/bundle-secret scans and backend install/519-test suite/dependency audit/container build/Redis and persistent-volume smoke/Trivy report export and upload all passed.
- CodeQL [#157](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42639533040) completed successfully for Python and JavaScript/TypeScript on the same exact HEAD. Vercel status for the same commit is success.
- Repository open-item audit found no open pull requests or open issues at the time of review. The active branch remains `phase-2/market-data-foundation`.
- This was a documentation-only correction plus CI evidence recording; no production configuration, credentials, runtime behavior, or infrastructure changed. CI and CodeQL success do not close production acceptance gates.
- Six production gates remain open: authorized Firebase signed-token E2E plus visible sign-in and scoped WebSocket-ticket lifecycle; actual Fly Volume permission/restart; encrypted off-host backup/retention/restore; managed Redis TLS/private networking/failover; deployed HTTPS/WSS and Android/web smoke; production monitoring/fault recovery.
- Stage 1 remains **75.00% provisional** under the historical equal-weight method. No percentage increase is assigned from documentation or CI success alone; owner approval of scoring acceptance criteria remains required. `main` remains untouched.


### 2026-11-10 — Stage 1 yellow-gate follow-up: auth boundary and production configuration audit

- Continued only on `phase-2/market-data-foundation`; protected `main` was not used as a write target.
- Added ten explicit Firebase auth fail-closed action scenarios in `src/auth/AuthProvider.test.tsx` (commit `27314b5ba865fd2d58c10cfe443bca5ed182da82`), then made the action-table typing explicit (commit `4fd3075a9e907f88d6532cf955315708e94f9d8d`). These are source-level regression tests; do not claim they passed until the exact-head CI run completes.
- Audited production startup guards: production requires both `REDIS_URL` and `FIREBASE_PROJECT_ID`; production Redis must use `rediss://`; production CORS accepts HTTPS origins only; wildcard and non-origin CORS values are rejected. These guards are present in `backend/app/config.py` and already have baseline coverage in `backend/tests/test_config_security.py`. No redundant duplicate test file is retained.
- Audited WebSocket origin enforcement in `backend/app/main.py`: a supplied Origin must exactly match the configured allowlist; mismatches are rejected before acceptance. Existing API tests cover attacker origins, an empty allowlist, and non-browser clients without an Origin header.
- Audited shared-guard behavior: Redis is checked during application startup; HTTP rate limiting fails closed on Redis errors; WebSocket admission/lease refresh also fails closed. CI's isolated Redis test is not evidence of managed-production Redis TLS, private networking, or failover.
- Audited backup behavior: `backend/app/sqlite_backup.py` creates a consistent local SQLite snapshot, checks integrity, applies owner-only POSIX permissions, and atomically publishes it. The helper explicitly does not encrypt or upload backups. Encrypted off-host retention and a real restore drill remain open.
- Audited `backend/fly.toml.example` and `docs/BACKEND_DEPLOYMENT.md`: they are deployment templates/instructions, not evidence that a Fly app, persistent volume, or managed Redis has been provisioned and verified. Actual Fly volume ownership/restart, production HTTPS/WSS client smoke, production Firebase valid/expired/revoked/wrong-project E2E, and monitoring/incident alert delivery remain external acceptance gates.
- Vercel reported `success` for commit `2bcd038edbf3115af2a8776868fc5eb2c439a288` at the time of this audit. This verifies the frontend deployment status only. No exact-head GitHub Actions test result was available from the status evidence retrieved in this audit.
- Stage 1 remains **75.00% provisional**. No percentage increase is assigned: production acceptance gates and the owner-approved scoring criteria remain open.


## Superseding status reconciliation — 2026-11-13

This section supersedes older status summaries in this file where they conflict with the current detailed acceptance records. Historical entries are retained as history, not current truth.

- Active work branch: `phase-2/market-data-foundation`; protected `main` remains the baseline and is not a work target.
- Latest audited branch HEAD at this reconciliation: `4ab240cefc0f1fbc7ccecaf92d00095ebb01de60`. This HEAD contains documentation-only APK audit updates; no application runtime code was changed.
- Stage 1 accounting: **30/40 = 75.00% provisional**, not production accepted. The ten remaining criteria are external/operational verification gates described in `docs/STAGE_1_ACCEPTANCE_MATRIX.md` and the zero-cost dispositions in `docs/STAGE_1_ZERO_COST_GATE_PLAN.md`. Older statements in this file referring to six remaining production gates are superseded by the current 40-criterion matrix and its ten open external gates.
- Overall project progress: **20.9% remains a historical owner-confirmed conversational checkpoint**. A fresh weighted overall calculation is not established; do not present 20.9% as a newly recalculated current percentage.
- ZERO MONEY remains mandatory. No paid host, market-data provider, managed Redis, Firebase billing upgrade, domain, CDN, monitoring, runner, or trial may be activated. Gates that cannot be satisfied on existing owner-controlled resources remain constrained/deferred; security controls must not be weakened to force closure.
- The Android APK workflow run [#43442780935](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43442780935) successfully produced the 4.23 MB debug APK. The owner confirms installing the matching-size APK. Static inspection recorded in `docs/PROJECT_PROGRESS.md` confirms package `com.dezzta.chart`, Android Debug signing identity, `debuggable=true`, and `allowBackup=true`. The owner's antivirus warning and clean manual scan are both reports, not a conclusive malware verdict. The exact scanner name/detection label is still unknown. This artifact is a debug/test build, not a production release.
- Indicator state is fully documented in `docs/INDICATOR_DATA_ARCHITECTURE.md`: SMA/EMA/RSI/MACD/Bollinger calculation foundations are tested but not wired to visible chart controls/panes/overlays; the shared indicator hook has no visible controls; Footprint is SIMULATED educational aggregation only; Heatmap and Liquidation Maps are unimplemented. No indicator progress is awarded for APK build, installation, or static security review.
- Latest documentation commit Vercel statuses: `3e5cf784c8ad75dd7c0a93973d6a49e8fc0a068e` and `4ab240cefc0f1fbc7ccecaf92d00095ebb01de60` both report Vercel success. This is not a new full CI/CodeQL run, and must not be described as one.
- No application source, dependency manifest, production secret, provider configuration, paid service, or `main` branch was changed by this reconciliation.


## Latest Stage 1 blocker audit — 2026-11-13

- Audit starting HEAD before this blocker-documentation pass: `f82d1f8c38c7d0e70ea3fa75d40907d9260fcca6`. Follow-up documentation-only commits: status `ff848589591c65c4eaf48100fb2903bdfcbef467` and progress `88d2e08fef17e0ab87626c8816c529965f358b19`; no application runtime source changed.
- Vercel status on this exact HEAD: **success**.
- No Automated Tests or CodeQL status is attached to this exact documentation HEAD. The latest recorded full source CI/CodeQL evidence remains the prior exact source checkpoint `f7728136a480925bca11feb51b56f3b59b67bbf6`; comparison shows the commits since that checkpoint changed documentation and one Android workflow comment only, not application source. Do not call the current HEAD a newly CI/CodeQL-verified commit.
- Stage 1 remains **30/40 = 75.00% provisional**. The ten open criteria are exactly **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. All require real owner-controlled operational evidence; local CI, docs, APK build, or an isolated test cannot substitute.
- The ZERO MONEY policy forbids purchasing or activating hosting, managed Redis, paid Firebase, market-data feeds, backup storage, monitoring, domains/CDN, or paid alerts. Any criterion that cannot be safely exercised on existing owner-controlled resources remains constrained/deferred rather than waived or misrepresented.
- The Termux Google Play repository/keyring mismatch remains unresolved: the configured source offers `python-cryptography 48.0.1-1`, below the backend's `cryptography>=50,<51`; the upstream repository is rejected with `NO_PUBKEY 5A897D96E57CF20C`. Preserve the working repository and do not bypass APT signature verification, lower the dependency, or alter AES-GCM/PBKDF2.
- Indicator acceptance is unchanged and remains fully detailed in `docs/INDICATOR_DATA_ARCHITECTURE.md`. No indicator completion credit is assigned for this audit.


## Owner environment correction — single-phone constraint (2026-11-13)

The owner has already stated that the only available device is one Infinix GT20 running Android 15; there is no second phone, PC, or laptop. This is a confirmed constraint, not an unanswered question. Do not ask again or suggest purchasing hardware.

The previous "existing owner-controlled host/second device" candidate is not available. The phone-only feasibility and gate-by-gate disposition are now recorded in docs/STAGE_1_ZERO_COST_GATE_PLAN.md and docs/STAGE_1_ACCEPTANCE_MATRIX.md.

- Criterion 30 (SQLite restore to a fresh local database) is the nearest actionable same-device target; existing SQLite helper/device smoke and CI application-record tests are useful but still need a consolidated owner-device application-record restore report.
- Criterion 31 (encrypted off-host recovery) cannot be demonstrated with only one device and no verified existing off-host destination; the Termux Google Play cryptography package/keyring mismatch remains an additional blocker.
- Local CI/loopback/on-device tests can improve confidence for other gates but cannot be relabelled as production host, public HTTPS/WSS, persistent-volume, independent monitoring, or external alert-delivery evidence.
- Current Stage 1 remains 30/40 = 75.00% provisional; no percentage changes. A 40/40 production result is not honestly achievable with the currently verified resources. A phone-only demo-stage scope change would require explicit owner approval and would be a different acceptance definition.

Do not repeat the earlier request for a PC, laptop, or second phone. Do not buy or enable paid infrastructure. Keep the full indicator tracker in docs/INDICATOR_DATA_ARCHITECTURE.md; its acceptance status is unchanged.


## Criterion 8 — repository security audit checkpoint (2026-11-13)

- Full reachable Git history scanned by Gitleaks v8.30.1: 1,133 commits, ~2.57 MB, no leaks found.
- Integrated CI #43451610297 and CodeQL #43451610192 passed on implementation/workflow commit `efdf9a9ecfa68647586cd89f819e76469e11d3df`.
- Criterion 8 remains open because production host secret injection, deployed runtime/build-host logs, and GitHub native secret-scanning/push-protection settings plus alert inventory are not verified.
- No change to Stage 1 (30/40 = 75% provisional), overall project progress (20.9% historical), or indicator acceptance. The complete indicator matrix remains in `docs/INDICATOR_DATA_ARCHITECTURE.md`.
 
## Latest Gate 10 exact-head verification — 2026-11-14

- Verified source/test HEAD: `462bca4342d6cb585b6b389ae5996020c4c47dd3`.
- Automated Tests #1149: **SUCCESS** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43594614075.
- CodeQL #507: **SUCCESS** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43594614165.
- Full Git History Secret Audit #88: **SUCCESS** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43594614104.
- Secret scan remediation: investigated the redacted Gitleaks finding and fixed the narrow metadata false-positive allowlist. An intermediate TOML syntax failure was corrected; final exact-head audit passed.
- Stage 1 remains 30/40 provisional criteria = 300/400 ticks = 75% provisional. External criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain OPEN; no external tick was awarded.
- Stages 2–6 remain NOT SCORED. Overall 20.90% remains a historical owner-confirmed checkpoint, not a fresh weighted calculation.
- No Termux package/repository/keyring changes, crypto downgrade, production secret, paid service, or APK release occurred.


## Gate 38 internal metrics cardinality correction — 2026-11-17

- Fixed an off-by-one in `backend/app/observability.py`: the overflow bucket is now included inside the configured maximum of 127 total metric route series, instead of allowing 127 named series plus an additional overflow series.
- Added `backend/tests/test_observability.py` with three regression tests for the exact 127-series ceiling, label sanitization/invalid values, and detached snapshots.
- Exact-head backend test log confirms **999 passed in 26.96s**, including all three new tests. Automated Tests & Build [44098987046](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44098987046), CodeQL [44098987058](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44098987058), and Full Git History Secret Audit [44098987124](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44098987124) all passed on `ee9a68da14001839a1aebc03082187b4b34162ef`.
- This is repository-side hardening only. Gate 38 remains OPEN until bounded metrics are integrated with durable aggregation/retention, protected host operations, and a verified dashboard/incident workflow. No Stage 1 tick is awarded.


## Current Vercel preview read-back — 2026-11-17

- FastAPI POC project `dezzta-chart-ws-poc`: latest deployment `dpl_GRGdGjm4W9dYuAD9FEFn84rdcHtm`, READY, https://dezzta-chart-ws-fyyd5o3ui-deszztagd377-pixel.vercel.app. SSO protection is enabled for **all** deployment targets.
- Main Vite frontend project `dezzta-chart`: latest deployment `dpl_CXHJ9UXKfK4jVQVsLzNumSkbfdex`, READY, https://dezzta-chart-la5w28fic-deszztagd377-pixel.vercel.app. SSO protection is enabled for all deployment targets except custom domains.
- Both latest deployments point to documentation-only commit `1dbc5a544c294fc74a441158af65ed6d1cb523d0`; both project read-backs report `live=false`. These are protected previews, not production releases or proof of live market-data delivery.
- No Vercel protection setting, billing plan, custom domain, secret, or production target was changed.


## Gate 36 deployment-context evidence — 2026-11-17

- Vercel team context identifies the account as Hobby and the isolated FastAPI project as `dezzta-chart-ws-poc`.
- Latest observed deployment: `dpl_39dRJ6Ki9gU1PrXcN8YU4kQ7zCzW`, READY, source `b789e229290290c91143077449a83ec94098162f`.
- SSO protection: enabled for all deployment targets.
- Build log confirms Python 3.12 from `poc/vercel_ws/.python-version` and requirements from `poc/vercel_ws/requirements.txt`, confirming the expected POC build subdirectory.
- Project settings response omits effective Fluid Compute. Source `fluid: true` is not substituted for independent runtime read-back. Gate 36 remains OPEN.


---

## Batch 62J-225 — exact-head reconciliation and current production blockers (24 November 2026)

**Audited branch:** `phase-2/market-data-foundation`  
**Pre-documentation HEAD:** `2d56e8c079801bcbaa1c47963844c31736476589`  
**Exact-HEAD CI:** 4/4 configured workflows terminal SUCCESS  
**Scope:** documentation reconciliation only; no runtime source, tests, dependencies, secrets, deployment, or paid services changed.

### Exact-HEAD workflow evidence

All four workflow runs report the exact SHA `2d56e8c079801bcbaa1c47963844c31736476589` and terminal `completed / success`:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | [45417603350](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45417603350) | 🟩 SUCCESS |
| CodeQL Security Analysis | [45417602448](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45417602448) | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | [45417606609](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45417606609) | 🟩 SUCCESS |
| Full Git History Secret Audit | [45417602216](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45417602216) | 🟩 SUCCESS |

No workflow was queued or in progress in the exact-SHA query. This is GitHub CI evidence, not public production WSS, live market-data, owner-host or Android physical-device acceptance.

### WebSocket / Gate 25 / infrastructure status

- 🟩 Repository foundations: protocol validation, ticket/authentication enforcement, reconnect/sequence/replay and Redis replica/recovery logic; Batch 223 shared-series owner consistency has exact-head CI acceptance.
- 🟩 Gate 25 repository-side checks: owner-pinned Ed25519 allow-list, persisted receipt signature re-verification, identity/key binding, durable checkpoint digest comparison and fail-closed validation before Redis client construction.
- 🟥 Gate 25 external acceptance remains OPEN: owner private-key custody, authenticated owner-host callback transport, actual signed snapshot transfer, retrieval of each gateway's persisted immutable receipt, restart-time re-verification and multi-gateway durable high-water acknowledgement.
- 🟥 Gate 36 remains OPEN: public HTTPS/WSS and reverse proxy/TLS, independent runtime/Fluid Compute read-back, Android-native WSS lifecycle and production multi-instance fan-out.
- 🟥 Firebase production sign-in/revocation/entitlement E2E remains OPEN.
- 🟥 Redis destructive retention remains BLOCKED until gateway inventory/retirement, pending-entry policy, per-gateway durable floor acknowledgements, separate retention authority and crash-safe trim/reconcile are accepted. XTRIM/XDEL and consumer-group destruction remain unauthorized.
- No external host credentials, private keys, production endpoint or second device were available to verify. Do not convert repository tests or synthetic preview evidence into production acceptance.

### Indicator ledger — no score inflation

| Indicator | Verified foundation | Visible chart integration | Status |
|---|---|---|---|
| SMA20 | 20-close mean; first valid index 19 | Not integrated | 🟨 Foundation |
| EMA20 | SMA-seeded; alpha 2/21; first valid index 19 | Not integrated | 🟨 Foundation |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | No 0–100 pane/30–70 guides | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; signal EMA9; histogram identity; MACD index 25, signal/histogram 33 | No pane/lines/histogram | 🟨 Foundation |
| Bollinger20,2 | Population standard deviation; mean ± 2σ; first valid index 19 | No three-line overlay/fill | 🟨 Foundation |
| Shared Indicator Hook | Exact keyed immutable snapshot, shared cache, trust gating, stale-output clearing | Not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Owner references recorded; renderer gated | 🟧 Gated |
| Volume Profile / Complete VP / movable-range VP tool | No complete production implementation verified | Not integrated | 🟥 Open |
| Heatmap | No accepted depth/liquidity engine and renderer | Not integrated; owner reference/data contract required | 🟥 Open |
| Liquidation Maps | No accepted methodology/provenance/renderer | Not integrated | 🟥 Open |

Focused test inventory remains 17 calculation-engine + 7 shared-hook = 24 named tests; it is not a completion percentage. Footprint OFF must preserve ordinary candle spacing; explicit ON alone enables the spaced-cluster layout. Indicator visual expansion remains behind the official Stage 4 gate, scoped blueprint and owner review. Aggregate indicator completion remains **NOT SCORED** because no approved denominator/weights exist.

### Official progress accounting

- Stage 1: **30/40 criteria = 300/400 ticks = 75% provisional**; previously recorded, not independently re-audited in this documentation cycle.
- Gate 10: **0/10 formally closed**; external acceptance remains OPEN.
- Stage 2: active engineering, denominator not approved — 🟦 NOT SCORED.
- Stages 3–6: ⬜ NOT SCORED.
- Overall project: ⚪ NOT SCORED; no approved weighted denominator.
- Aggregate indicators: ⚪ NOT SCORED.
- IP3S/significant progress: ⚪ NOT SCORED; no approved scoring formula applied.

Do not extrapolate Stage 1's provisional 75% to total project completion. No Stage 1 ticks or indicator credit are awarded by this documentation reconciliation.

### Execution order retained

1. Continue only source-backed repository work that does not cross the owner-review boundary.
2. Gate 25 next requires real owner-host authenticated transfer and durable remote receipt/restart evidence; no callback-only simulation is sufficient.
3. Then public WSS/TLS and Firebase production E2E.
4. Then browser/Android real-device lifecycle and production multi-instance recovery.
5. Keep Redis destructive retention blocked until its independent safety contract passes.
6. Keep indicator UI work behind Stage 4 and its approved blueprint/review.

**Constraints:** ZERO COST; active branch only; `main` untouched; no Vercel deployment; target remains approximately 24 December 2026 as a planning target, not a guarantee.


---

## Batch 62J-226 — indicator test-count correction (24 November 2026)

A fresh declaration-level audit of the current branch source supersedes the earlier current-count statements in this document. Counting each `it(...)` declaration in the two focused suites gives:

- `src/indicators/indicatorCalculations.test.ts`: **21 named tests**.
- `src/indicators/useMarketIndicators.test.ts`: **7 named tests**.
- **Current focused indicator total: 28 named tests (21 + 7).**

This is a source declaration count, not a claim that 28 indicators are implemented or that all 28 passed independently. Exact-head Automated Tests workflow is the pass/fail authority. Older batch entries recording 17 + 7 = 24 are retained as historical counts at their respective earlier source revisions and must not be read as the current count. Indicator aggregate completion remains NOT SCORED; no visual-integration credit is awarded. The calculations and hook remain foundations until chart binding, controls, pane/overlay rendering, identity/lifecycle clearing and render-level acceptance are complete.


---

## Batch 62J-227 — exact-HEAD CI closure, WebSocket boundary re-audit, and indicator ledger synchronization (24 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Audited source/documentation HEAD:** `435dc3faa564d2afae6b5e7a3cb717c6232d4d08`  
**Exact-HEAD CI:** 4/4 configured workflows terminal SUCCESS  
**Cost:** ZERO COST • **main:** untouched • **Vercel:** no deployment  
**Delivery target:** approximately 24 December 2026 (planning target, not a guarantee)

### 1. Exact-HEAD CI — all workflows terminal

The branch HEAD was checked before this documentation update. All four workflow runs below reference the exact SHA `435dc3faa564d2afae6b5e7a3cb717c6232d4d08`, and each run plus its job steps is terminal SUCCESS:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | [45427397505](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45427397505) | 🟩 SUCCESS |
| CodeQL Security Analysis | [45427397419](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45427397419) | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | [45427397478](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45427397478) | 🟩 SUCCESS |
| Full Git History Secret Audit | [45427397474](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45427397474) | 🟩 SUCCESS |

Automated Tests completed all 39/39 listed steps, including frontend unit tests/build, backend tests, isolated Redis TLS CA/hostname fixture, synthetic Worker/Workerd and Durable Object checks, Android host/release preflight checks, dependency audits, backend container build/smoke and image scan/report steps. CodeQL completed Python and JavaScript/TypeScript. ARM64 completed all 7/7 steps. Secret-history audit completed all 6/6 steps. No exact-HEAD workflow remained queued or in progress at the time of this audit.

This closes the CI wait from Batch 62J-226. It does not establish public production WSS, Firebase production E2E, owner-host snapshot transport, or physical-device acceptance.

### 2. WebSocket / Gate 25 source boundary re-audit

Read current branch source:
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/snapshot_attestation.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`
- the latest Gate 25 and cross-path acceptance records.

Confirmed repository-side controls include owner-pinned Ed25519 trust keys, deterministic snapshot attestation verification, immutable persisted receipt re-verification, authenticated source/key binding, checkpoint/receipt cursor and digest equality, retention/schema/protocol validation, and fail-closed ordering before Redis client construction. The runtime closes a Redis client if consumer construction fails. No new source defect was established by this targeted re-audit; no speculative runtime edit was made.

External acceptance remains open and cannot be manufactured in repository tests:
1. Authenticated owner-host snapshot transfer and retrieval of each gateway's persisted immutable receipt.
2. Restart/re-verification and durable high-water acknowledgement from every gateway.
3. Public HTTPS/WSS endpoint, reverse proxy and TLS proof.
4. Firebase production sign-in, entitlement and revocation E2E.
5. Browser/Android lifecycle, process-death recovery, network handover and production multi-instance failover.
6. Redis destructive retention only after gateway inventory/retirement, pending-entry policy, per-gateway floor acknowledgements, separate authority and crash-safe trim/reconcile are proven.

No production secrets, private keys, host, domain, paid service, or destructive Redis operation was introduced. XTRIM/XDEL and consumer-group destruction remain unauthorized.

### 3. Indicator inventory — declaration-level recount

A fresh source count at `435dc3faa564d2afae6b5e7a3cb717c6232d4d08` confirms:
- `src/indicators/indicatorCalculations.test.ts`: **21** named `it(...)` tests.
- `src/indicators/useMarketIndicators.test.ts`: **7** named `it(...)` tests.
- Focused indicator total: **28 named tests (21 + 7)**.

The exact-HEAD Automated Tests workflow succeeded. The count is test inventory, not indicator count or a completion percentage.

| Indicator / subsystem | Verified calculation or data foundation | Visible chart integration | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid source index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 Foundation |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 Foundation |
| RSI14 Wilder | 14-change seed + Wilder recurrence; first valid index 14 | 0–100 pane and 30/70 guides absent | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; MACD index 25, signal/histogram 33 | Pane, lines, histogram, zero guide absent | 🟨 Foundation |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Three-line overlay, fill, toggle and latest values absent | 🟨 Foundation |
| Shared Indicator Hook | Exact keyed immutable backend snapshot, shared cache, trust gating, stale-output clearing | Not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Visual renderer remains gated; user references recorded | 🟧 Gated |
| Volume Profile / Complete VP / movable-range VP tool | No complete production implementation verified | Not integrated | 🟥 Open |
| Heatmap | No accepted depth/liquidity engine and renderer | Not integrated; reference and validated depth contract still required | 🟥 Open |
| Liquidation Maps | No accepted methodology/provenance and renderer | Not integrated | 🟥 Open |

Footprint OFF must preserve normal candlestick spacing; explicit ON alone activates the dedicated spaced-cluster layout. Footprint and Heatmap visuals remain reference/blueprint gated. Major indicator chart integration remains behind the official Stage 4 gate and scoped user-reviewed blueprint. The older 24-test count in historical batch entries remains historical; this 28-test recount is the current source inventory. **Aggregate indicator progress remains NOT SCORED.**

### 4. Official progress dashboard — no score inflation

| Meter | Verified value | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 criteria = 300/400 ticks = 75% provisional | 🟨 Active; inherited baseline, not re-scored in this batch |
| Stage 2 — Market Data Infrastructure | Active engineering; no approved denominator | 🟦 Active / NOT SCORED |
| Stage 3 | Not officially opened/scored | ⬜ NOT SCORED |
| Stage 4 | Waiting on stage gate / approved blueprint | 🟪 Gated / NOT SCORED |
| Stage 5 | Not officially opened/scored | ⬜ NOT SCORED |
| Stage 6 | Not officially opened/scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 Open |
| Overall project | No approved six-stage weighted denominator | ⚪ NOT SCORED |
| Aggregate indicator completion | No approved indicator denominator/weights | ⚪ NOT SCORED |
| IP3S / significant progress | No approved scoring formula applied | ⚪ NOT SCORED |

Do not extrapolate Stage 1's provisional 75% to total project completion. This documentation/CI batch awards no stage ticks, no indicator integration credit and no external WebSocket gate closure.

### 5. Execution order retained

Continue repository-verifiable work first; then real owner-host authenticated transfer and durable receipt/restart proof (Gate 25); then public WSS/TLS and Firebase production E2E; then browser/Android lifecycle and multi-instance recovery; then Redis retention only after its safety contract. Indicator UI remains behind Stage 4 and its blueprint/review gate. No branch change, deployment, or paid service is authorized by this record.


---

## Batch 62J-228 — WebSocket color taxonomy and parent-gate roll-up correction (24 November 2026)

**Audited HEAD:** `f3ca6becff4d72ba1638e4cf0233366f5d3368bb`  
**Branch:** `phase-2/market-data-foundation`  
**Exact-HEAD CI:** 4/4 terminal SUCCESS  
**Scope:** status semantics and acceptance accounting; no runtime source changed  
**Cost:** ZERO COST • `main` untouched • Vercel deployment deferred

### Why a WebSocket sub-status can be yellow/green while the overall gate is red

There was no demonstrated code regression between the previous yellow/partial indication and the red end-to-end gate indication. The colors had been used at different scopes without a clear legend. A repository-side capability can be green or yellow while the parent production-acceptance gate remains red because external proof is still missing. These are separate dimensions, not a downgrade of the same test result.

The following color legend is now authoritative for new progress entries:

| Color | Meaning | What it does not mean |
|---|---|---|
| 🟩 Green | The named criterion is implemented and verified at the stated scope, with evidence | Does not automatically close its parent production gate |
| 🟨 Yellow | Partial foundation or repository-side capability exists; additional integration/acceptance remains | Does not mean production acceptance is complete |
| 🟧 Orange | Gated or blocked on a prerequisite, owner input, reference, or safety condition | Does not imply a code failure |
| 🟥 Red | The named acceptance criterion or parent end-to-end gate remains unmet/open | Does not mean already-green repository tests regressed |
| 🟦 Blue | Active work or CI currently running | Not a pass/fail result |
| 🟪 Purple | Stage/blueprint gate prevents implementation from starting | Not a defect report |
| ⬜ Grey | Not started / not yet assessed | Not evidence of failure |
| ⚪ Neutral | No approved denominator or score | Never convert to a guessed percentage |

### Canonical WebSocket roll-up at this HEAD

| Scope | Current status | Evidence / remaining acceptance |
|---|---|---|
| Browser protocol, ticket/authentication, replay and reconnect foundations | 🟩 Repository-verified | Existing source and exact-HEAD CI coverage |
| Redis replica, replay, recovery and consumer lifecycle foundations | 🟩 Repository-verified | Existing backend suites and synthetic Redis fixtures |
| Gate 25 owner-pinned Ed25519 verification, immutable receipt re-verification, source/key binding and fail-before-Redis | 🟩 Repository-verified | Batch 62J-221 source/test contract and exact-HEAD CI |
| Gate 25 owner-host private-key custody, authenticated remote transfer, each gateway's persisted receipt retrieval, restart re-verification and per-gateway durable high-water ACK | 🟥 External acceptance open | Requires actual owner-controlled host/gateway evidence; repository callback tests cannot prove remote custody or network authentication |
| Gate 25 parent acceptance | 🟥 OPEN | Parent gate closes only after all required external owner-host evidence is accepted |
| Gate 36 public HTTPS/WSS, reverse proxy/TLS, production runtime and physical Android lifecycle | 🟥 OPEN | Requires public endpoint and real deployment/device evidence |
| Firebase production sign-in, entitlement and revocation E2E | 🟥 OPEN | Requires owner-controlled Firebase project evidence |
| Browser/Android process-death, network handover, production multi-instance failover | 🟨/🟥 PARTIAL / OPEN | Repository foundations exist; deployed browser and real-device/host acceptance incomplete |
| Redis destructive retention | 🟧 BLOCKED | No XTRIM/XDEL/group destruction until gateway inventory/retirement, PEL policy, per-gateway floor ACK, separate authority and crash-safe trim/reconcile are proven |
| Whole WebSocket production end-to-end | 🟥 NOT COMPLETE | Parent status is determined by outstanding external acceptance, not the green repository rows |

**Important:** A green sub-row does not make Gate 25 or the complete WebSocket green. Likewise, a red parent gate does not invalidate a previously successful unit test or CI run. Future dashboards must show the scope next to every colored status.

### Exact-HEAD CI read-back

At `f3ca6becff4d72ba1638e4cf0233366f5d3368bb`, all configured workflows are terminal SUCCESS, with every reported job step completed and no failed steps:

- Automated Tests: [45428878737](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428878737) — 41/41 steps.
- Full Git History Secret Audit: [45428878666](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428878666) — 6/6 steps.
- CodeQL: [45428879181](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428879181) — JavaScript/TypeScript 8/8 and Python 8/8.
- OCI ARM64: [45428878741](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428878741) — 7/7 steps.

This 4/4 result applies to this exact HEAD only. It is repository CI, not external production acceptance.

### Indicator progress reconciliation — no score inflation

| Indicator / subsystem | Current evidence | Chart/UI state | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay/toggle/legend/latest value/lifecycle absent | 🟨 Foundation |
| EMA20 | SMA-seeded EMA, alpha 2/21; first valid index 19 | Overlay/toggle/legend/latest value/lifecycle absent | 🟨 Foundation |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | Pane and 30/70 guides absent | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; first MACD index 25, signal/histogram index 33 | Pane/lines/histogram/zero guide absent | 🟨 Foundation |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Three-line overlay/fill/toggle/latest values absent | 🟨 Foundation |
| Shared Indicator Hook | Keyed immutable snapshot, shared cache, trust gating, stale-output clearing | Not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Renderer gated; two user reference images on record | 🟧 Gated |
| Volume Profile / Complete VP / movable-range VP | No complete production implementation verified | Not integrated | 🟥 Open |
| Heatmap | Depth/liquidity engine and accepted renderer not verified | Visual implementation remains gated; user reference/data contract outstanding | 🟥 Open |
| Liquidation Maps | Methodology/provenance and renderer not accepted | Not integrated | 🟥 Open |

Focused test declaration inventory remains **28 total = 21 calculation tests + 7 shared-hook tests**. This is not a count of completed indicators or a completion percentage. All 28 are declarations in the two focused test files; exact-HEAD CI is the pass/fail authority. Older 24-count notes are historical source snapshots, not current inventory.

Footprint OFF must retain standard candle spacing; explicit ON alone enables the spaced-cluster layout. Footprint/Heatmap visual work and major chart integration remain behind the required stage/blueprint/user-review gates. Aggregate indicator progress stays NOT SCORED.

### Project progress dashboard — unchanged scores

| Meter | Current value | Status |
|---|---:|---|
| Stage 1 Foundation | 30/40 = 75% provisional; inherited baseline, not independently re-audited in this cycle | 🟨 |
| Stage 2 Market Data Infrastructure | Active; denominator not approved | 🟦 NOT SCORED |
| Stage 3 Chart Engine & Timeframe | Not formally scored | ⬜ NOT SCORED |
| Stage 4 Indicators & Analytics | Stage gate / blueprint required | 🟪 NOT SCORED |
| Stage 5 Professional UI & Interactive Tools | Not formally scored | ⬜ NOT SCORED |
| Stage 6 Hardening, Validation & APK Release | Not formally scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicator completion | No approved denominator/weights | ⚪ NOT SCORED |
| IP3S / significant progress | No approved formula applied | ⚪ NOT SCORED |

No stage tick, indicator integration credit, Gate 25 external acceptance, or overall percentage is awarded by this documentation/status correction.

### Work order remains unchanged

1. Continue repository-verifiable work and exact-HEAD CI.
2. Close Gate 25 with actual owner-host authenticated transfer, persisted receipt retrieval, restart verification and durable high-water ACK from every gateway.
3. Close public WSS/TLS and Firebase production E2E.
4. Complete browser/Android lifecycle and production multi-instance recovery.
5. Consider Redis destructive retention only after all independent safety prerequisites pass.
6. Keep indicator chart UI behind Stage 4 and its scoped approved blueprint/user review.

No paid service, production credential, domain, deployment, or destructive Redis action was used. APK planning target remains approximately 24 December 2026, not end-of-month.


## Batch 72 exact-head CI closure — 25 November 2026

**Audited commit:** `a342a2abe8f70315445343e123e661ea37c52050` on `phase-2/market-data-foundation`. All four required workflows are now terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45599485761 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45599485734 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45599485776 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45599485759 | 🟢 SUCCESS | 6/6 |

Automated Tests log confirms **1,426 passed, 1 skipped, 6 warnings in 59.44 seconds**. The skipped test is the isolated Redis TLS integration fixture because it is not configured. Therefore this is not owner-host Redis TLS acceptance. Container smoke checks passed for health, Redis ACL/AOF persistence across restart, fail-closed API response during Redis outage, backend reconnect, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence, and HTTP rate-limit rejection. OCI ARM64, CodeQL and full-history secret audit passed. No failure was recorded.

**Evidence boundary:** these are GitHub CI results only. They do not prove a live Cloudflare deployment, public WSS, Firebase identity, real market-data provider, owner-host Redis TLS, Android/browser production lifecycle, or production snapshot transfer/ACK. The CI success does not change Stage 1 30/40 provisional or Gate 10 0/10. Indicator implementation status and completion credit are unchanged.


## Batch 73 exact-head CI closure and dedicated Redis TLS acceptance — 25 November 2026

**Audited commit:** `c3effcd4f48f03ef9cbe28edf59787ed74f4bc88` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45601263082 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45601263013 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45601262998 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45601263240 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 48.77 seconds**. In addition, the dedicated TLS step generated an ephemeral test CA, trusted server certificate for DNS:localhost, wrong CA and a TLS-only Redis listener; it ran `tests/test_shared_guard_tls_integration.py` separately and the result was **1 passed in 0.07s**. That test verified successful CA/hostname validation and ACL-backed shared-guard operations, rejection of wrong hostname, untrusted CA and plaintext downgrade. The same TLS listener then proved AOF data, TLS-only listener and ACL survived a real container restart. The later general pytest run reports the TLS test skipped because its short-lived fixture variables are intentionally scoped to the preceding dedicated step; this does not negate the dedicated 1/1 pass.

The same run also passed frontend tests/build and secret scanning, Cloudflare synthetic proof tests, Durable Object runtime tests, backend dependency audit, synthetic SQLite outbox and metrics benchmarks, backend container build, container smoke tests and container vulnerability scan. CodeQL, native ARM64 and full reachable-history secret audit passed. No CI failure was recorded.

**Evidence boundary remains:** isolated CI Redis TLS acceptance is not owner-host Redis TLS deployment acceptance. CI still does not prove production Cloudflare deployment, public WSS, Firebase identity/entitlement, live provider rights/data, production snapshot transfer/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10 formally closed. Indicator completion credit unchanged.


## Batch 74 exact-head CI closure — 25 November 2026

**Audited commit:** `9671ce0b9c1c54b1127fe55a03e5008611c6fc2e` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45602155645 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45602155744 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45602155670 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45602155558 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 48.66 seconds**. Dedicated Redis TLS integration: **1 passed in 0.07 seconds** using an ephemeral CA, DNS:localhost certificate, wrong CA and TLS-only Redis listener. Wrong-hostname, untrusted-CA and plaintext downgrade cases were rejected; authenticated shared-guard operations succeeded. Redis AOF data, TLS-only listener and ACL survived an actual container restart. The later general suite's one skip is expected because the temporary TLS fixture variables are scoped to the dedicated preceding step. Container health, fail-closed Redis outage/reconnect, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence and HTTP rate-limit smoke checks passed. Frontend tests/build/secret scan, Cloudflare synthetic Worker/DO runtime tests, backend dependency audit, synthetic SQLite benchmarks, backend container build and vulnerability scan passed.

This CI success does not prove owner-host TLS, production Cloudflare deployment/public WSS, Firebase identity, live provider rights/data, production snapshot/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10. Indicator status and completion credit are unchanged.


## Batch 75 exact-head CI closure — 25 November 2026

**Audited commit:** `fd200b617a87d04693a08d04be26ad4991a0f978` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45603007729 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45603007940 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45603007601 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45603008057 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 71.47 seconds**. Dedicated Redis TLS integration: **1 passed in 0.11 seconds**. Ephemeral CA/server certificate/TLS-only Redis fixture verified trusted CA + DNS hostname, ACL-backed shared-guard operations, rejection of wrong hostname, untrusted CA and plaintext downgrade; AOF data, TLS-only listener and ACL survived an actual container restart. The later general pytest invocation skips the TLS test because fixture environment variables are intentionally scoped to the preceding dedicated step. Backend container health/outage/reconnect, non-root runtime, persistent volume, SQLite integrity/restart and rate-limit smoke checks passed. Frontend tests/build/secret scan, Cloudflare synthetic Worker/DO tests, dependency audit, synthetic SQLite benchmarks, image build/scan, CodeQL, ARM64 and full-history secret audit passed.

Evidence remains CI-only: not owner-host TLS acceptance, production Cloudflare deployment/public WSS, Firebase identity, live provider rights/data, production snapshot/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10. Indicator completion credit unchanged.


## Batch 76 exact-head CI closure — 25 November 2026

**Audited source commit:** `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45604020771 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45604020613 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45604020280 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45604020286 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 57.78 seconds**. Dedicated Redis TLS integration: **1 passed in 0.08 seconds**. It used an ephemeral CA, DNS:localhost certificate and TLS-only Redis listener; trusted CA/hostname and ACL-backed shared-guard operations passed; wrong hostname, untrusted CA and plaintext downgrade were rejected. AOF data, TLS-only listener and ACL survived a real Redis container restart. The general pytest suite's one skip is expected because fixture variables are scoped to the dedicated preceding step. Backend container smoke tests, frontend build/tests/secret scan, Cloudflare synthetic Worker/DO tests, backend dependency audit, synthetic SQLite benchmarks, container vulnerability scan, CodeQL, ARM64 and full-history secret audit all passed.

This is CI evidence only. It does not prove owner-host TLS, production Cloudflare deployment/public WSS, Firebase identity/entitlement, live provider rights/data, production signed snapshot/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10. Indicator completion credit unchanged.

The following documentation-only reconciliation commit does not change runtime/source files; CI is not rerun for that documentation-only commit because the exact source tree above already passed all four workflows.


---

## PROJECT STATUS — Batch 78 (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Documentation HEAD before Batch 78:** `fb4fb9843535b0dae1cc733d65df9de653dd88ba`  
**Last source/test SHA:** `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`  
**Batch 78 report:** [Recovery, monitoring and five-batch reconciliation](WORK_CYCLE_2026-11-25_BATCH78_RECOVERY_MONITORING_RECONCILIATION.md)

Batches 74–77 already existed and are reconciled; they are not reimplemented. Exact-source CI recorded by Batch 77: Automated Tests 41/41 (1,426 passed, 1 skipped, 6 warnings), CodeQL 16/16, OCI ARM64 7/7, Secret Audit 6/6; dedicated Redis TLS integration 1 passed. The subsequent branch commits are documentation-only and marked `[skip ci]`; no new source CI run is claimed for them.

**Stage dashboard:** Stage 1 official active, 30/40 = 75% provisional 🟨; Gate 10 = 0/10 formally closed 🟥 (criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39). Stage 2 🟦 preparatory only; Stage 3 ⚪ not scored; Stage 4 🟪 gated; Stages 5–6 ⚪ not scored. Overall project, aggregate indicator completion and IP3S remain ⚪ NOT SCORED because no approved weighted denominator exists.

**WebSocket/Gate 25:** production WSS, Firebase identity/entitlement, lawful zero-cost provider provenance, production ticket issuance, signed snapshot transfer, authenticated persisted receipt retrieval, durable per-gateway high-water ACK/fencing/restart reconciliation and public browser/Android E2E remain OPEN. Redis `XTRIM`, `XDEL` and consumer-group destruction remain BLOCKED until durable gateway ACK acceptance. Cloudflare Worker/DO remains synthetic-only; no production resources were created. The connected account inventory is empty, while the user has separately stated the project server is on Cloudflare; do not infer that the connected account is the hosting account or create duplicate infrastructure.

**Recovery/monitoring:** CI verifies container-scope health, Redis ACL/AOF restart, outage fail-closed/reconnect, non-root execution, volume ownership smoke, SQLite integrity/restart, rate limiting and isolated TLS. Owner-host secret/volume/DB restore/off-host encrypted backup, independent alert/incident drill, production WSS and device recovery remain unaccepted.

**Indicators:** SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 FOUNDATION; Footprint PRO 2GD 🟧 GATED; Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps 🟥 OPEN. Focused declarations remain 28 (21 calculation + 7 hook), not completion. No indicator source/UI change and no completion credit in Batch 78. `CandlestickChart.tsx` integration remains absent. Preserve warm-up nulls, prefix causality, no lookahead/repaint, exact timestamp alignment and Footprint OFF normal candle spacing.

**Controls:** ZERO COST; `main` untouched; Vercel deferred; no paid data/hosting/monitoring/backup; no production deployment; delivery target around 24 December 2026.


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

## Batch 80–86 execution reconciliation — 25 November 2026

The latest evidence reconciliation is recorded in `docs/WORK_CYCLE_2026-11-25_BATCH80_86_EXECUTION_RECONCILIATION.md`. Corrected accounting: Batch 80 is complete at code/CI scope; source/gateway factory components for Batches 81–82 already exist but owner callback/host integration is still open; prior real-Redis two-ASGI/TCP recovery and snapshot-generation scenarios provide partial Batch 83 acceptance; immutable signed snapshot receipts exist but Gate 25 owner-accepted durable high-water ACK remains open; public Cloudflare WSS/device E2E remains open; local recovery/metrics foundations exist but owner-host backup/restore remains open.

Exact source/test SHA `66d4c6a812d5ce2570345e1108e813b5067f5248`: Automated Tests 1,433 passed, 1 skipped, 6 warnings; CodeQL Python 8/8 and JavaScript/TypeScript 8/8; Full Git History Secret Audit 6/6; OCI ARM64 7/7. Every job is terminal success. This evidence does not apply to later documentation-only HEADs. See the reconciliation report for test scope, skipped TLS test boundary, detailed batch states, and ordered dependencies.


---

## Latest verified source/test checkpoint — Batch 81 (25 November 2026)

- Active branch: `phase-2/market-data-foundation`; `main` untouched.
- Source/test SHA: `9138249fc31431c1112fb6fa49c4e11e63dc0f1a`.
- Change: source publisher snapshot evidence now requires each gateway receipt's explicit `gateway_id` to match the authenticated inventory key; mismatch fails before Redis client construction.
- Files: `backend/app/ohlcv_redis_runtime.py`, `backend/tests/test_ohlcv_redis_runtime.py`.
- Exact-head CI: 4/4 required workflows terminal SUCCESS. Backend 1,434 passed, 1 skipped, 6 warnings; dedicated Redis TLS fixture 1 passed in 0.08 s. Automated Tests, CodeQL, Full Git History Secret Audit and OCI ARM64 all terminal; no running jobs.
- Batch 81 remains component foundation, not production activation: owner-authenticated remote verifier and durable receipt retrieval still required. Batch 82 owner installer/key pinning, Batch 84 owner-accepted high-water ACK, Batch 85 public Cloudflare WSS/device E2E and Batch 86 owner-host restore/incident acceptance remain open.
- Indicator source/UI unchanged; no indicator progress credit. Full ledger: `docs/WORK_CYCLE_2026-11-25_BATCH81_GATEWAY_IDENTITY_RECEIPT_BINDING.md`.
- ZERO COST; no Cloudflare resource or production deployment changed; delivery target around 24 December 2026.


---

## Latest checkpoint — 25 November 2026 / Batch 81 authenticated peer binding

Source/test SHA `e1d2cfe05130e705264f416c61f56c6d12a73df3` adds `authenticated_gateway_id` binding to the source publisher receipt validator. It must match the inventory gateway ID and must be populated from authenticated connection identity by the owner callback, never copied from receipt payload. Regression cases for both gateway ID fields passed.

Exact SHA CI: **4/4 workflows SUCCESS**. Backend **1,435 passed, 1 skipped, 6 warnings** in 58.80s; dedicated isolated Redis TLS test **1 passed in 0.08s**. CodeQL, full reachable-history secret audit and OCI ARM64 readiness all passed. No running jobs remain.

Batch 81 remains 🟨 foundation/hardening pending owner callback; 82 🟨 foundation; 83 🟨 broad matrix; 84 🟧 receipt foundation; 85 🟥 production WSS/E2E; 86 🟧 local recovery foundation. No indicator source/UI changed; indicator status receives no new completion credit. Full evidence and CI run IDs are recorded in `docs/WORK_CYCLE_2026-11-25_BATCH81_GATEWAY_IDENTITY_RECEIPT_BINDING.md`.

Cloudflare: expected account display name `DZZTV2GD ENGINE SERVER` is not present in the currently connected account list (exact-name read-only lookup returned zero). No account/resource mutation or billing action was performed. Batch 85 must use the existing account after it is connected; do not create duplicate infrastructure.
