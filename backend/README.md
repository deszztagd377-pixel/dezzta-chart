# DEZZTA CHART Backend

Python backend foundation for the React/TypeScript application.

## Requirements

- Python 3.10 or newer.
- No Databento account or API key is required to run the health/status/catalog scaffold.

## Local setup

From the repository root:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment, then install dependencies:

```bash
pip install -r requirements-dev.txt
```

Copy `.env.example` to `.env` for local configuration. The authenticated
OHLCV WebSocket and REST snapshot routes require a verified Firebase ID token
and an active per-instrument entitlement. The frontend obtains the ID token from
its authentication provider; do not put a static WebSocket token or provider
secret in the browser bundle. Keep provider switches off and leave
`DATABENTO_API_KEY` empty unless a separate provider-access review has been
completed. Never commit `.env` or share secrets.

Start the service:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## HTTP endpoints

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/v1/market-data/status`
- `GET http://127.0.0.1:8000/v1/instruments`
- `GET http://127.0.0.1:8000/v1/instruments?root=ES` (also NQ and GC)

The instrument endpoint currently returns the supported product roots and an
empty contract list. It will only list expiry-specific outright futures after
validated provider instrument definitions are supplied. It does not invent
contract months, choose a front month, or apply an automatic rollover rule.
Spread instruments and unsupported roots are excluded.

## Definition adapter

`app/databento_definitions.py` converts Databento DBN-like instrument
definition record objects into plain Python mappings. It preserves provider
numeric units and record order, and validates required attributes. It is a
pure adapter: it does not create a Databento client, connect to a feed, read
credentials, or download provider data.

The mappings can be passed to `InstrumentCatalog.replace_definitions()`
after a trusted definition source has been separately configured and reviewed.

## Instrument definition lifecycle

The in-memory catalog supports two distinct update paths:

- `replace_definitions(rows)` replaces a complete authoritative snapshot; contracts omitted from that snapshot are removed.
- `upsert_definition(row)` inserts or updates one contract using the provider event timestamp.
- `delete_definition(publisher_id, instrument_id, event_ts_ns)` applies a timestamped deletion and retains a tombstone.

Incremental events are ordered by `ts_event`: older updates cannot overwrite newer definitions, older deletes cannot remove newer definitions, and delayed updates cannot resurrect a deleted contract. Contract identity is scoped by dataset, publisher ID, and instrument ID. These lifecycle methods are currently in-memory only; no provider event consumer or persistent store is connected.

## WebSocket

WebSocket: `ws://127.0.0.1:8000/ws/market-data`

The current prototype requires the client to send a Firebase Authentication ID token
as the first WebSocket message after connecting. The backend verifies the token
with Firebase Admin, including revocation checks, and derives the account identity
from the verified principal:

```json
{"type":"auth","token":"FIREBASE_ID_TOKEN"}
```

Do not use a static shared WebSocket token or put a signing secret in the browser.
The prototype currently verifies the Firebase ID token directly; the separately
approved short-lived, narrowly scoped WebSocket-ticket exchange is **not yet
implemented**. Do not treat this prototype handshake as the final production
credential design. Production release remains blocked on the ticket lifecycle,
real Firebase signed-token end-to-end tests, and deployment verification.

After authentication, the server sends a status message. The client must then send
one version 1 subscription with the exact verified series identity:

```json
{
  "type": "market_data.subscribe",
  "version": 1,
  "series": {
    "dataset": "GLBX.MDP3",
    "publisherId": 1,
    "instrumentId": 123,
    "rawSymbol": "ESZ6",
    "timeframe": "1s",
    "bucketPolicy": "UTC_LEGACY",
    "calendarId": "",
    "calendarVersion": ""
  }
}
```

The server responds with a `market_data.ohlcv.snapshot` envelope containing
`streamId` and `watermark`, followed by ordered
`market_data.ohlcv.update` events. The outer event sequence is scoped to the
subscription and is distinct from the local bar revision sequence.

Snapshot query and subscription registration occur synchronously on the same
asyncio event loop, with no await between them. This creates an atomic
snapshot/watermark boundary relative to the single-writer ingestion loop.
Accepted base and derived bar revisions are fanned out only to exact matching
series subscriptions. Bucket identity is part of the exact series key: omitted
`bucketPolicy` defaults to `UTC_LEGACY`; `UTC_FIXED_V1` is a separate UTC-aligned
intraday series. Calendar identifiers are currently rejected because no
calendar-based policy is enabled. REST snapshots accept the corresponding
`bucket_policy`, `calendar_id`, and `calendar_version` query parameters.

Each client has a bounded queue. If it fills, the server closes that connection
with code 1013; the client must reconnect and request a new snapshot. Updates
are never silently skipped to keep a slow client connected. This is in-memory
delivery only: server restart, process loss, and reconnect require a fresh
snapshot. No provider connection or live feed is implied by a successful
WebSocket subscription.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Current limitations

- Optional Databento SDK source adapters and a bounded OHLCV ingestion/provider lifecycle are present, but no production provider key or session is configured or verified for this project.
- Provider live and historical features remain disabled by default. Enabling them requires a separate review of account entitlements, exchange licensing, explicit symbols, historical query costs, and operational limits.
- Provider instrument definitions are not automatically refreshed on a schedule. The in-memory catalog is empty until trusted definitions are loaded.
- The authenticated WebSocket supports exact-series OHLCV snapshots and bounded in-memory updates. Subscription identity includes bucket policy and calendar identity; the currently enabled policies are `UTC_LEGACY` and `UTC_FIXED_V1`, while calendar-based CME session aggregation remains disabled. It does not provide order-book/MBO events, durable event replay, or cross-process delivery.
- Normalized OHLCV bars and coverage intervals are persisted in SQLite, and bounded explicit historical gap recovery is implemented. The in-memory pipeline/catalog and WebSocket queues are process-local; the WebSocket event stream has no durable outbox or replay after disconnect/restart. Provider definitions are not automatically refreshed on a schedule.
- With default settings, the status endpoint correctly reports the provider as disconnected; this is not evidence of a working external feed.
- Review CORS, TLS, hosting access controls, and WebSocket authentication before public deployment.

## Consistent SQLite backups

The backend includes `app.sqlite_backup.create_consistent_sqlite_backup()`
for creating a transactionally consistent local snapshot of a file-backed
SQLite database. It uses SQLite's Online Backup API, validates the completed
snapshot with `PRAGMA integrity_check`, writes to a temporary file in the
destination directory, and atomically replaces the destination only after the
backup passes validation. The temporary snapshot is restricted to owner-only
permissions where the filesystem supports POSIX modes.

Example from the `backend/` directory:

```python
from app.sqlite_backup import create_consistent_sqlite_backup

create_consistent_sqlite_backup(
    "/data/dezzta-chart.sqlite3",
    "/data/backups/dezzta-chart-2026-11-08.sqlite3",
)
```

This helper provides a local consistent snapshot only. It does **not** encrypt,
upload, schedule, retain, or restore off-host backups. Production backup
operations still require an independently managed encryption/key process,
off-host storage, retention policy, and a tested restore drill. Do not treat a
copy of a live SQLite database file (or a Fly Volume snapshot alone) as a
substitute for this Online Backup API workflow and a verified recovery plan.

## Container deployment

A portable, non-root backend image is defined in `backend/Dockerfile`. It reads the
platform-provided `PORT`, exposes `/health` for liveness checks, and keeps provider
features off unless explicitly configured. See [`docs/BACKEND_DEPLOYMENT.md`](../docs/BACKEND_DEPLOYMENT.md)
for container build, smoke-test, CORS, and safe deployment guidance.


## Phase 2 — Databento OHLCV ingestion

Everything is **off by default**; without `DATABENTO_API_KEY` the backend starts normally and
`GET /v1/market-data/status` reports `ohlcv.state = "disconnected"`.

Environment variables: `DATABENTO_API_KEY`, `DATABENTO_DATASET`, `DATABENTO_LIVE_ENABLED`,
`DATABENTO_LIVE_SYMBOLS` (explicit contracts), `DATABENTO_HISTORICAL_ENABLED`,
`DATABENTO_DEFINITION_SYMBOLS`, `DATABENTO_HISTORICAL_MAX_SPAN_HOURS`,
`DATABENTO_HISTORICAL_WINDOW_MINUTES`, `INSTRUMENT_ROOTS`, `OHLCV_QUEUE_MAX`, `OHLCV_MAX_RESPONSE_BARS`.

Modules: `symbology.py` (identity/validity), `databento_ohlcv.py` (record -> bar), `aggregation.py`,
`coverage.py`, `ingest.py` (bounded single writer), `provider.py` (lifecycle, backfill),
`databento_sources.py` (SDK wrappers, UNVERIFIED, lazily imported).

Tests need no network and no API key. Async tests use `asyncio.run`, so no extra pytest plugin is needed.
Historical queries can cost money on the provider side: keep spans small.

Live ingestion also requires point-in-time instrument definitions. Set
`DATABENTO_HISTORICAL_ENABLED=true` and explicitly configure
`DATABENTO_DEFINITION_SYMBOLS` (for example `ES.FUT`) so startup can resolve
provider instrument IDs before accepting OHLCV records. This definitions request
is an explicit provider-data operation; keep the configured symbol scope narrow.
Live OHLCV observations do not establish continuous time coverage because
Databento omits intervals without trades. Only successful historical query
windows mark per-instrument coverage as complete.


## Persistent canonical instrument registry

The backend now initializes a file-backed SQLite registry at
\`INSTRUMENT_REGISTRY_DB_PATH\` (default:
\`./data/instrument_registry.sqlite3\`). The internal registry stores immutable
canonical instrument records and provider-scoped, point-in-time mappings.
It is intentionally not exposed through public write endpoints before Firebase
authentication and per-instrument entitlements are implemented.

For deployment, mount a persistent volume at the configured database path.
An ephemeral container filesystem will lose its database when the instance is
replaced. This adapter is intended for a single backend instance; review
\`docs/PERSISTENT_INSTRUMENT_REGISTRY.md\` before production deployment.


## Android / Termux compatibility

Termux is an Android/Bionic environment and is not equivalent to the Linux container used by CI. For native Termux use, install platform-native Python dependencies through the official Termux package repository where available. In particular, the backend requires `cryptography>=50,<51`; the official Termux `python-cryptography` package recipe currently declares version 50.0.2 and includes Android-specific Rust/Python linking configuration.

Prefer the Termux-maintained `python-cryptography` package over attempting a generic PyPI source build on-device. Verify that the installed package version satisfies the backend requirement and that the exact interpreter used to run the project can import `cryptography`. A standard isolated virtual environment does not automatically expose packages installed into Termux's system Python; if using a virtual environment, its system-site-package visibility must be configured intentionally. Do not relax the encryption dependency or replace AES-GCM with a weaker or custom implementation to work around installation issues.

The native SQLite backup helper can be tested independently of encryption, but a successful SQLite snapshot/restore does not certify encrypted backup support. See [Android/Termux readiness](../docs/ANDROID_TERMUX_STATUS.md) for the current device evidence and acceptance gates.
