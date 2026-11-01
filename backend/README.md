# DEZZTA CHART Backend

Python backend foundation for the React/TypeScript application.

## Requirements

- Python 3.10 or newer.
- No Databento account or API key is required to run the health/status scaffold.

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
Do not commit `.env` or share the token. The Databento key is not used yet.

Start the service:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Check:

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/v1/market-data/status`
- WebSocket: `ws://127.0.0.1:8000/ws/market-data`

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
- No market-data events are broadcast.
- No persistence, replay, snapshot recovery, or gap recovery is implemented.
- The status endpoint intentionally reports the feed as disconnected.
- Configure a production WebSocket authentication mechanism and TLS termination before public deployment.
