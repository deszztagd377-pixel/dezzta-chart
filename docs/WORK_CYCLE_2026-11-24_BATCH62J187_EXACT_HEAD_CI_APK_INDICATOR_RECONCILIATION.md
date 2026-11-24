# DEZZTA CHART — Batch 62J-187
## Exact-HEAD CI, Android debug APK and progress reconciliation

**Audit date:** 24 November 2026 (Asia/Jakarta)  
**Branch:** `phase-2/market-data-foundation`  
**Verified HEAD:** `1b3f39ea8f3a6cfd56425fc799b58ee8e0d0991b`  
**Protected main:** unchanged at audit time (`e3841681bc69b73619058deaf939df82ae5116a1`).  
**Cost:** ZERO COST; GitHub Actions only.

## 1. Latest commit audit

HEAD is one commit ahead of the preceding checkpoint. Commit `1b3f39ea8f3a6cfd56425fc799b58ee8e0d0991b`, message `security: override vulnerable Miniflare undici dependency`, changes only `package.json` (4 additions, 1 deletion). It adds a scoped npm override pinning Miniflare's `undici` resolution to `7.30.1`. No market-data, WebSocket, indicator, renderer, or Android runtime source changed.

## 2. Exact-HEAD CI — five of five SUCCESS

All five workflows target the exact same HEAD:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45215527228](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215527228) | 🟢 SUCCESS |
| CodeQL | [45215526929](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215526929) | 🟢 SUCCESS |
| OCI ARM64 Image Readiness | [45215526908](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215526908) | 🟢 SUCCESS |
| Android APK Build | [45215527101](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215527101) | 🟢 SUCCESS |
| Full Git History Secret Audit | [45215526995](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215526995) | 🟢 SUCCESS |

The Automated Tests job completed successfully, including frontend dependency-audit enforcement. Do not infer test counts beyond the published job evidence.

## 3. Android APK artifact

The zero-cost CI workflow built the web app, generated a temporary Capacitor 7 Android wrapper, assembled a debug APK, verified its file type and SHA-256, and uploaded the artifact.

- Artifact: `dezzta-chart-android-debug-apk`
- Artifact ID: `14838496390`
- Run: [45215527101](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215527101)
- [Open APK artifact](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215527101/artifacts/14838496390)
- Uploaded ZIP size: 3,879,940 bytes
- APK SHA-256: `978da27dedc506a7b3060d89deef4639d6b3dc19862628e3fa86324a998295a1`
- ZIP SHA-256: `01ee90d46cbd4b9f42f44d85d6fab7b6413f6b5b5cf80dc487d577b4c20deb78`

This is a CI-built **debug** APK, not a release-signed APK or Play Store publication. Real-device installation, authentication, foreground/background, reconnect, network handover and public WSS remain unverified. Artifact retention is finite.

## 4. WebSocket and indicator reconciliation

No production WebSocket or indicator runtime code changed in `1b3f39e`.

WebSocket: existing Redis replay has bounded event/scan limits, exact-series filtering, cursor-gap/retention detection and fail-closed resnapshot. Subscriber queues are bounded (capacity 256) and per-subscriber isolated. Durable Object concurrency/lifecycle suite reached 10/10 in prior exact-head CI. Synthetic Worker/DO tests do not prove public WSS, production Firebase ticket authority, production host deployment, or upstream provider-demand pooling.

Indicator regression evidence:
- Batch 62J-185: hook trust-boundary transitions; ready/degraded backend accepted, demo/error suppressed and stale values cleared.
- Batch 62J-186: immutable snapshot revision causes rolling SMA recalculation after a validated live bar.
- Prior frontend exact-head run: 315/315 across 34 files.
- No formula, chart renderer, pane, legend, toggle or visible settings changed.

## 5. Complete indicator progress

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19; revision regression | Chart overlay, toggle, legend/value, lifecycle/render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first index 19 | Overlay, toggle, legend/value, lifecycle/render/performance |
| RSI14 Wilder | 🟨 Foundation | 14-change seed + Wilder recurrence; first index 14 | 0–100 pane, 30/70 guides, toggle, legend/value, render/lifecycle |
| MACD12/26/9 | 🟨 Foundation | MACD first index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle/legend/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first index 19 | Three-line overlay, toggle, values, lifecycle/render/performance |
| Shared Indicator Hook | 🟨 Foundation | Exact backend snapshot, aligned output, trust/revision regressions | Chart binding, identity stale clearing, settings/legend, accessibility/performance |
| Footprint | 🟧 Synthetic prototype | Educational synthetic accumulator only; not exchange-native bid/ask | Owner reference image(s), reviewed blueprint, valid bid/ask source, spaced cluster renderer |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | Owner reference image(s), validated depth contract, reviewed blueprint and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render | Defensible provenance/methodology, blueprint, renderer and tests |

No aggregate indicator percentage is awarded; approved weights/denominator do not exist. Preserve warm-up nulls, exact candle alignment, prefix causality/no future repaint, invalid/gapped-input rejection and stale-output clearing on identity changes. Footprint OFF keeps standard candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visual work remains gated on owner references and reviewed blueprint.

## 6. Stage and overall progress

| Stage | Verified status |
|---|---:|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional 🟨 |
| 2. Market Data Infrastructure | Not scored / not officially opened ⬜ |
| 3. Chart Engine & Timeframe | Not scored ⬜ |
| 4. Indicators & Analytics | Not scored ⬜ |
| 5. Professional UI & Interactive Tools | Not scored ⬜ |
| 6. Hardening, Validation & APK Release | Not scored ⬜ |

**Overall project: NOT SCORED.** No approved weighted denominator exists. Gate 10: **0/10 external criteria formally closed**. Open external acceptance includes owner-host/public WSS, real Firebase identity/ticket exchange, production Redis persistence/receipt custody, Android device/network handover, provider entitlements and production source identity.

## 7. Blocking work order

1. Recurring-zero-cost market-data entitlement: unresolved; verify CME/instrument coverage, redistribution rights, API semantics and recurring-$0 cost before enabling a provider.
2. Provider demand pooling: unresolved end-to-end; do not add a disconnected reference counter.
3. Public WSS/owner-host: unresolved; CI synthetic Worker/OCI is not deployment or endpoint acceptance.
4. Android device acceptance: debug APK exists, but real-device install and lifecycle/network tests remain outstanding.
5. Indicator visible integration: calculations/hooks exist; panes, overlays, settings and legends remain incomplete.
6. Footprint/Heatmap: obtain owner reference images, then review blueprint and source contract before visuals.
7. Liquidation Maps: establish provenance and calculation methodology first.

Delivery target remains **24 December 2026**, a planning target, not a guarantee. ZERO COST remains mandatory. No paid provider/hosting, cloud account, publication fee, or main-branch modification was introduced.

## 8. Outcome

- Reconciled latest source HEAD and exact-HEAD CI.
- Verified five successful workflows.
- Verified debug APK artifact and checksums.
- Updated indicator and stage accounting without inflating implementation credit.
- Preserved the distinction between CI proof and external production/device acceptance.

Next: continue source-backed WebSocket/provider-demand and Android acceptance work without duplicating replay/queue logic or adding paid dependencies.
