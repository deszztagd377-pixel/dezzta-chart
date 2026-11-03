# Instrument Identity vs. Versioned Metadata — Architecture Decision

**Status:** Accepted; SQLite schema v3 is implemented and its code/test commit passed the complete GitHub Actions pipeline.

## Decision

Separate stable instrument identity from time-varying descriptive and trading metadata. A canonical UUID identifies the logical instrument and must survive provider reconnects, metadata refreshes, and process restarts. It must never be regenerated from a ticker or provider ID.

### Layer A — canonical identity

Keep stable identity fields: registry-issued UUID, asset class, instrument type, verified canonical venue, stable identity/contract key, creation time, and lifecycle state. Ordinary provider refreshes must not rewrite identity. Identity corrections require explicit audited registry operations.

The current `CanonicalInstrument` model still contains descriptive/trading fields for compatibility with the existing registry contract. Those rows are immutable. New time-varying authoritative metadata belongs in Layer B; do not mutate canonical rows to apply provider refreshes.

### Layer B — metadata revisions

The SQLite `instrument_metadata_revisions` table (introduced in schema v2) stores versioned metadata payloads with:

- canonical ID and source provenance (`source_kind`, `source_name`, optional dataset);
- source event timestamp (nullable) and backend receive timestamp;
- effective-from/effective-to timestamps;
- validity status (`known` or `historical_unknown`);
- payload schema version and validated JSON payload.

Known intervals use half-open semantics `[effective_from_ns, effective_to_ns)`. Overlapping known intervals for the same canonical ID and source identity are rejected at the database boundary; adjacent intervals are allowed. An open interval can be closed once, without modifying its payload or provenance. Revisions cannot otherwise be updated or deleted.

A historical-unknown baseline has no fabricated effective timestamps. The migration timestamp records when the legacy payload was copied, not when that metadata became true.

The v2 migration, typed SQLite repository API, and ordered transition path are implemented. The repository supports append, list, as-of resolution, one-time closure of an open revision, and atomic supersession of the current source revision. Exact event replays are idempotent, including replays after a later revision has closed the original interval. Older events and conflicting events at the same effective timestamp are rejected without changing the active revision. Live provider ingestion is not yet connected.

`backend/app/instrument_registry.py` now enforces option-underlying relationships in SQLite. An option can be registered only after its underlying canonical instrument exists, and an option cannot reference another option as its underlying. The database automatically records the relationship on canonical option insertion, including direct SQL insertion attempts; relationship rows are immutable and protected by foreign keys. The v2-to-v3 migration backfills existing options and rolls back entirely if any legacy option references a missing underlying.

`backend/app/instrument_events.py` adds a coordinated provider-definition event repository. One call applies a provider mapping and its matching provider metadata revision in a single `BEGIN IMMEDIATE` transaction. It closes the previous open mapping and metadata intervals, inserts both new rows, and commits only when both succeed. Exact paired replays remain idempotent after supersession; partial replays, stale mapping events, and stale metadata events are rejected. This is an event-level persistence primitive, not a Databento feed adapter or a complete ingestion pipeline.

### Layer C — provider mappings

Keep provider mappings separate: provider, dataset, publisher ID, provider instrument ID, raw symbol/symbology type, canonical ID, validity interval, and mapping provenance. Resolve only with provider + dataset + publisher + instrument ID + event timestamp. Unknown or ambiguous mappings fail closed.

## Transaction and consistency rules

For each provider definition event, the eventual ingestion workflow must validate and normalize; resolve or create canonical identity using an explicit identity-key policy; close prior mapping/revision intervals only for authoritative, strictly newer events; insert mapping and metadata revision; then commit atomically. On any failure, roll back the complete event.

Duplicate identical events should be idempotent. Out-of-order events must not replace newer metadata. Conflicting events at the same effective timestamp must be rejected or quarantined. Conflicting source claims must retain provenance and must never be silently merged or arbitrarily selected.

## Canonical identity key policy

Never use a raw ticker alone. For dated futures, the candidate key must include verified venue, product/root, expiry, and contract type. Venue must come from authoritative product/venue metadata; do not infer it from a broad dataset name. For crypto spot, include venue + base + quote + market type. For FX, define the pair convention and quote basis. For options, include underlying + expiry + right + strike + contract terms. If required authoritative fields are missing, reject/quarantine rather than invent values.

## Migration v1 → v2

The migration is implemented in `backend/app/instrument_registry.py` and runs when a file-backed v1 registry is opened:

- Adds `instrument_metadata_revisions`, indexes, constraints, and overlap/append-only triggers.
- Copies each existing canonical payload as a `legacy_migration` baseline.
- Preserves existing canonical instrument and provider mapping rows.
- Marks migrated metadata `historical_unknown` and leaves source/effective event timestamps NULL.
- Uses a transaction so a failed migration rolls back the schema changes and leaves the database at v1.
- Sets `PRAGMA user_version = 2` only after successful migration.

## Migration v2 → v3

The v2-to-v3 migration creates `canonical_instrument_relationships`, foreign keys, validation triggers, and immutable relationship protections. It backfills each existing option's `underlying_canonical_id` from its canonical payload. If a legacy option has a missing or invalid underlying, the migration's relationship validation fails and rolls back completely, leaving the database at schema v2. Successful migration sets `PRAGMA user_version = 3`.

Migration and interval behavior are covered in `backend/tests/test_instrument_registry.py`, including data preservation, reopen idempotency, rollback, half-open intervals, overlap rejection, and append-only enforcement. Repository behavior is covered in `backend/tests/test_instrument_metadata.py`, including persistence, exact replay idempotency, atomic interval transitions, out-of-order rejection, same-time conflict rejection, independent source timelines, as-of resolution, and forced insert-failure rollback. Cross-table event behavior is covered in `backend/tests/test_instrument_events.py`, including paired mapping/metadata insertion, paired interval closure, replay after supersession, partial replay rejection, stale-event rejection, and rollback when metadata insertion fails after the previous mapping and metadata intervals have been closed.

## Validation checkpoint

At commit `dcbde9fbd80dac590faadd89ac68b65d1754e0ee`, the GitHub Actions workflow `DEZZTA CHART - Automated Tests` completed successfully, validating the cross-table provider-definition event implementation. The schema-v3 implementation and tests at commit `6f695f123b39994672d662728c018ca938c1923d` also passed workflow run `41627908763`: frontend unit tests, frontend build, backend tests, and Docker image build all completed successfully. Later commits through `3516e68be0bdb2ddea45d9fd30f390c43a0b52a2` changed documentation only.

## Non-goals

This design does not claim live Databento data, broad multi-asset coverage, exchange licensing, public catalog APIs, Firebase auth, per-series entitlements, frontend WebSocket delivery, or PostgreSQL multi-instance readiness. No live market feed has been integrated by this migration.


## Canonical option relationships (schema v3)

Option identity contains `underlying_canonical_id`. Schema v3 materializes this reference in `canonical_instrument_relationships` rather than relying only on JSON payload validation.

- Relationship type is `underlying`.
- The source must be an option; the target must already exist and must not itself be an option.
- Both endpoints are protected by foreign keys; self-reference is rejected.
- Relationship rows are immutable and cannot be deleted.
- The canonical option payload and its relational edge are created in the same SQLite statement transaction by a database trigger.
- Migration from v2 backfills existing option payloads. A missing or invalid legacy underlying is treated as a data-integrity fault and causes the complete migration to roll back; it is never silently repaired or guessed.

This relationship layer is intentionally narrow. It does not yet model option chains, corporate actions, futures continuous-contract rolls, or market-data events.
