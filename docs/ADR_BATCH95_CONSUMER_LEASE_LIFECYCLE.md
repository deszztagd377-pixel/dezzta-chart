# ADR — Batch 95 Consumer Lease, Fencing, and Retention Lifecycle

- Status: **PROPOSED — YELLOW**
- Date: 2026-11-27
- Scope: synthetic Durable Object delivery proof; production contract design
- Related PR: https://github.com/deszztagd377-pixel/dezzta-chart/pull/13
- Decision owner: DEZZTA CHART engineering

## 1. Problem statement

The current v4 `required_consumers` registry stores only registration time and an active flag. A consumer that disappears without an orderly close can remain active indefinitely. The compaction guard then correctly refuses to delete data, but storage retention can grow without bound. Simply expiring rows by age is unsafe unless the protocol explicitly makes expired clients resnapshot and rejects stale acknowledgements.

The lifecycle must therefore provide bounded ownership, explicit renewal, stale-owner fencing, safe deregistration, and a retention rule that agrees with the reconnect protocol.

## 2. Decision

Use a **lease with monotonically increasing fencing token** per logical consumer identity.

A lease record contains:

- `series_key`, `consumer_id`, and `generation_id`: existing scoped identity.
- `owner_token`: opaque current owner/session generation; never client-selected.
- `fencing_token`: monotonically increasing integer advanced whenever ownership is reacquired after expiry or deactivation.
- `lease_expires_at_ms`: absolute expiry based on the Durable Object clock.
- `active`: lifecycle state retained for audit and query efficiency.

A mutation is accepted only when series, generation, owner token, fencing token, and lease state match. An expired lease cannot be revived by a late ping or ACK. A new owner may acquire an expired identity, but the fence increments first. Old sockets can no longer ACK or deregister the replacement owner.

## 3. Timing policy for the synthetic proof

| Parameter | Proposed value | Rationale |
|---|---:|---|
| WebSocket lease | 120 seconds | Bounded retention obligation |
| Client heartbeat | 30 seconds | Four heartbeat intervals fit within the lease |
| HTTP proof registration | 300 seconds | Short-lived test fixture, not production identity |
| Minimum accepted lease | 15 seconds | Reject accidental near-zero leases |
| Maximum accepted lease | 300 seconds | Bound stale-consumer retention |

These are test-policy values, not a production SLO. A production mobile client may be suspended by the operating system; the protocol must treat a lease-expired reconnect as a fresh snapshot, not promise indefinite replay. Heartbeats are event-driven and leases are renewed by a valid ping or ACK. Do not create a recurring timer or a fixed polling loop.

Cloudflare Durable Object alarms are one-shot and must be rescheduled by the handler when more work remains. Schedule only the earliest actual expiry. This avoids a permanently running timer, but does not itself prove the Cloudflare account is on a zero-cost plan.

## 4. Lifecycle state machine

1. **Unregistered** — no required-consumer row exists.
2. **Active(owner, fence, expiry)** — registration committed in the same SQLite transaction as ownership fields.
3. **Renewed** — exact owner and fence renew before expiry; fence is unchanged.
4. **Expired** — clock reaches expiry; renewal and ACK are rejected.
5. **Reacquired** — a new owner takes over after expiry/deactivation; fence increments.
6. **Deregistered** — exact owner/fence deactivates the row; stale close handlers cannot deactivate a newer owner.

The Durable Object alarm marks expired rows inactive and closes expired attached sockets. A normal socket close deregisters only when the final socket for that owner generation is gone. Abrupt disconnect is handled by expiry.

## 5. ACK and compaction invariants

- A WebSocket ACK must refer to a sequence actually delivered to that socket and must match the persisted event digest.
- ACK commit checks the current lease owner and fence in the same synchronous SQLite transaction as the receipt update.
- A late ACK after expiry returns a stable rejection; it never recreates a lease.
- Compaction blocks while any **unexpired active lease** lacks a receipt at or beyond the proposed retention floor.
- Expired consumers no longer block compaction. Their reconnect path must receive `resnapshot_required` when the requested cursor is below the retention floor.
- If no consumer has ever been registered for the series, retain the existing fail-closed empty-registry guard.
- Expiry is not permission to delete the only canonical snapshot. Production compaction must retain enough source state to construct a valid replacement snapshot before advancing the floor.

## 6. Identity boundary for production

The current proof uses a synthetic subject and fixed synthetic consumer identity. It must not be exposed as a production authentication route.

Production sequence:

1. Client sends its Firebase ID token over HTTPS to the FastAPI backend.
2. The existing backend `FirebaseIdentityVerifier` verifies the token and checks revocation.
3. Backend derives an opaque consumer identity from the verified Firebase UID and a validated installation identifier. The raw UID and installation identifier are not accepted from the Worker as proof of ownership.
4. Backend issues a short-lived, one-time, series-scoped signed grant. The grant binds subject, opaque consumer ID, series, purpose, expiry, and unique ticket ID.
5. Worker validates the grant using a backend-held signing key's public counterpart. Firebase Admin credentials remain backend-only.
6. A new session for the same installation rotates ownership and fences the prior session. Separate installations have separate consumer identities.

The production grant format, key rotation, installation enrollment, logout/revocation propagation, and multi-tab policy require dedicated tests before production acceptance.

## 7. Failure and recovery behavior

| Failure | Required behavior |
|---|---|
| Client stops heartbeating | Lease expires; socket closes; later reconnect resnapshots |
| Delayed ping after expiry | Reject; do not revive old lease |
| Old socket ACK after replacement | Reject by fencing-token mismatch |
| Old socket close after replacement | Must not deregister the new owner |
| Duplicate registration by same live owner | Idempotent renewal; same fence |
| Compaction races with ACK | Serialize through DO protocol queue and SQLite transaction |
| Alarm runs more than once | Idempotent expiry update |
| Alarm is delayed | ACK still checks expiry synchronously; compaction excludes expired lease |
| v4 row has no owner proof | Deactivate during v5 migration; reconnect must register again |

## 8. Required test matrix

- v4 → v5 migration preserves series/event/receipt data and deactivates ownerless legacy registrations.
- First registration creates fence 1.
- Same-owner renewal preserves the fence and extends expiry.
- Different owner before expiry is rejected.
- Reacquisition after expiry increments the fence.
- Old owner ACK and deregistration are rejected after reacquisition.
- Current owner ACK succeeds only for a delivered sequence and matching digest.
- Expired lease cannot be renewed.
- Close of one of several sockets does not deregister the shared owner.
- Final socket close deregisters the owner.
- Alarm expiry is idempotent and closes expired sockets.
- Compaction blocks for an active lagging lease and proceeds after that lease expires, subject to the canonical-snapshot retention rule.
- Reconnect below retention floor receives a fresh snapshot instruction.
- ACK/expiry/compaction concurrency tests run against pinned workerd/Miniflare, not only mocked storage.

## 9. Rollout and rollback

- Keep changes on the existing PR branch; do not merge or modify `main` automatically.
- Migration is additive. Existing v4 ownerless rows are deactivated rather than guessed into live ownership.
- Deploy no Worker or Durable Object until Firebase grant verification and production namespace configuration are independently accepted.
- A rollback to pre-v5 code is expected to fail closed for retention (possible retention growth), not to infer lease ownership. Verify this behavior in migration tests before any deployment.
- Do not claim zero cost until the Cloudflare plan and usage limits are verified from an authorized billing view.

## 10. Schedule to the 24 December target

| Window | Engineering outcome | Acceptance evidence |
|---|---|---|
| 27 Nov–2 Dec | Lease/fence lifecycle and synthetic integration tests | Exact-head CI; migration, ACK, expiry, close, and compaction tests |
| 3–9 Dec | Firebase grant and installation ownership contract | Backend identity tests; signed-grant tamper, expiry, replay, and key-rotation tests |
| 10–16 Dec | Public WSS path and browser/Android integration | Real endpoint handshake, reconnect, replay, ACK, and resnapshot E2E |
| 17–21 Dec | Provider/legal and operational gates | Written redistribution scope, source provenance, rate limits, outage/recovery tests |
| 22–24 Dec | Release qualification | Full CI, zero-cost evidence, security review, rollback rehearsal, release checklist |

Dates are planning windows, not a promise of autonomous background execution. Any unresolved production acceptance item remains YELLOW.

## 11. Primary references

- Firebase Admin ID-token verification: https://firebase.google.com/docs/auth/admin/verify-id-tokens
- Firebase session revocation: https://firebase.google.com/docs/auth/admin/manage-sessions
- Firebase Admin `verifyIdToken(checkRevoked)`: https://firebase.google.com/docs/reference/admin/node/firebase-admin.auth.baseauth
- Cloudflare Durable Object WebSocket hibernation and attachments: https://developers.cloudflare.com/durable-objects/best-practices/websockets/
- Cloudflare Durable Object SQLite transactions: https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/
- Cloudflare Durable Object rules and alarm lifecycle: https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/

## 12. Acceptance status

This ADR is a design artifact. It does not change the production status of Batch 95. The current synthetic WebSocket ACK proof remains the last verified implementation milestone. Lifecycle implementation, Firebase grant binding, public WSS, provider approval, and device E2E remain YELLOW until code and exact-head CI evidence exist.
