"""Consistent SQLite backup helper for file-backed application databases.

This creates a transactionally consistent local snapshot using SQLite's Online
Backup API. It does not encrypt or upload the result; off-host retention must
wrap the resulting file in an approved encryption and storage workflow.
"""
from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import tempfile


def _fsync_directory(directory: Path) -> None:
    """Persist directory-entry changes on POSIX filesystems."""
    descriptor = os.open(
        directory,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def create_consistent_sqlite_backup(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    pages: int = 256,
) -> Path:
    """Create and atomically publish a consistent SQLite database snapshot.

    The destination is first written to a temporary file in the destination
    directory, checked with PRAGMA integrity_check, restricted to owner-only
    permissions where supported, and flushed before atomic replacement. On
    POSIX, the containing directory is flushed after replacement so the
    directory-entry update is persisted as well.

    Failures before replacement leave any previous destination untouched. If
    the post-replacement directory flush fails, the new valid snapshot may
    already be visible, but crash durability of the rename is uncertain; the
    error is raised rather than reported as a fully durable backup.
    """
    if not isinstance(pages, int) or isinstance(pages, bool) or pages < 1:
        raise ValueError("pages must be a positive integer.")

    source = Path(source_path).expanduser().resolve()
    destination = Path(destination_path).expanduser().resolve()

    if source == destination:
        raise ValueError("source_path and destination_path must be different.")
    if not source.is_file():
        raise FileNotFoundError(source)

    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".sqlite-backup.tmp",
        dir=destination.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    source_db: sqlite3.Connection | None = None
    destination_db: sqlite3.Connection | None = None

    try:
        source_db = sqlite3.connect(
            f"{source.as_uri()}?mode=ro",
            uri=True,
            timeout=30,
        )
        destination_db = sqlite3.connect(str(temporary), timeout=30)
        source_db.backup(destination_db, pages=pages, sleep=0.01)

        integrity = destination_db.execute("PRAGMA integrity_check").fetchone()
        if integrity is None or integrity[0] != "ok":
            detail = "no result" if integrity is None else str(integrity[0])
            raise sqlite3.DatabaseError(
                f"SQLite backup integrity check failed: {detail}"
            )
        destination_db.close()
        destination_db = None
        source_db.close()
        source_db = None

        if os.name == "posix":
            # Backups contain application data: never publish a POSIX snapshot
            # if owner-only permissions or the file flush cannot be completed.
            os.chmod(temporary, 0o600)
            with temporary.open("rb") as backup_file:
                os.fsync(backup_file.fileno())
        os.replace(temporary, destination)
        if os.name == "posix":
            # The rename is already visible. If this fails, surface the
            # durability uncertainty; do not pretend the backup is durable.
            _fsync_directory(destination.parent)
        return destination
    finally:
        if destination_db is not None:
            destination_db.close()
        if source_db is not None:
            source_db.close()
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def restore_consistent_sqlite_backup(
    backup_path: str | Path,
    destination_path: str | Path,
) -> Path:
    """Restore a verified SQLite backup to a new path without overwriting data.

    The backup is opened read-only and copied through SQLite's Online Backup
    API into a temporary file in the destination directory. The copy must pass
    integrity_check and foreign_key_check before it is published. On POSIX,
    the temporary file is owner-only and flushed before publication.

    Publication uses a same-directory hard link, which atomically fails if the
    destination already exists. Filesystems that do not support hard links fail
    closed rather than falling back to an overwrite-prone operation. The
    destination directory is flushed after publication on POSIX. If that final
    flush fails, the restored file may already be visible but crash durability
    of the directory entry is uncertain; the error is raised.
    """
    backup = Path(backup_path).expanduser().resolve()
    destination = Path(destination_path).expanduser().resolve()

    if backup == destination:
        raise ValueError("backup_path and destination_path must be different.")
    if not backup.is_file():
        raise FileNotFoundError(backup)
    if destination.exists():
        raise FileExistsError(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".sqlite-restore.tmp",
        dir=destination.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    source_db: sqlite3.Connection | None = None
    destination_db: sqlite3.Connection | None = None

    try:
        source_db = sqlite3.connect(
            f"{backup.as_uri()}?mode=ro",
            uri=True,
            timeout=30,
        )
        destination_db = sqlite3.connect(str(temporary), timeout=30)
        source_db.backup(destination_db)

        integrity_rows = destination_db.execute(
            "PRAGMA integrity_check"
        ).fetchall()
        if integrity_rows != [("ok",)]:
            raise sqlite3.DatabaseError(
                "SQLite restore integrity check failed."
            )
        foreign_key_errors = destination_db.execute(
            "PRAGMA foreign_key_check"
        ).fetchmany(1)
        if foreign_key_errors:
            raise sqlite3.DatabaseError(
                "SQLite restore foreign-key check failed."
            )

        destination_db.close()
        destination_db = None
        source_db.close()
        source_db = None

        if os.name == "posix":
            os.chmod(temporary, 0o600)
            with temporary.open("rb") as restored_file:
                os.fsync(restored_file.fileno())

        # A hard link publishes the completed file atomically and never
        # replaces a destination created concurrently by another process.
        os.link(temporary, destination)
        temporary.unlink()
        if os.name == "posix":
            _fsync_directory(destination.parent)
        return destination
    finally:
        if destination_db is not None:
            destination_db.close()
        if source_db is not None:
            source_db.close()
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
