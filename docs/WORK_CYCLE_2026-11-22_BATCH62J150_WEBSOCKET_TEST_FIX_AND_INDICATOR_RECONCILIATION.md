# Work Cycle 62J-150 — WebSocket subscriber test correction and indicator reconciliation

Date: 22 November 2026
Branch: phase-2/market-data-foundation
Starting failing HEAD: 041da77cb9ce95e083f8851614928d0de0994ad4
Test correction commit: cb708c3e6357c59ef7a61fcb5fc5c304b014d62a
Cost: ZERO COST. main untouched.

## CI failure investigation

Automated Tests run 45018172626 completed with 1,297 passed, 1 failed and 1 skipped. Frontend tests/build, Android preflight/publisher tests, frontend secret scanning and dependency audit passed. The only failure was backend/tests/test_ohlcv_stream.py::test_same_series_subscribers_are_isolated_when_one_disconnects.

The test published an event to both subscriber queues, verified both queue sizes, then disconnected subscriber A without consuming A's already-enqueued first event. It subsequently asserted A's queue was empty. The hub correctly marked A closed and removed it from future fan-out; unsubscribe does not retroactively erase a message already queued before disconnect. The assertion tested an incorrect precondition, not a production delivery-isolation defect.

## Minimal correction

Updated the test to consume and verify subscriber A's already-delivered first event before unsubscribe. It then verifies A is closed, no later update is queued for A, B continues receiving the next update, and subscriber count transitions 2 → 1 → 0.

No production runtime code, queue semantics, API contract or provider behavior changed. This is intentionally test-only. No queue-draining behavior was added to production because disconnecting does not need to mutate messages already delivered to a disconnected consumer.

## CI evidence and qualification

At failing HEAD 041da77cb9ce95e083f8851614928d0de0994ad4: Automated Tests failed solely on the incorrect queue precondition; CodeQL Python and JavaScript/TypeScript succeeded; OCI native ARM64 image build and smoke test succeeded; Full Git-history Secret Audit succeeded.

Correction test commit cb708c3e6357c59ef7a61fcb5fc5c304b014d62a was verified as an ancestor of exact CI HEAD 754e1d9edc270e110161662aad83b6fac4a792bc. All four workflows completed SUCCESS on that exact HEAD:
- Automated Tests [45018667056](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018667056): SUCCESS. Backend pytest: 1,298 passed, 1 skipped. Frontend unit tests/build, Android host preflight/publisher tests, frontend dependency audit, synthetic SQLite outbox and metrics benchmarks, backend dependency audit, backend image build, container smoke test and image vulnerability scan all succeeded. The container vulnerability report artifact was uploaded.
- CodeQL [45018667061](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018667061): SUCCESS for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [45018667128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018667128): SUCCESS.
- OCI ARM64 [45018667069](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45018667069): SUCCESS; native ARM64 image build and unprivileged/persistent-volume smoke test passed.

CI result applies to exact HEAD 754e1d9edc270e110161662aad83b6fac4a792bc. It is not an OCI VM deployment, public hostname, TLS/WSS endpoint or Android-device acceptance.

## Complete indicator progress — unchanged

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Chart overlay, independent toggle, legend/latest value, identity/lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change gain/loss mean and Wilder recurrence; first valid index 14; period-2 recurrence regression added | Dedicated 0–100 pane, 30/70 guides, toggle/legend/latest value, identity/lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | EMA12 − EMA26; MACD first valid index 25; EMA9 signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle/legend/latest values, lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle/current values, identity/lifecycle/render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | Validated snapshot and candle-index-aligned calculations | Hook tests, chart binding, settings/legend integration, stale clearing and identity/lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, verified bid/ask source contract, ON-only spaced clusters, OFF-layout regression and renderer acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity runtime contract or renderer | User reference image(s), verified source contract, reviewed blueprint, renderer, scale/legend/toggle/tests |
| Liquidation Maps | 🟥 Not implemented | No accepted provenance/calculation contract or renderer | Defensible source/provenance, reviewed blueprint, renderer, scale/legend/tests |

Shared invariants: warm-up values remain null (not zero); outputs align to source candle indices; no future-candle repaint; invalid/gapped bars are not silently converted to zero; stale outputs clear on symbol/venue/dataset/chart/timeframe identity changes. Footprint OFF preserves ordinary candle spacing; explicit ON alone enables spaced clusters. Footprint and Heatmap visual implementation remains gated on user reference images and review of a scoped blueprint. No aggregate indicator percentage without approved study weights and denominator.

No indicator formula, calculation kernel, shared hook, renderer, chart UI or indicator test changed in this WebSocket-only cycle. Award zero indicator implementation progress.

## Project stage and Gate accounting

- Stage 1 Foundation, Security & Data Integrity: 30/40 = 75% provisional 🟨.
- Stage 2 Market Data Infrastructure: NOT SCORED / not officially opened ⬜. Upstream on-demand subscription and provider lifecycle remain unresolved.
- Stage 3 Chart Engine & Timeframe: NOT SCORED ⬜.
- Stage 4 Indicators & Analytics: NOT SCORED ⬜.
- Stage 5 Professional UI & Interactive Tools: NOT SCORED ⬜.
- Stage 6 Hardening, Validation & APK Release: NOT SCORED ⬜.
- Overall project: NOT SCORED; approved stage weights/denominator do not exist.
- Gate 10: 0/10 external acceptance criteria formally closed. Owner-host, public-network, real Android-device and provider-rights checks remain distinct from CI.

## WebSocket / On-demand boundary

This correction improves evidence for downstream per-client disconnect isolation only. It does not implement provider-side dynamic subscribe/unsubscribe, upstream pooling/reference counting, multiple simultaneous frontend chart supervisors, or chart-open/close/background demand coordination. Stage 2 remains open. Do not add a disconnected reference counter and claim on-demand complete. The fixed-symbol provider adapter and recurring-$0 compatible feed/redistribution-rights gap remain explicit blockers.

## ZERO COST and release boundary

No paid service, provider, account, credential, cloud resource, deployment, payment method, device/Termux operation or main change. OCI CI remains image-build/smoke evidence, not an installed OCI VM, public hostname, TLS/WSS endpoint or production server. Target remains 24 December 2026; it is not a guaranteed delivery claim.
## IP3S — significant work-cycle progress score

**Batch 62J-150: 90/100.** This is a per-cycle delivery-quality score, not project completion.

| Dimension | Score | Basis |
|---|---:|---|
| Verified engineering delta | 15/25 | Corrected and strengthened deterministic subscriber-isolation regression; no production runtime change |
| Exact-HEAD tests/security CI | 20/20 | Automated Tests, CodeQL, Secret Audit and OCI ARM64 all succeeded on HEAD 754e1d9 |
| Blocker reduction | 20/20 | Sole failing backend assertion was traced to an incorrect queued-message precondition, corrected, and backend suite passed |
| Canonical documentation | 20/20 | Work-cycle report and full indicator/project dashboard reconciled |
| Scope and ZERO COST integrity | 15/15 | Correct branch, no main changes, no paid resources or unapproved deployment |

Total: 15 + 20 + 20 + 20 + 15 = 90/100. No Stage 2, indicator-rendering or external Gate 10 closure is inferred from this score.