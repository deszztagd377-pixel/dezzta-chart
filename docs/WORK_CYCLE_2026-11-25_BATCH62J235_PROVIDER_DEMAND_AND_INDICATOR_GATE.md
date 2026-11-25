# DEZZTA CHART — Batch 62J-235
## Exact-head CI, provider-demand subscription blueprint, and full indicator ledger

Date: 25 November 2026  
Branch: phase-2/market-data-foundation  
Documentation parent: 2bd311e1479659c418e5b8623826114f5dfb86f7  
Unchanged code/test baseline: bd4904b52d29b3ec456da91014e90922fec35f21  
Cost policy: ZERO COST  
Delivery planning target: approximately 24 December 2026.

## 1. Exact-head CI verification

The active branch ref was read directly and resolved to 2bd311e1479659c418e5b8623826114f5dfb86f7. Four required workflow runs were queried for that exact SHA. All four are terminal SUCCESS:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | 45521703215 | 🟩 SUCCESS — Test and Build job, 41/41 steps completed, including cleanup |
| CodeQL Security Analysis | 45521703291 | 🟩 SUCCESS — Python 8/8 and JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45521703194 | 🟩 SUCCESS — native ARM64 build/smoke-test job, 7/7 steps |
| Full Git History Secret Audit | 45521703184 | 🟩 SUCCESS — full reachable-history scan, 6/6 steps |

All four run objects report exact SHA 2bd311e1479659c418e5b8623826114f5dfb86f7, status completed, conclusion success. Job records were fetched separately. No active workflow remained. The legacy combined-status endpoint returned no rows; the evidence is the completed workflow run/job records, not a claim about legacy status rows.

The HEAD is documentation-only and its parent is the unchanged source/test baseline bd4904b52d29b3ec456da91014e90922fec35f21. CI success does not establish external production acceptance.

## 2. WebSocket source audit: what is actually implemented

Repository foundations verified:
- src/services/ohlcvSeriesSupervisorRegistry.ts shares a client-side authenticated supervisor per canonical series, tracks chart-panel owners, rejects conflicting endpoint/canonical-instrument mappings, and stops the client transport after the final owner releases.
- src/services/marketDataSeriesLeaseRegistry.ts tracks panel ownership with generation-safe, idempotent cleanup. Its own source comment explicitly says it does not create sockets or claim provider-side reference counting.
- backend/app/ohlcv_stream.py implements bounded downstream fan-out indexed by the full canonical series identity. It avoids payload construction when no subscriber exists for that exact series.
- Ticket authentication, snapshot/watermark, replay/sequence and Redis replica foundations remain separate from provider-upstream demand control.

## 3. Confirmed WebSocket blocker: provider demand is still static

Source-backed findings:
1. backend/app/databento_sources.py constructs a Databento Live client and calls subscribe once during start using the configured static symbols tuple. The adapter exposes stop(), but no dynamic add/remove subscription method exists in this repository adapter.
2. backend/app/provider.py determines live eligibility from configured databento_live_symbols and starts the provider session from that static configuration. It does not consume chart-owner acquire/release events.
3. backend/requirements.txt allows databento>=0.88,<1, which is a broad version range rather than one verified SDK build.
4. databento_sources.py explicitly labels its SDK calls UNVERIFIED: the repository has not executed the wrapper against the real SDK, network or credentials.

Consequently, provider upstream reference counting, dynamic subscribe/unsubscribe, shared provider-session ownership across users and zero upstream activity for inactive symbols are NOT complete. Client-side panel leases and backend downstream fan-out are not proof of provider-level demand control.

## 4. Scoped provider-demand implementation blueprint

Proposed ownership path:

Chart panel owner → exact-series client supervisor → authenticated backend subscriber → provider-demand coordinator → provider adapter → shared upstream session.

Identity separation:
- Downstream identity includes user/session/connection and the exact authorized series.
- Upstream identity includes provider, dataset, schema, input symbology and source instrument identity.
- Timeframe may be excluded from upstream identity only if the provider stream is timeframe-neutral and the backend derives multiple timeframes from the same upstream records. That assumption must be explicit and tested.
- Never merge different venues, datasets, publishers, symbology or instruments merely because display symbols look alike.

Required lifecycle:
- First authorized demand creates or joins one upstream key.
- Further equivalent demands attach without creating duplicate upstream sessions.
- One subscriber's close, revocation, slow queue or network loss removes only that subscriber.
- An upstream remains active while at least one authorized subscriber still requires it.
- Final release stops the upstream under a bounded, observable shutdown policy.
- Failed start/add/remove/stop operations remain visible and reconcile to a known state; no silent subscription leak.
- Reconnect resumes only currently active authorized demands and uses the established snapshot/watermark/replay sequence.
- No catalogue-wide subscriptions, hidden polling, artificial keepalive or background resubscribe.

SDK compatibility gate:
Before implementation, pin and inspect one exact Databento SDK version. Verify whether it supports adding/removing symbols on an already-running Live client, repeated-subscribe semantics, unsubscribe behavior, callback ordering and thread-safety. If live mutation is unsupported, design a bounded session-reconciliation strategy that preserves existing symbols and does not introduce silent gaps. Do not guess SDK method names or signatures. Never put a real API key in CI.

Required tests:
1. Zero subscribers → zero live sessions.
2. First demand → exactly one upstream session.
3. Two users requesting the same upstream key → one upstream, two isolated downstream subscribers.
4. Release one of two → upstream remains active.
5. Final release → upstream stops exactly once.
6. Same display symbol but different venue/dataset/instrument → separate upstream keys.
7. Timeframe fan-out from one upstream only when provider schema permits.
8. Duplicate acquire/release and stale-generation cleanup are idempotent.
9. Concurrent acquire/release during start/stop cannot leak or prematurely close.
10. Failed add/remove/start/stop recovers deterministically.
11. Entitlement revocation removes only the revoked subscriber.
12. Inactive catalogue entries create no provider demand.
13. Reconnect/replay preserves cursor continuity and resnapshots on a gap.
14. Credentials never appear in logs, status, exceptions or frontend bundle.

ZERO COST boundary:
Fake-provider and deterministic integration tests can be developed without paid services. Databento is not assumed to be a free recurring live CME feed. No paid source, account, domain, host, deployment or billing resource may be provisioned. Production live CME data remains a separate cost/data-rights blocker until a genuinely free and lawful source is validated.

This is a scoped blueprint for review, not permission to invent or wire an unverified SDK API. No provider source code changed in this batch. After blueprint acceptance and exact SDK compatibility verification, implement the coordinator, fake adapter and failure-matrix tests as one coherent change.

## 5. Gate 25 / Gate 36 / Redis

| Requirement | Status | Remaining acceptance |
|---|---|---|
| Gate 25 repository signature/receipt/file boundary | 🟩 Repo CI verified | Ed25519 trust, immutable receipt, startup verification and hardened private-key file boundary |
| Gate 25 owner-host key custody | 🟥 OPEN | Owner-controlled host/key custody evidence |
| Gate 25 authenticated transfer to every gateway | 🟥 OPEN | Real authenticated snapshot transfer evidence |
| Gate 25 receipt retrieval after restart | 🟥 OPEN | Retrieve and re-verify each gateway's durable receipt |
| Gate 25 durable per-gateway high-water ACK | 🟥 OPEN | Read durable per-gateway checkpoint; Redis XACK is not a substitute |
| Gate 36 public HTTPS/WSS + proxy/TLS/runtime | 🟥 OPEN | Public production endpoint acceptance |
| Firebase production sign-in/entitlement/revocation | 🟥 OPEN | Real configured Firebase E2E evidence |
| Browser/Android lifecycle and network handover | 🟥 OPEN | Physical-device/production-host acceptance |
| Production multi-instance failover/replay | 🟥 OPEN | Real multi-instance evidence |
| Redis destructive retention | 🟧 BLOCKED | Gateway inventory/retirement, PEL policy, durable floor ACK, separate authority and crash-safe reconciliation must all pass |

No destructive Redis operation was performed. No external host, key or credential was accessed. No production deployment was made.

## 6. Complete indicator progress ledger

Verified source inventory:
- src/indicators/indicatorCalculations.test.ts: 21 named test declarations.
- src/indicators/useMarketIndicators.test.ts: 7 named test declarations.
- Total: 28 focused indicator test declarations (21 calculation + 7 shared hook).
- The exact-head Automated Tests workflow passed. Test declaration count is not a completion percentage.
- src/components/CandlestickChart.tsx does not import or call useMarketIndicators. Visible chart integration remains absent.

| Study | Calculation contract | First valid index | Visible chart/UI acceptance | Status |
|---|---|---:|---|---|
| SMA20 | Mean of current 20 closes; normalized/stable mean avoids avoidable overflow | 19 | Overlay, toggle, legend/latest value, identity reset and multi-panel lifecycle absent | 🟨 Foundation only |
| EMA20 | SMA-seeded EMA; alpha = 2/(20+1) = 2/21 | 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 Foundation only |
| RSI14 Wilder | 14 close-to-close changes seed average gain/loss; Wilder recurrence; flat=50, gain-only=100 | 14 | 0–100 pane, 30/70 guides, toggle and latest-value legend absent | 🟨 Foundation only |
| MACD12/26/9 | EMA12 − EMA26; EMA9 signal over valid MACD values; histogram = MACD − signal | MACD 25; signal/histogram 33 | Pane, MACD/signal lines, histogram, zero line, toggle and legend absent | 🟨 Foundation only |
| Bollinger20,2 | 20-close mean ± 2 × population standard deviation (ddof=0) | 19 | Upper/middle/lower overlay, fill, toggle and latest values absent | 🟨 Foundation only |
| Shared Indicator Hook | Exact keyed immutable snapshot, shared calculation cache, trust gating, revision updates and stale-output clearing | Per study | Hook tests exist; not wired into CandlestickChart | 🟨 Foundation only |
| Footprint PRO 2GD | Synthetic/offline educational accumulator; not exchange-native bid/ask execution truth | N/A | Visual implementation gated by reviewed blueprint; two owner references supplied | 🟧 Gated |
| Volume Profile | Production calculation and volume-source semantics not verified | N/A | Not integrated | 🟥 Open |
| Complete Volume Profile | Complete production calculation/acceptance not verified | N/A | Not integrated | 🟥 Open |
| Movable-range Volume Profile | Range selection, recalculation and lifecycle contract not accepted | N/A | Not integrated | 🟥 Open |
| Heatmap | Accepted depth/liquidity feed and aggregation contract not verified | N/A | Not integrated; owner visual reference still required | 🟥 Open |
| Liquidation Maps | Methodology, provenance and validated data source not accepted | N/A | Not integrated | 🟥 Open |

Numeric/lifecycle invariants:
- Warm-up points remain null; no synthetic warm-up values.
- Every output index maps to the same source candle index.
- MACD signal starts only after nine valid MACD values; histogram remains null until signal exists.
- Reject non-finite input/output rather than silently emitting invalid chart values.
- No future-candle dependency or repaint from later candles.
- Instrument, timeframe, provider, dataset or canonical identity changes clear stale output before new values appear.
- Shared cached output is immutable and keyed by full series identity + data revision + study parameters.
- Visibility toggles do not mutate source market data.
- Footprint OFF preserves normal candlesticks and spacing. Explicit ON alone activates spaced candle clusters. Synthetic values must never be labelled real exchange bid/ask.
- Footprint and Heatmap visuals remain behind the formal Stage 4 gate, scoped blueprint and owner review.

Indicator aggregate completion: ⚪ NOT SCORED. No approved denominator or weighting exists.

## 7. Project progress meters

| Stage / metric | Current accounting | Status |
|---|---|---|
| Stage 1 — Foundation/Security/Data Integrity | 30/40 criteria = 75% provisional, inherited and not rescored | 🟨 |
| Stage 2 — Market Data Infrastructure | Active; provider-demand reference counting incomplete; denominator not approved | 🟦 ACTIVE / NOT SCORED |
| Stage 3 — Chart Engine & Timeframe | No approved denominator/formal score | ⬜ NOT SCORED |
| Stage 4 — Indicators & Analytics | Entry/blueprint/review gate not cleared | 🟪 GATED |
| Stage 5 — Professional UI & Tools | No approved denominator/formal score | ⬜ NOT SCORED |
| Stage 6 — Hardening/Validation/APK | No approved denominator/formal score | ⬜ NOT SCORED |
| Gate 10 | 0/10 external criteria formally closed in inherited ledger | 🟥 OPEN |
| Overall project | No approved six-stage weights/denominator | ⚪ NOT SCORED |
| Indicator aggregate | No approved study weights/denominator | ⚪ NOT SCORED |
| IP3S / significant progress | No approved scoring formula applied | ⚪ NOT SCORED |

Stage 1's provisional 75% must not be represented as overall project completion.

## 8. Batch result and next order

Documentation-only changes:
- Added this Batch 62J-235 work-cycle record.
- No runtime source, tests, dependencies, schema, credentials, provider account, deployment, APK or Redis retention behavior changed.
- main untouched; active branch remains phase-2/market-data-foundation.

Next order remains:
1. Gate 25 owner-host authenticated transfer, receipt retrieval/re-verification and durable per-gateway high-water ACK.
2. Gate 36 public HTTPS/WSS + TLS/proxy/runtime evidence.
3. Firebase production sign-in, entitlement and revocation E2E.
4. Real browser/Android lifecycle and production multi-instance failover/replay.
5. Redis retention safety acceptance; destructive retention remains blocked.
6. Provider-demand coordinator after this blueprint is reviewed and exact SDK behavior is verified.
7. Stage 3 chart integration, then Stage 4 indicators after the stage gate and reviewed blueprint.
8. Remaining UI, hardening and APK acceptance.

Conclusion: exact active HEAD CI is 4/4 terminal SUCCESS. The most important newly isolated WebSocket blocker is provider-upstream demand control: client and downstream foundations exist, but the real provider adapter is static and its SDK surface is explicitly unverified. No speculative source code was introduced. ZERO COST and the approximately 24 December 2026 planning target remain unchanged.


## 9. Official SDK API compatibility research — 25 November 2026

The official Databento Python Live API documentation and release history narrow the earlier compatibility uncertainty:

- Live.subscribe() is documented as adding a subscription to an existing session; subscriptions in one Live session must use the same dataset. The API returns a subscription ID. See https://databento.com/docs/api-live/client/subscribe?lang=python.
- Live.unsubscribe() is documented for removing selected symbols from a schema. The accepted input symbology for unsubscribe must be compatible with the original subscription. The gateway can return an UNSUBSCRIBE_ACK or an ErrorMsg; a local call returning does not itself prove the gateway accepted the removal. See https://databento.com/docs/api-live?lang=python.
- The official Python changelog identifies Live.unsubscribe() as added in version 0.89.0. It also records a 0.90.0 fix for Live methods such as stop()/terminate() blocking during reconnect attempts. See https://github.com/databento/databento-python/blob/main/CHANGELOG.md.

**Engineering consequence:** the repository currently permits versions from 0.88, so its declared dependency range includes a version before the documented unsubscribe addition. A dynamic implementation must raise the minimum supported SDK to at least 0.89 and pin an exact tested version for reproducible CI before relying on unsubscribe. It must also process gateway acknowledgement/error records and respect the single-dataset-per-session constraint.

**Still unverified:** the active environment's installed SDK version, exact runtime behavior for the repository's callback threading model, and real gateway acknowledgement behavior. Official API documentation narrows the design, but does not substitute for fake-adapter regression tests and a separately authorized real-provider acceptance test. No provider dependency or runtime code was changed in this batch.

**ZERO COST decision:** this API research does not authorize Databento usage. Databento remains a potentially billable source; no account, key, paid subscription or live request was created. The app must retain disabled-by-default behavior unless a lawful, genuinely free source is validated or the owner changes the zero-cost requirement.

