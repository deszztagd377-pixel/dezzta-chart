# Work Cycle — Batch 62J-69: WebSocket source publisher lifecycle

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Exact source/test HEAD:** `6f49951c253a7e7b995b4bdd52eba8153edaef77`  
**Commit:** `fix(websocket): fence publisher runtime to source checkpoint`

## Objective

Close the repository-level gap between the durable SQLite OHLCV outbox and Redis Streams without enabling the publisher by default, mixing source and gateway roles, skipping retained cursors, or assuming that a production snapshot already exists.

## Implemented

1. **FastAPI lifecycle ownership**
   - Added the optional `publisher_runtime_factory` injection point to `create_app()`.
   - Publisher and gateway replica runtime factories are mutually exclusive; source and gateway remain separate app roles.
   - The default module-level ASGI app remains publisher-disabled until its owner explicitly injects the source runtime factory.

2. **Fail-closed runtime binding**
   - The factory receives the exact `SQLiteOhlcvStore` instance used by ingestion.
   - Startup requires the publisher and checkpoint to reference that same store.
   - Checkpoint state must exist and match the configured stream key and source ID.
   - The appender must use the same dedicated Redis client, stream key and source ID.
   - Any mismatch fails startup before provider ingestion; no cursor is invented and no source database is silently substituted.

3. **Readiness and relay scheduling**
   - Dedicated Redis `PING` completes before provider ingestion starts.
   - Synchronous bounded `publish_available()` calls run through `asyncio.to_thread`, not on the ASGI event loop.
   - A successful durable-bar callback wakes the publisher using `call_soon_threadsafe`.
   - A one-second bounded poll recovers retained backlog after restart or missed wake-up.

4. **Failure and shutdown controls**
   - Transient failures use exponential backoff from 1 to 30 seconds.
   - A typed `PublisherResnapshotRequired` state is terminal for that worker; the durable checkpoint is not advanced and no cursor is skipped.
   - Shutdown signals the worker, waits up to 15 seconds, and closes the dedicated Redis client only after the publisher task stops. If a synchronous call remains active, the client is deliberately left open rather than closed underneath it.
   - Only sanitized exception class names and bounded batch counters are retained in application state; raw exception messages and credentials are not exposed.

## Regression coverage

Added three lifecycle contract tests for:
- Redis PING, background task startup, running state and graceful client close.
- Rejection of a combined source-publisher/gateway app role.
- Fail-closed rejection of a publisher runtime whose configured stream does not match its checkpoint/appender.

The startup validation also checks exact source-store identity, checkpoint-store identity, source ID and checkpoint state. Existing publisher tests continue to cover ordered deterministic Stream IDs, lost-XADD-reply exact-ID verification, outage cursor preservation, retention-gap rejection and fenced checkpoint advancement.

## Exact-head CI

- Automated Tests: [44866818528](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44866818528) — **SUCCESS**.
- CodeQL Security Analysis: [44866818498](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44866818498) — **SUCCESS**.
- Full Git History Secret Audit: [44866818495](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44866818495) — **SUCCESS**.
- Frontend tests: **247/247 passed**.
- Backend tests: **1,241 passed**.
- Automated workflow: **33/33 steps succeeded**.
- Backend image build, Redis ACL/AOF + persistent-volume smoke test, container scan, vulnerability-report export and artifact upload: **SUCCESS**.

This is repository/CI evidence. It is not proof of a live owner-host Redis connection, snapshot distribution, public WSS, or browser/Android acceptance.

## Publisher wiring status

<badge color="warning">🟨🟩 HOST-FACTORY / SNAPSHOT VERIFICATION PENDING</badge>

The source publisher lifecycle hook is no longer a repository-code blocker. Actual activation still requires an owner-injected source runtime factory that:
- uses the persistent source database and a dedicated publisher ACL identity;
- uses finite Redis connect/socket timeouts;
- verifies that the publisher checkpoint watermark matches the exact global snapshot generation already installed on every target gateway;
- confirms Redis TLS/ACL and durable-volume behavior on the actual host.

The default ASGI app intentionally remains disabled until these preconditions are supplied. Do not initialize the checkpoint from an arbitrary current cursor. Do not mark the source-to-gateway production path green from CI alone.

## Indicator progress — unchanged

| Indicator / subsystem | Status | Formula / first valid candle | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Mean of 20 closes; index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; alpha 2/21; index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| RSI14 | 🟨 FOUNDATION | Wilder smoothing over 14 close changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend and renderer tests |
| MACD 12/26/9 | 🟨 FOUNDATION | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, MACD/signal lines, histogram, zero guide, toggle and legend |
| Bollinger20,2 | 🟨 FOUNDATION | Mean ± 2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing and renderer tests |
| Shared Indicator Hook | 🟨 FOUNDATION | Validated backend snapshot; candle-index aligned | Identity/timeframe binding, loading/error, stale clearing and series isolation |
| Footprint | 🟧 SIMULATED / GATED | Educational simulation; not exchange-native bid/ask truth | Owner reference image, approved blueprint, ON-only spaced clusters, bid/ask cells and performance tests |
| Heatmap | 🟥 NOT IMPLEMENTED | Data source/calculation contract not approved | Reference image, zero-cost source feasibility, validated data contract, blueprint and renderer |
| Liquidation Maps | 🟥 NOT IMPLEMENTED | No validated liquidation dataset/calculation contract | Zero-cost source feasibility, validated calculation, blueprint/reference and renderer |

**Indicator invariants:** warm-up slots remain null, never fabricated zeroes; series align to candle indices; future candles cannot change earlier outputs; symbol/venue/dataset/chart/timeframe changes invalidate stale series. Footprint OFF retains ordinary candle spacing; only explicit ON enables the spaced cluster layout. Footprint and Heatmap visual work remains gated on the user's reference images and approved blueprints. No indicator progress percentage is awarded by this backend batch.

## Gate 10 and project accounting

| Gate | Status | Remaining evidence |
|---:|---|---|
| 8 — Secrets | 🟨 HOST VERIFICATION ONLY | Actual owner-host secret injection, owner/mode, UID/GID readability, process exposure, rotation and runtime review |
| 20 — Firebase | 🟧 OPEN | Verified no-billing Firebase auth/revocation/entitlement and browser/Android flow |
| 25 — Redis | 🟧 OPEN | Real host TLS, ACL, credential lifecycle, persistence and failover |
| 30 — Restore | 🟧 OPEN | Restore drill against the actual live database path on owner-controlled runtime |
| 31 — Off-host backup | 🟧 OPEN | Independent destination/key custody and restore |
| 34 — Persistent volume | 🟧 OPEN | Actual host mount, ownership, restart persistence and disk-pressure recovery |
| 35 — HTTPS | 🟧 OPEN | Real HTTPS endpoint, certificate/hostname and renewal path |
| 36 — WSS | 🟧 OPEN | Public reverse proxy plus real browser and Android WebView acceptance |
| 38 — Monitoring | 🟧 OPEN | Collector/dashboard, retention, access control and disk-pressure acceptance |
| 39 — Incident response | 🟧 OPEN | Real operator visibility, acknowledgement/escalation and recovery drill |

- Gate 10: **0/10 formally closed**.
- Stage 1: **30/40 = 75% provisional**; no Stage 1 acceptance tick is awarded by this source/CI batch.
- Stages 2–6: not scored.
- Overall project and aggregate indicator percentages: not scored; approved weights and denominators remain absent.
- ZERO COST: no deployment, paid service, production credential, Termux/device operation, Vercel/Cloudflare action, or `main` modification.
