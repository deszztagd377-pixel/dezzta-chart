# DEZZTA CHART — Batch 62J-232
## Non-blocking POSIX private-key file opening and FIFO rejection

**Date:** 25 November 2026  
**Branch:** phase-2/market-data-foundation  
**Parent SHA:** 821b3b6602fa2568bf2e103bb725651b1a60de6c  
**Scope:** Gate 25 owner-side Ed25519 key-file loader. ZERO COST; no production credentials or secrets.

### Finding and correction
The loader previously used O_NOFOLLOW and then fstat, but opening a FIFO with O_RDONLY can block before fstat executes. POSIX open flags now also include O_NONBLOCK. The descriptor must still pass fstat regular-file validation. O_CLOEXEC remains enabled where supported.

The permissions diagnostic now describes the actual invariant: no group/world access. Owner-read-only mode is valid; exactly 0600 is not the only acceptable owner-only mode.

### Regression coverage
Added a POSIX-only FIFO fixture using os.mkfifo. With no writer connected, the loader must promptly raise ValueError because the path is not a regular file. This test would hang under the prior blocking-open behavior, so it specifically guards that failure mode. Existing symlink, directory and oversized-file tests remain.

### Gate 25 status
Repository-side key-file handling is hardened, but Gate 25 remains 🟥 OPEN until actual owner-host private-key custody, authenticated remote transfer, persisted receipt retrieval from every gateway, restart re-verification and durable per-gateway high-water ACK are evidenced. Unit tests cannot close those external acceptance criteria.

### Complete indicator ledger
Focused indicator inventory remains 28 named declarations = 21 calculation-engine + 7 shared-hook tests. The new FIFO test is backend security coverage and is excluded.

| Indicator / subsystem | Foundation state | Chart/UI integration | Status |
|---|---|---|---|
| SMA20 | 20-close mean; first valid index 19 | Overlay/toggle/legend/lifecycle absent | 🟨 |
| EMA20 | SMA-seeded EMA, alpha 2/21; first valid index 19 | Overlay/toggle/legend/lifecycle absent | 🟨 |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | 0–100 pane and 30/70 guides absent | 🟨 |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; first MACD index 25, signal index 33 | Pane/lines/histogram/zero guide absent | 🟨 |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Three-line overlay/fill/toggle absent | 🟨 |
| Shared Indicator Hook | Keyed immutable snapshot/cache/trust gating/stale clearing | Not integrated into CandlestickChart | 🟨 |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Renderer gated; owner references recorded | 🟧 |
| Volume Profile | Production calculation not verified | Not integrated | 🟥 |
| Complete Volume Profile | Production calculation not verified | Not integrated | 🟥 |
| Movable-range VP Tool | Range-selection/calculation lifecycle not verified | Not integrated | 🟥 |
| Heatmap | Accepted depth/liquidity engine not verified | Not integrated; reference/data gate | 🟥 |
| Liquidation Maps | Methodology/provenance not accepted | Not integrated | 🟥 |

Footprint OFF preserves ordinary candle layout/spacing; explicit ON alone activates spaced clusters. Footprint and Heatmap visuals remain behind the stage gate, scoped blueprint and user review. Aggregate indicator completion remains ⚪ NOT SCORED; no approved denominator/weights.

### Project meters
| Meter | Evidence | Status |
|---|---|---|
| Stage 1 Foundation | 30/40 = 75% provisional, inherited baseline | 🟨 |
| Stage 2 Market Data Infrastructure | Active; denominator unapproved | 🟦 NOT SCORED |
| Stage 3 Chart Engine & Timeframe | Not formally scored | ⬜ NOT SCORED |
| Stage 4 Indicators & Analytics | Stage gate and reviewed blueprint required | 🟪 GATED |
| Stage 5 Professional UI & Tools | Not formally scored | ⬜ NOT SCORED |
| Stage 6 Hardening/Validation/APK | Not formally scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicators | No approved denominator/weights | ⚪ NOT SCORED |
| IP3S/significant progress | No approved formula applied | ⚪ NOT SCORED |

### WebSocket strict work order
1. Gate 25 owner-host custody, authenticated transfer, per-gateway durable receipt/restart/high-water evidence.
2. Gate 36 public HTTPS/WSS, reverse proxy/TLS and production runtime.
3. Firebase production sign-in, entitlement and revocation E2E.
4. Browser/Android lifecycle, process death, network handover and multi-instance failover/replay.
5. Redis destructive retention only after gateway inventory/retirement, PEL policy, per-gateway floor ACK, separate authority and crash-safe trim/reconcile all pass.

No destructive Redis operation, Vercel deployment, paid service or main-branch update. Exact-HEAD Automated Tests, CodeQL, OCI ARM64 and Full Git History Secret Audit are required for this new SHA.

**Result:** FIFO open-blocking edge case addressed in source and test; Gate 25 external acceptance remains open; no completion percentages awarded. APK target approximately 24 December 2026 (planning target only).
