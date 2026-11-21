# Work Cycle Batch 62J-86 — SQLite schema-bootstrap contention hardening

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `2c584fcef5a20b21ec2850692ab51e28341c4eff`  
**Base:** `c2f9b99fc05dd17050674a39317bd5aa601e6182`  
**CI:** pending exact-head verification.

## Failure evidence

The full-cardinality benchmark attempt at c2f9b99 failed at the SQLite connection bootstrap path. Sixteen simulated workers opened the same database at once; repeated schema DDL/PRAGMA work caused an uncaught `sqlite3.OperationalError: database is locked` during `_connect()`. The failure happened before aggregate transaction processing, so the earlier outer flush retry loop could not reliably contain it.

## Corrective implementation

1. Each `SQLiteMetricsCollector` instance now guards one-time schema initialization with a `threading.Lock`.
2. Schema bootstrap retries only transient `database is locked` errors, with bounded exponential delay across seven attempts. Corruption, invalid schema and non-lock errors still propagate; no blanket exception suppression was added.
3. After schema initialization, normal connections no longer rerun the DDL script. They retain the existing 250 ms busy timeout and per-connection synchronous setting.
4. The benchmark now creates one collector instance per simulated worker, sharing only the same SQLite path. It therefore tests the initialization lifecycle of separate ASGI worker instances more accurately.
5. Added a regression test for four independent collector instances concurrently initializing and writing to one shared SQLite database.

## Acceptance status

- Previous Automated Tests run [44902446746](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902446746) FAILED at the metrics benchmark. The exact error was `database is locked` in `SQLiteMetricsCollector._connect()`. This result is retained and not hidden.
- Previous CodeQL [44902446747](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902446747) SUCCESS; previous Full Git History Secret Audit [44902446769](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902446769) SUCCESS. Those checks were for the prior c2f9 head, not this new source head.
- New exact-head Automated Tests, CodeQL and secret-history audit remain pending for `2c584fcef5a20b21ec2850692ab51e28341c4eff`.
- Full 899-series cardinality and payload-size assertions remain mandatory. The benchmark is synthetic, local, Python-thread based and not a separate-OS-process or owner-host test.
- Gate 38 remains 🟧 OPEN pending exact-head CI, separate-process contention, read-only/disk-full behavior, app-level traffic isolation and owner-host acceptance.
- WebSocket wire protocol/data path unchanged. Production WSS remains host-gated.
- Indicators unchanged; no progress credit. Gate 10 remains 0/10 formally closed; Stage 1 30/40 = 75% provisional; overall project percentage unscored.

ZERO COST. No deployment, Vercel/Cloudflare operation, paid provider, production credentials, Termux/device operation or `main` modification.
