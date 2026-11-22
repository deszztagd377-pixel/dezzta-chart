# DEZZTA CHART — Work Cycle 62J-142
## Exact-HEAD CI closure, zero-cost WebSocket hosting assessment and indicator reconciliation

Date: 22 November 2026
Branch: `phase-2/market-data-foundation`
Verified starting HEAD: `ad3fa4413cdc827d49e6ec05731f0cd90360c75d`
ZERO COST: no account, payment method, deployment, cloud resource, paid service, production credential, device operation or `main` change.

## 1. Exact-HEAD CI closure

The starting HEAD `ad3fa4413cdc827d49e6ec05731f0cd90360c75d` was re-verified as the active branch ref.

- Automated Tests [45001169602](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45001169602): **SUCCESS** on exact HEAD.
- CodeQL [45001169566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45001169566): **SUCCESS** on exact HEAD.
- Full Git History Secret Audit [45001169507](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45001169507): **SUCCESS** on exact HEAD.
- OCI ARM64 Image Readiness [45001169506](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45001169506): **SUCCESS** on exact HEAD.

Automated Tests job completed all steps successfully, including frontend dependency audit, frontend unit tests/build, source and bundle secret scans, Android host preflight, immutable Android preview publisher test, Redis TLS fixture, backend tests, bounded synthetic SQLite outbox and metrics benchmarks, backend dependency audit, backend image build/smoke and image scan/report.

ARM64 smoke acceptance proved native ARM64 build, backend health, PID 1 UID 10001, mounted-volume write and persistence after container restart. This is GitHub-hosted CI evidence only. It is not an OCI account, VM, public WSS endpoint or production deployment.

## 2. Hosting alternatives — decision, not deployment

The hard constraints are: $0 with no surprise charges, WebSocket support, portable backend contract, safe credential handling, and no requirement for the project operator to provide a payment card. Google-only sign-in is not assumed: the provider's current signup options and any payment verification must be checked by the adult account owner before an account is created.

### Candidate A — Cloudflare Workers + Durable Objects (best architecture candidate; account/signup verification still required)

Official documentation confirms Durable Objects are available on Workers Free, including SQLite-backed Durable Objects. Published free limits include 100,000 requests/day and 13,000 GB-s/day for Durable Objects; Workers Free has 100,000 requests/day and 10 ms CPU per invocation. Exceeding a free quota causes the relevant operations to fail rather than proving unlimited capacity.

Sources:
- https://developers.cloudflare.com/durable-objects/
- https://developers.cloudflare.com/durable-objects/platform/pricing/
- https://developers.cloudflare.com/workers/platform/limits/

Fit: stateful WebSocket coordination and per-symbol/per-session actors are a natural match. However, this is not a drop-in host for the existing Python/container backend. It would require a separately reviewed TypeScript Worker/ Durable Object adapter, an explicit state model, and tests for reconnect, hibernation, message ordering, backpressure, and quota exhaustion. Existing Python services, Redis TLS runtime, SQLite outbox, and owner-host receipt model cannot simply be assumed to run unchanged in a Worker. No migration is approved or started.

Signup/card condition: the reviewed technical docs establish free product quotas, not that every signup path is Google-only or that no payment verification can ever be requested. Treat cardless signup as **UNVERIFIED** until an adult account owner reviews the live signup flow. Do not enter payment information or create an account during this work cycle.

### Candidate B — Render Free Web Service (fastest container/Python proof-of-concept; not continuous production)

Official Render docs confirm WebSocket support and free web services. Free instances spin down after 15 minutes without inbound HTTP or WebSocket messages; a subsequent connection wakes the service and can take about one minute. Free service filesystems are ephemeral, and free Postgres expires after 30 days. Free instance allowance is 750 hours/workspace/month; outbound bandwidth/build limits apply. Render's Docker hosting page advertises free Docker hosting without a credit card.

Sources:
- https://render.com/docs/free
- https://render.com/docs/websocket
- https://render.com/hosting/docker

Fit: likely the least invasive way to run the existing container for a temporary integration smoke test. It is unsuitable as the project's always-on market-data origin because of idle sleep, restarts, ephemeral local storage, and no durable free disk. Do not put Redis/SQLite durable state on its ephemeral filesystem. Confirm current signup and usage protections before any adult-owned test deployment.

### Candidate C — Oracle Cloud Always Free (ARM64-capable, but blocked on card verification)

Oracle's official FAQ says credit/debit card details are required for identity verification; debit cards that function like credit cards are accepted, but PIN-only debit, virtual, single-use and prepaid cards are not. A temporary authorization hold may occur. This is incompatible with the user's current no-card situation. No workaround, borrowed card, fake details or verification bypass is acceptable.

Source:
- https://www.oracle.com/apac/cloud/free/faq/

### Decision

1. Keep OCI as an optional future target, not a dependency.
2. Keep the existing backend/container portable.
3. Evaluate Cloudflare Workers + Durable Objects as a future WebSocket edge/coordination adapter only after code-level architecture review and adult-owned account eligibility confirmation.
4. Use Render only if a temporary, sleeping proof-of-concept is needed and its current signup terms are acceptable.
5. Do not move the existing authoritative Redis/SQLite/receipt persistence to a provider's ephemeral free filesystem.
6. No Google-only sign-in claim is made for any provider. No account was created, and no payment method was requested.

## 3. WebSocket status and gates

Supervisor ownership and stale-callback regression hardening remain accepted by exact-HEAD CI. Public production WebSocket acceptance is not complete.

- Gate 25: **OPEN** — immutable authenticated snapshot-installation receipt, receipt custody, key lifecycle, owner-host Redis persistence/recovery.
- Gate 36: **OPEN** — public hostname/WSS, reverse proxy/certificate, live Firebase identity/entitlement, real Android WebView foreground/background/process-death/network-handover.
- Gate 38: **OPEN** — owner-host durable metrics, disk pressure, restart/backup/retention, dashboards/alerts/recovery drill.
- Other open Stage 1 tracks: 8, 20, 30, 31, 34, 35, 39.
- Gate 10: **0/10 external criteria formally closed**.

CI success does not close external acceptance gates.

## 4. Complete technical indicator ledger

No indicator formula, hook, renderer, UI or indicator test source changed in this work cycle. No technical-indicator implementation credit is awarded.

| Indicator/component | Status | Verified foundation and remaining work |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; chart integration and edge-case acceptance remain |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; first valid index 19; chart integration and edge-case acceptance remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; numerical edge cases and chart integration remain |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33; chart integration remains |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19; chart integration remains |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; full chart integration remains |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator, not exchange-native bid/ask truth; user reference image(s) and reviewed blueprint required before visuals |
| Heatmap | 🟥 Not implemented | User reference image(s), validated data contract and reviewed blueprint required before visuals |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence; data contract and renderer remain |

Mandatory invariants:
- Warm-up values remain null, not zero.
- Outputs remain aligned to source candle indices.
- Prefix causality: adding future candles cannot change earlier outputs.
- Invalid/missing/gapped bars are never silently coerced to zero.
- Stale output clears on symbol, venue, dataset, chart and timeframe identity changes.
- Calculation, rendering, interaction, lifecycle and performance are separate acceptance dimensions.
- Footprint OFF preserves ordinary candle spacing; explicit ON alone enables the dedicated spaced-cluster layout.
- Footprint/Heatmap visual implementation remains blocked until user reference image(s) are supplied and the scoped blueprint is reviewed.
- Aggregate indicator completion remains **NOT SCORED** because weights and denominator are unapproved.

## 5. Project-wide progress

Legend: 🟩 accepted; 🟨 partial/provisional; 🟧 prototype; 🟥 not implemented; ⬜ not scored/not opened.

| Official stage | Current progress | Status |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 criteria = 75% provisional | 🟨 |
| 2. Market Data Infrastructure | Not scored / not officially opened | ⬜ |
| 3. Chart Engine & Timeframe | Not scored / not officially opened | ⬜ |
| 4. Indicators & Analytics | Not scored / not officially opened | ⬜ |
| 5. Professional UI & Interactive Tools | Not scored / not officially opened | ⬜ |
| 6. Hardening, Validation & APK Release | Not scored / not officially opened | ⬜ |

Overall project: **NOT SCORED**. Six-stage weights and overall acceptance denominator are not approved. Stage 1's 75% is not the overall project percentage.

IPS35: **PENDING** for this documentation cycle until exact-HEAD checks complete on the resulting commit. Do not award engineering or indicator points for hosting research/documentation alone.

## 6. Integrity and next steps

- Branch: `phase-2/market-data-foundation`; `main` untouched.
- No runtime, schema, dependency or workflow changes in this cycle.
- No account, cloud resource, deployment, domain, payment method or production credential.
- No device or Termux operation.
- Any cloud account must be owned and managed by a parent/guardian, using their own consented identity and payment arrangements; no credentials or payment details are to be shared in chat.

Next technical sequence:
1. Audit current backend protocol boundaries before selecting any provider-specific adapter.
2. Write a provider-neutral WebSocket deployment interface and conformance test plan before any port.
3. Preserve the current Python/container backend as the authoritative implementation until an alternative adapter passes equivalent tests.
4. Continue Gate 25 receipt design/approval and Gate 36 client lifecycle tests without weakening authentication or replay protection.
5. Do not begin Footprint/Heatmap visual work before user references and blueprint review.

**Final status:** exact-HEAD CI is green on starting HEAD; OCI ARM64 smoke passed in CI only; Cloudflare is the strongest architecture candidate but signup/payment verification is not confirmed; Render is a limited sleeping proof-of-concept; no cloud provider is deployed; indicator status unchanged; Gate 10 remains 0/10; overall project remains not scored.
