# Batch 62C — atomic SQLite snapshot/watermark and Redis ticket race hardening

**Parent:** 7063e1c9708bc3228aedb44153ed4c4461553e28  
**Branch:** phase-2/market-data-foundation  
**Cost:** ZERO COST • no deploy • no Termux • main untouched.

## Changes
1. Added `SQLiteOhlcvStore.query_snapshot()`. It reads exact filtered bars, total count, global outbox high-water and retention floor inside one SQLite read transaction.
2. The method follows the existing write invariant: accepted bar revision, outbox event and high-water state are committed atomically by `apply()`. A snapshot therefore has a stable replay cursor.
3. Added tests verifying snapshot content and cursor progression across commits, plus invalid page limit rejection.
4. Tightened Batch 62B cross-process Redis test: only the process that successfully consumes the single-use ticket may attempt the authenticated per-account lease. This ensures the ticket winner and lease winner are the same process.
5. Updated the cross-instance ADR, full indicator ledger, dashboard and this work-cycle report.

## Important integration boundary
The live WebSocket route is not switched to the new method yet. It still uses the event-loop-confined in-memory pipeline/hub for its atomic local snapshot hand-off. The new method is a tested durable storage primitive for future replica/gateway snapshots, not a claim that multi-instance fan-out is complete. Instrument registry, entitlements, session calendar and historical snapshot availability also require a defined replication/authority contract.

## Gate 10
All 10 gates remain OPEN. Gate 25 has CI-level cross-process ticket/lease coverage but still needs owner-managed Redis, independent deployed instances and outage/recovery evidence. Gate 36 remains OPEN until authoritative source + replica read models, entitlement/catalog consistency, stream fan-out, public WSS, browser/Android WebView and 330-second attribution are proven. No gate closure or Stage 1 ticks awarded.

## Indicator status
Full detailed ledger: docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and shared hook are calculation/data foundations, not completed visible indicators. Footprint is SIMULATED and gated on owner reference + reviewed blueprint. Heatmap and Liquidation Maps are unimplemented. Footprint OFF preserves ordinary candles; explicit ON alone switches to spaced clusters. Stage 4 UI remains parked while Stage 1 active.

## Batch 62B exact-head CI observation
- CodeQL run 44494114971: SUCCESS, Python + JavaScript/TypeScript.
- Full Git History Secret Audit run 44494115057: SUCCESS.
- Automated Tests run 44494115133: still IN PROGRESS at last observation; frontend tests/build, backend pytest, outbox benchmark, dependency audit had succeeded; backend container build was the active step. Do not call this 3/3 complete until all remaining container validation and cleanup steps succeed.
