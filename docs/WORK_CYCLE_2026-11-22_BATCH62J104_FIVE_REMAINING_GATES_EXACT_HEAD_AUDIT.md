# DEZZTA CHART — Work Cycle 62J-104
## Five remaining Gate 10 acceptance tracks — exact-head CI and source audit

**Date:** 22 November 2026  
**Active branch:** `phase-2/market-data-foundation`  
**Audited source/test HEAD:** `a18e963d4cd067fe22ec8d03c653418e003c7fde`  
**ZERO COST:** no deployment, paid service, production credential, Termux/device operation or `main` modification.

## 1. Exact-head CI acceptance — VERIFIED

All workflows below point to the exact audited source/test HEAD `a18e963d4cd067fe22ec8d03c653418e003c7fde`:

- Automated Tests [44970436441](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436441): **SUCCESS**. Frontend: 255/255 tests across 29 files. Backend: **1,289 passed in 51.98 s**. The five tests added in Batch 62J-103 were individually visible as PASSED in the job log.
- CodeQL [44970436417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436417): **SUCCESS**, both Python and JavaScript/TypeScript analyses.
- Full Git History Secret Audit [44970436377](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436377): **SUCCESS**, complete reachable Git history.
- Automated job also passed frontend dependency audit, source and production-bundle secret scans, backend dependency audit, container build, shared Redis guard/persistent-volume smoke, configured container image scan and vulnerability report export.

This resolves the previous Batch 62J-103 CI evidence uncertainty. It does not substitute for production-host or owner-operator acceptance.

## 2. Five remaining Gate 10 tracks

All five remain **🟧 OPEN** for integration/acceptance. Their repository-side coverage is materially stronger, but the outstanding acceptance requires owner-controlled infrastructure or credentials not available in this repository session.

### Gate 20 — identity, entitlement and WebSocket ticket
**Repository evidence:** verified-principal claim validation, Firebase Admin SDK initialization/revocation checks, malformed/oversized token rejection, identity-provider outage normalization, account-bound tickets, single-use ticket consumption, subject mismatch rejection, entitlement recheck on renewal, invalid/expired renewal ticket rejection, ticket-store outage fail-closed behavior and sanitized error responses. Exact-head tests are included in the 1,289 backend pass.

**Still external:** actual Firebase project signed-token E2E for valid, expired, revoked and wrong-project tokens; production project configuration and final ticket-scope threat-model review. Test verifier fixtures are not live Firebase credentials.

### Gate 25 — Redis shared guard and snapshot/replica path
**Repository evidence:** TLS certificate/hostname validation, production rediss/ACL configuration guard, atomic Lua rate-limit/lease/ticket operations, digest-keyed one-use tickets, exact 90-second TTL, NX create-only writes, cross-client and cross-process state, renewal/expiry/outage behavior, snapshot verification before runtime install, source mismatch and unverified installer rejection. CI shared Redis ACL/AOF persistent-volume container smoke passed on the exact-head Automated Tests job.

**Still external:** owner-host Redis TLS/ACL credentials, independent authenticated snapshot transfer/receipt, actual persistent-volume lifecycle and failover/recovery on the intended host. CI container evidence is not owner-host evidence.

### Gate 31 — encrypted backup and recovery
**Repository evidence:** SQLite Online Backup API snapshot, integrity and foreign-key checks, schema and row-content hashes, fresh-path restore, post-restore write/read/cleanup probe, AES-256-GCM, PBKDF2-HMAC-SHA256 with 600,000 iterations, random salt/nonce and authenticated header, wrong-key/tamper/truncation rejection, private temporary files, no-overwrite atomic publication, symlink rejection and encrypted full-application round-trip into the restore drill.

**Still external:** an independently controlled off-host copy, separately stored offline recovery key, retention/access policy, and successful key-recovery restore on the intended owner host. Losing the passphrase makes that encrypted artifact unrecoverable. No key or credential is to be placed in Git or chat.

### Gate 36 — WebSocket runtime and client acceptance
**Repository evidence:** authentication, ticket renewal, lease renewal/release, heartbeat and timeout behavior, replay cursor validation, replay/live handoff, entitlement recheck, origin policy, failure isolation, close-code handling, reconnect/resnapshot behavior, frontend WebSocket client tests and backend WebSocket integration tests. Exact-head frontend suite passed 255/255; backend passed 1,289/1,289.

**Still external:** public HTTPS/WSS endpoint, owner-host TLS/reverse-proxy configuration, live Redis, cross-instance fan-out and browser/Android WebView foreground/background acceptance, including the required real observation window. No deployment was performed to manufacture this evidence.

### Gate 38 — monitoring, retention and operator recovery
**Repository evidence:** bounded process-local metrics, same-host SQLite aggregation, 899 logical series against a 900-series limit, 15-minute buckets, seven-day retention, 650,000 aggregate-row ceiling, 16-worker cap, 256 worker-generation cap, 4,096 tombstones, 256 KiB snapshot cap, WAL, 250 ms busy timeout, bounded lock retries, startup staggering, disk-full/read-only/corrupt DB tests and application-level HTTP/WebSocket failure isolation. Exact-head CI benchmark and container smoke passed.

**Capacity arithmetic:** 899 × 672 = **604,128** planned aggregate rows. The 650,000 row cap leaves **45,872 rows**, or **7.06%** nominal headroom. Series utilization is 899/900 = **99.89%**, leaving one logical series. The CI startup-staggered 16-worker case verified 512/512 flushes, 899/899 series, zero retries, SQLite integrity `ok`, peak DB+WAL+SHM of 5,744,952 bytes and post-checkpoint total of 1,126,400 bytes. This is a synthetic CI-runner observation, not an owner-host byte budget or SLA.

**Still external:** actual owner-host persistent-volume identity/permissions/restart persistence, private firewall/reverse-proxy perimeter, operator-token injection/rotation, a human-facing dashboard/access review, independent no-cost notification/acknowledgement and a real disk-pressure/incident/recovery drill. The JSON metrics endpoint and local logs alone are not a dashboard or independent alert route. SQLite collector scope is same-host only, not multi-host.

## 3. Gate 10 status and project accounting

- Gate 10: **0/10 formally closed**.
- 🟨🟩 host/operator-only verification: Gates 8, 30, 34, 35 and 39.
- 🟧 integration/acceptance still open: Gates 20, 25, 31, 36 and 38.
- Stage 1: **30/40 = 75% provisional**. No point is awarded by CI alone.
- Stages 2–6 and overall project percentage: unscored because approved weights/denominators are not defined.
- No stage/gate was marked complete by this audit.

## 4. Indicator progress — no implementation change

This was a backend/acceptance audit. No indicator calculation, data contract, shared hook, renderer, chart UI or indicator test changed; no indicator progress credit is awarded.

- SMA20 🟨 — mean of 20 closes; valid from candle index 19; overlay/toggle/legend/stale-clear/renderer tests remain.
- EMA20 🟨 — SMA-seeded EMA, α = 2/21; valid from index 19; overlay/toggle/legend/stale-clear/renderer tests remain.
- RSI14 🟨 — Wilder smoothing over 14 close changes; valid from index 14; 0–100 pane, 30/70 guides and renderer acceptance remain.
- MACD 12/26/9 🟨 — EMA12−EMA26; MACD index 25, signal/histogram index 33; pane/lines/histogram/zero guide and renderer acceptance remain.
- Bollinger20,2 🟨 — 20-close mean ±2 × population SD; valid from index 19; three-line overlay and renderer acceptance remain.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot; chart identity/timeframe, loading/error lifecycle, stale clearing and series isolation remain.
- Footprint 🟧 — simulated/educational only, not exchange-native bid/ask truth; user reference image and reviewed blueprint required before visual work. OFF preserves normal candle spacing; explicit ON alone enables spaced clusters.
- Heatmap 🟥 — not implemented; requires zero-cost source feasibility, reference, validated contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥 — not implemented; requires zero-cost source feasibility, validated calculation/data contract, reference/blueprint and renderer.

Shared invariants: warm-up values null, never zero; candle-index alignment; no future-candle repaint; clear stale series on symbol/venue/dataset/chart/timeframe changes. Aggregate indicator percentage remains unscored without approved weights/denominators.

## 5. Engineering decision

No further production-source patch was justified by this five-track source audit: existing tests and code cover the repository-controllable failure boundaries extensively, and the remaining blockers are external acceptance evidence. Adding duplicate tests or synthetic configuration would inflate activity without closing a gate.

Next work should proceed against the actual owner-controlled host evidence packs, with zero-cost constraints and redacted evidence. Do not request production secrets in chat. Do not use Termux unless a real device-side acceptance step is later confirmed and the owner is notified first.

No deployment, no paid service, no Termux/device operation, no production credentials and no `main` modification.
