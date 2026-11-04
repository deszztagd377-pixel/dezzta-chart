# Instrument Identity vs. Versioned Metadata — Architecture Decision

**Status:** Accepted; SQLite schema v5, durable Databento definition synchronization, and regression tests are committed on the working branch. Latest synchronization CI validation passed.

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

## Canonical identity uniqueness (schema v4)

Schema v4 adds a SQLite-generated, virtual `identity_key` column and a unique index. The key is derived from immutable canonical payload fields, not provider symbols or provider instrument IDs. It is venue-scoped: otherwise-identical instruments at different venues remain distinct canonical identities.

Identity components are type-aware:

- Equity, ETF, and index: asset class, instrument type, venue, and normalized symbol.
- Crypto spot and FX pairs: asset class, instrument type, venue, base currency, and quote currency. Provider-specific pair-symbol formatting does not create a second identity.
- Crypto perpetual: the pair identity plus required authoritative settlement currency and contract multiplier.
- Dated futures: venue, product/root symbol, expiration date, and required authoritative settlement currency and contract multiplier.
- Options: venue, underlying canonical UUID, expiration date, call/put right, normalized strike, and required authoritative settlement currency and contract multiplier. The provider-specific option symbol is not used as identity.

The generated key is indexed uniquely inside SQLite, so concurrent repository writes and direct SQL inserts cannot register a second UUID for the same venue-scoped identity. A different venue creates a different identity. The canonical UUID remains registry-issued and is never computed from the key.

The v3-to-v4 migration validates required identity fields, then adds the generated column, unique index, and direct-SQL validation trigger in one transaction. A legacy derivative missing settlement currency or contract multiplier, an incomplete pair, or a duplicate identity causes migration to abort and roll back; it never selects a winner, deletes a row, or merges histories. Such records require authoritative enrichment or explicit, audited reconciliation before migration can proceed. New perpetual, future, and option records require authoritative settlement currency and contract multiplier.

This key is intentionally based only on fields currently modeled by `CanonicalInstrument`. Product-specific deliverables, complex option adjustment terms, FX composite-source definitions, and continuous-futures roll methodology require dedicated typed models and must not be guessed from display symbols.

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


## Databento definition field capture (2026-11-04)

The record adapter captures the following additional provider fields without assigning semantics beyond the documented schema:

- Venue and product descriptors: `exchange`, `asset`, `security_type`, and `underlying`.
- Contract-size and currency descriptors: `unit_of_measure_qty`, `unit_of_measure`, `currency`, `settl_currency`, and `contract_multiplier`.
- Lifecycle and effective-time context: `security_update_action`, `activation`, and `ts_event`.
- Price/lot metadata: `display_factor`, `min_price_increment`, `min_lot_size`, and `min_lot_size_round_lot`.

Character fields are decoded from null-padded ASCII bytes. Numeric values are preserved in their original DBN representation; in particular, fixed-point fields such as `unit_of_measure_qty`, `display_factor`, and `min_price_increment` are not converted in this low-level adapter. Conversion must apply the documented 1e-9 scale exactly once.

Databento documents `unit_of_measure_qty` together with `unit_of_measure` as the contract size, `settl_currency` as the settlement currency when it differs from `currency`, and `exchange` as the exchange identifier. Definitions are point-in-time events. The adapter retains action and timestamp fields. The in-memory event path now processes Add (`A`), Modify (`M`), and Delete (`D`) in stable event-time order, closes resolver mapping windows at exclusive event timestamps, and retains delete tombstones to prevent stale resurrection.

Sources:
- https://www.databento.com/docs/schemas-and-data-formats/instrument-definitions
- https://www.databento.tech/blog/definition-schema-updates-may

This adapter expansion is not the provider-to-registry integration milestone. Persistent canonical registration and atomic mapping/metadata event application remain pending. A contract must be quarantined if required identity or contract metadata is absent or ambiguous; no multiplier, venue, settlement currency, or validity interval may be inferred from its ticker or dataset name.


## Lifecycle event processing milestone (2026-11-04)

- `security_update_action` is now required by the low-level Databento adapter; deletion records do not need an expiration field.
- `InstrumentCatalog.apply_definition_event` handles Add, Modify, and Delete records. Delete events only require publisher ID, instrument ID, and event timestamp.
- Provider refresh applies historical records in stable ascending `ts_event` order. Equal-timestamp records preserve provider order.
- Resolver mapping intervals close at the event timestamp (exclusive). A subsequent Modify can open a new mapping for the same provider identity, and Delete closes the current mapping. Duplicate/stale events do not mutate the catalog.
- This milestone is still in-memory catalog/resolver processing. It does **not** yet create canonical UUIDs or persist the Databento mappings and metadata revisions in SQLite.
- A later persistent synchronizer must reconcile the canonical model's `contract_multiplier` field with Databento's distinct `unit_of_measure_qty` (contract size) and `contract_multiplier` (deliverable multiplier). Do not overload one field or infer missing terms without an explicit model decision.

Additional source:
- https://databento.com/docs/schemas-and-data-formats/instrument-definitions

## Schema v5 — futures identity, contract terms, and durable definition journal

Schema v5 makes a deliberate distinction between a dated futures instrument's stable identity and provider-specific contract terms:

- A dated future is identified by verified venue, product/root, expiry, and settlement currency. Its identity key no longer includes `contract_multiplier`.
- Futures may therefore be registered without populating the legacy `CanonicalInstrument.contract_multiplier` field. That field remains available for compatibility, but Databento contract-size and deliverable-multiplier values must not be copied into it by assumption.
- Perpetuals and options retain their existing authoritative settlement-currency and multiplier requirements. Option identity continues to include its contract terms.
- The migration rebuilds the generated identity key and unique index inside one transaction. If removing futures multiplier from the key reveals duplicate canonical identities, the migration aborts and rolls back; it never merges UUIDs or histories.
- Existing v4 canonical payloads are preserved. The migration does not rewrite legacy metadata or fabricate missing terms.

Schema v5 also adds `provider_definition_events`, an append-only SQLite journal for source Add (`A`), Modify (`M`), and Delete (`D`) records. Each record stores the provider/dataset/publisher/instrument key, source event timestamp, explicit source order for equal timestamps, action, raw symbol, exact JSON payload, payload SHA-256, receive timestamp, processing state, and optional canonical UUID or quarantine error.

`SQLiteProviderDefinitionJournal` supports exact idempotent replays, rejects conflicting payloads at the same source-order key, preserves raw DBN fixed-point integers, lists pending records in deterministic order, and allows only a one-way pending → applied/quarantined state transition. Journal payloads are retained when a record is quarantined. The journal is wired into the historical Databento definition refresh path through `DatabentoDefinitionSynchronizer`. Marking a record applied occurs only after the corresponding mapping/metadata registry transaction succeeds. This integration does not establish that a live Databento session has been configured or validated.

Databento fields such as `unit_of_measure_qty`, `unit_of_measure`, `contract_multiplier`, `contract_multiplier_unit`, `currency`, and `settl_currency` remain distinct source fields. Fixed-point integers remain raw in the journal and adapter; any conversion must use the documented scale exactly once. Missing or ambiguous authoritative fields must be quarantined rather than inferred from a ticker or dataset name.

## Databento definition normalization — first strict futures adapter

`backend/app/databento_definition_normalizer.py` now provides a pure, strict adapter for dated futures definitions in the initial CME scope. It requires the provider's explicit `asset` root, `exchange`, instrument class, expiration, currency, publisher/instrument IDs, action, and event timestamp. It never parses a futures root from the ticker when the authoritative root is absent.

Settlement currency follows Databento's documented override semantics: use `settl_currency` when supplied, otherwise use `currency`. Expiration is converted from Unix nanoseconds to a UTC calendar date using integer arithmetic, without floating-point timestamp conversion.

Provider-native contract terms are retained independently in versioned metadata: raw `unit_of_measure_qty` plus its 1e-9 scale, raw `contract_multiplier` in provider-native integer units, raw tick increment plus its scale and display factor, unit, currency, lot-size fields, and source timestamps. No floating-point conversion or assumption that contract size equals multiplier is performed.

Delete records are normalized with their minimal lifecycle key and do not require contract identity fields. Unsupported instrument classes, malformed timestamps, and missing authoritative identity values fail closed so the caller can persist and quarantine the original event.

The adapter is wired into `ProviderManager.refresh_definitions` through `DatabentoDefinitionSynchronizer`. The synchronizer journals original source payloads, allocates/reuses canonical UUIDs by the registry identity key, applies Add/Modify mapping and metadata transitions atomically, closes Delete intervals atomically, and marks journal events applied only after successful persistence. Pending records can be replayed after a restart, and the in-memory resolver can be rebuilt from persisted provider mappings.


## Durable Databento definition synchronization — implemented foundation (2026-11-04)

`backend/app/databento_definition_sync.py` is the orchestration boundary between provider records and the persistent instrument model.

Processing order:

1. Historical definition records are converted to plain mappings by the low-level adapter and appended to `provider_definition_events` before canonical resolution.
2. Pending journal records are replayed in deterministic event-time/source-order order.
3. Add/Modify records are strictly normalized. Existing point-in-time mappings are reused where appropriate; otherwise the registry identity key is searched and a registry-issued UUID is created only when no matching identity exists.
4. Canonical identity fields are checked against the immutable registered instrument. A provider Modify cannot silently rewrite canonical identity.
5. `SQLiteProviderDefinitionEventRepository.apply_event` commits the new provider mapping and matching metadata revision, including closure of prior intervals, in one SQLite transaction.
6. Delete records close the active mapping and its corresponding provider metadata interval in one SQLite transaction.
7. The resolver/catalog projections are updated, then the journal record is marked applied. If the process stops after the database transaction but before the journal state update, replay recognizes the exact persisted transition and completes the journal state idempotently.
8. At provider startup, the point-in-time resolver can be restored from canonical instruments and their persisted provider mappings.

Failure behavior:
- Missing or unsupported authoritative identity fields, stale transitions, unknown Modify/Delete keys, and conflicting canonical identity changes are quarantined; the original event payload remains in the append-only journal.
- SQLite operational failures are not converted into permanent quarantine decisions; they propagate so the pending event can be retried.
- Equal event timestamps retain the stable input iteration order in the journal. The current mapping/metadata interval model requires strictly increasing effective timestamps for successive transitions of the same provider key. A second conflicting transition at the same timestamp is quarantined rather than assigned a fabricated timestamp or silently reordered.
- The adapter currently derives a per-key ordinal from stable provider record iteration for equal timestamps because it does not yet consume a universal provider sequence field. This ordinal is deterministic for an identical fetched batch; it must not be described as an exchange-provided sequence number.

Validation: GitHub Actions run [41827550928](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41827550928) passed frontend unit tests, frontend production build, backend tests, and backend container image build at replay-hardened code commit `3e3fcd715d31c00cd2884a7f5ce5510d83daa6ff`. The initial integration checkpoint also passed in run [41826984399](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41826984399).

Scope boundary: this milestone persists instrument definitions, canonical identities, provider mappings, and metadata revisions. It does not persist OHLCV bars or coverage state, configure a real Databento account, prove live delivery, add a periodic definition refresh scheduler, or deploy/validate the backend in production.
