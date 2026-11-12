# Backend deployment preparation

This guide packages the existing FastAPI service as a portable container. The
mandatory ZERO MONEY policy permits only owner-controlled hardware and
networking that create no new payment obligation. Do not provision paid hosting,
managed Redis, paid identity, market-data, backup, or monitoring services.

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

## Required zero-cost prerequisites

Production mode requires both a Firebase project ID and a TLS Redis endpoint.
This is a configuration requirement, not permission to enable billing or use a
managed service.

Before starting production mode, the owner must independently verify that:

- the Firebase project remains on a no-billing configuration and the selected
  authentication flow does not require a paid add-on;
- Redis runs on existing owner-controlled hardware, uses TLS with certificate
  and hostname validation, has ACLs restricted to the backend, and is not
  exposed to the public network;
- the existing host, network path, and certificate lifecycle introduce no
  incremental charge.

If any prerequisite cannot be verified, keep production deployment deferred.
Do not substitute plaintext Redis, an in-memory limiter, a free trial, or a
paid managed endpoint.

## Container build and local smoke test

Run from the repository root after configuring an owner-controlled self-hosted
Redis TLS endpoint and a no-billing Firebase project. Export values only in the
backend host's protected environment; never echo them or paste them into chat.
The example intentionally uses variable names without embedding credentials.

```sh
: "${REDIS_URL:?Configure the owner-controlled self-hosted Redis TLS URL}"
: "${FIREBASE_PROJECT_ID:?Configure the no-billing Firebase project ID}"
case "$REDIS_URL" in rediss://*) ;; *) echo "REDIS_URL must use rediss:// in production" >&2; exit 1 ;; esac

docker build -f backend/Dockerfile -t dezzta-chart-backend:local backend
docker run --rm -p 8000:8000 \
  -e APP_ENV=production \
  -e REDIS_URL \
  -e FIREBASE_PROJECT_ID \
  -e CORS_ALLOWED_ORIGINS=https://dezzta-chart.vercel.app \
  -v dezzta-chart-data:/data \
  dezzta-chart-backend:local
```

The API intentionally fails startup if the Redis connection cannot be
established. Do not replace this with a local in-memory limiter or use an
unencrypted Redis URL in production. The named Docker volume above is local to
the Docker host; it is not an off-host backup and must be included in the
owner's tested backup/restore procedure.

In a second terminal, verify:

```sh
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/v1/market-data/status
curl -fsS http://127.0.0.1:8000/v1/instruments
curl -fsS http://127.0.0.1:8000/v1/ohlcv
```

The health response should be
`{"status":"ok","service":"dezzta-chart-backend"}`. The other endpoints must
retain their explicit empty/disconnected/unavailable semantics until trusted
definitions or bars are actually ingested.

## Owner-controlled host settings

For a container-based Python service on existing owner hardware, use:

- Dockerfile: `backend/Dockerfile`
- Docker build context: `backend/`
- Health-check path: `/health`
- Port: the host-provided `PORT` environment variable (defaults to 8000)
- `APP_ENV=production`
- `CORS_ALLOWED_ORIGINS`: exact HTTPS browser origins only
- `FIREBASE_PROJECT_ID`: backend-only project identifier for a verified
  no-billing Firebase configuration
- `REDIS_URL`: backend-only secret for the owner-controlled Redis TLS endpoint

Do not use managed Redis, paid hosting, paid domains, a CDN, or any trial that
can convert into a charge. Add preview origins only when needed, as
comma-separated exact origins. Never put backend secrets in Vite variables.

The `/ws/market-data` route currently authenticates with a Firebase ID token
sent in the first JSON `auth` message. The backend verifies the token
(including revocation checks) and periodically re-verifies both identity and
instrument entitlement during the connection. This route does not read
`MARKET_DATA_WS_TOKEN`; do not use that setting as evidence that this route
is enabled or disabled.

A route present in source is not proof of deployed WSS availability or client
end-to-end compatibility. Before production acceptance, verify the HTTPS/WSS
reverse-proxy configuration, the deployed WebSocket handshake, and the actual
web and Android client flow. A separate short-lived scoped WebSocket-ticket
exchange is not implemented in this checkpoint; keep that design decision and
its key lifecycle subject to an approved threat model before adding it.

The `/v1/market-data/status` payload includes provider state, reconnect
attempts, ingestion counters, queue depth, degraded reasons, persistence and
coverage statistics, and bounded-window latency samples. This application
status payload is not a substitute for self-hosted monitoring, durable log
retention, alert routing, or a tested incident/recovery procedure. Configure
those controls on existing hardware or explicitly defer them.

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
  filesystem and must be treated as ephemeral unless the host mounts
  persistent storage there.
- The container runs as UID/GID `10001:10001`; a mounted database directory
  must be writable by that user. Back up the database and test restore before
  treating it as production-grade storage.
- Use `backend/app/backup_encryption.py` to encrypt backup artifacts before
  any off-host transfer. Keep the passphrase separately from both the source
  database and encrypted backup; see [BACKUP_ENCRYPTION.md](BACKUP_ENCRYPTION.md).
- SQLite persistence does not provide a durable WebSocket event outbox or
  replay cursor. After a disconnect or backend restart, clients still need a
  fresh authenticated snapshot/resubscription. Sustained write-rate and
  multi-process contention benchmarks are still pending.
- A successful container health check proves process liveness only. It does
  not prove provider connectivity, contract-definition availability, OHLCV
  completeness, or market-data freshness.
- Redis must be reachable only over the owner's private network. Validate ACL
  command scope, TLS certificates, persistence, restart and failure behavior
  on the actual host before production acceptance.
