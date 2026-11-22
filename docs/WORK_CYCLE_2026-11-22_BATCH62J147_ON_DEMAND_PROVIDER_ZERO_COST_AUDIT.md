# Work Cycle 62J-147 — On-demand provider capability and zero-cost feasibility audit

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Pre-cycle documentation HEAD: `0004fd4bbc1a768079e9474aa0bbdd1b954cbc45`  
Scope: Stage 2 On-demand Market Data Subscription, Stage 1 WebSocket prerequisites, provider capability, recurring-zero-cost feasibility and indicator reconciliation.  
Cost: **ZERO COST**  
Runtime changes: **none**  
`main`: untouched.

## 1. Goal and delivery

The goal was to move the mandatory On-demand requirement from a broad product statement toward an implementable provider contract without introducing unverified SDK calls or a false zero-cost assumption.

Delivered:
- Extended `docs/ADR_ON_DEMAND_MARKET_DATA_SUBSCRIPTIONS.md` with a provider capability and zero-cost feasibility audit.
- Updated `docs/INDICATOR_PROGRESS_LEDGER.md` to preserve the full indicator audit as the canonical formula/acceptance reference.
- This work-cycle report records exact source findings, blockers, evidence and next implementation gates.

## 2. Files inspected

- `backend/app/databento_sources.py`
- `backend/app/provider.py`
- `backend/app/main.py`
- `backend/app/ohlcv_stream.py`
- `backend/requirements.txt`
- `backend/tests/test_databento_sources.py`
- `backend/tests/test_provider.py`
- `src/components/CandlestickChart.tsx`
- `src/services/ohlcvStreamSupervisor.ts`
- `src/services/ohlcvWebSocketClient.ts`
- `docs/FREE_MARKET_DATA_SOURCE_POLICY.md`
- `docs/MARKET_DATA_SOURCE_INVENTORY_ZERO_COST.md`
- `docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md`

## 3. Confirmed implementation boundaries

### Client

- The chart component starts a stream supervisor for its selected exact series and ties the owner to visibility/network lifecycle.
- The supervisor is module-singleton because it writes to a singleton market-data store. A newly selected chart stops the prior supervisor.
- The WebSocket client authenticates with a short-lived ticket and subscribes to one exact canonical series.
- Therefore the current frontend supports a single active owner path, not an independently managed set of simultaneous chart panels.

### WebSocket backend

- `OhlcvStreamHub` allocates per-client stream IDs and bounded queues, then fans validated events out to subscriptions matching exact series identity.
- This is downstream WebSocket fan-out. It is not evidence of provider upstream pooling, upstream dynamic subscribe/unsubscribe, or upstream reference counting.
- Existing real-TLS test evidence proves ticket-authenticated WSS, renewal and client isolation behavior; it does not prove chart-driven provider demand.

### Provider

- `ProviderManager.start()` starts its ingestion consumer and configured live-source supervisor as part of application process lifecycle.
- `DatabentoLiveSource` creates a Live client and subscribes once to a fixed constructor-provided symbol list.
- It exposes stop, but no verified dynamic symbol acquire/release contract is wired to active chart demand.
- The adapter explicitly labels real SDK method signatures/behavior unverified. Its test uses a fake SDK object.
- Backend dependency is `databento>=0.88,<1`, which is not an exact SDK pin.

## 4. ZERO COST feasibility finding

The repository's own source policy excludes Databento from recurring-$0 baseline because live access requires a paid subscription and introductory credits are finite. On-demand reduces avoidable use but does not change the upstream data entitlement's price.

The current public candidate inventory is not a drop-in replacement for the existing CME futures instrument target. A source must match instrument universe, venue, freshness, data family, symbol identity and display/redistribution rights. No feed is approved by this work cycle.

No API key, account, provider session, deployment, cloud resource or paid entitlement was created or used.

## 5. Engineering decision

No runtime code was changed. It would be unsafe to add a local reference-count class and claim success while:
- the provider adapter still ingests a fixed configured symbol list;
- dynamic subscription semantics of the SDK are unverified;
- a sustainable recurring-$0 source for the target futures universe is not approved;
- the current frontend store/supervisor is singleton-owned.

A disconnected helper would create dead code and false progress. The correct next step is to verify provider capability and source entitlement, then design a coordinator that actually controls upstream state.

## 6. Required Stage 2 acceptance work

1. Approve a recurring-$0 source/feed with exact product coverage and display/redistribution rights. If no suitable source exists, mark unsupported series unavailable rather than silently using paid data.
2. Pin one exact SDK/provider adapter version in a reproducible lockfile or dependency constraint approved for the repository.
3. Verify dynamic add/remove behavior and reconnect semantics without a production key or paid feed. Document whether updates are live, multiplexed, restart-required or unsupported.
4. Define canonical upstream identity and a provider capability interface.
5. Implement an idempotent demand coordinator with per-series subscriber ownership and reference counts.
6. Connect client chart open/switch/close/background to per-client subscribe/unsubscribe.
7. Resolve singleton chart-store ownership before supporting multiple simultaneous chart panels; preserve the current single-chart behavior until the multi-chart design is accepted.
8. Test two users on one series, two series on one provider, one-user disconnect, last-subscriber release, provider restart, reconnect reconciliation, inactive catalogue, quota exhaustion and entitlement revocation.
9. Measure client data and host budgets separately. No numerical savings or free-tier capacity claim without a reproducible workload and actual provider plan limits.

## 7. Exact-HEAD CI evidence

The pre-cycle documentation HEAD `0004fd4bbc1a768079e9474aa0bbdd1b954cbc45` completed all four workflows successfully:

- Automated Tests [45016264628](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016264628): **SUCCESS**.
- CodeQL [45016264675](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016264675): **SUCCESS**.
- Full Git History Secret Audit [45016264627](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016264627): **SUCCESS**.
- OCI ARM64 Image Readiness [45016264696](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016264696): **SUCCESS**.

Automated Tests included frontend unit tests/build, backend tests, isolated Redis TLS fixture, synthetic SQLite benchmarks, backend image build, persistent-volume/shared-Redis-guard smoke and image scan. These are exact-head CI checks, not public-host/provider/device acceptance.

The new documentation commits are later HEADs. Their workflows must be checked independently before this report can claim exact-final-HEAD CI acceptance.

## 8. Indicator progress — complete status

| Indicator | Status | Mathematical/data foundation | Remaining |
|---|---|---|---|
| SMA20 | 🟨 | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render tests |
| EMA20 | 🟨 | SMA seed; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render tests |
| RSI14 Wilder | 🟨 | First 14 close-to-close changes; Wilder smoothing; first valid index 14 | 0–100 pane, 30/70 guides, toggle/legend and lifecycle/render tests |
| MACD12/26/9 | 🟨 | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Dedicated pane, lines/histogram/zero guide, toggle/legend and tests |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population SD; first valid index 19 | Three-line overlay, toggle/values, identity/lifecycle/render tests |
| Shared Indicator Hook | 🟨 | Exact backend snapshot/aligned calculations | Hook tests, chart binding, stale clearing and renderer integration |
| Footprint | 🟧 | Synthetic educational accumulator only | User reference image(s), reviewed blueprint, valid bid/ask source contract and cluster acceptance |
| Heatmap | 🟥 | Not implemented | Reference image(s), validated depth/liquidity contract, blueprint and renderer |
| Liquidation Maps | 🟥 | Not implemented | Valid data provenance/calculation contract, reviewed blueprint and renderer |

No indicator code or test was changed. No indicator implementation credit is awarded. Preserve warm-up nulls, candle-index alignment, prefix causality/no future repaint, invalid/gapped-bar rejection, stale-output clearing and Footprint OFF standard candle spacing. Footprint/Heatmap visual work remains reference-gated. Detailed formula and numerical acceptance audit: `docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md`.

## 9. Project and Gate accounting

| Stage | Status |
|---|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional 🟨 |
| 2. Market Data Infrastructure | Not officially opened / not scored ⬜ |
| 3. Chart Engine & Timeframe | Not scored ⬜ |
| 4. Indicators & Analytics | Not scored ⬜ |
| 5. Professional UI & Interactive Tools | Not scored ⬜ |
| 6. Hardening, Validation & APK Release | Not scored ⬜ |

Overall project: **NOT SCORED**. Stage weights and denominator are not approved. Gate 10 remains **0/10 external criteria formally closed**. Relevant open gates include 25 (snapshot provenance/owner-host recovery), 36 (public WSS/live Firebase/Android lifecycle), and 38 (durable operational metrics/alert/recovery), plus the other previously recorded external criteria.

The Stage 2 on-demand subscription requirement remains mandatory and open. This work cycle does not open Stage 2 or award Stage 2 progress.

## 10. Deadline risk — 22 November to 31 December 2026

There are 39 calendar days after 22 November through 31 December inclusive. Completing every stage, external acceptance, market-data licensing, public hosting, Android device lifecycle and full indicator UI within that window cannot be guaranteed, especially while the zero-cost source for the target instruments is unresolved.

The correct execution strategy is to prioritize a verified, installable, zero-cost MVP and explicitly defer unsupported or unlicensed data families rather than claim a complete professional trading platform without evidence.

## 11. Scope and cost statement

ZERO COST. Documentation only. No runtime source, test source, schema, dependency, provider account, API credential, production service, deployment, payment method, Android device/Termux operation or main branch change.
