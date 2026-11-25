# DEZZTA CHART — Work Cycle 88: Cloudflare Native Zero-Origin Architecture Alignment

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Audited repository HEAD before this cycle: `86f682988b4a5c2252be1aae9d05584b9014e660`  
Cost ceiling: ZERO COST  
Delivery planning target: around 24 December 2026

## 1. Executive decision

The user's latest accepted architecture direction is **B — Cloudflare Native / Zero-Origin**: no owner-operated PC/server, no paid host, no new external origin, and no paid fallback.

The older Batch 80–86 plan assumes a continuously running owner-hosted source/gateway topology, Redis TLS, local file-backed SQLite and two gateway processes. That is not the approved Zero-Origin target. Executing that old plan as written would create a parallel architecture and repeat work. It is now **historical/reference material only**, not the active execution order.

This cycle aligns the project plan to the selected architecture. It does not deploy, create Cloudflare resources, change production routing, enable a provider, or modify runtime code. The major implementation gate remains: a scoped Zero-Origin blueprint must be reviewed before production runtime composition is changed.

## 2. Repository evidence

Current source files inspected on `phase-2/market-data-foundation`:

- `backend/requirements.txt` blob `da7f78eada7bd9108ee712590f57476cbfbfd96e`
- `backend/app/main.py` blob `faefb0d117e084d37c99da8837a4270fa9a6951c`
- `backend/app/config.py` blob `bed8a7061601334a294604a910218425b357c33e`
- `backend/app/ohlcv_store.py` blob `fd2e04beb87b511929a5f431abfa8f08babf3c71`
- `backend/app/snapshot_attestation.py` blob `f2c665974a2b7175c55eef80701c04b4c421f16c`
- `backend/app/identity.py` blob `cd28544c04388eb0811f70e473c794c6cdef858a`
- `cloudflare/wrangler.jsonc` blob `b25de82ed9e82d294b92a336c89b3b45153738a0`
- `cloudflare/proof/worker.mjs` blob `b124b6886454d788f6a83d4cd2e4e692bacc7205`

The FastAPI application is a 1,939-line module with a large import graph: SQLite metrics/coverage/instrument/alert/incident/entitlement stores; Databento source adapters; Redis guard, stream publisher and gateway worker; snapshot attestation; Firebase identity; and WebSocket/ticket routes. The app factory exposes mutually exclusive `publisher_runtime_factory` and `replica_runtime_factory`, while the module-level app is created with `app = create_app()` and neither factory. This confirms the earlier source/gateway composition gap, but it does not justify deploying that topology under the newly selected architecture.

The requirements currently include FastAPI, Uvicorn, Databento, Firebase Admin, Redis and cryptography. Package compatibility must be established individually; a package installing on CPython does not imply it is compatible with Pyodide/Python Workers.

The existing Cloudflare Worker remains a separate synthetic-only proof. It is not the FastAPI production backend, not a live data provider, and not a deployed public WSS service.

## 3. Compatibility facts and constraints

### Supported platform facts

Official Cloudflare documentation confirms:

- FastAPI/ASGI can run in Python Workers using Cloudflare's ASGI entrypoint.
- Python Workers execute on Pyodide/WebAssembly.
- Python Workers have an ephemeral in-memory filesystem; files are not durable across isolate lifetimes.
- `threading` and `multiprocessing` can be imported but are not functional under the WebAssembly runtime.
- Python packages need to be pure Python, included in Pyodide, or available as compatible PyEmscripten wheels. CPython-native wheels cannot be assumed compatible.
- Workers accept inbound WebSockets; clients must reconnect and restore application state after runtime restarts.
- Durable Objects support SQLite-backed persistent storage and WebSocket hibernation.

Official references:
- FastAPI in Python Workers: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
- Python Workers standard library and filesystem: https://developers.cloudflare.com/workers/languages/python/stdlib/
- Python package compatibility: https://developers.cloudflare.com/workers/languages/python/packages/
- WebSocket lifecycle: https://developers.cloudflare.com/workers/runtime-apis/websockets/
- Durable Objects limits: https://developers.cloudflare.com/durable-objects/platform/limits/
- Durable Objects pricing: https://developers.cloudflare.com/durable-objects/platform/pricing/
- Workers limits: https://developers.cloudflare.com/workers/platform/limits/

### Current Free-plan limits to design against

As verified from Cloudflare's published documentation on 25 November 2026:

| Resource | Workers Free / DO SQLite Free limit | Design consequence |
|---|---:|---|
| Workers requests | 100,000/day | Request budgets and backpressure required |
| Workers CPU per HTTP request | 10 ms | No heavy synchronous calculations in request path |
| Worker isolate memory | 128 MB | Bound buffers, caches and per-request work |
| Durable Object requests | 100,000/day | DO RPC/HTTP/alarms and WebSocket message accounting must be modelled |
| DO duration | 13,000 GB-s/day | WebSocket Hibernation is mandatory for idle clients |
| DO SQL row reads | 5,000,000/day | Batch reads and avoid chatty polling |
| DO SQL row writes | 100,000/day | Event, cursor and receipt writes need bounded batching |
| DO SQLite storage | 5 GB/account total | Retention and snapshot compaction must be measured |
| DO classes | 100/account on Free | Keep class count low |

On Free, exceeding a quota causes operations of that type to fail; it is not a license to assume automatic paid headroom. Keep the account on the zero-cost plan and treat these as hard ceilings. These limits are not a production-capacity guarantee.

A continuously active DO WebSocket can incur duration usage; use WebSocket Hibernation and explicitly model connection counts, event frequency and idle duration. Incoming WebSocket messages count toward DO request usage under the published billing rules (20:1 request accounting for incoming messages).

## 4. Legacy-to-Zero-Origin compatibility matrix

| Existing subsystem | Existing assumption | Zero-Origin disposition | Status |
|---|---|---|---|
| FastAPI app | Uvicorn process on owner host | ASGI entrypoint in Python Worker is supported; split app into compatible modules and remove server-process assumptions | 🟨 FEASIBILITY CONFIRMED, PORT NOT DONE |
| Uvicorn | Owns socket/event loop | Not used as the Worker socket server; Cloudflare ASGI runtime owns inbound request handling | 🟥 REMOVE FROM DEPLOY RUNTIME, RETAIN LOCAL TEST DEPENDENCY IF NEEDED |
| SQLite file stores | Persistent local filesystem | Durable Objects SQLite is the durable target; filesystem SQLite cannot be treated as durable in Workers | 🟥 MIGRATION REQUIRED |
| SQLite outbox | Source-host authoritative outbox | Port transaction semantics into DO SQLite or a deliberately scoped authoritative storage object | 🟥 DESIGN REQUIRED |
| Redis Streams | External Redis TLS server and consumer groups | Do not carry Redis into the Zero-Origin design by default; replace with native durable event log/coordination only after semantics and quotas are specified | 🟥 REPLACEMENT REQUIRED |
| Redis shared ticket guard | External Redis | Durable Object-backed single-use ticket/entitlement state; no in-memory-only security state | 🟥 REPLACEMENT REQUIRED |
| Databento SDK | Python SDK / live source process | Package/runtime and provider transport compatibility unverified; no assumption that its SDK or streaming transport runs on Workers | 🟥 BLOCKER |
| Firebase Admin | Admin SDK with credentials and network calls | Verify package, credential model, token verification, revocation and outbound HTTP compatibility; prefer provider-neutral verified-principal contract | 🟧 COMPATIBILITY AUDIT REQUIRED |
| Ed25519 snapshot attestation | cryptography package and local key files | Preserve signature/digest contract; test crypto package compatibility and store keys only in Worker secrets, never filesystem | 🟨 CONTRACT PRESERVATION REQUIRED |
| WebSocket | FastAPI route plus gateway worker | Worker/DO WebSocket with hibernation, bounded per-series fan-out, authenticated reconnect and durable cursor recovery | 🟨 PROOF EXISTS, PRODUCTION PORT NOT DONE |
| Metrics/coverage/alerts | Multiple local SQLite stores and background loops | Consolidate or explicitly scope durable state; background loops and local file paths cannot be copied directly | 🟥 MIGRATION REQUIRED |
| Backups | Host filesystem / off-host copy | Define export/restore from durable DO storage using zero-cost approved destination; no backup claim until restore drill | 🟥 OPEN |

## 5. Important unresolved provider constraint

A Zero-Origin Worker cannot simply run the existing always-on Databento SDK process. The current dependency and transport must be tested against the Python Workers runtime, outbound protocol support, package wheel availability, provider authentication and licensing. Do not infer compatibility from FastAPI support.

The data provider must meet all of these conditions before a live connector is enabled:
1. Lawful access and redistribution rights for the intended chart use.
2. Zero-cost access within documented quotas.
3. A transport supported by Workers (for example an authenticated HTTPS fetch/push path) and compatible with the runtime.
4. Reconnect, gap detection, sequence, timestamp, rate-limit and backfill semantics.
5. A failure mode that keeps market data explicitly unavailable rather than fabricating real-time data.

Until a source passes those checks, market data remains unavailable/synthetic-only. No synthetic fixture may be labelled as live market data.

## 6. Target architecture — proposed, not deployed

Proposed control/data path:

1. **Cloudflare Worker edge/API entrypoint**: request validation, CORS/Origin allowlist, authentication handoff, request quotas and route dispatch.
2. **Python ASGI service module**: retain compatible FastAPI route/domain logic selectively; do not import the entire CPython application graph blindly.
3. **Durable Objects SQLite**: persistent series state, snapshot generation, outbox/event log, high-water cursor, retention floor, single-use ticket state and durable receipt ledger.
4. **Series coordinator DO**: canonical per-series serialization, exact-series WebSocket fan-out, sequence enforcement, hibernation and reconnect/replay coordination.
5. **Provider ingress adapter**: separate module activated only after a lawful zero-cost provider/transport compatibility gate passes.
6. **Client WebSocket**: authenticated session, initial signed snapshot or verifiable state response, cursor replay, bounded reconnect and stale-state clearing.
7. **Backup/export path**: explicit snapshot export, integrity verification and restore drill; no silent reliance on ephemeral filesystem.

This is a design target only. Whether to use Python Workers for all HTTP routes or a small JavaScript Worker shell around a Python ASGI module must be decided by package compatibility and runtime tests, not preference alone.

### Data ownership and transaction invariants

- A canonical series has one authoritative durable sequence owner.
- Snapshot generation, digest, source identity and high-water cursor are persisted atomically.
- A live event is visible only after its durable write and cursor transition commit.
- Duplicate sequence is idempotent; sequence gap triggers replay/resnapshot, never silent skipping.
- A generation switch is explicit and cannot roll back.
- A client ACK/receipt is separate from a transport send, socket write or in-memory cursor.
- Retention cannot advance beyond the minimum durable accepted high-water receipt for every required consumer.
- WebSocket fan-out is best-effort delivery; durable state and replay remain authoritative.
- All event payloads, fan-out queues, replay windows, per-series clients and storage growth are bounded.

## 7. Gate 25 and Gate 36 under Zero-Origin

The old Gate 25 wording assumes multiple owner-hosted gateway replicas. That exact topology no longer exists in the selected Zero-Origin direction. Do not silently mark Gate 25 complete or quietly redefine the acceptance condition.

A revised Gate 25 proposal must preserve its core safety property: **durable, owner-auditable proof that each required consumer has accepted a particular authenticated snapshot generation and monotonic high-water cursor**. The proposed DO receipt ledger must include stable consumer identity, source/series identity, generation, digest, accepted cursor, monotonic version and restart reconciliation. The owner acceptance contract remains open for review.

Gate 36 remains open until a real public WSS endpoint is proven through browser and Android end-to-end tests, including TLS, Origin policy, authentication, reconnect, network handover, process death and stale-state recovery. A synthetic local Worker test is not Gate 36 evidence.

## 8. Corrected, non-looping execution sequence

This sequence replaces execution of the old owner-host Batch 80–86 plan. Existing code and tests remain reference material; no source history is discarded.

| Order | Work package | Deliverable / exit condition | Status |
|---:|---|---|---|
| 88 | Architecture alignment + platform/package audit | This Zero-Origin compatibility record; old plan explicitly superseded for execution | 🟩 DOCUMENTED |
| 89 | Python Workers compatibility spike | CI/local-runtime proof for FastAPI, Pydantic, cryptography, Firebase token path and required imports; isolate unsupported packages; no deployment | 🟨 NEXT |
| 90 | Durable data model + migration design | DO SQLite schema, atomic snapshot/outbox, generation/high-water/retention and legacy export/import mapping | 🟥 OPEN |
| 91 | Provider-neutral Worker API shell | Minimal ASGI/Worker entrypoint, fail-closed config, health/status and auth boundary; no provider feed | 🟥 OPEN |
| 92 | Series Durable Object core | Durable state, cursor, event log, replay, idempotence and bounded retention with deterministic tests | 🟥 OPEN |
| 93 | WebSocket production protocol | Hibernation, ticket/identity, session limits, reconnect, snapshot alignment and durable receipts | 🟥 OPEN |
| 94 | Provider ingress feasibility + connector | Only lawful free compatible source; otherwise explicitly report no live feed and do not fabricate | 🟥 BLOCKED ON PROVIDER |
| 95 | Public WSS/device E2E + recovery | Existing Cloudflare route mapping, TLS, browser/Android E2E, backup/restore and quota acceptance | 🟥 OPEN |

No stage is skipped. Work packages 89–95 are the active order. Do not restart Batch 80–86 in their old owner-host/Redis order.

## 9. Work package 89 — immediate test plan

The next implementation must be a non-production compatibility spike with no secrets and no Cloudflare deployment:

- Create an isolated Python Worker test entrypoint separate from `backend/app/main.py`.
- Start with the smallest FastAPI route and Cloudflare ASGI entrypoint.
- Verify Pydantic validation and JSON serialization.
- Verify Ed25519 sign/verify using the exact candidate crypto package and supported runtime.
- Verify Firebase ID-token verification strategy without embedding a service-account private key in code; determine whether remote certificate/JWKS verification can meet revocation and issuer requirements.
- Probe imports and behavior for Databento, Redis and Firebase Admin; unsupported packages must be excluded from the Worker dependency graph, not forced into it.
- Confirm DO SQLite binding API from a minimal test object.
- Test Worker and DO WebSocket hibernation/reconnect locally with deterministic synthetic events.
- Test quotas and bounded event batches using explicit load fixtures; do not extrapolate from a tiny happy-path test.
- Run the project's static checks and CI to terminal state; if the available integration cannot observe a running push workflow, report the exact limitation and do not claim completion.
- No production secrets, provider keys, account resource creation, deployment or paid fallback.

Exit condition: a compatibility matrix with PASS/FAIL/UNSUPPORTED per dependency and a minimal local Worker+DO test suite passing. No production runtime migration before this exit condition.

## 10. Indicator progress — unchanged, fully tracked in parallel

No indicator source or chart UI changes are made in this architecture cycle. The full current indicator inventory remains:

| # | Indicator / subsystem | Status | Acceptance boundary |
|---:|---|---|---|
| 1 | SMA20 | 🟨 FOUNDATION | Arithmetic mean; first valid index 19; prefix-causal and finite |
| 2 | EMA20 | 🟨 FOUNDATION | SMA-seeded; alpha 2/21; first valid index 19 |
| 3 | RSI14 Wilder | 🟨 FOUNDATION | 14-change seed; first valid index 14; stable flat/rising/falling cases |
| 4 | MACD12/26/9 | 🟨 FOUNDATION | MACD index 25; signal/histogram index 33 |
| 5 | Bollinger20,2 | 🟨 FOUNDATION | Population SD; first valid index 19; symmetric and translation-invariant |
| 6 | Shared Indicator Hook | 🟨 FOUNDATION | Exact keyed immutable snapshot; stale/demo/error/unavailable clearing |
| 7 | Footprint PRO 2GD | 🟧 GATED | Synthetic/offline accumulator only; match both saved visual references |
| 8 | Volume Profile | 🟥 OPEN | Price-bin conservation, boundaries, POC/VA method |
| 9 | Complete Volume Profile | 🟥 OPEN | Session completeness, POC/VAH/VAL and conservation |
| 10 | Movable-range Volume Profile | 🟥 OPEN | User range selection and deterministic recomputation |
| 11 | Heatmap | 🟥 OPEN | Provenance, aggregation, decay; visual reference still required |
| 12 | Liquidation Maps | 🟥 OPEN | Provenance, estimation method and confidence contract |

Focused test declaration inventory: 28 (21 calculation + 7 hook), not a passing-test count. `CandlestickChart.tsx` does not yet integrate `useMarketIndicators`. Aggregate indicator completion remains NOT SCORED.

Mathematical acceptance remains: warm-up nulls, prefix causality, no lookahead, timestamp/series identity alignment, deterministic results, finite outputs, no source mutation, bounded history, and no output for demo/loading/unavailable/error/empty snapshots. Footprint OFF must preserve normal candle spacing; only explicit Footprint ON uses spaced clusters. Heatmap visual implementation waits for the user's reference.

## 11. Project dashboard — truthful status

- Stage 1: 30/40 = 75% provisional 🟨; not whole-project completion.
- Gate 10: 0/10 formally closed 🟥; remaining criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stage 2: 🟦 PREPARATORY.
- Stage 3: ⚪ NOT SCORED.
- Stage 4: 🟪 GATED.
- Stage 5: ⚪ NOT SCORED.
- Stage 6: ⚪ NOT SCORED.
- Overall project: ⚪ NOT SCORED; no approved weighted denominator.
- Significant progress / IP3S: ⚪ NOT SCORED; no approved reproducible formula.
- Production Worker/API: 🟥 NOT DEPLOYED / NOT EVIDENCED.
- Project Gate 25: 🟥 OPEN; receipt contract requires Zero-Origin mapping review.
- Gate 36: 🟥 OPEN; public WSS/TLS/device E2E absent.
- Live market data: 🟥 OPEN; provider access and transport not yet proven zero-cost compatible.
- CI on latest docs-only commit: not run by design; do not represent as a runtime test pass.

## 12. Safety, cost and branch controls

- Branch remains `phase-2/market-data-foundation`; never modify `main`.
- ZERO COST: no Workers Paid, Containers, paid Redis, paid market data, external hosting, paid monitoring, paid backup or publication fees.
- No Cloudflare account resource creation or production deployment without explicit authorization.
- Do not enable Databento or any other provider unless legal rights, cost and runtime compatibility are proven.
- No destructive retention, delete, trim or namespace migration.
- Preserve legacy SQLite snapshots and signed attestation semantics during any future migration.
- No user-side manual edits or unverified commands are required.
- Planning target remains around 24 December 2026.

## 13. Outcome

- The architecture conflict is documented and resolved at the planning/execution-order level.
- The old owner-host/Redis Batch 80–86 plan is explicitly superseded for execution, not erased.
- Cloudflare Python Workers feasibility is distinguished from full dependency compatibility.
- Free-plan limits are included as hard capacity constraints.
- The next active package is 89, a no-deploy compatibility spike; not another generic audit.
- Indicator dashboard remains complete and honest; no unsupported completion credit is added.
