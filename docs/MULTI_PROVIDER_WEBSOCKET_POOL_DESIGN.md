# Multi-provider WebSocket pool — zero-cost architecture

Review date: 2026-11-16  
Stage: 1 — Foundation, Security & Data Integrity  
Gate: 10 — market-data source and ingestion foundations  
Status: **provider-aware downstream WebSocket routing implemented and exact-HEAD CI verified; upstream multi-provider pool remains design-only; no new provider socket is active**

## Decision

DEZZTA CHART should support multiple independent market-data providers, but it must not open one WebSocket per symbol by default. The preferred design is a bounded **provider connection pool** with topic multiplexing where the upstream protocol supports it, plus a single provider-neutral internal event pipeline.

Five to ten upstream connections can be reasonable when they represent distinct providers or venue feeds. Ten connections per pair is not the target. The pool size is a deployment setting constrained by documented provider limits, device/server resources, and the zero-cost operating budget.

## Connection topology

```text
Provider A WS ─┐
Provider B WS ─┤
Provider C WS ─┤   bounded provider sessions
Provider ...  ─┘
        │
        ▼
Provider-specific decoder + schema validation
        │
        ▼
Canonical instrument / venue / event-time mapping
        │
        ▼
Bounded per-provider ingress queues
        │
        ▼
Deduplication + ordering + gap/staleness tracking
        │
        ▼
Provider-neutral normalized event bus
        │
        ├──► OHLCV aggregation / persistence
        ├──► quote and trade consumers
        ├──► order-book snapshot/delta consumer
        └──► client fan-out / chart subscriptions
```

The upstream connection count and downstream client subscription count are independent. A single upstream session may feed many local subscribers, but only if the provider's documented multiplexing rules permit it.

## Pooling rules

1. Keep at most one active session per provider endpoint/credential scope unless provider documentation requires separate sessions.
2. Multiplex symbols/topics on that session only when the provider explicitly supports it.
3. Split sessions by provider, venue, credential, or protocol when isolation is required.
4. Do not subscribe to every pair by default. Subscribe only to instruments with active demand and permitted feed scope.
5. Maintain a hard configured connection ceiling. A new provider must not silently increase the ceiling.
6. Use a single owner for each socket lifecycle; prevent duplicate reconnect loops and duplicate subscriptions.
7. On reconnect, re-authenticate if required, restore only the desired subscription set, then reconcile missed data using an allowed REST backfill path when available.
8. A provider outage must not cause an uncontrolled reconnect storm across healthy providers.

## Latency and resource controls

- **Exponential backoff with jitter:** bounded retry schedule, reset only after a stable session interval.
- **Heartbeat:** use the protocol's ping/pong or documented heartbeat; distinguish transport-alive from data-fresh.
- **Bounded queues:** cap both event count and approximate bytes per provider. Queue overflow is an observable incident, not permission to grow memory indefinitely.
- **Backpressure:** pause or reduce low-priority subscriptions where the provider supports it. If not, disconnect the slow consumer and resynchronize rather than corrupting sequence-sensitive data.
- **Coalescing:** latest-value ticker updates may be coalesced for chart display; trades, order-book deltas and sequence-sensitive events must not be silently dropped.
- **Parsing:** validate and normalize off the socket read loop where safe; keep the read loop short and avoid blocking persistence or client delivery.
- **Batching:** batch database writes and client fan-out with bounded latency; do not delay time-sensitive events behind large historical batches.
- **Compression:** enable only when supported and when CPU savings exceed decompression cost on the target hardware.
- **Observability:** record connection state, reconnect count, queue depth/age, message rate, parse failures, event lag, stale duration and dropped/coalesced counts.

No performance claim is accepted from connection count alone. Actual latency, CPU, memory, bandwidth and recovery must be measured on the target host/device before a capacity limit is approved.

## Data integrity rules

Every normalized event must retain, where supplied by the source:

- provider ID and venue/exchange ID;
- canonical instrument ID and original provider symbol;
- event type (trade, quote, depth update, candle, definition);
- source event timestamp and local receive timestamp;
- sequence/update ID and snapshot/delta semantics for order books;
- source schema/version metadata and raw-event provenance reference where retention is permitted.

Do not merge venue-specific books into a synthetic consolidated book unless a separately specified and validated consolidation algorithm exists. Do not silently switch a chart from one venue to another during failover. A fallback source must be explicitly marked and must pass instrument, session, currency, event-type and rights equivalence checks.

## Quota and zero-cost guardrails

- Encode provider limits as hard budgets: concurrent sessions, subscriptions per session, request weight, messages/second, REST backfill calls and monthly credits.
- Use a local quota ledger with a safety margin; do not rely only on a provider's response errors.
- On quota exhaustion, stop or degrade the affected feed and expose its stale/unavailable status.
- Never fall back to a paid endpoint, paid tier, expiring trial or metered credit.
- Do not create cloud infrastructure, managed queues, hosted Redis, paid monitoring or paid egress to support the pool.
- Public/no-key endpoints remain subject to terms, fair-use limits and redistribution review.
- Provider credentials, when necessary, remain server-side and must never be embedded in the APK or committed to the repository.

A recurring-$0 API plan does not prove zero total operating cost. Hosting, bandwidth, storage, backup, secrets and monitoring must also remain within the owner's explicitly approved free/self-hosted resources.

## Failure isolation and recovery

| Condition | Required behavior |
|---|---|
| One provider disconnects | Retry only that provider with bounded backoff |
| Provider sends malformed payload | Reject event, increment bounded error metric, keep other providers running |
| Queue reaches high-water mark | Apply documented coalescing or controlled disconnect/resync policy |
| Sequence gap in order book | Mark book invalid/stale and request a fresh snapshot; never apply later deltas blindly |
| REST quota exhausted | Do not backfill through a paid route; mark gap unresolved |
| Feed timestamp is old | Mark source stale; do not label chart as live |
| Provider schema changes | Fail validation closed and quarantine unknown payload shape |
| Credential is rejected | Stop retry storm; surface configuration fault without logging secrets |
| Process restarts | Rebuild desired subscriptions from configuration and reconcile source state |

## Candidate rollout sequence

1. **Inventory only:** record provider, endpoint, data family, venue scope, limits, freshness, authentication and official terms.
2. **Rights gate:** verify recurring $0 and the intended display/cache/redistribution rights. No approval means no activation.
3. **One adapter:** select one approved provider and one narrow event family; do not activate several providers simultaneously.
4. **Contract tests:** malformed payload, duplicate, out-of-order, reconnect, gap, stale feed, quota exhaustion and schema drift.
5. **Controlled integration:** compare provider events with documented fixtures and verify canonical instrument mapping.
6. **Measured capacity:** load-test increasing subscriptions and record p50/p95/p99 event lag, CPU, memory, network and queue depth.
7. **Second provider:** add only after first adapter has stable evidence; test isolation and explicit source labeling.
8. **Scale toward 5–10 providers:** only as distinct approved sources are justified by asset/venue coverage. Keep an explicit cap and per-provider budgets.

## Acceptance criteria before production activation

- Recurring total cost is evidenced as $0 for the exact workload; no billing fallback exists.
- Display, caching and redistribution rights are documented for the app's actual audience.
- Provider-specific session, subscription, rate and message limits are encoded as hard caps.
- Instrument/venue identity and event timestamp semantics are preserved.
- Duplicate, ordering, gap, reconnect, stale and malformed-data tests pass.
- Slow-consumer behavior is bounded and sequence-sensitive events are not silently lost.
- Target-environment measurements demonstrate acceptable latency, CPU, memory and bandwidth.
- Exact adapter commit has successful CI and controlled live verification.
- Operator can disable a provider without affecting unrelated providers.

## Implemented downstream routing boundary — 2026-11-16

The authenticated OHLCV WebSocket consumer is now provider-aware:
- subscription identity accepts an explicit provider while defaulting older clients to Databento;
- authorization resolves the exact provider/dataset/publisher/instrument mapping to the canonical instrument;
- snapshot query, fan-out identity and durable replay remain scoped to the same provider series;
- cross-provider fan-out is isolated by the full provider-scoped series identity;
- a provider without its own lifecycle status is never reported live by borrowing another provider's status.

The exact implementation is commit [3158a61](https://github.com/deszztagd377-pixel/dezzta-chart/commit/3158a61af80e378e1b27a4001fc1184f0a10a48f). Automated Tests, CodeQL and Full Git History Secret Audit all succeeded on that exact commit.

This is the downstream consumer boundary only. The upstream ingestion manager and source adapters remain Databento-oriented. No second provider client, connection pool, credentials, or live feed is active. Pair-coverage federation remains evidence-driven; no provider is claimed to support a pair without official scope, recurring-$0 cost and intended-use rights evidence.

No Termux action or paid service is required. This is a Stage 1 foundation change and does not close any of the ten external Stage 1 gates or authorize transition to Stage 2.
