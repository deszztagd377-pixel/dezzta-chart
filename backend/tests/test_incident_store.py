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
