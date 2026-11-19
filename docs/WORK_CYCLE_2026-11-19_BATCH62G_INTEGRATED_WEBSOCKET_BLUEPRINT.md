# WORK CYCLE 62G BLUEPRINT — FULL SNAPSHOT TO CROSS-INSTANCE WEBSOCKET

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Baseline:** `1cb577c1de31e7a5c286075da5cf8f770b2c16e1`  
**Approval:** Owner approved combining all eight architecture points into one multi-work cycle.  
**Cost policy:** ZERO COST. No deployment, paid service, new hosting, paid Redis, or Termux requirement. `main` untouched.

## 0. Exact-head validation before this cycle

Batch 62F exact HEAD `1cb577c1de31e7a5c286075da5cf8f770b2c16e1` is CI **3/3 SUCCESS**:

- Automated Tests + Build: [44500814706](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44500814706) — frontend unit tests/build, backend tests, bounded SQLite outbox benchmark, dependency audit, container build/smoke and image scan/report all completed successfully.
- CodeQL Python + JavaScript/TypeScript: [44500815399](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44500815399) — both analyses SUCCESS.
- Full Git History Secret Audit: [44500814616](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44500814616) — SUCCESS.

CI success is repository-side evidence only; it does not close owner-host Gate 10 acceptance.

## 1. Newly confirmed architectural constraint

`SQLiteOhlcvStore.query_snapshot()` currently provides a consistent bars + global outbox watermark read transaction for its requested query. It is safe for a scoped chart snapshot. It is **not yet a complete global replica snapshot contract**:

1. Its default bucket/calendar filters intentionally select the default UTC series and do not include every calendar-qualified CME session series.
2. A global replica must include all retained canonical bars across every supported series identity before it can set a global cursor checkpoint.
3. A paginated full snapshot cannot independently open a new read transaction per page and still claim one consistent watermark. Concurrent writes could make pages represent different source moments.
4. Materializing an unbounded full snapshot in one Python list may create memory pressure as the number of instruments/timeframes grows.

Therefore the first implementation must introduce a bounded, transaction-consistent snapshot transfer contract (or a source-side immutable snapshot generation) that includes every supported bucket/calendar identity and an unambiguous global watermark. No per-instrument snapshot may be used to advance a global replica cursor.

## 2. Eight-point integrated work cycle

These are one dependency-ordered delivery, not eight independent production switches.

### Point 1 — Authoritative full read-model snapshot

- Snapshot generation captures every retained OHLCV row, all series identities (provider, dataset, publisher, instrument, series type, symbol, timeframe, bucket policy, calendar ID/version), retention metadata and global outbox high-water.
- Snapshot rows and watermark must represent one SQLite read view.
- Transfer must be bounded and restart-safe. Preferred design: create a snapshot generation with stable generation ID and a deterministic ordered manifest; stream pages from that immutable generation. If snapshot staging is too costly, hold one read transaction only for a bounded local export and measure WAL/memory impact before choosing.
- A replica checkpoint is set to the snapshot watermark only after all pages and manifest validation succeed and the replica snapshot swap commits atomically.
- If the source retention boundary makes the requested incremental cursor unavailable, discard partial transfer and restart from a fresh snapshot.

### Point 2 — Replica identity and checkpoint schema

- Each local gateway has a stable, unique replica identity.
- The source has a stable source identity; a replica cannot silently continue from another source database.
- Persist source ID, replica ID, applied global cursor, snapshot generation, retention floor observed and schema/protocol version.
- Schema creation/migration must be transactional and must not alter the shared registry `PRAGMA user_version`.
- Checkpoint is local to each gateway database. Never share SQLite WAL files between hosts.

### Point 3 — Atomic, idempotent replica apply without outbox echo

- A relay event is validated against its canonical envelope, event ID, global cursor, schema version and full series identity before writes.
- Apply the OHLCV revision to the replica's local bars table and advance its checkpoint in the **same SQLite transaction**.
- Replica apply must not append a new source outbox event. No relay echo loops.
- Exact Decimal text and integer nanosecond timestamps must round-trip unchanged.
- Duplicate/stale events do not mutate bars or regress the checkpoint.
- A conflicting event ID at the same cursor is a hard integrity error.
- An event beyond the next expected cursor is a gap and must stop the consumer for resnapshot.

### Point 4 — Redis Streams append and per-instance consumer groups

- Redis Streams is a transport/wakeup layer, not the source of truth. SQLite source outbox remains authoritative.
- Stream IDs or fields must carry source ID, global cursor, event ID and payload/reference with deterministic retry identity.
- Publisher retries must not create ambiguous duplicate logical events; duplicate append resolution must verify the existing event identity.
- Every gateway has its **own consumer group** so every gateway receives every event. A shared group is prohibited because it load-balances events to one consumer rather than broadcasting to all gateways.
- Redis credentials/ACL/TLS are owner configuration; no secrets in source or CI logs.

### Point 5 — Consumer handoff, pending reclaim and publication ordering

- Consumer applies event transactionally to local SQLite before acknowledging the Redis entry.
- After commit, publish the corresponding local notification to the process-local hub. If process crashes after commit but before ack, replay is harmless because apply is idempotent.
- If process crashes before commit, entry remains pending and is safely reclaimed.
- Hub notification must not occur before durable local apply.
- Reclaim/claim policy must have bounded idle threshold, retry count and dead-letter/incident behavior; no silent discard.

### Point 6 — Two-process parity and snapshot handoff

- Run two independent backend processes with independent local SQLite files and independent consumer groups.
- Both must receive the same global source event sequence and converge to equivalent retained read models and watermarks.
- A new instance must complete full snapshot first, then consume events strictly after its snapshot cursor.
- A running instance must not advertise readiness for replicated market data until its snapshot and replay catch up to the required watermark.
- Do not use a shared SQLite WAL or a single shared consumer group.

### Point 7 — Failure, recovery and retention matrix

Required deterministic tests:
- Duplicate event and retry after successful commit.
- Crash before local commit; crash after commit before Redis ACK.
- Out-of-order event and cursor gap.
- Conflicting event ID / malformed envelope / wrong source ID.
- Exact decimals, nanosecond values, calendar-qualified identity.
- Process restart and checkpoint persistence.
- Redis outage while source SQLite continues ingesting.
- Publisher retry and duplicate stream append.
- Pending reclaim by a restarted consumer.
- Source outbox retention expiry during catch-up.
- Snapshot interrupted mid-transfer and resumed/restarted.
- Atomic snapshot install failure; previous good replica snapshot remains usable.
- Two gateways converge without event loss or duplicate bar mutation.

### Point 8 — Gate 25/36 owner acceptance

- Gate 25: owner Redis ACL/TLS, two separately deployed app instances, independent consumer groups, ticket/lease race, Redis outage/recovery and named operator evidence.
- Gate 36: existing owner-approved public HTTPS/WSS endpoint, authenticated cross-instance fan-out, consistent snapshot, browser and Android WebView foreground/background, 330-second run and actual platform close attribution.
- No deployment is authorized merely to create evidence. Reuse an already available owner environment. If it does not exist at zero incremental cost, record BLOCKED with the exact missing prerequisite.
- CI, local Redis and two local processes are supporting evidence, not owner production acceptance.

## 3. Correctness invariants and calculations

Let (C) be the replica's durable applied global cursor and (E) the incoming source event cursor:

- (E = C + 1): eligible for validation and transactional apply.
- (E \le C): duplicate/stale path; verify identity where retained and never mutate or regress checkpoint.
- (E > C + 1): gap; do not ACK as applied, do not skip; stop and request a consistent full snapshot.

Atomicity invariant:

`COMMIT = ApplyBar + UpdateReplicaCheckpoint`

If either operation fails, both roll back. Redis ACK is strictly after this commit.

Snapshot invariant:

`ReplicaCheckpoint = SnapshotHighWater`

only after every page, count/hash/manifest check and atomic snapshot swap succeed.

Catch-up distance:

`lag = source_high_water - replica_checkpoint`

A negative value is invalid (wrong source/checkpoint); zero means caught up at that observation; positive is pending work. This is a cursor count, not a time-latency measurement.

Memory/transfer sizing must be measured rather than guessed. For (N) retained bars and mean serialized row size (S), raw payload lower bound is (N \times S), excluding Python/SQLite object overhead. Page size must be bounded by measured peak memory and transfer duration. Do not hard-code a claimed capacity before benchmark results exist.

## 4. Rollout gates — no partial activation

1. Schema + local unit tests.
2. Snapshot generation/export/install tests.
3. Replica apply and checkpoint transaction tests.
4. Publisher/consumer tests against ephemeral CI Redis.
5. Two-process local parity tests.
6. Failure/recovery matrix.
7. Only then consider a feature-flagged owner-host rollout after owner acceptance.

The app startup path remains unchanged until the entire data plane is implemented and tested. No partial Redis relay is enabled.

## 5. Multi-work output and documentation obligations

The implementation batch must update:
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md` — latest verified checkpoint, Stage/Gate accounting and complete indicator ledger.
- This work-cycle report — actual changed files, exact tests, CI run IDs, measured benchmark results, known limits and next blockers.
- `docs/ADR_WEBSOCKET_CROSS_INSTANCE_OUTBOX_RELAY.md` — final decisions only after implementation evidence confirms them.

Do not award Stage 1 ticks or Gate 25/36 closure from blueprint or CI alone.

## 6. Gate 10 parallel evidence packs

| Pack | Gates | Combined work | Still needs owner evidence |
|---|---|---|---|
| A — identity/shared state | 20, 25 | Firebase token matrix + Redis shared-state integration | Real Firebase project, owner Redis, independent deployed instances, outage/recovery |
| B — persistence/recovery | 30, 31, 34 | Restore verification + zero-cost backup/key separation + volume/restart/disk pressure | Owner target DB, off-host destination and separately controlled key custody |
| C — secrets/ingress | 8, 35 | Runtime secret boundary + HTTPS/WSS/certificate checks | Owner host mounts/readback, public endpoint, renewal and external scan |
| D — fan-out/operations | 36, 38, 39 | Snapshot fan-out + durable telemetry + incident drill | Public WebView evidence, durable protected collector, named operator and acknowledgement |

Gate status remains **0/10 formally closed** until each owner acceptance artifact is independently reviewed.

## 7. Full indicator ledger — unchanged by WebSocket blueprint

| Indicator | Formula contract | First valid index | Verified foundation | Remaining work | State |
|---|---|---:|---|---|---|
| SMA20 | Rolling arithmetic mean of close | 19 | Calculation + fixture tests | Visible overlay, toggle, legend/latest value, stale clearing, render tests | 🟨 |
| EMA20 | SMA-seeded EMA, alpha (2/21) | 19 | Calculation + fixture tests | Visible overlay, toggle, legend/latest value, stale clearing, render tests | 🟨 |
| RSI14 | Wilder-smoothed close-to-close gains/losses | 14 | Calculation + edge fixtures | Dedicated 0–100 pane, 30/70 guides, toggle, lifecycle/render tests | 🟨 |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal | MACD 25; signal/histogram 33 | Calculation + warm-up fixtures | Pane, signal line, histogram, zero guide, render tests | 🟨 |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 | Calculation + population-deviation fixture | Three-line overlay, toggle, legend/latest values, render tests | 🟨 |
| Shared indicator hook | Validated backend snapshot only; no DEMO fallback | Snapshot-dependent | Hook reads shared market-data store | Chart binding, loading/error handling, identity/timeframe stale clearing | 🟨 |
| Footprint | Deterministic educational accumulator, explicitly SIMULATED | Not production order flow | Simulation only | Owner reference + reviewed blueprint + ON-only spaced cluster renderer | 🟨 GATED |
| Heatmap | Not implemented | — | None | Owner reference, blueprint, source data, calculation, renderer and tests | 🟥 |
| Liquidation Maps | Not implemented | — | None | Owner reference, blueprint, source data, calculation, renderer and tests | 🟥 |

Calculation test boundary: seven existing calculation cases cover alignment/warm-up, RSI edge cases, MACD signal warm-up, Bollinger population deviation, shared calculation entry point, 18 timeframe labels and invalid inputs. They do not prove visible chart integration or live-provider correctness.

Visual invariants: Footprint OFF preserves standard candle spacing. Only explicit Footprint ON enables spaced candle/cluster layout. Footprint, Heatmap and Liquidation Maps visuals remain gated on owner reference images and reviewed blueprints. Stage 4 visible UI remains parked while Stage 1 is active.

## 8. Progress, cost and device controls

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** — M1–M8 weights are unapproved.
- ZERO COST: no paid infrastructure or market data.
- No Vercel/Cloudflare deployment or promotion.
- No Termux operation required for this repository-side design and CI work.
- `main` untouched.

**Disposition:** owner approval received for the integrated eight-point work cycle. The architecture constraint is now explicit: global snapshot semantics must be fixed before any global replica checkpoint or Redis consumer is activated.
