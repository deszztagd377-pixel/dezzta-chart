# DEZZTA CHART — Batch 62J-34: Gate 8/38/39 Operational Hardening

**Date:** 20 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent HEAD:** `3d3f3c7a481e78bc9c09b966c1fbf1f70091517d`  
**Scope:** Zero-cost repository-side security, observability, and alert-delivery reliability.

## 1. Gate 38 — monitoring scrape hygiene
The internal `/internal/metrics` and `/internal/alert-delivery` endpoints were excluded from HTTP request counters and request logs. Previously only `/internal/metrics` was excluded, so repeated alert-status scraping polluted application request telemetry. Both routes remain conditional on an owner-injected token, require exact Bearer authentication, use constant-time comparison, and return no-store responses.

**Regression coverage:** missing token, wrong token, successful operator access, no-store headers, no query-string/token disclosure, and confirmation that scrape endpoints do not create request metric series.

## 2. Gate 39 — durable retry boundary coverage
Added regression tests for:
- capped exponential retry schedule (100 ns then capped at 150 ns despite an uncapped 200 ns second delay);
- strict due-time boundary (not claimable at due−1 ns, claimable at due);
- durable attempt-count progression;
- retry timestamp overflow beyond SQLite signed-int64 becoming a terminal failure without leaking an overflowing value into SQLite.

The existing lease-token acknowledgement, lease expiry, retry/terminal state, permanent failure and idempotency tests remain intact.

## 3. Gate 8 — evidence boundary
The API tests verify that internal operator endpoints deny missing/wrong credentials and do not expose the configured token or request query sentinels. This is repository-level evidence only. Owner-host secret injection, file permissions, process exposure and production log/crash redaction remain external acceptance items.

## 4. Indicator progress — no status inflation

| Indicator / subsystem | Status | Calculation / data foundation | Remaining work |
|---|---|---|---|
| SMA 20 | 🟨 | Rolling mean; first valid index 19 | Overlay, toggle, legend, stale clearing, render/lifecycle |
| EMA 20 | 🟨 | SMA-seeded; alpha 2/21; first valid index 19 | Overlay, toggle, legend, stale clearing, render/lifecycle |
| RSI 14 | 🟨 | Wilder smoothing; first valid index 14 | 0–100 pane, 30/70 guides, toggle, render/lifecycle |
| MACD 12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Dedicated pane, lines, histogram, zero guide, render/lifecycle |
| Bollinger 20,2 | 🟨 | Population deviation; first valid index 19 | Three-line overlay, toggle, legend, stale clearing |
| Shared Indicator Hook | 🟨 | Validated backend snapshot | Chart identity/timeframe binding and stale-state handling |
| Footprint | 🟧 | SIMULATED educational accumulator | Owner reference image and reviewed blueprint; ON-only cluster layout |
| Heatmap | 🟥 | Not implemented | Owner reference, approved blueprint and validated source contract |
| Liquidation Maps | 🟥 | No validated data/calculation contract | Source feasibility and reviewed design |

No indicator implementation changed in this batch. No indicator progress percentage is awarded.

## 5. Gate 10 and project accounting

| Gate | Status | Remaining acceptance |
|---:|---|---|
| 8 | 🟧 | Owner-host secret injection, permissions, process/log/crash redaction |
| 20 | 🟧 | Real Firebase sign-in, expiry/revocation, entitlement denial, browser/Android reconnect |
| 25 | 🟧 | Owner-host Redis TLS/ACL/rotation, persistence/recovery, snapshot/relay |
| 30 | 🟧 | Actual Android DB path, fresh-path restore, application readback and timing |
| 31 | 🟧 | Encrypted off-host artifact, separate key custody, independent restore, retention/deletion |
| 34 | 🟧 | Actual persistent mount/path, UID/GID, restart persistence, disk pressure |
| 35 | 🟧 | Owner-controlled HTTPS host, certificate/hostname, health/startup/secret injection |
| 36 | 🟧 | Authenticated public WSS proxy, browser/Android acceptance, reconnect/replay/restart |
| 38 | 🟧 | Owner-controlled dashboard access, bounded retention/cardinality, disk pressure and redaction |
| 39 | 🟧 | Induced-failure alert, operator acknowledgement/escalation and tested incident recovery |

- Gate 10: **10/10 ORANGE, 0 CLOSED**.
- Stage 1: **30/40 = 75% provisional**.
- Stages 2–6: unscored.
- Overall project percentage: not established; M1–M8 weights are not approved.
- Indicator aggregate percentage: not established; no approved acceptance denominator.

## 6. Validation and cost controls
The batch must pass exact-head Automated Tests, CodeQL (JavaScript/TypeScript and Python), and Full Git History Secret Audit before it is considered verified. CI failure blocks acceptance. No Vercel/Cloudflare deployment, paid provider, paid monitoring, or Termux operation is part of this batch. Repository CI does not close owner-host or Android-device acceptance gates.

## 7. Files changed
- `backend/app/main.py`
- `backend/tests/test_api.py`
- `backend/tests/test_alert_store.py`
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
- `docs/INDICATOR_PROGRESS_LEDGER.md`
- `docs/WORK_CYCLE_2026-11-20_BATCH62J34_GATE8_38_39_OPERATIONAL_HARDENING.md`
