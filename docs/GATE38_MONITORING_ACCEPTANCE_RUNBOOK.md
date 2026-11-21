# Gate 38 — Monitoring and observability acceptance runbook

**Status:** 🟧 OPEN — repository-side instrumentation, same-host aggregation and failure tests are implemented; owner-host/operator acceptance is not complete.  
**Branch:** `phase-2/market-data-foundation`  
**Cost boundary:** ZERO COST. No paid monitoring, hosted dashboards, alerting vendors, paid storage or trials.

## 1. Repository implementation verified

### Process-local inputs
- `backend/app/observability.py` maintains bounded HTTP request metrics and WebSocket lifecycle metrics.
- HTTP labels use route templates and bounded method/status classes; raw URLs, query strings, path parameters, IPs, headers and tokens are not metric dimensions.
- WebSocket counters cover starts, active/completed/accepted connections, peer disconnects, fixed close-code classes and cumulative duration. These are process-local inputs and reset with process restart.

### Same-host multi-worker aggregation
- `backend/app/metrics_collector.py` persists aggregate counters in a dedicated SQLite database, separate from market-data registry and incident storage.
- WAL mode; 250 ms SQLite busy timeout; bounded `BEGIN IMMEDIATE` lock retries; off-event-loop flush via `asyncio.to_thread`; 15-second staggered worker checkpoint interval.
- 899 logical series: 762 HTTP request + 127 latency histogram + 10 WebSocket series; configured hard limit 900.
- 15-minute aggregate buckets; 7-day retention (672 buckets); 650,000 aggregate-row cap; at most 16 live workers and 256 worker generations; workers stale after 90 seconds.
- At full cardinality, theoretical retained rows are (899 \times 672 = 604,128). Row-cap headroom is (650,000 - 604,128 = 45,872) rows (7.06%). This is a row budget, **not** a byte cap; no DB-byte cap is inferred.
- Default path: `./data/observability_metrics.sqlite3`; override: `OBSERVABILITY_METRICS_DB_PATH`.
- Aggregation scope is **same-host, shared local persistent volume only**. Multi-host SQLite is unsupported.
- `/internal/metrics` is registered only when `OBSERVABILITY_METRICS_TOKEN` is configured; it preserves authenticated/no-store behavior and exposes local plus cluster aggregate/status data.

### Failure isolation and regression evidence
Exact source/test HEAD `a62e7423a5d36d3fdbc003e0e56d86c3a9e6ecbb`:
- Automated Tests [44911391436](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391436): SUCCESS, 35/35 steps; frontend 255/255; backend 1,271 passed in 55.86 s.
- CodeQL [44911391400](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391400): SUCCESS.
- Full Git History Secret Audit [44911391397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391397): SUCCESS.
- Full-cardinality 899-series benchmark passed for 1/4/16 threads and four separate OS processes; exact worker/series counts and SQLite integrity verified.
- SQLite read-only failure/recovery and genuine `SQLITE_FULL` rollback/recovery tests passed.
- Application-level isolation test passed: collector degraded while HTTP health, authenticated metrics scrape and authenticated WebSocket status remained responsive.

### Full-cardinality benchmark notes
The batch-read optimization reduces 16-worker bucket SELECT count from 460,288 to 512 per 512 flushes. On the CI runner, 16-thread p95 changed 654.798 → 600.947 ms, p99 921.534 → 944.797 ms, max 2,769.913 → 1,727.381 ms, retries 251 → 154. Four-process p95 changed 243.724 → 114.703 ms and retries 4 → 2. Four-thread p99 regressed 290.086 → 405.913 ms; 16-thread p99 regressed 2.52%. Keep the tail-latency caveat visible; no production SLA is established.

## 2. Why Gate 38 remains orange

1. No owner-host proof of the actual persistent volume, mount identity, ownership/mode, restart persistence, disk pressure, bounded retention or backup/restore.
2. No verified owner-host reverse-proxy/firewall restriction around the private metrics endpoint.
3. No owner-host operator-token injection, rotation, access review or evidence that tokens stay out of process arguments/logs/browser history.
4. No operator dashboard/accessibility review. The authenticated JSON scrape endpoint is not a human-facing dashboard.
5. Escalation currently produces local structured logs; no independent human notification channel is verified.
6. No real operator acknowledgement, escalation, resolution and recovery drill against the owner-controlled runtime.
7. No actual owner-host restart/failure drill proving incident journal and metrics persistence.

A green CI container smoke test is repository evidence only; it does not establish an owner-controlled host or production monitoring service.

## 3. Required owner-host/operator acceptance

Before changing Gate 38 to 🟨🟩, the owner-controlled runtime must demonstrate:
- Persistent local volume mounted at the configured path with restrictive owner/group/mode.
- Metrics and incident state survive process restart; backup/restore and retention are verified.
- Private network perimeter/firewall blocks public access; missing/wrong token returns 401.
- Operator token is injected securely, rotated, and absent from URLs, logs, process arguments and client bundles.
- Operator can view health, HTTP errors/latency, WebSocket lifecycle/reconnect/lag, Redis state, collector health, capacity and incidents.
- Disk pressure and collector degradation are observable without blocking HTTP/WebSocket traffic.
- A controlled incident is delivered through an independently monitored no-cost channel, acknowledged, escalated, resolved and recovered.
- Exported telemetry contains no account identifiers, user identifiers, raw query strings, tokens or secret-bearing environment values.

Do not add paid vendors, public metrics endpoints, paid object storage, managed databases, or billing-enabled plans. If the existing owner-controlled hardware cannot safely satisfy this, keep Gate 38 🟧 OPEN and defer the external integration.

**No Termux/device command is needed for this repository-side update.**


## Batch 62J-94–96 — tail-latency diagnostics and rejected retry experiment (21 November 2026)

**Accepted source/test HEAD:** `2eb3181b21b7f2aa3a53c8c293ab6d27ec959b75`  
**Automated Tests:** [44913778296](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778296) SUCCESS — frontend 255/255; backend 1,271 passed.  
**CodeQL:** [44913778266](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778266) SUCCESS.  
**Secret audit:** [44913778270](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778270) SUCCESS.

The accepted collector returns internal `lock_wait_ms` and `transaction_ms` diagnostics. The benchmark records p50/p95/p99/mean/max for these phases and end-to-end flush latency. In the restored-source 16-thread synthetic case, p99 end-to-end was 644.926 ms, p99 lock wait 613.413 ms, p99 transaction body/commit 18.152 ms, with 68 retries. Four-process case: p99 end-to-end 135.398 ms, p99 lock wait 128.640 ms, transaction p99 9.771 ms, 0 retries.

**Important statistical caveat:** each percentile is calculated independently across its own sample array. Dividing phase p99 by end-to-end p99 does not yield the exact fraction of time spent waiting in the same p99 flush. Treat these as diagnostic distributions, not additive decomposition or an SLA.

Batch 62J-95 tried stable per-worker retry jitter. It passed its source CI but failed the performance comparison: 16-thread p95/p99/max worsened by +53.6%/+79.9%/+132.4%, retries rose 72.4%; four-process p95 worsened 123.8%. Batch 62J-96 reverted that helper and test. The source/test files are restored to the accepted 62J-94 diagnostic version. No jitter change is retained.

The next benchmark should model the production worker cadence (including the initial per-worker phase staggering in `backend/app/main.py`) separately from simultaneous worst-case contention. Do not change production lock policy based only on the synchronized stress case.

Gate 38 remains 🟧 OPEN pending owner-host persistent volume, permissions, restart/retention/backup, disk pressure, private perimeter, operator-token lifecycle, dashboard visibility and a real no-cost operator incident/recovery drill. No Gate 10 tick is awarded by CI.
