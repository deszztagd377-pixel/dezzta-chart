# DEZZTA CHART — WORK CYCLE 62J-27
## WebSocket A–E integration reconciliation and indicator evidence
**Date:** 20 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audited exact HEAD:** `5c5205ebc5d6b58b8e177854edb79f93ba9ea118`  
**Cost:** ZERO COST

## Executive result

The approved WebSocket blueprint is no longer wholly pending. The branch already contains the opt-in replica integration and real two-ASGI process acceptance. This cycle audited the current implementation, reconciled stale dashboard statements, and recorded the latest exact-head CI evidence. No runtime code was changed in this documentation cycle.

## Blueprint A–E

| Workstream | Current result | Evidence / boundary |
|---|---|---|
| A. Replica read model | 🟩 Implemented | Atomic replica bars/checkpoint query, atomic hydration snapshot, durable cursor, bounded Redis replay |
| B. FastAPI lifecycle | 🟩 Implemented for opt-in mode | Injected runtime factory, runtime identity validation, Redis group readiness, hydration before worker, managed worker, provider suppression, bounded shutdown |
| C. WebSocket route | 🟩 Implemented for opt-in mode | Source SQLite remains default; replica mode uses replica snapshot/checkpoint and Redis replay; shared auth/entitlement checks retained |
| D. Two ASGI processes | 🟩 CI-verified | Two real Uvicorn/FastAPI processes, independent SQLite replicas, shared Redis 7, identical live cursor delivered to both |
| E. Failure matrix | 🟨 Partially complete | Component-level retry/reclaim/gap/ACK-loss/shutdown and real route reconnect replay covered; full ASGI restart, Redis outage recovery and snapshot-generation replacement still need cross-process acceptance |

### Exact-head CI

All three workflows passed on `5c5205ebc5d6b58b8e177854edb79f93ba9ea118`:

- Automated Tests: run `44686658866` — SUCCESS
- CodeQL Security Analysis: run `44686658770` — SUCCESS
- Full Git History Secret Audit: run `44686658757` — SUCCESS

The latest reconnect test extends the two-ASGI scenario: both replicas first receive live cursor 1; a new client reconnects with cursor 0; the actual route emits replay_started from 0 through 1, the replay event at cursor 1 with `replayed=true`, and replay_complete at cursor 1.

## Engineering invariants confirmed in source

1. Source SQLite remains the default when no replica runtime is injected.
2. Replica mode is explicit and owner-injected; it is not enabled from an environment flag.
3. The provider is not started in replica mode, avoiding a competing local source-ingestion path.
4. Replica snapshot bars and checkpoint cursor are read atomically.
5. Redis consumer-group readiness is checked before the ASGI app accepts traffic.
6. The worker callback is dispatched onto the owning asyncio loop and awaited before Redis ACK.
7. Source SQLite and replica Redis cursor domains are not mixed.
8. Existing authentication, exact-series entitlement checks, connection leases and WebSocket queue controls remain in the shared route.
9. No production snapshot distribution, TLS/ACL secret provisioning or public WSS acceptance is inferred from CI.

## Remaining acceptance work

- Real ASGI process restart and consumer recovery while preserving cursor continuity.
- Redis outage/recovery across two running gateway processes.
- Snapshot-generation replacement followed by a clean consumer-group generation and cursor parity check.
- Owner-provisioned production snapshot artifact distribution and lifecycle.
- Production Redis TLS, least-privilege ACL, credential rotation and target verification.
- Public WSS, browser and Android end-to-end acceptance.
- Operational retention/trim policy, cleanup authorization and recovery runbook.

Do not close Gates 25, 34 or 36 from repository CI alone. Gate closure requires the corresponding owner-side security, infrastructure and client acceptance evidence.

## Indicator progress — full current status

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA 20 | 🟨 | Rolling mean; first valid index 19; calculation fixtures | Chart overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| EMA 20 | 🟨 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| RSI 14 | 🟨 | Wilder smoothing; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend and render tests |
| MACD 12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Dedicated pane, lines, histogram, zero guide, toggle and render tests |
| Bollinger 20,2 | 🟨 | SMA20 ± 2 population standard deviations; first valid index 19 | Band overlay, toggle, current values, stale clearing and render tests |
| Shared Indicator Hook | 🟨 | Validated backend snapshot only; no DEMO fallback | Chart identity/timeframe binding, loading/error UI, stale clearing and isolation tests |
| Footprint | 🟧 | Deterministic educational accumulator; explicitly SIMULATED | User reference image, reviewed blueprint, ON-only spaced cluster layout, bid/ask cells and performance tests |
| Heatmap | 🟥 | No implementation verified | User reference, reviewed blueprint, source contract, calculation, renderer and controls |
| Liquidation Maps | 🟥 | No validated data/calculation contract | Source feasibility, reference/blueprint, calculation, renderer and controls |

Formula/warm-up contracts remain: SMA20 index 19; EMA20 index 19; RSI14 index 14; MACD index 25 and signal/histogram index 33; Bollinger20,2 index 19. Warm-up values remain null and aligned to candle indexes. Footprint OFF preserves normal candle spacing; only explicit ON may activate the spaced cluster layout. Footprint and Heatmap visuals remain gated on the user's reference image(s) and reviewed blueprint.

## Project-level progress

- Stage 1: **30/40 criteria = 300/400 ticks = 75% provisional**.
- Gate 10: **10/10 🟧 ORANGE, 0/10 formally closed** — IDs 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: not scored.
- Overall project percentage: not established; M1–M8 weights are not approved.
- Indicator aggregate percentage: not established; no approved weighted denominator.

## Change and cost record

- Runtime source files changed: none.
- Test source files changed: none in this reconciliation; the reconnect assertion is already present at the audited HEAD.
- Documentation files changed: `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`, `docs/INDICATOR_PROGRESS_LEDGER.md`, and this report.
- Branch `main`: untouched.
- Deployments: none.
- Vercel/Cloudflare: no actions.
- Paid services: none.
- Termux: not required.
