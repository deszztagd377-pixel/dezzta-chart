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

**Implemented in the reconnect path (CI-verified on 2026-11-10):** clients may supply their last durable cursor as an unsigned decimal string; the server validates it, authorizes the exact canonical series, and performs bounded exact-series replay. The server registers the live subscription before replay, emits replay events with a fresh stream ID and stream-local sequence, then hands off queued live updates with sequence continuity. Events already covered by replay are removed from the queued handoff. If the cursor is expired/ahead, replay storage is unavailable, or the backlog exceeds the 10,000-event socket replay cap, the server explicitly requests a fresh snapshot instead of silently skipping history. The frontend validates replay boundaries and event sequences, applies each event before advancing its cursor, preserves the last validated chart during transient reconnect, and replaces it only after a resnapshot. Cursor values travel as decimal strings to preserve SQLite 64-bit integer precision in JavaScript.

**Still required:** sustained write/reconnect benchmarks with P50/P95/P99 measurements, real browser and Android WSS tests against the deployed reverse proxy, and production evidence for Firebase/Redis/volume/backup/monitoring/provider gates. The replay code is repository-tested; it is not yet production-deployment proof.


## 11. Durable cursor propagation into WebSocket snapshot/live path

Implemented and CI-verified on commit `26a9ed840449cab9abeb573d5029b02d8fcbe998`:

- Snapshot setup reads the outbox high-water and performs the in-memory pipeline snapshot plus subscription registration without an intervening await on the single-writer event loop. The response includes `cursor` and declares its scope as a global outbox cursor filtered by exact series identity.
- Live notifications now carry the durable cursor and the persisted stable event ID rather than relying only on a per-connection sequence.
- The callback resolves the exact outbox row for the bar revision. It deliberately does not attach the global latest cursor: derived bars can be persisted between a source bar commit and its notification callback. Exact series identity, timestamps, sequence, and decimal OHLCV are checked before returning the cursor/event ID.
- Regression tests cover snapshot high-water, live cursor progression, stable event ID propagation, and distinct source/derived timeframe cursors.
- CI passed on the exact commit: frontend tests/build and bundle secret scans, backend pytest/dependency audit, Docker image build, Redis + persistent-volume smoke test, Trivy scan/report export/upload. CodeQL JavaScript/TypeScript and Python both passed.

**Implemented in the reconnect path (CI-verified on 2026-11-10):** clients may supply their last durable cursor as an unsigned decimal string; the server validates it, authorizes the exact canonical series, and performs bounded exact-series replay. The server registers the live subscription before replay, emits replay events with a fresh stream ID and stream-local sequence, then hands off queued live updates with sequence continuity. Events already covered by replay are removed from the queued handoff. If the cursor is expired/ahead, replay storage is unavailable, or the backlog exceeds the 10,000-event socket replay cap, the server explicitly requests a fresh snapshot instead of silently skipping history. The frontend validates replay boundaries and event sequences, applies each event before advancing its cursor, preserves the last validated chart during transient reconnect, and replaces it only after a resnapshot. Cursor values travel as decimal strings to preserve SQLite 64-bit integer precision in JavaScript.

**Still required:** sustained write/reconnect benchmarks with P50/P95/P99 measurements, real browser and Android WSS tests against the deployed reverse proxy, and production evidence for Firebase/Redis/volume/backup/monitoring/provider gates. The replay code is repository-tested; it is not yet production-deployment proof.

## 12. Current live-feed coverage constraint

The live source is Databento `ohlcv-1s` and subscribes only to explicit raw contract symbols from `DATABENTO_LIVE_SYMBOLS`. That configuration defaults to an empty tuple; the current default allowed roots are ES, NQ, and GC. Therefore this repository does **not** currently prove live coverage for every pair/contract. A configured provider credential, licensed entitlement, and explicit symbol list are required. Do not report all-pair real-time availability or zero delay until each requested instrument is configured, legally entitled, and monitored for gaps and timestamp latency.


## 13. Durable WebSocket reconnect and replay integration

Implemented on `phase-2/market-data-foundation`, exact tested commit `38174c9c4e6280669649cb4677426809c37d9cf5`:

- The subscription request accepts an optional durable `cursor` as a decimal string. The server rejects malformed or out-of-range values before replay.
- The server authenticates the Firebase principal and rechecks entitlement for the exact provider/dataset/publisher/instrument/series/symbol/timeframe identity before it reads replay history.
- The server registers the live queue before replay, preventing a replay-to-live subscription gap. Replay reads are exact-series filtered and bounded to 10,000 events per reconnect, with storage pages capped at 500.
- Replay events retain their persisted event IDs and durable cursors. The server adds a fresh connection stream ID and contiguous stream-local sequence. Live updates queued during replay are handed off after the replay boundary with contiguous sequence numbers; overlap already represented by replay is discarded.
- Expired/ahead cursors, unavailable replay storage, and excessive replay backlog produce an explicit `market_data.ohlcv.resnapshot_required` followed by a new snapshot. No missing history is silently represented as current.
- The browser client validates replay start/end cursors, event schema, exact series identity, and stream sequence. The supervisor advances the durable cursor only after applying validated updates, preserves the existing chart while transiently reconnecting, and resumes using the last accepted cursor.
- Durable cursors are serialized as decimal strings so values above JavaScript's safe-integer range remain exact.
- Regression tests cover exact-series replay, cursor-ahead resnapshot fallback, lossless cursor parsing, replay-to-live handoff, supervisor reconnect, and preservation of the last chart state.

Verification on the exact code commit:
- Automated Tests & Build: [run 42812016639](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812016639) — **success**.
- CodeQL Security Analysis: [run 42812016650](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812016650) — **success** for Python and JavaScript/TypeScript.
- CI included frontend tests/build/secret scans, backend pytest/dependency audit, Docker build, Redis + persistent-volume smoke test, Trivy image scan, and vulnerability-report export/upload.

**Not closed by this implementation:** production browser/Android WSS verification, managed Firebase/Redis configuration, deployed persistent volume, encrypted off-host backup/restore, external monitoring/alerting, provider licensing/coverage, and measured throughput/reconnect latency benchmarks. The 40-point matrix remains 30/40 with 10 external verification gates outstanding; Stage 1 is not production-accepted.


## 14. Cursor validation hardening checkpoint

Verified on exact code commit `9cb7a876bca9215b7792312aa908b3ad60e0b5a6`:

- Replay cursor input is restricted to ASCII decimal digits before integer conversion, preventing Unicode digit lookalikes from reaching integer parsing.
- Regression cases cover superscript and Arabic-Indic digit characters, decimal notation, excessively long values, and values above the signed SQLite 64-bit maximum.
- The malformed-cursor tests pass in Automated Tests & Build [run 42812627122](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812627122); CodeQL Python and JavaScript/TypeScript pass in [run 42812627082](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812627082).
- This hardening does not prove production WSS behavior, all-pair/all-timeframe provider coverage, or measured end-to-end latency. Those remain separate acceptance requirements.


## 15. Replay read event-loop isolation (candidate)

Candidate implementation on `phase-2/market-data-foundation`, commit `dac22020bfe10e48cef58f5125ee3e6d341bc969`:

- The WebSocket route now awaits `asyncio.to_thread(ohlcv_store.replay_outbox, ...)` for each bounded SQLite replay page. The store method opens and closes its own SQLite connection, while the existing live queue is registered before replay; queued live events can therefore continue to be serviced while replay I/O runs off the event-loop thread.
- This is intended to reduce event-loop blocking during reconnect backlogs. It is not a measured latency improvement yet. Exact-commit CI, concurrency/reconnect benchmarks, and production WSS measurements are still required before acceptance.
