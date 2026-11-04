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
