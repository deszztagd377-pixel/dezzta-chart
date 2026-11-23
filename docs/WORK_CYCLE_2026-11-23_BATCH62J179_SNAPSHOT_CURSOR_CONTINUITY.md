# DEZZTA CHART — Batch 62J-179
## Synthetic WebSocket snapshot watermark and live-boundary consistency

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Final code/test HEAD:** `141bf18a644c81be5cdfca39d522b2ed47b00b7b`  
**Snapshot/live implementation commit:** `4813ac1dbe0b7128e5da3909a916dd58696c7bb6`  
**Test-fixture correction commit:** `141bf18a644c81be5cdfca39d522b2ed47b00b7b`  
**Protected `main`:** unchanged at `e3841681bc69b73619058deaf939df82ae5116a1`  
**ZERO COST:** preserved  
**Exact-final-HEAD CI:** all four workflows SUCCESS.

## 1. Defect and impact

The synthetic-only Durable Object previously returned a fixed snapshot watermark of 50 even when the per-series persisted sequence cursor had already advanced. A client authenticating after an event had been emitted could therefore receive a snapshot that omitted that event while claiming watermark 50. Its next live event could appear to skip a cursor.

This was a consistency defect in the isolated synthetic proof. It was not evidence of a production Redis/WebSocket outage.

## 2. Implementation

Files changed:
- `cloudflare/proof/worker.mjs`
- `cloudflare/proof/worker.node-test.mjs`
- `cloudflare/proof/worker.durable-object.runtime.mjs`

Changes:
1. One-time ticket consumption now reads the persisted per-series sequence watermark inside the same storage transaction and returns that watermark with the consumed ticket.
2. Invalid, missing, unsafe, below-snapshot or out-of-range stored watermarks fail closed.
3. Authorized socket attachments accept only safe watermarks in the supported interval.
4. Snapshot construction now accepts a terminal sequence and returns the most recent 50 synthetic bars ending exactly at that sequence.
5. Authentication serializes the authorized attachment and sends the snapshot before the next asynchronous yield. This establishes the local synthetic snapshot/live ordering boundary.
6. The next contiguous update is then accepted and fanned out from watermark + 1.

### Exact regression scenario

`ticket issued → sequence 51 emitted before authentication → client authenticates → snapshot watermark 51 with bars 2..51 → sequence 52 emitted → client receives update 52`

Both Node method-level coverage and the real local workerd Durable Object runtime suite exercise this sequence.

## 3. Test-fixture correction

The first run against implementation commit `4813ac1dbe0b7128e5da3909a916dd58696c7bb6` exposed four older unit-test fixtures that issued or consumed tickets without initializing the per-series cursor. Production ticket issuance already initializes that cursor, but those direct helper tests did not model the route contract.

The test setup was corrected in `141bf18a644c81be5cdfca39d522b2ed47b00b7b` by explicitly initializing the cursor in the affected fixtures. No production logic was weakened and no validation was bypassed.

## 4. Exact-final-HEAD CI

All four workflows passed on final HEAD `141bf18a644c81be5cdfca39d522b2ed47b00b7b`:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45209641510](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45209641510) | SUCCESS |
| CodeQL Security Analysis | [45209641231](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45209641231) | SUCCESS |
| Full Git History Secret Audit | [45209641064](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45209641064) | SUCCESS |
| OCI ARM64 Image Readiness | [45209641157](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45209641157) | SUCCESS |

The Automated Tests workflow passed:
- synthetic Worker Node proof;
- pinned local workerd WebSocket runtime;
- Durable Object hibernation, alarms, per-series isolation and snapshot/live boundary;
- frontend tests/build and secret scans;
- Android host preflight and immutable preview publisher tests;
- backend tests;
- Redis TLS CA/hostname and persistence checks;
- synthetic SQLite outbox and metrics collector benchmarks;
- dependency audits;
- backend container build and shared-Redis/persistent-volume smoke;
- container image scan and vulnerability-report export.

No deployment was performed.

## 5. Remaining WebSocket scope

### Verified locally
- Snapshot watermark is read from the current persisted series cursor at ticket consumption.
- Snapshot's 50 bars end at that watermark.
- The next contiguous live update follows the snapshot.
- Two-client same-series fan-out and cross-series isolation.
- Single-use ticket enforcement, including concurrent consumption race.
- Attachment restoration after Durable Object eviction.
- Unauthenticated socket alarm cleanup.
- Duplicate/gap cursor rejection.
- Failed-send isolation: one failed socket does not prevent a healthy peer from receiving the event.

### Still open
1. **Reconnect replay/resnapshot:** the synthetic DO still has no bounded event replay buffer. A disconnected client must not silently resume from an outdated cursor; define a replay window and explicit resnapshot-required behavior.
2. **Slow-consumer control:** synchronous send failure is isolated, but there is no measured buffered-byte ceiling, bounded queue, or sustained slow-consumer policy.
3. **Production acceptance:** public HTTPS/WSS hostname, reverse proxy/TLS, Firebase token lifecycle, owner-host Redis durability/failover, Android WebView lifecycle/network handover, and cross-instance acceptance remain external.
4. **Data truth:** all Cloudflare proof messages remain synthetic and must never be described as live exchange data.

The production Redis-backed path already has its own cursor/replay/resnapshot protocol and apply-before-ACK consumer semantics. Do not conflate that production path with this isolated Cloudflare proof.

## 6. Indicator progress — unchanged

This batch changes only synthetic WebSocket snapshot/cursor handling. It receives **zero indicator implementation credit**.

| Indicator / subsystem | Status | Foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial mean of 14 changes; Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; first MACD index 25; signal/histogram index 33 | Dedicated pane, lines/histogram/zero guide, toggle, legend/latest values, lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/lifecycle/render/performance |
| Shared Indicator Hook | 🟨 Foundation | Exact-snapshot aligned multi-study output; ready/degraded accepted; demo/error suppressed; immutable revision regression | Chart binding, stale clearing across identity changes, settings/legend, lifecycle/accessibility/performance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask volume | User reference images, reviewed blueprint, verified bid/ask data contract, spaced-cluster renderer/tests |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference images, reviewed blueprint, validated data contract, renderer/tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render/data contract | Defensible methodology/provenance, reviewed blueprint, renderer/tests |

Invariants remain: null warm-up values; source-index alignment; prefix causality/no future repaint; invalid/gapped data is not silently coerced to zero; stale output clears on symbol/venue/dataset/chart/timeframe changes. Footprint OFF retains ordinary candle spacing; explicit ON alone enables spaced clusters. Footprint and Heatmap visuals remain blocked pending user reference images and scoped blueprint review.

Aggregate indicator completion remains **NOT SCORED** because per-study weights and denominator are not approved.

## 7. Project progress dashboard

| Area | Status | Accounting |
|---|---|---|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 75% provisional | 30/40 criteria (300/400 ticks) |
| Stage 2 — Market Data Infrastructure | 🟧 Synthetic proof strengthened; not scored | Snapshot/live boundary now verified locally; replay and production gates open |
| Stage 3 — Chart Engine & Timeframe | ⬜ Not scored | No approved denominator |
| Stage 4 — Indicators & Analytics | 🟨 Foundation states above; aggregate not scored | No indicator implementation delta |
| Stage 5 — Professional UI & Interactive Tools | ⬜ Not scored | No new acceptance evidence |
| Stage 6 — Hardening, Validation & APK Release | ⬜ Not scored | No new device/release acceptance |
| Gate 10 — external acceptance | 🟥 0/10 formally closed | No external gate closed |
| Overall project | **NOT SCORED** | Approved stage weights and denominator unavailable |

Stage 1's provisional 75% is not the overall project percentage.

## 8. Next queue

1. Design and implement bounded reconnect replay plus explicit resnapshot-required behavior in the synthetic proof, aligned with the production protocol without claiming parity prematurely.
2. Define slow-consumer limits and behavior; test bounded memory, send failures, cleanup and healthy-peer isolation.
3. Keep all external production acceptance gates open until direct owner-host/device evidence is captured.

**Target date:** approximately 24 December 2026; planning target only.

**Decision:** Batch 62J-179 is accepted after all four exact-final-HEAD CI workflows passed. Snapshot-to-live cursor continuity is now locally verified for the synthetic proof. Production and indicator completion credit is unchanged.
