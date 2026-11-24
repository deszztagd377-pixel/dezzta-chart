# Work Cycle — 24 November 2026 — Batch 62J-200
## Redis ACL key-scope audit, exact-head CI verification, and project indicator reconciliation

Repository: deszztagd377-pixel/dezzta-chart  
Branch: phase-2/market-data-foundation  
Audited documentation HEAD: 24f3ba5dd94b18ae5558b8dabd0a3d1b9c264473  
Latest source/test HEAD: 23bf2da93ec8b4c935d2898a993f4d1c80ce9a7d  
Official stage: Stage 1 — Foundation, Security & Data Integrity  
ZERO COST: maintained  
Protected main: untouched  
Delivery target: approximately 24 December 2026, planning target only

## 1. Scope and disposition

This cycle verifies the current branch HEAD and all configured workflow runs, then performs a source-level Redis ACL key-scope review beyond the destructive-command checks added in Batch 62J-199.

No runtime source, test, dependency, ACL credential, provider, deployment, device, or configuration was changed in this audit. The exact-head CI is green, but the ACL review found an additional privilege-boundary gap that must be addressed before the Redis relay ACL contract is accepted for owner-host use.

## 2. Exact branch HEAD and CI

The branch reference resolves to 24f3ba5dd94b18ae5558b8dabd0a3d1b9c264473. Its commit message is “docs: refresh current project and indicator progress ledgers”. This documentation-only commit changes the indicator progress ledger and current indicator progress document. The latest source/test checkpoint remains 23bf2da93ec8b4c935d2898a993f4d1c80ce9a7d.

All four workflow runs below have a head_sha that exactly matches the current branch HEAD and reached completed / success:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests #2326 | https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45315461372 | SUCCESS — 1/1 job, 40/40 steps |
| CodeQL #1683 | https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45315461472 | SUCCESS — Python and JavaScript/TypeScript, 2/2 jobs |
| Full Git History Secret Audit #1265 | https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45315461471 | SUCCESS — 1/1 job, 6/6 steps |
| OCI ARM64 Image Readiness #312 | https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45315461449 | SUCCESS — native ARM64 build/smoke, 1/1 job, 7/7 steps |

The Automated Tests job completed frontend dependency audit, synthetic Cloudflare Worker/workerd proof, Durable Object hibernation/alarms/isolation tests, frontend unit tests/build and bundle-secret scan, Android host preflight and immutable preview-publisher tests, Redis TLS CA/hostname fixture, backend tests, SQLite outbox and metrics benchmarks, backend dependency audit, container build, Redis guard/persistent-volume smoke, vulnerability scan/report export and frontend audit enforcement. No failed or skipped steps were reported in the latest job summary.

No workflow for the current HEAD is queued or in progress. The previous source/test HEAD has separate exact-head evidence in Batch 62J-199; it is not conflated with this documentation HEAD.

## 3. Source/test evidence carried forward from Batch 62J-199

On source/test HEAD 23bf2da93ec8b4c935d2898a993f4d1c80ce9a7d:
- Backend pytest: 1,359 passed, 1 skipped, 6 non-failing warnings.
- Frontend: 320 passed across 34 test files.
- Real ephemeral Redis ACL integration: publisher XTRIM/XDEL denied; gateway XTRIM/XDEL/XGROUP DESTROY denied.
- Dedicated Redis TLS CA/hostname fixture passed.
- Frontend npm audit reported 0 vulnerabilities; backend pip-audit reported no known vulnerabilities.
- Synthetic Durable Object runtime proof: 11 tests passed.
- Backend container build/smoke, Redis ACL/AOF restart, unprivileged runtime, persistent-volume, SQLite integrity/restart and HTTP rate-limit checks passed.
- Trivy image scan/report export completed. This is CI artifact evidence, not owner-host security certification.

## 4. NEW FINDING — gateway ACL commands are not isolated from the stream key

Inspected:
- backend/app/ohlcv_redis_config.py
- backend/app/ohlcv_redis_lease.py
- backend/app/ohlcv_redis_consumer.py
- backend/tests/test_ohlcv_redis_acl_integration.py
- backend/tests/test_ohlcv_redis_config.py

The gateway command allow-list currently includes:
- +set
- +eval
- +get
- +pexpire
- +del

The integration test creates the gateway ACL user with both the stream key pattern and the lease key pattern, then grants the above commands to that user. Those command permissions are not individually restricted to the lease key by the current flat command allow-list.

Consequently, the test's current negative cases for XTRIM, XDEL and XGROUP DESTROY do not prove that the gateway cannot:
- SET the stream key, potentially replacing the Redis Stream key with a string;
- DEL the stream key, deleting replay history;
- PEXPIRE the stream key, causing it to disappear after expiry;
- invoke EVAL against an allowed stream key, subject to Redis ACL script/key enforcement.

This is a latent ACL-contract and test-coverage risk, not evidence of an active production exposure: the relay configuration explicitly remains disabled/unwired until owner-controlled snapshot transport and ACL credentials are ready. Nevertheless, the current gateway ACL contract must not be described as fully least-privilege until this key/command interaction is closed.

The lease implementation uses SET NX PX for acquisition and token-checked Lua scripts for renewal, ownership checks and release. The release script calls DEL; simply removing DEL without replacing the lease-release design would break the current lifecycle. A safe correction must preserve lease correctness while preventing lease commands from being applied to the stream key.

## 5. Required remediation design and acceptance tests

Do not broaden permissions or change the stream key policy as a shortcut. Before enabling the relay with owner credentials, choose and prove one of these security shapes:

A. Redis 7 ACL command selectors that isolate stream-consumer commands from lease-key commands, with real Redis 7 integration tests proving key-scoped command denial; or

B. Separate Redis ACL identities/credentials and clients for stream consumption versus lease lifecycle, with the lease identity restricted to lease keys only.

The selected approach must be verified against the exact Redis 7.x version used by the project. Required real-Redis negative and positive tests:
1. Gateway may perform intended group/read/ack operations on the stream key.
2. Gateway SET, DEL and PEXPIRE against the stream key are denied.
3. Gateway lease SET NX PX, GET, renewal and token-checked release remain functional only on the lease key.
4. EVAL cannot mutate, delete or expire the stream key.
5. Publisher cannot access gateway lease keys.
6. Both identities remain unable to execute XTRIM/XDEL/XGROUP DESTROY.
7. Out-of-scope keys and database switching remain denied.
8. Lease takeover, expiry, Redis restart and concurrent gateway ownership regressions remain fail-closed.

No production ACL credentials or deployed Redis instance are available in this repository audit. Do not claim owner-host acceptance from ephemeral CI tests.

## 6. Redis retention remains a separate open blocker

SQLite source/outbox retention is implemented with a 100,000-event window and transactional monotonic floor advancement. Redis Stream retention remains not implemented. Publisher/gateway destructive permissions must remain denied.

A separate retention controller is unsafe until the owner-controlled durable gateway inventory, explicit retirement semantics, authenticated snapshot receipt custody, per-gateway floor acknowledgement, Redis 7.x PEL reference policy, crash-safe intent/commit/trim/reconcile protocol and real integration tests are defined.

Do not add XTRIM to the publisher or gateway. Do not implement guessed gateway retirement based on last-seen time.

## 7. Complete project progress and indicator ledger

| Meter | Verified state | Status |
|---|---:|---|
| Official stage | Stage 1 of 6 | 🟨 Active |
| Stage 1 | 30/40 criteria; 300/400 ticks; 75% provisional | 🟨 |
| Gate 10 | 0/10 formally closed | 🟥 |
| Open Gate 10 criteria | 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 | 🟥 |
| Stages 2–6 | Not scored / not officially opened | ⬜ |
| Overall project | NOT SCORED | ⚪ |
| Aggregate indicator progress | NOT SCORED | ⚪ |
| Exact-head CI | 4/4 terminal success | 🟩 |

Indicator implementation status:

| Indicator | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value, identity invalidation, lifecycle, rendering/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity invalidation, lifecycle, rendering/performance |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change average and Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle and latest values |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity invalidation and lifecycle |
| Shared useMarketIndicators hook | 🟨 Foundation | Identity-bound validated backend snapshot, aligned calculations, trust-state suppression and revision cache | Chart binding, stale clearing, settings, legend, accessibility and performance |
| Footprint | 🟧 Synthetic prototype | Educational synthetic accumulator only; not exchange-native bid/ask truth | Owner reference image, reviewed blueprint, valid bid/ask source contract, dedicated spaced-cluster renderer |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | Owner reference, validated depth contract, reviewed blueprint, renderer/tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/calculation renderer | Defensible provenance/methodology, reviewed blueprint, renderer/tests |

Mandatory indicator invariants: warm-up values remain null; exact source-candle alignment; prefix causality/no future repaint; reject invalid/non-finite/gapped input; clear stale output on identity/timeframe changes. Footprint OFF preserves ordinary candle spacing; explicit ON alone enables the dedicated spaced-cluster layout. Footprint and Heatmap visuals remain blocked pending owner reference images and reviewed scoped blueprints. No aggregate indicator percentage is invented.

## 8. Next engineering sequence

1. Close the gateway ACL key-scope risk with a reviewed selector or split-identity design and real Redis 7.x tests before relay activation.
2. Preserve the current exact-head CI and re-run all relevant workflows after any authorized code change.
3. Continue the durable gateway inventory and Redis retention design without implementing trim until owner lifecycle semantics are defined.
4. Continue source-level owner-host acceptance mapping for WSS, Firebase, Redis persistence, backup/restore, metrics/alerts and Android lifecycle.
5. Keep visible indicator UI parked until official Stage 4; keep Footprint/Heatmap reference-gated.
6. Preserve Stage 1 at 30/40 until external acceptance evidence closes a criterion.

## 9. Change and cost boundary

This cycle is a read-only engineering audit and documentation report. No runtime source or tests changed, no dependency was installed, no provider or deployment was activated, no billing was enabled, and no device/Termux operation was performed. No paid service or incremental spend was introduced. Protected main was not modified.

Disposition: exact-head CI is green, but the gateway ACL key-scope risk is now a red engineering blocker for future relay activation. Stage 1 remains 75% provisional; Gate 10 remains 0/10 closed; overall and indicator aggregate progress remain not scored.
