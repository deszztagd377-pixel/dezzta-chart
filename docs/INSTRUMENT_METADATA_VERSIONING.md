# Instrument Identity vs. Versioned Metadata — Architecture Decision

**Status:** Accepted for implementation planning; schema migration is not yet applied.

## Decision

Separate stable instrument identity from time-varying descriptive and trading metadata. A canonical UUID identifies the logical instrument and must survive provider reconnects, metadata refreshes, and process restarts. It must never be regenerated from a ticker or provider ID.

### Layer A — canonical identity

Keep stable identity fields: registry-issued UUID, asset class, instrument type, verified canonical venue, stable identity/contract key, creation time, and lifecycle state. Ordinary provider refreshes must not rewrite identity. Identity corrections require explicit audited registry operations.

### Layer B — metadata revisions

Store changeable metadata in append-only, versioned records: canonical ID, source/provider and dataset, source event time, backend receive time, effective-from/effective-to timestamps, display name, currencies, expiry, multiplier, tick size, quantity increment, option terms, session calendar, revision status, and payload schema version.

Use half-open effective intervals [from, to). Never overwrite an earlier revision. A new authoritative definition closes the prior interval and inserts the new revision in one transaction. Reject ambiguous overlapping revisions from the same authoritative source. Preserve conflicting source claims with provenance or resolve them through an explicit source-priority policy; never silently choose one.

### Layer C — provider mappings

Keep provider mappings separate: provider, dataset, publisher ID, provider instrument ID, raw symbol/symbology type, canonical ID, validity interval, and mapping provenance. Resolve only with provider + dataset + publisher + instrument ID + event timestamp. Unknown or ambiguous mappings fail closed.

## Why this must precede provider integration

The current CanonicalInstrument object contains both stable identity and changeable trading metadata, while the SQLite registry makes its entire serialized record immutable. Directly wiring provider refreshes into that row would either reject legitimate corrections (for example tick-size updates) or weaken identity immutability. Neither is acceptable. The next implementation should add a schema-versioned metadata-revision table and repository API rather than mutating canonical rows.

## Transaction and consistency rules

For each provider definition event: validate and normalize; resolve or create canonical identity using an explicit identity-key policy; close prior mapping/revision intervals only for authoritative, strictly newer events; insert mapping and metadata revision; commit atomically. On any failure, roll back the complete event. Duplicate identical events are idempotent. Out-of-order events cannot replace newer metadata. Conflicting events at the same effective timestamp are rejected or quarantined.

## Canonical identity key policy

Never use a raw ticker alone. For dated futures, the candidate key must include verified venue, product/root, expiry, and contract type. Venue must come from authoritative product/venue metadata; do not infer it from a broad dataset name. For crypto spot, include venue + base + quote + market type. For FX, define the pair convention and quote basis. For options, include underlying + expiry + right + strike + contract terms. If required authoritative fields are missing, reject/quarantine rather than invent values.

## Migration requirements

The existing SQLite schema is version 1. The next migration should add the metadata revision table, foreign keys, effective-time indexes, provenance and payload versioning while retaining existing canonical and provider mapping rows. Existing rows must not be assigned fabricated historical effective timestamps. Mark their historical validity as unknown until verified source events provide it. Validate foreign keys and interval constraints; rehearse backup and rollback before production.

## Non-goals

This design does not claim live Databento data, broad multi-asset coverage, exchange licensing, public catalog APIs, Firebase auth, per-series entitlements, frontend WebSocket delivery, or PostgreSQL multi-instance readiness.