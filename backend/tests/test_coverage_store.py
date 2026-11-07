from app.coverage_store import SQLiteCoverageTracker


def test_covered_intervals_and_explicit_gaps_survive_restart(tmp_path):
    path = str(tmp_path / "coverage.sqlite3")
    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    tracker = SQLiteCoverageTracker(path)
    tracker.add_covered(scope, 0, 100)
    tracker.add_gap(scope, 30, 50)

    assert tracker.status(scope, 0, 30) == "covered"
    assert tracker.status(scope, 30, 50) == "unknown"
    assert tracker.status(scope, 50, 100) == "covered"
    assert tracker.gaps(scope) == [(30, 50)]

    restored = SQLiteCoverageTracker(path)
    assert restored.intervals(scope) == [(0, 30), (50, 100)]
    assert restored.gaps(scope) == [(30, 50)]
    assert restored.status(scope, 0, 100) == "partial"


def test_successful_backfill_fills_and_removes_overlapping_gap(tmp_path):
    path = str(tmp_path / "coverage.sqlite3")
    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    tracker = SQLiteCoverageTracker(path)
    tracker.add_covered(scope, 0, 100)
    tracker.add_gap(scope, 30, 70)
    tracker.add_covered(scope, 40, 60)

    assert tracker.gaps(scope) == [(30, 40), (60, 70)]
    assert tracker.intervals(scope) == [(0, 30), (40, 60), (70, 100)]
    assert tracker.status(scope, 40, 60) == "covered"

    restarted = SQLiteCoverageTracker(path)
    assert restarted.gaps(scope) == [(30, 40), (60, 70)]
    assert restarted.intervals(scope) == [(0, 30), (40, 60), (70, 100)]


def test_gap_is_recorded_even_when_no_covered_interval_exists(tmp_path):
    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    tracker = SQLiteCoverageTracker(str(tmp_path / "coverage.sqlite3"))
    tracker.add_gap(scope, 100, 200)
    assert tracker.gaps(scope) == [(100, 200)]
    assert tracker.intervals(scope) == []
    assert tracker.status(scope, 100, 200) == "unknown"


def test_gap_interval_count_is_bounded_and_truncation_survives_restart(tmp_path):
    path = str(tmp_path / "coverage.sqlite3")
    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    tracker = SQLiteCoverageTracker(path, max_intervals=2)
    tracker.add_gap(scope, 0, 1)
    tracker.add_gap(scope, 3, 4)
    tracker.add_gap(scope, 6, 7)
    assert tracker.gaps(scope) == [(3, 4), (6, 7)]
    assert tracker.truncated == 1

    restarted = SQLiteCoverageTracker(path, max_intervals=2)
    assert restarted.gaps(scope) == [(3, 4), (6, 7)]
    assert restarted.truncated == 1


def test_failed_coverage_persistence_rolls_back_in_memory_state(tmp_path):
    class FailingTracker(SQLiteCoverageTracker):
        def _persist_scope(self, scope):
            raise OSError("disk unavailable")

    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    tracker = FailingTracker(str(tmp_path / "coverage.sqlite3"))
    import pytest
    with pytest.raises(OSError):
        tracker.add_covered(scope, 0, 100)
    assert tracker.intervals(scope) == []
    with pytest.raises(OSError):
        tracker.add_gap(scope, 100, 200)
    assert tracker.gaps(scope) == []



def test_overflow_journal_is_idempotent_and_survives_restart(tmp_path):
    path = str(tmp_path / "coverage.sqlite3")
    tracker = SQLiteCoverageTracker(path)
    hint = (7, 101)

    first_id = tracker.journal_overflow(hint, 1_000, 2_000, 10)
    duplicate_id = tracker.journal_overflow(hint, 1_000, 2_000, 11)

    assert duplicate_id == first_id
    restored = SQLiteCoverageTracker(path)
    assert restored.pending_overflows() == [{
        "id": first_id,
        "instrument_hint": hint,
        "start_ns": 1_000,
        "end_ns": 2_000,
        "created_at_ns": 10,
    }]

    restored.resolve_overflow(first_id)
    assert SQLiteCoverageTracker(path).pending_overflows() == []


def test_failed_overflow_journal_delete_rolls_back_and_preserves_record(tmp_path):
    import sqlite3
    import pytest

    path = str(tmp_path / "journal-delete-rollback.sqlite3")
    tracker = SQLiteCoverageTracker(path)
    journal_id = tracker.journal_overflow((7, 101), 1_000, 2_000, 10)

    class DeleteBlockedTracker(SQLiteCoverageTracker):
        def _connect(self):
            db = super()._connect()

            def deny_delete(action, arg1, arg2, database, trigger):
                if action == sqlite3.SQLITE_DELETE and arg1 == "ohlcv_overflow_journal":
                    return sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK

            db.set_authorizer(deny_delete)
            return db

    blocked = DeleteBlockedTracker(path)
    with pytest.raises(sqlite3.DatabaseError):
        blocked.resolve_overflow(journal_id)

    # The failed transaction must not erase the durable recovery record.
    pending = SQLiteCoverageTracker(path).pending_overflows()
    assert [row["id"] for row in pending] == [journal_id]


def test_unscoped_overflow_journal_survives_restart_until_resolved(tmp_path):
    path = str(tmp_path / "coverage.sqlite3")
    tracker = SQLiteCoverageTracker(path)
    journal_id = tracker.journal_overflow(None, 3_000, 4_000, 20)

    restarted = SQLiteCoverageTracker(path)
    pending = restarted.pending_overflows()
    assert len(pending) == 1
    assert pending[0]["id"] == journal_id
    assert pending[0]["instrument_hint"] is None

def test_concurrent_connections_preserve_all_overflow_journal_records(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    path = str(tmp_path / "concurrent-coverage.sqlite3")
    tracker = SQLiteCoverageTracker(path, busy_timeout_ms=10_000)
    workers = 8
    records_per_worker = 20

    def journal_partition(worker):
        ids = []
        for offset in range(records_per_worker):
            index = worker * records_per_worker + offset
            ids.append(tracker.journal_overflow(
                (worker, index), index * 100, index * 100 + 50, index,
            ))
        return ids

    with ThreadPoolExecutor(max_workers=workers) as executor:
        partitions = list(executor.map(journal_partition, range(workers)))

    ids = [journal_id for partition in partitions for journal_id in partition]
    pending = tracker.pending_overflows()
    assert len(ids) == workers * records_per_worker
    assert len(set(ids)) == len(ids)
    assert len(pending) == workers * records_per_worker
    assert {row["id"] for row in pending} == set(ids)
