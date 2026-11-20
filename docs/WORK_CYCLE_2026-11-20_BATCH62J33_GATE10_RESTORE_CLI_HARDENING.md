# Batch 62J-33 — Gate 10 restore-drill CLI acceptance hardening

**Date:** 20 November 2026
**Repository:** `deszztagd377-pixel/dezzta-chart`
**Branch:** `phase-2/market-data-foundation`
**Starting HEAD:** `5bfa0d231469ef711fb4a7162e3a2d5a49715e8c`
**Scope:** continue immediately after WebSocket E automated acceptance closure and advance Gate 10 repository-side work. No production deployment, paid infrastructure or owner-device operation was performed.

## 1. WebSocket E disposition

Batch 62J-31 added and passed:
- Controlled TCP-path interruption across two live ASGI gateways, with both proxy paths restored without restarting the gateway processes and cursor-1 parity confirmed.
- Coordinated installation of the same verified snapshot watermark into two durable replicas, new-generation consumers applying cursor 3, parity at cursor 3, and old pending entries left isolated.

Therefore E is **COMPLETE FOR THE DEFINED AUTOMATED FAILURE-MATRIX SCOPE**. This does not mean Redis server shutdown, production relay activation, owner-host TLS/ACL rotation, public WSS, browser/Android acceptance or operational recovery have passed.

## 2. Exact-head starting CI

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | 44710864296 | SUCCESS |
| CodeQL | 44710864281 | SUCCESS |
| Full Git History Secret Audit | 44710864297 | SUCCESS |

All three workflows passed on starting HEAD `5bfa0d231469ef711fb4a7162e3a2d5a49715e8c`. The new CLI tests in this batch require a fresh exact-head run before being called verified.

## 3. Gate 30 change

Added CLI tests for `app.sqlite_restore_drill.main`:
- Failure path: returns exit code 1, emits a sanitized JSON error with only the exception class, and withholds absolute paths and low-level exception details.
- Success path: returns exit code 0, emits a parseable JSON restore report, verifies its SHA-256 digest, confirms representative application-domain readback, redacts source/backup/restore paths, and confirms the source database bytes remain unchanged.

The underlying restore drill already uses SQLite Online Backup API, fresh destinations, integrity and foreign-key checks, schema and full row-content hashes, application-domain readback, post-restore committed write/read/cleanup, and a timestamped redacted report.

**Evidence boundary:** these are isolated CI fixture tests. They do not access the owner's live Android database and do not close Gate 30.

## 4. Gate 10 disposition

All ten gates remain 🟧 ORANGE / OPEN, 0/10 closed:
- 8: actual host secret injection and runtime inspection remain.
- 20: real no-billing Firebase provider and device/browser acceptance remain.
- 25: owner-host Redis TLS/ACL/rotation/network/relay acceptance remains.
- 30: live Android database path and owner-device restore report remain.
- 31: off-host backup and independent key custody remain constrained by one-device environment and Termux package/keyring compatibility.
- 34: actual persistent host volume acceptance remains.
- 35: owner-controlled HTTPS endpoint and certificate acceptance remain.
- 36: public WSS proxy and browser/Android acceptance remain.
- 38: deployed dashboard access/retention/disk-pressure acceptance remains.
- 39: operator alert acknowledgement and incident-response drill remain.

No gate closure or Stage 1 tick is awarded by documentation or CI alone.

## 5. Indicator dashboard

- SMA20 🟨 — rolling mean, first valid index 19.
- EMA20 🟨 — SMA-seeded, alpha 2/21, first valid index 19.
- RSI14 🟨 — Wilder smoothing, first valid index 14.
- MACD12/26/9 🟨 — MACD index 25; signal/histogram index 33.
- Bollinger20,2 🟨 — population standard deviation, first valid index 19.
- Shared Indicator Hook 🟨 — validated shared snapshot; chart binding/lifecycle remains.
- Footprint 🟧 — deterministic simulated data only; owner reference image and reviewed blueprint required.
- Heatmap 🟥 — not implemented; owner reference image and reviewed blueprint required.
- Liquidation Maps 🟥 — validated data/calculation contract absent.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 are unscored. Overall project percentage is not established because M1–M8 weights are not approved. Indicator aggregate percentage is also not established.

## 6. Cost, device and branch controls

- ZERO COST maintained.
- No Vercel/Cloudflare deployment or promotion.
- No paid provider, hosting, subscription, trial or billing change.
- No Termux operation required for this batch.
- No `main` branch modification.
- No production runtime activation.

## 7. Next safe sequence

1. Verify the exact-head CI for the two new CLI tests.
2. Continue Gate 30 only after the effective live Android database path can be positively identified; never guess or overwrite the source.
3. In parallel, advance repository-only evidence for Gates 8, 25, 34, 38 and 39 where tests can add value without pretending to be owner-host acceptance.
4. Keep Gate 31 deferred until a verified no-cost off-host destination and safe key custody exist.
