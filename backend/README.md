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

Copy `.env.example` to `.env` and set a long random `MARKET_DATA_WS_TOKEN`.
Do not commit `.env` or share the token. The Databento key is not used by this scaffold.

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

- No Databento connection or subscription is implemented.
- No provider instrument-definition download or refresh scheduler is implemented.
- The in-memory catalog is not populated by a provider.
- No market-data events are broadcast.
- No persistence, replay, snapshot recovery, or gap recovery is implemented.
- The status endpoint intentionally reports the feed as disconnected.
- Configure a production WebSocket authentication mechanism and TLS termination before any public deployment.
