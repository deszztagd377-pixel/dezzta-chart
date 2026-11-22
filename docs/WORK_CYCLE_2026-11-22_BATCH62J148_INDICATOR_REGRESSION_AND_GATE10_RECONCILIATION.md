# Work Cycle 62J-148 — Indicator regression coverage and Gate 10 reconciliation

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Starting HEAD: `1d8667fc5d6810bbde88b6a596214cdedc5fc80f`  
Test commit: `79d88d9aa5261dde3f2e31d1e742d45f461e43c2`  
Delivery target: **24 December 2026**, as explicitly corrected by the project owner.  
Cost: **ZERO COST**.  
`main`: untouched.

## 1. Scope and delivery

This cycle adds deterministic numerical regression tests for the indicator calculation kernel and reconciles the full indicator/project dashboard to the 24 December target. Runtime formulas, chart UI and provider code were not changed. This avoids claiming visual indicator completion or Stage 2 provider demand implementation without the required contracts.

## 2. Source inspection

Inspected indicator calculations/tests, shared market-indicator hook, CandlestickChart, market-data store, WebSocket supervisor, backend provider manager, Databento adapter, provider dependency range, and current indicator/project progress records.

## 3. Code/test change

Only `src/indicators/indicatorCalculations.test.ts` changed in the test-source commit.

### Test A — Wilder RSI recurrence

For closes `[1, 2, 1, 2, 1]` with period 2: initial average gain/loss are 0.5/0.5 (RSI 50); next Wilder averages are 0.75/0.25 (RSI 75); next averages are 0.375/0.625 (RSI 37.5). Expected aligned output: `[null, null, 50, 75, 37.5]`. This guards the Wilder recursive smoothing and warm-up alignment.

### Test B — fail-closed close validation

A 24-bar fixture with NaN close at source index 7 must cause `calculateIndicators` to throw `Bar 7 has a non-finite close value.` It must not emit a misleading zero, null or partial study set.

These tests strengthen numerical regression coverage only. No indicator is promoted to visually implemented or user-configurable status.

## 4. Complete indicator acceptance dashboard

| Indicator | Status | Verified foundation | Main remaining work |
|---|---|---|---|
| SMA20 | 🟨 | 20-close mean; first index 19 | Overlay, toggle, legend/value, identity/lifecycle/render tests |
| EMA20 | 🟨 | SMA seed; alpha 2/21; first index 19 | Overlay, toggle, legend/value, identity/lifecycle/render tests |
| RSI14 Wilder | 🟨 | Wilder recurrence; first index 14; exact mixed-gain regression added | 0–100 pane, 30/70 guides, toggle/legend/value, lifecycle/render |
| MACD12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, controls and render tests |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population SD; first index 19 | Three-line overlay, controls/value and render tests |
| Shared Indicator Hook | 🟨 | Exact validated snapshot calculation; null outside backend ready/degraded | Hook tests, chart binding, stale clearing, UI and lifecycle |
| Footprint | 🟧 | Synthetic educational accumulator only | User reference, reviewed blueprint, bid/ask data rights/contract, cluster renderer |
| Heatmap | 🟥 | Not implemented | User reference, depth/liquidity contract, blueprint, renderer |
| Liquidation Maps | 🟥 | Not implemented | Data provenance/methodology, blueprint, renderer |

Invariants: warm-up nulls, candle-index alignment, prefix causality, no future repaint, reject non-finite/gapped data, clear stale identity outputs. Footprint OFF must retain standard candle spacing; explicit ON alone enables spaced clusters.

## 5. WebSocket, OCI and Gate 10 status

The preceding exact HEAD `1d8667fc5d6810bbde88b6a596214cdedc5fc80f` passed all four workflows:
- Automated Tests [45016825555](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016825555)
- CodeQL [45016825571](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016825571)
- Full Git History Secret Audit [45016825575](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016825575)
- OCI ARM64 Image Readiness [45016825580](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45016825580)

Automated Tests completed frontend tests/build, Android preflight/publisher tests, backend tests, isolated Redis TLS enforcement, synthetic outbox/metrics checks, container build/smoke and image scanning. OCI ARM64 completed native build and smoke tests. This does not mean OCI cloud installation or public endpoint deployment has occurred.

The test commit and documentation commits have their own CI runs. Query the exact final branch SHA before claiming those runs pass. Gate 10 remains 0/10 external acceptance criteria formally closed; CI does not replace public WSS, owner-host persistence/recovery, real Firebase, Android WebView lifecycle, network handover or operational metrics/alert acceptance.

## 6. Stage accounting

- Stage 1 Foundation/Security/Data Integrity: 30/40 = 75% provisional 🟨.
- Stage 2 Market Data Infrastructure: not officially opened / not scored ⬜.
- Stage 3 Chart Engine & Timeframe: not scored ⬜.
- Stage 4 Indicators & Analytics: not scored ⬜.
- Stage 5 Professional UI & Interactive Tools: not scored ⬜.
- Stage 6 Hardening, Validation & APK Release: not scored ⬜.
- Overall project: **NOT SCORED**; stage weights and denominator are not approved.

## 7. Mandatory Stage 2 On-demand Market Subscription

Still OPEN. Frontend supervisor is singleton-owned; backend provider ingestion is process/configuration scoped; downstream WebSocket fan-out is not upstream provider pooling. The current Databento adapter uses a fixed symbol tuple and real SDK behavior is not verified; Databento is not an approved recurring-$0 live source for the target CME futures feed.

Do not add a detached reference counter. Implementation must control actual upstream subscribe/unsubscribe and prove: unopened catalogue symbols do not start feeds; chart open requests only its exact series; switch/close/background releases that client's demand; equivalent users share upstream work where supported; one user's disconnect cannot stop another; last-subscriber release stops demand; provider restart reconciles active subscriptions; entitlement/quota revocation fails closed.

A recurring-$0 feed with exact instrument coverage and display/redistribution rights is prerequisite. If none exists, affected instruments remain explicitly unavailable rather than silently using paid or unlicensed data.

## 8. Delivery date and risk

The requested target is **24 December 2026**. From 22 November, 32 calendar days remain after today through the target date. Full production completion cannot be guaranteed while compatible recurring-$0 market data, external hosting, public TLS, owner-host acceptance and real-device validation remain unresolved. Priority is a verifiable ZERO COST installable MVP.

## 9. ZERO COST and repository integrity

- No paid provider, account, cloud resource, production credential, payment method or deployment.
- No device/Termux action.
- No changes to `main`.
- One test-source file changed; progress dashboard and indicator ledger updated; this report added.
- Exact final CI remains pending until queried on the final documentation HEAD.
## 10. Official market-data source due diligence — recurring ZERO COST

Reviewed official CME Group and Databento material on 22 November 2026:

- CME real-time Futures & Options WebSocket API is a monthly subscription/order product with onboarding, not a verified free feed: [CME API ordering](https://www.cmegroup.com/tools-information/webhelp/data-services-portal/Content/Ordering-CME-Group-Market-Data-APIs.html).
- CME public delayed quotes are at least 10 minutes delayed, but the public webpage does not itself grant an application API or redistribution right: [CME delayed quotes](https://www.cmegroup.com/market-data/browse-data/delayed-quotes.html).
- CME's delayed Website Information REST API requires OAuth entitlement and an active Public Website (Delayed) Redistribution license; the last-trade endpoint is an hourly snapshot at minute 15, not a continuous stream: [CME REST API onboarding and availability](https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/1892122625/Distribution+Trades+and+Settlements+REST+API).
- Databento's $125 signup credits are not a sustainable live-data entitlement; its pricing page describes the usage-based tier as historical-only, Standard live access at $199/month and Plus at $1,750/month with external distribution: [Databento pricing](https://databento.com/pricing/).
- Databento's live-data guide confirms qualifying subscription plans and potential venue license fees: [Databento live-data guide](https://www.databento.tech/docs/portal/live-data).

Decision: no recurring-$0 source with verified exact CME instrument coverage and application redistribution rights has been approved. This is a bounded research result, not a universal claim that all free data is impossible. Do not scrape the public delayed quote page or use personal web display as an API. Unsupported CME instruments remain explicitly unavailable/demo until a compliant feed is verified.

