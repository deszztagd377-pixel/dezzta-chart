# Educational Simulated Footprint Contract

Status: first deterministic aggregation engine added; CI verification pending.
Branch: `phase-2/market-data-foundation`

## Scope

This module is an offline educational/test fixture only. It accepts synthetic events supplied by tests or a future clearly labelled simulator. It has no provider adapter, network connection, broker integration, order entry, or live-market subscription.

The UI must preserve the `SIMULATED` label whenever these values are shown. Synthetic values must never be presented as actual market observations.

## Event model

Each synthetic event contains:

- `eventId`: stable identifier used for replay deduplication.
- `timestampMs`: event-time Unix timestamp in milliseconds.
- `priceTicks`: integer price-step index, avoiding floating-point grouping.
- `quantity`: positive integer simulation units.
- `aggressorSide`: `buy`, `sell`, or `unknown`.

Unknown side remains in its own volume field. The engine must not infer or guess a side.

## Aggregation contract

- Default interval is one second.
- Every accepted event updates its bucket immediately; there is no need to wait for the interval to close to update the in-memory snapshot.
- Bucket assignment uses event time, not arrival time.
- Late and out-of-order events stay in their original event-time bucket.
- Cells are grouped by bucket start and integer price step.
- Buy, sell, and unknown quantities remain separate; delta is buy minus sell.
- Repeated event IDs are ignored.
- Invalid events are rejected without mutating state.
- The deduplication ledger is bounded. At capacity, the engine rejects new unique events rather than evicting IDs and risking replay double-counting.
- Snapshots are deterministic and sorted by bucket time ascending, then price descending.

## Verification coverage

The unit tests cover:

1. Immediate one-second cell updates after each event.
2. Event-time bucketing under late/out-of-order arrival.
3. Larger fixed intervals while retaining per-price cells.
4. Duplicate replay protection.
5. Unknown aggressor side preservation.
6. Invalid event rejection and bounded-ledger behavior.
7. Reset behavior.
8. Explicit simulated-origin metadata.

## Important limitations

This engine demonstrates aggregation mechanics only. It does not establish the correctness of any real-world trade classification, provider timestamp, feed freshness, latency, or market interpretation. It must not be wired to live provider or broker data as part of this educational stage.

Before implementing the visual Footprint layout, obtain the user's preferred visual reference. The ordinary candlestick layout must remain unchanged when the Footprint view is not explicitly enabled.
