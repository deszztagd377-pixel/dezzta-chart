# Work cycle — 24 November 2026 — Batch 62J-192: Replay boundary regression and indicator ledger

**Branch:** `phase-2/market-data-foundation`  
**Previous checkpoint:** `999d2b34fb83e918198460fd795785d5b88758dc`  
**Source/test commit:** `b361cc9e18c5f152a2284f18b165b7a17700938f`  
**ZERO COST:** maintained. No paid data, hosting, services, provider activation, publication, or device operation. Protected `main` untouched.

## 1. CI reconciliation before work

For previous checkpoint `999d2b34...`:
- Automated Tests `45306613371`: RUNNING at initial inspection; frontend tests and frontend build had passed, backend dependency installation was still running.
- CodeQL `45306613394`: SUCCESS.
- OCI ARM64 `45306613435`: SUCCESS.
- Full Git History Secret Audit `45306613369`: SUCCESS.

The previous commit's CI was not represented as fully green. Automated Tests was still executing backend dependency setup, Redis TLS fixture, backend tests, benchmark/audit and image stages.

## 2. Replay boundary test work

Added three focused tests to `backend/tests/test_ohlcv_redis_replay.py`:

1. **Retention-floor inclusivity:** verifies the precise boundary rule with `after_cursor = floor - 1` (resnapshot required), `after_cursor = floor` (valid), and `after_cursor = floor + 1` (valid). The accepted cases replay the remaining contiguous events through the fixed checkpoint watermark.
2. **Malformed checkpoint matrix:** rejects bool-as-int, negative applied cursor, missing retention-floor field, floor above applied cursor, and negative floor before any Redis read.
3. **Exact scan-limit page transition:** verifies a page containing exactly `scan_limit` entries advertises `has_more`, advances to the final scanned cursor, and the next page continues without a gap or duplicate.

These are regression tests, not a claim that the CI execution has passed. Exact-HEAD workflow verification is required before green status.

## 3. Code-path findings and safety assessment

The inspected implementation in `backend/app/ohlcv_redis_replay.py` already enforces:
- strict integer validation using `type(value) is int` (so booleans do not pass as integers);
- `0 <= retention_floor <= applied_cursor`;
- strict expiry only when `after_cursor < retention_floor`, making equality valid;
- fixed checkpoint `applied_cursor` watermark;
- global cursor scanning across unrelated series;
- contiguous cursor enforcement and fail-closed resnapshot on missing/trimmed/corrupt history;
- all-or-resnapshot behavior when event or scan caps are exceeded.

No runtime change was justified by this test-first review. This avoids altering correct production behavior merely to increase diff size.

## 4. Indicator progress ledger — complete current evidence

This batch changes no indicator runtime, formulas, hook, chart renderer, controls, panes, toggles, or indicator-specific calculation behavior. **Indicator implementation credit for Batch 62J-192: zero.**

| Indicator / subsystem | Status | Verified foundation | Required work for acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; warm-up nulls; aligned output | Visible candlestick overlay, toggle, legend/latest value, exact-identity invalidation, lifecycle and render/performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha = 2/21; first valid index 19 | Visible overlay, toggle, legend/latest value, identity invalidation, lifecycle and render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change average followed by Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | EMA12/EMA26; MACD line first valid index 25; signal and histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values and lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close middle mean ± 2 population standard deviations; first valid index 19 | Upper/middle/lower chart overlay, toggle, latest values, identity invalidation, lifecycle and render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | `useMarketIndicators()` consumes the validated shared backend OHLCV snapshot; trust-state suppression, aligned calculations, immutable-revision regression coverage | Actual chart binding, visible settings/legend, stale-output clearing across every identity/timeframe transition, accessibility and performance acceptance |
| Footprint | 🟧 Synthetic prototype only | Offline educational accumulator; explicitly not exchange-native bid/ask/order-flow truth | Owner reference image, reviewed scoped blueprint, verified bid/ask source contract, dedicated cluster renderer and acceptance tests |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer verified | Owner reference image, validated depth/liquidity source contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime or renderer verified | Defensible provenance/calculation contract, reviewed blueprint, renderer and tests |

### Indicator data-integrity rules

- All studies consume the same validated OHLCV series as the selected canonical instrument and timeframe.
- No separate indicator price fetch, symbol substitution, or silent DEMO fallback.
- DEMO, loading, unavailable, and error states produce no live indicator values.
- Warm-up values remain null; no fabricated leading values.
- Outputs remain aligned to source candle indexes.
- Prefix causality must hold: appending future bars must not change already-finalized historical outputs.
- Invalid, non-finite, malformed, or discontinuous input must fail closed or return the explicitly documented unavailable state.
- Revisions must invalidate/recompute affected outputs; stale results must not survive instrument/timeframe identity changes.
- Visible completion is separate from calculation-foundation completion. Current chart UI does not yet wire the hook into visible indicator controls, panes, overlays, or legends.
- Footprint OFF must preserve standard candlestick spacing. Only explicit Footprint ON may activate a dedicated spaced-candle/cluster layout.
- Footprint and Heatmap visual work remains blocked until the user supplies the respective reference image(s) and reviews the scoped blueprint. No visual implementation is started without those inputs.

### Indicator score

**Aggregate indicator progress: NOT SCORED.** No approved indicator weighting/acceptance denominator exists. Counting six foundation rows as six completed visible indicators would be inaccurate. The three non-foundation studies are not implementation-ready. The ledger records evidence and remaining acceptance, not an invented percentage.

## 5. Project progress accounting

| Area | Evidence-based status |
|---|---|
| Stage 1 | 30/40 acceptance criteria = **75% provisional**; Batch 62J-192 adds no Stage 1 closure |
| Stages 2–6 | Not scored |
| Gate 10 | 0/10 formally closed; external acceptance evidence remains outstanding |
| Overall project | **NOT SCORED**; approved weighted denominator unavailable |
| WebSocket replay/reconnect | Strong code/test foundation; this batch adds three boundary-focused regression tests, pending exact-HEAD CI |
| Indicator aggregate | **NOT SCORED** |
| Delivery target | 24 December 2026, planning target only; not a completion guarantee |
| Cost | ZERO COST |

No weighted project percentage is fabricated. The historical 75% is Stage 1 only, not the entire product.

## 6. Verification and next work

The source/test commit `b361cc9e...` triggers a new exact-HEAD CI cycle. All new tests remain pending CI until the run reports completion. CI from an earlier SHA does not certify this commit.

Next independent work order:
1. Add deterministic replay/live atomic handoff interleaving coverage at the snapshot/subscription boundary.
2. Add queue saturation during replay handoff and prove no silent event loss.
3. Add concurrent subscriber isolation tests for distinct canonical series.
4. Reconcile the exact-HEAD CI results and investigate any failing job from its logs before changing code.
5. Keep the indicator UI gate closed until the scoped blueprint and required visual references are available.

**No user-side code or document repair is requested.**
