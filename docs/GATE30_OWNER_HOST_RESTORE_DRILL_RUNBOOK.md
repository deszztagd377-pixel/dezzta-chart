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

Let `S` be the current source database file size in bytes.

The backup helper writes a temporary backup file in the backup destination directory before atomic publication. The restore helper similarly writes a temporary restore file before publishing the restored copy. The final backup and restored copy are retained for inspection.

Conservative additional free-space planning:

```
required_free_bytes >= 3 * S + max(64 MiB, ceil(0.10 * 3 * S))
```

This covers the backup temporary file, retained backup, restore temporary file, plus a minimum/percentage safety margin. The source file itself is already present and is not included in the additional-free-space figure. Check available space on both destination filesystems if the two destinations are on different mounts; each mount must independently accommodate its peak temporary/final allocation.

Use two new, distinct destination paths on storage controlled by the backend owner. Both must be absent before the drill. Do not place either destination over the source, a live database, a symlink target, or an existing backup. Keep the report and artifacts in a private owner-only directory. The helper applies owner-only file permissions on POSIX and fails closed if it cannot safely publish.

Do not place backup artifacts in a publicly served frontend directory, repository checkout, shared downloads folder, or cloud-sync directory.

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
