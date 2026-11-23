# DEZZTA CHART — Batch 62J-177
## Synthetic WebSocket cursor initialization and sequence-integrity hardening

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Code/test HEAD:** `c017f9ff3cc7c46b9813efe7728106d47cd8e3ac`  
**Scope:** isolated synthetic-only Worker / Durable Object proof  
**Protected branch:** `main` untouched  
**ZERO COST:** preserved  
**Exact-HEAD CI:** pending verification at documentation time; no success is claimed.

## 1. Defect found and why it mattered

The per-series Durable Object previously initialized its snapshot watermark with a separate storage `get` followed by `put`. The first synthetic update sequence is 51. If ticket issuance and that first update interleaved, the update could persist sequence 51 and the ticket path could subsequently write the older watermark 50. That would rewind the cursor and break snapshot-to-live continuity.

This was a real storage-ordering defect in the synthetic proof, not a production outage. It was fixed before extending the proof.

## 2. Engineering changes

### Atomic snapshot watermark initialization
- Added `initializeSequenceWatermark(storage, seriesKey)`.
- The read-and-initialize operation now executes inside the same Durable Object storage transaction mechanism used by sequence advancement.
- If the sequence key is absent, it initializes exactly once to watermark 50.
- If a concurrent first update already advanced the cursor to 51, initialization preserves 51 and never rewinds it.
- Invalid series identities are rejected.

### Stored cursor and incoming sequence validation
- Existing persisted cursors must be safe integers in the supported interval [50, 1,000,000,000].
- Incoming sequence values must be safe integers in [51, 1,000,000,000].
- Corrupt persisted cursor values fail closed: update acceptance returns false, and watermark initialization throws an explicit integrity error.
- Values beyond the synthetic bar generator's supported maximum are rejected before storage mutation, preventing an accepted cursor from being committed before bar construction fails.

### Regression coverage
- Added a race regression covering both operation orderings: initialization before first update, and first update before initialization.
- Extended sequence-gate tests for values above the supported maximum, unsafe integers and a corrupted stored cursor.
- Synthetic proof suite now contains **17 Node tests** (previously 16).
- Tests remain separate from Vitest discovery and use Node's built-in test runner; no package dependency was added.

## 3. Files changed in the engineering batch

| File | Change |
|---|---|
| `cloudflare/proof/worker.mjs` | Added transactional watermark initialization; fail-closed stored-cursor and input bounds |
| `cloudflare/proof/worker.node-test.mjs` | Added initialization/update race test and corrupt/out-of-range cursor assertions |

No indicator formula, chart renderer, frontend, FastAPI runtime, Redis production path, provider adapter, authentication integration or deployment configuration was changed.

## 4. Commit chain

- Atomic watermark helper and ticket-path integration: `20814331ed03717e74cdf5514c02cd169df02ef6`
- Race regression test: `e26eb094e016f5b174b39c5ad261984ce9fe1380`
- Stored cursor and sequence-bound hardening: `dd9ee442240a0aa3d3a03d12b4b28b79d8181056`
- Corrupt/out-of-range cursor regression assertions and current code/test HEAD: `c017f9ff3cc7c46b9813efe7728106d47cd8e3ac`

The exact-HEAD automated test, CodeQL, secret-history and OCI workflows must complete against the current code/test SHA before this batch receives CI acceptance credit.

## 5. Scope and proof limits

This batch strengthens the isolated synthetic proof only. It does not prove:
- actual Cloudflare Durable Object runtime behavior;
- real `WebSocketPair` handshake or browser socket lifecycle;
- forced hibernation/eviction and attachment restoration;
- same-series two-client fan-out or cross-series isolation in a real runtime;
- slow-consumer behavior, unauthenticated-socket timeout/cleanup or durable replay;
- Firebase production authentication parity;
- public HTTPS/WSS, Android WebView or external-network acceptance;
- any live market data or provider integration.

No Cloudflare deployment, account activation, paid service, domain, payment method, production secret, provider credential or external market-data feed was used. Wrangler workers.dev and preview URLs remain disabled.

## 6. Complete indicator progress ledger — unchanged by this batch

This is an engineering status ledger, not trading guidance. The synthetic WebSocket work earns **zero indicator implementation credit**.

| Indicator / subsystem | Status | Mathematical foundation and first valid output | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Arithmetic mean of 20 closes; first valid index 19 | Chart overlay, toggle, legend/current value, identity/lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha = 2/21; first valid index 19 | Overlay, toggle, legend/current value, identity/lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial mean of 14 close-to-close changes; Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD first valid index 25; EMA9 signal and histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero line, toggle/legend/latest values, lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/lifecycle/render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | Aligned multi-study output from the exact market-data snapshot; null outside backend ready/degraded state | Hook tests, chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask volume | User reference image(s), reviewed blueprint, verified data contract, cluster layout and renderer |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), reviewed blueprint, validated data contract, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render/data contract | Defensible provenance and methodology, reviewed blueprint, renderer and tests |

### Non-negotiable indicator invariants
1. Warm-up values are `null`, never fabricated zero.
2. Output remains aligned to the exact source-candle index.
3. Prefix causality: appending future candles cannot change prior outputs.
4. Invalid/non-finite bars and data gaps are not silently converted to zero.
5. Stale output clears on symbol, venue, dataset, chart identity or timeframe changes.
6. No future-candle leakage or repainting.
7. Calculation, chart rendering, interaction, lifecycle, accessibility and performance are separate acceptance dimensions.
8. Footprint OFF preserves ordinary candle spacing; only explicit ON may activate a dedicated spaced-cluster layout.
9. Footprint and Heatmap visual implementation stays blocked until user reference image(s) and a scoped blueprint review are available.
10. Aggregate indicator completion remains **NOT SCORED** because per-study weights and denominator are not approved.

## 7. Project progress dashboard

| Project area | Current indicator | Evidence / decision |
|---|---|---|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 30/40 = 75% provisional | Prior accepted score; this batch does not change it |
| Stage 2 — Market Data Infrastructure | 🟨 Synthetic-only proof increment; not scored | Atomic cursor initialization hardened; runtime integration and acceptance remain open |
| Stage 3 — Chart Engine & Timeframe | ⬜ Not scored | No new acceptance evidence |
| Stage 4 — Indicators & Analytics | ⬜ Not scored | Indicator status table above; no indicator implementation change |
| Stage 5 — Professional UI & Interactive Tools | ⬜ Not scored | No new acceptance evidence |
| Stage 6 — Hardening, Validation & APK Release | ⬜ Not scored | No new device/release acceptance |
| Gate 10 — external acceptance | 🟥 0/10 formally closed | No external acceptance gate closed by this batch |
| Overall project | **NOT SCORED** | Approved stage weights and denominator remain unavailable |
| Significant progress this batch | 🟨 Cursor-integrity defect fixed | Transactional initialization, bounds validation, 17-test suite; CI pending |

### Next technical queue (ordered)
1. Run the actual local Wrangler/Cloudflare runtime smoke with a pinned, reproducible toolchain; do not enable hosted deployment.
2. Exercise real DO WebSocket handshake and one-time ticket consumption.
3. Verify two-client same-series fan-out and strict cross-series isolation.
4. Verify attachment restoration across hibernation/rehydration.
5. Add bounded unauthenticated-socket cleanup and slow-consumer behavior tests without recurring background work.
6. Prove snapshot watermark to first live cursor continuity and define bounded replay behavior.
7. Keep production authentication, public WSS and Android acceptance as external gates, not synthetic test claims.

**Target date:** 24 December 2026. This is a planning target, not a completion guarantee.

**Decision:** cursor initialization and sequence validation are materially stronger. Stage 2 remains unscored, production WebSocket acceptance remains open, and indicator/project-wide percentages do not increase from this batch.
