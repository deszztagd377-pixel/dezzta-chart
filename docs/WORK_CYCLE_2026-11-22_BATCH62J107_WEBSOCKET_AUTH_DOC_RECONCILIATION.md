# Batch 62J-107 — WebSocket authentication documentation reconciliation

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Scope: Gate 20 / Gate 25 / Gate 36 documentation accuracy; indicator ledger reconciliation  
Cost: ZERO COST

## 1. Defect found and corrected

The WebSocket section in `backend/README.md` was stale. It said the client must send a Firebase ID token as its first WebSocket frame and that the short-lived WebSocket-ticket exchange was not implemented.

The current source contradicts that description:

- `POST /v1/auth/websocket-ticket` authenticates a Firebase Bearer token and issues a purpose-bound ticket.
- Ticket TTL is 90 seconds.
- The WebSocket production handshake consumes the ticket from the first `auth` frame.
- The ticket store is shared through the configured shared guard; the in-memory fallback is process-local and is not production multi-instance storage.
- Direct Firebase-token authentication in the WebSocket frame is allowed only outside production; `APP_ENV=production` rejects that fallback.
- Repository tests cover digest-keyed ticket storage, NX/single-use semantics, TTL, concurrent consumption, invalid/expired tickets, store outage, cross-account renewal rejection and entitlement recheck.

The README now describes the HTTP ticket exchange and WebSocket ticket handshake, separates local development from production WSS URL shape, and no longer claims that ticket exchange is unimplemented.

## 2. Production acceptance is still open

This correction is documentation-only. It does not prove production activation or close any gate.

| Area | Repository evidence | Remaining production acceptance |
|---|---|---|
| Gate 20 — Firebase | Token verifier, revocation-aware identity path, ticket issuance and entitlement checks exist; failure matrix is tested | Real Firebase project signed-token, revocation and entitlement E2E |
| Gate 25 — Redis | Shared guard/ticket store and Redis relay primitives are implemented; CI Redis ACL/AOF and multi-process relay scenarios exist | Owner-host `rediss://`, real ACL identities, secret rotation, persistent volume, failover/recovery, verified snapshot distribution/receipts |
| Gate 36 — WebSocket | Client/server lifecycle, one-use ticket, replay, heartbeat, renewal and reconnect behavior have repository tests; two-process CI fan-out and controlled TCP interruption/recovery are documented | Public HTTPS/WSS hostname, valid TLS/SAN/chain, reverse-proxy Upgrade/timeouts, real public WSS E2E, browser and Android WebView foreground/background/network-switch acceptance |

CI evidence remains tied to its recorded source/test commit and is not a fresh run for this docs-only batch. No production host, Redis credentials, Firebase credentials, or device session is assumed.

## 3. Indicator progress — complete current matrix

No indicator calculation, data contract, shared hook, chart renderer, UI, or indicator test changed in this batch. No indicator progress credit is awarded.

| Indicator/subsystem | Status | Calculation / first valid index | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Arithmetic mean of 20 closes; index 19 | Visible overlay, independent toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; alpha = 2/21; index 19 | Visible overlay, independent toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 FOUNDATION | Wilder-smoothed average gains/losses over 14 close changes; index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 FOUNDATION | EMA12 − EMA26; MACD index 25; signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/current values, stale clearing, renderer tests |
| Bollinger20,2 | 🟨 FOUNDATION | 20-close mean ± 2 × population standard deviation; index 19 | Upper/middle/lower overlay, toggle, values, stale clearing, renderer/lifecycle tests |
| Shared Indicator Hook | 🟨 FOUNDATION | Validated candle-index-aligned indicator snapshot | Chart identity/timeframe binding, loading/error lifecycle, stale clearing, per-series isolation, renderer integration |
| Footprint | 🟧 SIMULATED / REFERENCE-GATED | Current accumulator is simulated/educational, not exchange-native bid/ask truth | User reference image and approved blueprint first; validated source/data contract; cluster renderer, toggle, scale/interaction, performance/lifecycle tests. OFF preserves normal candle spacing; explicit ON alone enables spaced clusters |
| Heatmap | 🟥 NOT IMPLEMENTED | No validated zero-cost data contract yet | Zero-cost source feasibility, user reference image, validated data contract, approved blueprint, renderer, legend/scale, toggle and lifecycle tests |
| Liquidation Maps | 🟥 NOT IMPLEMENTED | No validated zero-cost source/calculation contract yet | Zero-cost source feasibility, validated calculation/data contract, user reference/blueprint, renderer, scale/legend, toggle and lifecycle tests; never fabricate levels |

### Shared indicator invariants

- Warm-up output is `null`, never zero.
- Output is aligned to the original candle index.
- No future-candle repaint/look-ahead.
- Clear stale series on symbol, venue, dataset, chart identity or timeframe changes.
- Invalid bars and missing source values must not be silently converted to zero.
- Footprint OFF preserves standard candle spacing; explicit ON switches to spaced cluster layout.
- Footprint and Heatmap visual implementation must wait for user-supplied reference image(s) and a reviewed blueprint.
- Aggregate indicator percentage remains unscored until approved weights and denominators exist.

## 4. Gate 10 and overall project progress

Gate 10 remains **0/10 formally closed**. This is a closure count, not a claim that every gate is at zero implementation.

- 🟨🟩 Host/operator verification-only: Gates 8, 30, 34, 35, 39.
- 🟧 Integration/acceptance: Gates 20, 25, 31, 36, 38.
- Stage 1 foundation/security/data integrity: **30/40 = 75% provisional**.
- Stages 2–6 and overall project percentage: **unscored**, because approved denominators/weights do not exist.

The five integration/acceptance tracks remain distinct; completing repository-side WebSocket code does not close owner-host or device acceptance.

## 5. Verification and change accounting

- Changed runtime source: none.
- Changed client source: none.
- Changed indicator source/tests: none.
- Documentation correction: `backend/README.md`.
- New work-cycle record: this file.
- CI run triggered by this docs-only batch: none.
- Existing CI evidence: unchanged; refer to the acceptance pack for run IDs and exact source/test checkpoint.
- Deployment / Vercel / Cloudflare / paid service / production credentials / Termux action: none.
- `main`: untouched.

## 6. Next critical dependency

Public WSS acceptance cannot be truthfully executed until an owner-controlled public HTTPS hostname exists. The user does not need to know technical deployment terminology: the hostname is simply the internet address of the backend, such as `api.example.com`. Do not request or share passwords, Firebase tokens, Redis URLs, private keys, or other secrets in chat. If no public backend exists yet, continue only with repository-side verification and do not deploy or purchase hosting without explicit approval.
