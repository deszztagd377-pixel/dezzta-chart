# Batch 89–93 — Source Audit and Execution Readiness Record

**Audit date:** 25 November 2026  
**Audited branch:** `phase-2/market-data-foundation`  
**Audited HEAD:** `5004d47ac9a492032f275c6df610b875a8b2d869`  
**Architecture:** Cloudflare Native / Zero-Origin  
**Scope:** Batch 89 execution readiness and Batch 90–93 source blockers  
**Result:** Static repository audit completed; runtime acceptance remains OPEN.

## 1. Exact repository evidence

The following files were read from the audited branch:

| File | Blob SHA |
|---|---|
| `package.json` | `07cfadb7b71bd85fcd0d6049b8a5e00ccbc58457` |
| `package-lock.json` | `f7edcad1381f2348dabd45e71f3b31e62af47123` |
| `cloudflare/wrangler.jsonc` | `b25de82ed9e82d294b92a336c89b3b45153738a0` |
| `cloudflare/proof/worker.mjs` | `b124b6886454d788f6a83d4cd2e4e692bacc7205` |
| `cloudflare/proof/worker.node-test.mjs` | `6238c8c3df1520a16b95c23ff8459c61a06a5fe0` |
| `cloudflare/proof/worker.durable-object.runtime.mjs` | `b6cf9438e2c2f124c6e1b170581226f2957e1020` |
| `cloudflare/proof/worker.miniflare-test.mjs` | `74ef3daf4b9a9951e21d4710790329b4d8c6f117` |
| `vitest.cloudflare.config.mts` | `4fbbeb51fa0354a999681a1c951cdf12ec0f7132` |
| `scripts/report-npm-audit.mjs` | `85b150e6dfce25802b5e07ff24b379da839f950b` |

The branch comparison against the preceding project checkpoint found one intervening commit, with no branch divergence. The intervening commit updates the indicator ledger; it is retained and not overwritten.

## 2. Batch 89 — package and test harness inspection

### 2.1 Lockfile consistency

Static JSON inspection found:
- `package-lock.json` uses lockfileVersion 3.
- Root package name/version match `dezzta-chart@1.0.0`.
- Every root dependency and devDependency declaration in `package.json` has an identical version range in the lockfile root package metadata.
- No root dependency declaration mismatch was found.
- `package.json` does not declare a Node.js engine range.

This is a metadata consistency check only. It does not replace `npm ci`, package integrity verification, runtime compatibility testing, or an install.

### 2.2 Test declaration inventory

Static declaration scan found:

| Test surface | Declared tests | Execution result |
|---|---:|---|
| `cloudflare/proof/worker.node-test.mjs` | 31 | NOT RUN |
| `cloudflare/proof/worker.durable-object.runtime.mjs` | 11 | NOT RUN |
| `cloudflare/proof/worker.miniflare-test.mjs` | 1 | NOT RUN |
| **Cloudflare proof-specific declarations** | **43** | **NOT RUN** |

The 43 declarations are a source inventory, not a passing-test count. The application-wide Vitest suite count has not been computed in this audit.

### 2.3 Ordered acceptance commands

The current package scripts still define the Batch 89 sequence:
1. `npm ci`
2. `npm test -- --reporter=verbose`
3. `npm run build`
4. `npm run test:cloudflare-runtime`
5. `npm run test:cloudflare-durable-objects`
6. `git status --short`

Rows 2–5 are the four validation commands. All four must exit 0, with complete logs and exact tested SHA. Setup and final hygiene must also succeed. Node/npm versions must be captured at execution time because no Node engine is declared in the package manifest.

The current tool connection provides repository file/commit/status inspection but no checked-out repository command runner. No install, build, test, audit or Git working-tree command was executed. Batch 89 therefore remains OPEN; no test pass is inferred.

## 3. Batch 92 — verified source-level event-delivery blocker

The current `acceptNextSequence(storage, seriesKey, sequence)` transaction writes only the `sequence:<series>` cursor. The inspected emit handler then constructs the synthetic event after that transaction returns and sends it to connected sockets.

Consequences:
- The event payload and digest are not stored with the sequence.
- The sequence transaction is not an event-log transaction.
- If execution stops after cursor commit but before fan-out, the accepted event has no durable replay payload in the inspected source.
- Existing fan-out tests prove delivery to currently connected sockets for the exercised case, not crash recovery of a committed event.

**Required Batch 92 change:** event payload, canonical digest and high-water must be committed atomically. Fan-out must occur only after that commit. Replay must read from the durable event log and enforce contiguous bounded cursors.

No runtime code was changed because it cannot be executed and verified in the available environment.

## 4. Batch 93 — verified protocol blocker

The current authenticated `webSocketMessage` path accepts `ping` and sends `pong`; other authenticated messages are rejected as unsupported synthetic proof messages.

The inspected source has no implemented:
- ACK request validation;
- durable consumer receipt ledger;
- monotonic receipt version;
- RESUME request/response;
- replay cursor recovery;
- retention-floor resnapshot response.

The DO eviction runtime tests restore serialized socket attachments and send a ping/pong after eviction. That demonstrates attachment restoration and socket message continuity for that test; it does not demonstrate durable event replay, ACK receipt recovery, or authenticated resume after process death.

**Required Batch 93 change:** authenticate stable consumer identity; validate ACK against series, generation, committed sequence and exact digest; persist a monotonic receipt transactionally; implement bounded RESUME and explicit resnapshot behavior; prove recovery after eviction.

## 5. Batch 90–91 — implementation gate

The current Wrangler config declares only migration `v1` for `SeriesCoordinatorDO`. No event-log/receipt migration is present in the inspected config. The schema/API design is specified in `BATCH90_95_DURABLE_WEBSOCKET_DELIVERY_SPEC.md`, but no corresponding runtime migration or provider-neutral endpoint implementation is accepted.

Batch 90 must preserve v1 compatibility and prove the new SQLite schema in the actual local Durable Object runtime. Batch 91 may prepare independent envelope/contract tests in parallel, but it must not claim a production API or bypass canonical event validation.

## 6. Consolidated Batch 89–93 status

| Batch | Static evidence | Runtime implementation | Acceptance |
|---:|---|---|---|
| 89 | 🟨 Scripts and lock metadata inspected | ⚪ Not executed | 🟥 OPEN |
| 90 | 🟦 Logical schema specified | ⚪ Not implemented | 🟥 OPEN |
| 91 | 🟦 API envelope specified | ⚪ Not implemented | 🟥 OPEN |
| 92 | 🟥 Source blocker confirmed | ⚪ Not implemented | 🟥 OPEN |
| 93 | 🟥 Protocol blocker confirmed | ⚪ Not implemented | 🟥 OPEN |

## 7. Next implementation order and parallel work

The dependency order remains:
- Batch 89 runtime gate first.
- Batch 90 schema and migration.
- Batch 91 provider-neutral API contract.
- Batch 92 atomic event log and bounded replay.
- Batch 93 ACK, durable receipts, RESUME and recovery.

Parallelize only independent preparation: schema review, API contract test design, failure-injection test design and provider-neutral protocol review. Serialize schema migrations and shared runtime source edits. Batch 92/93 runtime acceptance cannot precede the schema/runtime gate.

## 8. Zero-cost and safety constraints

- No paid runner, paid service, hosted database, paid data feed or deployment.
- No Cloudflare resource creation.
- No production WSS enablement.
- No live market-data claims from synthetic proof fixtures.
- No changes to `main`.
- No runtime code commit without a supported execution path and captured validation evidence.
- A missing, skipped, timed-out or logless test is OPEN, not PASS.

## 9. Project and indicator accounting

This audit is backend-only. Indicator implementation credit for this cycle is **0**. All 12 indicator statuses remain as recorded in `INDICATOR_PROGRESS_LEDGER.md`; calculation declarations are not converted to passing tests. Stage 1 remains 30/40 = 75% provisional, Gate 10 remains 0/10 formally closed, and overall project progress / IP3S remain NOT SCORED.

The project target remains around 24 December 2026. The date is a planning target, not a reason to waive runtime or data-provenance acceptance.


## 10. Additional snapshot/live boundary race — test required before acceptance

A second ordering hazard was identified in the current source path and is recorded as a **potential interleaving race**, not as a reproduced runtime failure:

1. `webSocketMessage` awaits `consumeTicket(...)`.
2. `consumeTicket` transaction reads the current `sequence:<series>` value and deletes the one-time ticket, then returns the captured `snapshotWatermark`.
3. After that awaited transaction resolves, the handler marks the socket attachment authorized and sends the snapshot synchronously.
4. The emit handler advances the cursor and fans out only to sockets already marked authorized.

If an emit is scheduled after the consume transaction commits but before the authentication continuation marks the socket authorized, the new event may be omitted from fan-out while the snapshot still carries the earlier watermark. The existing test named `snapshot captures the current cursor and next live update follows its watermark` verifies the ordinary ordering but does not, by its inspected assertions, force this exact interleaving.

**Required regression proof:** deterministically pause authentication immediately after ticket-consumption transaction completion; commit the next event while the socket is not yet authorized; resume authentication; then prove the client receives either (a) a snapshot at or beyond the new committed cursor, or (b) a contiguous replay beginning immediately after the snapshot watermark. No event may be silently lost or duplicated. Repeat with two concurrent auth/emit schedules and under the actual pinned Miniflare/DO runtime.

**Implementation constraint:** do not fix this by moving the cursor read later without a replayable event log. The durable Batch 92 event log and Batch 93 bounded RESUME path are the intended foundation for closing this race. Keep the socket snapshot/live boundary explicit and testable.

This is a source-ordering risk requiring deterministic runtime reproduction. It does not change the 15 acceptance statuses or imply a test passed. Batch 92/93 remain OPEN.
