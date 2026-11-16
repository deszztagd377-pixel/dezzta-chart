# DEZZTA CHART — Long-Lived Data Foundation and Evolution Contract

**Status:** Adopted engineering contract; implementation and owner-environment acceptance are tracked separately.  
**Scope:** Canonical instrument identity, market data, OHLCV, alert zones, alert outbox, device registrations, entitlements, backups, restore, and future TradingView-like features.  
**Non-goal:** A promise that one physical database, device, filesystem, cloud vendor, or encryption key will survive forever. The goal is that the product can be upgraded, migrated, recovered, and operated for decades without silently corrupting or abandoning user data.

## 1. Non-negotiable foundation rules

1. **One canonical shared SQLite database per backend deployment.** Durable adapters must use the configured `INSTRUMENT_REGISTRY_DB_PATH`; no feature may quietly create a second authoritative copy.
2. **Canonical identity is stable.** Instruments use canonical IDs. Provider symbols, exchange aliases, display names, and vendor identifiers are mappings with validity/version context, never primary identity.
3. **Exact financial values stay exact.** Prices and quantities that require decimal precision are stored as canonical decimal text or a documented integer scale. Never use binary floating point as the durable source of truth for price, quantity, fees, or P/L.
4. **Time is explicit.** Persist UTC timestamps and source timestamps with named units. Nanosecond source timestamps are signed 64-bit integers only after explicit range validation. Never mix seconds, milliseconds, and nanoseconds in one field.
5. **Events are immutable identities.** Durable outbox events have stable event IDs. Delivery is at-least-once, not exactly-once. Every client side-effect consumer must deduplicate by event ID with a durable retention policy.
6. **Migrations are additive-first and reversible by restore.** Never silently drop, rename, truncate, or reinterpret user data during startup. Destructive transformations require a separate reviewed migration, a verified backup, a fresh-copy rehearsal, and explicit release approval.
7. **No destructive startup repair.** If a database is newer than the running application, malformed, or fails integrity checks, fail closed with a safe diagnostic. Do not reset, recreate, or overwrite the database automatically.
8. **Backups are independent recovery artifacts.** A backup on the same device/disk is not sufficient disaster recovery. Encryption-key custody and independent destination must be proven before production reliance.
9. **Vendor-neutral data ownership.** Provider APIs are ingestion/delivery adapters. Raw vendor IDs must not become the only way to recover canonical application records.
10. **No feature bypasses the shared durability contract.** Chart layouts, footprint, heatmap, indicators, alerts, replay, watchlists, and future analytics must use documented canonical IDs, schema ownership, and migration rules.

## 2. Data-domain ownership

| Domain | Durable owner | Invariant |
|---|---|---|
| Instruments and provider mappings | Instrument registry | Canonical instrument ID survives provider symbol changes |
| Entitlements | Entitlement store | Owner + canonical instrument; no client-supplied owner authority |
| OHLCV and replay cursor | OHLCV store/outbox | Stable event/cursor ordering; exact decimal values |
| Market coverage | Coverage tracker | Explicit source/session/calendar version |
| Session calendars | Versioned immutable artifacts | SHA-256 + release/version metadata |
| Alert zones and trigger state | Price-alert store | Owner-scoped, canonical instrument, deterministic transition |
| Alert delivery outbox | Price-alert store | Stable event ID, lease token/expiry, bounded retry, terminal status |
| Mobile push tokens | Encrypted device store | AES-GCM, owner+installation AAD, no plaintext persistence |
| Backups and restore reports | Backup/restore subsystem | Source read-only; fresh destination; integrity, FK, schema and row-digest checks |

New durable domains must be added to the full-database restore inventory and its representative read/write recovery test before the feature is considered foundationally complete.

## 3. Schema evolution contract

### Required before a domain is declared stable

- A documented schema owner and table inventory.
- Explicit schema version and migration ordering for that domain.
- A migration checksum or equivalent immutable migration identity.
- A clean-install test and an upgrade test from every supported prior schema version.
- A backup-before-upgrade rehearsal on a copy of representative data.
- Tests proving old rows, foreign keys, indexes, triggers, uniqueness, and exact values survive.
- A downgrade policy: if the application binary is older than the database schema, startup refuses to write; it never attempts an unsafe downgrade.
- A documented deprecation window for fields/API contracts and a compatibility adapter where required.

### Migration procedure

1. Identify the current schema and supported source versions.
2. Create a consistent backup to a new path; never overwrite the source.
3. Verify backup integrity, foreign keys, schema digest, and typed row digest.
4. Apply one deterministic migration sequence inside controlled transactions where SQLite permits it.
5. Validate all domain invariants and row counts/digests.
6. Perform a post-migration write/read check on the migrated copy.
7. Preserve the original database and backup until acceptance and retention policy permit retirement.
8. Record migration version, checksum, application version, timestamp, and result without logging row contents or secrets.

Existing repositories currently contain idempotent table creation and additive alert-outbox column migration logic. That is useful compatibility behavior, but it is **not yet a unified, versioned migration ledger for every durable domain**. A central schema-version/migration registry remains a foundation task; do not claim it is complete merely because individual stores use `CREATE TABLE IF NOT EXISTS` or `ALTER TABLE`.

## 4. SQLite operating contract

- Use the same configured database path across durable adapters.
- Keep foreign-key enforcement enabled on every connection that relies on it.
- Use bounded busy timeouts and short write transactions; do not hold SQLite write locks during network calls.
- Network I/O, FCM sends, provider requests, and expensive calculations happen outside database transactions.
- WAL and synchronous settings must be chosen and verified for the actual host/filesystem; never assume Android storage semantics equal Linux CI.
- Monitor database size, WAL growth, free disk, write latency, busy/locked errors, integrity status, and backup age.
- Use SQLite's consistent backup API for live databases; do not copy only the main DB file while WAL is active.
- Run `integrity_check` and `foreign_key_check` on restored copies before switching any service to them.
- Keep the original database immutable during restore rehearsals.

## 5. Event and notification contract

- Event IDs are stable across retry/restart.
- Outbox claims use leases; acknowledgements and reschedules require the current unexpired lease.
- Retries are bounded with capped backoff; permanent token errors revoke only the matching owner+installation.
- A provider success followed by a process crash can cause a duplicate. Android must durably deduplicate event IDs before presenting/acting on an alert.
- A worker must be bounded, single-instance per process, started only by explicit opt-in, and stopped cleanly with application lifespan.
- No token, credential, provider response body, or raw exception is written to logs or outbox metadata.
- Multi-process deployments need a shared durable lease store and must not rely on in-process task uniqueness alone.

## 6. Security and key lifecycle

- No secrets in source control, APK, progress documents, logs, or chat.
- Device tokens are encrypted at rest with AES-256-GCM and owner+installation associated data.
- Runtime encryption keys are injected by the owner-controlled host secret mechanism; no generated fallback key.
- Key rotation requires versioned key identifiers, a dual-read/re-encrypt migration, backup of old ciphertext/key under owner custody, and a tested rollback/recovery plan. The current device-token format does not yet implement key-versioned ciphertext rotation; that remains open.
- Firebase Admin uses runtime ADC/workload identity. No long-lived service-account JSON is bundled.
- Production TLS, Redis ACL, monitoring, independent backup, and incident recovery require live host evidence, not mocked tests.

## 7. Long-horizon compatibility and portability

- Keep canonical application records exportable without requiring a live market-data provider.
- Version external API and event payload schemas; clients must ignore unknown optional fields and reject unsupported required versions safely.
- Keep vendor-specific ingestion behind adapters and preserve source provenance.
- Maintain deterministic replay and migration fixtures for representative old datasets.
- Test fresh install, upgrade, backup, restore, process restart, disk-full behavior, clock jumps, provider outage, key loss simulation, and partial delivery.
- Keep documentation of units, precision, nullability, identity, retention, and ownership next to each durable schema.
- Review supported Android OS/filesystem and backend runtime versions on a published compatibility schedule.

## 8. Current evidence and open work

### Implemented in repository

- Shared configured SQLite path across durable adapters, with regression coverage.
- Canonical instrument registry and provider mapping separation.
- Decimal-text financial values and explicit timestamp bounds in alert/OHLCV paths.
- Durable OHLCV and alert outboxes with stable IDs/cursors.
- Alert outbox lease, capped retry, terminal failure, and stale-lease rejection.
- Encrypted device-token storage, owner scoping, quota, and revocation.
- Consistent SQLite backup/restore helpers and a redacted restore drill with schema/row digests and domain readback.
- FCM sender adapter and opt-in FastAPI lifespan worker integration are implemented in source; CI and live ADC/Android acceptance must be checked against the exact final commit.

### Still open; do not mark as accepted

- Unified schema migration ledger and explicit versioned migrations across all durable stores.
- Versioned device-token ciphertext/key rotation.
- Actual Android filesystem/WAL/backup/restore compatibility and a full owner-device restore drill.
- Owner-controlled independent backup destination, key custody, retention and recovery exercise.
- Real Firebase ADC host initialization, real Android token registration/refresh/revocation, background/closed-app delivery and durable event-ID deduplication.
- Production monitoring, disk-pressure and recovery drills, TLS/WSS deployment evidence.
- Long-term export/import and cross-runtime compatibility tests.

## 9. Acceptance policy

A foundation item is accepted only when all of these exist:
1. Source implementation reviewed.
2. Regression tests executed and passing on the exact commit.
3. Upgrade/restore compatibility evidence where persistent data is affected.
4. Security review for identity, secrets, encryption, and ownership boundaries.
5. Owner-host/device acceptance evidence where platform behavior is involved.
6. Progress criterion explicitly mapped to its evidence.

A code commit, test file, green CI, or updated dashboard alone does not close a Stage 1 criterion or award progress ticks.


## 10. Automatic evolution: what updates, and what does not

"Auto-evolution" means the application can recognize and apply a reviewed, versioned database migration when a compatible application release starts. It does **not** mean that a remote server silently rewrites the database, that arbitrary SQL is downloaded and executed, or that a mobile app can update its own binary without the platform's update mechanism.

- A released backend carries its ordered migration definitions and immutable SHA-256 checksums.
- At startup, the migration runner compares each component's recorded schema head with the release's supported migration sequence.
- It applies only the exact next migration, in a transaction with its ledger entry, and refuses skipped versions, checksum drift, and schema downgrades.
- Existing legacy stores must first be adopted with a verified baseline. The baseline records the schema fingerprint observed at adoption; it does not invent historical migration records.
- A verified backup and restore rehearsal are required before any migration that could affect user data. Destructive changes require a separate reviewed plan and must not run as silent startup work.
- New app features and provider data releases are separate from schema migrations. Provider data refreshes update versioned records through ingestion rules; they do not rewrite canonical identities.
- Android APK updates remain governed by Android installation/update rules. Database evolution does not automatically update the APK binary.

The initial append-only ledger and migration runner now exist in `backend/app/schema_migrations.py`, with tests in `backend/tests/test_schema_migrations.py`. They are **not yet wired into every existing persistence adapter**. Current adapters still have their own schema-version mechanisms or additive initialization paths. Adapter adoption, baseline fingerprints, backup gates, and live upgrade rehearsals remain open before automatic migrations can be called production-ready.
