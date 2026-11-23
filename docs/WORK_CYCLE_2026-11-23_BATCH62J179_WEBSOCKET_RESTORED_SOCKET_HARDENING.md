# Work Cycle Batch 62J-179 — WebSocket restored-socket validation and fan-out hardening

**Date:** 23 November 2026  
**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Previous checkpoint:** `70705cb1ce425cc6f6ed6279323e786a201c6826`  
**Worker change:** `90a9a05cd5a9b105608ebba27f0d80b1ed3efa3e`  
**Test change:** `253faf401a03e6441a3842f1403aae82835d8118`  
**Main:** untouched  
**Cost policy:** ZERO COST; no paid runtime, no hosted deployment, no public WSS.

## 1. Audit findings

The previous batch introduced a 15-second unauthenticated WebSocket deadline using one Durable Object alarm. A follow-up source review identified two defensive gaps:

1. During Durable Object construction after hibernation, malformed restored attachment state was closed without a try/catch. A socket already transitioning to CLOSED could throw from `close()` and interrupt object initialization.
2. The synthetic fan-out loop trusted the `authorized` and `seriesKey` fields before validating the complete serialized attachment. A malformed attachment should never be treated as an authorized recipient, even if its partial fields look plausible.

These are defensive lifecycle and authorization-state validation gaps, not evidence of an observed production exploit.

## 2. Implementation

### Worker changes — `cloudflare/proof/worker.mjs`

- Constructor restoration now catches close errors for malformed/closed sockets, allowing the Durable Object to continue restoring other valid connections.
- Every socket in the synthetic fan-out path is revalidated with the complete `isValidSocketAttachment` contract before recipient selection.
- Invalid attachment sockets are closed with 4401 where possible and skipped.
- Send failures attempt a 1011 close defensively; a close failure no longer escapes the fan-out loop.
- Valid recipients still require both a valid authorized attachment and exact series-key equality.
- Sequence acceptance remains contiguous and transaction guarded.

### Test changes — `cloudflare/proof/worker.node-test.mjs`

Two regression tests were added:
- Constructor initialization survives a malformed restored socket whose close operation throws, while preserving a valid socket.
- Fan-out skips malformed authorization attachments and sends only to the valid same-series socket.

The synthetic Node test file now declares **25 test cases** (23 before this batch + 2 additions). This is a test-definition count only; it is not a claim that the tests have executed or passed.

## 3. Runtime contract review

Official Cloudflare Durable Objects documentation confirms:
- A Durable Object has one alarm at a time; multiple deadlines must be coordinated by tracking the earliest one and scheduling the next after processing.
- Alarm handlers are at-least-once and should be idempotent.
- Hibernatable WebSockets remain connected through eviction, and serialized attachments are the supported mechanism for restoring per-connection state.
- `getWebSockets()` can include sockets in CLOSING state, so defensive close handling is appropriate.

The current implementation does not set alarms from the constructor; the alarm is created on connection acceptance and is recomputed on authorization transitions. This avoids constructor-side alarm replacement during hibernation restoration.

## 4. Acceptance boundary

| Check | Status |
|---|---|
| Source edits committed to active branch | 🟩 Done |
| Regression test definitions added | 🟩 Done |
| Test execution on current branch head | 🟨 Not verified in this work cycle |
| GitHub CI exact-head result | 🟨 No status/check record returned by available connector |
| Wrangler/Miniflare runtime smoke | 🟥 Not run |
| Real WebSocketPair handshake | 🟥 Not run in runtime |
| Runtime hibernation/eviction verification | 🟥 Not run |
| Public deployment / production WSS | ⬛ Explicitly out of scope |
| Live provider / broker / exchange integration | ⬛ Explicitly out of scope |

The Node test doubles are not equivalent to a real Cloudflare runtime. No deployment or paid service is required or authorized for this batch.

## 5. WebSocket queue

1. Run the pinned local Wrangler/Miniflare runtime smoke without deploying.
2. Verify a real local WebSocketPair handshake and one-time ticket consumption.
3. Verify same-series fan-out and cross-series isolation in the actual runtime.
4. Verify hibernation/eviction and attachment restoration.
5. Verify alarm deadline expiry and close-code behavior in runtime.
6. Test slow-consumer/backpressure only against documented APIs and observable runtime behavior.
7. Prove snapshot watermark to first live sequence continuity and bounded replay semantics.
8. Keep production authentication, public WSS and Android lifecycle as separate external acceptance gates.

## 6. Full indicator progress ledger

| Indicator | Status | Mathematical / implementation foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Chart overlay, toggle, legend/latest value, lifecycle/render/performance |
| EMA20 | 🟨 Foundation | SMA seed; alpha = 2/21; first valid index 19 | Chart overlay, toggle, legend/latest value, lifecycle/render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial average of 14 close changes; Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle and latest-value display |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero line and legend |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, latest values, lifecycle/render/performance |
| Shared Indicator Hook | 🟨 Foundation | Exact-snapshot aligned multi-study output | Hook tests, chart binding, stale-output clearing, settings/legend integration |
| Footprint | 🟧 Synthetic prototype only | No user-approved visual implementation | User reference image(s), scoped blueprint review, verified synthetic data contract and renderer |
| Heatmap | 🟥 Not implemented | No accepted implementation baseline | User reference image(s), scoped blueprint review, data contract and renderer |
| Liquidation Maps | 🟥 Not implemented | No accepted methodology/provenance baseline | Define safe synthetic visualization methodology, blueprint, data contract and renderer |

### Indicator invariants

- Warm-up outputs remain `null`; no zero-fill.
- Output index alignment must exactly match the candle snapshot.
- Prefix causality must hold: appending future candles cannot alter earlier outputs.
- No future-candle leakage or repainting.
- Invalid, duplicate or gapped input must be rejected or explicitly classified; never silently repaired with fabricated values.
- Clear stale output whenever symbol/venue/dataset/chart identity/timeframe changes.
- Calculation, rendering, interaction, lifecycle, accessibility and performance are separate acceptance dimensions.
- Footprint OFF must preserve standard candle spacing; Footprint ON alone may switch to the dedicated spaced-cluster layout.
- Footprint and Heatmap visual work remains blocked until the user supplies reference images and reviews the scoped blueprint.

No indicator completion percentage is inferred from the WebSocket changes. Indicator aggregate remains **NOT SCORED**.

## 7. Project dashboard

| Stage / gate | Status | Evidence |
|---|---|---|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 **30/40 = 75% provisional** | Existing scored foundation; unchanged |
| Stage 2 — Market Data Infrastructure | 🟦 **Synthetic proof increment; NOT SCORED** | Local runtime acceptance still outstanding |
| Stage 3 — Chart Engine & Timeframe | ⬜ **NOT SCORED** | No new acceptance evidence |
| Stage 4 — Indicators & Analytics | ⬜ **NOT SCORED** | Indicator ledger remains foundation/prototype/not implemented |
| Stage 5 — Professional UI & Interactive Tools | ⬜ **NOT SCORED** | No new acceptance evidence |
| Stage 6 — Hardening, Validation & APK Release | ⬜ **NOT SCORED** | Runtime, device and release gates remain |
| Gate 10 — External acceptance | 🟥 **0/10 formally closed** | No owner-accepted external evidence |
| Gate 25 — Snapshot/replica custody | 🟧 **OPEN** | Replay/custody verification outstanding |
| Gate 36 — Public WSS/Firebase/Android lifecycle | 🟥 **OPEN** | External integration not part of synthetic proof |
| Gate 38 — Owner-host telemetry persistence/restore/operations | 🟧 **OPEN** | Operational acceptance outstanding |
| Gate 39 — Operational alert acknowledgement/recovery | 🟥 **OPEN** | Operational acceptance outstanding |
| Overall project | **NOT SCORED** | Approved weighted denominator is not defined |

**Significant progress in this batch:** malformed socket state can no longer abort restoration merely because close throws; fan-out now enforces the full attachment contract before delivery. This closes two narrow source-level gaps but does not justify raising stage or project percentages.

**Target date:** 24 December 2026 — planning target, not a completion guarantee.
