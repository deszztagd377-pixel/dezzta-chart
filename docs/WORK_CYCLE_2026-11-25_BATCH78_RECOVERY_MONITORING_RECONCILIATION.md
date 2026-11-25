# DEZZTA CHART — Work Cycle 78: Recovery, monitoring, and five-batch reconciliation
Date: 25 November 2026
Branch: `phase-2/market-data-foundation`
Documentation parent HEAD: `fb4fb9843535b0dae1cc733d65df9de653dd88ba`
Last runtime/source-tested SHA: `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`
Scope: reconcile Batches 74–77, complete the Batch 78 recovery/monitoring audit, and update project/indicator ledgers without inventing production evidence.
Runtime/source changes: none. No Cloudflare resources, secrets, host settings, or production endpoints were created or changed.
Cost: ZERO COST.

## 1. Branch and source integrity

The active branch exists: `phase-2/market-data-foundation`.
Current documentation HEAD before this report: `fb4fb9843535b0dae1cc733d65df9de653dd88ba`.
The branch is one documentation-only commit ahead of the last source/test commit `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`. The latest commit message is `docs(ci): record Batch 76 closure [skip ci]`.
No source/runtime diff exists between the last source/test SHA and the documentation HEAD. `main` is not touched.

The Batch 77 record reports four exact-source CI workflows terminal SUCCESS on `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`:
- Automated Tests run 45604020771 — 41/41 steps.
- CodeQL run 45604020613 — Python 8/8 and JavaScript/TypeScript 8/8.
- OCI ARM64 run 45604020280 — 7/7.
- Full Git History Secret Audit run 45604020286 — 6/6.
Automated suite: 1,426 passed, 1 skipped, 6 warnings in 57.78s. Dedicated Redis TLS integration: 1 passed in 0.08s.
These are the exact-source results recorded by Batch 77. The documentation-only HEAD has no new runtime code and is intentionally marked `[skip ci]`; no claim is made that a new CI run was started or left running for this documentation commit.

## 2. Batches 74–77 reconciliation

The requested batches already exist and are not repeated:
- Batch 74: `docs/WORK_CYCLE_2026-11-25_BATCH74_CI_TLS_PROOF_CLOSURE.md` — Batch 73 CI closure; dedicated Redis TLS proof clarified.
- Batch 75: `docs/WORK_CYCLE_2026-11-25_BATCH75_BATCH74_CI_CLOSURE.md` — exact-head CI closure.
- Batch 76: `docs/WORK_CYCLE_2026-11-25_BATCH76_BATCH75_CI_CLOSURE.md` — exact-head CI closure.
- Batch 77: `docs/WORK_CYCLE_2026-11-25_BATCH77_FINAL_CI_HANDOFF.md` — Batch 76 CI closure and final handoff.
All four workflows are recorded SUCCESS on their respective audited source SHAs. The dedicated TLS fixture proves certificate/hostname validation, ACL-backed Redis operations, rejection of wrong CA/hostname/plaintext downgrade, and AOF data surviving a real Redis container restart. It is isolated CI evidence, not owner-host acceptance.

## 3. Batch 78 — recovery and monitoring audit

### Verified recovery capabilities (CI/container scope only)
- Backend container health and health JSON.
- Redis ACL authentication and AOF persistence across container restart.
- Fail-closed API behavior during Redis outage and backend reconnection.
- Non-root UID/GID execution.
- Mounted-volume ownership smoke checks.
- SQLite integrity and restart persistence.
- HTTP rate-limit rejection.
- Dedicated Redis TLS listener and ACL remain active after Redis restart.
- Synthetic SQLite outbox and metrics collector benchmarks.
- Synthetic Cloudflare Worker/Durable Object proof tests, including hibernation/alarm/per-series isolation as covered by the CI workflow.

### Production recovery/observability acceptance still OPEN
1. Owner-host secret injection, rotation, ownership/mode, and log-exposure proof (Stage 1 criterion 8).
2. Actual application DB restore to a fresh owner-controlled destination (criterion 30).
3. Encrypted off-host backup, separate key custody and key-recovery restore (criterion 31).
4. Actual owner-host persistent-volume mount, permissions, disk-pressure and restart durability (criterion 34).
5. Owner-host backend runtime, startup and health evidence (criterion 35).
6. Durable metrics retention and a real independent alert route with acknowledgement/recovery drill (criteria 38 and 39).
7. Public HTTPS/WSS through the actual Cloudflare-controlled route, with browser and Android reconnect/resnapshot/cross-instance E2E (criterion 36).

CI container smoke tests cannot close these owner-host or real-device acceptance criteria. No external backup destination, key custodian, owner host, real browser/device, or production Cloudflare route was available in this work cycle. Therefore no production recovery drill or alert acknowledgement is claimed.

### Monitoring contract for the next implementation review
The following metric families are required before production observability acceptance:
- WebSocket: active connections by gateway/series, handshake rejects by reason, auth/ticket expiry, reconnects, close codes, ping/pong timeout, outbound queue depth, send failures and snapshot/resnapshot count.
- Snapshot/receipt: source sequence, installed sequence, receipt verification failures, receipt age, per-gateway durable high-water ACK, stale-owner/fencing rejects, restart reconciliation duration and missing-ACK age.
- Redis: connection/TLS/auth failures, command latency, AOF last-write/health, memory, evictions, persistence/restart recovery, pending-entry-list depth/age and consumer lag.
- Provider: upstream connection state, subscribe/unsubscribe demand, active symbol count, provider lag, data age, sequence gaps, rate-limit responses and provenance/entitlement rejection.
- Backend/host: request latency/error rate, health transitions, process restarts, CPU/memory/disk, persistent-volume capacity and backup/restore outcomes.
- Alert evidence: threshold, owner, local no-cost delivery route, acknowledgement timestamp, incident record and recovery verification.

Metrics must avoid credentials, bearer tokens, private keys, full user identifiers and raw sensitive payloads. Alerting must remain no-cost and owner-controlled. Metrics definitions alone do not count as an operationally accepted dashboard or alert drill.

## 4. WebSocket and Project Gate 25 — final blocker state

The Cloudflare Worker/SQLite Durable Object code remains a synthetic-only proof. It is not a deployed production WSS service and is not wired to the production FastAPI entrypoint, Firebase identity/entitlement, live provider, production ticket issuance or UI.

The source/gateway production composition still lacks proven owner-controlled callback wiring in the default application entrypoint. The following remain OPEN:
- Firebase identity and entitlement verification.
- Production single-use ticket issuance, expiry and revocation.
- Lawful zero-cost provider access and source provenance.
- Authenticated source-to-gateway signed snapshot transfer.
- Authenticated persisted receipt retrieval after restart and re-verification.
- Durable per-gateway high-water ACK ledger, fencing and stale-owner rejection.
- Restart reconciliation and missing-ACK recovery.
- Public HTTPS/WSS through the real Cloudflare route and browser/Android lifecycle E2E.

Redis `XACK` and a local `applied_cursor` are not the owner-accepted durable high-water ACK. Redis `XTRIM`, `XDEL` and consumer-group destruction remain BLOCKED until every gateway's durable receipt/ACK is accepted and restart reconciliation is proven.

The connected Cloudflare account inventory previously returned no Worker scripts, Pages projects, Tunnels, Durable Object namespaces, Queues, D1 databases, KV namespaces, Worker domains or Zones. The user has separately stated the project server is on Cloudflare; this account inventory therefore cannot be treated as proof that no other Cloudflare account/project exists. Do not deploy into the connected account or invent a production hostname/Worker binding based on an empty inventory. The synthetic proof must remain isolated.

## 5. Stage and progress accounting

- Official active stage: Stage 1 — Foundation, Security & Data Integrity.
- Stage 1: 30/40 = 75% provisional 🟨.
- Gate 10: 0/10 formally closed 🟥; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 remain acceptance items.
- Stage 2: 🟦 PREPARATORY only; branch name is not a stage transition.
- Stage 3: ⚪ NOT SCORED.
- Stage 4: 🟪 GATED.
- Stages 5–6: ⚪ NOT SCORED.
- Overall project, aggregate indicator completion and IP3S: ⚪ NOT SCORED; no approved weighted denominator/formula.
- No Stage 1 acceptance credit is awarded for documentation or synthetic CI alone.

### Complete indicator inventory

| Indicator/subsystem | Calculation/data foundation | Rendering/interaction/lifecycle | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay/toggle/legend/lifecycle absent | 🟨 FOUNDATION |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay/toggle/legend/lifecycle absent | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed + Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides and lifecycle absent | 🟨 FOUNDATION |
| MACD12/26/9 | MACD index 25; signal/histogram index 33 | Pane, lines, histogram and zero guide absent | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Bands, fill, legend and lifecycle absent | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed immutable snapshot/cache/trust gate; 7 focused declarations | Not integrated into `CandlestickChart.tsx` | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Stage 4 gated; two supplied references remain authoritative | 🟧 GATED |
| Volume Profile | Binning/value-area behavior not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range selection/recalculation lifecycle not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Lawful depth source, aggregation and decay not accepted | Not integrated; reference gate remains | 🟥 OPEN |
| Liquidation Maps | Provenance, estimation methodology and confidence limits not accepted | Not integrated | 🟥 OPEN |

Focused declarations remain 28 = 21 calculation + 7 shared-hook. This is not a pass count or completion percentage. No indicator source/UI changed in Batches 74–78; indicator completion credit is zero. Mathematical invariants remain warm-up nulls, prefix causality, no future-candle lookahead/repaint, exact timestamp/canonical series alignment, stale-output clearing on identity change, and no calculations for demo/loading/unavailable/error/empty snapshots. Footprint OFF preserves normal candle spacing; explicit ON alone enables spaced clusters. Heatmap visual work remains reference-gated.

## 6. Final status and next work order

Batch 78 documentation/reconciliation is complete. Batches 74–77 are already documented and reconciled. The five-batch documentation/CI-closure campaign is therefore complete, but production WebSocket/Gate 25 and external Stage 1 acceptance are NOT complete.

Next engineering order:
1. Reconcile the user's Cloudflare-hosted project with the connected Cloudflare account without creating duplicate resources.
2. Inspect the actual production Worker/route and owner-controlled origin before selecting the Worker-native or Tunnel composition.
3. Review the production transport/identity contract before runtime wiring.
4. Implement and test authenticated single-use tickets and Firebase identity/entitlement.
5. Implement signed snapshot transfer, persisted receipt retrieval and durable per-gateway high-water ACK/fencing/restart reconciliation.
6. Prove provider adapter subscribe/unsubscribe, legal data rights and source provenance at zero cost.
7. Complete public WSS/TLS browser and Android E2E.
8. Complete owner-host backup/restore, secret, volume, metrics and incident acceptance.
9. Keep Redis destructive retention blocked until durable ACK acceptance.
10. Keep indicator UI behind Stage 4 scoped blueprint and user review.

Controls: ZERO COST; `main` untouched; Vercel deferred; no paid data/hosting/monitoring/backup; no production deployment or Cloudflare resource changes in this cycle. Planning target remains around 24 December 2026.
