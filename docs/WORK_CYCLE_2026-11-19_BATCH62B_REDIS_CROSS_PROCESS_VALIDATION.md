# Batch 62B — Redis cross-process guard validation and fan-out topology blocker

**Parent:** 97880bda671231a803d1abb06865fc849c16d686  
**Branch:** phase-2/market-data-foundation  
**Cost:** ZERO COST • CI Redis only • no deploy • no Termux • main untouched.

## Changes
1. Added a Redis integration test spawning two independent Python backend processes with separate Redis clients.
2. Both processes race to consume one single-use WebSocket ticket and acquire one account-scoped connection lease.
3. Acceptance requires exactly one ticket consumer and exactly one lease winner; the winner's lease is released during cleanup.
4. Updated the cross-instance ADR: Redis fan-out alone is insufficient because each process has local SQLite/WAL, pipeline, registry and hub. A receiving gateway also needs a consistent initial snapshot.
5. Updated the current complete indicator ledger and color dashboard with verified Batch 62A exact-head CI results.

## Architecture blocker resolved safely
No partial Redis Stream relay is wired into application startup. A correct data plane needs an explicit authoritative ingestion owner/source identity, snapshot-consistent local replica read models or a separately specified authenticated snapshot API, idempotent replica apply without re-emitting source outbox events, cursor/watermark consistency, entitlement consistency, and explicit recovery when source retention is exceeded.

Preferred zero-cost path: authoritative SQLite writer + Redis Streams + per-instance local read models. Not yet implemented. Existing Redis ACL remains narrow; no speculative Stream permissions were added.

## Gate 10
- Gate 25 remains OPEN. New process-level CI evidence counts only if exact-head CI passes; owner-managed Redis, independent deployment, outage/recovery and acknowledgement remain required.
- Gate 36 remains OPEN. Public authenticated WSS, browser/Android WebView, 330-second attribution and snapshot-consistent fan-out remain unproven.
- Gates 8, 20, 30, 31, 34, 35, 38 and 39 remain OPEN.
- No production gate closure or Stage 1 ticks awarded.

## Indicator ledger
Full current ledger: docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and shared hook remain calculation/data foundations; visible UI parked until Stage 4. Footprint is SIMULATED and gated on owner reference + reviewed blueprint. Heatmap and Liquidation Maps unimplemented. Footprint OFF preserves normal candles; explicit ON alone enables spaced clusters.

## Exact-head baseline
Batch 62A HEAD 97880bda671231a803d1abb06865fc849c16d686:
- Automated Tests run 44487591377: 1,044 backend, 236 frontend tests / 28 files, build, benchmark, audits and container smoke succeeded.
- CodeQL run 44487591390: JavaScript/TypeScript and Python succeeded.
- Full Git History Secret Audit run 44487591396: succeeded.

Batch 62B exact-head CI is pending; the new process test is not yet claimed as passed.
