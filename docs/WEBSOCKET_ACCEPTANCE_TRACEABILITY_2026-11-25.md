# WebSocket Acceptance Traceability and Indicator Reconciliation — 25 November 2026

**Branch:** `phase-2/market-data-foundation`  
**Pre-documentation HEAD:** `572abed1dbab52d23f87074023f3b9a53a90b7e2`  
**Architecture:** Cloudflare Native / Zero-Origin  
**Cost boundary:** ZERO COST; no paid runner, hosting, market-data feed, deployment, or Cloudflare resource creation.  
**Purpose:** map the approved durable-delivery acceptance contract to the exact current synthetic proof tests, distinguish existing coverage from missing coverage, and preserve the complete 12-row indicator ledger without inflating progress.

## 1. Current source baseline

The following source blobs were read from the branch at the pre-documentation HEAD:

| File | Blob SHA | Static declaration count |
|---|---|---:|
| `cloudflare/proof/worker.node-test.mjs` | `6238c8c3df1520a16b95c23ff8459c61a06a5fe0` | 31 |
| `cloudflare/proof/worker.durable-object.runtime.mjs` | `b6cf9438e2c2f124c6e1b170581226f2957e1020` | 11 |
| `cloudflare/proof/worker.miniflare-test.mjs` | `74ef3daf4b9a9951e21d4710790329b4d8c6f117` | 1 |
| `cloudflare/proof/worker.mjs` | `b124b6886454d788f6a83d4cd2e4e692bacc7205` | — |

**43 is a declaration inventory, not a pass count. All 43 remain NOT RUN in this work cycle.** No Node, npm, Vitest, Miniflare, build, audit, or working-tree command was executed.

## 2. Fifteen-point durable WebSocket acceptance traceability

Status meanings: 🟩 existing source/test coverage for the narrow stated behavior; 🟨 partial or adjacent coverage only; 🟥 missing implementation/acceptance. None of these statuses means runtime tests passed.

| # | Required acceptance | Existing exact test evidence | Disposition |
|---:|---|---|---|
| 1 | Event payload, digest and high-water commit atomically; transaction failure changes none | No event-log transaction or payload/digest persistence found; cursor-only `acceptNextSequence` exists | 🟥 |
| 2 | Same sequence + same digest is idempotent | Existing duplicate sequence is rejected as `sequence_conflict`; no digest identity exists | 🟥 |
| 3 | Same sequence + different digest is a hard conflict | No persisted digest comparison | 🟥 |
| 4 | Sequence gap leaves high-water unchanged | `series sequence gate rejects gaps, duplicates, and accepts only the next cursor`; DO test `rejects duplicate and skipped cursors without fan-out, then accepts the next contiguous cursor` | 🟨 |
| 5 | Committed event replays after DO eviction/recreation | Existing eviction tests restore socket attachments, not durable event payload/replay | 🟥 |
| 6 | Fan-out occurs only after durable event commit | Current source fans out after cursor-only commit; payload is constructed after cursor acceptance | 🟥 |
| 7 | ACK validates series, generation, sequence, digest and committed high-water | No ACK protocol or validator found | 🟥 |
| 8 | ACK receipt is durable and queryable after eviction | No consumer receipt ledger found | 🟥 |
| 9 | Receipt version is monotonic; identical replay idempotent; regression rejected | No receipt version or receipt mutation path found | 🟥 |
| 10 | RESUME returns contiguous bounded replay page | No RESUME handler or durable event-log query found | 🟥 |
| 11 | Cursor below retention floor returns explicit `resnapshot_required` | No retention-floor state or response found | 🟥 |
| 12 | Generation mismatch prevents stale replay | Current snapshot uses fixed synthetic generation; no durable generation-bound replay validation | 🟥 |
| 13 | Two concurrent consumers cannot create duplicate/regressing receipt | Ticket single-use race is tested, but no ACK/receipt race exists | 🟥 |
| 14 | Hibernation/DO eviction preserves authorized identity and reconnect cursor | Tests `restores serialized socket identity and resumes messages after DO eviction` and `restores every authenticated socket attachment after Durable Object eviction`; cursor replay is not covered | 🟨 |
| 15 | Browser/Android reconnect after process death/network handover at Gate 36 | No public WSS/TLS/device E2E evidence in this source set | 🟥 |

### Existing coverage that must be preserved

The source already tests canonical series validation, sequence parsing, deterministic synthetic OHLCV, bounded snapshots, single-use ticket concurrency, ticket expiry/series binding, fail-closed proof mode/auth/origin, bounded JSON parsing, socket capacity, snapshot/live watermark ordering, exact-series fan-out, failed-socket isolation, attachment validation, unauthenticated socket alarms, and attachment restoration after DO eviction.

These are valuable security and regression foundations. They must not be removed or weakened when durable event delivery is implemented. However, none substitutes for the missing event log, digest-bound ACK, receipt ledger, RESUME, retention-floor, generation, or device-E2E behavior.

## 3. Source blockers confirmed at this checkpoint

1. `acceptNextSequence(storage, seriesKey, sequence)` persists only `sequence:<series>`.
2. The synthetic event payload is constructed after cursor acceptance; neither payload nor canonical digest is committed atomically with high-water.
3. A failure after cursor commit but before socket fan-out leaves no durable payload to replay.
4. Authenticated `webSocketMessage` accepts ping/pong only; ACK and RESUME are not implemented.
5. No durable consumer receipt schema, monotonic receipt version, or retention-floor contract exists in the inspected runtime.
6. Wrangler migration history contains only the existing v1 `SeriesCoordinatorDO` migration; additive event/receipt schema migration is not implemented.
7. Existing eviction tests prove attachment restoration and ping/pong continuity only, not replay or receipt recovery.

## 4. Correct dependency order and parallelization

The approved sequence remains strict:

1. **Batch 89 — runtime gate:** `npm ci`; app tests; production build; Miniflare runtime; Durable Object runtime; final working-tree hygiene. Capture Node/npm versions, logs, exit codes and exact SHA. All four validation commands must pass.
2. **Batch 90 — SQLite schema/migration:** additive migration preserving v1 state; verify in the pinned local DO runtime.
3. **Batch 91 — provider-neutral API/envelope contract:** independent schema/contract tests may be prepared alongside Batch 90, but cannot claim runtime acceptance ahead of the migration.
4. **Batch 92 — durable event log:** atomic payload + digest + sequence/high-water transaction; fan-out only after commit; contiguous bounded replay; retention-floor semantics.
5. **Batch 93 — ACK/receipt/RESUME:** authenticated stable consumer identity; exact series/generation/sequence/digest validation; durable monotonic receipt; bounded resume and resnapshot; eviction/restart recovery.
6. **Batch 94 — provider gate:** only lawful, compatible, genuinely zero-cost source evidence; synthetic fixtures remain explicitly synthetic.
7. **Batch 95 — public WSS/device E2E:** only after all prior gates; browser and Android reconnect, TLS, process-death/network-handover and restore acceptance.

Parallel preparation is allowed for independent contract review, failure-injection case design, and test traceability. Shared Worker/DO runtime edits and schema migrations remain serialized. No batch is declared complete by documentation alone.

## 5. Batch 89 execution and CI status

The available GitHub connector exposes repository contents, commits, comparisons and limited status reads; it does not provide a checked-out repository or command runner. The exact-HEAD status endpoint returned no status records, and the workflow-run query returned no runs. These empty results mean **CI UNKNOWN / NOT VERIFIED**, not success, failure, or proof that a workflow is running.

No runtime command was started or left running by this work cycle. Runtime code was not changed. Do not infer execution from the 43 declarations or historical CI records.

## 6. Complete indicator progress ledger — all 12 rows

**Indicator source/UI changes this cycle: none. Indicator implementation credit: 0.** This cycle is WebSocket/backend documentation and source traceability only.

| # | Indicator / subsystem | Current foundation and acceptance boundary | Chart/UI state | Status |
|---:|---|---|---|---|
| 1 | SMA20 | Arithmetic mean of 20 closes; first valid index 19; warm-up nulls and prefix-causality required | Price overlay, toggle, legend/latest value and lifecycle not accepted | 🟨 FOUNDATION |
| 2 | EMA20 | SMA-seeded EMA; alpha = 2/21; first valid index 19 | Price overlay, toggle, legend/latest value and lifecycle not accepted | 🟨 FOUNDATION |
| 3 | RSI14 Wilder | Seed from 14 close-to-close changes; Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides and lifecycle not accepted | 🟨 FOUNDATION |
| 4 | MACD12/26/9 | EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram and zero guide not accepted | 🟨 FOUNDATION |
| 5 | Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Upper/middle/lower overlays, fill, toggle and lifecycle not accepted | 🟨 FOUNDATION |
| 6 | Shared Indicator Hook | Keyed immutable backend snapshot/cache and trust gate; 7 focused test declarations | `CandlestickChart.tsx` does not import/call `useMarketIndicators` | 🟨 FOUNDATION |
| 7 | Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Stage 4 gated; two saved user references are authoritative; OFF = normal spacing, explicit ON = spaced clusters | 🟧 GATED |
| 8 | Volume Profile | Binning, POC/value-area calculation and source acceptance incomplete | Not integrated | 🟥 OPEN |
| 9 | Complete Volume Profile | Session completeness, POC/VAH/VAL methodology and source acceptance incomplete | Not integrated | 🟥 OPEN |
| 10 | Movable-range Volume Profile | User-selected range, recomputation and lifecycle acceptance incomplete | Not integrated | 🟥 OPEN |
| 11 | Heatmap | Lawful depth source, aggregation, decay and provenance incomplete | Not integrated; visual work remains gated on user's reference | 🟥 OPEN |
| 12 | Liquidation Maps | Data provenance, estimation methodology and confidence limits incomplete | Not integrated | 🟥 OPEN |

### Indicator mathematical and data invariants

- Warm-up outputs must be null; never backfill or fabricate values.
- Prefix-causality: appending future candles cannot alter prior outputs.
- No future-candle lookahead or repaint.
- Exact canonical series identity and source timestamp alignment.
- Deterministic finite numeric output; no source mutation; bounded history.
- Clear stale output on instrument/timeframe identity change.
- No indicator output from DEMO, loading, unavailable, error, or empty snapshots.
- Indicator inputs must ultimately come from authenticated, durable OHLCV snapshots; synthetic proof data is not live-market provenance.
- Preserve Footprint OFF standard candle spacing; only explicit ON activates the dedicated spaced-cluster layout.
- Heatmap rendering must not begin before the user's visual reference is supplied.

**Focused indicator declarations:** 21 calculation + 7 shared-hook = 28 declarations; NOT a pass count and not a completion percentage.  
**Aggregate indicator completion:** ⚪ NOT SCORED; no approved weighted denominator exists.

## 7. Project progress dashboard

| Workstream | Current evidence-based status |
|---|---|
| Stage 1 | 🟨 30/40 = 75% provisional; not overall project completion |
| Gate 10 | 🟥 0/10 formally closed; remaining criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 |
| Stage 2 | 🟦 Preparatory technical work only |
| Stage 3 | ⚪ Not scored |
| Stage 4 — Indicators & Analytics | 🟪 GATED |
| Stage 5 | ⚪ Not scored |
| Stage 6 | ⚪ Not scored |
| Overall project progress | ⚪ NOT SCORED; no approved weighted denominator |
| Significant Progress / IP3S | ⚪ NOT SCORED |
| Batch 89 | 🟥 OPEN; runtime gate not executed |
| Batches 90–91 | 🟦 Specification/preparation only; runtime implementation not accepted |
| Batches 92–93 | 🟥 Durable event/replay and ACK/receipt/RESUME missing |
| Batch 94 | 🟥 Zero-cost lawful provider gate not passed |
| Batch 95 / Gate 36 | 🟥 Public WSS/TLS/browser/Android E2E absent |
| Project Gate 25 | 🟥 Durable signed snapshot/receipt/high-water acceptance remains open |
| Production Worker/API | 🟥 Not deployed; no production acceptance claimed |

Stage 1's 75% provisional figure must not be extrapolated into overall project completion. Documentation and source audit do not close external owner/device gates.

## 8. Cost, branch and release safeguards

- Active branch only: `phase-2/market-data-foundation`.
- `main` remains untouched.
- No runtime source, dependency, lockfile, indicator renderer, or UI code changed in this cycle.
- No deployment, Cloudflare resource creation, paid service, paid runner, or market-data provider was used.
- Keep synthetic-only proof mode and localhost origin restrictions.
- Do not enable public WSS or provider ingress before their acceptance gates.
- Planning target remains around **24 December 2026**, not a guaranteed delivery date and not grounds to waive acceptance.


## 9. Additional concurrency acceptance — snapshot-to-live handoff

A potential interleaving race exists between one-time ticket consumption and socket authorization. The ticket-consumption transaction captures the current sequence watermark; after the awaited transaction returns, the handler marks the socket authorized and sends its snapshot. An event committed in that gap may be excluded from fan-out because the socket is not yet authorized, while the returned snapshot watermark remains older.

This race is **not yet reproduced** and is not counted as a confirmed runtime failure. The existing snapshot/live ordering test does not explicitly force the consume-commit → concurrent emit → socket-authorize schedule.

Add a deterministic failure-injection test: pause the auth handler after ticket-consumption commit, emit the next contiguous event, resume auth, and assert no gap between snapshot watermark and subsequent delivered/replayed events. The test must run against the actual pinned Durable Object runtime. Accept only a snapshot at/after the event cursor or contiguous durable replay after the snapshot; reject silent loss and duplicate delivery. The durable event log (Batch 92) plus RESUME (Batch 93) are the intended recovery mechanism. Do not attempt to close the gap with a non-durable cursor-only read.
