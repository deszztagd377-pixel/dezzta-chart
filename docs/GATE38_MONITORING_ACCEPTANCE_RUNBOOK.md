# Gate 38 — Monitoring and observability acceptance runbook

**Status:** 🟧 OPEN — repository instrumentation exists; central host monitoring is not deployed.  
**Branch:** phase-2/market-data-foundation  
**Cost boundary:** ZERO COST. Do not provision paid monitoring, hosted dashboards, alerting services or trial plans.

## 1. What is implemented in the repository

### HTTP request metrics

backend/app/observability.py provides a bounded, thread-safe RequestMetrics collector:

- Process-local counters and latency histograms, reset when the process restarts.
- At most 127 route/method series, including the shared overflow series.
- Low-cardinality methods and route templates; no raw URL, query, path parameters, client IP or authorization header in metric labels.
- HTTP status classes, fixed latency buckets (5 ms through 5,000 ms), one-day duration clamp and saturating counters.
- Detached JSON snapshots; snapshot mutation cannot change internal state.

The collector is **not cross-process aggregation**. Each ASGI worker has its own in-memory metrics.

### Private scrape endpoint

GET /internal/metrics exists only when OBSERVABILITY_METRICS_TOKEN is configured. It uses constant-time bearer-token comparison and private/no-store response headers. GET /internal/alert-delivery uses the same configured token and exposes sanitized process-local worker status.

If the token is absent, these routes are not registered. No unauthenticated public scrape endpoint is created.

### Persistent incident journal

backend/app/incident_store.py stores deduplicated alert-delivery incidents in local SQLite:

- Maximum 1,000 rows; unresolved incidents are never evicted to make space.
- Resolved incidents older than 30 days are pruned when a new incident is recorded.
- Three bounded escalation levels use 5-, 10- and 15-minute delays.
- Separate operator-token-protected list, acknowledge and resolve routes.
- Incident state survives process restart when the configured SQLite file is on durable storage.

Escalation currently emits structured application logs. It does not prove delivery to an independent human notification channel.

## 2. Current gaps — why Gate 38 remains orange

1. No deployed central collector or dashboard.
2. No multi-worker or multi-instance aggregation and scrape inventory.
3. No durable metrics retention, log rotation policy or disk-capacity alert.
4. No WebSocket telemetry aggregation for active sessions, close codes, reconnects, consumer lag, publisher cursor drift or snapshot age.
5. No integrated alert routing to an independently monitored operator channel.
6. No owner-host evidence for scrape network restrictions, token injection/rotation, retention behavior, disk pressure or incident recovery.

A successful CI container smoke test is not a production monitoring acceptance test. It does not establish an active host or persistent monitoring service.

## 3. Required no-cost acceptance evidence

Before Gate 38 can turn bright green, an owner-controlled runtime must demonstrate:

- Metrics endpoints are private and return 401 for missing/wrong bearer tokens.
- The configured operator can scrape each running process without exposing the token in URLs, logs or browser history.
- A collector identifies each process/instance and aggregates without double-counting.
- The dashboard shows HTTP request/error/latency metrics, backend health, publisher/consumer progress, Redis status, WebSocket connection/reconnect behavior, SQLite capacity and open incidents.
- Metrics and logs have explicit bounded retention, rotation and disk-pressure behavior.
- A controlled alert can be observed, acknowledged and resolved through the actual operator workflow.
- Restart/recovery preserves incident state on the real persistent volume.
- No user identifiers, account IDs, raw query strings, tokens or secret-bearing environment values appear in exported telemetry.

## 4. Zero-cost boundary

Do not add a hosted vendor, paid object store, paid database, billing-enabled project or public metrics endpoint. If a genuinely secure no-cost collector/dashboard cannot be operated on infrastructure the owner already controls, keep Gate 38 🟧 OPEN and defer the external integration. Do not weaken authentication or retention to manufacture a green result.

**No server exists yet.** No Termux command, credential, deployment or user-side code change is required for this repository audit.
