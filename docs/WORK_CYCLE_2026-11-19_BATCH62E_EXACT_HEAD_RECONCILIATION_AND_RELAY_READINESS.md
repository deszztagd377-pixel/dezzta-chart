# Batch 62E — exact-head reconciliation and safe WebSocket relay readiness

**Date:** 19 November 2026 (UTC)
**Branch:** phase-2/market-data-foundation
**Parent/source baseline:** e36240032aec2539e8bb0fec3c037248133648f9
**Scope:** repository audit, architecture decision, progress-ledger/dashboard reconciliation and acceptance planning. Documentation-only; no application source change.
**Cost:** ZERO COST • no Vercel/Cloudflare deployment • no paid service • no Termux • main untouched.

## 1. Exact branch and CI verification

The branch ref was read directly and resolved to e36240032aec2539e8bb0fec3c037248133648f9. Its parent is a documentation-only Batch 62D verification commit; the WebSocket runtime source is unchanged from the preceding tested source baseline.

All three GitHub workflows completed successfully against this exact SHA:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44496224508](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44496224508) | SUCCESS |
| CodeQL Security Analysis | [44496224516](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44496224516) | SUCCESS |
| Full Git History Secret Audit | [44496224538](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44496224538) | SUCCESS |

The automated job reports successful frontend tests/build, backend tests, bounded outbox benchmark, dependency audits, backend container build, Redis/persistent-volume smoke test, image scan/report, and cleanup steps. This report records workflow success only; it does not infer additional test counts or production acceptance absent explicit run evidence.

## 2. WebSocket blocker — source-level confirmation

The backend application factory constructs an OhlcvPipeline, an OhlcvStreamHub, and an SQLiteOhlcvStore for that application process. The ingestion callback publishes persisted bars to that process-local hub. Redis event fan-out by itself therefore cannot give a second process an authoritative initial snapshot.

The SQLite store uses a local file-backed database in WAL mode. Sharing that WAL database between arbitrary hosts is not an accepted replication strategy.

### Decision: do not wire partial fan-out into application startup

The safe zero-cost direction remains one authoritative ingestion writer plus independently maintained local gateway read models:

1. One explicitly identified writer owns canonical ingestion and the durable SQLite outbox.
2. Each gateway receives committed outbox events and applies them idempotently to its own local SQLite read model.
3. Replica application must not re-emit source outbox events.
4. Each replica exposes a snapshot whose bars, applied cursor and retention boundary come from one consistent read transaction.
5. Each gateway uses its own Redis Stream consumer group; a shared group would distribute rather than broadcast events.
6. Consumer acknowledgement occurs only after successful local hand-off; pending entries are reclaimable after process death.
7. A cursor below the source retention floor forces explicit resnapshot/reconciliation. It must never silently jump forward.
8. Authorization, instrument catalog and entitlement state must be synchronized before a replica can serve a client snapshot.
9. Redis outage may delay fan-out but must not roll back committed source bars/outbox events.

### Why no runtime code changed in this batch

The repository confirms the process-local pipeline/hub and local SQLite construction. Writer ownership, replica-apply transaction, entitlement/catalog synchronization, stream ACL contract and resnapshot recovery are not yet implemented as one complete tested data plane. Adding only a Redis publisher or consumer now would create a misleading partial implementation and could serve inconsistent snapshots. No speculative source edit is safer than an untestable half-relay.

## 3. Next bounded implementation sequence

| Batch | Work | Exit evidence |
|---|---|---|
| 62F | Define source-writer ownership and replica schema/identity contract | ADR reviewed against actual config, store and ingestion lifecycle |
| 62G | Implement idempotent replica apply with no source outbox re-emission | Unit tests for duplicate, out-of-order, cursor gap, exact decimals and watermark |
| 62H | Implement Redis Streams relay append/checkpoint and per-instance consumer groups | Retry/crash/pending-reclaim tests with isolated CI Redis |
| 62I | Two independent backend processes with independent local read models | Both instances serve same snapshot watermark and receive every event at application boundary |
| 62J | Failure matrix: relay restart, consumer restart, Redis outage, retention expiry | No silent loss; explicit resnapshot; bounded lag; recovery evidence |
| 62K | Owner-side Gate 25/36 acceptance | Independent owner Redis, public WSS, browser/Android WebView and 330-second attribution |

No deployment is required for 62F–62J. CI Redis is the integration fixture. Do not add Redis Stream ACL permissions until exact key names and commands are fixed and reviewed.

## 4. Gate 10 multi-workstream reduction plan

Formal closure remains 0/10. The next efficient evidence packs are:

- Pack A — Gates 20 + 25: real Firebase token-state matrix, owner Redis ACL/TLS, independent application instances, ticket/lease race and outage/recovery.
- Pack B — Gates 30 + 31 + 34: owner target restore, zero-cost off-host copy, separate key custody, retention, persistent-volume restart and disk-pressure drill.
- Pack C — Gates 8 + 35: protected runtime secret injection/readback, public HTTPS/WSS ingress, certificate chain/renewal and external scan.
- Pack D — Gates 36 + 38 + 39: replicated snapshot-consistent fan-out, durable telemetry/retention, protected dashboard, named operator, escalation and acknowledgement/recovery drill.

CI evidence is supporting evidence only. No owner-controlled acceptance is inferred.

## 5. Indicator and project ledger

The calculation foundations remain: SMA20, EMA20, Wilder RSI14, MACD12/26/9 and Bollinger20,2. They are not visible chart features. The shared indicator hook is groundwork; visible toggles, overlays/panes, legend/current values, stale-series clearing and render/lifecycle tests remain pending under Stage 4.

Footprint remains deterministic SIMULATED data and waits for owner reference images plus a reviewed blueprint. Heatmap and Liquidation Maps remain unimplemented and similarly gated. Footprint OFF must preserve normal candle spacing; only explicit ON may enable the dedicated spaced-cluster layout.

- Stage 1: 75% provisional — 30/40 criteria; 300/400 ticks.
- Gate 10: 0/10 formally closed — all ten remain OPEN.
- Stages 2–6: NOT SCORED.
- Overall project percentage: NOT ESTABLISHED; M1–M8 weights are not approved.
- No progress ticks are awarded for this documentation/audit batch.

## 6. Safety, cost and release controls

No application source changed. No deploy, production promotion, paid resource, billing change, Termux command or main modification was performed. Keep the existing WebSocket lifecycle state machine unchanged unless a reproducible source-level defect is found. Any future source change must be followed by exact-head CI before it is reported as validated.