# Batch 62D — deterministic concurrent SQLite snapshot consistency regression

**Parent:** b213824e8cee4402ab0b846feb05a45de98fe415  
**Branch:** phase-2/market-data-foundation  
**Cost:** ZERO COST • no deployment • no Termux • main untouched.

## Why this matters
Batch 62C introduced `SQLiteOhlcvStore.query_snapshot()`, which reads selected bars, total count, outbox high-water and retention floor under one SQLite read transaction. A basic progression test is useful, but it does not prove a concurrent writer cannot commit between the cursor read and bar query and create a mixed snapshot.

## Change
Added a deterministic threaded regression:
1. Insert first bar and outbox event.
2. Snapshot reader starts a read transaction and pauses immediately after reading outbox state.
3. Independent writer commits a second bar and outbox event.
4. Snapshot reader resumes and must return only first bar with cursor/high-water 1.
5. A fresh snapshot must return both bars with cursor/high-water 2.

This validates the cursor is a real snapshot boundary, not merely a high-water value sampled at a different moment.

## Gate disposition
- Gate 36 remains OPEN: snapshot primitive and local transaction test are not a replicated read model, Redis Streams fan-out, entitlement/catalog replication, or public WSS/WebView acceptance.
- Gate 25 remains OPEN: Batch 62B exact-head CI has process-level Redis ticket/lease evidence; owner-managed multi-instance/outage/recovery still missing.
- All 10 gates remain OPEN; no formal closure or Stage 1 ticks awarded.

## Indicator ledger
Complete current ledger: docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and shared hook remain calculation/data foundations. Footprint is SIMULATED and gated on owner reference + reviewed blueprint. Heatmap and Liquidation Maps remain unimplemented. Footprint OFF retains ordinary candles; explicit ON alone switches to spaced clusters. Stage 4 UI remains parked.

## Validation baseline
Batch 62B exact-head CI (7063e1c9708bc3228aedb44153ed4c4461553e28) passed 3/3: 1,045 backend, 236 frontend / 28 files, CodeQL Python+JS/TS, full history secret audit, container build/smoke, Trivy scan and artifact upload. Batch 62C and 62D exact-head CI remain pending.
