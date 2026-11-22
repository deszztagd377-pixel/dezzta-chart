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

## Oracle Cloud Always Free candidate — single-instance acceptance profile

The owner has selected Oracle Cloud Infrastructure (OCI) Always Free as the
candidate public host for the first single-instance deployment. This is a
candidate deployment target, not evidence that an OCI tenancy, VM, hostname,
or public endpoint exists.

The initial topology is intentionally single-node:

- One Always Free eligible Ampere A1 VM runs the FastAPI application, reverse
  proxy, and a locally bound Redis instance.
- SQLite remains the authoritative OHLCV store and durable outbox on the VM's
  persistent boot/block volume. The application and database must use the same
  configured persistent path.
- Redis is used for the production shared security guard and single-use
  WebSocket ticket storage. Bind it only to loopback/private interfaces, use a
  dedicated ACL user, and require TLS with certificate and hostname validation.
- The normal source-mode WebSocket hub remains process-local. Do not enable
  publisher/replica mode or add gateway replicas for this first deployment.
- The reverse proxy terminates public HTTPS/WSS and forwards only to the
  loopback FastAPI listener. Do not expose Redis or the application worker port
  directly to the public internet.

OCI currently documents Always Free Ampere A1 allowance as up to 2 OCPUs and
12 GB memory, with 200 GB total boot/block-volume storage in the tenancy's
home region. Capacity is not guaranteed; an out-of-host-capacity response can
prevent provisioning. Always Free resources are free only within their
published limits and eligible labels. Do not create or resize into a paid
shape, paid volume, paid load balancer, or other non-Always-Free resource.

**Availability limitation:** OCI states that Always Free compute instances may
be reclaimed when they remain below its idle thresholds over a seven-day
period (CPU p95 below 20%, network below 20%, and memory below 20% for A1).
The tenancy account can also be suspended or terminated under OCI's account
and inactivity terms. Therefore Always Free is a zero-cost candidate, not a
promise of uninterrupted service or permanent data retention. Keep encrypted
backups outside the VM and prove restore independently.

Before any production deployment, the adult account owner must confirm the
tenancy's current Always Free eligibility, region capacity, resource labels,
account terms, and that no billing upgrade or paid resource is enabled. Never
share identity, card, tenancy, SSH, Firebase, or Redis credentials in chat.
Do not create multiple accounts or bypass identity, payment-method, age, or
account-verification requirements.

**OCI-specific acceptance gates (all remain open until tested):**

1. Confirm the VM shape, boot volume, and every attached resource are marked
   Always Free in the actual tenancy and stay within published limits.
2. Confirm the host survives restart with the SQLite database and Redis data
   intact; measure disk usage, WAL growth, and Redis persistence behavior.
3. Configure the Redis ACL user and TLS trust chain. The backend must reject
   wrong hostname, untrusted certificate, invalid ACL credentials, and
   unreachable Redis during production startup.
4. Establish a stable public HTTPS hostname and publicly trusted TLS chain
   without introducing a paid domain or service. If that cannot be achieved
   at zero cost, public WSS acceptance remains blocked.
5. Validate reverse-proxy WebSocket upgrade, heartbeat, ticket renewal, and
   reconnect using a real browser and Android client.
6. Back up the SQLite database, encrypt the backup, restore it to a clean
   location, and verify the restored outbox cursor and OHLCV snapshot.
7. Record actual host resource use and test recovery after VM restart and
   unexpected termination. Do not claim high availability from a single VM.

Official OCI limits and policies must be rechecked at provisioning time:
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- https://www.oracle.com/cloud/free/

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
- Alert-device storage remains disabled unless explicitly opted in with
  `ALERT_DEVICE_STORE_ENABLED=true` and a protected key file supplied through
  `ALERT_DEVICE_ENCRYPTION_KEY_FILE`. The key file must be readable by the
  unprivileged application identity only and contain canonical base64 for
  exactly 32 random bytes. Do not pass the key as an environment value or
  Docker build argument.

When enabled, the opt-in initializes encrypted token persistence and
conditionally exposes authenticated `POST /v1/alerts/devices` and
`DELETE /v1/alerts/devices/{installation_id}` routes. Ownership is derived
from the verified Firebase principal; clients cannot submit an owner ID and
responses never contain the FCM token.

The routes register/rotate and revoke device tokens only. They do not send
notifications: FCM sender credentials, a delivery worker, and real push
delivery are not enabled. Keep the store disabled in deployment until key
custody/recovery, sender setup, and Android end-to-end acceptance are complete.

Do not use managed Redis, paid hosting, paid domains, a CDN, or any trial that
can convert into a charge. Add preview origins only when needed, as
comma-separated exact origins. Never put backend secrets in Vite variables.

The `/ws/market-data` route uses a short-lived, single-use WebSocket ticket in production. The client first sends the Firebase ID token over HTTPS to `POST /v1/auth/websocket-ticket` using the Bearer Authorization header. The backend verifies the Firebase identity (including revocation checks) and returns a purpose-bound `market-data` ticket with a 90-second lifetime. The client sends that ticket—not the Firebase ID token—in the first WebSocket JSON `auth` message. Production rejects the raw-token WebSocket authentication fallback.

The client requests a fresh ticket over HTTPS every 45 seconds by default, then sends it in an `auth.renew` WebSocket control message. The backend consumes the ticket once, requires the same authenticated subject, rechecks exact-series entitlement and acknowledges renewal. Missing renewal reaches the server's bounded authentication-renewal deadline and closes the connection. The ticket is stored through the shared Redis guard when configured; production configuration requires Redis, while the in-memory ticket store is only the non-production fallback. The Firebase ID token is not placed in a WSS URL or frame. This route does not read `MARKET_DATA_WS_TOKEN`; do not use that setting as evidence that this route is enabled or disabled.

A route present in source is not proof of deployed WSS availability or client
end-to-end compatibility. Before production acceptance, verify the HTTPS/WSS
reverse-proxy configuration, the deployed WebSocket handshake, and the actual
web and Android client flow. The production ticket exchange is implemented in the
repository: the client obtains a purpose-bound, single-use ticket over HTTPS at
`POST /v1/auth/websocket-ticket`, then sends that ticket in the first WSS auth
frame. This source-level implementation is not proof of deployed WSS or live
Firebase acceptance; those remain owner-host integration requirements.

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
- `SQLiteOhlcvStore` commits normalized bar revisions and their durable
  OHLCV outbox events in the same SQLite transaction. The outbox has a
  monotonic global cursor, bounded retention, atomic snapshot/watermark reads,
  global relay paging, and exact-series reconnect replay. A retention gap or
  unavailable replay store must trigger explicit snapshot recovery; clients
  must never silently skip a cursor.
- This local durable outbox is not the same as a production multi-instance
  data plane. The default source-mode WebSocket hub remains process-local, and
  SQLite files must not be shared as a WAL database across arbitrary hosts.
  Cross-instance delivery requires the separate publisher and gateway-replica
  roles, independent Redis consumer groups, durable replica checkpoints, and
  the owner-authenticated snapshot installer/receipt verification described
  in `docs/ADR_WEBSOCKET_CROSS_INSTANCE_OUTBOX_RELAY.md` and the WebSocket
  production-acceptance pack. Those runtime factories are owner-injected and
  fail closed; environment variables alone do not activate them.
- A durable local outbox is not an off-host backup or a guarantee against host
  loss. Persistent-volume configuration, encrypted off-host backup, restore
  drills, and production Redis persistence/failover remain separate gates.
  Sustained write-rate and multi-process contention results must be measured
  on the intended host before production capacity claims.
- A successful container health check proves process liveness only. It does
  not prove provider connectivity, contract-definition availability, OHLCV
  completeness, or market-data freshness.
- Redis must be reachable only over the owner's private network. Validate ACL
  command scope, TLS certificates, persistence, restart and failure behavior
  on the actual host before production acceptance.


## WebSocket durability clarification — 2026-11-22

A source-to-documentation audit corrected an obsolete statement that SQLite
provided no durable WebSocket outbox or replay cursor. The current
`SQLiteOhlcvStore` does persist an OHLCV event outbox and monotonic cursor
atomically with accepted bar revisions, and the WebSocket route supports
bounded exact-series replay from that source store. Snapshot bars and the
source watermark also have an atomic SQLite read primitive.

This correction does **not** mark production WebSocket acceptance complete.
The normal source-mode hub remains process-local. Multi-instance operation
requires the separately implemented source-publisher and gateway-replica
runtime factories, trusted snapshot transfer/install, per-gateway Redis
consumer groups, and matching installation receipts. Those callbacks and
production host resources are not available by default and must remain
owner-injected and fail closed.

The repository/CI tests prove only their documented test topology. Public
HTTPS/WSS, real Firebase token/entitlement E2E, owner-host Redis TLS/ACL and
failover, production snapshot distribution, and real browser/Android WebView
acceptance remain unverified. No host, account, credential, paid service, or
deployment is introduced by this documentation correction.
