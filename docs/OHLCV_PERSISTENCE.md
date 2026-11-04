# OHLCV Persistence and Restart Recovery

Status: implemented foundation; final branch-head CI and operational load validation are tracked separately.

## Storage boundary

`SQLiteOhlcvStore` stores normalized base and derived bars in the same file-backed SQLite database used by the canonical instrument registry. It creates additive `ohlcv_bars` and `ohlcv_store_state` tables and does not change the registry's `PRAGMA user_version`.

The persistent bar key matches the in-memory pipeline identity:

- provider
- dataset
- publisher ID
- instrument ID
- series type
- timeframe
- bucket start timestamp

Raw symbol is stored and checked as a conflict guard. A different raw symbol cannot silently take over an existing provider instrument identity.

## Precision and ordering

- Prices and volume are stored as exact decimal text; no SQLite floating-point conversion is used.
- Event, receive, provider-out, and bucket timestamps remain integer nanoseconds.
- Sequence value and sequence origin are persisted separately.
- The local ingest sequence high-water mark is kept outside the retained bar rows. Pruning old bars therefore cannot cause the next backend process to reuse a smaller local sequence.
- Provider-origin bars take precedence over derived bars for the same bar identity.
- Exact duplicates, stale revisions, symbol conflicts, and expired late bars are not written.
- A derived bar may be revised with the same event/sequence ordering key when its completeness label changes.

## Write and recovery order

1. Normalize an incoming provider record into an `OhlcvBar`.
2. Commit the base bar to SQLite.
3. Apply the base bar to the single-writer in-memory pipeline.
4. Recompute affected derived timeframes.
5. For each derived bar, commit it to SQLite before the aggregator applies it to memory.
6. Broadcast accepted base/derived bars only after their persistence gate has succeeded.
7. At application construction, load the retained persistent snapshot into the pipeline before the provider consumer starts.
8. Resume local sequence numbering from the durable high-water mark.

This order ensures that a process stop after a SQLite commit but before the corresponding in-memory mutation can recover from the persisted row on restart. A failed persistence gate does not publish the bar as an accepted stream update and marks ingestion degraded.

## Retention

Retention is bounded per provider series and timeframe using the same configured limits as the in-memory pipeline defaults. Pruning removes the oldest bucket rows for that series. A new bar older than the oldest row is rejected once the retained series is full, matching the in-memory pipeline's expired-bar behavior.

The current storage limits are in `backend/app/ohlcv.py` (`DEFAULT_RETENTION` and `MIN_RETENTION`). Retention is a safety bound, not a promise of a particular historical coverage duration; duration depends on the active timeframe and incoming bar density.

## Current limitations

- Coverage intervals and known data gaps are not yet persisted.
- No durable outbox/event log exists for WebSocket client update replay. Clients still need snapshot/resubscription recovery after disconnect.
- Historical gap detection and bounded automatic backfill orchestration are not yet implemented.
- SQLite persistence has unit/integration coverage but has not yet been benchmarked under sustained high-rate market data or multi-process write load.
- Live Databento credentials, exchange entitlements, and delivery have not been validated.
- The backend deployment must use a persistent writable volume for the configured SQLite database path. An ephemeral container filesystem would not provide restart durability across replacement deployments.

## Tests

See `backend/tests/test_ohlcv_store.py`, `backend/tests/test_api.py`, and `backend/tests/test_aggregation.py` for exact-value round-trip, revision precedence, retention, late-event rejection, shared-schema compatibility, sequence recovery, application restart restoration, and the derived-bar persistence gate.


## Durable coverage and explicit gaps

`SQLiteCoverageTracker` adds `ohlcv_coverage_intervals` and `ohlcv_coverage_meta` tables to the same SQLite file. The existing instrument-registry schema version is unchanged.

- Covered intervals and explicit gap intervals are half-open nanosecond ranges scoped to the exact provider/dataset/publisher/instrument/series/raw-symbol identity.
- A successful historical query window adds covered time and removes only the overlapping portion of gap intervals.
- Ingestion queue overflow carves the affected range out of covered time and records an explicit gap, including when no earlier coverage interval exists.
- Covered and gap interval counts are bounded. Truncation counts are durable. A failed SQLite write restores the prior in-memory interval state.
- Coverage is restored when the application is constructed, before provider ingestion begins.

### Bounded gap recovery

`ProviderManager.recover_gaps(max_gaps=...)` is an explicit service operation. It does not make an automatic network request during application startup and is not exposed as a public API route.

For each selected gap, it:
1. Requires a matching resolver mapping for the exact provider coverage scope.
2. Intersects the gap with the mapping's validity interval.
3. Splits the request into spans no larger than `historical_max_span_hours`.
4. Uses the existing bounded historical query windows and explicit raw-symbol symbology.
5. Removes gap portions only when a historical window completes successfully and its coverage is persisted.
6. Leaves unresolved gaps intact and reports them as skipped/remaining.

The operation is bounded by `max_gaps`, the configured maximum historical span, and the existing per-query window size. It must only be invoked after valid provider credentials, exchange/data entitlements, and historical-access settings have been separately reviewed.

### Remaining recovery work

- Automatic scheduling/triggering of gap recovery is not implemented.
- The WebSocket stream still has no durable event outbox or replay cursor. Clients must resnapshot after reconnect.
- Coverage and gap persistence has regression tests but no sustained write-rate or multi-process benchmark.
