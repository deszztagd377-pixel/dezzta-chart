# Batch 93 — consumer receipt persistence foundation

**Date:** 27 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Exact source/test SHA:** `8691fd631a82218f0f0ebb71546d2e6ed40d8baf`  
**State:** GREEN for synthetic-proof persistence slice; production WebSocket ACK remains YELLOW  
**Cost:** ZERO COST.

## Implemented and verified

- Added `commitConsumerReceipt`, a SQLite `transactionSync` operation.
- Validates canonical series key, bounded consumer identifier, generation, sequence and lowercase SHA-256 event digest.
- Verifies durable generation/high-water, retention boundary and exact persisted event digest before receipt writes.
- Receipt is monotonic per (series_key, consumer_id): lower sequence returns `ack_regression`; same sequence + same digest is idempotent; changed digest returns `digest_mismatch`; newer sequence increments receipt_version.
- Added authenticated synthetic-proof `/__proof/ack` and internal DO route.
- Real-workerd Miniflare test covers first receipt, identical retry, regression rejection and digest mismatch against SQLite.

## Exact-head CI

All four required workflows passed on exact SHA `8691fd631a82218f0f0ebb71546d2e6ed40d8baf`:
- Automated Tests [45923131065](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45923131065) — SUCCESS
- CodeQL [45923130942](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45923130942) — SUCCESS
- Full Git History Secret Audit [45923131029](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45923131029) — SUCCESS
- OCI ARM64 [45923131051](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45923131051) — SUCCESS

## Security boundary

The proof endpoint requires the synthetic proof bearer token, but `consumerId` is caller-supplied. This is acceptable only for isolated synthetic proof testing. It is NOT an authenticated production user identity. Do not wire this to production WebSocket ACK frames until a trusted identity source binds the consumer ID.

## Remaining YELLOW exit criteria

- Define owner-authenticated stable consumer identity.
- Add WebSocket ACK request/response frames and client ACK behavior only after identity binding.
- Add concurrent receipt/compaction, rollback and malformed persisted receipt fault injection.
- Public WSS and Android device E2E remain separate acceptance gates.
