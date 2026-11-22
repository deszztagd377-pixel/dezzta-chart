# DEZZTA CHART — Zero-Cost Backend Longevity Blueprint

Date: 2026-11-22
Working branch: `phase-2/market-data-foundation`
Baseline HEAD: `1eff552c68487e7411ac423f289c07a4856d2074`
Status: **ARCHITECTURE PROPOSAL — OWNER REVIEW REQUIRED; NO DEPLOYMENT OR RUNTIME CHANGE**

## 1. Mission and non-negotiable constraints

Design a backend that can evolve for decades without rebuilding its foundations, while the current owner budget remains exactly zero.

"Decades" is a software-longevity target, not a guarantee that any cloud vendor, free tier, domain, network, or hardware will remain available for decades. No external free tier can provide that guarantee. The architecture must therefore make replacement and recovery routine rather than depend on a promise from one provider.

Hard constraints:

- No paid hosting, managed database, managed Redis, domain, market-data feed, monitoring, runner, trial, card-backed usage, or new hardware.
- No deployment, account provisioning, billing activation, or service connection is authorized by this document.
- Do not use Vercel or Cloudflare as the proposed backend host for this plan.
- Never weaken Firebase identity/entitlement checks, HTTPS/WSS validation, Redis TLS/ACL, one-time ticket semantics, fail-closed guards, backup encryption, or secret handling to fit a free tier.
- Never put server secrets in the APK, Vite variables, Git history, logs, screenshots, or chat.
- Never present sample OHLC, delayed placeholders, or synthetic events as live exchange data.
- Keep the existing branch `phase-2/market-data-foundation`; never touch `main`.
- Inspect before editing. Every later implementation slice requires an approved scope, focused tests, full relevant CI, exact changed-file list, and commit SHA.

## 2. Reality check: zero cost versus long-term availability

There is no verified way to promise all three simultaneously:
1. a public, always-on FastAPI + WebSocket server;
2. durable database, Redis-compatible TLS/ACL coordination, backups, and monitoring;
3. guaranteed zero cost for decades.

Free plans are useful for prototypes, but their limits are material:

| Candidate | Verified free-plan facts | Architectural decision |
|---|---|---|
| Render Free Web Service | Supports Python/FastAPI and WebSockets; sleeps after 15 minutes without inbound HTTP/WebSocket messages; about one minute to wake; filesystem is ephemeral; free services can restart at any time; no persistent disks; free Postgres expires after 30 days; free Key Value is in-memory and loses state on restart. Outbound bandwidth is quota-limited and excess usage can be billed. | **Not selected for use yet.** It may be considered for synthetic-data POC only after the account's billing/overage controls are verified to make accidental charges impossible. Never use it as production compute, durable storage, or the Redis shared-guard. |
| Supabase Free | Postgres database; 500 MB database; 5 GB egress; free projects can pause after about seven days of low activity; no automatic backups on Free; manual export is required; Realtime Free limits include 200 concurrent connections and 100 messages/second. | **Candidate for a disposable integration/portability POC only.** Do not make it the only backup or assume continuous availability. Revalidate quotas before use. |
| Neon Free | Serverless Postgres with scale-to-zero and a published free allowance; exact quotas and plan rules can change. | **Secondary database candidate for a controlled comparison**, not a production decision until current official quotas, inactivity behavior, export/restore, and billing safeguards are rechecked. |
| Koyeb, Railway, Fly.io, cloud free credits, and similar offers | Some offers sleep, require a card, are time-limited credits, or have no standing always-free compute. | **Not selected.** A trial or credit is not a permanent zero-cost plan. |
| Existing Android phone / Termux | Owner-controlled but Android can suspend/kill processes; current Termux package-signature/keyring trust and Android/Bionic dependency issues remain unresolved. | **Local development experiment only**, not public always-on production. No package changes until repository-signature trust is resolved. |

Official plan references checked on 2026-11-22:
- Render free service limitations: https://render.com/docs/free
- Render WebSocket behavior: https://render.com/docs/websocket
- Supabase pricing and quotas: https://supabase.com/pricing
- Supabase Free project pausing: https://supabase.com/docs/guides/platform/free-project-pausing
- Supabase Free backup policy: https://supabase.com/docs/guides/platform/backups
- Supabase Realtime limits: https://supabase.com/docs/guides/realtime/limits
- Neon plans: https://neon.com/pricing

Plan pages are mutable. Recheck them before creating an account or relying on a quota. Do not infer "always free" from a marketing headline.

## 3. Long-lived architecture: separate responsibilities

The application must not depend on a single provider-specific product. Keep the following boundaries explicit:

### 3.1 Client

- Android Capacitor/WebView and browser clients use a versioned HTTPS API and WSS endpoint.
- The frontend receives only public configuration. No database, Redis, Firebase Admin, encryption, or market-data provider secret is shipped to the client.
- The client must expose explicit disconnected, stale, delayed, unavailable, and live states. "Connected" is not the same as "live market data."
- Client reconnect always reauthenticates, obtains a new short-lived ticket, validates snapshot generation/cursor, and resumes only from a verified state.

### 3.2 API and WebSocket compute

- Keep FastAPI as the current application framework. Package it as a portable OCI container; do not couple application logic to Render-specific APIs or filesystem paths.
- Compute instances must be replaceable and treated as stateless. Local filesystem writes are scratch only.
- Health/readiness endpoints must distinguish process liveness from database, Redis, Firebase, snapshot, and provider readiness.
- WebSocket connections are disposable. Heartbeat, ticket renewal, reconnect, snapshot, and replay are mandatory protocol behavior, not host-specific workarounds.
- A free compute host may be used only for an isolated POC if its limitations are visible in the app and acceptance record.

### 3.3 Durable system of record

- Long-lived user, entitlement, instrument, OHLCV, alert, incident, audit, snapshot-manifest, and replay-cursor records require a durable database.
- PostgreSQL is the preferred portable target for future shared/cloud persistence because it can be exported and self-hosted. SQLite remains useful for local development and the existing single-process/device tests.
- Do not switch the current SQLite-backed stores to Postgres in one large rewrite. First define repository interfaces, schema ownership, migration ordering, compatibility tests, and a measured import/export path.
- All schema changes use versioned, repeatable migrations. Use expand/contract migrations: add compatible schema, deploy compatible code, backfill/verify, then remove obsolete schema only in a later approved release.
- Use UTC timestamps, stable IDs, explicit source/provider IDs, decimal-safe price representation, unique constraints, and idempotency keys. Do not use vendor-generated row IDs as public identities.
- Database export must be a documented, tested, provider-independent artifact. Restore must be tested into a clean database and compare row counts, checksums, critical invariants, and sequence high-water marks.

### 3.4 Redis and realtime coordination

- Preserve the existing separation between shared security guards and the OHLCV relay. They have different trust boundaries and ACL identities.
- Redis remains a coordination/transport component, not the only canonical copy of important user or market records.
- Production Redis must use TLS with certificate and hostname validation, separate least-privilege ACL users, restricted network access, persistence/restart tests, and fail-closed behavior.
- A free in-memory key-value product is not a Redis replacement for single-use WebSocket tickets, shared rate/lease guards, or durable replay.
- Do not migrate Redis guards to Postgres, Supabase Realtime, or another product merely because the free plan is available. Any replacement needs a separate threat model, atomicity/concurrency proof, replay semantics, and security review.
- Durable event delivery needs a recoverable source of truth. Before any transport redesign, specify a transactional outbox or equivalent durable event journal, monotonic cursor, idempotent consumer, snapshot generation, replay window, and gap recovery. Redis streams/pub-sub may accelerate delivery but must not silently become the only record of committed business events.

### 3.5 Market-data source boundary

- Keep provider adapters isolated from API, persistence, chart calculations, and WebSocket protocol.
- Provider activation is a separate decision requiring lawful data entitlement, a genuinely free source if zero cost remains mandatory, symbol/contract definitions, rate limits, retention rights, and quality validation.
- No free hosting provider supplies exchange market data merely by hosting the backend.
- Until a source passes review, provider flags remain disabled and the API returns explicit unavailable/empty state. Never synthesize bid/ask, footprint, heatmap, or liquidation data and label it as exchange truth.

### 3.6 Backups, keys, and disaster recovery

- A database is not considered durable until backup and restore have been exercised on the actual target.
- Keep encrypted backups in a physically/logically separate location from the primary database. A second folder on the same host is not off-host backup.
- Keep encryption keys separate from backup artifacts and source databases. Define key rotation, recovery custody, and a lost-key no-go procedure.
- Use open export formats and documented restore tools. Verify SHA-256 checksums and application-level invariants after restore.
- Define recovery point objective (RPO) and recovery time objective (RTO) only after measurement. Do not claim zero data loss or a recovery time without a drill.
- Under the current one-phone/no-new-hardware/no-money constraint, a verified off-host backup destination has not been established. Gate 31 must remain open.

### 3.7 Observability and operations

- Emit structured, redacted logs with bounded retention and rotation. Never log tokens, passwords, private keys, or full authorization headers.
- Track API latency/error rate, WebSocket connect/reconnect/renewal failures, stream lag, cursor gaps, database capacity, Redis health, snapshot age, provider freshness, and backup/restore outcomes.
- Health endpoints are not alert delivery. Gate 39 requires a real operator-visible notification and acknowledgement/recovery drill.
- Define runbooks for provider outage, database restore, Redis outage, TLS expiry, secret rotation, migration rollback, and vendor exit.
- Every operational control must have an owner, trigger, action, verification, and recovery path.

## 4. Provider portability contract

No provider-specific SDK or proprietary feature may leak into core business logic. Implement only after review:

- `ComputeAdapter`: deployment and health contract; core code remains OCI/FastAPI.
- `DatabaseAdapter`: transaction, migration, query, export, and restore contract; PostgreSQL implementation first, SQLite implementation retained for local tests.
- `CoordinationAdapter`: Redis TLS/ACL implementation with explicit capabilities; do not silently fall back to memory.
- `ObjectBackupAdapter`: encrypted export/import interface; target must be independent of primary host.
- `IdentityAdapter`: Firebase Admin verification remains server-side and replaceable only through an approved identity migration.
- `MarketDataAdapter`: source identity, licensing/entitlement, timestamps, sequence, quality, and provenance are mandatory.

Adapters must expose capability checks. Startup must fail closed if the selected deployment lacks a required capability. Never "best effort" downgrade TLS, persistence, ACL, backup, or identity guarantees.

## 5. Migration strategy: strengthen without demolishing

No major migration should happen until its predecessor is accepted.

| Phase | Work | Exit evidence | Must not happen |
|---|---|---|---|
| A — Baseline inventory | Map each current SQLite file/store, Redis role, data owner, schema, retention, and process lifecycle. Capture current tests and exact branch HEAD. | Complete data-flow and dependency map; no unknown production-critical store. | No provider account, deployment, schema rewrite, or security downgrade. |
| B — Contract freeze | Define API/WS protocol versions, durable entities, IDs, sequence/cursor rules, event envelopes, schema ownership, and failure semantics. | Versioned contracts and compatibility tests. | No visual/UI expansion or unrelated refactor. |
| C — Portability seam | Introduce narrow repository interfaces around existing stores without changing behavior. | Existing tests unchanged/pass; contract tests run against current SQLite adapter. | No simultaneous SQLite-to-Postgres rewrite. |
| D — Database migration POC | Add a separate Postgres adapter and repeatable migrations in an isolated test environment. Compare round-trip exports and application invariants. | Import/export parity, migration rollback plan, concurrency tests, restore drill. | No production cutover and no free-tier data as the only copy. |
| E — Durable event/replay proof | Validate durable event journal/outbox, monotonic cursor, snapshot manifests, SHA-256, replica installation receipts, duplicate handling, replay and gap recovery. | Multi-process failure/restart tests and exact snapshot-to-cursor consistency. | No Redis-only assumption for irreplaceable data. |
| F — Provider capability POC | Compare only genuinely zero-cost options against WebSocket, TLS, persistence, backup, quota, and no-card/no-trial constraints. | Dated provider matrix, proof of no billing path, measured limits, exit plan. | No deployment just because a signup page says "Free." |
| G — Isolated hosted POC | Only after explicit approval, deploy synthetic/non-sensitive data to one selected free candidate. | Public HTTPS/WSS tests, cold-start behavior, quotas, reconnect, restart, export and restore. | No production secrets, real user data, live market data, or production claim. |
| H — Production cutover review | Reassess all ten Gate 10 criteria and owner constraints. | Every applicable acceptance gate has evidence and owner approval. | No cutover if any security, persistence, backup, or data-source gate is open. |

## 6. Vendor exit and decades-long maintainability

- Keep source code, container build, database migrations, API schemas, test fixtures, and runbooks in the repository.
- Pin supported runtime/dependency ranges and update through reviewed, tested batches; do not pin an obsolete dependency forever.
- Maintain a software bill of materials and license inventory when the build pipeline can generate them without introducing paid tooling.
- Keep database dumps and event exports in documented open formats; test restoration without the original vendor.
- Maintain a provider-neutral environment-variable contract and deployment manifest. Provider configuration belongs outside business logic.
- Keep old API protocol versions only for a documented compatibility window; publish deprecation policy before removal.
- Run periodic dependency/security review and restore drills. A decades-long target requires maintenance; it cannot be achieved by freezing today's versions.
- Preserve a "last known good" source commit and migration path. Never rely on a provider's dashboard as the only record of configuration.

## 7. Current repository facts that constrain this design

- Current branch baseline: `1eff552c68487e7411ac423f289c07a4856d2074`.
- Current backend is FastAPI/Python and has SQLite-backed stores for OHLCV, instruments, coverage, alerts, incidents, and observability.
- Existing production configuration requires Firebase project identity and TLS Redis with ACL username/password; shared guards intentionally fail closed.
- Existing WebSocket flow obtains a purpose-bound, single-use ticket over HTTPS and sends the ticket in the first WSS auth frame. Do not regress to raw Firebase ID tokens in WSS frames.
- Existing Redis publisher/gateway runtime factories are owner-injected and fail closed until trusted production snapshot source/installer details are supplied.
- SQLite persistence depends on a real persistent writable volume; container-local defaults are ephemeral.
- Existing SQLite stores do not by themselves establish a durable WebSocket event outbox/replay cursor across backend restart.
- Existing Android APK is frontend-only; it does not bundle or supervise FastAPI or Redis.
- Android/Termux package-signature trust and Python/Bionic compatibility remain unresolved. Do not run package changes as part of this architecture proposal.
- No public production hostname, Redis endpoint, backup destination, production secrets, or real market-data provider is available in this checkpoint.

## 8. Explicit no-go conditions

Stop the affected phase and keep its gate open if:
- the provider requires a card, trial, billing upgrade, or a possible charge;
- the free plan lacks durable storage, required WebSocket behavior, TLS, or required atomic coordination;
- a host can discard irreplaceable data on restart/redeploy;
- the only way to keep the service awake is synthetic traffic that violates provider rules;
- backups are not independent from the primary failure domain or cannot be restored;
- a migration cannot prove row, checksum, entitlement, and cursor parity;
- Firebase, Redis, TLS, or authorization must be weakened;
- no lawful, verified, zero-cost market-data source exists;
- Android lifecycle or device thermal/storage constraints make local hosting unreliable.

## 9. Owner review required

This document is a foundation proposal, not an implementation authorization. Review these decisions before code changes:

1. Accept the vendor-neutral architecture and the rule that no free provider is considered permanent.
2. Do not use Render until billing/overage controls are verified to prevent accidental charges. If that cannot be proven, exclude it entirely; even if later approved for a synthetic-data POC, never use its filesystem, free Postgres, or free Key Value as production durability.
3. Keep Supabase/Neon as isolated Postgres portability candidates only; do not select one as the canonical production store until export/restore, pause behavior, quotas, and billing constraints are proven.
4. Preserve the existing Firebase + Redis TLS/ACL security contract until an explicitly reviewed replacement passes equivalent tests.
5. Keep Gate 31 (off-host backup), Gate 35 (public HTTPS/TLS), Gate 36 (public WSS/Android), and all other Gate 10 criteria open until actual evidence exists.
6. Authorize Phase A inventory and Phase B contract design as the next scoped work. No provider account creation, deployment, credential entry, Termux package change, or production data migration is included.

## 10. Decision

**Recommended direction:** build the portable foundation first; use free hosting only as disposable test infrastructure; keep the canonical data and security model independent of the provider; and require tested export/restore plus vendor-exit evidence before any production cutover.

This is the only honest approach that preserves the zero-cost constraint without pretending that a vendor's current free tier can guarantee service for decades.
