# WORK CYCLE 62J-152 — Exact-series WebSocket isolation regression

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Target: 24 December 2026  
ZERO COST: enforced  
Main: untouched

## Change

Added one regression test to `backend/tests/test_ohlcv_stream.py`:

`test_stream_hub_rejects_updates_when_any_series_identity_dimension_differs`

The test registers a subscriber for one exact series and publishes ten deliberately mismatched bars. It verifies that none enters the subscriber queue and that the stream watermark remains unchanged.

The ten mismatch dimensions are:
1. dataset;
2. publisher ID;
3. instrument ID/raw symbol;
4. raw symbol;
5. timeframe;
6. provider;
7. series type;
8. bucket policy;
9. calendar ID;
10. calendar version.

This strengthens the downstream routing boundary: an authenticated subscriber for one canonical series must not receive an update for a different series. The test uses `dataclasses.replace` on the existing valid OHLCV fixture and does not require provider credentials, network access, paid services, or production data.

## Why this is safe

- No production runtime code changed.
- No provider SDK behavior is assumed.
- No new dependency was introduced.
- The test checks the existing `OhlcvStreamHub.identity_for()` contract against the exact identity tuple already used by subscription registration and publish routing.
- It complements, rather than replaces, the existing same-series two-subscriber disconnect test, provider isolation test, bucket-policy isolation test, replay boundary tests, and exact-series filter test.

## Expected acceptance

- All ten mismatched updates are rejected by routing (no queue delivery).
- Subscriber watermark remains zero.
- Unsubscribe leaves subscriber count at zero.
- Existing backend and full CI suites remain green.

The test is repository-level routing evidence only. It does not prove upstream provider pooling, demand-driven subscribe/unsubscribe, or a licensed recurring-$0 CME feed.

## Commit

Code/test commit: `4c8658c99a85b07327455e1f4bb63b786bdc26d2`

Changed file:
- `backend/tests/test_ohlcv_stream.py` — one new exact-series identity regression test.

No deletions. No production files changed.

## WebSocket evidence boundary

Already present:
- per-client bounded queues and exact-series fan-out;
- provider and series-type isolation;
- bucket-policy isolation;
- same-series subscriber disconnect isolation;
- replay/live boundary and overflow fail-closed tests.

Still open:
- frontend singleton supervisor versus multi-chart ownership;
- backend process-scoped provider lifecycle versus chart-demand lifecycle;
- verified dynamic upstream provider capability;
- actual shared-upstream reference counting and reconnect reconciliation;
- public hostname/TLS/WSS and real Android lifecycle acceptance.

Do not award Stage 2 completion for downstream WebSocket tests alone.

## Full indicator progress ledger

No indicator formulas, hooks, renderers, or indicator tests changed in this batch. Indicator implementation credit: zero.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; mixed gain/loss regression | 0–100 pane, 30/70 guides, toggle/legend/latest value and rendering |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Pane, MACD/signal lines, histogram, zero guide, controls and rendering |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, controls, values and rendering |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot and candle-aligned calculations | Hook tests, chart binding, stale clearing, renderer integration |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator | User visual references, reviewed blueprint, valid bid/ask source contract, cluster renderer |
| Heatmap | 🟥 Not implemented | No accepted runtime depth renderer | User references, validated depth/liquidity contract, blueprint and renderer |
| Liquidation Maps | 🟥 Not implemented | No accepted data/provenance calculation contract | Defensible provenance, calculation contract, blueprint and renderer |

Mandatory invariants:
- warm-up values remain null, not zero;
- output aligns exactly with candle indices;
- prefix causality/no future-candle repaint;
- invalid or gapped bars are rejected rather than silently converted to zero;
- stale output is cleared on symbol, venue, dataset, chart, and timeframe changes;
- Footprint OFF retains normal candle spacing; explicit ON alone activates cluster spacing;
- Footprint and Heatmap visual implementation remains gated on user-provided references and a reviewed blueprint.

## Project stage and gate accounting

- Stage 1 Foundation, Security & Data Integrity: 30/40 = 75% provisional 🟨.
- Stage 2 Market Data Infrastructure: not scored; on-demand provider integration remains open ⬜.
- Stage 3 Chart Engine & Timeframe: not scored ⬜.
- Stage 4 Indicators & Analytics: not scored ⬜.
- Stage 5 Professional UI & Interactive Tools: not scored ⬜.
- Stage 6 Hardening, Validation & APK Release: not scored ⬜.
- Overall project: NOT SCORED; approved weights and denominator are not defined.
- Gate 10: 0/10 external criteria formally closed.

## ZERO COST and release boundary

No paid service, provider plan, account, credential, deployment, payment method, cloud resource, or device operation was introduced. OCI ARM64 CI remains image/build/smoke evidence only, not a provisioned VM or public endpoint.

The recurring-$0 exact-instrument data and redistribution-rights gap remains unresolved. Unsupported live series must remain clearly unavailable/demo. The 24 December 2026 date remains the project delivery target, not a guarantee that external prerequisites will become available.

## CI

The new test commit triggers exact-HEAD workflows. Do not mark this batch CI-verified until Automated Tests, CodeQL, Secret Audit, and OCI ARM64 all finish successfully on the resulting HEAD. If any fail, inspect the exact failing job and fix the root cause before declaring completion.
