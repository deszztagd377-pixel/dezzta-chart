# DEZZTA CHART — Batch 81 gateway receipt identity hardening

**Date:** 25 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test commit:** `9138249fc31431c1112fb6fa49c4e11e63dc0f1a`  
**Parent:** `24c8ce4935c2f9099d1b299a07ec9f76d611da02`  
**Cost/deployment:** ZERO COST. No paid service, production deployment, Cloudflare mutation, or `main` change.

## Change delivered

The source publisher's owner-snapshot evidence validator now requires every `gateway_installations[gateway_id]` receipt to carry a `gateway_id` exactly equal to its authenticated inventory key. A receipt mapped under `gateway-a` but claiming `gateway-b` is rejected before Redis client construction.

Files changed:
- `backend/app/ohlcv_redis_runtime.py`
- `backend/tests/test_ohlcv_redis_runtime.py`

The existing parameterized receipt-identity regression test now includes a mismatched `gateway_id` case. Its CI case passed. Existing source, stream, generation, cursor, digest, replica uniqueness, signer-key consistency, and complete gateway-set checks remain in place.

This hardens the repository-side Batch 81 evidence boundary. It does **not** create the owner-controlled remote verifier, prove the remote gateway's identity by itself, or activate the production publisher. The owner callback must still authenticate the remote connection and retrieve the receipt from the gateway's durable store; it must populate the gateway ID from that authenticated identity, not trust an untrusted payload field.

## Exact CI evidence on the source/test SHA

All four required workflows are terminal SUCCESS on the exact commit `9138249fc31431c1112fb6fa49c4e11e63dc0f1a`:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45624619369](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45624619369) | SUCCESS; backend **1,434 passed, 1 skipped, 6 warnings** in 61.47 s; all job steps completed successfully |
| CodeQL | [45624619219](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45624619219) | SUCCESS; Python and JavaScript/TypeScript jobs both completed |
| Full Git History Secret Audit | [45624619269](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45624619269) | SUCCESS |
| OCI ARM64 Image Readiness | [45624619275](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45624619275) | SUCCESS |

The new `gateway_id` mismatch case is explicitly shown as PASSED in the test log. The one full-suite skip is the Redis TLS integration test when invoked without its isolated fixture variables; the workflow separately starts the TLS fixture and runs that exact integration test successfully: **1 passed in 0.08 s**. The dedicated path verifies CA/hostname validation and Redis ACL/shared-guard operations.

Additional completed Automated Tests job checks:
- Frontend unit tests and frontend build.
- Synthetic Cloudflare Worker/SQLite Durable Object proof tests (not production deployment).
- Synthetic SQLite outbox benchmark: 1,000 inserted/replayed events, two concurrent reader threads, report uploaded.
- Synthetic SQLite metrics collector benchmark: 1, 4 and 16 workers; SQLite integrity `ok`; report uploaded.
- Backend dependency audit.
- Backend container build and smoke test with shared Redis guard and persistent volume.
- Redis ACL authentication and AOF persistence across container restart.
- API fail-closed behavior during Redis outage and backend reconnection.
- Non-root container identity, mounted-volume ownership, SQLite integrity/restart persistence, HTTP rate-limit rejection.
- Container vulnerability scan and report export/upload.

Every workflow and job is terminal; no CI run was left running. CI evidence applies to the exact source/test SHA above. This report is documentation-only and does not claim a new CI run for its own docs commit.

## Batch 80–86 status — evidence-based

| Batch | State | Remaining boundary |
|---|---|---|
| 80 — strict runtime role binding | 🟩 COMPLETE at source/test/CI scope | Production deployment acceptance is separate |
| 81 — source publisher runtime | 🟨 COMPONENT FOUNDATION + receipt identity hardening | Owner-authenticated verifier and durable receipt retrieval for every required gateway; real host injection |
| 82 — gateway replica runtime | 🟨 COMPONENT FOUNDATION | Owner-authenticated snapshot transfer/install callback and owner-pinned production Ed25519 public keys |
| 83 — Redis/two-gateway recovery | 🟨 BROAD AUTOMATED MATRIX PASSED | Remaining uncovered Redis server/host failure and owner-host network/restart acceptance; do not duplicate the 22 existing consumer tests |
| 84 — durable receipt/high-water ACK | 🟧 RECEIPT FOUNDATION | Owner-accepted durable per-gateway applied high-water ACK and restart reconciliation across the actual gateway inventory |
| 85 — Cloudflare WSS/device E2E | 🟥 OPEN | Existing production account/zone/route/origin mapping, public WSS, Firebase production auth/entitlement, browser and Android lifecycle |
| 86 — recovery/observability/backup | 🟧 LOCAL FOUNDATION | Owner-host backup/restore, off-host encrypted backup using an already available zero-cost destination, production monitoring and incident drill |

No owner-specific endpoint, hostname, private key, remote receipt source, or deployment topology has been fabricated. Redis `XTRIM`, `XDEL`, and consumer-group destruction remain prohibited until every required gateway has a durable owner-accepted high-water ACK and restart reconciliation proof.

## Ordered WebSocket execution

1. Batch 81: owner-controlled source verifier authenticates snapshot artifact and obtains every gateway's durable receipt; bind source ID, stream key, generation, cursor, SHA-256, gateway ID, replica ID, signer key ID and owner signature.
2. Batch 82: owner-controlled authenticated gateway installer; persistent replica path, expected source ID, stable consumer identity and pinned Ed25519 key map. Verify snapshot before Redis consume.
3. Batch 83: add only uncovered server restart/fencing/receipt recovery tests; existing real-Redis/two-ASGI tests remain authoritative for their covered cases.
4. Batch 84: separate source publisher cursor, replica applied cursor, Redis XACK and owner-accepted durable gateway high-water ACK. Enforce monotonicity, generation/digest binding, stale-owner fencing and restart reconciliation.
5. Batch 85: use only the existing Cloudflare production route/origin after owner mapping is known; verify public WSS and real browser/Android lifecycle.
6. Batch 86: owner-host persistence, restore to a separate path, compare identity/generation/digest/cursor, and execute incident drills.

## Full indicator progress — no false credit

No indicator calculation, chart integration, or renderer changed in this WebSocket batch. The focused declaration inventory remains **28 = 21 calculation declarations + 7 shared-hook declarations**; it is not a passing-test count or completion percentage.

| Indicator | Status | Current evidence and acceptance still required |
|---|---|---|
| SMA20 | 🟨 FOUNDATION | Arithmetic mean; first valid index 19; chart overlay/toggle/legend/value/lifecycle not accepted |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; alpha 2/21; first valid index 19; chart integration not accepted |
| RSI14 Wilder | 🟨 FOUNDATION | Wilder recurrence; first valid index 14; 0–100 pane and 30/70 guides not accepted |
| MACD12/26/9 | 🟨 FOUNDATION | MACD line first index 25; signal/histogram first index 33; dedicated pane not accepted |
| Bollinger20,2 | 🟨 FOUNDATION | 20-close mean ± 2 population SD; first valid index 19; bands/fill/toggle not accepted |
| Shared Indicator Hook | 🟨 FOUNDATION | 7 focused declarations; integration with `CandlestickChart.tsx` not accepted |
| Footprint PRO 2GD | 🟧 GATED | Synthetic/offline accumulator only; not exchange-native bid/ask truth; visual implementation must match both saved references |
| Volume Profile | 🟥 OPEN | Price-bin volume conservation, range semantics and timestamp boundaries |
| Complete Volume Profile | 🟥 OPEN | Full-session completeness, POC/VAH/VAL and conservation |
| Movable-range Volume Profile | 🟥 OPEN | User-selected bounds and deterministic recomputation |
| Heatmap | 🟥 OPEN | Data provenance/aggregation/decay; visual work waits for the user's Heatmap reference |
| Liquidation Maps | 🟥 OPEN | Provenance, estimation method and confidence contract |

Global mathematical and lifecycle invariants:
- Warm-up values remain null until valid: SMA/EMA index 19; RSI14 index 14; MACD line index 25 and signal/histogram index 33; Bollinger index 19.
- Prefix causality: appending future candles cannot alter prior outputs.
- No future-candle lookahead or repaint.
- Exact timestamp and series-identity alignment; stale outputs clear on identity change.
- Deterministic repeated calculations, bounded work, no mutation of source candles.
- No calculations for demo/loading/unavailable/error/empty snapshots.
- Footprint OFF keeps ordinary candle spacing; explicit ON alone enables spaced clusters.
- Footprint visual work uses the two saved user references. Heatmap visual work remains blocked until its reference is supplied.

## Project progress dashboard

| Project meter | Current value | State |
|---|---:|---|
| Stage 1 | 30/40 = 75% provisional | 🟨 |
| Gate 10 | 0/10 formally closed | 🟥 |
| Stage 2 | Preparatory; not formally scored | 🟦 |
| Stage 3 | Not scored | ⚪ |
| Stage 4 | Gated | 🟪 |
| Stage 5 | Not scored | ⚪ |
| Stage 6 | Not scored | ⚪ |
| Overall project | No approved weighted denominator | ⚪ NOT SCORED |
| Significant progress / IP3S | No approved weighted denominator | ⚪ NOT SCORED |
| Indicator aggregate | No approved weighted denominator | ⚪ NOT SCORED |
| Delivery target | Around 24 December 2026; planning target only | 🟨 |

Stage 1 remains provisional; this patch does not close unrelated criteria. Gate 10 criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain open. Overall project/IP3S/indicator percentages are intentionally not invented.

## ZERO COST and ownership boundary

No Cloudflare account, zone, Worker, Pages project, Tunnel, Durable Object, R2 bucket, domain or paid service was created or changed. The prior connected-account inventory is only evidence about the connected account, not proof that the user's production server is absent. A Cloudflare account name by itself does not create a subscription or charge; only explicit activation/purchase actions can do that. Do not upgrade or purchase anything.

Planning delivery target remains around **24 December 2026**, not month-end and not a guarantee.


---

## Batch 81 authenticated gateway peer binding — 25 November 2026

- Source/test commit: `e1d2cfe05130e705264f416c61f56c6d12a73df3`.
- The source evidence validator now requires both `gateway_id` and `authenticated_gateway_id` to equal the required gateway inventory key. The owner callback contract explicitly states that `authenticated_gateway_id` must be derived from the authenticated remote connection identity, not copied from the receipt payload.
- Regression coverage includes mismatched `gateway_id` and mismatched `authenticated_gateway_id`; both negative cases are explicitly PASSED. All receipt mismatches fail before Redis client creation.
- Exact-head CI: 4/4 workflows terminal SUCCESS. Automated Tests: **1,435 passed, 1 skipped, 6 warnings** in 58.80s. Dedicated isolated Redis TLS integration: **1 passed in 0.08s**. CodeQL Python + JavaScript/TypeScript SUCCESS; full reachable-history secret audit SUCCESS; OCI ARM64 build/smoke SUCCESS. All jobs and cleanup steps completed; no running jobs remain.
- The single suite skip is the TLS integration test invoked without its isolated fixture variables; the same exact test passed in the dedicated TLS-fixture step.
- The code change hardens the owner callback evidence boundary; it does not itself authenticate remote connections or implement the missing owner-host callback. Batch 81 remains 🟨 foundation/hardening, not production activation.
- Files changed in this source commit: `backend/app/ohlcv_redis_runtime.py`, `backend/tests/test_ohlcv_redis_runtime.py`.
- CI runs: Automated Tests [45627353203](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45627353203); CodeQL [45627353126](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45627353126); OCI ARM64 [45627353138](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45627353138); Full Git History Secret Audit [45627353123](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45627353123).

## Cloudflare account-name resolution — read-only

The user supplied `DZZTV2GD ENGINE SERVER` as the expected display name of the account leading the DEZZTA CHART APK server. A read-only inventory of the Cloudflare account currently connected to this session returned one account, but an exact-name lookup for `DZZTV2GD ENGINE SERVER` returned zero matches. This does not prove the user's production account is absent; it means the expected account is not available through the current Cloudflare connection. No resource was created, modified, deleted, deployed, upgraded or purchased. No billing action occurred. Batch 85 remains blocked until the correct existing Cloudflare account is connected by the account owner.
