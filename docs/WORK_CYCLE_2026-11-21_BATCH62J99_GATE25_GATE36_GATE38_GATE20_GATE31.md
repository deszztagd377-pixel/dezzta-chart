# DEZZTA CHART — Work Cycle 62J-99
## Three-workstream repository audit: Gate 25/36, Gate 38, Gate 20/31

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audit baseline:** `ae1ff4ada7977239b6970cd5bef02335ece29f08`  
**Main branch:** unchanged  
**Cost:** ZERO COST; no deployment, hosted monitoring, paid storage, Termux or device action.

## Executive disposition

This cycle executes the next three repository workstreams in parallel at the source/evidence layer. It does not claim external host acceptance.

| Workstream | Repository-side result | External blocker | Gate disposition |
|---|---|---|---|
| 1. Gate 25 + 36 | Gateway factory, snapshot install contract, Redis TLS guard, HTTPS/WSS ticket/client guards and existing exact-head tests audited | Owner-host Redis TLS/ACL, actual gateway snapshot installer/receipts, public HTTPS/WSS reverse proxy, browser + Android WebView | 🟧 |
| 2. Gate 38 | Bounded 899-series same-host collector, SQLite WAL, 15-minute buckets, 7-day retention, row cap, token-gated scrape, disk-full/read-only/corruption/isolation tests and benchmark artifacts audited | Actual persistent volume, operator access perimeter, retention/backup on host, dashboard, independent no-cost notification and operator drill | 🟧 |
| 3. Gate 20 + 31 | Firebase Admin identity verification/revocation, per-account deny-by-default entitlements, scoped ticket flow, AES-256-GCM encrypted backup and fresh-path restore tests audited | Real signed Firebase token E2E and owner-host independent off-host backup/key-recovery restore | 🟧 |

No production credential, endpoint, device state, host or operator acceptance is invented.

## 1. Gate 25 and Gate 36 — integration boundary

Audited source:
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/ohlcv_redis_runtime.py`
- `backend/app/ohlcv_redis_config.py`
- `backend/app/ohlcv_redis_consumer.py`
- `src/services/ohlcvWebSocketTicket.ts`
- `src/services/ohlcvWebSocketClient.ts`

Gateway startup remains opt-in. The owner-provided snapshot installer is the trust boundary; the runtime checks installed checkpoint identity, generation and cursor before Redis client construction. Production Redis is TLS-only with certificate and hostname verification. The source publisher and gateway use separate ACL identities; the Redis 7 integration contract restricts publisher and consumer commands/keys. The browser client rejects plaintext production WebSocket transport and uses HTTPS ticket exchange followed by WSS.

No code-level defect was established in this audit. A repository-only change cannot manufacture the real snapshot transfer, ACL secret injection, TLS endpoint, reverse-proxy route or Android runtime evidence. Gate 25 and 36 therefore remain 🟧. Do not promote them to host-verification-only until their respective live host tests pass.

## 2. Gate 38 — telemetry, storage and failure isolation

Audited source:
- `backend/app/observability.py`
- `backend/app/metrics_collector.py`
- `backend/app/main.py`
- `backend/tests/test_metrics_collector.py`
- `backend/tests/test_metrics_collector_benchmark.py`
- `docs/GATE38_METRICS_COLLECTOR_BLUEPRINT.md`
- `docs/GATE38_MONITORING_ACCEPTANCE_RUNBOOK.md`

Verified design limits:
- 899 logical series = 762 HTTP request + 127 latency histogram + 10 WebSocket.
- Hard series limit 900.
- 15-minute aggregation buckets and 7-day retention: 672 buckets.
- Theoretical full-cardinality row count: 899 × 672 = 604,128.
- Hard aggregate-row cap: 650,000; remaining headroom: 45,872 rows (7.06%).
- Maximum 16 live workers; 256 worker generations; stale after 90 seconds.
- Snapshot payload cap 256 KiB; 1 MiB is not used as a per-request payload target.
- Storage is same-host shared local volume only; multi-host SQLite is unsupported.

Failure coverage includes bounded contention retries, transaction rollback, busy database recovery, SQLITE_FULL rollback/recovery, read-only degradation, worker generation limits, retention behavior and application-level isolation so collector degradation does not take down HTTP health, authenticated metrics or WebSocket status.

Prior benchmark evidence remains synthetic CI-runner evidence, not an owner-host SLO. A 4-thread p99 regression in the accepted batch is documented; no latency guarantee is claimed. No new retry policy or jitter experiment is introduced in this cycle.

Gate 38 remains 🟧 until owner-host mount identity/permissions, restart persistence, retention and backup, disk-pressure recovery, private network perimeter, operator token rotation, human-facing dashboard, independent notification, acknowledgement/escalation and controlled recovery drill are evidenced.

## 3. Gate 20 — identity and authorization

Audited source:
- `backend/app/identity.py`
- `backend/tests/test_identity.py`
- `backend/app/entitlements.py`
- `backend/tests/test_entitlements.py`
- `backend/app/websocket_tickets.py`
- `backend/app/main.py`
- `src/services/firebase.ts`
- `src/auth/AuthProvider.tsx`
- `docs/WEBSOCKET_AUTH_DESIGN.md`

Repository-side protections:
- Firebase Admin verifies ID tokens with `check_revoked=True`.
- Issuer, audience/project, subject and auth_time are validated before a principal is created.
- SDK details and token fragments are normalized out of errors.
- Missing configuration/provider initialization fails closed.
- Per-account canonical-instrument entitlements default deny; grants are tied to a verified subject and immutable canonical UUID; revocation is immediate and idempotent.
- Short-lived WebSocket ticket is separate from the Firebase ID token and consumed once; exact-series mapping and entitlement are rechecked in the subscription path.
- Frontend Firebase config is public client configuration only; no service-account key is placed in VITE variables.

The test suite uses an injected/mock verifier at the identity-provider boundary. It cannot prove a real Firebase signed token, real revocation, deployed provider configuration or the live browser/Android session. Gate 20 remains 🟧. No Firebase billing, Phone/SMS auth, service account or production credential is added.

## 4. Gate 31 — encrypted backup and recovery

Audited source:
- `backend/app/sqlite_backup.py`
- `backend/app/backup_encryption.py`
- `backend/app/sqlite_restore_drill.py`
- `backend/tests/test_sqlite_backup.py`
- `backend/tests/test_backup_encryption.py`
- `backend/tests/test_sqlite_restore_drill.py`
- `docs/BACKUP_ENCRYPTION.md`
- `docs/GATE30_OWNER_HOST_RESTORE_DRILL_RUNBOOK.md`

Repository-side protections:
- SQLite Online Backup API creates a consistent read-only source snapshot.
- Backup and restore outputs are integrity-checked and atomically published to fresh paths.
- POSIX artifacts are owner-only (0600), flushed, and parent directory fsync is attempted.
- Encrypted artifact uses versioned AES-256-GCM, PBKDF2-HMAC-SHA256 with 600,000 iterations, random 16-byte salt and 12-byte nonce, and authenticated header.
- Decryption publishes no plaintext destination until GCM authentication succeeds.
- Tests cover round-trip, wrong passphrase, tampering, truncated/invalid format, cleanup, destination preservation, concurrent destination creation, symlink destinations, WAL consistency and application-domain restore verification.

Capacity planning for the owner-host restore drill is conjunctive. Let S = max(source main file + WAL bytes, logical page_count × page_size). For two destinations on one filesystem, required free space is at least 3S + max(64 MiB, ceil(0.10 × 3S)). On separate filesystems, each destination independently needs S + max(64 MiB, ceil(0.10 × S)). This is a preflight bound, not an estimate of the user's actual disk; the real source and filesystem must be measured on the owner host.

A local encrypted artifact is not an off-host backup. Separate offline key custody, independent destination, retention/access controls and successful key-recovery restore remain unverified. Gate 31 remains 🟧.

## 5. CI, mutation and deployment policy

This is a source/documentation audit against the exact branch baseline `ae1ff4ada7977239b6970cd5bef02335ece29f08`. No source files or runtime behavior changed. Existing exact-head evidence remains linked in Batch 62J-98 and the Gate 38 runbook. No new CI workflow was triggered because this cycle introduces documentation only; a docs-only green badge would add no source/test evidence.

No Vercel/Cloudflare deployment, paid service, remote host action, Termux command, Android device action, production credential, or `main` change occurred.

## 6. Gate 10 and project accounting

Gate 10 remains **0/10 formally closed**:
- 🟨🟩 Host/operator verification only: Gates 8, 30, 34, 35, 39.
- 🟧 Integration/acceptance still open: Gates 20, 25, 31, 36, 38.

Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored because approved denominators and weights are not established. No formal gate tick is awarded by this audit.

## 7. Complete indicator progress — no changes

No indicator formula, calculation module, data contract, shared hook, chart renderer, chart UI or indicator test changed. **No indicator progress credit is awarded.**

| Indicator / subsystem | Status | Formula / first valid candle index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; index 19 | Overlay, independent toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing over 14 price changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests |
| Bollinger20,2 | 🟨 Foundation | Mean ±2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated candle-index-aligned snapshot | Chart identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 Simulated/reference-gated | Synthetic educational accumulator, not exchange-native bid/ask truth | User reference image, reviewed blueprint, ON-only spaced clusters, bid/ask cells, performance acceptance |
| Heatmap | 🟥 Not implemented | No validated source/calculation contract | User reference, zero-cost source feasibility, validated contract, reviewed blueprint and renderer |
| Liquidation Maps | 🟥 Not implemented | No validated source/calculation contract | Zero-cost source feasibility, validated calculation, user reference/blueprint and renderer |

Correctness invariants remain: warm-up values null (never zero); candle-index alignment; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF retains normal candle spacing; only explicit ON activates spaced clusters. Footprint and Heatmap visual implementation remains gated on the user's visual references and reviewed blueprints.

## 8. Next executable order

1. Continue repository-side Gate 38 observability/retention and Gate 39 alert-recovery audit only where a measurable defect is found; do not repeat existing tests or benchmark experiments.
2. Prepare a single owner-host acceptance evidence checklist for Gate 25/36/38/20/31; do not attempt to fabricate host results.
3. Keep external acceptance blocked until the owner-controlled host/provider/device exists. Continue other repository-only gates without deployment or paid infrastructure.

**Final disposition:** three workstreams audited and documented; external acceptance remains honestly open. ZERO COST.
