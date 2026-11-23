# WORK CYCLE — Batch 62J-169: Redis Pending Recovery Scan Safety

Date: 23 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent/source HEAD: `9478dbc1d4a75be051f1e7547380c3bfbdaf5281`  
Scope: deterministic consumer recovery regression coverage.

## Finding

The consumer has two important fail-closed recovery branches:
1. `XAUTOCLAIM` may report pending stream IDs that have been deleted from the stream. The consumer must require a fresh snapshot rather than acknowledge or continue from a potentially incomplete history.
2. `XAUTOCLAIM` may return a non-terminal scan cursor with no entries. The consumer must finish scanning pending entries before reading new (`>`) stream events.

These paths existed in the implementation but lacked deterministic unit coverage; existing real-Redis integration tests primarily cover actual pending reclaim and cursor gaps.

## Change

Added a small deterministic Redis fake and two regression tests:
- Deleted pending entry: raises `ReplicaResnapshotRequired`, performs no ACK, does not advance SQLite cursor, and does not read new stream entries.
- Incomplete pending scan: returns `pending_scan`, carries the scan cursor into the next call, and only reads new entries after XAUTOCLAIM returns terminal `0-0`.

No production consumer code changed because the inspected implementation already enforced the intended ordering and fail-closed behavior. This batch adds proof without altering the transport protocol.

## Acceptance boundary

Tests use a deterministic fake Redis client. Real Redis TLS, AOF persistence, XAUTOCLAIM semantics, independent gateway processes, and network-fault recovery remain covered by the separate CI/integration environment. This does not prove production cloud deployment.

## Changed files

1. `backend/tests/test_ohlcv_redis_consumer.py`
2. `docs/WORK_CYCLE_2026-11-23_BATCH62J169_PENDING_RECOVERY.md`
3. `docs/INDICATOR_PROGRESS_LEDGER.md`
4. `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`

## Indicator progress — unchanged

No indicator formula, numeric kernel, hook, chart binding, renderer, UI or indicator-specific test changed. Indicator implementation credit: **0**.

| Indicator | Status | Foundation / remaining acceptance |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19; overlay/toggle/legend/lifecycle remain |
| EMA20 | 🟨 Foundation | SMA seed, alpha 2/21; first valid index 19; overlay/toggle/legend/lifecycle remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; pane, 30/70 guides and lifecycle remain |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; pane/lines/histogram/zero guide remain |
| Bollinger20,2 | 🟨 Foundation | Mean ±2 population SD; first valid index 19; three-line overlay/toggle/value/lifecycle remain |
| Shared Indicator Hook | 🟨 Foundation | Validated aligned backend output; chart binding, stale clearing and settings/legend remain |
| Footprint | 🟧 Prototype only | Synthetic accumulator; user reference, reviewed blueprint and valid bid/ask contract required |
| Heatmap | 🟥 Not implemented | User reference, reviewed blueprint and validated depth/liquidity contract required |
| Liquidation Maps | 🟥 Not implemented | Defensible data provenance/calculation contract and reviewed implementation required |

Invariants: warm-up nulls; exact candle alignment; prefix causality/no future repaint; reject invalid/gapped data; clear stale outputs on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone activates spaced clusters. Aggregate indicator progress remains NOT SCORED without approved weights and denominator.

## Overall project progress

- Stage 1: 30/40 = 75% provisional 🟨.
- Stages 2–6: NOT SCORED / not officially opened ⬜.
- Gate 10: 0/10 external acceptance criteria formally closed 🟥.
- Gate 25: OPEN 🟧 — local digest, receipt-set and pending-recovery safety strengthened; authenticated cross-host receipt/key lifecycle remains.
- Gate 36: OPEN 🟥 — public production WSS, real Firebase, reverse proxy and physical Android WebView acceptance remain.
- Gate 38: OPEN 🟥 — owner-host metrics persistence, backup/retention, alert and recovery acceptance remain.
- Overall project: NOT SCORED; approved stage weights and denominator are unavailable.

ZERO COST. No paid service, deployment, credentials, physical device or publication fee. `main` untouched.
