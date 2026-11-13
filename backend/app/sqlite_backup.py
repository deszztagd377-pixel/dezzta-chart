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


def create_consistent_sqlite_backup(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    pages: int = 256,
) -> Path:
    """Create and atomically publish a consistent SQLite database snapshot.

    The destination is first written to a temporary file in the destination
    directory, checked with PRAGMA integrity_check, restricted to owner-only
    permissions where supported, flushed to storage on POSIX, and then
    atomically replaced. A failed backup leaves any previous destination file
    untouched.
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
            # if owner-only permissions cannot be applied or the completed
            # database file cannot be flushed before its atomic publication.
            os.chmod(temporary, 0o600)
            with temporary.open("rb") as backup_file:
                os.fsync(backup_file.fileno())
        os.replace(temporary, destination)
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
