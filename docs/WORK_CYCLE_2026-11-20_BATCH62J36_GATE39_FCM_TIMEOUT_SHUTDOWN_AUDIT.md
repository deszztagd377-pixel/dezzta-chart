# Batch 62J-36 — Gate 39 FCM timeout and shutdown-boundary audit

**Date:** 20 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Starting HEAD:** `7bcd970de949743e8ecf1883344df86af3b97552`  
**Scope:** source-level audit and evidence documentation; no provider/runtime behavior changed.

## Exact-head CI evidence for Batch 62J-35

The three workflows for starting HEAD `7bcd970de949743e8ecf1883344df86af3b97552` completed successfully:

- Automated Tests: run `44714421029` — SUCCESS.
- CodeQL JavaScript/TypeScript + Python: run `44714420946` — both analyses SUCCESS.
- Full Git History Secret Audit: run `44714421017` — SUCCESS.

Batch 62J-35's partial multi-device fan-out retry test is therefore CI-verified. Its guarantee remains at-least-once delivery with stable `event_id` for client-side deduplication; it does not establish exactly-once notification display.

## Gate 39 — material timeout and shutdown finding

The source audit identified a concrete gap that must remain visible rather than being hidden by a superficial cancellation patch:

1. `FirebaseCloudMessagingSender.from_application_credentials()` initializes the named Firebase Admin app with only `projectId`; it does not set `httpTimeout`.
2. Firebase Admin Python's documented default HTTP timeout is 120 seconds when `httpTimeout` is omitted. Its Messaging service consumes that app option when constructing its HTTP clients. The SDK also mounts an HTTP adapter with its default retry configuration.
3. One outbox event can fan out sequentially to up to 10 active installations in `build_alert_event_sender()`.
4. The worker's default lease is 120 seconds. The configured batch size is intentionally fixed at 1, but that does not bound the duration of the up-to-10-recipient fan-out.
5. The lifespan shutdown sets `worker_stop` and then awaits `worker_task`. The stop event is only observed after the current `asyncio.to_thread(run_alert_delivery_batch, ...)` call returns.

The timeout arithmetic is therefore not safe to treat as a 120-second total-event deadline: a single recipient request may consume up to the SDK's default request timeout, and a multi-recipient fan-out is sequential. Retry behavior can extend elapsed time further. The current code does not establish a strict total wall-clock bound for a full event batch or graceful shutdown.

## Why no speculative cancellation change was made

Wrapping the worker await in `asyncio.wait_for()` and cancelling the coroutine would not terminate a synchronous function already executing in a worker thread. That thread could continue sending after the ASGI lifespan has moved on, while its durable lease expires and another worker later reclaims the same event. That creates an avoidable duplicate-send and acknowledgement race.

A safe implementation must first choose and test a provider-level bounded request/retry policy, then derive a lease budget from the maximum fan-out and acknowledgement overhead, and finally define shutdown behavior that does not falsely assume thread cancellation stops network I/O. An alternative bounded-parallel FCM batch design would require explicit per-recipient result handling and tests for partial success. Neither architecture is silently introduced in this audit-only batch.

## Gate 39 disposition

<badge color="warning">ORANGE — OPEN</badge>

Automated retry boundaries, lease expiry, stale acknowledgement rejection, partial fan-out retry, and stable event IDs have repository tests. The following remain unaccepted:

- strict total FCM event-delivery deadline under provider retries;
- bounded graceful shutdown while a send is in flight;
- process interruption during an actual provider request;
- production Firebase delivery and Android-side deduplication;
- operator acknowledgement, escalation, and incident recovery.

No claim of production readiness or Gate 39 closure is made.

## Indicator and project dashboard — unchanged

| Indicator | Status | Verified foundation / remaining acceptance |
|---|---|---|
| SMA 20 | 🟨 | Rolling arithmetic mean; first valid index 19; chart overlay/lifecycle not integrated |
| EMA 20 | 🟨 | SMA-seeded EMA; alpha 2/21; first valid index 19; chart overlay/lifecycle not integrated |
| RSI 14 | 🟨 | Wilder smoothing; first valid index 14; oscillator pane not integrated |
| MACD 12/26/9 | 🟨 | MACD first index 25; signal/histogram first index 33; pane not integrated |
| Bollinger 20,2 | 🟨 | Population standard deviation; first valid index 19; three-line overlay not integrated |
| Shared Indicator Hook | 🟨 | Validated backend snapshot; chart binding/lifecycle remains |
| Footprint | 🟧 | SIMULATED only; owner reference image and reviewed blueprint required; OFF keeps standard candle spacing |
| Heatmap | 🟥 | Not implemented; owner reference image, reviewed blueprint and data contract required |
| Liquidation Maps | 🟥 | No validated data/calculation contract |

No indicator code changed and no indicator completion credit is awarded by this Gate 39 audit.

- Stage 1: 30/40 = 75% provisional.
- Stages 2–6: unscored.
- Gate 10: 10/10 ORANGE / 0 CLOSED.
- Overall project percentage: not established; M1–M8 weights remain unapproved.
- Indicator aggregate percentage: not established; no approved weighted denominator.

## Cost and change boundary

ZERO COST maintained. No Vercel/Cloudflare deployment, paid provider, Termux operation, dependency change, production activation, or `main` modification. This batch changes documentation only because the safe implementation requires a provider-timeout/retry design and failure-matrix acceptance before changing runtime behavior.
