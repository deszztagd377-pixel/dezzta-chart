# Stage 1 — WebSocket Reliability and Market-Data Integrity Blueprint

Status: owner-approved blueprint (2026-11-10). Durable outbox/replay implementation may proceed in reviewed increments. WebSocket-ticket code remains gated on a separate security review and passing threat-model tests.

Branch: `phase-2/market-data-foundation`
Baseline inspected: commit `bb604521d37262bdeb6745111c012a088429863a`

## 1. Non-negotiable requirements

- Never fabricate, silently interpolate, relabel, or present unavailable/stale data as live.
- Preserve provider provenance and timestamps. Keep event time, receive time, provider-out time (when supplied), sequence origin, bar origin, and completeness distinguishable.
- Use exact decimal prices/volume; preserve the existing canonical bar identity, provider precedence, and stale/duplicate rejection rules.
- Show explicit disconnected, delayed, stale, degraded, gap, partial, and unavailable states. A healthy API process is not proof of a live feed.
- Minimize latency without claiming physically impossible zero latency. Measure end-to-end and component latency using monotonic clocks where appropriate.
- Support multiple timeframes and multiple indicators concurrently. Each series subscription and each indicator instance must have isolated identity/state; one timeframe or indicator must not overwrite another.
- Prefer free/open-source infrastructure and a no-paid-service deployment profile. Do not activate a licensed feed or create a paid provider/service without a separate cost and entitlement review. A genuinely real-time exchange feed may not be available at zero cost; if no lawful free real-time source exists, disclose that limitation rather than substituting synthetic or mislabelled delayed data.

## 2. Current baseline and observed limitations

- `OhlcvIngestionService` is a single-writer asyncio consumer. Provider callbacks enter a bounded buffer; overflow is counted and recorded as a coverage gap rather than silently discarded.
- Accepted live bars are persisted through `SQLiteOhlcvStore.apply`, applied to the in-memory `OhlcvPipeline`, then passed to `OhlcvStreamHub.publish`.
- `SQLiteOhlcvStore` persists normalized OHLCV revisions and local-sequence high-water state, but it does not currently persist WebSocket delivery events.
- `OhlcvStreamHub` uses bounded in-memory per-subscription queues. Slow consumers are closed for resnapshot rather than silently skipping updates.
- Snapshot registration and live publish are atomic relative to one another on the same event loop, but a process restart loses in-memory subscriptions and there is no durable replay cursor.
- Current reconnect behavior is fresh authenticated snapshot/resubscription. Sustained write-rate and multi-process contention benchmarks remain outstanding.
- The backend has exact decimal OHLCV normalization, provider-vs-derived precedence, explicit completeness/provenance fields, and multiple supported timeframes. Exchange-session correctness still depends on verified calendar artifacts and policy.

## 3. Proposed durable event/replay design

1. Extend the existing SQLite OHLCV persistence boundary with a durable outbox. The bar revision and its corresponding outbox event must be committed in the same SQLite transaction; never publish an event for a bar revision that failed persistence.
2. Give each committed outbox event a monotonic durable cursor and stable event ID. Store the full canonical series identity (provider, dataset, publisher, instrument, series type, symbol, timeframe, bucket policy, calendar ID/version), operation/revision, source timestamps, sequence provenance, origin, completeness, and exact decimal OHLCV payload.
3. Keep the current in-memory fan-out as the low-latency notification path, but treat the durable outbox as the recovery source of truth. A notification is only a hint that a cursor may have advanced.
4. On reconnect, authenticate first, re-check entitlement for every requested series, then accept a bounded last-seen cursor per series (or a global cursor with server-side series filtering). Replay only authorized events after that cursor.
5. If the cursor predates retained history, is malformed, or cannot be proven continuous, return an explicit resnapshot-required response. Never skip the gap and pretend replay is complete.
6. Snapshot handoff must return a durable high-water cursor captured consistently with the snapshot. Replay begins strictly after that cursor. Clients deduplicate by stable event ID/cursor and apply revisions idempotently.
7. Retention and cleanup must be bounded and observable. Never delete events newer than the minimum acknowledged/retained recovery boundary. If no client acknowledgements are supported, define a conservative time/size retention and force resnapshot when older cursors expire.
8. Preserve fail-closed behavior: outbox write failure prevents the corresponding bar from being advertised as durably accepted; replay storage failure closes/rejects replay with a retryable degraded status rather than silently falling back to incomplete data.

## 4. Reconnect and multi-series semantics

- Connection lifecycle: authenticate -> authorize requested canonical series -> snapshot + cursor -> replay newer durable events -> live notifications.
- Every subscription is keyed by the complete canonical series identity, including timeframe and calendar policy. Multiple timeframes can be active on one connection without sharing cursors or queues.
- Reconnect uses the last durably applied cursor, not a timestamp guessed by the client. Duplicate delivery is expected and harmless; missing cursor ranges require resnapshot.
- Queue overflow, server restart, expired cursor, authorization change, and provider recovery each have explicit protocol outcomes.
- Revalidate identity and entitlement during long-lived sessions as the current implementation already does. A reconnect never inherits stale authorization.
- Indicator instances must be keyed independently from their source series and settings. Multiple indicators on the same chart/timeframe, and indicators across multiple timeframes, must coexist. Indicator calculations must not mutate canonical provider bars.
- Derived timeframe bars must be reproducible from validated source bars and an explicit bucket/calendar policy. Do not fill missing intervals with invented OHLCV. Mark incomplete/gapped coverage and recompute affected derived bars when legitimate late provider corrections arrive.

## 5. Short-lived scoped WebSocket ticket threat model

- Keep Firebase ID-token verification on an authenticated HTTPS ticket-issuance endpoint; do not put Firebase ID tokens in URL query strings.
- Issue an opaque, cryptographically random, one-use ticket with a short configurable TTL. Bind it server-side to verified subject, allowed origin/client context, requested canonical series scope, and an audience/purpose of WebSocket connection establishment.
- Store ticket state in shared Redis with TTL and consume it atomically (single-use) using a Redis transaction/Lua operation. Never trust a subject, entitlement, or scope supplied by the WebSocket client.
- On consume, verify expiry, origin, audience, one-use state, and current entitlement. Fail closed on Redis/provider verification outage. Do not log ticket values; return generic errors.
- Do not broaden a ticket's scope after issuance. Reconnect requires a new ticket. Revocation/entitlement changes must invalidate or deny the next handshake.
- Keep Firebase ID-token first-message authentication as the current safe baseline until this design is reviewed and tests demonstrate that the ticket flow reduces exposure without weakening authorization. Ticket exchange is not required merely for appearance or convenience.

## 6. Cost and deployment guardrails

- First evaluate whether the existing SQLite persistent volume plus already-required Redis can support the measured outbox/replay workload on the chosen free deployment profile.
- Do not assume managed Redis, hosting, exchange data, or backup storage is permanently free. Verify current free-tier limits, sleep behavior, storage limits, and licensing before selecting a provider.
- Keep a single backend writer/replica until concurrency benchmarks prove the storage and lease design safe. Do not scale replicas just to chase throughput if SQLite volume semantics are not safe for that provider.
- If a zero-cost deployment cannot provide lawful real-time market data, show delayed/unavailable status honestly and keep the provider disabled. Do not fabricate ticks or candles.

## 7. Benchmark and acceptance plan

Before implementation, capture a baseline and define target capacity from realistic client/provider needs. Benchmark at least:
- 1, 2, and 4 concurrent backend worker/process configurations where supported by the selected storage topology;
- sustained writes at increasing rates, burst recovery, queue overflow, replay backlog, and reconnect storms;
- SQLite write-lock wait, transaction duration, outbox growth/cleanup, Redis lease operations, CPU/memory, and end-to-end event latency;
- P50/P95/P99 for callback-to-persist, persist-to-publish, replay, and reconnect-to-live;
- correctness under duplicate, stale, late-correction, out-of-order, provider restart, process crash, and entitlement revocation scenarios.

Record environment, workload, commit SHA, data source, result distributions, and known limits. Do not claim zero lag or high accuracy from a synthetic benchmark alone. Production acceptance requires real-provider timestamp/provenance checks and a documented gap/correction audit.

## 8. Required regression tests

- Atomic bar + outbox commit/rollback; no event for failed or rejected persistence.
- Stable cursor/event IDs across process restart; replay exactly after cursor with duplicate-safe application.
- Expired/unknown cursor forces explicit resnapshot; no silent holes.
- Snapshot/high-water handoff under concurrent publish has no missed event window.
- Unauthorized series cannot be replayed even with a guessed cursor or modified client identity.
- One-use ticket replay, expiry, wrong origin/audience, scope escalation, Redis outage, token revocation, and entitlement revocation all fail closed.
- Queue overflow and server restart recover via durable replay or explicit resnapshot.
- Concurrent 1s/1m/5m/etc. subscriptions and multiple independent indicator instances do not overwrite each other's state.
- Provider bars remain authoritative over derived bars; missing intervals remain missing; late provider corrections recompute only affected derived outputs.
- Latency/throughput tests report measured percentiles and never relabel simulated data as provider data.

## 9. Implementation gates

1. **Complete — owner approved this blueprint on 2026-11-10**, including the replay cursor model, outbox retention policy, benchmark plan, and ticket threat model.
2. **Still required before ticket code:** independent security review of the ticket threat model and storage/atomic-consumption design, followed by fail-closed regression tests.
3. Benchmark baseline and deployment topology are documented before choosing SQLite-only or a separate broker.
4. Implement in small migrations with rollback strategy, bounded storage, fail-closed behavior, and regression tests.
5. Re-run CI, CodeQL, container smoke/Trivy, and crash/restart/replay tests on the exact candidate commit.
6. Production provider, licensing, hosting cost, and monitoring are reviewed separately. No paid service or provider credential is enabled by this blueprint.

This document is a proposal, not proof of implementation, provider entitlement, production availability, or zero-latency performance.


## 10. First implementation increment — transactional SQLite outbox

Implemented on the approved branch as a storage-layer increment (pending exact-commit CI verification):

- OHLCV schema version 3 creates `ohlcv_outbox` and its exact-series/cursor index, plus durable `high_water` and `retention_floor` metadata. Existing schema-v2 OHLCV rows are preserved; the shared SQLite `user_version` remains owned by the instrument registry.
- `SQLiteOhlcvStore.apply` writes the accepted bar revision and its outbox event in the same `BEGIN IMMEDIATE` transaction. A failed outbox insert rolls back the bar write. Duplicate, stale, expired, and provider-precedence-rejected bars do not create events.
- Event payloads preserve the complete canonical series identity, exact decimal strings, nanosecond timestamps, sequence provenance, origin, and completeness. Each committed event receives a stable opaque event ID and monotonic SQLite cursor.
- The initial bounded retention policy is a maximum of 100,000 events. Pruning advances a durable retention floor; a replay cursor below that floor (or ahead of the durable high-water) returns `resnapshot_required` rather than silently omitting history.
- `replay_outbox` returns a bounded exact-series replay page. Its global cursor can advance across unrelated series only when no matching events remain before the high-water; when more matching events remain, it stops at the last returned event cursor.
- Regression coverage was added for transaction rollback, restart replay, exact decimal preservation, deduplication, series isolation, and retention-expiry behavior.

**Not yet complete:** the current WebSocket route still uses its in-memory subscription watermark and has not yet been wired to this durable cursor/replay API. Snapshot/high-water handoff, reconnect protocol integration, live notification cursor propagation, multi-series authorization/replay, and sustained write/reconnect benchmarks remain follow-on implementation and verification work. This increment alone does not claim durable WebSocket reconnect is production-ready.
