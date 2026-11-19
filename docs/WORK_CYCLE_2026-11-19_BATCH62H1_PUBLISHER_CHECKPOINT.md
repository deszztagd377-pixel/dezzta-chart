# BATCH 62H-1 — durable Redis publisher checkpoint (19 November 2026)

**Branch:** \`phase-2/market-data-foundation\` • **Parent:** \`26c72f51c20faa3f00a636735778e876ef16eb21\`  
**Scope:** additive SQLite checkpoint schema, source snapshot watermark initialization, single-publisher lease with fencing epoch, and contiguous cursor compare-and-swap. Redis transport calls and startup wiring are intentionally excluded from this batch.  
**Cost:** ZERO COST • no hosted service • no Vercel/Cloudflare deployment • no Termux • \`main\` untouched.

## Implementation

Added \`backend/app/ohlcv_redis_publisher.py\` with \`SQLiteOhlcvPublisherCheckpoint\`.

- Stores one durable publisher row per authoritative \`source_id\` in the same local SQLite database as the source outbox.
- Binds the checkpoint to one unique Redis stream key; a stream cannot silently be reassigned to another source.
- Initializes only from a snapshot cursor that is still within the source outbox retention window and not ahead of its high-water mark.
- Persists \`published_cursor\`, last event ID, deterministic last stream ID, lease owner, lease epoch, lease expiry, update timestamp and schema version.
- Uses \`BEGIN IMMEDIATE\` for initialization, lease acquisition/renewal/release and cursor advancement.
- A live lease excludes another publisher. An expired lease can be acquired by a new owner only with an incremented fencing epoch. A stale owner cannot release or advance the newer owner's lease.
- Cursor advancement is one event at a time: \`next_cursor = expected_cursor + 1\`. A compare-and-swap protects against double advancement.
- Requires the deterministic Redis Stream ID \`<cursor>-0\`.
- The API is explicitly named \`record_confirmed_append\`: its caller must invoke it only after Redis XADD succeeds or after an exact deterministic-ID read-back confirms the existing event. That Redis confirmation is **not implemented in 62H-1**.
- Redis outage cannot roll back source bar/outbox commits because this module does not run inside the source \`apply()\` transaction.
- No publisher is started from application startup; no Redis ACL changes or stream trimming are introduced.

## Regression tests

Added \`backend/tests/test_ohlcv_redis_publisher.py\` for:
1. Source identity, stream binding and snapshot cursor initialization.
2. Rejection when the snapshot cursor has fallen behind the outbox retention floor.
3. Lease exclusion, same-owner renewal, expiry takeover and fencing epoch.
4. One-cursor advancement with deterministic Stream ID and stable event ID.
5. Gap, wrong Stream ID and expired lease rejection.
6. Compare-and-swap protection against double advancement.

The tests use local temporary SQLite only. No paid Redis service or credentials are required.

## Safety boundary and next batch

62H-1 does not yet perform Redis append, duplicate read-back, or publisher worker scheduling. Those belong to 62H-2. Do not wire this class into application startup until deterministic XADD retry and exact duplicate verification pass. Do not add MAXLEN trimming. If source retention overtakes the checkpoint, the publisher must stop and require a fresh snapshot; it must never silently skip.

## Indicator progress ledger — unchanged by WebSocket work

| Indicator | Calculation foundation and first valid output | Remaining visible work | Status |
|---|---|---|---|
| SMA 20 | Rolling arithmetic mean; first index 19; calculation and fixture tests present | Overlay, toggle, legend/current value, stale-series clearing, render tests | 🟨 Foundation |
| EMA 20 | SMA-seeded EMA; alpha = 2/21; first index 19; calculation and fixture tests present | Overlay, toggle, legend/current value, stale-series clearing, render tests | 🟨 Foundation |
| RSI 14 | Wilder-smoothed gains/losses; first index 14; calculation and edge fixtures present | Dedicated 0–100 pane, 30/70 guides, toggle, lifecycle/render tests | 🟨 Foundation |
| MACD 12/26/9 | EMA12−EMA26; MACD first index 25; signal/histogram first index 33; warm-up fixtures present | Pane, signal line, histogram, zero guide, render tests | 🟨 Foundation |
| Bollinger 20,2 | 20-close mean ± 2 population standard deviations; first index 19; fixture present | Upper/middle/lower overlay, toggle, legend/current values, render tests | 🟨 Foundation |
| Shared indicator hook | Validated backend snapshot only; no DEMO fallback | Chart binding, loading/error handling, identity/timeframe stale clearing | 🟨 Foundation |
| Footprint | Deterministic educational accumulator; explicitly SIMULATED, not production order flow | Owner reference image, reviewed blueprint, explicit-ON spaced cluster renderer and tests | 🟨 Gated |
| Heatmap | No implementation verified | Owner reference, reviewed blueprint, data contract, calculation, renderer and tests | 🟥 Not implemented |
| Liquidation Maps | No implementation verified | Owner reference, reviewed blueprint, data contract, calculation, renderer and tests | 🟥 Not implemented |

**Formula and lifecycle contract:** outputs remain aligned to original candle indexes; warm-up slots remain null. Calculation fixtures across 18 timeframe labels do not prove live-provider correctness or visible chart integration. Footprint OFF must preserve normal candle spacing; only explicit ON may switch to the spaced cluster layout. Footprint, Heatmap and Liquidation Maps visual implementation remains blocked on the owner's reference images and reviewed scoped blueprint. Stage 4 visual work stays parked while Stage 1 is active.

## Gate 10 and project accounting

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN pending owner-side evidence.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; M1–M8 weights remain unapproved.
- 62H-1 earns no Stage ticks and closes no owner gate. CI evidence is not owner acceptance.
- Gate 25/36 still need independent owner Redis topology, public WSS, WebView foreground/background and 330-second attribution evidence. Gates 8,20,30,31,34,35,38,39 retain their existing evidence packs.



## CI fixture correction — exact-head run 44537009483

The first 62H-1 backend regression run reported **1,067 passed / 1 failed**. The failure was isolated to the compare-and-swap test fixture, not a production-code defect: it attempted to submit cursor 2 while declaring expected cursor 0. The production method correctly rejected this earlier at its contiguous-cursor invariant, so the test never reached the CAS branch it intended to exercise.

Corrected the fixture to replay the already-confirmed authoritative cursor 1 with stale expected cursor 0 and deterministic Stream ID `1-0`. The event now satisfies source-outbox validation and contiguous cursor validation, allowing the test to specifically assert that the persisted checkpoint at cursor 1 rejects a second advance from stale expected cursor 0. Production implementation is unchanged by this test-only repair. Exact-head CI for the repair is required before the batch is declared green.
