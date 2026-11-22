# Work cycle — Batch 62J-125 WebSocket acceptance evidence mapping

**Date:** 22 November 2026  
**Branch:** phase-2/market-data-foundation  
**Baseline commit:** 4cb91f518b14cff2b6d7ee1af3c53ed836dd6b5d

## Summary

Completed a focused read-only source/test audit of WebSocket authentication, ticket issuance/consumption, Origin policy, entitlement rechecks, snapshot installation, replay, browser reconnect and CI scope. All three workflows for the baseline documentation commit are green.

## Confirmed repository evidence

1. **Ticket lifecycle:** Redis-backed ticket record is digest-keyed; stored value binds verified account subject and purpose; TTL is 90 seconds; create-only write uses NX; Lua GET+DEL consumes atomically. Unit, Redis integration and multi-process tests cover single-use behavior and account lease coordination.
2. **Ticket endpoint and handshake:** HTTPS endpoint requires verified Firebase principal. WebSocket handshake checks non-empty Origin against allowlist, consumes the one-time ticket, and then performs separate exact series/canonical-instrument entitlement checks.
3. **Identity:** Firebase verifier calls revocation checking and validates identity claims. Tests use verifier test doubles, not a real Firebase project.
4. **Snapshot bootstrap:** Gateway installs snapshot before creating Redis client; it compares source ID, generation ID, high-water cursor, digest format and durable checkpoint. Source mismatch and incomplete install fail before Redis client construction. Authenticated remote transfer and independent gateway receipt authenticity are still owner-supplied boundaries.
5. **Replay:** Global cursor scan across unrelated series, fixed watermark, retention gap/cursor-ahead rejection, bounded replay scan/event limits, and resnapshot fallback are covered by repository tests.
6. **Browser client:** Tests cover authentication, exact subscription, snapshot/update, durable replay ordering, renewal acknowledgement, heartbeat, close cleanup, reconnect and resnapshot recovery. Tests use simulated socket instances.
7. **Server runtime:** Source checks Origin allowlist, rechecks entitlement periodically and renews shared Redis connection lease. Redis outage/lease renewal failure close the socket fail-closed.
8. **Android:** Current CI Android checks are host preflight and preview publisher contract tests, not real-device or WebView lifecycle tests.

## Remaining production evidence

- Gate 25: owner-operated authenticated snapshot transfer, independent per-gateway receipt authentication/custody, exact snapshot bytes/hash/generation/high-water proof, Redis persistence/restart/failover.
- Gate 36: public HTTPS ticket exchange and WSS reverse proxy with verified TLS, real Firebase project and entitlement end-to-end, real browser and Android WebView lifecycle/reconnect/network handover, replay/resnapshot/duplicate suppression, production telemetry and operator evidence.
- Other Stage 1 owner-host gates remain open: secret lifecycle, database restore, encrypted off-host backup/key custody, persistent volume and disk-pressure, monitoring/alert delivery and human acknowledgement.

**Status remains Gate 10 = 0/10 formally closed; Stage 1 = 30/40 provisional.** No production acceptance is claimed.

## Indicator progress

No indicator source/tests changed. The six foundational studies/shared hook remain foundation; Footprint remains reference/blueprint gated; Heatmap and Liquidation Maps remain unimplemented. No percentage increase is credited. Requirements on warm-up nulls, alignment, no repaint, stale clearing and Footprint OFF layout remain intact.

## Files changed

- docs/WEBSOCKET_PRODUCTION_WIRING_AUDIT.md
- docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md
- docs/INDICATOR_PROGRESS_LEDGER.md
- docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md
- docs/WORK_CYCLE_2026-11-22_BATCH62J125_WEBSOCKET_ACCEPTANCE_EVIDENCE.md (new)

No runtime code, tests, workflows, deployment, credentials, paid services or resources changed. main remains untouched. ZERO COST.

## Next safe work

Continue read-only inspection of backup/restore and monitoring gates, then review ARM64 build feasibility. Do not provision a public host or request secrets; production evidence must come from the authorized account/host owner.
