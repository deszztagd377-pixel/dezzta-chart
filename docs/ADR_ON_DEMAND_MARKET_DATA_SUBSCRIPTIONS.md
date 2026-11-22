# ADR — On-demand Market Data Subscriptions

Date: 22 November 2026
Status: **Accepted product requirement; implementation/design validation pending**
Branch: `phase-2/market-data-foundation`
Cost constraint: **ZERO COST**
Stage ownership: **Stage 2 — Market Data Infrastructure** (primary); Stage 1 supplies security/session/lifecycle prerequisites.

## 1. Decision

DEZZTA CHART must use chart-driven, on-demand market-data subscriptions. Listing or searching the available pair catalogue must not start OHLCV streaming or periodic market-data polling for every pair.

A pair/series becomes eligible for a live market-data subscription only while at least one chart surface that the user is actively viewing requests that exact series. A closed, replaced, hidden, backgrounded, or otherwise inactive chart must release its subscription. The backend must not keep a user's subscription alive merely because the pair exists in the catalogue.

This is a binding product/architecture requirement. It is not evidence that the complete behavior is already implemented.

## 2. Stage allocation

### Stage 1 — Foundation, Security & Data Integrity

Stage 1 owns prerequisite controls:
- Firebase identity verification and short-lived, single-use WebSocket ticket authentication.
- Per-user connection/session isolation and entitlement enforcement.
- Foreground/background and visibility lifecycle handling for each client.
- Safe disconnect, cancellation, reconnect, snapshot and replay boundaries.
- No single user's disconnect may stop the independently hosted server or another user's connection.

Stage 1 does **not** receive implementation credit for the Stage 2 subscription/fan-out system merely because these prerequisites exist.

### Stage 2 — Market Data Infrastructure

Stage 2 owns the on-demand market-data capability:
- Explicit subscribe/unsubscribe driven by active chart ownership.
- No stream/polling for unopened pairs.
- Shared upstream stream for equivalent active subscribers when supported by the provider's stream contract.
- Reference counting and independent subscriber lifecycle.
- Snapshot/live boundary, replay, sequence continuity and resnapshot recovery.
- Quota-aware message rates, payloads, batching and idle behavior.
- Tests proving zero inactive-pair subscriptions and correct multi-user fan-out.

Stage 2 remains **not officially opened / not scored** until its entry criteria and denominator are approved. This ADR records the requirement and allocation; it does not open the stage or award progress.

## 3. Required client behavior

1. Pair catalogue, search, watchlist and symbol metadata views do not subscribe to OHLCV market streams.
2. Opening a chart requests only its exact canonical series identity: dataset, publisher/source, instrument and timeframe (plus any other server-defined identity fields).
3. Replacing the active chart series first releases the previous subscription, then requests the new series. A safe handover may overlap only if explicitly required to avoid a visible data gap and must be bounded.
4. Closing a chart releases its subscription.
5. When the app becomes hidden, offline, backgrounded or is explicitly stopped, the client releases chart ownership and closes/pauses its foreground-only connection according to the established lifecycle policy.
6. Returning to foreground obtains fresh identity/ticket material, reconnects, receives an atomic snapshot/watermark, then applies replay/live events with sequence validation.
7. No hidden timer, fallback polling loop, or reconnect loop may silently reactivate an inactive chart.
8. If multiple chart panels are intentionally visible, each panel may hold its own logical subscription; equivalent subscriptions should be deduplicated at the appropriate client/backend boundary.

## 4. Required backend behavior

### 4.1 Shared upstream and subscriber registry

The backend should maintain a subscriber registry keyed by the provider's true upstream stream identity. Do not assume that a display pair string alone is sufficient. At minimum, identity must account for venue/source and instrument; timeframe is included when the upstream provider exposes timeframe-specific streams. If one raw trade/depth stream can serve multiple derived timeframes, that fan-out must be explicit and tested rather than inferred.

For each upstream key:
- First eligible subscriber starts one upstream stream.
- Further equivalent subscribers attach to the existing stream.
- A subscriber receives only the authorized series it requested.
- A disconnect removes only that subscriber.
- The upstream is stopped only after the final subscriber releases it, subject to a short, bounded debounce if needed to prevent churn.
- Subscriber state is per user/connection; upstream process lifetime is independent of any one client.
- One user's close, entitlement revocation, slow consumer or network loss must not interrupt other subscribers.

This is the intended shared-upstream/reference-counting model. Current repository evidence for independent WebSocket clients does not by itself prove provider-level upstream deduplication.

### 4.2 Snapshot and live correctness

- Establish a consistent snapshot/live boundary and watermark.
- Replay from the last durable cursor before applying live events.
- Reject duplicate, stale, wrong-stream, wrong-series and out-of-order events.
- On sequence gap or retention miss, fail closed and obtain a fresh snapshot.
- Preserve existing ticket authentication, exact-series authorization and entitlement rechecks.
- Do not use an in-memory subscriber count as durable market-data history or as a substitute for the existing Redis/replica recovery contract.

## 5. Quota and bandwidth model

The design optimizes two separate budgets:

**Client mobile-data budget**
- No unopened-pair market-data payloads.
- No catalogue-wide polling.
- Subscribe only to active chart series.
- Use bounded payloads and avoid sending unchanged/redundant updates where the source contract permits.
- Heartbeats and authentication/reconnect traffic may still consume small amounts of data while the active connection is open; therefore “inactive pair uses zero streaming data” must not be misreported as “the app uses absolutely zero network data.”

**Hosting/free-tier budget**
- Count requests, WebSocket messages/frames, CPU/compute duration, storage, egress and connection limits separately according to the selected provider's current plan.
- Shared upstream reduces duplicate provider connections and ingestion work; it does not make per-subscriber egress or all provider billing dimensions disappear.
- Idle upstream shutdown must follow subscriber count and provider constraints, not one user's app lifecycle.
- Never rely on artificial keep-alive traffic to evade a host's free-tier idle policy.
- No paid upgrade, payment method or billable resource is permitted under the current ZERO COST requirement.

No numerical capacity claim is approved until expected active users, simultaneous chart count, update frequency, average payload size, reconnect rate and provider plan limits are measured.

## 6. Required acceptance matrix

| Scenario | Expected result |
|---|---|
| Open catalogue with 200 listed pairs, no chart | 0 pair market-data subscriptions; 0 pair polling loops |
| Open one chart | Exactly its authorized canonical series becomes active |
| Switch pair A to pair B | A is released; B becomes active; no orphan A subscription |
| Close chart | Its logical subscription is removed |
| Background/offline one user | Only that user's client subscriptions are removed |
| Two users view same upstream identity | One upstream where provider contract permits; two isolated subscribers |
| User B closes while A remains | B is removed; A continues receiving valid updates |
| Last subscriber closes | Upstream is stopped after bounded idle/debounce policy |
| User reopens chart | Fresh auth/ticket, snapshot/watermark, replay then live |
| Sequence gap during reconnect | No silent skip; resnapshot/replay recovery |
| Entitlement revoked for one user | That user's stream is denied/closed; other authorized subscribers continue |
| Inactive pair receives upstream event | No forwarding to users without an active authorized subscription |
| App backgrounded with pending reconnect | Pending timer/request is cancelled; no background resubscribe |
| Multiple visible chart panels | Each intended panel is represented; equivalent upstream is deduplicated safely |

Acceptance evidence must include unit, integration and real-host tests where applicable. Test reports must distinguish repository-local simulation from public provider/device acceptance.

## 7. Current evidence and limitations (22 November 2026)

Verified branch HEAD: `06a3c3c9e5b5ecd2ff4c8c29e0e472972c1c6e7e`.

Exact-HEAD workflows:
- Automated Tests run 45006546194: SUCCESS.
- CodeQL run 45006545959: SUCCESS.
- Full Git History Secret Audit run 45006545947: SUCCESS.
- OCI ARM64 readiness run 45006545965: SUCCESS.

The latest source change only updates `backend/tests/test_api.py` to exercise HTTPS WebSocket-ticket issuance and ticket-authenticated WSS, renewal and two-user disconnect isolation over a real loopback TLS listener. These green workflows do not prove on-demand chart-driven subscriptions or shared upstream fan-out.

Existing client documentation describes an exact-series `market_data.subscribe` message and foreground-only lifecycle. The real-TLS multi-user test proves one client's disconnect does not terminate the other client's connection. Neither fact alone proves:
- chart-open/close UI ownership is wired end-to-end for every chart surface;
- catalogue views never start polling/streaming;
- backend provider subscriptions are deduplicated across users;
- reference counting correctly starts/stops actual upstream streams;
- real provider bandwidth or hosting quotas remain within free-tier limits.

Therefore this requirement is **accepted as design/product direction but not yet implemented/accepted end-to-end**.

## 8. Implementation sequence and safety gates

1. Audit the current chart owner, `ohlcvStreamSupervisor`, WebSocket protocol, backend stream hub and provider adapter before changing code.
2. Trace every subscribe, reconnect, chart replacement, close, visibility, offline and unmount path; identify whether current subscription identity already matches the canonical series.
3. Add/verify client-side active-chart ownership and idempotent unsubscribe without weakening ticket auth, snapshot/replay or existing lifecycle protections.
4. Add backend subscriber registry/reference counting at the correct provider boundary; do not conflate per-client socket count with upstream stream count.
5. Add tests for inactive catalogue, pair switching, same-series multi-user fan-out, one-user disconnect, last-subscriber shutdown, revocation and reconnect.
6. Measure request/message/compute/egress budgets using bounded synthetic workloads; no production provider or paid service.
7. Only after local evidence passes, plan free-host compatibility and external acceptance. Do not create accounts, deploy, add payment methods or upgrade plans without explicit authorization and verified ZERO COST terms.

No runtime, schema, dependency, deployment or account change is authorized by this ADR alone.

## 9. Progress accounting

- Stage 1: remains 30/40 = 75% provisional; this ADR adds no Stage 1 implementation credit.
- Stage 2: not officially opened / not scored; no Stage 2 implementation credit is awarded.
- Indicator implementation: no indicator code changed; zero indicator credit.
- Gate 10: remains 0/10 external criteria formally closed.
- Overall project: NOT SCORED; stage weights and denominator remain unapproved.

## 10. Non-negotiable invariants

- ZERO COST.
- Never touch `main`; active branch remains `phase-2/market-data-foundation`.
- Inspect before editing; preserve working behavior.
- No background market-data streaming.
- One user's disconnect must never stop another user's session or the independent backend.
- Do not claim shared upstream, quota savings, Stage 2 completion or production readiness without direct test evidence.
- No implementation before source audit and acceptance tests are designed.


## 11. Repository source audit addendum — Batch 62J-146 (22 November 2026)

Inspected current source at the documentation branch baseline. This is a source review, not a runtime change.

### Frontend ownership

- `src/components/CandlestickChart.tsx` starts an authenticated supervisor for the selected contract/timeframe and binds it to the chart component lifecycle and foreground/online state.
- `src/services/ohlcvStreamSupervisor.ts` has a module-level `activeSupervisorStop` singleton. Starting a new supervisor stops the previous owner. This protects the singleton market-data store from competing writers, but it means the current frontend architecture supports one active supervisor owner, not independently active simultaneous chart panels.
- `src/services/ohlcvWebSocketClient.ts` sends one exact-series `market_data.subscribe` request after authentication. The transport supports ticket renewal, heartbeat, cursor replay and sequence validation.
- The current client therefore has a meaningful single-chart on-demand selection boundary, but it is not yet a general multi-chart subscription manager.

### Backend ownership and upstream boundary

- `backend/app/main.py` constructs one `ProviderManager` and, in the non-replica mode, calls `await provider.start()` from application lifespan startup. Provider lifecycle is therefore process-scoped in the current source path, not activated/deactivated by the count of open chart subscriptions.
- `backend/app/provider.py` starts the ingestion consumer and supervises its configured live source when provider configuration and live-symbol settings permit. No chart-subscriber demand registry is wired into this provider lifecycle in the inspected path.
- `backend/app/ohlcv_stream.py` implements an in-memory `OhlcvStreamHub`: each WebSocket subscription receives its own stream ID and bounded queue; publish filters by exact series identity and fans out to matching subscriptions. This is downstream client fan-out, not proof of provider upstream pooling, demand-based provider subscribe/unsubscribe, or reference-counted upstream shutdown.
- The current provider pipeline is intentionally separate from the WebSocket subscriber registry. Do not conflate an active client subscription with an upstream provider connection.

### Consequence

The complete requested behavior is **not yet implemented**. The gap is broader than adding a client-side unsubscribe:
1. Keep the existing single-chart behavior correct while designing an explicit active-chart owner abstraction.
2. Decide whether simultaneous chart panels are a supported product requirement now or a later extension; do not silently broaden the current singleton store.
3. Introduce a provider-demand coordinator between active authorized series and the provider adapter, with provider-specific multiplexing semantics and a reference-counted desired-subscription set.
4. Reconcile desired upstream subscriptions on startup, reconnect, entitlement change, last-subscriber release and provider restart.
5. Preserve process independence: a client disconnect only removes that subscriber; it never stops the provider process while other subscribers or explicitly required ingestion work remain.
6. Prove the absence of inactive-pair polling/streaming using tests at both the client and provider boundary.

No runtime implementation is made in this addendum because the provider-demand ownership contract, multi-chart support boundary and provider SDK subscription semantics must be resolved first. Do not weaken the existing persistence, replay, sequence, entitlement or lifecycle guarantees.

