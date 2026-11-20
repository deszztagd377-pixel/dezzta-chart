# Batch 62J-40 — bounded FCM child-process delivery

Date: 20 November 2026  
Branch: `phase-2/market-data-foundation`

## Objective

Close the unsafe cancellation gap in Gate 39 without changing the durable outbox's at-least-once semantics, token encryption, owner scoping, or stable event-id deduplication.

## Root cause addressed

The Firebase Admin Python sender is synchronous. Running it via `asyncio.to_thread` keeps the ASGI loop responsive, but cancelling the awaiting coroutine does not stop a synchronous call already executing in its worker thread. A provider call could therefore outlive the lease, be reclaimed by another worker, or delay application shutdown.

## Implementation

- Added `backend/app/alert_fcm_process.py`.
- One claimed event's bounded fan-out (maximum 10 registered devices) executes in one disposable `spawn` child process.
- The parent enforces a **60-second total event deadline**. A timed-out child is terminated, then escalated to kill after a 2-second grace period.
- Firebase Admin ADC initialization and token decryption happen inside the child. Tokens do not cross the IPC pipe and are not included in logs or error payloads.
- The child returns only a sanitized success/error classification. Explicit `UNREGISTERED` token invalidation continues to revoke only the affected installation.
- A timeout or child failure becomes a retryable, sanitized `FCMDeliveryError`; the durable outbox schedules a retry.
- Partial provider acceptance remains **at-least-once**, not exactly-once. Retries retain the immutable `event_id` for client-side deduplication.
- Main lifespan no longer initializes the synchronous FCM sender in the ASGI parent; per-event child initialization failures are retried through the outbox.

## Deadline / lease calculation

| Component | Bound |
|---|---:|
| Child event deadline, including ADC startup, SQLite token reads, up to 10 sequential sends | 60 s |
| Process exit grace before kill escalation | 2 s |
| Parent outbox acknowledgement / SQLite contention allowance | 10 s |
| Calculated minimum | 72 s |
| Configured minimum lease when worker enabled | **90 s** |
| Default configured lease | **120 s** |

At the configured default, nominal reserve after the 60-second event deadline, 2-second process cleanup and 10-second acknowledgement allowance is:

`120 - 60 - 2 - 10 = 48 seconds`

At the minimum permitted lease:

`90 - 60 - 2 - 10 = 18 seconds`

The lease is validated only when the FCM worker is enabled; disabled installations retain existing settings compatibility. The worker's batch size remains 1, so there is no multiplication by multiple claimed events.

## Shutdown behavior

The lifespan shutdown sets the worker stop event and awaits the active batch. Since the sender returns after at most the child deadline plus bounded process cleanup, the current event no longer has an unbounded synchronous-provider wait under normal process scheduling. The worker then observes the stop event and exits. A forced child termination can leave partial provider acceptance; the outbox deliberately retries using the same event id.

OS-level uninterruptible process states cannot be mathematically excluded by application code. CI tests verify the normal process timeout/termination path, not every host kernel failure mode.

## Tests added

- Spawned child returns a structured result.
- Hung child is terminated at the deadline.
- Parent passes event metadata, not decrypted FCM tokens, through the IPC arguments.
- Timeout is converted to a retryable sanitized outbox error.
- Permanent invalid-token classification survives IPC.
- Incomplete events are rejected before process creation.
- Configuration rejects an enabled worker lease below 90 seconds and accepts 90 seconds.

Existing fan-out tests continue to cover owner-scoped delivery, invalid-token revocation, transient retry, and stable event-id deduplication.

## Boundaries / no overclaim

- No real Firebase project or external FCM call was made in CI.
- No public backend deployment, paid provider, Vercel, Cloudflare, or Termux operation.
- This closes the source-level bounded-process/shutdown design gap only after exact-head CI passes. Gate 39 still needs owner-host induced-failure alert, operator acknowledgement/escalation, and real incident-recovery acceptance.
- Gate 25/30/31/34/35/36/38 remain external acceptance items.
- No indicator formula or UI code changed; indicator status is unchanged.

## Changed files

- `backend/app/alert_fcm_process.py` (new)
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/tests/test_alert_fcm_process.py` (new)
- `backend/tests/test_config.py`
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
- `docs/INDICATOR_PROGRESS_LEDGER.md`
- `docs/WORK_CYCLE_2026-11-20_BATCH62J40_FCM_PROCESS_ISOLATION_DEADLINE.md` (new)
