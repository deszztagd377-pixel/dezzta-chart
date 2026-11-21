## Batch 62J-87 — bounded writer-lock retry (21 November 2026)

The 16-worker full-cardinality benchmark at source/test HEAD `73a19e5db54b44d1d07caa038ec567d31d19a0a8` failed at `BEGIN IMMEDIATE` with `database is locked`. This was separate from the schema-bootstrap race fixed in Batch 62J-86. The collector now retries writer-lock acquisition for up to eight attempts, with bounded exponential backoff and the existing 250 ms SQLite busy timeout. The retry count is included in flush results and benchmark evidence. A regression test exercises lock release after 350 ms and verifies the metrics delta is applied once.

This does not prove that every 16-worker load passes; exact-head CI for the new source/test change is pending. Gate 38 remains 🟧 OPEN. Full separate-process test, disk-full/read-only behavior, HTTP/WebSocket traffic isolation and owner-host acceptance remain.

Capacity model unchanged: 899 logical series × 672 15-minute buckets = 604,128 aggregate rows; 650,000 row ceiling leaves 45,872 rows before checkpoint/metadata and SQLite/WAL/index overhead. This is not a byte budget.

ZERO COST. No deployment, paid provider, production credentials, Termux/device operation or `main` modification.

---

## Batch 62J-86 — schema-bootstrap contention hardening (21 November 2026)

The first full-cardinality CI benchmark attempt failed at concurrent SQLite schema initialization with `database is locked`. This is a real regression signal and is not suppressed. The collector now serializes one-time schema initialization per collector instance and applies bounded retry/backoff only to transient SQLite lock errors. The benchmark now gives each simulated worker a separate collector instance, and a new regression test exercises four independent instances initializing the same shared database concurrently.

The previous attempt's CodeQL and secret-history audit passed, but Automated Tests failed at the benchmark step. Current source/test HEAD `2c584fcef5a20b21ec2850692ab51e28341c4eff` has new exact-head CI pending. Gate 38 remains 🟧 until the new benchmark and all failure/isolation/host requirements are accepted. The row-cap arithmetic is not a byte budget. ZERO COST; no deployment, no paid provider, no Termux, no production credential, and no `main` modification.

---

## Batch 62J-85 — full-cardinality benchmark update (21 November 2026)

The former 12-series synthetic benchmark has been replaced with a full 899-logical-series benchmark matching the current collector dimensions: 762 request series + 127 latency histogram series + 10 WebSocket metric series. It measures 1/4/16 Python-thread cases and checks aggregate cardinality, expected request totals, worker totals, serialized snapshot size and SQLite integrity. A write-rejection transaction rollback/retry regression was added.

**Capacity arithmetic:** 899 × 672 retained 15-minute buckets = 604,128 aggregate rows. Against the 650,000 aggregate-row ceiling, nominal headroom is 45,872 rows (7.06% of cap). This excludes worker/checkpoint rows, tombstones, indexes, SQLite page overhead, WAL and filesystem metadata. It is not a byte budget.

**Still open:** exact-head CI; separate OS-process contention; actual read-only/disk-full behavior; app-level proof that collector failures cannot delay or fail HTTP/WebSocket traffic; owner-host volume permissions, restart persistence, backup/restore, retention and disk-pressure recovery; operator access and recovery acceptance. The trigger-based write failure is only a transactional rollback simulation. Gate 38 remains 🟧 OPEN.

No WebSocket protocol/data-path behavior changed. No indicator progress credit. ZERO COST; no deploy, paid provider, Termux/device operation, production credential or `main` modification.

---

# Gate 38 — Zero-cost metrics collector and retention blueprint
**Status:** REPOSITORY IMPLEMENTATION AND EXACT-HEAD CI VERIFIED — INITIAL LOW-CARDINALITY BENCHMARK MEASURED; FULL-CARDINALITY AND HOST ACCEPTANCE REQUIRED  
**Prepared:** 21 November 2026  
**Branch baseline:** 3eadda21f795abe5af195eedf0c81727d31f6436
**Implementation HEAD at hardening start:** b1e21f552182a720400cd9a2d276705834a41358  
**Scope:** repository-side design for bounded multi-worker monitoring on one owner-controlled host.

## 1. Current verified baseline

- RequestMetrics and WebSocketMetrics are thread-safe, bounded, process-local counters.
- The WebSocket middleware observes only lifecycle metadata for /ws/market-data; it never reads payloads, auth tickets, headers, account IDs, IP addresses, symbols or query strings.
- /internal/metrics is protected by a dedicated Bearer token, constant-time comparison and no-store response behavior.
- The SQLite incident journal is separate from metrics time-series storage. It is bounded to 1,000 incidents, retains resolved incidents for 30 days, and supports local escalation logs. It is not a metrics collector or independent notification channel.
- The existing Redis client is coupled to shared security guards. Reusing it for telemetry would couple monitoring to authentication/rate-limit availability and may exceed the actual ACL scope. This blueprint does not repurpose that client.

## 2. Selected zero-cost topology

Use a dedicated SQLite metrics database file on the same owner-controlled host and persistent local volume as the backend runtime, but separate from INSTRUMENT_REGISTRY_DB_PATH.

- Each ASGI worker owns a random process-lifetime worker ID and keeps the existing in-memory counters on the request/WebSocket hot path.
- A background flush task snapshots counters every 15 seconds and writes bounded deltas in a short transaction.
- The database uses WAL, a finite busy timeout and explicit transaction boundaries. Flush runs off the event loop; it never runs synchronously inside request or WebSocket callbacks.
- The collector stores aggregated 15-minute buckets and current worker heartbeats. It does not persist request payloads, raw URLs, query strings, headers, account identifiers, IP addresses, auth material, symbols or arbitrary labels.
- The protected metrics endpoint reads a combined snapshot across live worker heartbeats. A separate history view may expose only bounded time windows and fixed metric dimensions.
- A worker heartbeat older than 90 seconds is stale for live gauges. Worker checkpoint rows remain available for idempotence until capacity pressure requires eviction; an evicted worker ID is retained in a seven-day tombstone table so it cannot resume and replay counters. Committed historical buckets remain.
- Retention target: 7 days of 15-minute buckets, with a hard row/size ceiling and oldest-bucket eviction. Retention is bounded by both age and capacity; the endpoint must report when capacity eviction shortens effective retention.
- The metrics DB path is configurable and must be validated on the actual persistent local volume before production use. It must not be placed on an unsupported network filesystem.

This supports multiple worker processes on one host sharing one supported local persistent volume. It does not support multi-host aggregation or horizontally distributed hosts. Do not call it a cross-host collector.

## 3. Delta and restart correctness

Each worker snapshot contains monotonically increasing counters for that process lifetime. The collector stores the last accepted snapshot per worker and computes non-negative deltas transactionally:

1. Validate schema version, worker ID, timestamp, metric dimensions and all numeric bounds.
2. Compare new counters with that worker's last snapshot. A lower counter is an invalid regression for the same worker ID; process restart must generate a new worker ID.
3. Add deltas to the current 15-minute aggregate bucket and update the worker checkpoint in the same transaction.
4. Update active-connection gauges and heartbeat separately from cumulative counters.
5. On restart, the new worker ID starts a new checkpoint. The old worker expires from live gauges after 90 seconds; if its checkpoint is later evicted, a seven-day tombstone rejects that retired ID so it cannot replay prior cumulative totals.
6. If a flush fails, retain the last successfully persisted checkpoint and retry with bounded exponential backoff. Never advance the checkpoint before the aggregate write commits.

Histogram bucket deltas must remain monotonic and cumulative. WebSocket counters and close-code classes use the same delta rule. Active connections are gauges, not summed historical counters.

## 4. Capacity and load budget

A 15-second flush means 4 flush opportunities per minute per worker, 16 per minute for 4 workers, and 64 per minute for 16 workers.

At 100 HTTP requests/second, raw per-request persistence would create 8,640,000 write opportunities/day/worker. A 15-second snapshot reduces that worker's flush opportunities to 5,760/day, a 1,500x reduction. With 4 workers, 23,040 flush opportunities/day replace 34,560,000 request-level write opportunities/day, also 1,500x fewer.

These are operation-count estimates, not a benchmark or a promise of zero I/O contention. A dedicated DB, off-event-loop flush, short transaction, finite busy timeout and load tests are mandatory.

The collector enforces 16 live workers, 256 checkpoint generations, 4,096 seven-day retired-worker tombstones, 900 logical series per snapshot, 256 KiB serialized snapshot size, 650,000 aggregate rows, and seven-day age retention. The actual SQLite byte ceiling remains benchmark-derived; explicit disk-full, busy-lock, corruption and read-only-volume acceptance remains required.

## 5. Security and failure behavior

- Reuse the existing metrics Bearer-token authentication boundary; do not add credentials to URLs or logs.
- Apply host firewall/reverse-proxy restrictions to all /internal routes. Application tokens are not a network perimeter.
- Validate worker IDs as opaque bounded random identifiers. Do not derive them from hostnames, IP addresses, process command lines or user data.
- Use fixed route/method/status labels already emitted by RequestMetrics; overflow remains a single bounded series.
- Do not store raw exception messages. Collector errors use fixed summary codes.
- Metrics storage failure must not fail market-data requests, WebSocket delivery, authentication, rate limiting or OHLCV persistence. It may degrade monitoring completeness and must expose a bounded health flag.
- Do not reuse the market-data registry database; do not make metrics writes part of an OHLCV transaction.
- Do not use Redis guard keys or Redis ACL expansion as an implicit collector dependency.

## 6. Required implementation and acceptance tests

1. Two or more worker instances sharing one temporary local DB produce a combined count equal to the sum of committed deltas.
2. Repeated identical snapshots do not double count.
3. A failed transaction does not advance the worker checkpoint.
4. A process restart with a new worker ID does not replay old process counters.
5. A stale worker disappears from live gauges after the 90-second heartbeat threshold.
6. Concurrent worker flushes preserve all deltas under WAL/lock contention.
7. A simulated busy database retries within the bounded retry/deadline policy.
8. Disk-full/read-only/corrupt DB failures do not affect market-data request or WebSocket success paths.
9. Cardinality, worker count, payload size, rows and database bytes remain bounded at saturation.
10. Retention removes expired buckets and capacity eviction is surfaced to the operator.
11. Missing/invalid/valid token, no-store behavior and network-perimeter assumptions are tested.
12. Request and WebSocket metrics aggregate independently and active gauges are not added to historical totals.
13. A restart/restore drill proves retained buckets survive the actual owner-host volume lifecycle.

## 7. Gate 38 acceptance boundary

Repository acceptance requires source tests, exact-head CI and an isolated local multi-worker test. Gate 38 still requires owner-host evidence for the actual persistent-volume path, ownership, restart persistence and disk-pressure behavior; firewall/reverse-proxy isolation and operator-token injection/rotation; measured disk use and retention under representative load; operator dashboard visibility/access review; independent notification/acknowledgement and a real recovery drill.

A single-host SQLite collector cannot satisfy a multi-host requirement. If the owner later confirms multiple backend hosts, this design must be replaced by a supported shared database or telemetry service; no paid or unverified provider is assumed.

## 8. Explicit non-goals

No production host is provisioned, no external provider is selected, no secret or production credential is requested, no Redis guard behavior is changed, no deployment is performed, and no Gate 10 status is upgraded by this document.

**Review gate:** implementation must not begin until this bounded scope is reviewed and explicitly approved. This preserves the project's blueprint-before-major-implementation rule.


## 9. Explicit loss window, cardinality and row budget (design clarification)

### 9.1 Monitoring-data loss semantics

The counters remain in process memory between successful flushes. A process crash can therefore lose the most recent unflushed interval: nominally up to 15 seconds, plus scheduler delay. A graceful shutdown should attempt one bounded final flush, but shutdown must not block market-data service termination indefinitely. This collector is operational telemetry, not a billing ledger, financial audit trail, or exact event store. The checkpoint transaction prevents double-counting already committed deltas; it cannot recover increments that were never flushed.

### 9.2 Series and retention calculation

The current RequestMetrics contract caps method/route pairs at 127, including the shared overflow series. It emits at most six HTTP status classes (1xx–5xx plus other), so request counters are bounded by:

- HTTP request series: 127 × 6 = 762.
- HTTP latency series: 127.
- WebSocket lifecycle history: conservatively budget 11 scalar series (five close-code classes plus starts, active/current gauge, completed, accepted, peer disconnects and duration sum). The active gauge is stored as current worker state, not added to historical bucket totals.
- Conservative total planning ceiling: 900 logical series per 15-minute bucket.

Seven days at 15-minute resolution is 7 × 24 × 4 = 672 buckets. Therefore the planning ceiling is 900 × 672 = 604,800 aggregate rows. The implementation stores one JSON checkpoint row per worker generation, not one SQL row per series: the checkpoint table is capped at 256 rows. A separate retired-worker tombstone table is capped at 4,096 rows and expires entries after seven days; the metadata table has one fixed counter row. The aggregate-table ceiling is 650,000 rows, leaving 45,200 rows (about 7.47%) above the 604,800-row seven-day planning bound. At the aggregate ceiling, the additional bounded tables contribute at most 256 + 4,096 + 1 = 4,353 rows, so the combined logical table-row ceiling is 654,353 before SQLite indexes and WAL pages. Enforce all four limits independently; do not mislabel the aggregate-row ceiling as a total database-row or byte ceiling.

These are schema-level planning bounds, not measured SQLite disk consumption. A separate byte ceiling must be selected from the isolated benchmark, including WAL and index overhead. Do not invent a byte limit from logical row count. If the benchmark cannot fit the chosen operational disk budget with headroom, reduce series/retention or revise the schema before implementation acceptance.

### 9.3 Flush scheduling and contention

Worker startup should apply a bounded initial phase offset so all workers do not flush simultaneously. Keep the nominal 15-second interval and 90-second stale threshold. Test synchronized starts as a worst case, then test staggered starts and 16 concurrent workers. The finite SQLite busy timeout and retry deadline must be measured; a failed flush must never advance its checkpoint.

### 9.4 Interpretation of the 1,500x estimate

The 8,640,000 versus 5,760 daily operation comparison describes a hypothetical design that persists every request versus periodic metric snapshots. The current implementation does not write one SQLite row per request; it records in-memory counters. The 1,500x figure is therefore a comparison against naive per-request persistence, not a measured reduction from the current implementation and not a benchmark result.


## 10. Implemented repository behavior and hardening (Batch 62J-83)

- `backend/app/metrics_collector.py` implements the same-host SQLite collector; `backend/app/main.py` schedules the 15-second off-event-loop flush and adds the cluster snapshot to the existing token-protected endpoint; `backend/app/config.py` exposes `OBSERVABILITY_METRICS_DB_PATH`.
- Runtime limits: 16 live workers; 256 persisted worker checkpoints; 4096 retired-worker tombstones retained for seven days; 900 logical metric series per worker snapshot; 256 KiB serialized snapshot; 650,000 aggregate rows; 15-minute buckets; seven-day age window; 90-second live-worker staleness.
- When the worker-checkpoint table reaches 256, only the oldest stale checkpoints are evicted, and their worker IDs are retained as tombstones for seven days. A process attempting to resume an evicted ID is rejected rather than replaying its cumulative counters. If no stale checkpoint can be safely evicted or the tombstone ceiling is reached, the new worker is rejected and collector status degrades; market-data paths remain independent.
- Snapshot reads filter out buckets older than seven days even if no new flush has run. Aggregate-row capacity eviction is counted in `metrics_meta` and surfaced as `capacity_evicted_rows_total`, with the oldest retained bucket and effective retention also reported.
- Worker timestamps must be monotonic for a worker ID. A backwards timestamp or counter regression rejects the transaction; checkpoint and aggregate remain unchanged.
- The 650,000 row limit applies to aggregate bucket rows. Worker checkpoints, tombstones and metadata are separately bounded at 256, 4096 and one fixed row respectively. The combined logical table-row upper bound at full aggregate capacity is 654,353, before SQLite indexes and WAL pages; this is not a byte estimate.
- New regression tests cover stale checkpoint eviction/tombstones, live worker limit, read-side age filtering, and timestamp regression. Do not mark CI accepted until the exact hardening HEAD has all three workflows successful.

## 11. Remaining Gate 38 acceptance

1. Exact-head repository CI is verified on `92119a8dc05690e6492aab160662c9e36c839cad`: Automated Tests [44900892637](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892637) SUCCESS (35/35 steps; 1,265 backend tests), CodeQL [44900892567](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892567) SUCCESS, and Full Git History Secret Audit [44900892606](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892606) SUCCESS.
2. An initial 1/4/16-worker SQLite/WAL benchmark is complete. It uses 12 logical series and Python worker threads; it is a low-cardinality baseline only. Full 899-series cardinality and process-level concurrency still need measurement before any byte budget is considered.
3. Regression tests now cover concurrent worker commits, SQLite busy-lock recovery, corrupt-database rejection, transaction rollback, idempotence, stale-worker/tombstone behavior, retention filtering and timestamp regression. Disk-full and read-only tests, plus an app-level proof that collector failure cannot block HTTP/WebSocket traffic, remain.
4. Verify actual owner-host persistent local volume, permissions, restart persistence, backup/restore, disk-pressure recovery and retention behavior.
5. Verify reverse-proxy/firewall restrictions and operator access to the existing Bearer-protected endpoint; complete acknowledgement/escalation and recovery drill.
6. Keep multi-host aggregation explicitly unsupported unless a separate design and validated storage topology are approved.

## 12. Initial benchmark evidence — low-cardinality only

CI artifact: `synthetic-metrics-collector-benchmark`, from Automated Tests run [44900892637](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892637). Each worker performed 32 successful flushes against 12 logical series. All three cases passed aggregate-count verification and SQLite `integrity_check`; lock retry count was zero.

| Worker threads | Successful flushes | p50 ms | p95 ms | p99 ms | Peak database bytes | Peak WAL bytes | Peak total DB+WAL+SHM |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 32 | 0.803282 | 0.888808 | 2.144816 | 49,152 | 0 | 81,920 |
| 4 | 128 | 0.324234 | 4.258792 | 19.107692 | 49,152 | 1,211,312 | 1,293,232 |
| 16 | 512 | 0.436627 | 19.058717 | 78.977826 | 57,344 | 4,194,192 | 4,284,304 |

After `wal_checkpoint(TRUNCATE)`, WAL size was zero and combined database+SHM sizes were 81,920 / 81,920 / 90,112 bytes respectively. These values are runner-specific and cannot be extrapolated linearly to 899 series, separate processes, persistent host volumes or a production retention window. They do not justify a database byte cap.



## 13. Full-cardinality benchmark and process-level follow-up — Batch 62J-88

Exact-head baseline `8424e5eefeecbd06c6534bc34d166f4749ba4055`: Automated Tests [44903581963](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581963) SUCCESS (35/35 steps; frontend 255/255; backend 1,268 passed), CodeQL [44903581995](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581995) SUCCESS and Full Git History Secret Audit [44903581971](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581971) SUCCESS.

The 899-series thread benchmark passed at 1/4/16 workers. The 16-thread case measured p50 56.776 ms, p95 562.426 ms, p99 982.128 ms, max 1,583.741 ms, 196 retries and 7,277,592 peak DB+WAL+SHM bytes. All cases verified exact aggregation and SQLite integrity. CI runner synthetic evidence only.

Batch 62J-88 adds a four-independent-process benchmark and read-only failure/recovery test, and removes outer retries from benchmark/test code so only the collector's internal bounded retry is measured. Treat additions as pending until exact-head CI is green. Process benchmark does not imply multi-host support.

Capacity: 7×24×4 = 672 fifteen-minute buckets; 899×672 = 604,128 aggregate rows; 650,000 limit leaves 45,872 rows (7.06%) nominal headroom. This is not a byte budget. Full disk and app-level isolation remain outstanding, as do owner-host volume/retention/backup and operator acceptance.


## 14. Batch 62J-89 — regression test correction

The first CI attempt for Batch 62J-88 failed one thread test because an unconditional leftover `AssertionError("bounded SQLite retry loop exhausted")` remained directly after a successful `collector.flush()`. The read-only recovery test and the separate-process benchmark test both passed. This was a test harness defect, not evidence of lock retry exhaustion. Batch 62J-89 removes only that assertion; no collector implementation or retry policy change. Exact-head CI is pending. Gate 38 remains 🟧 OPEN until the corrected exact-head workflow passes and the remaining storage/app/host acceptance items are complete.


## 15. Disk-full and application isolation tests — Batch 62J-90

Exact-head baseline `2650c70e977b22a4c70a5e0e292dcc3a8a59082c` passed all repository CI (frontend 255/255; backend 1,269 passed; CodeQL and secret audit passed). The four-process 899-series case completed 128/128 flushes with integrity `ok`; 16-thread contention measured p95 654.798 ms and max 2,769.913 ms with 251 retries. This remains CI-runner evidence.

Batch 62J-90 adds two regression tests:
1. A genuine SQLite storage-exhaustion path using `PRAGMA max_page_count` fixed at the existing database page count after VACUUM. The second full-cardinality bucket must raise `SQLITE_FULL`, roll back all partial bucket writes and worker checkpoint changes, and then recover on a later writable flush without double counting.
2. An application-level failure-isolation test that forces metrics flush to raise a storage-full error, waits for the collector to enter `degraded`, then checks `/health`, authenticated `/internal/metrics`, and authenticated `/ws/market-data` remain responsive.

These tests are pending exact-head CI. They do not prove actual owner-host filesystem exhaustion behavior or production operator recovery. Gate 38 remains 🟧 OPEN until exact-head CI and host acceptance.


## 17. Batch 62J-91 — disk-full test observation correction

The SQLite page-limit test correctly reached `SQLITE_FULL` and verified aggregate rollback. Its worker-count assertion used snapshot time 1801 against an unchanged checkpoint at 900, so the worker was correctly stale under the 90-second threshold. The test now checks at 901 to verify the unchanged checkpoint while it remains live. App-level collector failure isolation and read-only recovery passed in the same run. Only the test timestamp changed; no collector implementation change. Exact-head CI pending.


## 18. Batch 62J-92 — exact-head repository acceptance

Exact HEAD `427e5952d2f209ae1f40405223d8d0a4c7d8408c` passed Automated Tests [44905839386](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839386) (35/35 steps; frontend 255/255; backend 1,271 passed in 39.80s), CodeQL [44905839403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839403) and Full Git History Secret Audit [44905839442](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839442).

The repository-side Gate 38 matrix now includes full 899-series thread/process contention, read-only failure/recovery, genuine SQLite `SQLITE_FULL` rollback/recovery, and app-level isolation proving HTTP health, authenticated metrics scrape and authenticated WebSocket status remain responsive during collector failure. All passed on the exact HEAD above.

Gate 38 remains 🟧 OPEN, not 🟨🟩: actual owner-host persistent volume/permissions/restart/backup/retention/disk-pressure, operator-token perimeter/rotation, operator dashboard visibility, independent notification/acknowledgement/escalation and recovery drill remain. SQLite aggregation remains same-host only; no multi-host claim.


## 19. Batch 62J-93 — batched bucket reads and measured contention

Exact source/test HEAD `a62e7423a5d36d3fdbc003e0e56d86c3a9e6ecbb` passed Automated Tests [44911391436](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391436), CodeQL [44911391400](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391400) and Full Git History Secret Audit [44911391397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391397).

The collector now performs one `SELECT metric_key,value_json WHERE bucket_start=?` per flush and calculates existing totals in memory, then uses `executemany` for non-zero UPSERTs. The `BEGIN IMMEDIATE` transaction still protects both bucket reads and aggregate/checkpoint writes. At 899 series × 512 flushes, the per-key bucket-read query count falls from 460,288 to 512 (99.8888% reduction).

Full 899-series results, prior exact-head comparison:

| Workload | p95 before → after | p99 before → after | Max before → after | Retries before → after |
|---|---:|---:|---:|---:|
| 1 thread | 15.997 → 13.172 ms | 17.820 → 14.003 ms | 17.820 → 14.003 ms | 0 → 0 |
| 4 threads | 192.993 → 190.979 ms | 290.086 → 405.913 ms | 354.538 → 441.050 ms | 2 → 3 |
| 16 threads | 654.798 → 600.947 ms | 921.534 → 944.797 ms | 2,769.913 → 1,727.381 ms | 251 → 154 |
| 4 OS processes | 243.724 → 114.703 ms | 278.107 → 280.654 ms | 415.647 → 378.409 ms | 4 → 2 |

The 4-thread p99/max and the 16-thread p99 did not improve. The 16-thread p95/max/retries and four-process p95/retries did improve. The workload is synthetic and runner-dependent; no SLA or production disk/latency guarantee is inferred. All workloads verified 899/899 series and SQLite integrity `ok`. Gate 38 remains 🟧 OPEN for owner-host and operator acceptance.
