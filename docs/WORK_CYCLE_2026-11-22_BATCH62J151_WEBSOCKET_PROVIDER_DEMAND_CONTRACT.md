# WORK CYCLE 62J-151 — WebSocket lifecycle and provider-demand implementation plan

Date: 22 November 2026  
Target delivery date: 24 December 2026  
Branch: `phase-2/market-data-foundation`  
Baseline HEAD inspected: `bf1ae4c8b2dfd192cd627b3a4638b5fd1ca0eb3f`  
Main branch: untouched  
Cost policy: ZERO COST

## Scope and result

This batch performed a source-level lifecycle audit of the frontend OHLCV supervisor, its tests, the backend stream hub, and ProviderManager. It deliberately makes no runtime change: the current provider adapter is fixed-symbol/process-lifecycle scoped, and the frontend supervisor owns a singleton shared snapshot. Adding an isolated reference counter without wiring it to a verified upstream add/remove API would be a false implementation.

This report converts the observed constraints into an ordered implementation contract and acceptance matrix. Documentation-only work receives no runtime feature completion credit.

## Verified current behavior

### Frontend
- The supervisor authenticates through the ticket flow, subscribes to one exact series identity, validates snapshot/update sequencing, and reconnects with cursor replay.
- Stop cancels pending identity requests, reconnect timers, and the active connection.
- The module-level `activeSupervisorStop` is a single-owner guard. It prevents competing supervisors from writing the same shared snapshot, but does not provide independent ownership for multiple simultaneous chart panels.
- Existing tests cover identity replacement, late callback suppression, token/ticket failures, reconnect and replay, sequence-gap recovery, explicit stop, and close-code handling.

### Backend
- `OhlcvStreamHub` provides downstream per-client queues and exact-series fan-out. Disconnecting one subscriber does not require closing another subscriber's queue.
- `ProviderManager.start()` starts configured ingestion at application lifecycle, not on chart demand.
- `DatabentoLiveSource` uses a fixed configured symbol set. Repository code does not currently demonstrate a dynamic per-series upstream subscribe/unsubscribe contract.
- The adapter's real SDK semantics have not been established against a pinned, verified SDK version.

## Required architecture contract

1. **Separate chart identity from market-series identity.** A chart panel has its own owner token; a market series is the canonical tuple (provider, dataset, venue/instrument, schema, timeframe).
2. **Idempotent acquire/release.** Repeated acquire by the same owner must not double-count. Repeated release must be harmless. Unknown owner release must not decrement another owner's demand.
3. **Per-series ownership.** Maintain the set of owners for each canonical series. A provider subscription is active only while at least one authorized owner requires it.
4. **Provider capability is explicit.** Each adapter must declare one of: dynamic subscribe/unsubscribe, multiplexed subscription set, restart-required reconfiguration, or unsupported. The coordinator must not assume dynamic behavior.
5. **Shared upstream is conditional.** Equivalent active series may share one upstream subscription only where provider semantics and redistribution rights allow it.
6. **Downstream isolation remains mandatory.** Removing owner A must not close owner B's WebSocket or clear B's chart snapshot.
7. **Lifecycle sources are explicit.** Chart open acquires; pair/timeframe change releases old then acquires new; chart close and foreground loss release; foreground return reacquires; auth/entitlement revocation terminates only the affected owner.
8. **Reconciliation is deterministic.** After backend/provider reconnect, rebuild desired upstream subscriptions from current authorized owners; do not trust stale in-memory counters.
9. **Unsupported data stays unavailable/demo.** Never substitute an unrelated feed or scrape a public quote page to impersonate licensed application data.

## Acceptance matrix — not yet passed

| Case | Expected invariant | Evidence required |
|---|---|---|
| 200 catalogue entries, no open charts | 0 live market subscriptions | provider-side subscription spy/counter |
| One chart opens series S | exactly one owner for S | coordinator unit + integration test |
| Same owner repeats acquire(S) | still one owner | idempotency test |
| Same user opens S in two panels | two panel owners, one upstream where supported | multi-panel test |
| Two users open S | independent downstream clients | real WSS integration test |
| User A disconnects | user B continues | subscriber isolation test |
| Last owner releases S | upstream release exactly once | adapter lifecycle test |
| Pair/timeframe changes S→T | S released, T acquired | transition/race test |
| Background then foreground | release then one reacquire | Android lifecycle acceptance |
| Provider reconnect | desired owner set reconciled | restart/reconnect test |
| Entitlement revoked for A | A removed; B unaffected if still entitled | authorization integration test |
| Provider lacks dynamic capability | no false live status; safe unavailable state | capability contract test |
| SDK version changes | adapter contract suite still passes | exact dependency pin + adapter tests |

## Implementation order and dependency gates

### P0 — provider capability proof
- Select a recurring-$0 feed only if exact instrument coverage, freshness, and application display/redistribution rights are documented.
- Verify provider SDK documentation and exact version; test adapter behavior with an isolated fake first.
- Do not use a paid provider, trial credits as a recurring plan, personal-only feed, or browser scraping as a production source.

### P1 — backend demand coordinator
- Define canonical series and owner identity types.
- Implement idempotent owner-set/refcount state only after P0 capability is known.
- Add serialized provider transitions, rollback on failed subscribe, and reconciliation after reconnect.
- Add tests for all acceptance cases above, including concurrency and cancellation.

### P2 — frontend multi-panel ownership
- Replace singleton ownership only after chart-store ownership is made panel-scoped or otherwise proven safe.
- Keep existing single-chart behavior as a regression baseline.
- Wire open/switch/close/background/foreground events to acquire/release.
- Add race tests for stale panel cleanup and rapid selection changes.

### P3 — external acceptance
- Verify public hostname, TLS/WSS, real Firebase session, real Android foreground/background/process death/network handover, and multi-user isolation.
- OCI ARM64 CI image readiness is not an OCI VM deployment or public endpoint.

## ZERO COST decision

No recurring-$0 source with verified exact CME instrument coverage and multi-user application redistribution rights is currently approved in the repository evidence. This is a project-specific evidence gap, not a claim that all free data is impossible. Until resolved, unsupported live series must remain clearly unavailable/demo. On-demand subscription reduces unnecessary consumption; it does not make a paid upstream free.

## Indicator progress accounting

No indicator formula, renderer, hook, or test changed in this batch. Therefore indicator implementation credit is **zero**.

| Indicator / subsystem | Current status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19 | Overlay, toggle, legend/value, lifecycle/render tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19 | Overlay, toggle, legend/value, lifecycle/render tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; recurrence regression | 0–100 pane, 30/70 guides, controls and render tests |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, controls and render tests |
| Bollinger20,2 | 🟨 Foundation | Mean ±2 population SD; first valid index 19 | Three-line overlay, controls and render tests |
| Shared Indicator Hook | 🟨 Foundation | Validated aligned snapshot calculations | Hook tests, chart binding, stale clearing and renderer |
| Footprint | 🟧 Prototype | Synthetic educational accumulator only | User references, reviewed blueprint, valid bid/ask contract, cluster renderer |
| Heatmap | 🟥 Not implemented | No accepted runtime renderer | User references, depth/liquidity contract, blueprint and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted data/provenance contract | Defensible provenance, calculation contract, blueprint and renderer |

Shared invariants: warm-up nulls; candle-index alignment; prefix causality; invalid/gapped-bar rejection; stale-output clearing on identity changes; Footprint OFF preserves normal candle spacing and explicit ON enables cluster spacing. Footprint and Heatmap visual implementation remain gated on user-provided reference images and a reviewed scoped blueprint.

## Stage and gate accounting

- Stage 1 Foundation, Security & Data Integrity: 30/40 = 75% provisional 🟨.
- Stage 2 Market Data Infrastructure: not scored; provider-demand implementation remains open ⬜.
- Stage 3 Chart Engine & Timeframe: not scored ⬜.
- Stage 4 Indicators & Analytics: not scored ⬜.
- Stage 5 Professional UI & Interactive Tools: not scored ⬜.
- Stage 6 Hardening, Validation & APK Release: not scored ⬜.
- Overall project: NOT SCORED; approved weights and denominator do not exist.
- Gate 10: 0/10 external criteria formally closed. CI success does not close external hosting, public network, provider-rights, or Android acceptance.

## Deadline arithmetic

From 22 November through 24 December 2026: 32 calendar days (inclusive of the target date). Delivery sequencing must prioritize a verified installable ZERO COST baseline and keep unsupported live data explicitly unavailable. Full production acceptance cannot be promised while provider rights, external hosting, and real-device acceptance remain unverified.

## Change and verification record

This batch adds this report only. No production runtime files were changed; no paid service, account, key, deployment, or main-branch operation was introduced. Baseline exact-HEAD CI evidence remains the four successful workflows recorded for `bf1ae4c8b2dfd192cd627b3a4638b5fd1ca0eb3f`; this documentation commit requires its own CI run before being described as fully verified.
