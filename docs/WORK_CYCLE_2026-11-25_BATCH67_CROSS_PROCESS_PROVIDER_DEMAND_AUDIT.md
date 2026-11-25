# DEZZTA CHART — Work Cycle 67: cross-process provider-demand ownership audit

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent HEAD: `b6cb9137f41b183d4dfa2983949c5a60fd4a9d16`  
Scope: source-backed Redis ownership-layer audit and safe next-step architecture  
Cost: ZERO COST  
`main`: untouched • Vercel deployment: deferred • Live provider: not enabled

## 1. Audit question

Can an existing Redis lease/guard be reused as the cross-process owner registry for on-demand market-provider subscriptions?

**Finding: no.** The repository contains Redis primitives for two different ownership problems, neither of which is a shared per-series provider-demand owner set.

## 2. Source evidence

### `backend/app/ohlcv_redis_lease.py`

- Uses `SET NX PX` with a random token and TTL.
- Uses token-checked Lua for renewal, ownership assertion and release.
- The key is derived from a generation-scoped replica consumer-group name.
- Purpose: exclusive ownership of one gateway replica consumer group, with fail-closed fencing.
- Semantics: one active process owner per consumer group.

This is not suitable for a series with multiple legitimate chart owners. Reusing it per provider key would incorrectly reject the second chart/user instead of adding another owner.

### `backend/app/ohlcv_redis_consumer.py`

- Each gateway replica has its own generation-scoped consumer group.
- The consumer applies events durably to its replica store before ACK.
- Ownership guard is checked at event boundaries.

This is delivery ownership for replica consumption, not ownership of an upstream market-data subscription.

### `backend/app/shared_guard.py`

- Redis sorted sets track global and per-account WebSocket connection quotas.
- Connection leases expire and renew for security/rate-limit purposes.
- Ticket consumption is one-time.
- No canonical provider-series owner registry, desired-subscription state, provider reconciliation epoch or provider-side ACK is represented.

A WebSocket connection quota lease must not be treated as proof that the connection is entitled to or currently owns a particular upstream provider subscription.

### `backend/app/provider_demand.py`

- Coordinator and pending-release IDs are process-local dictionaries/sets guarded by one asyncio lock.
- The offline adapter performs no I/O.
- The pending-release queue is not durable across process restart.
- The coordinator is not wired to `ProviderManager` or a live provider.

## 3. Correct ownership layers

| Layer | Current primitive | Actual purpose | Provider-demand reuse |
|---|---|---|---|
| Client connection quota | Redis ZSET in SharedGuard | Enforce global/account connection caps | NO |
| Gateway replica consumer | Token-fenced Redis SET lease | Exclusive consumer-group process owner | NO |
| Offline provider demand | In-memory owner/lease maps | Same-process 0↔1 reference counting | Local test foundation only |
| Cross-process provider demand | None accepted | Multi-owner desired state per canonical upstream series | OPEN |

These layers must remain separate. Treating them as interchangeable risks false release, leaked upstream subscriptions, or one gateway/client releasing another owner's demand.

## 4. Conditional architecture for a future provider adapter

Only after a lawful recurring-$0 source and a verified adapter capability contract exist, a distributed coordinator may be designed with:

1. **Canonical key:** provider/source, venue, dataset, canonical instrument, input symbology, schema/channel and timeframe where the provider actually scopes subscriptions by timeframe.
2. **Owner identity:** opaque per-chart/per-connection owner token, bound to authenticated subject and authorization decision; never use a client-supplied owner string as authority.
3. **Lease/TTL:** bounded owner expiry plus explicit release. Heartbeat loss must not silently preserve an indefinite owner.
4. **Atomic state transition:** Redis Lua or an equivalent transactional primitive atomically updates owner membership, desired-state version and a durable reconciliation intent. Do not perform network I/O inside Lua.
5. **Fenced reconciler:** one elected worker per provider/session partition, with a monotonically increasing fencing epoch so an old worker cannot overwrite a newer desired state.
6. **Provider capability declaration:** dynamic subscribe/unsubscribe, multiplexed subscription set, restart-required reconfiguration, or unsupported. No implicit dynamic capability.
7. **Idempotent provider commands:** stable command identity and explicit provider acknowledgement/error state. A local desired-state write is not provider acceptance.
8. **Recovery:** on worker restart, provider reconnect, lease expiry and entitlement revocation, rebuild desired subscriptions from authoritative live owners and reconcile observed provider state.
9. **Fail-closed visibility:** until provider acknowledgement is confirmed, status must remain pending/unavailable rather than live.
10. **Isolation:** release of owner A cannot stop a series while owner B remains authorized and active.

This is an architecture direction, not an implemented or approved schema. Exact Redis key layout, TTLs, Lua contracts, stream/outbox semantics and failure policy require a pinned provider capability and a scoped reviewed blueprint before coding.

## 5. Blocking prerequisites and decision

- Recurring-$0 entitlement and application display/redistribution rights: NOT APPROVED.
- Exact live provider SDK/API and version: NOT VERIFIED.
- Dynamic subscription capability and provider ACK: NOT VERIFIED.
- Cross-process provider-demand state: NOT IMPLEMENTED.
- Multi-host provider reconnect/reconciliation acceptance: NOT IMPLEMENTED.

**Decision:** do not wire a distributed provider-demand coordinator yet. Building it before the provider contract is known would risk implementing the wrong upstream identity and acknowledgement semantics. The current offline coordinator remains useful for local lifecycle regression but receives no production integration credit.

## 6. Batch 66 test status

Batch 66 adds two concurrency regressions:
- 32 simultaneous duplicate releases of one lease: exactly one successful release and one upstream stop.
- 16 distinct owners releasing a shared key concurrently: one upstream start, one final stop, zero residual owners.

Those tests belong to source/test commit `b6cb9137f41b183d4dfa2983949c5a60fd4a9d16`. Their exact-head CI must be reported separately from this documentation audit.

## 7. Indicator and project accounting

No indicator source, formula, hook, renderer, chart UI or indicator test changed in Batch 66/67. Indicator completion credit remains zero. Refer to `docs/INDICATOR_PROGRESS_LEDGER.md` for the full twelve-row inventory and numerical contracts.

- Stage 1: 30/40 = 75% provisional inherited baseline 🟨.
- Stage 2: active engineering, denominator not approved 🟦 NOT SCORED.
- Stage 3: ⬜ NOT SCORED.
- Stage 4: 🟪 GATED.
- Stage 5: ⬜ NOT SCORED.
- Stage 6: ⬜ NOT SCORED.
- Gate 10: 0/10 formally closed 🟥.
- Overall project: ⚪ NOT SCORED.
- Aggregate indicator completion: ⚪ NOT SCORED.
- Significant progress / IP3S: ⚪ NOT SCORED.

Target remains approximately 24 December 2026. ZERO COST maintained. No paid service, deployment, Vercel action, destructive Redis operation or `main` update.
