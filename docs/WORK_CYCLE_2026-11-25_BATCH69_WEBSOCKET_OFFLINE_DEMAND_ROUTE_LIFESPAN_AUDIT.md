# DEZZTA CHART — Work Cycle 69: WebSocket offline-demand route/lifespan audit

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Audited HEAD: `c746478cba0bbec95c663d9f9986e9863866538c`  
Scope: authenticated WebSocket route acquisition/release, per-series sharing, disconnect cleanup, lifespan pending-release recovery, and exact-head CI evidence.  
Cost: ZERO COST.

## 1. Source trace

The audit followed the path from `create_app()` through FastAPI lifespan and the authenticated WebSocket endpoint.

- The app constructs `InMemoryOfflineProviderAdapter` and `ProviderDemandCoordinator` explicitly as local-only/offline-fixture components.
- Only `provider_id == "offline-fixture"` acquires a demand lease.
- The key includes source, venue, dataset, canonical instrument, symbology and timeframe-scoped channel.
- Acquisition occurs after identity verification and instrument entitlement authorization.
- Disconnect cleanup unsubscribes the stream and calls bounded `release_with_retry` for the lease.
- Exhausted/cancelled cleanup retains the pending lease; the lifespan worker retries pending releases on a one-second cadence.
- Shutdown sets the stop event and waits for the recovery worker with a bounded two-second deadline.

No path from this offline adapter to a live provider SDK was found in the audited route. This remains an offline lifecycle exercise, not evidence of a production upstream subscription.

## 2. Regression evidence

`backend/tests/test_api.py` contains route/lifespan tests including:

- `test_offline_websocket_demand_is_shared_and_released_on_disconnect`: two authorized clients share one offline demand; first disconnect leaves one owner; final disconnect releases the last owner.
- `test_offline_websocket_pending_release_is_recovered_by_lifespan_worker`: injected stop failure is queued after bounded immediate retries and recovered by the lifespan worker.
- Existing WebSocket isolation test verifies one mobile client's disconnect does not stop another user's live socket.
- Existing entitlement-revocation tests verify active subscriptions are disconnected when access is revoked.

`backend/tests/test_provider_demand.py` separately covers duplicate acquisition, concurrent acquire/release, retry exhaustion, cancellation, pending queue retention and recovery.

## 3. Audit result and boundaries

**Result: PASS for the offline-fixture route/lifespan scope.** No source defect was established by this audit; no runtime source change was justified.

Still OPEN / not accepted:
- Cross-process or multi-host provider-demand ownership.
- Durable pending-release recovery across process restart.
- Provider SDK dynamic subscribe/unsubscribe and provider-side acknowledgement.
- Recurring-$0 data rights, display/redistribution permission and verified provider contract.
- Gate 25 authenticated owner-host receipt retrieval and durable high-water ACK.
- Gate 36 public WSS/TLS/Firebase end-to-end acceptance.
- Android process-death/network-handover and multi-instance device acceptance.

Do not infer production WebSocket completion from the offline-fixture tests. Existing Redis quota leases and exclusive replica consumer leases remain separate ownership layers.

## 4. Exact-HEAD CI

The audited HEAD `c746478cba0bbec95c663d9f9986e9863866538c` has four terminal SUCCESS workflows:
- Automated Tests — run 45592885822, job Test and Build: SUCCESS.
- CodeQL Security Analysis — run 45592885957: SUCCESS.
- OCI ARM64 Image Readiness — run 45592885915: SUCCESS.
- Full Git History Secret Audit — run 45592886298: SUCCESS.

All four records target the same exact HEAD. No workflow remains running on that SHA. The earlier Batch 66 run 45591449872 was cancelled by concurrency policy; the later exact-head Automated Tests run on this branch is successful and validates the source/test tree.

## 5. Indicator and project accounting

No indicator calculations, hooks, renderer, chart UI, or indicator-specific tests changed. No indicator completion credit is awarded.

- SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook: 🟨 FOUNDATION only.
- Footprint PRO 2GD: 🟧 GATED; renderer remains behind Stage 4 and supplied visual references.
- Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps: 🟥 OPEN.
- Focused declarations remain 21 calculation + 7 shared-hook test declarations; declarations are not completed-indicator counts.
- Stage 1: 30/40 = 75% provisional inherited baseline 🟨.
- Stage 2: active, no approved denominator 🟦 NOT SCORED.
- Stage 3: ⬜ NOT SCORED.
- Stage 4: 🟪 GATED.
- Stage 5/6: ⬜ NOT SCORED.
- Gate 10: 0/10 formally closed 🟥.
- Overall project, aggregate indicator completion and significant progress/IP3S: ⚪ NOT SCORED.

## 6. Next sequence

1. Continue repository-verifiable WebSocket/replication safety work without conflating offline fixture, Redis consumer ownership and provider ownership.
2. Resolve the lawful recurring-$0 provider contract and exact dynamic adapter/ACK contract before live-provider wiring.
3. Close Gate 25 with owner-host receipt/high-water evidence.
4. Close Gate 36 with public WSS/TLS/Firebase E2E after explicit deployment authorization.
5. Complete Android lifecycle and multi-instance acceptance.
6. Keep destructive Redis retention disabled until all independent prerequisites pass.
7. Keep major indicator UI behind Stage 4 and scoped blueprint/review.

ZERO COST maintained. `main` untouched. Vercel deployment deferred. No paid service, production feed, credential activation or destructive Redis operation. Planning target remains approximately 24 December 2026.
