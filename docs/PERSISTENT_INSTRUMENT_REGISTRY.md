# Persistent Instrument Registry

## Scope

The first persistent registry adapter uses Python's built-in SQLite driver. It stores canonical app-level instrument identities separately from provider-scoped instrument mappings. It does not replace the existing ES/NQ/GC futures catalog or change the OHLCV series identity protocol.

## Storage configuration

Set the backend-only environment variable:

\`\`\`text
INSTRUMENT_REGISTRY_DB_PATH=./data/instrument_registry.sqlite3
\`\`\`

The default is \`./data/instrument_registry.sqlite3\`. The backend creates the parent directory and database file. The database is not committed to Git. Use a durable mounted volume at the configured path if the deployment platform supports it. An ephemeral container filesystem is not durable across replacement or rescheduling.

The initial adapter requires a file-backed database and deliberately rejects \`:memory:\`, because an in-memory database would silently violate the persistence requirement.

## Database guards

- SQLite foreign-key enforcement is enabled on every connection.
- Writes use \`BEGIN IMMEDIATE\` and a bounded busy timeout.
- WAL journaling is enabled for local read/write concurrency.
- Canonical IDs are primary keys. Re-registering identical metadata is idempotent; reusing an ID for different metadata is rejected.
- Canonical instrument rows are immutable at the database layer.
- Provider mappings are scoped by provider, dataset, positive publisher ID, and positive provider instrument ID.
- Nanosecond timestamps must fit SQLite signed 64-bit integers; invalid overflow is rejected before database access.
- Mapping validity uses half-open nanosecond windows \`[valid_from_ns, valid_to_ns)\`; adjacent windows are valid.
- Database triggers reject overlapping mapping windows even if a caller bypasses the Python repository.
- Foreign keys prevent mappings from referencing unknown canonical instruments.
- A schema version guard refuses to open a database created by a newer backend.
- Indexes support asset/venue/symbol filtering and provider mapping lookups.

## Internal API boundary

The registry is exposed only as an internal backend service object on application state. No public create/update/delete HTTP route is added in this stage. Public writes must wait for Firebase-backed user identity, explicit per-instrument entitlements, rate limits, audit logging, and authorization tests.

## Operational boundaries

This is a durable single-backend SQLite adapter, not yet a multi-instance production database. Production deployment must provide a persistent volume and backups. SQLite WAL databases should be backed up using a SQLite-aware backup procedure or a consistent snapshot of the database and WAL files; do not copy only the main database file while writes are active.

Before running multiple backend replicas or requiring high write concurrency, migrate the repository adapter to PostgreSQL with versioned migrations, connection pooling, backup/restore drills, and concurrency tests. Keep the registry interface independent from the SQLite implementation.

No provider discovery, exchange licensing, data entitlements, Firebase integration, catalog endpoint, or live multi-asset feed is implied by this storage milestone.
