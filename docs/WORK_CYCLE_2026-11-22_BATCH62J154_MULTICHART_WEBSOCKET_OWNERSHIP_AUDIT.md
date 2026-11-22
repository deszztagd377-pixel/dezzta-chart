# WORK CYCLE 62J-154 — Multi-chart ownership audit and safe WebSocket scaling plan

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Delivery target: 24 December 2026  
ZERO COST: enforced  
`main`: untouched

## Audit scope

Read-only audit of:
- `src/services/ohlcvStreamSupervisor.ts`
- `src/services/marketDataStore.ts`
- `src/services/ohlcvWebSocketClient.ts`
- `src/components/CandlestickChart.tsx`
- `src/services/ohlcvStreamSupervisor.test.ts`
- `src/services/marketDataStore.test.ts`

No runtime code changed in this audit. The current behavior is covered by tests and must not be broken by an unscoped refactor.

## Confirmed current architecture

### Frontend ownership

1. `marketDataStore.ts` holds one module-global `currentSnapshot`, not a map of snapshots keyed by series identity or chart owner.
2. `ohlcvStreamSupervisor.ts` holds one module-global `activeSupervisorStop`.
3. Starting a new supervisor stops the previous owner. This is explicitly tested as a timeframe/selection replacement behavior.
4. `CandlestickChart.tsx` starts a supervisor from its own chart lifecycle effect. If multiple independent chart components mount, a later chart can supersede the earlier chart's supervisor and both components observe the same singleton store.
5. Therefore the current implementation is safe for one active chart selection but does not yet provide independent concurrent multi-chart data ownership.

### Backend client isolation

Existing backend tests and the stream hub support per-client bounded queues, exact-series subscriptions, and independent disconnect behavior. This is useful multi-user transport isolation evidence. It does not imply the frontend can own multiple chart panels, nor does it establish shared upstream provider demand/refcounting.

## Required architecture before multi-chart runtime implementation

The design must separate three lifetimes:

- **Chart-panel owner:** unique owner ID for a mounted panel; acquire/release is idempotent and cleanup-safe.
- **Series stream:** canonical exact identity key including provider, dataset, publisher, instrument, raw symbol, series type, timeframe, bucket policy, calendar ID and version.
- **Upstream provider demand:** shared provider subscription for a series, with reference-counted active consumers only where the provider adapter actually supports the required lifecycle operation.

Proposed ownership contract:
1. A chart panel acquires a series lease and receives a read-only snapshot subscription for that series.
2. Multiple panels on the same series share one authenticated transport where policy permits, but maintain independent panel leases.
3. Different series have independent snapshots and lifecycle state.
4. Releasing one panel removes only its lease; other panels continue receiving updates.
5. The last panel release closes the frontend stream and releases upstream demand only if the backend provider manager can safely remove that subscription.
6. A reconnect reconciles the complete desired owner set against actual provider state; it must not duplicate subscriptions.
7. Late events from a released owner or superseded generation cannot mutate another panel's state.
8. Owner IDs and generation tokens are opaque, bounded, and not treated as authentication credentials.
9. UI state must be keyed by canonical series identity; a chart must never render another panel's data because it shares a module-global mutable snapshot.

## Required test matrix

- two panels acquire the same series -> one shared stream, two independent panel listeners;
- two panels acquire different series -> neither snapshot overwrites the other;
- one of two same-series panels unmounts -> remaining panel stays subscribed;
- final panel unmounts -> stream closes exactly once;
- duplicate acquire/release calls -> no negative reference count or duplicate transport;
- panel switches series -> old lease releases and new lease acquires without stale-event crossover;
- reconnect -> desired owners reconcile exactly once;
- delayed close/event from old generation -> cannot clear or overwrite current series;
- authentication rejection -> all owners for that transport receive terminal unavailable state;
- one panel's rendering exception -> does not terminate other panels' subscriptions;
- backend multi-user tests continue to pass unchanged.

## Provider capability boundary

The backend provider manager currently starts configured ingestion at process/application lifespan. The inspected Databento source subscribes to a fixed constructor-provided symbol set and does not expose a verified repository-level dynamic add/remove API. SDK signatures and dynamic behavior remain unverified.

Do not implement only a local refcount and claim provider demand control. First verify an exact pinned SDK version and its documented/runtime-tested dynamic lifecycle. If the source is restart-required or unsupported, the coordinator must report that capability explicitly and must not pretend per-chart on-demand switching exists.

No provider credential or paid feed is available for this audit. ZERO COST remains absolute; no data scraping or redistribution-rights assumptions.

## Decision

- Preserve the current single-chart behavior until the keyed-store/owner-lease design has tests.
- Treat multi-chart frontend ownership as an open Stage 2/Stage 3 integration blocker.
- Keep backend multi-user transport isolation as a separate verified capability.
- Implement the refactor in a dedicated, reviewable work cycle after the interface contract and migration sequence are reviewed. Avoid mixing it with the unrelated CI fixture correction.

## Indicator and project progress impact

No indicator formula, renderer, hook, or test changed. Indicator progress credit: zero.

The complete indicator ledger is maintained in:
`docs/WORK_CYCLE_2026-11-22_BATCH62J153_BACKEND_CI_FIX_AND_INDICATOR_LEDGER.md`.

This audit does not change stage scores:
- Stage 1: 30/40 = 75% provisional 🟨.
- Stage 2: not scored ⬜.
- Stage 3: not scored ⬜.
- Stage 4: not scored ⬜.
- Stage 5: not scored ⬜.
- Stage 6: not scored ⬜.
- Overall: NOT SCORED; no approved denominator.
- Gate 10 external acceptance: 0/10 formally closed.

## CI and deployment boundary

Fresh CI is running for the corrected test commit and latest docs HEAD. This document does not claim success for pending jobs. OCI ARM64 CI is an image build/smoke test only, not a provisioned OCI VM, installed service, public hostname, or WSS deployment.
