# Work cycle — 24 November 2026 — Batch 62J-193: Replay/live handoff interleaving regression

**Branch:** `phase-2/market-data-foundation`  
**Current source/test HEAD:** `d24a124b01e076c9f1969020ce5ac0a13b19d11e`  
**Previous source/test change:** `b361cc9e18c5f152a2284f18b165b7a17700938f`  
**Indicator and combined work ledger:** [Batch 62J-192](WORK_CYCLE_2026-11-24_BATCH62J192_REPLAY_BOUNDARIES_INDICATOR_LEDGER.md)  
**ZERO COST:** no paid services, provider activation, production host, or device operation. `main` remains untouched.

## 1. New regression added

File: `backend/tests/test_ohlcv_stream.py`

Added `test_replay_live_handoff_deduplicates_both_sides_of_fixed_watermark`.

Deterministic sequence:
- Subscription snapshot cursor is 41.
- During replay, live durable cursors 42, 43, and 44 enter the queue.
- The replay result contains the exact-series events through fixed watermark 43 (42 and 43).
- Merge must discard queued 42 and 43 because replay already covers them.
- Cursor 44 must remain exactly once, resequenced to stream sequence 3 after two replay events.
- Snapshot cursor must remain immutable at 41; durable cursor must finish at 44.

Expected assertions include one surviving queued event, cursor 44, event ID `event-44`, sequence 3, no residual duplicate, and preserved snapshot/durable cursor distinction.

This directly tests the replay/live overlap interval rather than only the simpler one-covered/one-live case. It is a test addition; runtime source was not modified because the existing synchronous merge implementation already expresses the required behavior.

## 2. Combined Batch 62J-192 regression additions

The preceding source/test commit `b361cc9e...` added:
- Retention-floor inclusive boundary table (below/equal/above).
- Malformed replica checkpoint matrix (bool-as-int, negative applied cursor, missing floor, floor above watermark, negative floor).
- Exact scan-limit page transition across two contiguous pages.

Together with this batch, the test work adds four test functions and multiple parameterized cases. Exact count and pass/fail status are pending the latest exact-HEAD CI.

## 3. CI discipline

New exact-HEAD runs for `d24a124b...`:
- Automated Tests: [45307072354](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45307072354) — PENDING at report creation.
- CodeQL: [45307072259](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45307072259) — PENDING at report creation.
- OCI ARM64: [45307072261](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45307072261) — PENDING at report creation.
- Full Git History Secret Audit: [45307072291](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45307072291) — IN PROGRESS at report creation.

These are not marked green until GitHub reports success on this exact SHA. Earlier source/test CI was superseded/cancelled when subsequent commits arrived; that cancellation is not a test failure, but it is also not acceptance evidence for the new HEAD.

## 4. Cross-path coverage map

| Concern | Existing/new evidence | Status |
|---|---|---|
| Atomic snapshot + subscriber registration | Existing synchronous no-await boundary test | 🟩 Covered at unit level |
| Replay-before-live ordering and cursor resequencing | Existing replay merge regression + new overlap test | 🟨 Strengthened; exact CI pending |
| Replay cursor below immutable snapshot cursor | Existing rejection test; queue preserved on early rejection | 🟩 Covered at unit level |
| Queue overflow before replay merge | Existing capacity-1 overflow regression; resnapshot required | 🟩 Covered at unit level |
| Exact canonical series isolation | Existing full identity mismatch and multi-subscriber routing tests | 🟩 Covered at unit level |
| Retention floor inclusive semantics | New parameterized regression | 🟨 Added; exact CI pending |
| Malformed checkpoint values | New parameterized regression | 🟨 Added; exact CI pending |
| Exact scan-limit page continuation | New two-page regression | 🟨 Added; exact CI pending |
| Redis trimming between real pages / failover | No real Redis failover acceptance performed here | 🟥 External/runtime acceptance outstanding |
| Real provider + authenticated owner-host WSS | Not exercised | 🟥 External acceptance outstanding |
| Android background/network transition | Not exercised on physical device | 🟥 Device acceptance outstanding |

The 🟩 labels above mean deterministic repository-level test coverage exists; they do not mean production deployment acceptance is complete.

## 5. Project and indicator status

- Stage 1: 30/40 = **75% provisional**; no additional Stage 1 acceptance item closed.
- Stages 2–6: not scored.
- Gate 10: 0/10 formally closed.
- Overall project: **NOT SCORED**; no approved weighted denominator.
- Indicator aggregate: **NOT SCORED**; no approved weighting denominator.
- Indicator implementation statuses and formula/warm-up/acceptance detail: see [Batch 62J-192 indicator ledger](WORK_CYCLE_2026-11-24_BATCH62J192_REPLAY_BOUNDARIES_INDICATOR_LEDGER.md).
- Batch 62J-193 indicator implementation delta: zero.
- Delivery target: 24 December 2026, planning target only.
- ZERO COST maintained.

## 6. Next work

1. Reconcile latest exact-HEAD CI, inspect failing job logs if any, and make only evidence-backed fixes.
2. Add an explicit two-subscriber/two-series replay isolation regression if not already covered by current tests; avoid duplicating existing coverage.
3. Test replay merge rejection when queued cursor ordering is malformed and prove no success path can silently lose data.
4. Continue backend replica/Redis acceptance audit; distinguish local fake-Redis tests from actual Redis TLS/retention/failover evidence.
5. Keep indicator UI implementation gated until scoped blueprint review and the required owner reference images are supplied.

No user-side repair or manual code editing is requested.
