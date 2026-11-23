# DEZZTA CHART — Batch 62J-176
## Synthetic-only Cloudflare Worker / Durable Object proof and exact-HEAD CI

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Code/test HEAD:** `783811ccef97c0494203ad13a9f790b791a5e962`  
**Previous approved architecture blueprint:** Batch 62J-175  
**Scope:** Phase A/B synthetic-only proof, no production cutover  
**Protected branch:** `main` untouched  
**ZERO COST:** preserved

## 1. Scope and source-of-truth boundary

The owner approved beginning the Worker + Durable Object proof using synthetic data only. This batch creates an isolated proof directory and a CI lane. It does not replace, proxy, or modify the existing FastAPI production/reference backend.

Synthetic data means deterministic, locally generated OHLCV fixture values. It is not a live exchange price, not a licensed market-data feed, not a quote, and not evidence of market accuracy. The synthetic source is explicitly labelled `synthetic_only_not_market_data` in the proof responses.

No Cloudflare account, billing setting, payment method, domain, DNS record, production secret, provider key, Firebase credential, or live provider connection was used. No deployment was performed. The Worker configuration disables workers.dev and preview URLs; local secret files are ignored by Git.

## 2. Files added or changed

| File | Change | Responsibility |
|---|---|---|
| `cloudflare/proof/worker.mjs` | Added | Synthetic-only Worker routes, series Durable Object, deterministic OHLCV, hashed ticket helpers and sequence gate |
| `cloudflare/proof/worker.node-test.mjs` | Added | Node-only regression suite, deliberately outside Vitest's discovery pattern |
| `cloudflare/wrangler.jsonc` | Added | Isolated local Wrangler configuration, SQLite-backed DO migration and synthetic-only mode |
| `.github/workflows/ci.yml` | Modified | Runs syntax check, 15 Node proof tests and Wrangler JSONC parse validation after dependency setup |
| `.gitignore` | Modified | Ignores `cloudflare/.dev.vars` and local secret variants |

No frontend source, indicator formula, chart renderer, backend FastAPI runtime, Redis guard, production configuration or market-data provider adapter was changed.

## 3. Implemented proof contracts

### 3.1 Worker boundary

The Worker exposes only the isolated proof endpoints:
- `GET /health`: public liveness response that explicitly reports `synthetic-only` and provider `none`.
- `GET /v1/market-data/status`: proof-token protected; reports no live provider.
- `GET /v1/ohlcv?seriesKey=...`: proof-token protected; returns a bounded deterministic 50-bar synthetic snapshot.
- `POST /v1/auth/websocket-ticket`: proof-token protected; routes ticket issuance to the exact series DO.
- `GET /ws/market-data?seriesKey=...`: routes WebSocket upgrade to the deterministic per-series DO.
- `POST /__proof/emit`: proof-token protected synthetic event injection only.

Unknown routes fail closed. The Worker requires `PROOF_MODE=synthetic-only`; any other mode returns 503. The proof token is read only from an environment secret and is not committed. Browser Origin is checked against the explicit local allow-list. JSON bodies are bounded to 2,048 bytes.

### 3.2 Series identity and synthetic OHLCV

Canonical series key pattern:

`synthetic:<DATASET>:<SYMBOL>:<TIMEFRAME>`

Allowed timeframes in this proof: `1m`, `5m`, `15m`, `1h`.

Bars are deterministic for a given series key and sequence. OHLC values are emitted as decimal strings, volume is a decimal string, timestamps are unsigned nanosecond decimal strings, and high/low consistency is enforced by construction. The fixture is not exchange-derived.

Snapshot size is capped at 50 bars. Snapshot watermark is cursor `50`; the first accepted synthetic update is sequence `51`.

### 3.3 Ticket lifecycle

- 256 pending ticket cap per series DO.
- 90,000 ms lifetime.
- 256-bit random token; only SHA-256 digest is stored.
- Purpose is fixed to `market-data`.
- Subject is fixed to `synthetic-proof-subject`; no real account identity is accepted in this proof.
- Ticket is bound to one canonical series key.
- Consumption uses a storage transaction so concurrent duplicate use has one winner.
- A wrong-series attempt is rejected without consuming the still-valid ticket.
- Expired tickets are deleted when consumed; expired pending tickets are pruned on issuance.

This is a synthetic proof identity model, not Firebase authentication parity. It must not be connected to real user accounts.

### 3.4 Durable Object WebSocket handling

The per-series DO:
- accepts inbound WebSockets with the hibernation API `acceptWebSocket`;
- serializes the minimal connection attachment and restores attachments in its constructor;
- requires the first application frame to contain the one-time ticket;
- sends a 50-bar snapshot after ticket acceptance;
- responds to application ping with pong;
- enforces a maximum of 64 accepted sockets per series;
- accepts synthetic events only at the next contiguous sequence;
- fans out each accepted event only to authorized sockets attached to the same exact series.

No alarm, setInterval, setTimeout, polling loop, outbound provider socket, or provider subscription is created. This avoids manufacturing recurring work or hidden usage costs in the synthetic proof.

Important: the Node tests validate the pure ticket/sequence helpers and Worker HTTP boundary. They do not execute Cloudflare's actual Durable Object runtime, WebSocketPair, hibernation/eviction, attachment restoration, or end-to-end browser handshake. Those remain explicit integration gates.

## 4. Regression tests and CI result

### Synthetic proof tests

Exact code/test HEAD `783811ccef97c0494203ad13a9f790b791a5e962`:
- Node syntax check: PASS.
- Wrangler JSONC parse: PASS.
- Synthetic proof Node tests: **15 passed, 0 failed**.
- Vitest discovery no longer includes the Node-only proof suite.
- Frontend Vitest: **306 passed across 34 files**.
- Frontend dependency audit: **0 vulnerabilities**.
- Backend pytest: **1,347 passed, 1 skipped, 6 warnings**.
- Dedicated Redis TLS fixture step: PASS.
- Synthetic SQLite outbox benchmark: PASS; 1,000 synthetic bars inserted and replayed, two concurrent replay readers.
- Same-host SQLite metrics collector benchmark: PASS.
- Python dependency audit: **No known vulnerabilities found**.
- Backend container build and persistent-volume/Redis smoke test: PASS.
- Backend image HIGH/CRITICAL scan: PASS.
- Frontend source/bundle secret scans: PASS.

The one skipped backend pytest case is the shared-guard TLS integration test, which is executed separately by the dedicated isolated Redis TLS fixture step in this workflow.

### Exact-HEAD workflow results

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | 45167249268 | SUCCESS |
| CodeQL Python | 45167249876 | SUCCESS |
| CodeQL JavaScript/TypeScript | 45167249876 | SUCCESS |
| Full Git History Secret Audit | 45167250254 | SUCCESS |
| OCI ARM64 Image Readiness | 45167249525 | SUCCESS |

All listed runs target the exact code/test HEAD above. The ARM64 job built and smoke-tested the native ARM64 backend image. The automated workflow completed 37 successful steps with no failed step.

These are CI and container-smoke results. They do not prove a deployed Worker, a public WSS hostname, production authentication, a production data provider, or Android-device end-to-end acceptance.

## 5. Corrections made during the work cycle

1. First Node test run found that a ticket could be consumed by a wrong-series attempt. The consume logic was corrected so a mismatched series cannot invalidate a valid ticket.
2. The initial CI placement ran proof tests before `npm ci`, causing downstream dependency-audit steps to be skipped. The proof step was moved after frontend dependency installation and audit.
3. Vitest initially discovered `worker.test.mjs` as a frontend suite and reported “No test suite found.” The file was renamed to `worker.node-test.mjs`, and CI was updated to invoke Node's test runner. The final exact-HEAD CI passed.

No failure was suppressed. The corrected final workflow is the evidence source.

## 6. Explicitly incomplete / red gates

| Area | Status | Reason |
|---|---|---|
| Wrangler local runtime smoke | 🟥 OPEN | Wrangler/Miniflare runtime not installed or executed in this batch |
| Actual DO WebSocket handshake | 🟥 OPEN | No runtime WebSocketPair integration test |
| Hibernation and attachment restore | 🟥 OPEN | No forced eviction/rehydration test |
| Two-client / two-series isolation | 🟥 OPEN | Requires DO runtime integration tests |
| Snapshot-to-live race and durable replay | 🟥 OPEN | Current proof is bounded synthetic snapshot plus sequential synthetic updates; no durable outbox replay |
| Firebase auth parity | 🟥 OPEN | Proof uses a local synthetic bearer secret and fixed synthetic subject only |
| Public HTTPS/WSS and Android device acceptance | 🟥 OPEN | No deployment, hostname, TLS proxy or device test |
| Provider-side demand control | 🟥 OPEN | No real or recurring-$0 provider adapter connected |
| Production persistence/restore | 🟥 OPEN | No production schema migration, backup or restore drill |

The proof is not production-ready and is not wired into the main app. It is an isolated synthetic architecture slice.

## 7. Cost and capacity controls

No new package dependency was added. The proof tests use Node's built-in `node:test`. No Cloudflare account, deployment, domain, paid plan, trial, market-data API, or provider credential was used.

Local-only secret handling:
- `SYNTHETIC_PROOF_TOKEN` is not present in source or Wrangler vars.
- `cloudflare/.dev.vars` and variants are Git-ignored.
- `workers_dev` and `preview_urls` are disabled in the config.

This is a zero-cost code/test result, not a promise that future hosted traffic will remain within a vendor's free quota. No hosted quota or recurring-cost claim is awarded.

## 8. Indicator progress reconciliation

No indicator calculation, formula, hook, renderer, pane, setting, legend, chart binding, Footprint, Heatmap, or Liquidation Maps implementation changed in Batch 62J-176.

Keep existing indicator statuses unchanged:
- SMA20: 🟨 mathematical foundation; chart overlay and UI acceptance remain.
- EMA20: 🟨 mathematical foundation; chart overlay and UI acceptance remain.
- RSI14 Wilder: 🟨 mathematical foundation; dedicated pane and UI acceptance remain.
- MACD 12/26/9: 🟨 mathematical foundation; dedicated pane and UI acceptance remain.
- Bollinger20,2: 🟨 mathematical foundation; overlay and UI acceptance remain.
- Shared Indicator Hook: 🟨 foundation; chart integration/lifecycle acceptance remains.
- Footprint: 🟧 synthetic prototype only; visual reference and approved blueprint required.
- Heatmap: 🟥 not implemented; visual reference and data contract required.
- Liquidation Maps: 🟥 not implemented; defensible data contract and implementation required.

No indicator implementation credit is awarded from WebSocket/Worker work.

## 9. Project progress indicators

- Stage 1 Foundation, Security & Data Integrity: retain **30/40 = 75% provisional** from the existing ledger; this batch does not change Stage 1 acceptance.
- Stage 2 Market Data Infrastructure: synthetic Worker/DO proof source and Node tests added, but Stage 2 remains **not scored** pending runtime integration, authentication parity, replay, provider demand and external host acceptance.
- Stages 3–6: unchanged and not officially scored.
- Gate 10: **0/10 external acceptance criteria closed**.
- Overall project: **NOT SCORED**; no approved weighted denominator is available.
- Significant progress: isolated synthetic Worker/DO source plus 15 passing tests and exact-HEAD CI success. This is a meaningful engineering increment, not production WebSocket completion.

Target remains **24 December 2026**, a target and not a guaranteed delivery date.

## 10. Next work cycle

1. Add a local Wrangler/Miniflare runtime test lane only after pinning and reviewing a zero-cost-compatible toolchain; no deploy.
2. Exercise actual Durable Object WebSocket handshake, ticket consumption, two-client same-series fan-out and two-series isolation.
3. Force DO hibernation/rehydration and prove attachment restoration without losing authorized series identity.
4. Add bounded slow-consumer and unauthorized-socket handling tests; prevent unauthenticated sockets from consuming capacity indefinitely.
5. Add snapshot-to-live cursor continuity and bounded replay before claiming replay parity.
6. Keep Firebase production auth, provider integration, public WSS, Android acceptance, and persistence migration closed until separately approved and evidenced.
7. Reconcile the indicator ledger after each actual indicator-specific source/test change, not from infrastructure work.

**Batch 62J-176 result:** isolated synthetic Worker/DO proof source, local Wrangler config, Node regression tests and CI lane committed; exact-head CI/security/ARM64 workflows succeeded. No deployment, production cutover, live provider, paid service, main-branch change or indicator implementation credit.
