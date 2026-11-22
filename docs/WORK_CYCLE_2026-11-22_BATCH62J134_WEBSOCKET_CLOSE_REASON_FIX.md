# Batch 62J-134 — WebSocket close-reason accuracy fix
Date: 22 November 2026
Branch: `phase-2/market-data-foundation`
Source/test commit: `ecf7decb8e823effe09a6be8a9973bb98619ae92`

## Finding
Backend `/ws/market-data` emits close code 4403 for both an Origin allowlist rejection (`Origin not allowed`) and series/instrument entitlement denial (e.g. `Instrument access denied`, `Instrument access revoked`). The client supervisor previously mapped all 4403 closes to entitlement denial. This caused a misleading user-facing diagnosis when frontend Origin configuration was the actual cause.

## Change
`src/services/ohlcvStreamSupervisor.ts` now uses the close reason to distinguish:
- Origin allowlist failure → explicit Origin configuration diagnostic.
- Other 4403 reasons → entitlement denial/revocation diagnostic.

Both cases remain terminal; the supervisor does not retry unchanged rejected sessions.

`src/services/ohlcvStreamSupervisor.test.ts` now asserts both cases, the displayed diagnostic, error reporting and absence of reconnect. No authentication, authorization or policy enforcement was relaxed.

## CI
- Automated Tests [44991640588](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640588): IN PROGRESS at time of report; frontend unit tests/build and Redis TLS fixture passed; backend tests still running.
- CodeQL [44991640593](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640593): SUCCESS, JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44991640577](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640577): SUCCESS.
- Zero-cost Android debug APK [44991640574](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640574): IN PROGRESS; APK assembly not yet complete.

Regression tests remain unaccepted until Automated Tests succeeds. No APK success/artifact claimed.

## Remaining gates
- Gate 25 OPEN: immutable snapshot digest/provenance receipt, owner-authenticated transfer and owner-host Redis acceptance.
- Gate 36 OPEN: public WSS/reverse proxy/certificate, live Firebase, production browser and Android WebView lifecycle/network-handover.
- Gate 38 OPEN: owner-host metrics persistence, disk pressure/restart/backup/retention and operator acceptance.

## Indicator ledger
No indicator runtime/test source changed. SMA20 🟨 first index 19; EMA20 🟨 SMA-seeded alpha 2/21 first index 19; RSI14 Wilder 🟨 first index 14; MACD12/26/9 🟨 MACD index 25 and signal/histogram index 33; Bollinger20,2 🟨 first index 19; Shared Indicator Hook 🟨 backend-only alignment foundation; Footprint 🟧 synthetic accumulator only; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. Footprint/Heatmap visuals remain gated on user reference images and reviewed blueprint.

## Project indicator
Stage 1: 30/40 = 75% provisional. Stages 2–6: NOT SCORED. Gate 10: 0/10 formally closed. Overall project: NOT SCORED pending approved stage weights and denominator.

## IP3S
Batch 62J-134: **PENDING CI**. No score awarded before the exact-commit Automated Tests result. ZERO COST; no deployment, paid services, production credentials, device/Termux or `main` changes.
