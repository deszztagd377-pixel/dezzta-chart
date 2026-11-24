# DEZZTA CHART — Batch 62J-229

## Owner-host Ed25519 signing-key file boundary hardening (24 November 2026)

**Branch:** phase-2/market-data-foundation  
**Parent HEAD:** 79f93831bd08d1468b8954d2782970309326d46d  
**Scope:** source-host private-key file loading and regression coverage; no key material or production credentials used.  
**Cost:** ZERO COST • main untouched • no Vercel deployment.

### Correction note — Batch 62J-230

The three intended regression test functions were not present in this batch's initial test-file commit; post-CI diff inspection found that only the import had landed. Batch 62J-230 added the three functions, and Batch 62J-231 records their exact-HEAD CI success. The original source hardening remains as described below.

### 1. Finding and risk boundary

The previous loader checked path permissions with Path.stat() and then separately read the path. That left a symlink-following and path-replacement window between metadata validation and reading. It also did not explicitly require a regular file or bound the amount of PEM input read.

This matters because the private Ed25519 key is the source-side trust anchor for Gate 25 snapshot attestations. The repository-side loader should fail closed before key parsing when the path does not satisfy the file boundary.

### 2. Source change

Updated backend/app/snapshot_attestation.py:
- Open the key path once and validate the opened descriptor with fstat, avoiding a separate stat-then-read path race.
- On POSIX, require O_NOFOLLOW; symbolic links fail closed.
- Require a regular file.
- On POSIX, require ownership by the effective service user and deny group/world permissions.
- Read at most 65,537 bytes and reject files larger than 64 KiB.
- Close the descriptor on every success/error path before parsing the bounded PEM bytes.
- Preserve Ed25519 type validation and the existing environment-variable contract.

No private key bytes, environment values, production host details or secrets were added to source control.

### 3. Regression coverage

Updated backend/tests/test_snapshot_attestation.py with three cases:
1. POSIX symlink rejection.
2. Non-regular path rejection.
3. Oversized key file rejection.

Existing coverage still exercises successful owner-only PEM loading, group/world permission rejection, environment configuration pairing, Ed25519 signature round-trip, tamper rejection, trusted-key validation and authenticated snapshot receipt installation.

### 4. WebSocket / Gate 25 roll-up

| Scope | Status | Reason |
|---|---|---|
| Ed25519 signature verification and deterministic metadata binding | 🟩 Repository foundation | Existing source/tests |
| Immutable receipt persistence and receipt/checkpoint verification | 🟩 Repository foundation | Existing source/tests |
| Private-key path boundary on source host | 🟩 Hardened in this batch; CI pending | New descriptor-based loader and regression cases |
| Actual owner-host private-key custody and authenticated snapshot transfer | 🟥 OPEN | Requires real owner-controlled host execution and transport evidence |
| Every gateway's persisted receipt retrieval, restart re-verification and durable high-water ACK | 🟥 OPEN | Requires per-gateway operational evidence |
| Gate 25 parent acceptance | 🟥 OPEN | Cannot be closed by unit tests alone |
| Public HTTPS/WSS, reverse proxy/TLS and production runtime (Gate 36) | 🟥 OPEN | Requires public endpoint/deployment proof |
| Firebase production sign-in, entitlement and revocation E2E | 🟥 OPEN | Requires owner-controlled production project evidence |
| Browser/Android real lifecycle and production multi-instance failover | 🟥 OPEN | Requires deployed runtime and device acceptance |
| Redis destructive retention | 🟧 BLOCKED | Do not trim/delete stream entries or destroy consumer groups until all independent safety prerequisites pass |

The key-loader patch reduces local file-boundary risk. It does not establish remote authentication, host custody, transfer integrity, gateway receipt durability or production availability. Gate 25 remains open.

### 5. Indicator progress — complete inventory

Focused test declaration inventory at the parent source checkpoint: **28 total = 21 calculation-engine tests + 7 shared-hook tests**. The new Gate 25 patch does not alter indicator code or award indicator completion credit.

| Indicator / subsystem | Foundation | Chart/UI integration | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay/toggle/legend/lifecycle absent | 🟨 |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay/toggle/legend/lifecycle absent | 🟨 |
| RSI14 Wilder | 14-change seed + Wilder recurrence; first valid index 14 | Pane and 30/70 guides absent | 🟨 |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; indices 25/33 | Pane, lines, histogram and zero guide absent | 🟨 |
| Bollinger20,2 | Mean ± 2 population standard deviations; first valid index 19 | Bands/fill/toggle/latest values absent | 🟨 |
| Shared Indicator Hook | Keyed immutable snapshot, shared cache, trust gating, stale clearing | Not integrated into CandlestickChart | 🟨 |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Renderer gated; owner references recorded | 🟧 |
| Volume Profile | Incomplete | Not integrated | 🟥 |
| Complete Volume Profile | Incomplete | Not integrated | 🟥 |
| Movable-range VP Tool | Incomplete | Not integrated | 🟥 |
| Heatmap | Depth/liquidity engine not verified | Not integrated; reference gate remains | 🟥 |
| Liquidation Maps | Methodology/provenance not verified | Not integrated | 🟥 |

Footprint OFF must retain standard candlestick spacing; only explicit ON may switch to spaced clusters. Footprint and Heatmap visual implementation remain behind the stage/blueprint/user-review gates. **Aggregate indicator completion remains NOT SCORED** because no approved denominator/weights exist.

### 6. Project progress dashboard

| Meter | Current evidence | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 criteria = 75% provisional; inherited baseline, not rescored here | 🟨 |
| Stage 2 — Market Data Infrastructure | Active engineering; denominator not approved | 🟦 NOT SCORED |
| Stage 3 — Chart Engine & Timeframe | Not formally scored | ⬜ NOT SCORED |
| Stage 4 — Indicators & Analytics | Stage gate and scoped blueprint/review required | 🟪 GATED |
| Stage 5 — Professional UI & Interactive Tools | Not formally scored | ⬜ NOT SCORED |
| Stage 6 — Hardening, Validation & APK Release | Not formally scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicator completion | No approved denominator/weights | ⚪ NOT SCORED |
| IP3S / significant progress | No approved formula applied | ⚪ NOT SCORED |

No overall percentage or IP3S value is inferred from Stage 1's provisional 75%.

### 7. CI and release controls

The code/test commit created from this batch must receive its own exact-HEAD CI read-back. Required workflows: Automated Tests, CodeQL, OCI ARM64 readiness and Full Git History Secret Audit. Parent CI success is not inherited by a new SHA. Poll every workflow to a terminal state and inspect any failure before calling the batch complete.

No deployment, Vercel commit/deploy, main update, paid service, new dependency, destructive Redis operation or APK release is part of this batch. Delivery target remains approximately **24 December 2026**, a planning target only.

### 8. Next strict work order

1. Finish exact-HEAD CI for this source/test batch and repair any confirmed regression.
2. Continue Gate 25 owner-host authenticated transfer and per-gateway durable receipt/restart/high-water evidence.
3. Then close public HTTPS/WSS and Firebase production E2E (Gate 36).
4. Then browser/Android process lifecycle, network handover and production multi-instance failover.
5. Redis destructive retention only after gateway inventory/retirement, PEL policy, per-gateway floor ACK, separate authority and crash-safe trim/reconcile are all proven.
6. Keep chart indicator UI behind the formal stage gate and reviewed blueprint.

**Batch result:** source and regression test prepared; external Gate 25 acceptance remains open; no indicator/stage progress percentage awarded.



### Batch 62J-231 — exact-HEAD CI closure (24 November 2026)

The correction commit 1b7096566030f7c7775958c1fb60fbe628a3b7f1 has now completed all four required workflows successfully:

- Automated Tests [45435451481](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45435451481) — SUCCESS, 41/41 steps.
- CodeQL [45435451743](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45435451743) — SUCCESS, Python 8/8 and JavaScript/TypeScript 8/8 steps.
- OCI ARM64 [45435451497](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45435451497) — SUCCESS, 7/7 steps.
- Full Git History Secret Audit [45435451477](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45435451477) — SUCCESS, 6/6 steps.

Backend test log confirms **1,393 passed, 1 skipped, 6 warnings in 61.36s**. The one skip is the separately configured Redis TLS integration fixture. All three new Gate 25 signing-key loader regression tests explicitly passed. This is repository CI evidence only; it does not close owner-host Gate 25 or production WebSocket acceptance.
