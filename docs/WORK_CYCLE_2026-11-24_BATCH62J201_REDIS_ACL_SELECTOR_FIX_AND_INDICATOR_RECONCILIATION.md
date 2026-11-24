# Work Cycle — 24 November 2026 — Batch 62J-201
## Redis 7 ACL selector isolation, exact-head CI closure, and full indicator/progress ledger refresh

Repository: `deszztagd377-pixel/dezzta-chart`  
Branch: `phase-2/market-data-foundation`  
Code/test HEAD: `b71bf86c31fadd2895a2b4f18991b6742847e1a1`  
Official stage: Stage 1 — Foundation, Security & Data Integrity  
ZERO COST: maintained • Protected `main`: untouched • Delivery target: approximately 24 December 2026 (planning target)

## 1. Result

This cycle closes the Redis gateway ACL key-scope gap found in Batch 62J-200, proves the updated policy against the ephemeral Redis 7 CI service, and reconciles the current project/indicator documentation while preserving historical checkpoint sections.

**Exact-head CI: 4/4 terminal SUCCESS.** All four workflow run objects report `head_sha = b71bf86c31fadd2895a2b4f18991b6742847e1a1`, `completed`, `success`.

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests & Build | [#2329](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594594) | 1/1 job, 40/40 steps SUCCESS |
| CodeQL Security Analysis | [#1686](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594526) | Python + JavaScript/TypeScript, 2/2 jobs SUCCESS |
| OCI ARM64 Image Readiness | [#315](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594556) | Native ARM64 build/smoke SUCCESS |
| Full Git History Secret Audit | [#1268](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45321594499) | 1/1 job SUCCESS |

Automated Tests passed frontend unit/build and credential scans, synthetic Cloudflare Worker/workerd and Durable Object proofs, Android host preflight and immutable preview publisher tests, Redis TLS CA/hostname fixture, backend tests, SQLite outbox/metrics benchmarks, backend dependency audit, container build, Redis guard/persistent-volume smoke, container vulnerability scan/report export and frontend dependency audit enforcement. No failed steps were present in the final job summary.

Artifacts: synthetic outbox benchmark `14888466029`; synthetic metrics collector benchmark `14888371233`; container vulnerability reports `14887418305`. No Android APK workflow run was found for this exact HEAD; CI success is not a real-device or release acceptance claim.

## 2. Redis ACL gap and correction

The previous flat gateway allow-list granted `SET`, `EVAL`, `GET`, `PEXPIRE` and `DEL` alongside stream-consumer commands while the gateway user had both stream and lease key patterns. Existing denials for XTRIM/XDEL/XGROUP DESTROY did not prove these lease commands were blocked against the stream key. This was a latent ACL-contract/test-coverage risk, not evidence of live production exposure: the relay remains disabled/unwired pending owner-controlled snapshot transport and dedicated ACL credentials.

Changed paths:
- `backend/app/ohlcv_redis_config.py`
- `backend/tests/test_ohlcv_redis_acl_integration.py`
- `backend/tests/test_ohlcv_redis_config.py`

The root gateway ACL now contains stream-consumer commands only. Lease lifecycle commands are placed in a Redis 7 ACL selector scoped to one exact literal lease key. The helper validates the key and rejects empty, whitespace, glob and selector-delimiter values.

Real Redis integration coverage proves:
1. Gateway may create/consume/ack/reclaim the intended stream group.
2. Gateway SET, DEL, PEXPIRE and EVAL against the stream key are denied.
3. Lease SET NX PX, renewal and token-fenced release remain functional on the lease key.
4. Out-of-scope keys and database switching remain denied.
5. Publisher cannot access the gateway lease key.
6. Publisher/gateway cannot XTRIM or XDEL; gateway cannot XGROUP DESTROY.
7. Existing lease expiry/takeover/fencing/fail-closed tests remain in the backend suite.

No production credentials, relay startup wiring, dependency, provider, deployment, device or billing configuration changed.

## 3. Complete project accounting

| Meter | Verified state | Status |
|---|---:|---|
| Stage 1 | 30/40 criteria • 300/400 ticks • 75% provisional | 🟨 Active |
| Gate 10 | 0/10 formally closed; open 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 | 🟥 Open |
| Stages 2–6 | Not officially opened/scored | 🟦 / ⬜ Parked |
| Overall project | No approved weighted denominator | ⚪ NOT SCORED |
| Aggregate indicator progress | No approved indicator denominator | ⚪ NOT SCORED |

No Stage 1 ticks or Gate 10 closures are awarded by this source/CI work. CI proves repository and ephemeral test-infrastructure behavior, not owner-host/device acceptance.

## 4. Complete technical indicator ledger

| Indicator / layer | Verified calculation foundation | Visible chart state | Status |
|---|---|---|---|
| SMA 20 | 20-close mean; first valid index 19; tests | No overlay/toggle/legend | 🟨 Foundation |
| EMA 20 | SMA-seeded; alpha 2/21; first valid index 19; tests | No overlay/toggle/legend | 🟨 Foundation |
| RSI 14 (Wilder) | Wilder smoothing; first valid index 14; tests | No pane, 0–100 scale, 30/70 guides or toggle | 🟨 Foundation |
| MACD 12/26/9 | MACD index 25; signal/histogram index 33; tests | No dedicated pane/visible histogram/zero guide | 🟨 Foundation |
| Bollinger 20,2 | Mean ± 2 population SD; first valid index 19; tests | No bands/fill/toggle | 🟨 Foundation |
| Shared indicator hook | Identity-bound validated backend snapshot; trust-state suppression | Hook only; not chart-integrated | 🟨 Foundation |
| Footprint | Deterministic synthetic/offline aggregation + fixtures | Wait for owner reference + scoped blueprint; OFF normal candles, ON spaced clusters | 🟧 Gated |
| Heatmap | No implementation verified | Not implemented; wait for owner reference | 🟥 Open |
| Liquidation Maps | No implementation verified | Not implemented; wait for owner reference | 🟥 Open |

Calculation tests establish foundations, not finished visible features. No aggregate indicator percentage is invented. Stage 4 remains parked. Footprint OFF must preserve standard candle spacing; only explicit Footprint ON may use the spaced-cluster layout. Footprint and Heatmap visual implementation must wait for owner reference images and scoped blueprint review.

## 5. WebSocket, relay and retention blockers

Repository foundations remain present for authenticated WebSocket delivery, snapshot/replay recovery, durable SQLite source outbox, per-replica checkpoints, Redis Stream publisher/consumer, generation-scoped groups and lease ownership.

Owner-controlled public WSS/TLS, real Firebase sign-in/revocation and entitlement E2E, Android/browser reconnect/resnapshot, cross-instance proof, owner-host Redis credentials/persistence/recovery, owner-host volume, off-host backup/key custody, metrics/alert escalation and platform-lifetime proof remain open.

SQLite source/outbox retention is bounded at 100,000 events with transactional monotonic floor advancement. Redis Stream retention remains **NOT IMPLEMENTED**. Safe trimming requires authoritative durable gateway inventory, explicit retirement semantics, authenticated snapshot receipt custody, per-gateway floor acknowledgement, PEL reference policy, and crash-safe intent/commit/trim/reconcile tests. Runtime publisher/gateway identities must not receive destructive stream permissions.

## 6. Documentation reconciliation

Updated current sections while preserving historical sections:
- `PROJECT_STATUS.md`
- `docs/PROJECT_PROGRESS.md`
- `docs/PROJECT_MASTER_PROGRESS_2026-11-24.md`
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
- `docs/assets/project-progress-dashboard-current.svg`

ZERO COST remains mandatory. Delivery target remains approximately 24 December 2026, planning target only.
