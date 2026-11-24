# DEZZTA CHART — Batch 62J-230

## Gate 25 signing-key loader regression-test completion (24 November 2026)

**Branch:** phase-2/market-data-foundation  
**Parent:** af5d30e3f8daa552c1676a16007f73c749c8f2a1  
**Parent CI:** 4/4 terminal SUCCESS (Automated Tests, CodeQL, OCI ARM64, Full Git History Secret Audit).  
**Purpose:** correct an incomplete test-file update discovered during post-CI diff inspection. The parent commit changed the test import but did not include the three intended test functions. This batch adds those functions explicitly.

### 1. Regression tests added

File: backend/tests/test_snapshot_attestation.py

- POSIX symbolic-link path: confirms O_NOFOLLOW boundary rejects a symlink before private-key parsing.
- Non-regular path: confirms a directory is rejected.
- Oversized file: confirms a 65,537-byte file is rejected by the 64 KiB bound.

The test file already imports os for the platform-specific skip condition. The tests exercise only temporary local fixtures and generated ephemeral test keys; no real signing key or secret is used.

### 2. Source implementation under test

The parent source commit af5d30e3f8daa552c1676a16007f73c749c8f2a1 introduced:
- single-descriptor open/fstat validation;
- POSIX O_NOFOLLOW requirement;
- regular-file validation;
- effective-service-user ownership validation;
- group/world permission rejection;
- bounded 64 KiB PEM read;
- descriptor cleanup on error and success.

The previous commit's Automated Tests workflow passed, but because the test functions were absent at that time, that result is not evidence for the three new cases. This new SHA must receive a fresh CI run.

### 3. Gate 25 status

| Criterion | Status |
|---|---|
| Deterministic Ed25519 attestation and trust-key validation | 🟩 Repository foundation |
| Immutable snapshot receipt and checkpoint binding | 🟩 Repository foundation |
| Safe source-side key file opening and bounded parsing | 🟩 Source implemented; new regression cases added |
| Actual owner-host key custody | 🟥 External proof open |
| Authenticated remote snapshot transfer | 🟥 External proof open |
| Each gateway's persisted receipt retrieval | 🟥 External proof open |
| Restart re-verification and durable per-gateway high-water ACK | 🟥 External proof open |
| Gate 25 parent acceptance | 🟥 OPEN |

No unit test or repository-only callback closes the external owner-host acceptance items.

### 4. Indicator and project progress

No indicator source, test or chart integration changed in this batch. The focused indicator declaration count remains 28 = 21 calculation-engine + 7 shared-hook tests. Backend Gate 25 security tests are tracked separately and must not be added to the indicator count.

| Indicator | Foundation | Chart/UI | Status |
|---|---|---|---|
| SMA20 | 20-close mean; first valid index 19 | Not integrated | 🟨 |
| EMA20 | SMA-seeded, alpha 2/21; first valid index 19 | Not integrated | 🟨 |
| RSI14 Wilder | 14-change seed/recurrence; first valid index 14 | Not integrated | 🟨 |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity | Not integrated | 🟨 |
| Bollinger20,2 | Mean ± 2 population SD | Not integrated | 🟨 |
| Shared Indicator Hook | Keyed immutable snapshot/cache/trust gating/stale clearing | Not integrated | 🟨 |
| Footprint PRO 2GD | Synthetic/offline only | Renderer gated; user refs recorded | 🟧 |
| Volume Profile | Incomplete | Not integrated | 🟥 |
| Complete Volume Profile | Incomplete | Not integrated | 🟥 |
| Movable-range VP | Incomplete | Not integrated | 🟥 |
| Heatmap | Depth/liquidity foundation unverified | Not integrated; reference gate | 🟥 |
| Liquidation Maps | Methodology/provenance unverified | Not integrated | 🟥 |

Footprint OFF keeps ordinary candle spacing; explicit ON alone switches to spaced clusters. Visual implementation remains gated by the formal stage/blueprint/user-review requirements.

| Project meter | Current value | Status |
|---|---:|---|
| Stage 1 | 30/40 = 75% provisional; inherited baseline | 🟨 |
| Stage 2 | Active; no approved denominator | 🟦 NOT SCORED |
| Stage 3 | Not formally scored | ⬜ |
| Stage 4 | Stage gate and reviewed blueprint required | 🟪 |
| Stage 5 | Not formally scored | ⬜ |
| Stage 6 | Not formally scored | ⬜ |
| Gate 10 | 0/10 formally closed | 🟥 |
| Overall project | No approved six-stage weighted denominator | ⚪ NOT SCORED |
| Aggregate indicators | No approved indicator denominator/weights | ⚪ NOT SCORED |
| IP3S | No approved formula applied | ⚪ NOT SCORED |

### 5. Execution controls

- Exact-head CI must run for this correction SHA: Automated Tests, CodeQL, OCI ARM64, Full Git History Secret Audit.
- Poll every run to terminal state; inspect and repair failures.
- No Vercel deployment, no main update, no paid service, no new dependency, no destructive Redis retention, no production credential handling.
- Delivery target remains approximately 24 December 2026 (planning target only).

**Batch result:** three explicit security regression tests added; Gate 25 external acceptance remains open; no indicator or overall project completion score awarded.
