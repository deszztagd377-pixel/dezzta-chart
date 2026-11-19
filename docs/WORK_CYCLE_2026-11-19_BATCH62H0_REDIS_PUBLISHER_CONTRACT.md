# Batch 62H-0 — Redis Streams publisher contract and implementation guard

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Parent checkpoint:** `3bccf107ff88a2bc7330afa1015e85b20708c773`  
**Scope:** repository audit + implementation contract only. No runtime code changed, no Redis service provisioned, no app startup wiring, no deployment.

## Audit result

The current repository already has `redis>=5.2,<7`, and `RedisSharedGuard` in `backend/app/shared_guard.py` uses Redis Lua scripts for HTTP limits, WebSocket leases and one-time tickets. That Redis integration is a security control, not a market-data relay.

In `backend/app/main.py`, accepted bars are persisted by `SQLiteOhlcvStore`; the callback then resolves the exact committed outbox event and publishes it to the process-local `OhlcvStreamHub`. The hub is not cross-process transport. The authoritative outbox remains in SQLite and is globally cursor-ordered.

The store already exposes `read_outbox_batch(after_cursor, limit)`. It returns bounded global pages, a consistent high-water and retention floor, and detects expired/ahead cursors or missing cursor continuity. This is the correct source API for a future relay publisher; exact-series `replay_outbox()` is not.

## 62H publisher contract

1. **Authority:** SQLite outbox remains the source of truth. Redis is a transport/cache of durable event delivery, never the only copy.
2. **Cursor identity:** map source cursor `C` to Redis Stream ID `C-0`; preserve the original `eventId` and canonical event envelope as stream fields.
3. **Publisher checkpoint:** persist the last confirmed Redis append cursor in the source SQLite database. Advance it only after the Redis append is confirmed or a same-ID entry is read back and byte-for-byte/canonically verified.
4. **Crash window:** if XADD succeeds and the process dies before SQLite checkpoint commit, retry the same deterministic Stream ID. A duplicate-ID response is not automatically success: read that exact ID and verify event ID and canonical payload. A mismatch is a hard integrity failure.
5. **Single-writer serialization:** one active publisher per source/stream is required. A lease/fencing design must prevent two publishers from interleaving IDs. Do not rely on process-local locks.
6. **Retention:** do not apply approximate MAXLEN trimming in this phase. A consumer group may still have undelivered or pending entries. Source outbox floor overtaking publisher checkpoint must stop and require a complete snapshot/rebuild; never jump the cursor silently.
7. **Outage behavior:** Redis failure must not roll back source bar/outbox commits. Publisher retries with bounded backoff and exposes lag/error state without logging credentials or full sensitive connection strings.
8. **Consumer topology:** each gateway/read replica gets an independent consumer group. A shared group would load-balance events and would not broadcast to every gateway.
9. **ACK boundary:** consumers ACK only after local replica transaction returns durable `applied`, `duplicate` or `stale`. Cursor gap, retention expiry, validation error or transaction failure must not be ACKed.
10. **No premature activation:** no app lifespan task, public relay route, or production Redis dependency is enabled until publisher crash tests, consumer reclaim tests, two-process parity and outage/recovery tests pass.

## Implementation sequence

- **62H-1:** publisher checkpoint schema + atomic checkpoint API + source/stream identity binding.
- **62H-2:** deterministic append, duplicate read-back verification, serialized publisher lease/fencing, retention-floor stop.
- **62H-3:** fake-Redis contract tests and real Redis integration tests gated by an explicitly configured test service.
- **62I:** independent consumer groups, apply-before-ACK, pending reclaim, restart/crash recovery.
- **62J:** two independent processes/read models, source-vs-replica cursor and bar parity, outage/recovery matrix.
- **62K:** owner-side Gate 25/36 evidence. This requires owner infrastructure and external WebView evidence; local tests cannot close these gates.

## Validation and cost

No runtime code was changed in 62H-0, so no new executable tests are claimed. The 62G-1 through 62G-3 test suites remain committed but exact-head execution is still unconfirmed. The prior container could not resolve GitHub, so no local clone/test run is represented as successful.

ZERO COST preserved: no new package, paid provider, hosted Redis, deployment, Vercel/Cloudflare action, or Termux step. Existing Redis dependency is reused only when an owner-controlled Redis endpoint is later available.

## Gate and project accounting

- Gate 10: **0/10 closed**; all ten remain OPEN pending owner evidence.
- Stage 1: **75% provisional** (30/40 criteria; 300/400 ticks), unchanged.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; M1–M8 weights remain unapproved.
- This architecture audit awards no Stage ticks and closes no Gate.

## Indicator ledger preservation

No indicator implementation changed in this WebSocket audit. The canonical, complete formula/warm-up/test/visual-gap ledger remains in `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`. Current states remain:

| Indicator | Calculation foundation | First valid output | Remaining visual/lifecycle work | State |
|---|---|---:|---|---|
| SMA20 | Rolling arithmetic mean; fixture-tested | 19 | Overlay, toggle, legend/current value, stale clearing, render tests | 🟨 Foundation |
| EMA20 | SMA-seeded EMA; alpha 2/21; fixture-tested | 19 | Overlay, toggle, legend/current value, stale clearing, render tests | 🟨 Foundation |
| RSI14 | Wilder-smoothed close gains/losses; edge fixtures | 14 | Dedicated 0–100 pane, 30/70 guides, toggle and lifecycle/render tests | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; warm-up fixtures | MACD 25; signal/histogram 33 | Pane, signal line, histogram, zero guide and render tests | 🟨 Foundation |
| Bollinger20,2 | Mean ±2 population standard deviations; fixture-tested | 19 | Three-line overlay, toggle, legend/current values, render tests | 🟨 Foundation |
| Shared indicator hook | Validated backend snapshot only; no demo fallback | Depends on source snapshot | Chart binding, loading/error states, identity/timeframe stale clearing | 🟨 Foundation |
| Footprint | Deterministic educational accumulator; explicitly SIMULATED | Not production order flow | Owner reference + reviewed blueprint + ON-only spaced cluster renderer | 🟨 Gated |
| Heatmap | No implementation verified | — | Reference, blueprint, data contract, calculation, renderer and tests | 🟥 Not implemented |
| Liquidation Maps | No implementation verified | — | Reference, blueprint, data contract, calculation, renderer and tests | 🟥 Not implemented |

**Visual invariants:** Footprint OFF preserves standard candle spacing; only explicit ON switches to spaced candle/cluster layout. Footprint, Heatmap and Liquidation Maps visual implementation remains blocked on the owner's reference images and a reviewed scoped blueprint. Stage 4 visible UI remains parked while Stage 1 is active.

## Next safe action

Proceed to 62H-1 only after the 62G exact-head regression suite is validated. If exact-head CI remains unavailable, repair the evidence path first rather than layering more unverified runtime code on top of the replica foundation.
