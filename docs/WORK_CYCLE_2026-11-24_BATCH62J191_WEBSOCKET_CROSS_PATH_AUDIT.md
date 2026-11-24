# Work cycle — 24 November 2026 — Batch 62J-191: WebSocket replay and reconnect cross-path audit

**Branch:** `phase-2/market-data-foundation`  
**Audit base:** `13d39aa1d51f7e86ccbc4c64d557f489671f26ee` (documentation HEAD)  
**Latest source/test baseline:** `8606cb460f641b0b831081aeed8aae6a6149c91d`  
**ZERO COST:** maintained. No paid provider, hosting, deployment, production account, credentials, or device operation. Protected `main` unchanged.

## 1. Scope and method

Read-only cross-path audit of the existing WebSocket client, supervisor, backend replay reader, Redis replica replay, stream hub, replica bridge, and their focused tests. This batch deliberately does not modify runtime source: the available evidence supports existing behavior, but does not yet establish a safe new code defect. No speculative patch is accepted.

## 2. Verified coverage inventory

| Layer | Existing regression coverage observed | Assessment |
|---|---|---|
| WebSocket client | Authentication/subscribe, replay-before-live, server-directed resnapshot, replacement cursor equality, missing/malformed cursor rejection, sequence-gap rejection, heartbeat timeout, ticket renewal, observer exceptions and transport cleanup | Strong focused coverage |
| Client supervisor | Resume after transport reconnect, stale-cursor clearing after resnapshot, fresh snapshot watermark adoption, sequence-gap recovery, token/ticket retry bounds, auth/policy terminal failures, close/error race deduplication, cancellation on stop/supersession, late callback suppression | Strong lifecycle coverage |
| Redis replay page | Global cursor advance across unrelated series, first/middle gap rejection, history ending before watermark, identity mismatch, empty interval, bounded page scan | Strong cursor-integrity coverage |
| Replica replay | Fixed checkpoint watermark, sparse-series global scan, expired/ahead cursor resnapshot, no partial event return on event cap, scan cap, empty interval validation | Strong bounded-replay coverage |
| Stream hub / bridge | Exact series identity routing, durable cursor publication, snapshot cursor separated from advancing live cursor, atomic replica snapshot registration, duplicate-safe fanout | Source behavior inspected; full end-to-end production path remains external acceptance |

## 3. Cross-path invariants

1. The replay upper watermark is fixed from the replica checkpoint; it must not drift while pages are scanned.
2. Global cursors advance across unrelated series, while returned events remain filtered to the exact canonical series identity.
3. Missing, trimmed, malformed, or discontinuous Redis history fails closed and requests resnapshot; partial replay is not reported as success.
4. The subscription snapshot cursor is immutable. Live durable cursor advancement must not rewrite the snapshot boundary.
5. A server-directed resnapshot invalidates the client's old resume cursor. Reconnect must request a full snapshot and adopt only its validated cursor.
6. Replay events are applied before the stream transitions to live updates; sequence gaps are never silently skipped.
7. Queue overflow and inability to establish a consistent replay/live handoff must recover by resnapshot, not by silently dropping data.
8. Exact provider/dataset/publisher/instrument/series/timeframe/bucket/calendar identity remains part of routing and validation.

## 4. Findings and remaining proof gaps

**No confirmed new runtime defect found in this read-only batch.** The reviewed implementation and named regression tests cover the principal replay/reconnect failure modes.

The following remain acceptance gaps rather than proven defects:
- No real Redis deployment/failover or retention-trimming acceptance was executed in this session.
- No owner-operated authenticated snapshot transfer, public WSS endpoint, or multi-instance production handoff was exercised.
- No physical Android/browser background-resume test was performed.
- The repository test suite is CI evidence; it is not a substitute for external host/provider acceptance.

Candidate additions for the next focused test batch (must be implemented and run before claiming coverage):
- Retention-floor boundary table: `after_cursor == retention_floor`, one below, and one above.
- Malformed checkpoint matrix: bool-as-int, negative values, missing fields, and floor greater than applied watermark.
- Redis page boundary matrix: exactly `scan_limit`, one over the cap across multiple pages, and a trimmed range between pages.
- Replay/live interleaving: publish immediately before and after the atomic snapshot+subscription boundary and prove exactly-once cursor delivery.
- Subscriber queue saturation during replay handoff: prove deterministic resnapshot/disconnect and no silent event loss.
- Two simultaneous subscribers with distinct canonical identities: prove no cross-series delivery during reconnect.

These are explicitly marked as proposed coverage, not completed tests.

## 5. Verification state

The latest source/test baseline `8606cb460f641b0b831081aeed8aae6a6149c91d` had five exact-HEAD CI workflows SUCCESS:
- Automated Tests: [45304034616](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034616)
- CodeQL: [45304034690](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034690)
- OCI ARM64: [45304034703](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034703)
- Full Git History Secret Audit: [45304034693](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034693)
- Android debug APK build: [45304034582](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45304034582)

The documentation-only HEAD `13d39aa1d51f7e86ccbc4c64d557f489671f26ee` also has four observed workflows SUCCESS (Automated Tests, CodeQL, OCI ARM64, Secret Audit). Android APK workflow is not required for this documentation-only update; no new APK is requested or needed.

## 6. Project and indicator accounting

- Stage 1: 30/40 acceptance criteria = 75% provisional; no new criteria closed by this audit.
- Stages 2–6: not scored.
- Gate 10: 0/10 formally closed.
- Overall project: NOT SCORED; approved weighted denominator unavailable.
- Indicator implementation credit: zero for this batch. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 Foundation; Footprint 🟧 synthetic prototype only; Heatmap and Liquidation Maps 🟥 not implemented.
- Indicator aggregate: NOT SCORED.
- Footprint OFF preserves normal candle spacing; explicit ON alone enables spaced clusters.
- Footprint/Heatmap visual implementation remains gated on owner reference images and scoped blueprint review.
- Delivery target: 24 December 2026, planning target only.

## 7. Next work order

Batch 62J-192 should implement the highest-value deterministic test gaps, beginning with replay/live snapshot-boundary interleaving and exact retention-floor semantics. Source changes must be narrowly scoped, preserve current behavior, pass focused tests, then pass full exact-HEAD CI before being marked green.
