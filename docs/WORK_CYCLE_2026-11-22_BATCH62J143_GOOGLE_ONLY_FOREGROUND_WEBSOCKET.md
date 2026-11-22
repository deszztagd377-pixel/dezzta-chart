# DEZZTA CHART — Work Cycle 62J-143
## Google-only sign-in surface and foreground-only WebSocket lifecycle

Date: 22 November 2026
Branch: `phase-2/market-data-foundation`
Source baseline: `b1a89fd68ef5f1d9c76087c5f5c2ccd70fe8d985`
Source changes:
- `cf836c5fb810b6597b6d1aa33d393a70cd70a033` — Google-only sign-in UI.
- `b184cb869dcca6908df2256a80b6684f8eda95a2` — Google-only UI regression tests.
- `57413314fbaf9f7330250cfa750e2540287ad474` — corrected button matcher in test.
- `bd83d40bdf58262922462d67cde3da6c1f4a4387` — explicit pagehide pause/pageshow resume wiring.

## 1. Approved operating behavior

The product owner confirmed the desired runtime behavior:
- Zero-cost operation; no paid hosting, subscriptions, paid APIs or surprise billing.
- Sign-in UI exposes Google account sign-in only.
- When the app/page goes to the background or closes normally, stop the market-data WebSocket and its reconnect lifecycle. No background keep-alive is required.
- When the app/page returns to the foreground and network is available, create a new authenticated supervisor, obtain fresh identity/ticket credentials, and recover using a fresh validated snapshot (or the existing protocol's safe replay path when a cursor is available).
- The chart must not present stale/demo data as verified live data.
- The application is not required to keep collecting market data while closed.

This is a foreground-only client policy, not a promise that every operating system emits a graceful shutdown callback. If the process is force-killed, the OS/network stack closes its socket; a new app process starts a new authenticated session on next launch.

## 2. Source changes

### Google-only sign-in surface

`src/components/AuthPanel.tsx` now presents only:
- Continue with Google when signed out.
- Account identity and Sign out when signed in.
- Explicit loading/unconfigured/error states.

Email/password fields and account-creation actions are no longer exposed in the application sign-in panel. Firebase AuthProvider still contains legacy email/password helper methods and Firebase project configuration may still have that provider enabled; this UI change does not claim that the Firebase project has disabled the provider at its console level. Google provider must be enabled and the app's authorized domains/configuration must be correct.

Regression tests in `src/components/AuthPanel.test.tsx` assert that Google sign-in is the only sign-in action and that email/password inputs are absent. A malformed test matcher was corrected before the latest source HEAD.

### Foreground-only WebSocket lifecycle

`src/components/CandlestickChart.tsx` already stopped the stream while hidden/offline and recreated a supervisor on visibility/online restoration. This cycle adds explicit:
- `pagehide` → force lifecycle state to hidden, causing supervisor cleanup and socket close.
- `pageshow` → resynchronize visibility/network state; if visible and online, the chart lifecycle recreates the supervisor.

Existing `src/services/ohlcvStreamLifecycle.ts` policy remains: connect only when online AND visible. Existing supervisor cleanup cancels pending Firebase token requests, clears reconnect timers, closes the socket, and prevents stale owner cleanup from clearing a replacement supervisor's store.

Reconnect obtains a fresh Firebase ID token and a new short-lived, single-use WebSocket ticket. On relaunch, a fresh snapshot establishes current chart state; no background queue or persistent always-on client process is required.

## 3. Safety and correctness boundaries

- Google identity is not market-data entitlement. Backend verifies Firebase identity and separately checks the exact instrument/series entitlement.
- Firebase ID token is sent only over HTTPS to ticket exchange; the WebSocket uses a short-lived ticket, never a long-lived ID token in URL parameters.
- Closing the app pauses client transport; it does not stop any independently deployed backend/provider process.
- No market-data provider license, live CME feed entitlement, production WSS host, Firebase Admin secret, Redis host, or provider credentials are provisioned by this work cycle.
- No API key, service-account JSON, private key, or payment credential was added.
- No cloud account or deployment was created. Any cloud account must be owned/managed by a parent/guardian; no cardless signup guarantee is made.
- No paid service or unexpected billing path is introduced.

## 4. Exact-HEAD CI

Latest source HEAD at documentation time: `bd83d40bdf58262922462d67cde3da6c1f4a4387`.

Runs on this exact source HEAD:
- Automated Tests [45002751143](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45002751143): queued at documentation time.
- CodeQL [45002751165](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45002751165): queued.
- Full Git History Secret Audit [45002751245](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45002751245): in progress.
- OCI ARM64 readiness [45002751235](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45002751235): in progress.
- Android APK build [45002751178](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45002751178): in progress.

No exact-HEAD CI success is claimed until these runs complete. An earlier APK workflow on a superseded commit failed and is not used as evidence for this HEAD.

## 5. Indicator progress — no implementation changes

No indicator formula, numerical kernel, shared hook, chart renderer or indicator-specific tests changed. Therefore indicator implementation progress receives no credit in this work cycle.

| Indicator/component | State | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 | 20-close arithmetic mean; first valid index 19 | Numeric edge cases, chart integration, lifecycle and performance |
| EMA20 | 🟨 | SMA seed; alpha 2/21; first valid index 19 | Numeric edge cases, chart integration, lifecycle and performance |
| RSI14 Wilder | 🟨 | Wilder smoothing; first valid index 14 | Flat/monotonic/zero-loss edge cases and chart integration |
| MACD12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Edge cases, chart integration and lifecycle |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population SD; first valid index 19 | Variance edge cases, chart integration and lifecycle |
| Shared Indicator Hook | 🟨 | Backend snapshot/aligned calculation output | Full chart integration, identity invalidation and UI settings |
| Footprint | 🟧 | Synthetic educational accumulator only | Not exchange-native bid/ask truth; user reference image + reviewed blueprint required |
| Heatmap | 🟥 | No accepted implementation | Reference image, data contract, blueprint and rendering |
| Liquidation Maps | 🟥 | No accepted implementation | Data provenance, data contract, blueprint and rendering |

Shared invariants remain mandatory:
- Warm-up output is null, never fabricated zero.
- Output index matches source candle index.
- Prefix causality: appending future candles cannot change prior values.
- Invalid/gapped source bars are not silently converted to zero.
- Stale values clear when symbol, venue, dataset, chart or timeframe changes.
- Footprint OFF retains ordinary candle spacing; only explicit ON enables spaced cluster layout.
- Footprint and Heatmap visuals remain blocked pending user references and blueprint review.
- Aggregate indicator percentage remains NOT SCORED because weights/denominator are not approved.

## 6. Project progress and gates

| Stage | Status |
|---|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional 🟨 |
| 2. Market Data Infrastructure | Not scored / not officially opened ⬜ |
| 3. Chart Engine & Timeframe | Not scored / not officially opened ⬜ |
| 4. Indicators & Analytics | Not scored / not officially opened ⬜ |
| 5. Professional UI & Interactive Tools | Not scored / not officially opened ⬜ |
| 6. Hardening, Validation & APK Release | Not scored / not officially opened ⬜ |

Gate 10 remains **0/10 external criteria formally closed**. Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain open pending their own evidence. Overall project remains **NOT SCORED**; no aggregate percentage is invented. IPS35 is pending exact-HEAD CI.

## 7. Cost, branch and device integrity

- ZERO COST: no paid services, cloud resource, deployment, domain, payment method or subscription.
- Branch remains `phase-2/market-data-foundation`; `main` untouched.
- No device/Termux commands or operations.
- No APK installation or sideload performed.
- No credentials requested or committed.

**Outcome:** Google-only sign-in is now the sole visible sign-in route; the WebSocket explicitly pauses on pagehide and resumes on pageshow when online/visible. Exact-HEAD CI is pending; production hosting and live market-data remain external gates.
