# DEZZTA CHART — Batch 92 Canonical Series Identity Decision

**Date:** 26 November 2026  
**Status:** Engineering decision for the synthetic proof implementation  
**Scope:** additive design; no runtime code/schema changed in this commit  
**Cost:** ZERO COST.

## Problem

The series key format is `synthetic:<dataset>:<rawSymbol>:<timeframe>`, but the canonical Batch 91 digest input also binds `publisherId`, `instrumentId`, `seriesType`, `bucketPolicy`, `calendarId`, and `calendarVersion`. A client subscription currently supplies the full series identity; the internal emit request supplies only seriesKey and sequence. The event digest therefore cannot be authoritatively and deterministically constructed when no subscriber is connected. Generating one event per socket would produce multiple payload/digest identities for one logical sequence and is unacceptable for durable replay.

## Decision B92-ID-01 — Persist one immutable canonical identity per series key

Introduce an additive SQLite identity registry (migration v2) keyed by `series_key`, storing the exact canonical identity JSON and its SHA-256 identity digest. The identity is immutable for the life of the series key. A request that supplies a different canonical identity for an already registered key fails closed with `series_identity_conflict`; never overwrite identity based on whichever client connected last.

The first valid identity registration must be explicit and pass `validateSyntheticCanonicalSeries`, with an exact match between the identity's seriesKey, dataset, rawSymbol and timeframe and the parsed key. Store the canonical JSON representation with fixed field order, not arbitrary incoming object serialization.

## Registration paths

- REST snapshot: the Worker already receives a complete explicit synthetic series identity. Register-or-verify it before returning the snapshot.
- WebSocket subscribe: register-or-verify the complete identity before creating the snapshot or enabling fan-out.
- Internal synthetic emit: require the proof-only request to include the complete canonical `series` object as well as `seriesKey` and sequence. Validate equality and register-or-verify it before constructing the canonical event. The external proof endpoint remains authenticated and synthetic-only.
- Ticket issuance: does not establish identity; a ticket authenticates a series key only. No event may be committed until an identity is registered.

This makes event generation independent of subscriber count and connection timing. No default or invented publisher/instrument IDs are permitted.

## Event identity and persistence

For each accepted sequence, build exactly one Batch 91 canonical update envelope using the immutable registered identity. Persist that exact JSON payload and its existing canonical event digest with the sequence in the same SQLite transaction as high-water advancement. Fan-out the persisted payload bytes to every eligible socket. Subscribers must match the registered identity exactly; mismatches receive a non-retryable protocol error and are not subscribed.

## Migration and compatibility

Migration v2 is additive and must preserve schema v1 tables and all legacy KV ticket/cursor keys. Existing series with no registered identity remain unregistered until an explicit REST snapshot, subscribe, or emit request provides the full identity. Do not infer publisherId/instrumentId from the series key. A pre-existing high-water cursor is bootstrapped independently and cannot be rewound by identity registration.

## Required tests

Add cases for:
1. First identity registration and stable round-trip.
2. Same identity with reordered input object keys resolves to identical canonical bytes.
3. Same key with different publisherId or instrumentId is rejected.
4. Invalid key/identity mismatch is rejected before registry mutation.
5. Emit with no connected sockets persists one canonical event and digest.
6. Multiple subscribers receive byte-identical persisted payload.
7. A subscriber with conflicting identity cannot receive events.
8. DO eviction preserves registry identity, event rows and high-water.
9. Legacy series cursor bootstrap and identity registration can occur in either order without high-water rewind.
10. Existing ticket issuance/consumption behavior remains unchanged.

## Gate

This decision resolves the design ambiguity that blocked a safe durable event implementation. It does not claim Batch 92 runtime implementation is complete. Implement schema v2, identity registration, atomic event commit and replay together with tests; do not ship a partial state where event fan-out is still per-subscriber but persistence claims one canonical event.


## Stable event retry input

The authenticated synthetic proof emit request must carry the full canonical `series` object, `seriesKey`, sequence, and canonical decimal-string `emittedAtNs` (1–32 digits). The Worker validates that the supplied identity maps exactly to the key and that the timestamp is valid before event construction.

The same sequence retry is idempotent only when the stored event digest AND exact serialized payload bytes equal the newly constructed event. The caller must reuse the same `emittedAtNs` on retry; a changed timestamp changes the canonical bar receive time and digest and therefore conflicts. Persisted payload text is the authoritative fan-out/replay body. Never regenerate a stored event using a new timestamp.

This makes the idempotency contract deterministic without inventing server identity values or weakening the Batch 91 digest contract.
