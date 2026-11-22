# DEZZTA CHART — Work Cycle 62J-144
## Multi-user WebSocket ownership, client lifecycle regression and exact-HEAD repair

Date: 22 November 2026  
Branch: phase-2/market-data-foundation  
Starting HEAD: 36ae4c01f7e09e084a31b8a62f785e13e270f6ac

## 1. CI failure found and repaired

Automated Tests on the starting HEAD failed during frontend test transformation.

- src/components/AuthPanel.tsx had a malformed JSX role attribute: role="alert lacked its closing quote.
- src/components/AuthPanel.test.tsx used an over-escaped button matcher, so it did not correctly test the rendered button element.
- The transform failure caused AuthPanel and SettingsPanel suites to fail before assertions. The other 27 frontend test files passed and 255 tests passed in that run. Backend tests/build were skipped because the frontend test step failed.

Repairs committed:
- 43fb860b74544030432b51b035de288547e69cb2 — repaired JSX alert role attribute.
- ee6c21da678db11b8c1d9c6dd93c84970f915e27 — corrected the button matcher to use a real word-boundary expression.
- 78044a3b2419a6b38ecc251fa408f10b97608c54 — added explicit pagehide/pageshow lifecycle regression coverage.

No test result is claimed until the latest exact HEAD completes CI.

## 2. Multi-user server/client lifecycle — source-backed finding

The intended ownership model is:

- One independently hosted backend process serves many app installations.
- Every app installation/user creates its own authenticated WebSocket connection.
- Closing one app closes only that client's connection and removes only its subscription/connection lease.
- Other users' WebSocket connections and subscriptions remain active.
- Backend process lifetime is independent of any single mobile app's foreground/background state.
- When the last client disconnects, a future global-idle policy may pause upstream provider ingestion or other optional work after a grace period. It must not be implemented as "the first user's app closes, stop the whole backend."

Existing source evidence:
- backend/app/main.py assigns a unique connection_id for every WebSocket and reserves/releases that connection independently through the shared guard.
- Authenticated identity is derived from a consumed one-time ticket; clients cannot select another account subject.
- Each connection authorizes the exact canonical instrument against that principal's entitlement.
- backend/app/ohlcv_stream.py assigns a unique stream_id and bounded queue per subscription.
- The WebSocket route's finally block unsubscribes only that connection's stream and releases only that connection's lease.
- A slow client that fills its queue is closed/resnapshot-required; it does not block or silently skip updates for other subscribers.
- Lifespan-managed publisher/replica workers are application-service resources, not children of a mobile WebSocket connection.

Important limitation:
- Source audit confirms per-connection isolation and that one disconnect does not shut down the FastAPI service.
- A global "zero connected users → pause provider feed after grace period; first new user → resume provider feed" controller is NOT yet implemented or accepted.
- Provider live-feed connection remains separately disabled/unprovisioned by default. No real provider feed is claimed.
- In-memory fan-out is process-local; cross-process distribution requires the explicitly configured Redis relay. The relay is opt-in and still has external snapshot receipt/host acceptance gates.
- A sleeping/free host may suspend the whole service independently of user count. That is a hosting-platform lifecycle, not per-user WebSocket lifecycle.

## 3. Client lifecycle acceptance

Added a focused regression test in src/components/CandlestickChart.lifecycle.test.tsx:
- Initial foreground connection creates one supervisor.
- pagehide stops the current supervisor and clears verified stream state.
- pageshow while online/visible creates a fresh supervisor.
- Unmount stops the replacement supervisor.
- Existing offline/online, visibility, rapid-transition and unmount tests remain intact.

The browser test is not physical Android WebView evidence. Force-kill, process recreation, network handover, OS background suspension and real WSS remain external Gate 36 acceptance.

## 4. Zero-cost hosting interpretation

The app's Google sign-in is separate from the hosting provider's account registration. A hosting provider that offers "Sign in with Google" may still require a payment card or identity verification; do not infer cardless signup from Google OAuth.

- Keep backend provider-neutral and container-portable.
- Cloudflare Workers/Durable Objects remain an architectural candidate, not a drop-in deployment for the current Python/FastAPI service. A TypeScript/edge adapter would need protocol-conformance tests before replacing or fronting the current implementation.
- Render Free remains suitable only for a limited sleeping proof-of-concept, not a durable always-on market-data origin; ephemeral storage must never hold authoritative Redis/SQLite state.
- OCI remains blocked by card-based identity verification in the current user situation.
- No account, deployment, paid resource, domain, production credential or payment method was created.

## 5. Indicator progress — complete ledger

No indicator formula, numeric kernel, hook, renderer or indicator UI was changed. Therefore this work cycle receives zero indicator implementation credit.

| Indicator/component | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 | Flat/monotonic/zero-loss edge cases, chart integration and lifecycle |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Numerical edge cases, chart integration, identity invalidation and lifecycle |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Variance/flat-series edge cases, chart integration and lifecycle |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output | Full chart integration, visible settings/legend/current values and stale-output clearing |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, real licensed bid/ask data contract, cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted runtime/render implementation | User reference image(s), reviewed blueprint, validated depth/liquidity data contract and renderer |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance/contract, reviewed design, renderer and tests |

Shared invariants:
- Warm-up values are null, never fabricated zero.
- Outputs align exactly to source candle indices.
- Prefix causality: appending future candles cannot change prior values.
- Invalid/missing/gapped bars are not silently converted to zero.
- Stale outputs clear on symbol, venue, dataset, chart and timeframe identity changes.
- Formula correctness, rendering, interaction, lifecycle, accessibility and performance are separate acceptance dimensions.
- Footprint OFF preserves normal candle spacing; explicit ON alone enables the dedicated spaced-cluster layout.
- Footprint and Heatmap visual implementation remains blocked until the user supplies reference image(s) and reviews the scoped blueprint.
- No aggregate indicator completion percentage is published without approved weights and denominator.

## 6. Project progress and gate status

Legend: 🟩 accepted; 🟨 partial/provisional; 🟧 prototype; 🟥 not implemented; ⬜ not scored/not opened.

| Official stage | Progress | Status |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 |
| 2. Market Data Infrastructure | Not scored / not officially opened | ⬜ |
| 3. Chart Engine & Timeframe | Not scored / not officially opened | ⬜ |
| 4. Indicators & Analytics | Not scored / not officially opened | ⬜ |
| 5. Professional UI & Interactive Tools | Not scored / not officially opened | ⬜ |
| 6. Hardening, Validation & APK Release | Not scored / not officially opened | ⬜ |

Overall project: NOT SCORED; approved stage weights and total denominator are not available. Stage 1's provisional 75% is not an overall project percentage.

Gate 10: 0/10 external criteria formally closed.  
WebSocket Gate 25: OPEN — durable authenticated snapshot-installation receipt, key/attestation policy and owner-host recovery.  
WebSocket Gate 36: OPEN — public HTTPS/WSS, real Firebase/entitlement E2E and physical Android/browser lifecycle acceptance.  
WebSocket Gate 38: OPEN — owner-host durable metrics, backup/retention, alert and recovery evidence.  
Gates 8, 20, 30, 31, 34, 35 and 39 remain open pending their own acceptance evidence.

IP3S/IPS35: PENDING exact-HEAD CI. No cycle score is assigned until the final source/test HEAD has completed its relevant checks.

## 7. Cost and integrity

- ZERO COST preserved.
- No main changes; active branch remains phase-2/market-data-foundation.
- No production hosting, provider feed, account, domain, payment method or credentials created.
- No device/Termux operation.
- No paid dependency or schema migration.
- Google-only app sign-in UI does not imply Google-only hosting signup.
