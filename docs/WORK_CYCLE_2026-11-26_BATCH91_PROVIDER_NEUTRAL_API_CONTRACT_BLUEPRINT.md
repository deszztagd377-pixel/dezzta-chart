# DEZZTA CHART — Batch 91 Provider-Neutral API Contract Blueprint

**Date:** 26 November 2026  
**Status:** DESIGN ONLY — implementation requires owner review  
**Active branch:** `phase-2/market-data-foundation`  
**Code baseline:** `9a2f2b9faebdcaf1e97e93c6dfe85a2c93319fbb`  
**Current documentation HEAD:** `1016a4d533b32240c552e8989b4a4c2bcac8b33f`  
**Cost boundary:** ZERO COST.

## 1. Purpose and scope

Batch 91 defines one provider-neutral market-data wire contract for the existing OHLCV snapshot and WebSocket client. It reconciles the synthetic Cloudflare proof with the already-existing frontend protocol instead of introducing a competing message family.

This batch is contract and validation work only. It does not connect a provider, add a broker, execute trades or orders, deploy a Worker, or claim live market data. The Cloudflare proof remains synthetic-only.

The existing provider-specific Databento MBO DTO in `src/types/marketData.ts` remains separate from the provider-neutral OHLCV transport contract.

## 2. Existing contracts that must be reused

The frontend already defines:
- `OhlcvSnapshotMessage` in `src/types/ohlcv.ts`, with `market_data.ohlcv.snapshot`, version 1, nanosecond timestamps and decimal-string prices/volume.
- `OhlcvStreamSeriesIdentity` and `OhlcvStreamUpdateMessage` in `src/services/ohlcvStreamProtocol.ts`, with `market_data.ohlcv.update`, stream ID, event ID, numeric sequence, emitted-at nanoseconds, operation, finality, series identity and canonical bar.
- `parseOhlcvSnapshot` and `toChartCandles` in `src/utils/ohlcvAdapter.ts`.
- A WebSocket handshake in `src/services/ohlcvWebSocketClient.ts`: `market_data.status` → `market_data.subscribe` → snapshot or replay → updates. It already handles `market_data.ohlcv.replay_started`, `market_data.ohlcv.replay_completed`, `market_data.ohlcv.resnapshot_required`, `market_data.auth.renewed`, and `market_data.pong`.
- REST snapshot request construction in `src/services/ohlcvClient.ts`: `GET /v1/ohlcv` with dataset, publisher ID, instrument ID, raw symbol, timeframe and bucket policy query fields.
- Existing route paths: `/health`, `/v1/market-data/status`, `/v1/ohlcv`, `/v1/auth/websocket-ticket`, and `/ws/market-data`.

These are the compatibility baseline. Do not replace them with a second API family.

## 3. Confirmed mismatch in the synthetic Worker proof

The current Cloudflare proof does not yet implement the frontend protocol:
1. REST `/v1/ohlcv` currently accepts only `seriesKey` and returns `market_data.snapshot`; the frontend requests a fully identified series and expects `market_data.ohlcv.snapshot`.
2. The WebSocket proof sends a snapshot immediately after ticket authentication. The frontend expects a `market_data.status` message first, then sends `market_data.subscribe`.
3. The proof sends `market_data.update` with a string sequence and a minimal synthetic bar. The frontend expects `market_data.ohlcv.update` with a numeric sequence, event ID, emitted-at timestamp, operation, finality, complete series identity and canonical OHLCV bar.
4. The proof parses a JSON object with `type: "ping"` and replies with `type: "pong"`. The frontend sends the literal text frame `ping` and expects JSON `market_data.pong` with version 1.
5. The proof's synthetic bars do not satisfy the existing `OhlcvBarDto` shape or strict snapshot parser.
6. The proof's simplified `dataSource` marker is not a complete provenance envelope.
7. The synthetic proof uses a fixed synthetic subject and proof token; this is not Firebase authentication and must not be wired into the production frontend as if it were.

These mismatches are the reason Batch 91 is required. They are not evidence of live or deployed integration.

## 4. Proposed canonical envelope

### 4.1 Series identity

Reuse the existing `OhlcvStreamSeriesIdentity` fields and add a canonical `seriesKey`:
- `seriesKey`: bounded, deterministic key for one exact series;
- `provider`: explicit source label (`synthetic` in proof mode; provider name only after the provider gate);
- `seriesType`: `contract` or `continuous`;
- `dataset`, `publisherId`, `instrumentId`, `rawSymbol`, `timeframe`;
- `bucketPolicy`, `calendarId`, `calendarVersion` where applicable.

A series identity is immutable for a generation. Any identity mismatch is rejected; it is never silently remapped.

### 4.2 Provenance

Every snapshot, event and status envelope carries explicit provenance:
- `mode`: `synthetic` or `provider`;
- `dataStatus`: `synthetic_only`, `live`, `stale`, `unavailable`, or `error`;
- `provider` and `dataset`: nullable when no provider is connected;
- `asOfNs`: decimal nanosecond string or null.

Rules:
- Synthetic proof must always report `mode: "synthetic"` and `dataStatus: "synthetic_only"`.
- Synthetic proof must report `providerConnected: false` and must never use `live`.
- Provider mode remains unavailable until Batch 94 passes the lawful zero-cost provider gate.
- No generated candle may be described as market data.

### 4.3 Snapshot

Keep the existing `market_data.ohlcv.snapshot` version 1 envelope and add optional durable metadata:
- `generationId`;
- `highWaterCursor` and `retentionFloorCursor` as canonical unsigned decimal strings;
- `snapshotDigest` as lowercase 64-character SHA-256 hex;
- `provenance`.

For the WebSocket snapshot wrapper, preserve the existing `streamId`, numeric `watermark`, and string `cursor` fields. Where all are present, `cursor` and `highWaterCursor` must agree with `String(watermark)`. The retention floor cannot exceed the high-water cursor.

Bars must pass the existing `parseOhlcvSnapshot` validator. Nanosecond timestamps and OHLCV decimal values remain strings until the chart adapter.

### 4.4 Event

Keep `market_data.ohlcv.update` version 1 and extend it with:
- `generationId`;
- `cursor` (canonical decimal string, equal to `String(sequence)`);
- `digest` (lowercase SHA-256 hex);
- `provenance`.

Retain the existing fields: `streamId`, `eventId`, numeric `sequence`, `emittedAtNs`, `operation`, `isFinal`, `series`, and canonical `bar`.

The durable event identity is `(seriesKey, generationId, sequence)`. The digest covers a deterministic canonical representation of the series identity, generation, cursor, event timestamp, operation/finality and canonical payload. The exact byte encoding must be fixed in the implementation and tested with stable test vectors before Batch 92 writes events.

### 4.5 Replay

Keep replay on the existing authenticated WebSocket subscription flow; do not add a parallel REST replay route in Batch 91.

Client request remains `market_data.subscribe` version 1 with optional `cursor`. Add generation/cursor metadata to the existing replay messages:
- `market_data.ohlcv.replay_started`: stream ID, generation, from cursor, through cursor, count, high-water and retention floor;
- zero or more canonical `market_data.ohlcv.update` events;
- `market_data.ohlcv.replay_completed`: generation, count and final cursor;
- `market_data.ohlcv.resnapshot_required`: stable reason, generation, snapshot cursor, high-water and retention floor.

A cursor below the retention floor or a generation mismatch returns `resnapshot_required`; no sequence jump is silently accepted.

### 4.6 ACK and receipt

Define, but do not implement persistence in Batch 91:
- `market_data.ack.request`: consumer ID, series identity, generation ID, cursor, sequence, event digest and receipt version;
- `market_data.ack.response`: accepted/rejected result, committed cursor, receipt version, committed timestamp and correlation ID.

ACK is accepted only for the current generation, a digest-verified event, a monotonic cursor not beyond committed high-water, and a non-regressing receipt version. A server-side committed receipt records protocol acceptance; it does not claim durable storage on a user's device. Batch 93 implements the receipt transaction.

### 4.7 Error

Use one stable error envelope:
- `type: "market_data.error"`, `version: 1`;
- stable machine-readable `code`;
- `retryable`;
- `correlationId`;
- safe `message`.

Initial codes: `invalid_request`, `invalid_series`, `unsupported_version`, `unauthorized`, `forbidden`, `ticket_expired`, `ticket_replayed`, `generation_mismatch`, `cursor_invalid`, `cursor_expired`, `replay_limit_exceeded`, `digest_mismatch`, `ack_regression`, `rate_limited`, `temporarily_unavailable`, `internal_error`.

Never return raw exception details, tokens, ticket values, cookies, private keys or provider credentials.

## 5. Route reconciliation

Keep current frontend paths:
| Path | Batch 91 responsibility |
|---|---|
| `GET /health` | Runtime liveness only; not provider readiness |
| `GET /v1/market-data/status` | Provider-neutral readiness/provenance; explicit synthetic-only state |
| `GET /v1/ohlcv` | Existing exact-series REST snapshot contract |
| `POST /v1/auth/websocket-ticket` | Existing authenticated ticket exchange; synthetic proof remains isolated |
| `/ws/market-data` | Existing status/subscribe/snapshot/replay/update/heartbeat protocol |

Replay remains on WebSocket subscription messages. ACK is defined as a WebSocket control message for later Batch 93 implementation. Do not add duplicate `/v1/series/{seriesKey}/snapshot`, `/events`, or `/receipts` routes in this batch.

Keep `/__proof/emit` synthetic-only and internal `/internal/*` DO routes inaccessible as public application API.

## 6. Implementation scope after approval

1. Add provider-neutral TypeScript interfaces in a new `src/types/marketDataProtocol.ts`; do not overload the Databento MBO DTO.
2. Add strict runtime parsers and deterministic digest test vectors in a dedicated protocol service.
3. Extend existing snapshot/update parsers additively for generation, cursor, digest and provenance metadata.
4. Add Worker-side contract builders/validators in a dedicated `cloudflare/proof/market-data-contract.mjs`.
5. Adapt the synthetic proof to the existing frontend message names, sequence types, canonical bar DTO, status-first handshake and literal ping / versioned pong.
6. Preserve the current route paths and explicit synthetic-only state.
7. Add negative tests for invalid series, version, cursors, digests, timestamps, decimal values, payload bounds, generation mismatch, provenance mismatch and unexpected message order.
8. Do not implement event persistence, replay reads, ACK storage or receipt compaction in Batch 91; those belong to Batches 92–93.

## 7. Acceptance tests

- REST snapshot passes the existing frontend parser for an exact synthetic identity and remains visibly `synthetic_only`.
- WebSocket order is status → subscribe → snapshot or replay → updates.
- Snapshot/update envelopes pass existing validators and preserve all durable metadata.
- Literal `ping` receives `market_data.pong` version 1.
- Replay completion must match declared count and cursor; generation/retention mismatch requests a resnapshot.
- Unknown message types, malformed cursors, invalid digests, cross-series payloads and oversized frames fail closed.
- No live provider, Firebase production identity, broker, order endpoint, deployment or production secret is introduced.
- Exact-head CI must pass on the active branch before Batch 91 is accepted.

## 8. Explicit review gate

This is a scoped design proposal, not implementation approval. No Batch 91 source file has been changed. Review the route mapping, envelope fields, digest byte encoding and synthetic-only compatibility before implementation. Batch 92/93 must not be started until Batch 91's contract is accepted and tested.
