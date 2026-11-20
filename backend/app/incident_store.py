"""Bounded, persistent SQLite incident journal for local operator response."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import sqlite3
from uuid import uuid4

_FINGERPRINT = re.compile(r"^[a-z0-9_.:-]{1,96}$")
_CODE = re.compile(r"^[a-z0-9_]{1,64}$")
_SEVERITY = {"info": 0, "warning": 1, "error": 2, "critical": 3}
_DELAYS = (300, 600, 900)
_MAX_ROWS = 1000
_RETENTION_DAYS = 30


class IncidentCapacityError(RuntimeError):
    """The bounded journal is full of unresolved incidents."""


def _utc(value=None):
    result = value or datetime.now(timezone.utc)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Incident timestamps must be timezone-aware.")
    return result.astimezone(timezone.utc).replace(microsecond=0)


class SQLiteIncidentStore:
    """Durable, deduplicated and capacity-bounded operator incident journal."""
    def __init__(self, database_path: str, *, busy_timeout_ms: int = 10_000):
        if not isinstance(database_path, str) or not database_path.strip() or database_path == ":memory:":
            raise ValueError("A file-backed incident database path is required.")
        if not isinstance(busy_timeout_ms, int) or isinstance(busy_timeout_ms, bool) or busy_timeout_ms < 1:
            raise ValueError("busy_timeout_ms must be a positive integer.")
        self.database_path = str(Path(database_path).expanduser())
        self.busy_timeout_ms = busy_timeout_ms
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=self.busy_timeout_ms / 1000, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
        return connection

    def _initialize(self):
        connection = self._connect()
        try:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS operator_incidents (
                    incident_id TEXT PRIMARY KEY NOT NULL,
                    fingerprint TEXT NOT NULL,
                    category TEXT NOT NULL CHECK(category='alert_delivery'),
                    severity TEXT NOT NULL CHECK(severity IN ('info','warning','error','critical')),
                    status TEXT NOT NULL CHECK(status IN ('open','acknowledged','resolved')),
                    summary_code TEXT NOT NULL,
                    occurrence_count INTEGER NOT NULL CHECK(occurrence_count BETWEEN 1 AND 2147483647),
                    first_seen_utc TEXT NOT NULL,
                    last_seen_utc TEXT NOT NULL,
                    acknowledged_by TEXT,
                    acknowledged_at_utc TEXT,
                    resolved_at_utc TEXT,
                    escalation_count INTEGER NOT NULL DEFAULT 0 CHECK(escalation_count BETWEEN 0 AND 3),
                    next_escalation_utc TEXT,
                    created_at_utc TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_operator_incidents_active_fingerprint
                ON operator_incidents(fingerprint) WHERE status != 'resolved'
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_operator_incidents_status_last_seen
                ON operator_incidents(status,last_seen_utc DESC)
            """)
        finally:
            connection.close()

    @staticmethod
    def _validate(fingerprint, category, severity, summary_code):
        if not isinstance(fingerprint, str) or not _FINGERPRINT.fullmatch(fingerprint):
            raise ValueError("Incident fingerprint is invalid.")
        if category != "alert_delivery":
            raise ValueError("Incident category is invalid.")
        if severity not in _SEVERITY:
            raise ValueError("Incident severity is invalid.")
        if not isinstance(summary_code, str) or not _CODE.fullmatch(summary_code):
            raise ValueError("Incident summary code is invalid.")

    @staticmethod
    def _row(row):
        return {key: row[key] for key in (
            "incident_id","fingerprint","category","severity","status","summary_code",
            "occurrence_count","first_seen_utc","last_seen_utc","acknowledged_by",
            "acknowledged_at_utc","resolved_at_utc","escalation_count","next_escalation_utc"
        )}

    def record_incident(self, *, fingerprint, category, severity, summary_code, now_utc=None):
        self._validate(fingerprint, category, severity, summary_code)
        now = _utc(now_utc)
        stamp = now.isoformat()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            cutoff = (now - timedelta(days=_RETENTION_DAYS)).isoformat()
            connection.execute("DELETE FROM operator_incidents WHERE status='resolved' AND resolved_at_utc < ?", (cutoff,))
            row = connection.execute(
                "SELECT * FROM operator_incidents WHERE fingerprint=? AND status!='resolved'", (fingerprint,)
            ).fetchone()
            if row:
                acknowledged = row["status"] == "acknowledged"
                rank = max(_SEVERITY[row["severity"]], _SEVERITY[severity])
                severity_value = next(k for k,v in _SEVERITY.items() if v == rank)
                connection.execute("""
                    UPDATE operator_incidents SET severity=?,status='open',summary_code=?,
                        occurrence_count=MIN(occurrence_count+1,2147483647),last_seen_utc=?,
                        acknowledged_by=NULL,acknowledged_at_utc=NULL,
                        escalation_count=CASE WHEN ? THEN 0 ELSE escalation_count END,
                        next_escalation_utc=CASE WHEN ? THEN ? ELSE next_escalation_utc END
                    WHERE incident_id=?
                """, (severity_value,summary_code,stamp,int(acknowledged),int(acknowledged),
                      (now+timedelta(seconds=_DELAYS[0])).isoformat(),row["incident_id"]))
                updated=connection.execute("SELECT * FROM operator_incidents WHERE incident_id=?",(row["incident_id"],)).fetchone()
                connection.commit()
                return self._row(updated)
            total=connection.execute("SELECT COUNT(*) FROM operator_incidents").fetchone()[0]
            if total >= _MAX_ROWS:
                raise IncidentCapacityError("Incident journal capacity is exhausted.")
            incident_id=str(uuid4())
            connection.execute("""
                INSERT INTO operator_incidents(
                    incident_id,fingerprint,category,severity,status,summary_code,occurrence_count,
                    first_seen_utc,last_seen_utc,next_escalation_utc,created_at_utc
                ) VALUES(?,?,?,?, 'open', ?,1,?,?,?,?)
            """,(incident_id,fingerprint,category,severity,summary_code,stamp,stamp,
                 (now+timedelta(seconds=_DELAYS[0])).isoformat(),stamp))
            created=connection.execute("SELECT * FROM operator_incidents WHERE incident_id=?",(incident_id,)).fetchone()
            connection.commit()
            return self._row(created)
        except Exception:
            if connection.in_transaction: connection.rollback()
            raise
        finally:
            connection.close()

    def list_incidents(self, *, limit=50):
        if not isinstance(limit,int) or isinstance(limit,bool) or not 1 <= limit <= 100:
            raise ValueError("Incident list limit must be between 1 and 100.")
        connection=self._connect()
        try:
            rows=connection.execute("""
                SELECT * FROM operator_incidents
                ORDER BY CASE status WHEN 'open' THEN 0 WHEN 'acknowledged' THEN 1 ELSE 2 END,
                         last_seen_utc DESC LIMIT ?
            """,(limit,)).fetchall()
            return [self._row(row) for row in rows]
        finally: connection.close()

    def acknowledge(self, incident_id, *, now_utc=None):
        if not isinstance(incident_id,str) or not incident_id: raise ValueError("Incident identifier is invalid.")
        stamp=_utc(now_utc).isoformat()
        connection=self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row=connection.execute("SELECT * FROM operator_incidents WHERE incident_id=?",(incident_id,)).fetchone()
            if row is None: connection.rollback(); return None
            if row["status"]=="open":
                connection.execute("""
                    UPDATE operator_incidents SET status='acknowledged',acknowledged_by='operator',
                        acknowledged_at_utc=?,next_escalation_utc=NULL WHERE incident_id=?
                """,(stamp,incident_id))
            result=connection.execute("SELECT * FROM operator_incidents WHERE incident_id=?",(incident_id,)).fetchone()
            connection.commit()
            return self._row(result)
        except Exception:
            if connection.in_transaction: connection.rollback()
            raise
        finally: connection.close()

    def resolve(self, incident_id, *, now_utc=None):
        if not isinstance(incident_id,str) or not incident_id: raise ValueError("Incident identifier is invalid.")
        stamp=_utc(now_utc).isoformat()
        connection=self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row=connection.execute("SELECT * FROM operator_incidents WHERE incident_id=?",(incident_id,)).fetchone()
            if row is None: connection.rollback(); return None
            if row["status"]!="resolved":
                connection.execute("""
                    UPDATE operator_incidents SET status='resolved',resolved_at_utc=?,
                        next_escalation_utc=NULL WHERE incident_id=?
                """,(stamp,incident_id))
            result=connection.execute("SELECT * FROM operator_incidents WHERE incident_id=?",(incident_id,)).fetchone()
            connection.commit()
            return self._row(result)
        except Exception:
            if connection.in_transaction: connection.rollback()
            raise
        finally: connection.close()

    def resolve_category(self, category, *, now_utc=None):
        if category!="alert_delivery": raise ValueError("Incident category is invalid.")
        stamp=_utc(now_utc).isoformat()
        connection=self._connect()
        try:
            cursor=connection.execute("""
                UPDATE operator_incidents SET status='resolved',resolved_at_utc=?,next_escalation_utc=NULL
                WHERE category=? AND status!='resolved'
            """,(stamp,category))
            return cursor.rowcount
        finally: connection.close()

    def escalate_due(self, *, now_utc=None):
        now=_utc(now_utc); stamp=now.isoformat()
        connection=self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            rows=connection.execute("""
                SELECT * FROM operator_incidents WHERE status='open'
                  AND next_escalation_utc IS NOT NULL AND next_escalation_utc<=?
                  AND escalation_count<3 ORDER BY next_escalation_utc LIMIT 100
            """,(stamp,)).fetchall()
            result=[]
            for row in rows:
                count=row["escalation_count"]+1
                next_time=(now+timedelta(seconds=_DELAYS[count])).isoformat() if count<3 else None
                connection.execute("""
                    UPDATE operator_incidents SET escalation_count=?,next_escalation_utc=?
                    WHERE incident_id=? AND status='open'
                """,(count,next_time,row["incident_id"]))
                result.append({"incident_id":row["incident_id"],"severity":row["severity"],
                               "summary_code":row["summary_code"],"escalation_level":count})
            connection.commit()
            return result
        except Exception:
            if connection.in_transaction: connection.rollback()
            raise
        finally: connection.close()
