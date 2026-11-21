# Gate 30 — Owner-host SQLite restore drill runbook

**Status:** prepared; owner-host execution not yet performed  
**Branch:** `phase-2/market-data-foundation`  
**Scope:** one real application database, a new local backup path, and a separate new restore path.  
**Cost:** zero incremental service cost. No upload, deployment, paid storage, or external provider is part of this drill.

## 1. Purpose and acceptance boundary

This runbook executes the existing `backend.app.sqlite_restore_drill` workflow against the actual database used by the running backend. It is not a synthetic fixture test and it does not replace the separate Gate 31 off-host encrypted-backup/key-custody exercise.

A successful drill must establish all of the following:

1. The selected source is the database actually used by the target backend process.
2. The source remains read-only and is never overwritten.
3. A consistent SQLite Online Backup API snapshot is published to a new path.
4. The backup and restored copy both pass SQLite integrity and foreign-key checks.
5. Required application tables exist.
6. Every application table has identical row counts and deterministic typed row hashes between backup and restored copy.
7. Schema hashes match.
8. Application-domain stores can read instruments, provider mappings, entitlements, alert zones, coverage, OHLCV bars/series and outbox high-water state.
9. Outbox event IDs and cursors satisfy the uniqueness invariant.
10. A committed probe write is visible through a fresh read-only connection, then cleanup is verified.
11. The emitted report contains aggregate counts and hashes only, with no row values, account identifiers or absolute paths.

No individual check may be waived to produce a PASS result.

## 2. Resolve the real database path before execution

The backend configuration reads `INSTRUMENT_REGISTRY_DB_PATH` from its process environment. If it is absent or empty, the configured fallback is `./data/instrument_registry.sqlite3`, resolved relative to the backend process working directory.

Therefore, do **not** assume that the default path is the live database. Before running the drill, the operator must establish:

- which machine actually runs the backend;
- the backend process working directory;
- the effective `INSTRUMENT_REGISTRY_DB_PATH` value, if set;
- whether the path is relative or absolute;
- the resolved regular-file path and its owning process/account;
- that the selected file is not a stale development/test copy.

Do not print or export the complete process environment: it can contain credentials. Inspect only the one database-path setting using an owner-controlled method. If the backend is hosted remotely, the database is on that host/volume; Termux on the Android client cannot read it merely because the app is installed on the phone.

If the effective database is in-memory, missing, inaccessible, or its actual runtime path cannot be proven, stop. Do not substitute an empty database or a synthetic fixture.

## 3. Capacity and destination planning

Do not estimate capacity from the main database file alone. SQLite may hold committed transactions in a write-ahead log (WAL), so the main file can be smaller than the consistent logical snapshot copied by the Online Backup API.

Define these byte counts on the actual backend host immediately before the drill:

- `S_main`: source database main-file size.
- `S_wal`: current source `-wal` sidecar size, or zero if absent.
- `S_logical`: `PRAGMA page_count * PRAGMA page_size` from a read-only SQLite connection to the same source. The connection must see committed WAL state.
- `S = max(S_main + S_wal, S_logical)`: conservative snapshot-size estimate.

If the source is in rollback-journal mode and a `-journal` sidecar exists, do not guess its meaning or proceed during an unresolved transaction/recovery state. Establish a stable, healthy database state first. Do not delete, checkpoint, truncate, or otherwise manipulate SQLite sidecars as part of this preflight.

The backup helper writes a temporary snapshot in the backup destination directory and atomically publishes it. The restore helper similarly writes a temporary restored copy in the restore destination directory. The retained backup and restored copy are both present after a successful drill.

For two destinations on the **same filesystem**, use the conservative bound:

```
required_free_bytes >= 3 * S + max(64 MiB, ceil(0.10 * 3 * S))
```

For destinations on **separate filesystems**, independently require at least `S + max(64 MiB, ceil(0.10 * S))` free on the backup filesystem and the restore filesystem. The source filesystem must retain its normal operating headroom; do not count existing source/WAL bytes as newly required drill space.

This deliberately overestimates peak allocation to account for temporary publication, retained outputs, filesystem overhead and a safety margin. If measured free space is below the applicable bound, stop before creating either artifact.

Use two new, distinct destination paths on storage controlled by the backend owner. Both must be absent before the drill. Do not place either destination over the source, a live database, a symlink target, or an existing backup. Keep the report and artifacts in a private owner-only directory. The helper applies owner-only file permissions on POSIX and fails closed if it cannot safely publish.

Do not place backup artifacts in a publicly served frontend directory, repository checkout, shared downloads folder, or cloud-sync directory.

### Automated capacity preflight (enforced by the CLI)

Before creating either output artifact, the drill now opens the source read-only and measures:

- source main-file bytes;
- WAL sidecar bytes when present;
- logical database bytes from `PRAGMA page_count × page_size`;
- estimated snapshot size (S = max(main + WAL, logical));
- available bytes on the backup and restore destination filesystems.

If both destinations share a filesystem, the CLI requires at least:

```
3 × S + max(64 MiB, ceil(10% × 3 × S))
```

If they are on separate filesystems, each destination filesystem must independently provide:

```
S + max(64 MiB, ceil(10% × S))
```

A non-empty rollback-journal sidecar while the database is not in WAL mode, an unmeasurable database size, or insufficient free space causes a fail-closed stop before backup/restore artifacts are created. The success report records the size estimates, required capacity and observed free bytes without disclosing host paths. Keep the application database stable during the drill; this preflight does not replace the owner-host operational window or the actual restore acceptance checks.

## 4. Execution contract

The existing command is:

```text
python -m app.sqlite_restore_drill --source PATH --backup NEW_BACKUP_PATH --restore NEW_RESTORE_PATH
```

It must be run from the backend package context so `app` imports resolve. Replace each path only after the owner has verified the actual source and selected two new destinations. Never execute a placeholder literally.

The source is opened read-only. The drill refuses existing backup/restore destinations and refuses path collisions. It does not modify the source. Failed verification removes only output files that this invocation successfully published; successful backup and restore artifacts are retained.

The command emits a redacted JSON report on success. A failed run emits a generic failure status and exception type only; it intentionally withholds paths and raw error details. Preserve the original protected logs locally for operator diagnosis without copying secrets or database contents into the repository.

## 5. Acceptance calculation

Define:

- (I): SQLite integrity checks passed for backup and restored copy;
- (F): foreign-key checks passed for both;
- (T): required tables, table row counts, row hashes and schema hashes match;
- (D): application-domain readback completed and returned valid aggregates;
- (O): outbox event ID/cursor uniqueness check passed;
- (W): committed write, fresh read-only readback and cleanup all passed;
- (P): privacy and artifact-path handling checks passed.

Acceptance is conjunctive, not an average:

```
PASS = I AND F AND T AND D AND O AND W AND P
```

One failed or unobserved term means Gate 30 remains OPEN. A high percentage cannot compensate for a failed integrity or domain-readback check.

## 6. Evidence to retain

Retain, in the owner-controlled private location:

- the redacted JSON report and its `report_sha256`;
- source, backup and restored-copy file sizes;
- backup and restore SHA-256 values;
- UTC start/end time and elapsed milliseconds;
- the exact backend code commit used for the drill;
- confirmation of the effective database-path source (record the configuration key and whether default/override was used; do not put credentials or unrelated environment values in the report);
- available-space measurements before execution;
- any failure category and operator remediation.

Do not commit database files, backup files, restore files, raw application records, tokens, or host paths to GitHub.

## 7. Stop conditions

Stop without attempting a workaround if:

- the target backend host or active database cannot be identified;
- the effective path is uncertain or points to a test/empty database;
- free space is below the calculated threshold;
- either output path already exists;
- source and output paths resolve to the same file;
- storage does not support the helper's atomic publication requirements;
- integrity, foreign-key, schema, row-hash, domain-readback, outbox or probe checks fail;
- the backend is actively changing its database in a way that prevents a consistent operational window.

Do not delete the source, overwrite a prior backup, disable SQLite checks, or treat a failed report as a pass.

## 8. Current blocker and ownership boundary

Repository inspection confirms the application default is `./data/instrument_registry.sqlite3`, overridden by `INSTRUMENT_REGISTRY_DB_PATH`. It does not reveal the value injected into the live backend process, its host, process working directory, or mounted volume. Those are runtime facts and cannot be derived from GitHub source.

Permission to use Termux does not grant this chat a remote shell on the Android device or on a separate backend host. No device command has been executed. If the backend is on the Android device, the owner can provide the verified process/path context for the controlled drill. If it is on another host, the drill must run there using that host's approved access method; running it against a phone-side copy would not satisfy Gate 30.

**Gate 30 remains 🟧 OPEN** until the actual owner-host drill produces a PASS report and the owner verifies the report/artifact custody. This runbook itself awards no Stage 1 tick.
