# DEZZTA CHART — Batch 62J-233
## Exact-head CI closure and operational progress reconciliation

**Date:** 25 November 2026  
**Documentation parent:** bd4904b52d29b3ec456da91014e90922fec35f21  
**Code/test SHA:** bd4904b52d29b3ec456da91014e90922fec35f21  
**Branch:** phase-2/market-data-foundation  
**Cost:** ZERO COST

### 1. Exact-head CI evidence

All four required workflows reached terminal SUCCESS on the code/test SHA:
- Automated Tests: run 45520805106, 41/41 steps, SUCCESS.
- CodeQL: run 45520805120, Python 8/8 and JavaScript/TypeScript 8/8, SUCCESS.
- OCI ARM64: run 45520805221, 7/7 steps, SUCCESS.
- Full Git History Secret Audit: run 45520805267, 6/6 steps, SUCCESS.

Backend pytest summary from the completed job log: **1,394 passed, 1 skipped, 6 warnings in 66.76 seconds**. The skip is the separately configured Redis TLS integration fixture; the new FIFO test was explicitly PASSED. All steps, including cleanup/stop containers, completed. No workflow remains active for the code/test SHA.

### 2. Batch 62J-232 source change

The POSIX Ed25519 private-key loader opens the key descriptor with O_NOFOLLOW and O_NONBLOCK (plus O_CLOEXEC where supported). O_NONBLOCK closes the FIFO edge case where O_RDONLY could wait for a writer before fstat can reject a non-regular file. The new FIFO regression test passed. Group/world permissions remain forbidden; diagnostic wording now states the actual invariant and does not incorrectly imply exactly 0600 is the only owner-only mode.

### 3. WebSocket/Gate 25 state

| Requirement | Status | Evidence / remaining condition |
|---|---|---|
| Ed25519 canonical payload, signature verification, trusted key ID | 🟩 Repo verified | Source + CI |
| Immutable snapshot receipt, content digest and checkpoint binding | 🟩 Repo verified | Source + tests |
| Gateway startup re-verifies persisted receipt | 🟩 Repo verified | Dedicated test exists and CI passes |
| Source private-key file open boundary | 🟩 Repo verified | O_NOFOLLOW + O_NONBLOCK + FIFO/symlink/regular-file/size tests |
| Actual owner-host key custody outside Git/container context | 🟥 OPEN | Owner-operated host evidence required |
| Authenticated transfer of exact signed snapshot to every gateway | 🟥 OPEN | Owner-host callback is injected; real transfer evidence unavailable |
| Every gateway receipt retrieval after process restart | 🟥 OPEN | Runtime re-verification exists; per-host durable retrieval acceptance remains external |
| Durable per-gateway high-water ACK evidence | 🟥 OPEN | Must be read from each persistent gateway checkpoint after restart; do not equate Redis XACK with durable owner-accepted high-water ACK |
| Gate 25 parent acceptance | 🟥 OPEN | External evidence still required |
| Public HTTPS/WSS, reverse proxy/TLS and production runtime (Gate 36) | 🟥 OPEN | No public endpoint acceptance evidence |
| Firebase production sign-in, entitlement and revocation E2E | 🟥 OPEN | No real project E2E evidence |
| Browser/Android real lifecycle and production multi-instance failover | 🟥 OPEN | CI simulations are not device/host acceptance |
| Redis destructive retention | 🟧 BLOCKED | No XTRIM/XDEL/group destruction until every independent prerequisite is accepted |

The Redis consumer correctly performs durable SQLite apply and callback before XACK, and retries pending entries after ACK loss. Redis XACK removes a PEL entry; it is not by itself the separately required durable high-water floor acknowledgement for retention. No destructive retention operation was performed.

### 4. Indicator progress — complete inventory

Focused indicator suite: **28 named declarations = 21 calculation-engine + 7 shared-hook**. Backend Gate 25 tests are excluded. No indicator source or chart integration changed in Batches 62J-229 through 62J-233.

| Indicator / subsystem | Foundation | Visible chart/UI | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | 0–100 pane and 30/70 guides absent | 🟨 |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; MACD index 25, signal/histogram index 33 | Pane/lines/histogram/zero guide absent | 🟨 |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Three-line overlay/fill/toggle/latest values absent | 🟨 |
| Shared Indicator Hook | Keyed immutable snapshot, shared cache, trust gating, stale-output clearing | Not integrated into CandlestickChart | 🟨 |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Renderer gated; two user references recorded | 🟧 |
| Volume Profile | Complete production calculation not verified | Not integrated | 🟥 |
| Complete Volume Profile | Complete production calculation not verified | Not integrated | 🟥 |
| Movable-range VP Tool | Range-selection/calculation lifecycle not verified | Not integrated | 🟥 |
| Heatmap | Accepted depth/liquidity engine not verified | Not integrated; reference/data contract gate | 🟥 |
| Liquidation Maps | Methodology/provenance not accepted | Not integrated | 🟥 |

Footprint OFF preserves standard candlesticks and spacing; explicit ON alone enables spaced candle clusters. Footprint and Heatmap visuals remain behind Stage 4 gate, scoped blueprint and user review. Aggregate indicator completion remains NOT SCORED because no approved denominator/weights exist.

### 5. Project progress meters

| Stage / metric | Evidence | Status |
|---|---|---|
| Stage 1 Foundation | 30/40 criteria = 75% provisional; inherited baseline, not rescored | 🟨 |
| Stage 2 Market Data Infrastructure | Active engineering; denominator unapproved | 🟦 NOT SCORED |
| Stage 3 Chart Engine & Timeframe | Not formally scored | ⬜ NOT SCORED |
| Stage 4 Indicators & Analytics | Formal stage gate and reviewed blueprint required | 🟪 GATED |
| Stage 5 Professional UI & Tools | Not formally scored | ⬜ NOT SCORED |
| Stage 6 Hardening/Validation/APK | Not formally scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicators | No approved denominator/weights | ⚪ NOT SCORED |
| IP3S/significant progress | No approved formula applied | ⚪ NOT SCORED |

### 6. Strict next work order

1. Continue Gate 25 owner-host authenticated snapshot transfer and verify each gateway's persisted receipt after restart.
2. Obtain a separately durable high-water ACK/checkpoint from every gateway; do not use Redis XACK as a substitute.
3. Only after Gate 25 acceptance, proceed to Gate 36 public HTTPS/WSS and TLS/proxy production proof.
4. Then Firebase production sign-in, entitlement and revocation E2E.
5. Then real browser/Android process lifecycle, network handover, process-death recovery and production multi-instance failover/replay.
6. Redis destructive retention only after gateway inventory/retirement, PEL policy, per-gateway floor ACK, separate authority and crash-safe trim/reconcile all pass.
7. Keep indicator chart UI behind Stage 4 and reviewed scoped blueprint.

No paid services, secrets, deployments, main updates, destructive Redis actions or APK releases. APK target remains approximately 24 December 2026, planning target only.

**Batch result:** source/test CI 4/4 terminal SUCCESS; no active workflow remains for code/test SHA bd4904b5; production Gate 25/36 remain open; indicator and overall completion are not scored.
