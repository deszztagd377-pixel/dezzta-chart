# DEZZTA CHART — Batch 80–86 execution reconciliation

**Audit date:** 25 November 2026 (Asia/Jakarta)  
**Branch:** `phase-2/market-data-foundation`  
**Latest branch HEAD at audit:** `eec98b4f58b0aa74e0bd309196e49ca7a3959bcf`  
**Latest source/test commit with verified CI:** `66d4c6a812d5ce2570345e1108e813b5067f5248`  
**Baseline:** `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`  
**Cost policy:** ZERO COST. `main` untouched. No production deployment or Cloudflare resources changed.

This report reconciles the unified Batch 80–86 plan against the current branch rather than repeating planned work as if it were missing. It deliberately distinguishes source code, automated CI evidence, owner-host evidence, and production acceptance.

## 1. Exact repository and CI state

The branch currently points to `eec98b4f58b0aa74e0bd309196e49ca7a3959bcf`, a documentation-only commit titled `docs(project): record Batch 80 acceptance and indicator status [skip ci]`. Its parent is the source/test commit `66d4c6a812d5ce2570345e1108e813b5067f5248`. Compare against the source/test baseline `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`: 23 commits ahead, 0 behind.

The four workflows were fetched individually and every job was terminal SUCCESS on the exact source/test SHA `66d4c6a812d5ce2570345e1108e813b5067f5248`:

| Workflow | Run | Exact result |
|---|---:|---|
| Automated Tests | [45612188191](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188191) | SUCCESS; backend 1,433 passed, 1 skipped, 6 warnings; 65.77 s |
| CodeQL | [45612188170](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188170) | SUCCESS; Python 8/8 and JavaScript/TypeScript 8/8 |
| Full Git History Secret Audit | [45612188184](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188184) | SUCCESS; 6/6 |
| OCI ARM64 Image Readiness | [45612188277](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188277) | SUCCESS; 7/7 |

The Automated Tests job log was inspected: all 40 job steps were completed successfully. The full backend pytest invocation contains one expected skip at `tests/test_shared_guard_tls_integration.py:22` because that invocation does not receive the dedicated TLS fixture variables. However, the workflow has a separate earlier step that starts an isolated Redis TLS server, injects ephemeral CA/ACL credentials, and directly runs that exact integration test: **1 passed in 0.09s**. That dedicated test verifies CA trust, hostname validation, ACL authentication and shared-guard operations. The workflow also separately completed its Redis ACL/AOF/container smoke path, including an actual Redis container restart and persisted canary verification. The latest documentation HEAD has `[skip ci]` and therefore has no new CI run; CI success is attributed only to the exact source/test SHA above. No workflow/job was left running at this audit.

## 2. Batch 80–86 evidence reconciliation

| Batch | Verified repository evidence | Current honest state |
|---|---|---|
| 80 — strict role binding | Explicit source/gateway role, fail-closed role/factory binding, path validation, tests and env example; exact source CI green | 🟩 **COMPLETE at code/CI scope**. Not production deployment acceptance |
| 81 — source publisher runtime | `build_source_publisher_runtime_factory`, environment factory helper, checkpoint/stream validation, owner snapshot-evidence validator and focused tests exist | 🟨 **COMPONENT FOUNDATION COMPLETE**; production app activation remains blocked on an owner-supplied verifier that authenticates every required gateway's durable installation receipt |
| 82 — gateway replica runtime | `build_gateway_replica_runtime_factory`, authenticated snapshot installation, Ed25519 trusted-key validation, durable receipt/checkpoint comparison and focused tests exist | 🟨 **COMPONENT FOUNDATION COMPLETE**; production app activation remains blocked on the real authenticated snapshot-transfer/install callback and owner-pinned production public keys |
| 83 — multi-gateway/recovery | Real Redis CI tests run two independent ASGI gateway processes, WebSocket broadcast, replay, process restart with durable replica DB, and TCP-path interruption/recovery; dual-replica snapshot-generation test is documented in Batch 62J-31; Redis ACL integration test exists | 🟨 **BROAD AUTOMATED MATRIX PASSED**; existing real-Redis coverage includes callback failure before XACK, ACK reply loss, lease loss after durable apply, pending reclaim, consumer retry ordering, worker recovery, two independent ASGI gateways, WebSocket replay, process restart with persistent replica DB, TCP path interruption, and snapshot-generation replacement. Production host/network, full Redis server/host failure and owner-accepted receipt/retention acceptance remain separate |
| 84 — durable receipt/high-water ACK | Immutable per-generation SQLite snapshot installation receipts, signed Ed25519 manifests, persisted digest/checkpoint binding, source-side receipt field validation and tests exist | 🟧 **RECEIPT FOUNDATION COMPLETE; GATE 25 OPEN**. An owner-accepted, durable per-gateway applied high-water ACK and restart reconciliation across the real gateway inventory are not yet proven |
| 85 — Cloudflare WSS/device E2E | Cloudflare proof is synthetic-only and isolated from production FastAPI/Firebase/market-data path | 🟥 **OPEN**. No verified public production WSS route/origin, owner host mapping, browser/Android end-to-end evidence |
| 86 — recovery/observability/backup | Existing local metrics/incident primitives, Redis AOF restart/container smoke, SQLite integrity checks and recovery-oriented tests exist | 🟧 **LOCAL FOUNDATION EXISTS; OWNER-HOST ACCEPTANCE OPEN**. No verified owner-host backup/restore drill, off-host encrypted backup, production monitoring or incident exercise |

**Important corrections to the original plan:** Batch 83 must not be restarted from zero; significant two-ASGI/Redis TCP and snapshot-generation tests already exist and passed in earlier exact-head CI. Batch 84 must not be described as having no receipt implementation: immutable signed snapshot installation receipts exist. The remaining gap is specifically owner-accepted durable high-water acknowledgement/custody and restart proof. Existing source/gateway factory modules also exist; what is missing is safe owner callback injection and real host integration, not the factory code itself.

## 3. WebSocket critical path — ordered remaining work

1. **Batch 81 owner source verifier:** provide an owner-controlled callback that verifies the authoritative snapshot artifact and retrieves authenticated durable receipts from every required gateway. It must bind source ID, stream key, generation, cursor, SHA-256, gateway ID, replica ID, signer key ID and owner-signature verification state. The existing source validator checks the returned evidence but cannot authenticate remote hosts by itself.
2. **Batch 82 owner gateway installer:** provide an owner-controlled authenticated snapshot transport/installer, persistent replica path, expected source ID, stable gateway consumer identity and pinned Ed25519 public-key map. Gateway startup must install and verify before Redis construction/consumption.
3. **Batch 83 missing fault cases:** extend the existing real Redis/two-ASGI tests only for uncovered cases: Redis server restart while gateway consumers are connected, lease loss/fencing during apply, callback failure before XACK, pending reclaim after process death, Redis stream gap/deleted pending entry forcing resnapshot, and recovery with receipt/cursor parity. Keep tests isolated with ephemeral keys, random stream names and temporary SQLite files.
4. **Batch 84 ACK contract:** distinguish source publisher cursor, replica SQLite applied cursor, Redis XACK, and owner-accepted durable gateway high-water ACK. Only the fourth is the Gate 25 acceptance boundary. Enforce source/gateway/generation identity, monotonic cursor, digest binding, stale-owner fencing and restart reconciliation. No XTRIM/XDEL/XGROUP DESTROY until every required gateway has a current accepted receipt and the minimum safe retention floor is independently proven.
5. **Batch 85 existing Cloudflare route:** identify the existing owner-controlled Cloudflare route/zone/origin and the actual app process topology. Do not invent hostnames, deploy a duplicate Worker, or treat synthetic Worker tests as public WSS acceptance. Then verify Firebase principal, one-time 90-second ticket, 60-second entitlement recheck, Origin allowlist, reconnect/resnapshot and browser/Android lifecycle.
6. **Batch 86 owner-host recovery:** use existing local metrics/incident tools; verify persistent volume, SQLite integrity, Redis TLS/AOF and restart behavior; perform a restore into a separate path and compare source identity, replica identity, generation, digest and cursor. No paid monitoring or backup destination is permitted.

The most useful missing owner-controlled integration fact is the actual snapshot/receipt transport on the existing Cloudflare deployment. Without that, the callbacks cannot be truthfully implemented or public WSS validated. This is a dependency, not permission to invent an endpoint.

## 4. Indicator progress — no implementation credit from WebSocket work

No indicator source, chart UI, or visual renderer changed in Batch 80–86. Indicator progress remains:

| Indicator/subsystem | Calculation/data foundation | Chart UI/integration | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/value and lifecycle not accepted | 🟨 FOUNDATION |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/value and lifecycle not accepted | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides and lifecycle not accepted | 🟨 FOUNDATION |
| MACD12/26/9 | MACD first index 25; signal/histogram first index 33 | Dedicated pane, lines, histogram and zero guide not accepted | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Three overlays, fill, toggle and lifecycle not accepted | 🟨 FOUNDATION |
| Shared Indicator Hook | 7 focused declarations | Not integrated into `CandlestickChart.tsx` | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Stage 4 gated; match both supplied visual references | 🟧 GATED |
| Volume Profile | Full price-bin/value-area behavior not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range selection and deterministic recomputation not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Data provenance/aggregation/decay not accepted | Visual work waits for user reference image | 🟥 OPEN |
| Liquidation Maps | Data provenance, estimation and confidence contract not accepted | Not integrated | 🟥 OPEN |

Focused declarations remain 28 total (21 calculation + 7 shared hook); they are not a pass count or completion percentage. Mathematical acceptance remains: SMA/EMA warm-up index 19; RSI14 index 14; MACD line index 25 and signal/histogram index 33; Bollinger index 19. All outputs must preserve warm-up nulls, prefix causality, no future-candle lookahead/repaint, exact timestamp/series identity alignment, stale-output clearing on identity changes, deterministic repeated results, bounded computation and no calculations for demo/loading/unavailable/error/empty snapshots. Footprint OFF preserves normal candle spacing; explicit ON alone enables spaced clusters. The two saved Footprint references remain authoritative; Heatmap visual work still requires its reference.

## 5. Project progress and gate accounting

- Stage 1: **30/40 = 75% provisional 🟨**; Batch 80 code/CI does not automatically close unrelated Stage 1 criteria.
- Gate 10: **0/10 formally closed 🔴**; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 remain open.
- Stage 2: 🟦 preparatory; not officially entered/scored.
- Stage 3: ⚪ not scored.
- Stage 4: 🟪 gated.
- Stages 5–6: ⚪ not scored.
- Overall project: ⚪ NOT SCORED; approved weighted denominator is absent.
- Significant progress index/IP3S: ⚪ NOT SCORED for the same reason.
- Production WebSocket: 🔴 OPEN until the owner callback/transport, public WSS and host acceptance are proven.
- ZERO COST remains mandatory. No paid data, hosting, monitoring, backup, subscription, publication or duplicate Cloudflare resources.
- Target delivery remains around **24 December 2026**, as a planning target, not a guarantee.

## 6. Execution control

Do not skip or reorder batches. Do not change `main`. Do not invent remote APIs, receipt sources, Cloudflare hostnames, signing keys or credentials. Do not enable a role in production until its matching owner callback and configuration are present. Do not perform destructive Redis retention. The successful CI evidence above applies only to source/test SHA `66d4c6a812d5ce2570345e1108e813b5067f5248`; the latest docs-only HEAD has no CI claim.

**Next executable work:** finish owner callback contracts and test-only fault gaps while retaining the existing successful baseline. No source change is authorized by this reconciliation report alone.


## 7. Connected Cloudflare account visibility check — read-only

A fresh read-only inspection of the Cloudflare account currently connected to this session returned zero Worker scripts, zero Worker custom domains, zero Pages projects, zero Tunnels, zero Durable Object namespaces, zero Queues, zero D1 databases and zero Zones. R2 is not enabled in that connected account. No Cloudflare resource was created, changed or deleted.

This is an account-visibility result only. It does **not** prove that the user's stated production server is absent; it may be hosted in another Cloudflare account, an account not connected here, or an owner-managed origin behind a different route. Batch 85 and owner-host portions of Batch 86 remain blocked until the actual existing production account/zone/route/origin is identified. Do not create a replacement Worker, Pages project, Tunnel, zone, R2 bucket or domain as a workaround.


### Batch 83 test coverage already present (do not duplicate)

The current `backend/tests/test_ohlcv_redis_consumer.py` contains 22 focused test functions. Important real-Redis cases include `test_real_redis_callback_failure_keeps_durable_event_pending_until_retry`, `test_real_redis_callback_is_retried_after_ack_reply_loss`, `test_real_redis_lease_loss_after_apply_prevents_ack`, `test_real_redis_retries_same_consumers_pending_before_reading_new_cursor`, `test_two_independent_processes_broadcast_to_two_durable_gateway_replicas`, `test_two_gateway_processes_switch_snapshot_generation_and_converge_at_next_cursor`, `test_two_asgi_gateways_recover_after_real_redis_tcp_path_interruption`, and `test_two_independent_asgi_processes_broadcast_replica_live_event`. Publisher tests also cover real-Redis deterministic IDs, lost XADD replies, conflicting payloads and read-back uncertainty. The test suite and CI logs were inspected; no need to recreate these cases. Remaining Batch 83 additions must target genuinely uncovered server/host and receipt-reconciliation failure paths.
