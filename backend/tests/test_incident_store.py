from datetime import datetime, timedelta, timezone
import pytest
from app.incident_store import IncidentCapacityError, SQLiteIncidentStore


def _at(minutes=0):
    return datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def test_journal_persists_and_deduplicates_active_incident(tmp_path):
    path=str(tmp_path/"incidents.sqlite3")
    store=SQLiteIncidentStore(path)
    first=store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
        severity="warning",summary_code="delivery_attention",now_utc=_at())
    second=store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
        severity="critical",summary_code="delivery_attention",now_utc=_at(1))
    rows=SQLiteIncidentStore(path).list_incidents()
    assert first["incident_id"]==second["incident_id"]
    assert rows[0]["occurrence_count"]==2 and rows[0]["severity"]=="critical"
    assert rows[0]["first_seen_utc"]==first["first_seen_utc"]


def test_acknowledgement_stops_escalation_and_new_occurrence_reopens(tmp_path):
    store=SQLiteIncidentStore(str(tmp_path/"incidents.sqlite3"))
    incident=store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
        severity="warning",summary_code="delivery_attention",now_utc=_at())
    ack=store.acknowledge(incident["incident_id"],now_utc=_at(1))
    assert ack["status"]=="acknowledged" and ack["next_escalation_utc"] is None
    assert store.escalate_due(now_utc=_at(100))==[]
    reopened=store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
        severity="critical",summary_code="delivery_attention",now_utc=_at(2))
    assert reopened["incident_id"]==incident["incident_id"]
    assert reopened["status"]=="open" and reopened["acknowledged_at_utc"] is None
    assert reopened["escalation_count"]==0


def test_local_escalation_has_three_bounded_levels(tmp_path):
    store=SQLiteIncidentStore(str(tmp_path/"incidents.sqlite3"))
    store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
        severity="critical",summary_code="delivery_attention",now_utc=_at())
    assert store.escalate_due(now_utc=_at(5))[0]["escalation_level"]==1
    assert store.escalate_due(now_utc=_at(15))[0]["escalation_level"]==2
    assert store.escalate_due(now_utc=_at(30))[0]["escalation_level"]==3
    assert store.escalate_due(now_utc=_at(90))==[]


def test_resolve_allows_new_incident_identity(tmp_path):
    store=SQLiteIncidentStore(str(tmp_path/"incidents.sqlite3"))
    first=store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
        severity="warning",summary_code="delivery_attention",now_utc=_at())
    store.resolve(first["incident_id"],now_utc=_at(1))
    second=store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
        severity="warning",summary_code="delivery_attention",now_utc=_at(2))
    assert first["incident_id"]!=second["incident_id"] and second["status"]=="open"


def test_journal_rejects_free_form_fields_and_naive_timestamps(tmp_path):
    store=SQLiteIncidentStore(str(tmp_path/"incidents.sqlite3"))
    with pytest.raises(ValueError):
        store.record_incident(fingerprint="account:email@example.com",category="alert_delivery",
            severity="warning",summary_code="delivery_attention")
    with pytest.raises(ValueError):
        store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
            severity="warning",summary_code="secret provider response")
    with pytest.raises(ValueError,match="timezone-aware"):
        store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
            severity="warning",summary_code="delivery_attention",now_utc=datetime(2026,11,20,12,0))


def test_journal_list_limit_is_bounded(tmp_path):
    store=SQLiteIncidentStore(str(tmp_path/"incidents.sqlite3"))
    with pytest.raises(ValueError):
        store.list_incidents(limit=1000)


def test_journal_capacity_fails_closed_without_dropping_open_incidents(tmp_path, monkeypatch):
    import app.incident_store as incident_module
    monkeypatch.setattr(incident_module, "_MAX_ROWS", 1)
    store=SQLiteIncidentStore(str(tmp_path/"incidents.sqlite3"))
    first=store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
        severity="warning",summary_code="delivery_attention",now_utc=_at())
    with pytest.raises(IncidentCapacityError):
        store.record_incident(fingerprint="alert_delivery_worker:error",category="alert_delivery",
            severity="critical",summary_code="worker_error",now_utc=_at(1))
    rows=store.list_incidents()
    assert len(rows)==1 and rows[0]["incident_id"]==first["incident_id"]
    assert rows[0]["status"]=="open"


def test_journal_prunes_only_resolved_incidents_older_than_retention(tmp_path):
    store=SQLiteIncidentStore(str(tmp_path/"incidents.sqlite3"))
    old=store.record_incident(fingerprint="alert_delivery_degraded",category="alert_delivery",
        severity="warning",summary_code="delivery_attention",now_utc=_at(-60*24*60))
    store.resolve(old["incident_id"],now_utc=_at(-60*24*60+1))
    active=store.record_incident(fingerprint="alert_delivery_worker:error",category="alert_delivery",
        severity="critical",summary_code="worker_error",now_utc=_at())
    rows=store.list_incidents()
    assert [row["incident_id"] for row in rows]==[active["incident_id"]]


def test_worker_error_is_journaled_and_recovery_resolves_it(tmp_path):
    import logging
    from app.alert_operations import LocalAlertReporter
    store=SQLiteIncidentStore(str(tmp_path/"incidents.sqlite3"))
    reporter=LocalAlertReporter(logging.getLogger("test.incident.worker-error"),incident_store=store)
    reporter.report_error(RuntimeError("sensitive provider response must not be stored"))
    rows=store.list_incidents()
    assert len(rows)==1
    assert rows[0]["fingerprint"]=="alert_delivery_worker:RuntimeError"
    assert rows[0]["summary_code"]=="worker_error"
    assert "sensitive provider response" not in str(rows)
    reporter.report_batch(claimed=0,delivered=0,retry_scheduled=0,terminal_failed=0,lease_lost=0)
    assert store.list_incidents()[0]["status"]=="resolved"
