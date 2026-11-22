# DEZZTA CHART — Work Cycle 62J-162
Date: 2026-11-22
Branch: `phase-2/market-data-foundation`
Base HEAD: `a29e784eb8da13fa89f09c8e3f3a7596bc7f2096`

## Objective
Reduce backend OHLCV WebSocket fan-out work from scanning every connected subscription for every accepted bar to visiting only subscribers of the exact canonical series. Tighten validation ordering so malformed durable cursors are rejected before a potentially expensive snapshot query. Preserve replay ordering, queue overflow behavior, exact identity isolation, and zero-cost defaults.

## Implemented changes
1. `backend/app/ohlcv_stream.py`
   - Added `_subscriptions_by_identity`, keyed by the complete 10-field `SeriesIdentity`.
   - Both `subscribe_snapshot()` and `subscribe_snapshot_bars()` register through one internal helper so in-memory and replica snapshot paths share the same index lifecycle.
   - `publish()` now visits only the exact identity bucket instead of scanning all active subscriptions.
   - `unsubscribe()` removes the stream from both indexes and deletes an empty series bucket.
   - Added read-only `series_count` and `subscriber_count_for(identity)` diagnostics for invariant tests.
   - `merge_replay_boundary()` continues validating active subscription identity against the authoritative stream map.
   - Durable cursor type/range validation now runs before `pipeline.query()`; malformed values cannot trigger a snapshot read.

2. `backend/tests/test_ohlcv_stream.py`
   - Added a mixed registration-path test: two ES panels use the normal pipeline snapshot path; an NQ panel uses the externally consistent snapshot-bars path.
   - Asserts index cardinality and exact per-series subscriber counts.
   - Asserts ES publication reaches both ES subscribers but not NQ.
   - Asserts removing the final ES owner removes only the ES index bucket; NQ remains registered.
   - Added a query-spy regression proving invalid cursors (-1, bool, float) fail before snapshot query execution.

## Complexity and resource accounting
- Previous publication dispatch: O(S) identity comparisons for S total active subscriptions per accepted bar.
- New publication dispatch: O(S_k), where S_k is the subscriber count for the bar's exact canonical series.
- Index storage: O(S) additional dictionary entries/references; subscription payloads/queues are not duplicated.
- Theoretical illustration only: if 500 active clients are evenly distributed across 32 distinct series, average target bucket size is 15.625; compared with scanning 500, this is about 96.875% fewer subscriber entries visited per bar. This is not a benchmark result and actual skew may be higher.
- Per-subscriber queue capacity remains 256; global/per-account WebSocket connection limits remain governed by the existing shared guard.
- No provider, API key, paid hosting, cloud VM, or paid dependency was added.

## Safety and compatibility invariants
- Canonical identity includes provider, dataset, publisher ID, instrument ID, series type, raw symbol, timeframe, bucket policy, calendar ID, and calendar version.
- No cross-series fan-out.
- Snapshot registration remains synchronous on the owning event loop.
- Durable replay boundary, monotonic cursors, queue overflow fail-closed behavior, and resnapshot requirements are unchanged.
- Empty identity buckets are removed on final unsubscribe.
- No silent update dropping; a full subscriber queue remains overflowed and must resnapshot.
- No provider SDK calls or live-feed behavior changed.

## CI verification
Status at commit creation: PENDING.
Do not mark this cycle green until the Automated Tests, CodeQL, Secret Audit, OCI ARM64 readiness, and Android Debug APK workflows have completed for the exact code HEAD. OCI workflow success is only image build/smoke readiness, not an OCI VM deployment. APK workflow success is a CI artifact, not public release.

## Upstream provider and ZERO COST boundary
- Frontend per-series WebSocket supervisors are implemented.
- Backend stream hub now indexes downstream subscriber fan-out by canonical series.
- Backend `ProviderManager` remains process/configuration scoped and Databento SDK adapter signatures remain explicitly unverified against the real SDK.
- No dynamic vendor add/remove subscription API has been established.
- Databento live/historical usage is not a recurring-zero-cost source; production configuration continues to fail closed under the ZERO MONEY policy.
- No recurring-zero-cost CME feed with application redistribution rights has been verified.
- A WebSocket subscription or cached snapshot does not prove an upstream live feed exists.

## Full indicator progress
Legend: 🟩 verified/implemented foundation; 🟨 partial foundation; 🟧 prototype only; 🟥 not implemented.

| Indicator / component | Status | Verified foundation | Remaining acceptance work |
|---|---|---|---|
| SMA20 | 🟨 | 20-close arithmetic mean; first valid index 19; warm-up nulls; aligned output | Chart overlay, toggle, legend/latest value, identity/lifecycle/render tests |
| EMA20 | 🟨 | SMA seed; alpha 2/21; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render tests |
| RSI14 Wilder | 🟨 | Wilder smoothing; first valid index 14; regression tests | Dedicated 0–100 pane, 30/70 guides, toggle/legend/render tests |
| MACD12/26/9 | 🟨 | MACD first valid index 25; signal/histogram first valid index 33 | Pane, MACD/signal lines, histogram, zero guide, toggle/legend/render tests |
| Bollinger20,2 | 🟨 | 20-close mean ±2 population standard deviation; first valid index 19 | Three-line overlay, toggle, latest values, render tests |
| Shared Indicator Hook | 🟨 | Keyed React snapshot and pure reads; aligned calculations | Hook stale clearing, gap semantics, chart binding and renderer integration |
| Footprint | 🟧 | Synthetic educational accumulator only | User reference image, reviewed blueprint, validated bid/ask provenance, spaced cluster renderer and acceptance tests |
| Heatmap | 🟥 | No validated depth/liquidity renderer | User reference image, depth/liquidity source contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 | No validated liquidation calculation/renderer | Data provenance and calculation contract, reviewed blueprint, renderer and tests |

Indicator acceptance invariants:
- Warm-up values remain null; never substitute zero.
- Outputs remain candle-index aligned and prefix-causal.
- Gaps/invalid bars must not silently become synthetic candles or zeroes.
- Clear stale outputs when symbol, venue/provider, dataset, timeframe, bucket policy, calendar, or chart identity changes.
- Footprint OFF retains ordinary candle spacing; explicit ON uses the dedicated spaced cluster layout.
- Do not award indicator completion from docs, CI, or benchmarks.
- Footprint and Heatmap visual implementation remains blocked until the user supplies reference images and reviews the scoped blueprint.

## Project stage and Gate 10 dashboard
- Stage 1 — Foundation, Security & Data Integrity: 30/40 = 75% provisional 🟨.
- Stage 2 — Market Data Infrastructure: not formally scored; frontend multi-series transport and backend indexed fan-out are implemented, but upstream demand/provider lifecycle and zero-cost data entitlement remain open 🟨.
- Stage 3 — Chart Engine & Timeframe: not scored ⬜.
- Stage 4 — Indicators & Analytics: not scored ⬜.
- Stage 5 — Professional UI & Interactive Tools: not scored ⬜.
- Stage 6 — Hardening, Validation & APK Release: not scored ⬜.
- Overall project: NOT SCORED; no approved overall denominator or stage weights.
- Gate 10: 0/10 external acceptance criteria formally closed. CI success does not close external deployment/device/data-rights gates.
- Target delivery: 2026-12-24.

## Next engineering targets
1. Validate and formalize backend provider-demand lifecycle without inventing Databento SDK methods.
2. Establish a recurring-zero-cost source and redistribution-rights evidence before any production live market-data activation.
3. Complete reconnect/replay reconciliation and cross-process ownership tests.
4. Continue indicator renderer integration only after preserving the existing warm-up, gap, identity, and no-future-leak invariants.
5. Keep OCI/hosting work limited to zero-cost local/CI readiness unless a genuinely free, no-card, no-billing option is verified.


## Follow-on optimization while CI was running
- `OhlcvStreamHub.publish()` now returns immediately when no subscriber exists for the incoming bar's exact canonical identity.
- This avoids building the outgoing payload and converting decimal fields when no client can receive the event.
- Added a regression test with an active NQ subscription and an unobserved ES update; the test fails if payload serialization is attempted.
- This is a code-path optimization, not a measured throughput claim.


## Event metadata consistency hardening
- A single logical bar publication now generates one `eventId` and one `emittedAtNs` value, shared by every subscriber of that exact series.
- Previously, the UUID and clock were evaluated separately inside the per-subscriber loop, giving different identifiers/timestamps to panels receiving the same logical publication.
- The same-series multi-panel regression test now verifies identical event IDs and emission timestamps for both recipients.
- This preserves durable `eventId` values when supplied by the outbox and generates one fallback ID per publication otherwise.
