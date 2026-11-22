# Work cycle — Batch 62J-127 operator escalation and notification-boundary audit

**Date:** 22 November 2026  
**Branch:** phase-2/market-data-foundation  
**Parent:** b7d0482ff8fa5906c006460583ad3b175f4c282c

## Exact-parent CI

- Automated Tests [44987388625](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987388625): SUCCESS.
- CodeQL [44987388511](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987388511): SUCCESS.
- Full Git History Secret Audit [44987388505](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987388505): SUCCESS.

## Finding 1 — user-facing price-alert FCM path

A distinct user-notification path exists. Owner-scoped FCM registration and fan-out consume durable price-alert trigger events. Device tokens are stored encrypted with AES-256-GCM, bound by owner/installation associated data, and loaded using an owner-injected 32-byte encryption key. The key loader requires an absolute regular file, rejects a final symlink, and denies group/other permissions. Production Firebase Admin initialization uses Application Default Credentials. Fan-out is at-least-once; Android event-ID deduplication is required. Repository code and tests do not prove a live Firebase project, production ADC identity, successful real-device delivery or token revocation/renewal against the owner's project. Gate 20 remains open.

## Finding 2 — operator incident journal and escalation

The operational incident reporter writes sanitized local logs and a persistent SQLite incident journal. The journal deduplicates active fingerprints, bounds its row capacity, prunes resolved records after 30 days, and tracks open/acknowledged/resolved status. Acknowledgement currently uses the generic actor label "operator"; it does not capture a verified individual identity. A background loop calls escalate_due every 15 seconds and advances up to three escalation levels, but its output is only a structured local log event. There is no operator email/SMS/FCM/webhook/paging sender wired to this escalation path. Therefore escalation state is implemented; external escalation delivery is not.

Internal list/acknowledge/resolve endpoints are protected by an injected bearer token. This is an API surface, not a graphical operator dashboard, individual attribution, external alert delivery or a completed response drill.

## Finding 3 — observability scope

The internal metrics endpoint exposes process-local HTTP/WebSocket counters and may additionally return a same-host SQLite collector aggregation. The collector is bounded, uses 15-minute buckets and 7-day retention, and is best-effort local telemetry. The alert-delivery status endpoint explicitly declares process_local_since_start. No evidence of a central dashboard, independent off-host metrics retention, external monitoring sink, disk-pressure paging or cross-host operational visibility was established. Gate 38 remains open.

## Gate disposition

- Gate 8: owner-host secret injection, permissions, rotation and redaction still require acceptance.
- Gate 20: real Firebase project validation, revoked/expired/wrong-project token and entitlement E2E still required.
- Gate 38: owner-host retained dashboard/monitoring and disk-pressure/restart behavior still required.
- Gate 39: external operator alert delivery, verified recipient, human acknowledgement, escalation receipt and response drill still required.
- Gate 25 and 36 remain open as recorded in prior WebSocket audits.
- Gate 10 remains **0/10 formally closed**; Stage 1 remains **30/40 = 75% provisional**. Stage 2 remains blocked.

## Indicator progress — complete status reconciliation

No implementation changed. SMA20, EMA20, RSI14 Wilder, MACD12/26/9 and Bollinger20,2 remain 🟨 foundation with previously recorded calculation/warm-up rules. Shared Indicator Hook remains 🟨 foundation and is not chart-integrated. Footprint remains 🟧 synthetic educational accumulator only; do not begin visual implementation until the user supplies the reference image and the blueprint is reviewed. Heatmap and Liquidation Maps remain 🟥 unimplemented. No aggregate indicator percentage and no progress credit from documentation/CI. Preserve candle-index alignment, warm-up nulls, no future-candle repaint, stale-series clearing, and normal candlestick spacing whenever Footprint is OFF.

## Cost and change boundary

Documentation-only, ZERO COST. No runtime changes, tests, workflows, cloud services, accounts, domains, deployments, production credentials or device actions. main untouched.
