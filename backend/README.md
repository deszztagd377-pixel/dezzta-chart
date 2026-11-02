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

Copy `.env.example` to `.env` for local configuration. The WebSocket status route
requires a long random `MARKET_DATA_WS_TOKEN`; the current frontend chart uses
read-only HTTP and does not need the WebSocket token. Keep provider switches off
and leave `DATABENTO_API_KEY` empty unless a separate provider-access review has
been completed. Never commit `.env` or share secrets.

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

The WebSocket client must send this first message after connecting:

```json
{"type":"auth","token":"YOUR_LOCAL_MARKET_DATA_WS_TOKEN"}
```

The socket then sends a status message. It does not send market events yet.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Current limitations

- Optional Databento SDK source adapters and a bounded OHLCV ingestion/provider lifecycle are present, but no production provider key or session is configured or verified for this project.
- Provider live and historical features remain disabled by default. Enabling them requires a separate review of account entitlements, exchange licensing, explicit symbols, historical query costs, and operational limits.
- Provider instrument definitions are not automatically refreshed on a schedule. The in-memory catalog is empty until trusted definitions are loaded.
- The WebSocket sends status only; it does not broadcast OHLCV or order-book events.
- Catalog, OHLCV pipeline, and coverage state are in-memory. Persistence, replay, snapshot recovery, and gap recovery across restarts are not implemented.
- With default settings, the status endpoint correctly reports the provider as disconnected; this is not evidence of a working external feed.
- Review CORS, TLS, hosting access controls, and WebSocket authentication before public deployment.

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
