# Work Cycle 62J-23 — opt-in FastAPI replica runtime integration

**Date:** 20 November 2026  
**Branch:** phase-2/market-data-foundation  
**Parent code:** ef14752fcf3c6343a7389111c149c390ebed3d6f  
**Scope:** opt-in application lifecycle and WebSocket read-path integration; source mode remains default.

## Implemented

1. Added an explicit replica_runtime_factory injection point to create_app(). It is not activated from environment variables and cannot silently switch a deployment.
2. Lifespan validates the injected replica store, Redis client, consumer, and exact stream identity.
3. Startup hydrates the pipeline from the atomic verified SQLite snapshot before creating the event-loop dispatcher and starting one sequential consumer worker.
4. Replica mode does not start ProviderManager, preventing a gateway from becoming a competing source writer.
5. Shutdown stops the worker with a bounded deadline before closing its dedicated Redis client. If the worker does not stop, the client is deliberately not closed underneath a live thread.
6. /ws/market-data chooses either source SQLite (default) or the injected replica store/Redis replay path. Snapshot cursor and replay watermark stay within the selected domain.
7. Authentication, exact instrument identity checks, entitlements, periodic authorization revalidation, shared connection leases, ping limits, and bounded subscriber queues remain common to both modes.
8. Added tests for replica hydration-before-worker, replica snapshot delivery, provider suppression, Redis client closure, and startup failure without a verified snapshot.

## Explicit boundaries

- Source-backed mode remains the default when no runtime factory is supplied.
- The runtime factory must provision the local verified snapshot and dedicated Redis consumer/client. Production snapshot distribution and TLS/ACL credential rotation are not automated here.
- This does not prove two independently launched ASGI processes or public WSS/Android delivery.
- No Vercel/Cloudflare deploy, paid service, main branch change, or Termux use.
- Gate 10 remains 10/10 🟧 ORANGE / OPEN, 0/10 closed.
- Indicator statuses remain unchanged; see docs/INDICATOR_PROGRESS_LEDGER.md.

CI must pass on the exact resulting commit before this batch is considered verified.
