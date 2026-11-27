# Batch 93 — consumer receipt persistence foundation

**Date:** 27 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Base source/test SHA:** `1e3d5b1af40756411ca42cbbf61779a0516e5ceb`  
**State:** synthetic-proof-only implementation candidate; exact-head CI pending  
**Cost:** ZERO COST.

## Implementation

- Added `commitConsumerReceipt`, a SQLite `transactionSync` operation.
- Validates canonical series key, bounded consumer identifier, generation, sequence and lowercase SHA-256 event digest.
- Verifies the current durable generation/high-water, retention boundary and exact persisted event digest before writing a receipt.
- Persisting a receipt is monotonic per (series_key, consumer_id): lower sequence returns `ack_regression`; same sequence + same digest is idempotent; changed digest returns `digest_mismatch`; newer sequence increments receipt_version.
- Added authenticated `/__proof/ack` and internal DO route. These are synthetic-proof test routes, not production WebSocket ACK endpoints.
- Miniflare test covers first receipt, identical retry, regression rejection and digest mismatch against real workerd SQLite.

## Security boundary

The proof endpoint requires the synthetic proof bearer token, but its consumerId is supplied by the caller. That is acceptable only for isolated synthetic proof testing. It is NOT an authenticated production user identity. Do not wire this to production WebSocket ACK frames until a trusted identity source (e.g. validated owner identity callback) binds the consumer ID.

## Acceptance

YELLOW until exact-head Automated Tests, CodeQL, full-history secret audit and OCI ARM64 all pass. Production ACK/RESUME and public WSS remain YELLOW.
