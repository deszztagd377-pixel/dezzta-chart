# Batch 62J-37 — Gate 38 metrics boundary and Gate 39 bounded-worker design proposal

**Date:** 20 November 2026  
**Branch:** phase-2/market-data-foundation  
**Audited starting HEAD:** 04139cf0b43812c4afd09e8b5114d15df1aa2be9  
**Scope:** source audit plus design proposal only. No runtime source, tests, dependencies, provider settings, or deployment configuration changed.

## Gate 38 — bounded metrics source audit

Inspected backend/app/observability.py, its tests, and the FastAPI request-observation / private-scrape wiring.

Verified repository behavior:

- Metrics are process-local and explicitly scoped process_local_since_start; there is no persistent metrics store or cross-replica aggregation.
- Route/method series are capped at 127 total entries, including one reserved overflow series.
- Method labels are allow-listed; route labels must be slash-prefixed and at most 160 characters or become unmatched.
- Status labels are reduced to HTTP status classes; durations are finite, non-negative and capped at one day.
- Each route/method latency series has ten fixed buckets plus the overflow bucket; caller-controlled values cannot create additional histogram dimensions.
- Snapshot output is detached from internal state and protected by a lock.
- /internal/metrics and /internal/alert-delivery require exact Bearer-token authentication, use constant-time comparison, and return no-store/security headers.
- Both internal scrape paths are excluded from application request counters and HTTP request logs. HTTP logs omit raw URL, query, path parameters, headers and client address.

Tests verify the series cap/overflow accounting, label and duration sanitization, detached snapshots, concurrent recording, and the middleware exclusion/authentication behavior.

**Gate 38 remains 🟧 OPEN.** These controls establish bounded in-process instrumentation, not a production observability service. Still outstanding: owner-host dashboard/access control, multi-process aggregation, bounded log retention/rotation, disk-pressure behavior, and live verification that secrets/tokens are absent from host logs and crash reports. No external monitoring service is proposed; ZERO COST remains the constraint.

## Gate 39 — why a request timeout alone is not a hard event deadline

Current implementation facts:

- FirebaseCloudMessagingSender initializes Firebase Admin with projectId only; it does not set httpTimeout.
- Firebase Admin's documented default is 120 seconds per HTTP request when that option is omitted.
- One event fans out sequentially to up to ten active installations.
- The outbox lease defaults to 120 seconds and batch size is fixed at one event.
- The worker calls the synchronous delivery batch through asyncio.to_thread; lifespan shutdown sets the stop event and awaits the worker task.
- The synchronous send can therefore outlive the lease or delay shutdown. Cancelling the coroutine awaiting to_thread does not stop the underlying thread.

A numeric requests timeout is not, by itself, a proven total wall-clock deadline for a sequence of provider calls. It also does not provide a safe way to terminate a synchronous send already running in a thread. Do not patch this by wrapping the await in asyncio.wait_for or by selecting a lease value from a simple multiplication.

## Proposed architecture for owner review — not approved for implementation

**Recommendation:** retain the durable single-event outbox and isolate the complete synchronous FCM fan-out for one event in a short-lived child process with a parent-enforced monotonic wall-clock deadline.

Proposed flow:

1. The existing worker claims one event and loads at most ten active owner-scoped device installations in the parent process.
2. A spawned child process initializes Firebase Admin from runtime ADC and performs the sequential fan-out. It receives only the event payload, project ID, and the bounded recipient data required for delivery; credentials are not serialized or passed as arguments.
3. The child sends bounded per-recipient result records to the parent over a local IPC channel. Result records contain installation identifiers and sanitized outcome classifications, never registration tokens or raw provider exceptions.
4. The parent consumes results while supervising the child against an absolute time.monotonic() deadline. On deadline or shutdown expiry it terminates, then force-kills if needed, and joins the child before returning. It must verify that no child remains alive.
5. The parent alone revokes explicitly invalid registration tokens and acknowledges the outbox event. A retryable error, child crash, or deadline leaves the event retryable; already accepted recipients may receive the same event again, preserving the existing at-least-once contract and stable event_id.
6. Shutdown semantics become explicit: finish the current event only until its hard deadline, terminate the child if the deadline is reached, then stop the worker. No coroutine cancellation is treated as proof that provider I/O stopped.

The child-process boundary is proposed because terminating a process can stop its synchronous network call; cancelling an asyncio task or thread future cannot. It adds process-start overhead and must be tested under the actual container/runtime model before adoption. If process isolation is rejected, the alternative requires a genuinely cancellable async HTTP transport and a separately reviewed ADC token-refresh design; simply setting httpTimeout is not equivalent.

### Lease arithmetic to validate before coding

Define:

- T_event: parent-enforced monotonic deadline covering child startup, all recipient sends, result collection and child termination.
- T_db: configured SQLite busy-timeout budget for the final outbox acknowledgement/reschedule transaction.
- M: explicit scheduling, process teardown and measurement margin.

Require:

lease_seconds >= T_event + T_db + M

The candidate design value is T_event = 60 s; the existing SQLite busy timeout is 10 s; reserve at least 20 s for teardown/acknowledgement margin. This yields a provisional minimum lease of 90 s, so the current 120 s default has 30 s spare budget. These are **design candidates, not accepted production settings**. Tests must measure process startup/termination and database acknowledgement under load before values are finalized. The worker must reject configurations whose lease does not satisfy the derived inequality.

The deadline is enforced with a monotonic clock; the durable lease timestamp continues using the store's existing wall-clock nanosecond contract. A child timeout is a retryable failure, not a delivered event. A send accepted by FCM immediately before forced termination may be repeated after reclaim; this remains at-least-once delivery, not exactly-once.

### Required acceptance tests before implementation is considered complete

- Zero, one and ten recipient fan-out, including owner scoping.
- Per-recipient success and invalid-token revocation by the parent only.
- Retryable failure after earlier recipient success; stable event_id on retry.
- Child startup failure, child crash, IPC closure and malformed result handling.
- A deliberately blocked provider call reaches the hard deadline; child is terminated and joined; no orphan process remains.
- Lifespan shutdown during a blocked send completes within the documented event deadline plus acknowledgement margin.
- A second worker cannot reclaim the event before the configured lease expires; stale acknowledgement remains rejected.
- Process-spawn behavior is tested in the same Linux/container execution model used by CI.
- No tokens, credential values, raw provider payloads or absolute secret paths appear in logs, status responses or test artifacts.
- Full backend tests, frontend tests/build, container smoke, CodeQL and full-history secret audit all pass on the exact resulting HEAD.

### Explicit non-goals

- No new paid provider, hosted queue, monitoring service or deployment.
- No claim of exactly-once FCM delivery or Android display deduplication.
- No change to public alert routes, device-store encryption, owner scoping or current event payload.
- No main branch change and no Termux requirement.

## Gate and indicator accounting

Gate 38: 🟧 OPEN. Gate 39: 🟧 OPEN. Gate 10 remains 10/10 🟧 ORANGE / 0 CLOSED.

Indicator states are unchanged: SMA20 🟨 (first valid index 19); EMA20 🟨 (19); RSI14 🟨 (14); MACD12/26/9 🟨 (MACD index 25, signal/histogram 33); Bollinger20,2 🟨 (19); Shared Indicator Hook 🟨; Footprint 🟧 SIMULATED and gated on the owner reference image plus reviewed blueprint; Heatmap 🟥; Liquidation Maps 🟥. No indicator implementation or completion credit is included in this batch.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 remain unscored. Overall project and indicator aggregate percentages remain unestablished because approved weights/denominators do not exist.

## Change boundary

Documentation only. No runtime code, test code, dependencies, provider settings, production activation, deployment, paid service, Termux operation or main branch modification.
