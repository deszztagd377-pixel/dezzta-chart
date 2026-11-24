# DEZZTA CHART — Batch 62J-228



---

## Batch 62J-228 — WebSocket color taxonomy and parent-gate roll-up correction (24 November 2026)

**Audited HEAD:** `f3ca6becff4d72ba1638e4cf0233366f5d3368bb`  
**Branch:** `phase-2/market-data-foundation`  
**Exact-HEAD CI:** 4/4 terminal SUCCESS  
**Scope:** status semantics and acceptance accounting; no runtime source changed  
**Cost:** ZERO COST • `main` untouched • Vercel deployment deferred

### Why a WebSocket sub-status can be yellow/green while the overall gate is red

There was no demonstrated code regression between the previous yellow/partial indication and the red end-to-end gate indication. The colors had been used at different scopes without a clear legend. A repository-side capability can be green or yellow while the parent production-acceptance gate remains red because external proof is still missing. These are separate dimensions, not a downgrade of the same test result.

The following color legend is now authoritative for new progress entries:

| Color | Meaning | What it does not mean |
|---|---|---|
| 🟩 Green | The named criterion is implemented and verified at the stated scope, with evidence | Does not automatically close its parent production gate |
| 🟨 Yellow | Partial foundation or repository-side capability exists; additional integration/acceptance remains | Does not mean production acceptance is complete |
| 🟧 Orange | Gated or blocked on a prerequisite, owner input, reference, or safety condition | Does not imply a code failure |
| 🟥 Red | The named acceptance criterion or parent end-to-end gate remains unmet/open | Does not mean already-green repository tests regressed |
| 🟦 Blue | Active work or CI currently running | Not a pass/fail result |
| 🟪 Purple | Stage/blueprint gate prevents implementation from starting | Not a defect report |
| ⬜ Grey | Not started / not yet assessed | Not evidence of failure |
| ⚪ Neutral | No approved denominator or score | Never convert to a guessed percentage |

### Canonical WebSocket roll-up at this HEAD

| Scope | Current status | Evidence / remaining acceptance |
|---|---|---|
| Browser protocol, ticket/authentication, replay and reconnect foundations | 🟩 Repository-verified | Existing source and exact-HEAD CI coverage |
| Redis replica, replay, recovery and consumer lifecycle foundations | 🟩 Repository-verified | Existing backend suites and synthetic Redis fixtures |
| Gate 25 owner-pinned Ed25519 verification, immutable receipt re-verification, source/key binding and fail-before-Redis | 🟩 Repository-verified | Batch 62J-221 source/test contract and exact-HEAD CI |
| Gate 25 owner-host private-key custody, authenticated remote transfer, each gateway's persisted receipt retrieval, restart re-verification and per-gateway durable high-water ACK | 🟥 External acceptance open | Requires actual owner-controlled host/gateway evidence; repository callback tests cannot prove remote custody or network authentication |
| Gate 25 parent acceptance | 🟥 OPEN | Parent gate closes only after all required external owner-host evidence is accepted |
| Gate 36 public HTTPS/WSS, reverse proxy/TLS, production runtime and physical Android lifecycle | 🟥 OPEN | Requires public endpoint and real deployment/device evidence |
| Firebase production sign-in, entitlement and revocation E2E | 🟥 OPEN | Requires owner-controlled Firebase project evidence |
| Browser/Android process-death, network handover, production multi-instance failover | 🟨/🟥 PARTIAL / OPEN | Repository foundations exist; deployed browser and real-device/host acceptance incomplete |
| Redis destructive retention | 🟧 BLOCKED | No XTRIM/XDEL/group destruction until gateway inventory/retirement, PEL policy, per-gateway floor ACK, separate authority and crash-safe trim/reconcile are proven |
| Whole WebSocket production end-to-end | 🟥 NOT COMPLETE | Parent status is determined by outstanding external acceptance, not the green repository rows |

**Important:** A green sub-row does not make Gate 25 or the complete WebSocket green. Likewise, a red parent gate does not invalidate a previously successful unit test or CI run. Future dashboards must show the scope next to every colored status.

### Exact-HEAD CI read-back

At `f3ca6becff4d72ba1638e4cf0233366f5d3368bb`, all configured workflows are terminal SUCCESS, with every reported job step completed and no failed steps:

- Automated Tests: [45428878737](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428878737) — 41/41 steps.
- Full Git History Secret Audit: [45428878666](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428878666) — 6/6 steps.
- CodeQL: [45428879181](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428879181) — JavaScript/TypeScript 8/8 and Python 8/8.
- OCI ARM64: [45428878741](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428878741) — 7/7 steps.

This 4/4 result applies to this exact HEAD only. It is repository CI, not external production acceptance.

### Indicator progress reconciliation — no score inflation

| Indicator / subsystem | Current evidence | Chart/UI state | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay/toggle/legend/latest value/lifecycle absent | 🟨 Foundation |
| EMA20 | SMA-seeded EMA, alpha 2/21; first valid index 19 | Overlay/toggle/legend/latest value/lifecycle absent | 🟨 Foundation |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | Pane and 30/70 guides absent | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; first MACD index 25, signal/histogram index 33 | Pane/lines/histogram/zero guide absent | 🟨 Foundation |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Three-line overlay/fill/toggle/latest values absent | 🟨 Foundation |
| Shared Indicator Hook | Keyed immutable snapshot, shared cache, trust gating, stale-output clearing | Not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Renderer gated; two user reference images on record | 🟧 Gated |
| Volume Profile / Complete VP / movable-range VP | No complete production implementation verified | Not integrated | 🟥 Open |
| Heatmap | Depth/liquidity engine and accepted renderer not verified | Visual implementation remains gated; user reference/data contract outstanding | 🟥 Open |
| Liquidation Maps | Methodology/provenance and renderer not accepted | Not integrated | 🟥 Open |

Focused test declaration inventory remains **28 total = 21 calculation tests + 7 shared-hook tests**. This is not a count of completed indicators or a completion percentage. All 28 are declarations in the two focused test files; exact-HEAD CI is the pass/fail authority. Older 24-count notes are historical source snapshots, not current inventory.

Footprint OFF must retain standard candle spacing; explicit ON alone enables the spaced-cluster layout. Footprint/Heatmap visual work and major chart integration remain behind the required stage/blueprint/user-review gates. Aggregate indicator progress stays NOT SCORED.

### Project progress dashboard — unchanged scores

| Meter | Current value | Status |
|---|---:|---|
| Stage 1 Foundation | 30/40 = 75% provisional; inherited baseline, not independently re-audited in this cycle | 🟨 |
| Stage 2 Market Data Infrastructure | Active; denominator not approved | 🟦 NOT SCORED |
| Stage 3 Chart Engine & Timeframe | Not formally scored | ⬜ NOT SCORED |
| Stage 4 Indicators & Analytics | Stage gate / blueprint required | 🟪 NOT SCORED |
| Stage 5 Professional UI & Interactive Tools | Not formally scored | ⬜ NOT SCORED |
| Stage 6 Hardening, Validation & APK Release | Not formally scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicator completion | No approved denominator/weights | ⚪ NOT SCORED |
| IP3S / significant progress | No approved formula applied | ⚪ NOT SCORED |

No stage tick, indicator integration credit, Gate 25 external acceptance, or overall percentage is awarded by this documentation/status correction.

### Work order remains unchanged

1. Continue repository-verifiable work and exact-HEAD CI.
2. Close Gate 25 with actual owner-host authenticated transfer, persisted receipt retrieval, restart verification and durable high-water ACK from every gateway.
3. Close public WSS/TLS and Firebase production E2E.
4. Complete browser/Android lifecycle and production multi-instance recovery.
5. Consider Redis destructive retention only after all independent safety prerequisites pass.
6. Keep indicator chart UI behind Stage 4 and its scoped approved blueprint/user review.

No paid service, production credential, domain, deployment, or destructive Redis action was used. APK planning target remains approximately 24 December 2026, not end-of-month.
