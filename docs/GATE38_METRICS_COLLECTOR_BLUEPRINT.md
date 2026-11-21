# Gate 38 — Zero-cost metrics collector and retention blueprint
**Status:** DESIGN FOR OWNER REVIEW — NOT IMPLEMENTED  
**Prepared:** 21 November 2026  
**Branch baseline:** 3eadda21f795abe5af195eedf0c81727d31f6436  
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
- A worker heartbeat older than 90 seconds is stale for live gauges. Stale workers are removed from the live-worker table; committed historical buckets remain.
- Retention target: 7 days of 15-minute buckets, with a hard row/size ceiling and oldest-bucket eviction. Retention is bounded by both age and capacity; the endpoint must report when capacity eviction shortens effective retention.
- The metrics DB path is configurable and must be validated on the actual persistent local volume before production use. It must not be placed on an unsupported network filesystem.

This supports multiple worker processes on one host sharing one supported local persistent volume. It does not support multi-host aggregation or horizontally distributed hosts. Do not call it a cross-host collector.

## 3. Delta and restart correctness

Each worker snapshot contains monotonically increasing counters for that process lifetime. The collector stores the last accepted snapshot per worker and computes non-negative deltas transactionally:

1. Validate schema version, worker ID, timestamp, metric dimensions and all numeric bounds.
2. Compare new counters with that worker's last snapshot. A lower counter is an invalid regression for the same worker ID; process restart must generate a new worker ID.
3. Add deltas to the current 15-minute aggregate bucket and update the worker checkpoint in the same transaction.
4. Update active-connection gauges and heartbeat separately from cumulative counters.
5. On restart, the new worker ID starts a new checkpoint. The old worker expires from live gauges after 90 seconds; it cannot double-count prior totals.
6. If a flush fails, retain the last successfully persisted checkpoint and retry with bounded exponential backoff. Never advance the checkpoint before the aggregate write commits.

Histogram bucket deltas must remain monotonic and cumulative. WebSocket counters and close-code classes use the same delta rule. Active connections are gauges, not summed historical counters.

## 4. Capacity and load budget

A 15-second flush means 4 flush opportunities per minute per worker, 16 per minute for 4 workers, and 64 per minute for 16 workers.

At 100 HTTP requests/second, raw per-request persistence would create 8,640,000 write opportunities/day/worker. A 15-second snapshot reduces that worker's flush opportunities to 5,760/day, a 1,500x reduction. With 4 workers, 23,040 flush opportunities/day replace 34,560,000 request-level write opportunities/day, also 1,500x fewer.

These are operation-count estimates, not a benchmark or a promise of zero I/O contention. A dedicated DB, off-event-loop flush, short transaction, finite busy timeout and load tests are mandatory.

The collector must enforce bounded worker count, bounded metric-series cardinality, bounded payload size per flush, bounded transaction duration/retry count, 7-day age retention plus a hard row/database-size ceiling, and explicit disk-full, busy-lock, corruption and read-only-volume behavior.

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
