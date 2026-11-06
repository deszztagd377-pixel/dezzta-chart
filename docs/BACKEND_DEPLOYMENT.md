# Backend deployment preparation

This guide packages the existing FastAPI service as a portable container. It does
not select a hosting provider, configure a paid plan, or enable a market-data
provider. Choose a hosting provider only after reviewing its current pricing,
region, sleep/availability behavior, and secret-management controls.

## Safe default deployment

The container starts the API with the existing application defaults:

- `DATABENTO_LIVE_ENABLED=false`
- `DATABENTO_HISTORICAL_ENABLED=false`
- no Databento key is required
- no market data is fabricated
- `GET /health` is the liveness endpoint
- `GET /v1/instruments` may return an empty verified-contract catalog
- `GET /v1/ohlcv` may return an explicit unavailable state with zero bars

Do not enable provider flags or add a provider credential as part of this
deployment-preparation step. Provider account entitlement, data licensing,
symbol definitions, cost limits, and operational monitoring require a separate
review before any real provider session is enabled.

## Container build and local smoke test

Run from the repository root:

```sh
docker build -f backend/Dockerfile -t dezzta-chart-backend:local backend
docker run --rm -p 8000:8000 \
  -e APP_ENV=production \
  -e CORS_ALLOWED_ORIGINS=https://dezzta-chart.vercel.app \
  dezzta-chart-backend:local
```

In a second terminal, verify:

```sh
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/v1/market-data/status
curl -fsS http://127.0.0.1:8000/v1/instruments
curl -fsS http://127.0.0.1:8000/v1/ohlcv
```

The health response should be `{"status":"ok","service":"dezzta-chart-backend"}`.
The other endpoints must retain their explicit empty/disconnected/unavailable
semantics until trusted definitions or bars are actually ingested.

## Hosting-provider settings

For a container-based Python web service, use:

- Dockerfile: `backend/Dockerfile`
- Docker build context: `backend/`
- Health-check path: `/health`
- Port: the platform-provided `PORT` environment variable (defaults to 8000)
- `APP_ENV=production`
- `CORS_ALLOWED_ORIGINS=https://dezzta-chart.vercel.app`

Add any Vercel preview origins only when needed, as comma-separated exact
origins. Do not use `*` for production CORS. Set the frontend's
`VITE_MARKET_DATA_API_BASE_URL` to the deployed HTTPS API origin in Vercel,
then redeploy the frontend. Never put backend secrets in Vite variables.

The WebSocket endpoint remains unavailable unless its server-side
`MARKET_DATA_WS_TOKEN` is configured; the current frontend chart integration
uses read-only HTTP snapshots and does not need that token.

## Security and operational notes

- Keep `DATABENTO_API_KEY` absent and both provider feature flags false for
  this deployment-preparation milestone.
- Never place secrets in source files, frontend variables, build arguments,
  Docker image layers, logs, screenshots, or chat messages.
- The active OHLCV pipeline and instrument catalog are in-memory working
  snapshots, but normalized OHLCV bars, the instrument registry, coverage/gap
  intervals, price alerts, and instrument entitlements have SQLite-backed
  persistence. The ingestion service restores retained OHLCV bars and the
  durable local-sequence high-water mark before its consumer starts.
- SQLite durability across container replacement exists only when
  `INSTRUMENT_REGISTRY_DB_PATH` points to a persistent writable volume. The
  default `./data/instrument_registry.sqlite3` is inside the container
  filesystem and must be treated as ephemeral unless the hosting platform
  mounts persistent storage there.
- The container runs as UID/GID `10001:10001`; a mounted database directory
  must be writable by that user. Back up the database and test restore before
  treating it as production-grade storage.
- SQLite persistence does not provide a durable WebSocket event outbox or
  replay cursor. After a disconnect or backend restart, clients still need a
  fresh authenticated snapshot/resubscription. Sustained write-rate and
  multi-process contention benchmarks are still pending.
- A successful container health check proves process liveness only. It does
  not prove provider connectivity, contract-definition availability, OHLCV
  completeness, or market-data freshness.
- Review hosting cost, free-tier sleep limits, region, TLS, access logs,
  retention, and incident controls before creating a public service.
