# Fly.io backend deployment plan and validation

## Decision and current disposition

- Target hosting platform: **Fly.io** (selected by project owner on 2026-11-08).
- Application: FastAPI backend, built from `backend/Dockerfile` with `backend/` as the Docker build context.
- Status: **deployment design and repository audit only; no Fly app, Machine, volume, Redis service, DNS, or paid resource has been provisioned.**
- Active branch: `phase-2/market-data-foundation`.
- Audited source HEAD: `bf019975f464b62a50f1f1283e4419a516fa063f`.
- The `main` branch was not changed.

This document separates verified repository behavior from platform-specific work that still requires an actual Fly environment. Do not mark the backend deployed or production-ready based on CI-only evidence.

## Package 1 — Container and Fly service contract

### Verified in the repository

- Dockerfile: `backend/Dockerfile`.
- Python runtime: `python:3.12-alpine3.24`.
- The container runs as UID/GID `10001:10001`, not root.
- Uvicorn binds to `0.0.0.0` and reads the port from `PORT`, defaulting to `8000`.
- The image exposes port `8000` and its Docker health check calls `/health`.
- The API health endpoint returns the service liveness response; it does not prove that market data is connected or current.

### Fly configuration contract

- Build from the `backend/` directory so the Dockerfile's relative `COPY` instructions and requirements file resolve correctly.
- Fly service `internal_port` must be `8000`.
- Force HTTPS at the Fly service edge.
- Configure an HTTP health check for `GET /health`, with a startup grace period compatible with the image's existing 20-second Docker health-check start period.
- Keep the provider flags disabled for the first deployment. Do not add a Databento credential as part of hosting setup.

### Verification evidence

- Automated Tests run [#42432567375](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42432567375) completed successfully on source HEAD `bf019975f464b62a50f1f1283e4419a516fa063f`.
- CodeQL run [#42432567551](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42432567551) completed successfully on the same HEAD.
- Earlier exact-container CI run [#42432195466](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42432195466) built and started the image, observed `/health`, and verified Redis-backed HTTP status requests returned 200 then 429 under the test limit.
- These are CI checks, not Fly deployment checks.

## Package 2 — Redis shared protection

### Verified application contract

- `APP_ENV=production` requires `REDIS_URL`.
- Production Redis URLs must use `rediss://`; plain `redis://` is rejected by settings validation.
- The shared guard is started during application lifespan and checks Redis availability before serving.
- Redis unavailability fails closed: startup fails, and request-time guard failures return 503 rather than silently falling back to per-process memory.
- HTTP rate limits and WebSocket connection leases are shared across backend instances through Redis.
- The current CI smoke test uses an isolated loopback Redis service; it does not validate a managed production endpoint.

### Fly release requirements

- Select a managed Redis service only after reviewing its pricing, TLS, authentication, region/network reachability, persistence, and failover behavior.
- Store the full Redis connection URL as a Fly application secret, never in `fly.toml`, Git, frontend variables, build arguments, logs, or chat.
- Verify TLS certificate validation and a real connection from the selected Fly region.
- Test loss of Redis connectivity and confirm that the API refuses to operate without shared protection.
- Do not assume that a Redis integration or a successful local CI Redis test proves production Redis readiness.

## Package 3 — SQLite persistence and volume topology

### Verified application contract

- `INSTRUMENT_REGISTRY_DB_PATH` defaults to `./data/instrument_registry.sqlite3`.
- The instrument registry, OHLCV store, coverage tracker, price-alert store, and entitlement store use the configured SQLite database path.
- The container runs as UID/GID `10001:10001`; a mounted database directory must be writable by that identity.
- The repository documentation already states that the container filesystem is ephemeral unless the database path is mounted on persistent storage.

### Fly-specific risk

Fly Volumes are local persistent storage attached to individual Machines; they do not automatically replicate their contents between Machines. A second Machine with a separate volume would not share the first Machine's SQLite database.

Until SQLite is replaced by a shared database or a deliberately engineered replication layer is validated:

- Do not horizontally scale this SQLite-backed service across multiple Machines.
- Do not deploy multiple regions expecting a shared SQLite state.
- Treat a single-Machine volume deployment as a constrained initial topology with a single point of failure and possible deployment downtime.
- Confirm mount ownership/permissions for UID/GID `10001:10001` before starting the application.
- Test backup and restore from the actual volume before storing important production data.
- Do not assume Fly volume snapshots are a substitute for a tested application-consistent backup and restore procedure.

A production availability target requiring redundant Machines should trigger a database architecture decision before deployment. The safe options are to keep the initial service explicitly single-Machine with accepted downtime/risk, or complete a separately scoped migration to a shared managed database first. Do not silently create one independent SQLite volume per Machine.

## Package 4 — Firebase identity validation

### Verified application contract

- `FirebaseIdentityVerifier` uses the Firebase Admin SDK.
- It checks token revocation and validates the verified principal's subject, issuer, audience, and authentication time.
- The verifier initializes Firebase Admin with the configured project ID and relies on the Admin SDK's default application credential discovery; it does not currently accept a credential object through application settings.
- The production identity path has not been end-to-end validated against a real Firebase project and real signed ID token.
- `FIREBASE_PROJECT_ID` is parsed by backend settings, but the example environment file does not currently document a complete production credential arrangement.

### Fly release requirements

- Confirm the exact Firebase project ID and the Admin SDK credential mechanism available to the Fly Machine.
- Do not assume that setting only `FIREBASE_PROJECT_ID` is sufficient; the Admin SDK must also obtain valid server credentials.
- Never commit a service-account key or expose it to the Vite frontend. Any credential mechanism must be stored server-side and reviewed before enabling protected production routes.
- Test valid, expired, revoked, wrong-project, malformed, and unavailable-provider cases without placing real tokens or credentials in CI logs.
- Keep account-owned write routes disabled until identity verification and entitlement checks are proven end to end.

## Package 5 — Fly ingress and security smoke tests

### Verified application contract

- Production CORS parsing rejects wildcards and requires HTTPS origins.
- The current intended frontend origin is `https://dezzta-chart.vercel.app`.
- CORS is read-only (`GET`), does not allow credentials, and accepts only explicitly configured origins.
- HTTP rate limiting currently derives the client identity from `request.client.host`.
- The application does not currently establish a Fly-specific trusted-client-IP policy. Do not trust arbitrary `X-Forwarded-For` values.
- The WebSocket guard is configured, but the current frontend chart path uses read-only HTTP snapshots and does not require the WebSocket token.

### Fly ingress requirements

- Fly Proxy documents a `Fly-Client-IP` request header for the original client IP. Before using it for rate limiting, verify the exact ingress path and whether any additional proxy/CDN sits in front of Fly.
- Add a narrowly scoped Fly ingress identity policy and tests before public exposure; do not accept client-supplied forwarding headers as authoritative.
- Keep the application bound to the intended service interface and verify that the backend cannot be reached through an unintended bypass path.
- Confirm CORS preflight behavior from the production Vercel origin and rejection of unapproved origins.

### Required deployed smoke-test matrix

1. `GET /health` returns 200 through the Fly HTTPS hostname.
2. `GET /v1/market-data/status` succeeds with Redis available and retains honest disconnected/unavailable market-data semantics.
3. Rate-limit exhaustion returns 429; Redis outage fails closed.
4. Requests from the configured Vercel origin pass CORS; unapproved origins do not receive permissive CORS headers.
5. The Fly client-IP value used for limiting is correct and cannot be replaced by a caller-supplied spoofed header.
6. Firebase valid/invalid/revoked-token cases match the intended response behavior.
7. A backend restart preserves SQLite data from the mounted volume; a restore drill recovers a known test database.
8. WebSocket capacity/lease behavior is tested only if that endpoint is enabled for the deployment.
9. Databento remains disabled; no fabricated bars appear when the provider is disconnected.

## Deployment gate — decisions still required

Do not create a `fly.toml` or provision resources until these environment-specific decisions are confirmed:

- Fly app identifier and deployment region.
- Whether the initial Fly service is explicitly allowed to run as one Machine with a local SQLite volume, accepting the availability and backup constraints, or whether shared-database migration is required first.
- Managed Redis service and endpoint, after pricing and network review.
- Firebase Admin SDK credential strategy supported by the selected runtime.
- Whether Fly is reached directly or through another proxy/CDN, so the client-IP trust boundary can be implemented correctly.

No production secrets, credentials, provider entitlements, or account tokens should be pasted into chat or committed to the repository.

## Progress accounting

This is an architecture/deployment-readiness audit and runbook. It does not itself prove a Fly deployment, managed Redis connectivity, persistent-volume durability, Firebase production authentication, or public ingress security. It therefore does not increase the project's overall progress or Stage 1 completion percentage.


## Single-Machine SQLite decision — approved initial topology

The project owner selected **one Fly Machine with one attached Fly Volume** for the initial deployment. This is a deliberate constrained topology, not an HA configuration.

### Database path and shared-file audit

The backend creates all of the following stores with the same `Settings.instrument_registry_db_path`:

- `SQLiteInstrumentRegistry`
- `SQLitePriceAlertStore`
- `SQLiteInstrumentEntitlementStore`
- `SQLiteOhlcvStore`
- `SQLiteCoverageTracker`
- Databento definition journal/synchronizer

The configured default is `./data/instrument_registry.sqlite3`. For Fly, mount the volume at `/data` and set:

```text
INSTRUMENT_REGISTRY_DB_PATH=/data/dezzta-chart.sqlite3
```

This keeps the single shared SQLite database file on the persistent volume. Do not configure separate paths for individual stores.

The OHLCV store enables SQLite WAL mode during initialization. The other stores share that same database file. Backup operations must therefore account for SQLite's WAL sidecar and must not copy only the main `.sqlite3` file while the application is writing.

### UID/GID and mount permission audit

Verified container facts:

- `backend/Dockerfile` creates `appuser` with UID/GID `10001:10001`.
- The final image runs as `USER 10001:10001`; the application is not intended to run as root.
- Store constructors create the database parent directory, but they cannot override a mounted filesystem that is not writable by the runtime UID/GID.

Fly's volume documentation describes the mount point and local volume behavior. Fly community guidance indicates that mount ownership is normally initialized from the Docker image user, but permission behavior must be checked on the actual Machine rather than assumed. See the official [volume management documentation](https://fly.io/docs/volumes/volume-manage/) and the [Fly discussion of mount ownership](https://community.fly.io/t/fly-volumes-getting-permission-denied/1773).

Preflight acceptance checks, after a volume exists and before exposing the API:

1. Confirm the process identity is UID/GID `10001:10001`.
2. Inspect the mounted `/data` owner, group, and mode.
3. As the actual application user, create and remove a harmless test file in `/data`.
4. Start the backend and confirm it creates/opens `/data/dezzta-chart.sqlite3`.
5. Restart the Machine and confirm the same database file and known test record remain.
6. Confirm no application process has been changed to run as root to work around a permission failure.

If the write test fails, stop before production exposure. Diagnose the mounted directory ownership and correct it with a reviewed, least-privilege setup. Do not blindly run recursive ownership changes or weaken permissions to world-writable.

### Single-Machine Fly configuration template

A reviewable template is provided at `backend/fly.toml.example`. It intentionally contains placeholder app/region values and is not deployable until those values are chosen. It configures:

- Docker build context as `backend/` (the directory containing the Dockerfile and requirements).
- Internal HTTP port `8000`, HTTPS enforcement, and `GET /health` check.
- `APP_ENV=production`, the persistent database path, and the exact Vercel CORS origin.
- Databento live and historical ingestion disabled.
- One mounted volume at `/data`.
- Machine auto-stop disabled for predictable always-on service behavior.

The template does **not** contain `REDIS_URL`, Firebase credentials, Databento credentials, or any other secret. Supply secrets only through Fly's secret mechanism after the managed service and credential choices are reviewed.

The Fly app must be explicitly kept at **one Machine** for this SQLite topology. Do not use multiple regions, create a second Machine, or enable horizontal autoscaling. A Fly Volume is local to its attached Machine and does not replicate writes to another volume. A replacement Machine must be attached to the intended existing volume; a newly created empty volume is not a copy of the old database.

### Backup and restore policy

Fly documents scheduled daily volume snapshots as enabled by default, with a default retention of 5 days and a configurable retention range up to 60 days. Treat these snapshots as a short-window infrastructure recovery aid, not as the only backup or as proof that a SQLite application-consistent restore has been tested. See [Fly volume management and snapshots](https://fly.io/docs/volumes/volume-manage/) and [Fly Volumes overview](https://fly.io/docs/volumes/).

Required independent backup approach:

- Use Python's SQLite online backup API (`sqlite3.Connection.backup`) to create a transactionally consistent backup while the application is live. Do not use a plain file copy of the live main database while WAL writes may be active.
- Transfer the completed backup to a separate, access-controlled backup destination outside the Fly Volume and outside the Machine's ephemeral filesystem.
- Encrypt backups in transit and at rest; keep destination credentials outside Git and outside the application image.
- Retain multiple dated backups according to an agreed retention policy. The exact offsite destination, cost, and retention must be selected before production data is stored.
- Restore a backup into a separate test database, run `PRAGMA integrity_check`, verify expected tables and known records, and exercise representative read paths.
- Record backup completion, size, timestamp, database integrity result, and restore-test result without logging secrets or personal tokens.

Do not delete or replace the live database during a restore test. A production recovery requires a planned maintenance window, a verified backup, a stopped or isolated application, and a controlled replacement procedure.

### Single-Machine release acceptance gate

The initial deployment is not accepted until all of these are evidenced:

- Exactly one Fly Machine is attached to exactly one intended volume in the selected region.
- `INSTRUMENT_REGISTRY_DB_PATH` resolves to `/data/dezzta-chart.sqlite3`.
- UID/GID `10001:10001` can write to the mount without running the application as root.
- Database creation, restart persistence, and a known-record readback pass.
- An independent online backup is created outside the volume.
- A restore drill passes `PRAGMA integrity_check` and application-level readback.
- Automatic snapshot configuration and its retention are confirmed in the actual Fly app.
- A documented rollback path exists before subsequent schema-changing releases.

Until these checks run on an actual Fly Machine and volume, permission, persistence, backup, and restore status remains **unverified**.


Configuration clarification: the `[build]` section does not change Fly's Docker build context. Because this example is stored in `backend/` and its Dockerfile uses relative `COPY` instructions, run Fly commands with `backend/` as the deploy context (for example, work from that directory). The app name and primary region placeholders must be replaced before validation. The TOML does not itself enforce a one-Machine count; the actual Fly app must be kept at one Machine and checked after every deployment. The selected `auto_stop_machines = "off"` / `auto_start_machines = false` pair intentionally avoids proxy-driven stop/start behavior for the single-node SQLite service.
