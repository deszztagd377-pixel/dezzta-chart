# DEZZTA CHART — Work Cycle 89–93: Zero-Origin Runtime Blueprint

Date: 25 November 2026  
Branch: phase-2/market-data-foundation  
Parent checkpoint: bbd6c10bc28b7e090c0c35aa405a3d2785ffa9a8  
Cost ceiling: ZERO COST  
Planning target: around 24 December 2026  
Document status: OWNER APPROVED FOR SCOPED IMPLEMENTATION — PRODUCTION ACCEPTANCE STILL OPEN

## 0. Executive result

This cycle consolidates Batches 89–93 into one ordered engineering blueprint. It resolves the boundaries between Python Worker compatibility, durable storage, provider-neutral API, the series coordinator and the production WebSocket protocol.

This is a design deliverable only. It does NOT claim Python Worker dependencies passed runtime tests, a DO schema was migrated, an API/DO implementation exists, or production WSS is available. No runtime source, production configuration, Cloudflare resource, deployment, paid service or main branch was changed.

| Batch | Deliverable | Evidence status | Implementation status |
|---:|---|---|---|
| 89 | Dependency/runtime compatibility matrix | 🟨 Inspected; runtime test not executed | 🟥 Not passed |
| 90 | DO SQLite schema, invariants, migration mapping | 🟦 Design draft | 🟥 Not migrated |
| 91 | Provider-neutral API contract | 🟦 Design draft | 🟥 Not implemented |
| 92 | Series DO state machine, event log, cursor/replay | 🟦 Design draft | 🟥 Not implemented |
| 93 | WebSocket auth, hibernation, reconnect, receipts | 🟦 Design draft | 🟥 Not implemented |
| 94 | Lawful zero-cost provider ingress | 🟥 Blocked; no provider passed evidence gate | Not started |
| 95 | Public WSS/device E2E, quota and backup/restore | 🟥 Blocked; implementation, review and deployment authorization absent | Not started |

No false green statuses are awarded. Batches 90–93 require owner review before implementation. The selected Cloudflare Native / Zero-Origin direction remains unchanged; the old owner-host/Redis execution sequence is not reintroduced.

## 1. Repository inspection and verified facts

Inspected on the active branch:

- package.json — blob 07cfadb7b71bd85fcd0d6049b8a5e00ccbc58457
- backend/requirements.txt — blob da7f78eada7bd9108ee712590f57476cbfbfd96e
- cloudflare/wrangler.jsonc — blob b25de82ed9e82d294b92a336c89b3b45153738a0
- cloudflare/proof/worker.mjs — blob b124b6886454d788f6a83d4cd2e4e692bacc7205
- cloudflare/proof/worker.node-test.mjs — blob 6238c8c3df1520a16b95c23ff8459c61a06a5fe0
- src/indicators/indicatorCalculations.ts — blob 507284fb286c633144b497b9d98c8c810250a8db
- src/indicators/useMarketIndicators.ts — blob 40188569cfc1d823bef2d814404c7bd5bb577c0c
- src/components/CandlestickChart.tsx — blob d2ec7c1e825a969b055e3e4d0109290f6f951348

The root package declares:
- test: vitest run
- test:cloudflare-runtime: installs pinned Miniflare and runs cloudflare/proof/worker.miniflare-test.mjs
- test:cloudflare-durable-objects: installs a pinned Cloudflare Vitest plugin and runs vitest.cloudflare.config.mts

These scripts establish a prepared JS Worker/DO local test path, not a passing test result and not Python Workers compatibility evidence.

Backend requirements currently include FastAPI >=0.115,<1; Uvicorn standard extras >=0.30,<1; Databento >=0.88,<1; Firebase Admin >=6.5,<8; Redis >=5.2,<7; cryptography >=50,<51.

No Python Worker project manifest or isolated Python Worker entrypoint was found at the inspected candidate paths. Do not infer that such a project already exists.

## 2. Batch 89 — Python Workers compatibility spike

### Isolation

Create a separate non-production compatibility project under proposed directory cloudflare/python-compat/. It must not import backend.app.main, modify backend requirements or become the production Worker entrypoint. No provider credentials, Firebase service-account material, production signing keys, user data or live exchange connections are allowed.

### Package compatibility matrix

| Package / subsystem | Initial classification | Required test | Fail-closed decision |
|---|---|---|---|
| FastAPI | 🟨 Candidate; ASGI integration documented | Import, app construction, route request/response in Python Worker runtime | Use only after runtime smoke test passes |
| Pydantic / pydantic-core | 🟧 Transitive runtime compatibility unknown | Import, validation, serialization, malformed-input behavior | Replace/isolate if required native extension is unavailable |
| cryptography / Ed25519 | 🟧 Pinned-version compatibility unknown | Import and sign/verify with ephemeral test key; altered payload must fail | Preserve attestation contract; isolate if unsupported |
| Firebase Admin | 🟥 Unverified | Import graph, token verification, outbound HTTP, revocation semantics | Prefer verified-principal boundary; do not assume SDK works |
| Databento SDK | 🟥 Unverified and provider-gated | Import, transport, auth, reconnect, sequence, licensing and zero-cost audit | No provider enablement until every gate passes |
| redis-py | 🟥 Excluded from default Zero-Origin runtime | Diagnostic import only; no Redis server assumption | Replace with native DO semantics only after acceptance |
| Uvicorn | 🟥 Not a Worker production socket server | Retain only for local CPython development if needed | Do not run Uvicorn inside Workers |
| Python standard library | 🟨 Module-specific | Probe each used module and filesystem/threading behavior | No durable filesystem or background-thread assumptions |

Import success alone is not a pass. Each dependency needs a runtime behavior test for the exact feature used. Record exact package versions, runtime/toolchain and test output; classify each PASS, FAIL, UNSUPPORTED or NOT TESTED.

### Minimum acceptance suite

1. Minimal FastAPI ASGI Worker starts locally.
2. Health route returns deterministic JSON.
3. Request body parsing and response serialization work.
4. Pydantic validation and malformed-input behavior work.
5. Ed25519 ephemeral test key signs/verifies; altered payload fails verification.
6. No private key is written to filesystem or committed.
7. Firebase identity seam is tested without a service-account key.
8. Databento, Redis and Firebase Admin are independently probed; unsupported imports cannot break the minimal app.
9. DO binding is exercised in local simulator only after scaffold validation.
10. WebSocket open/auth/close and restart/reconnect are tested using synthetic-only events.
11. No external provider, paid resource, deployment or production secret is used.
12. Test process exits terminally; no unattended CI job is left running.

Batch 89 becomes 🟩 only after this isolated project actually runs and the minimum suite passes on an exact recorded commit. Current status remains 🟨 inspection recorded / 🟥 runtime compatibility unverified.

## 3. Batch 90 — Durable Objects SQLite data model

### Ownership boundary

One canonical series coordinator owns ordering and the durable cursor for one canonical series key. Durable storage is authoritative; socket memory, Worker isolate memory, client-local cursor and transport send success are not authoritative. A series identity maps deterministically to one coordinator. Cross-series aggregation is outside the first implementation scope.

### Proposed logical schema (not executed SQL)

| Table | Primary identity | Purpose | Invariant |
|---|---|---|---|
| series_meta | series_key | schema version, source identity, active generation, last sequence, retention floor | one authoritative cursor per series |
| snapshot_generations | series_key + generation_id | digest, source, high-water, row count, timestamp, attestation metadata | generation and high-water commit atomically |
| series_events | series_key + sequence | ordered event payload and canonical digest | unique monotonic sequence; immutable after commit |
| consumer_receipts | series_key + consumer_id + generation_id | accepted digest, high-water, receipt version, accepted time | durable and monotonic; idempotent replay |
| websocket_tickets | ticket_digest | subject, series, purpose, expiry, consumed time | only digest stored; atomic single use |
| idempotency_records | series_key + operation_id | deduplicate retried writes | same ID/digest is idempotent; conflicting digest rejected |

Do not store bearer tickets or raw identity tokens. Store only the minimum stable consumer identity required by the accepted receipt contract.

### Transaction invariants

- Snapshot metadata, initial cursor and associated outbox state commit atomically.
- Appending sequence N requires committed high-water N-1.
- Duplicate N with same digest is idempotent; different digest is an integrity conflict.
- Sequence gap never advances cursor.
- Generation change is explicit and cannot silently rewind active generation.
- Consumer receipt cannot exceed committed event high-water.
- Receipt version increases monotonically per consumer and series.
- Retention floor cannot pass the minimum accepted high-water of required consumers plus replay safety window.
- Failed transaction leaves cursor, event and snapshot metadata unchanged.
- Payloads, replay batches, queue sizes and connection counts are bounded.

### Legacy migration mapping

| Legacy data | Proposed mapping | Migration rule |
|---|---|---|
| OHLCV rows | series_events or compacted snapshot rows | preserve canonical timestamps and exact decimal representation |
| Snapshot generation metadata | snapshot_generations | verify digest and source identity before import |
| Outbox | series_events pending/replay state | preserve sequence and event digest; no silent gap |
| high_water | series_meta.last_sequence | import only if it agrees with event tail |
| retention_floor | series_meta.retention_floor | never advance during import |
| Ed25519 attestation | snapshot metadata + external key reference | preserve signature contract; keys remain secrets |
| Consumer ACK evidence | consumer_receipts | never synthesize missing receipts |

Migration must be export-first, deterministic, repeatable and verifiable. No destructive source deletion in the first migration. Round-trip digest comparison and restore drill are mandatory.

### Quota model

Cloudflare Free limits are hard ceilings, not targets. Budget daily DO requests, SQL reads, SQL writes, storage and active connection duration. Each workload test must record series count, events/series/day, average and p95 encoded bytes, writes/event, reads/replay, snapshot size, compaction frequency, concurrent sockets, idle duration and expected daily quota consumption.

No capacity claim before measurement. If workload cannot fit Free quotas, reduce scope or find a genuinely free alternative; never silently switch to paid.

## 4. Batch 91 — provider-neutral Worker API

### Boundary

The first API shell is provider-neutral. It reports readiness and may serve only explicitly identified synthetic fixtures in local proof mode. It must never imply live market data when no provider is connected.

### Proposed routes (not implemented)

| Route | Method | Responsibility | Failure behavior |
|---|---|---|---|
| /health | GET | runtime liveness only | 503 if proof/runtime disabled |
| /v1/market-data/status | GET | provider state, provenance and availability | explicit unavailable or synthetic_only |
| /v1/series/{seriesKey}/snapshot | GET | authenticated bounded snapshot | 401/403/404/503; no demo fallback |
| /v1/series/{seriesKey}/events?after={cursor} | GET | bounded replay page | typed gap/retention response |
| /v1/auth/websocket-ticket | POST | issue one-time series-bound ticket | rate-limited; ticket redacted from logs |
| /v1/series/{seriesKey}/receipts | POST | persist consumer acceptance receipt | reject cursor beyond committed high-water |
| /v1/series/{seriesKey}/status | GET | generation, cursor and retention health | no secret or private identity leakage |

Route names must be reconciled with existing frontend API contracts before implementation.

### Response envelope

Market-data responses carry schemaVersion, sourceId, seriesKey, generationId, snapshotDigest when snapshot-backed, highWaterCursor, retentionFloor, dataStatus (live, synthetic_only, unavailable, stale, error), asOf and bounded items.

Synthetic fixtures must be labelled synthetic_only in every relevant response. Never render synthetic payload as live data.

### Security requirements

- Validate browser Origin against explicit allowlist for WebSocket handshakes.
- Authenticate before issuing a socket ticket.
- Bind ticket to subject, canonical series, purpose, expiry and one-time use.
- Hash tickets at rest and consume atomically.
- Bound body, URL, query, event and response sizes.
- Apply per-subject, per-series and global rate limits with deterministic 429/503 behavior.
- Never log tokens, cookies, private keys, credentials or sensitive identity claims.
- CORS is not authentication; Origin validation is not authentication.
- Health liveness must not reveal secret configuration.

## 5. Batch 92 — Series Durable Object core

### Proposed state machine

- UNINITIALIZED: no accepted snapshot generation.
- SNAPSHOT_READY: verified generation and high-water committed.
- STREAMING: contiguous events are being durably appended.
- GAP_DETECTED: incoming sequence is ahead of expected next sequence; cursor does not advance.
- STALE: source heartbeat/sequence freshness exceeds configured threshold.
- RECOVERY_REQUIRED: replay floor passed a client cursor or integrity check failed.
- DISABLED: explicit kill switch or integrity/security failure.

State transitions affecting correctness must be explicit, persisted and deterministically tested. Restarts reconstruct from durable storage, never module globals.

### Append algorithm contract

1. Validate schema, series/source identity, timestamp and byte bounds.
2. Begin DO SQLite transaction.
3. Read canonical generation and current high-water.
4. If N = high-water + 1, insert event and update high-water atomically.
5. If N is existing and digest matches, return idempotent duplicate.
6. If N is duplicate with different digest, reject integrity conflict.
7. If N is greater than expected, return gap; do not advance high-water.
8. If N is below retention floor, reject expired; if retained, verify duplicate identity.
9. Commit before any WebSocket fan-out.
10. Fan-out is best-effort; reconnect/replay reads committed log.

Tests must cover concurrent append, duplicate, conflicting duplicate, gap, stale generation, transaction failure, restart and retention boundaries.

### Replay contract

- Cursor is a strictly parsed canonical decimal string.
- Replay returns events strictly greater than supplied cursor.
- Page count and response bytes are bounded.
- Cursor below retention floor returns typed resnapshot_required.
- Non-contiguous replay tail marks series degraded and stops.
- Client verifies series identity, generation and sequence continuity before applying.
- No future event is applied before initial snapshot generation/high-water is accepted.

## 6. Batch 93 — WebSocket protocol and durable receipts

### Handshake and authentication

1. Client requests a one-time ticket over authenticated HTTPS.
2. Ticket is bound to subject, canonical series, purpose, expiry and single use.
3. Client opens WSS with ticket and expected series/generation/cursor.
4. DO validates Origin, ticket digest, expiry, subject and series, then consumes ticket atomically.
5. DO sends session acknowledgement with current generation/high-water.
6. Client requests replay after accepted cursor or receives bounded snapshot/resnapshot instruction.
7. Live fan-out starts only after snapshot/cursor alignment.

Never put long-lived identity bearer token in WebSocket URL. Short-lived ticket is still sensitive and must be redacted from logs.

### Message envelope

Every server event carries protocol version, message type, canonical series key, generation ID, sequence cursor, event timestamp, payload digest and bounded payload.

Client messages are limited to ACK, PING and RESUME/control. Unknown message types, malformed cursors, oversized frames and cross-series messages are rejected and counted.

### Delivery and receipt semantics

- WebSocket send completion is not consumer acceptance.
- Client-local application is not durable owner evidence.
- ACK is accepted only after server validates identity, generation, digest and cursor and commits receipt transaction.
- Receipt identity includes stable consumer ID, series, generation, snapshot digest, accepted high-water, monotonic receipt version and accepted timestamp.
- Identical replayed receipt is idempotent.
- Receipt regression or digest/generation mismatch is rejected.
- Retention uses only committed receipts for required consumers.
- Restart reconciliation reloads receipts and series high-water from durable DO SQLite.

This is the proposed Zero-Origin replacement for topology-specific owner-host replica acknowledgement wording. Project Gate 25 remains open until owner accepts the contract and tests prove it.

### Hibernation and reconnect

- Use DO WebSocket Hibernation for idle sessions.
- Persist only minimum attachment needed to reconstruct authorized identity, series and cursor.
- Revalidate attachment after wake/restart; invalid attachments close fail-closed.
- Enforce per-series and global connection caps.
- Bound pending unauthenticated sockets and authentication deadlines.
- Reconnect uses exponential backoff with jitter and hard retry ceiling.
- On reconnect, fetch current generation/high-water and replay from last durably accepted cursor.
- On generation mismatch, retention gap or digest conflict, clear stale client state and require fresh snapshot.
- Android background/foreground, network handover and process death are explicit Gate 36 E2E scenarios.

### Quota and load acceptance

Measure active sockets, idle duration, incoming control messages, outgoing events, DO RPCs, SQL reads/writes and alarm invocations. Hibernation is mandatory for idle sessions. Do not assume WebSocket traffic is free or that local tests prove Free-plan capacity.

## 7. Batch 94 — provider ingress remains a hard gate

No provider is accepted by this blueprint. A source may proceed only with evidence for all of:
1. Lawful access and redistribution terms for intended chart display.
2. Zero-cost access at expected workload.
3. Worker-compatible protocol and authentication.
4. Compatible package or direct supported transport with dependency audit.
5. Documented timestamps, sequence, reconnect, backfill, gap and rate-limit behavior.
6. No continuously running owner-host process requirement.
7. End-to-end provenance carried into snapshot and chart state.

If any item fails or remains unverifiable, Batch 94 stays 🟥 BLOCKED and application reports market data unavailable. Do not substitute generated candles.

## 8. Batch 95 — production acceptance and deployment boundary

Batch 95 cannot be completed in this cycle: runtime is not implemented, blueprint is not owner-approved and deployment/resource creation is not authorized.

Required evidence before Gate 36 closure:
- exact production Worker and DO source SHA;
- explicit owner authorization for resource creation/deployment;
- verified route, domain, TLS and WSS endpoint;
- browser Origin allowlist and authenticated ticket flow;
- browser E2E and Android device E2E;
- reconnect after Wi-Fi/mobile network handover;
- app background/foreground and process-death recovery;
- snapshot generation/high-water alignment and replay;
- durable receipt commit and restart reconciliation;
- quota budget under expected load;
- export, integrity verification and restore drill;
- zero paid services and no surprise plan upgrade.

Local Miniflare is not public WSS evidence. Deployment without device E2E is not Gate 36 acceptance.

## 9. Complete indicator progress dashboard (12 items)

No indicator implementation is claimed in this backend cycle. Existing inventory remains:

| # | Indicator / subsystem | Current status | Next concrete acceptance |
|---:|---|---|---|
| 1 | SMA20 | 🟨 FOUNDATION | Chart overlay, toggle, legend, latest value and lifecycle |
| 2 | EMA20 | 🟨 FOUNDATION | Chart overlay, toggle, legend, latest value and lifecycle |
| 3 | RSI14 Wilder | 🟨 FOUNDATION | Dedicated 0–100 pane, 30/70 guides, toggle and lifecycle |
| 4 | MACD12/26/9 | 🟨 FOUNDATION | Dedicated pane, MACD/signal lines, histogram and zero guide |
| 5 | Bollinger20,2 | 🟨 FOUNDATION | Upper/middle/lower overlays, fill, legend and lifecycle |
| 6 | Shared Indicator Hook | 🟨 FOUNDATION | Chart integration after scoped Stage 4 review; preserve exact series/snapshot trust gate |
| 7 | Footprint PRO 2GD | 🟧 GATED | Match the two saved user references; synthetic accumulator is not exchange-native bid/ask |
| 8 | Volume Profile | 🟥 OPEN | Define binning, volume allocation, POC/VAH/VAL and deterministic tests |
| 9 | Complete Volume Profile | 🟥 OPEN | Define complete session coverage, session boundaries, POC/VAH/VAL and missing-data behavior |
| 10 | Movable-range Volume Profile | 🟥 OPEN | Define range selection, recomputation, zoom/scroll interaction and lifecycle |
| 11 | Heatmap | 🟥 OPEN | Obtain user visual reference; define lawful depth provenance, aggregation, decay and stale-state handling |
| 12 | Liquidation Maps | 🟥 OPEN | Define lawful provenance, estimation methodology, confidence labels and non-fabrication policy |

Mathematical contracts remain unchanged: SMA20 first valid index 19; EMA20 first valid index 19 with SMA seed and alpha 2/21; RSI14 Wilder first valid index 14; MACD line index 25 and signal/histogram index 33; Bollinger20,2 first valid index 19 using population standard deviation.

Global acceptance: warm-up nulls, prefix causality, no lookahead/repaint, exact series/timestamp alignment, deterministic finite output, no source mutation, bounded history, stale-output clearing and no output for demo/loading/unavailable/error/empty snapshots.

Footprint OFF preserves ordinary candle spacing. Only explicit Footprint ON switches to spaced candle clusters. Heatmap visual implementation remains blocked on user's reference. The 28 existing test declarations are not a passing-test count.

## 10. Non-looping execution order and blockers

| Priority | Blocker | Next action | Gate |
|---:|---|---|---|
| P0 | Batch 89 runtime not executed | Build isolated compatibility project and run exact matrix | No secrets / no deployment |
| P0 | Detailed Zero-Origin blueprint needs review | Review this document before implementation | Owner review |
| P0 | DO schema not migrated | Implement only after schema review | No destructive migration |
| P0 | Production WebSocket proof absent | Implement Batches 92/93 after review, then local tests | Gate 25/36 remain open |
| P1 | Provider unknown | Lawful zero-cost provider audit | Batch 94 blocked |
| P1 | Public WSS/device E2E absent | Only after implementation and explicit deployment authorization | Batch 95 blocked |
| P1 | Indicator UI not integrated | Separate Stage 4 scoped blueprint and review | No unsolicited UI expansion |

Execution order remains strictly 89 → 90 → 91 → 92 → 93 → 94 → 95. Do not restart historical Batch 80–86. Do not mark a package successful because design was written. CI terminal status must be checked on exact commit; do not claim background monitoring if connector cannot verify it.

## 11. Conservative progress scoring

- Batch 89: 🟨 source/dependency inspection recorded; runtime PASS not established.
- Batch 90: 🟦 schema and migration design drafted; not implemented/migrated.
- Batch 91: 🟦 API contract drafted; not implemented.
- Batch 92: 🟦 DO state/event/replay design drafted; not implemented.
- Batch 93: 🟦 WebSocket/receipt protocol drafted; not implemented.
- Batch 94: 🟥 blocked; no qualifying provider evidence.
- Batch 95: 🟥 blocked; implementation, review and deployment authorization absent.
- WebSocket production completion: 🟥 NOT COMPLETE.
- Project Gate 25: 🟥 OPEN.
- Gate 36: 🟥 OPEN.
- Stage 1: 30/40 = 75% provisional 🟨; not overall project completion.
- Overall project progress: ⚪ NOT SCORED; approved weighted denominator absent.
- Significant progress / IP3S: ⚪ NOT SCORED; approved reproducible formula absent.
- Aggregate indicator completion: ⚪ NOT SCORED; no approved weighted denominator.

No percentage is invented from document count, test declarations or batch count.

## 12. Safety and cost controls

- ZERO COST is a hard requirement. No paid Workers plan, Containers, paid provider, paid database, paid hosting, paid backup or paid monitoring.
- No Cloudflare resource creation or deployment in this cycle.
- No production secret or private key in repository.
- No provider or synthetic data mislabeling.
- No main branch modification.
- No destructive migration, retention trim or history rewrite.
- No code is claimed tested unless a test command actually ran and terminal result is recorded.
- Preserve legacy work as historical evidence; supersede execution order, not source history.


## 13. Official Python Workers documentation verification addendum

A fresh review of Cloudflare's current official documentation confirms that FastAPI is supported in Python Workers through Cloudflare's ASGI entrypoint. The documented minimal project uses:

- Python entrypoint importing FastAPI and workers.asgi, then assigning Default = asgi.entrypoint(app).
- Wrangler main pointing to the Python entrypoint and compatibility_flags containing python_workers.
- pyproject.toml with Python >=3.13, FastAPI dependency, and workers-py plus workers-runtime-sdk as development dependencies.
- Local-only runtime command: uv run pywrangler dev. The deployment command is deliberately excluded from this project cycle.

Official documentation:
- FastAPI on Python Workers: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
- Python package support and Pywrangler: https://developers.cloudflare.com/workers/languages/python/packages/
- Python Workers basics and local runtime: https://developers.cloudflare.com/workers/languages/python/basics/

This confirms the platform-level FastAPI/ASGI feasibility, not compatibility of this repository's complete dependency set. Pydantic's exact version, cryptography/Ed25519, Firebase Admin, Databento and Redis remain separate test gates. No isolated Worker scaffold was committed in this cycle because the local runtime could not be executed and a passing code artifact must not be guessed into the repository. Batch 89 therefore remains 🟨 platform feasibility confirmed / 🟥 repository runtime acceptance not executed.


## 13. Owner approval and source-level WebSocket gap audit — 25 November 2026

The project owner explicitly approved this blueprint in the current conversation. The blueprint is now the authorized basis for scoped implementation of Batches 89–93. This approval does not authorize Cloudflare resource creation, deployment, paid services, changes to main, or bypassing test gates.

### 13.1 Existing synthetic Worker source audit

The existing proof Worker and Durable Object source were re-read at the approved branch checkpoint. They remain explicitly synthetic-only and are not production WebSocket infrastructure. The audit found the following concrete gaps against the approved contract:

| Finding | Existing behavior | Consequence | Required correction |
|---|---|---|---|
| Event durability | acceptNextSequence persists only sequence:<series>; the event payload is not appended to a durable replay log | Sequence high-water can advance without a recoverable event | Atomically persist event digest/payload and high-water in one DO SQLite transaction |
| Fan-out boundary | Event is sent to sockets after sequence transaction commits | Runtime failure between commit and send loses delivery; there is no durable replay path | Fan-out only after durable append; replay from committed cursor |
| Client ACK | Authenticated sockets accept ping; other messages are closed | No client acceptance proof | Add bounded ACK schema and durable receipt commit |
| Resume/replay | No durable event replay endpoint or RESUME protocol | Reconnect cannot recover missed updates | Add cursor-bound replay with retention-floor response |
| Consumer identity | Synthetic proof subject is a single fixed test identity | No production user/device/consumer identity assurance | Integrate a verified-principal boundary only after Firebase/token compatibility and authorization tests |
| Snapshot proof | Synthetic snapshot generation/watermark are fixed fixture values | No signed production snapshot-generation acceptance | Bind real generation ID, digest and attestation after verified snapshot import |
| Provider | No provider is connected; events are deterministic fixtures | Cannot claim live market data | Preserve synthetic_only labeling; Batch 94 remains blocked |

These are not newly introduced defects in the proof: the file header explicitly scopes the Worker to synthetic-only experimentation. The problem would be promoting this proof as if it satisfied production requirements. That promotion is prohibited.

### 13.2 WebSocket implementation acceptance tests

The next implementation must add tests for each item below before the corresponding status can turn green:

1. Event and high-water commit atomically; injected transaction failure changes neither.
2. Duplicate sequence with identical digest is idempotent.
3. Duplicate sequence with different digest is rejected as integrity conflict.
4. Sequence gap does not advance high-water.
5. Event is replayable after DO eviction/recreation.
6. Fan-out occurs only after durable commit.
7. Client ACK is validated against series, generation, digest and committed high-water.
8. ACK receipt is persisted and remains queryable after DO eviction.
9. Receipt version is monotonic; replayed identical ACK is idempotent; regression is rejected.
10. RESUME returns a contiguous bounded replay page from the accepted cursor.
11. Cursor below retention floor returns explicit resnapshot_required.
12. Generation mismatch prevents stale replay and requires a new snapshot.
13. Two sockets racing to ACK/consume a ticket cannot create duplicate or regressing receipt state.
14. Hibernation wake and DO eviction preserve authorized session identity and cursor attachment.
15. Android/browser reconnect after process death and network handover is tested at Gate 36.

### 13.3 Batch 89 execution environment gate

The current GitHub connector provides repository file operations, not a checked-out working tree or command runner. The available local container could not resolve github.com, so the repository could not be cloned for an isolated runtime test. No Python Worker code was committed without the ability to run its syntax, dependency and runtime tests. This is an execution-environment limitation, not a package compatibility PASS.

To avoid a false success or broken artifact, Batch 89 remains 🟨 platform-level FastAPI/ASGI feasibility documented / 🟥 exact repository runtime test NOT EXECUTED. The next implementation session must use an already-authorized zero-cost local runner or a repository-connected test runner; it must not provision a paid sandbox or Cloudflare resource.

### 13.4 Stage 1 critical-path acceleration

Stage 1 is expected to be the longest foundation stage because it carries the data-integrity, security, persistence and client-delivery gates. Acceleration must come from parallelizing independent evidence work, not skipping acceptance:

- Track A: Batch 89 Python runtime/package compatibility.
- Track B: Batch 90 DO SQLite schema, migration and transaction invariants.
- Track C: Batch 91 API contract/frontend compatibility.
- Track D: Batch 92/93 event log, replay, ACK receipt and reconnect.
- Shared release gate: one exact commit, deterministic tests, terminal CI, quota budget and restore proof.

Tracks B–D may be designed in parallel but implementation dependencies remain ordered: schema and invariants before event engine; event engine before replay/ACK; replay/ACK before public WSS E2E. Batch 94 provider evaluation remains isolated and cannot block offline synthetic protocol testing. Batch 95 remains last.

The target of approximately 24 December 2026 remains a planning target. No completion date is guaranteed by documentation progress.


## 14. Execution checkpoint — source re-audit and safe implementation gate (25 November 2026)

This addendum records a fresh read of the active branch after the owner-approved blueprint. It does not change the architecture or acceptance order.

### 14.1 Exact source-level finding

The current `cloudflare/proof/worker.mjs` is a synthetic-only proof, not a production market-data service:

- `acceptNextSequence(storage, seriesKey, sequence)` transactionally updates only `sequence:<seriesKey>`; it does not insert an immutable event payload or payload digest.
- The `/__proof/emit` path constructs a synthetic update after sequence acceptance and then iterates authenticated sockets to send it. Thus the committed cursor is not backed by a replayable event record. A process interruption after cursor commit and before socket delivery has no durable event from which to recover.
- `webSocketMessage` authenticates a one-time synthetic proof ticket, sends a generated synthetic snapshot, and supports `ping`/pong. Other authenticated client message types are closed as unsupported. ACK and RESUME are not implemented.
- The snapshot is generated from deterministic fixtures and labels itself `synthetic_only_not_market_data`; it is not a verified production snapshot or provider feed.
- Existing serialized socket attachments support hibernation restoration of the proof identity, but that proof identity is fixed and is not a production subject/device authorization model.

These are intentional proof boundaries. Do not patch around them by relabelling the proof as production or by treating successful socket send as durable delivery.

### 14.2 Runtime execution boundary

The root `package.json` declares `test`, `test:cloudflare-runtime`, and `test:cloudflare-durable-objects`. The two Cloudflare-specific scripts install pinned tooling before executing the repository tests. The connector available in this session can read/write GitHub files and inspect commit/status metadata, but it does not expose a checked-out working tree or command runner. The local container also cannot resolve GitHub to obtain a clone. Therefore this session cannot honestly execute the repository's Vitest/Miniflare/DO runtime suites.

No runtime implementation is to be committed until an already-authorized zero-cost runner is available and can execute the exact repository scripts. This is a quality gate, not permission to introduce paid CI, a hosted sandbox, a Cloudflare resource, or a new service.

### 14.3 Next executable sequence (non-looping)

1. **Batch 89 — runner and Python Workers spike:** use an existing zero-cost local/repository runner; execute the isolated minimal FastAPI/ASGI probe and exact dependency probes. Record versions, terminal output and exact commit. Do not add Python packages to the production Worker until each required feature passes.
2. **Batch 90 — schema:** implement only after runner availability; migrate schema in a disposable local DO simulator, verify migration idempotence, transaction rollback and legacy digest parity.
3. **Batch 91 — API shell:** reconcile every proposed route with existing frontend contracts first; synthetic status must remain explicitly synthetic and unavailable must fail closed.
4. **Batch 92 — event engine:** atomically insert event payload + canonical digest + high-water; prove duplicate idempotency, conflicting duplicate rejection, gap rejection, rollback and eviction replay.
5. **Batch 93 — delivery protocol:** implement ACK/RESUME only on top of the durable event engine; persist monotonic receipts and test races, generation mismatch, retention floor and restart reconciliation.
6. **Batch 94 — provider:** remain blocked unless lawful terms, technical compatibility and genuinely zero-cost access are evidenced.
7. **Batch 95 — public acceptance:** only after prior gates and separate explicit deployment authorization; browser/Android WSS, TLS, reconnect, quota and restore evidence required.

### 14.4 No false completion

At this checkpoint Batches 89–95 retain their existing statuses. The source audit increases confidence in the blocker diagnosis, not implementation completion. Gate 25 and Gate 36 remain open; no live provider, public WSS, production Worker or durable ACK receipt is claimed. No Cloudflare resource, deployment, paid service or `main` branch change is authorized or performed.


## 15. Existing WebSocket test inventory and acceptance gap map — 25 November 2026

A fresh source-level inventory found **43 declared test cases** across three existing suites. This is a declaration count, not a test execution or pass count:

| Existing suite | Declared cases | Runtime scope |
|---|---:|---|
| `cloudflare/proof/worker.node-test.mjs` | 31 | Node-level validation, synthetic contract, request bounds, tickets, sequence gate and proof behavior |
| `cloudflare/proof/worker.durable-object.runtime.mjs` | 11 | Cloudflare Vitest/DO runtime: authenticated fan-out, snapshot watermark, single-use ticket/races, attachment restoration, alarms, series binding, duplicate/gap cursor behavior |
| `cloudflare/proof/worker.miniflare-test.mjs` | 1 | Miniflare/workerd integration for real local WebSocket, DO storage and fan-out |
| **Total** | **43** | **Not executed in this session** |

### 15.1 Existing coverage versus the 15 production acceptance tests

| # | Required production acceptance | Existing source-level coverage | Remaining gap |
|---:|---|---|---|
| 1 | Event payload and high-water atomic; rollback injected | 🟥 None | Implement event row + cursor in one transaction and rollback test |
| 2 | Same sequence/digest idempotent | 🟨 Partial | Existing duplicate cursor rejection does not compare payload digest |
| 3 | Same sequence/different digest conflict | 🟥 None | Canonical digest conflict behavior |
| 4 | Sequence gap never advances high-water | 🟩 Proof-only behavior | Re-test against durable event store, not cursor-only proof |
| 5 | Replay after DO eviction/recreation | 🟥 None | Persisted event rows and replay after eviction |
| 6 | Fan-out only after durable commit | 🟨 Partial | Current test verifies fan-out but not injected failure between commit and send |
| 7 | ACK bound to series/generation/digest/high-water | 🟥 None | ACK protocol and validation |
| 8 | ACK receipt durable after eviction | 🟥 None | Consumer receipt table and post-eviction query |
| 9 | Monotonic receipt version/idempotent replay/no regression | 🟥 None | Receipt version transaction and regression tests |
| 10 | Bounded contiguous RESUME page | 🟥 None | Cursor protocol, page bound and contiguity tests |
| 11 | Below retention floor returns resnapshot_required | 🟥 None | Retention floor semantics and explicit response |
| 12 | Generation mismatch prevents stale replay | 🟥 None | Generation-bound cursor/replay tests |
| 13 | Racing ACK/ticket consumption cannot duplicate/regress receipt | 🟨 Partial | Ticket race is tested; ACK receipt race is not |
| 14 | Hibernation wake + DO eviction preserve authorized identity and cursor | 🟨 Partial | Attachment restoration exists; durable cursor/replay restoration is not proven |
| 15 | Android/browser process death + network handover | 🟥 None | Device E2E at Gate 36 |

🟩 here means only the narrow synthetic proof behavior is covered by existing test source; it does not close a production gate. 🟨 means adjacent or partial coverage only. None of the 15 production acceptance items is accepted solely from this inventory.

### 15.2 Correct interpretation of the inventory

- 43 test declarations do not mean 43 tests passed.
- The 11 DO runtime cases and 1 Miniflare case require the repository's Cloudflare runtime test commands; they were not run in this session.
- Existing ticket-consumption race tests are not ACK receipt race tests.
- Existing serialized socket attachment restoration is not proof of durable event replay or cursor restoration.
- Existing sequence-gap tests exercise the synthetic cursor gate, not atomic event payload + digest + high-water.
- No test has been added or modified in this audit. Do not change production acceptance statuses based on test-name presence.

The first implementation test batch must be introduced with Batch 90/92 schema and event engine work, then the remaining ACK/replay/device cases in dependency order. No new code is safe to commit until a zero-cost runner can execute the exact suites.


---

# Coordinated implementation contract reference — Batches 90–95 (25 November 2026)

The cross-batch logical schema, event transaction, replay cursor, ACK/receipt protocol, RESUME state machine, provider-neutral envelopes, zero-cost provider gate, failure-injection matrix and public WSS/device acceptance are consolidated in [BATCH90_95_DURABLE_WEBSOCKET_DELIVERY_SPEC.md](BATCH90_95_DURABLE_WEBSOCKET_DELIVERY_SPEC.md), commit `327cac59c17894859d0deb6ac99644cdd3aa101f`.

This is a design reference, not implementation or production acceptance. Batch 89 runtime validation remains the prerequisite. Batch 90 schema → Batch 92 event/replay → Batch 93 ACK/recovery dependencies remain strict; Batch 91 contract preparation can be parallelized where independent. Batch 94 provider ingress and Batch 95 public WSS remain gated. No new Cloudflare SQL API syntax is assumed before runtime compatibility is demonstrated.
