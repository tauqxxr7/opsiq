import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from core.security import Role, hash_password


DEFAULT_DB = Path(__file__).parents[1] / "data" / "opsiq.db"
DB_PATH = Path(os.getenv("OPSIQ_DB_PATH", str(DEFAULT_DB)))


class OperationalStore:
    def __init__(self, path: Path | str = DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.initialize()

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self):
        with self._lock, self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
              username TEXT PRIMARY KEY, display_name TEXT NOT NULL, password_hash TEXT NOT NULL,
              role TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS incidents (
              incident_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL, plant TEXT NOT NULL, unit TEXT NOT NULL,
              severity TEXT NOT NULL, status TEXT NOT NULL, reported_at TEXT NOT NULL, description TEXT NOT NULL,
              symptoms TEXT NOT NULL DEFAULT '[]', suspected_cause TEXT, confirmed_root_cause TEXT,
              downtime_minutes INTEGER NOT NULL DEFAULT 0, cost REAL NOT NULL DEFAULT 0,
              corrective_action TEXT, created_by TEXT NOT NULL, assigned_to TEXT, closed_at TEXT,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_incidents_filter ON incidents(asset_id, plant, unit, severity, status, reported_at);
            CREATE TABLE IF NOT EXISTS work_orders (
              work_order_id TEXT PRIMARY KEY, incident_id TEXT, asset_id TEXT NOT NULL, priority TEXT NOT NULL,
              status TEXT NOT NULL, recommended_action TEXT NOT NULL, required_parts TEXT NOT NULL DEFAULT '[]',
              required_skills TEXT NOT NULL DEFAULT '[]', assigned_to TEXT, created_at TEXT NOT NULL,
              approved_at TEXT, completed_at TEXT, approval_history TEXT NOT NULL DEFAULT '[]',
              completion_notes TEXT, created_by TEXT NOT NULL, updated_at TEXT NOT NULL,
              FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
            );
            CREATE INDEX IF NOT EXISTS idx_work_orders_filter ON work_orders(asset_id, incident_id, priority, status, created_at);
            ''')
            username = os.getenv("OPSIQ_ADMIN_USERNAME", "").strip()
            password = os.getenv("OPSIQ_ADMIN_PASSWORD", "")
            if username and password and not self.get_user(username, db):
                db.execute("INSERT INTO users VALUES(?,?,?,?,1,?)", (username, os.getenv("OPSIQ_ADMIN_DISPLAY_NAME", "OPSIQ Administrator"), hash_password(password), Role.ADMINISTRATOR.value, self.now()))

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _row(row, json_fields=()):
        if not row:
            return None
        value = dict(row)
        for field in json_fields:
            value[field] = json.loads(value[field] or "[]")
        if "active" in value:
            value["active"] = bool(value["active"])
        value.pop("password_hash", None)
        return value

    def get_user(self, username, db=None, include_hash=False):
        owns = db is None
        db = db or self.connect()
        try:
            row = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            if not row:
                return None
            value = dict(row)
            value["active"] = bool(value["active"])
            if not include_hash:
                value.pop("password_hash", None)
            return value
        finally:
            if owns: db.close()

    def create_user(self, data):
        with self._lock, self.connect() as db:
            db.execute("INSERT INTO users VALUES(?,?,?,?,1,?)", (data["username"], data["display_name"], hash_password(data["password"]), data["role"], self.now()))
        return self.get_user(data["username"])

    def list_users(self):
        with self.connect() as db:
            return [self._row(row) for row in db.execute("SELECT * FROM users ORDER BY username")]

    def list_records(self, table, filters, limit, offset):
        json_fields = ("symptoms",) if table == "incidents" else ("required_parts", "required_skills", "approval_history")
        clauses, values = [], []
        for key, value in filters.items():
            if value is not None:
                clauses.append(f"{key}=?"); values.append(value)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self.connect() as db:
            total = db.execute(f"SELECT COUNT(*) FROM {table}{where}", values).fetchone()[0]
            rows = db.execute(f"SELECT * FROM {table}{where} ORDER BY created_at DESC LIMIT ? OFFSET ?", (*values, limit, offset)).fetchall()
        return {"items": [self._row(row, json_fields) for row in rows], "total": total, "limit": limit, "offset": offset}

    def get_record(self, table, record_id):
        key = "incident_id" if table == "incidents" else "work_order_id"
        fields = ("symptoms",) if table == "incidents" else ("required_parts", "required_skills", "approval_history")
        with self.connect() as db:
            return self._row(db.execute(f"SELECT * FROM {table} WHERE {key}=?", (record_id,)).fetchone(), fields)

    def create_incident(self, data, actor):
        now = self.now(); values = data.copy()
        values["incident_id"] = values.get("incident_id") or f"INC-{datetime.now():%Y%m%d}-{str(uuid4())[:6].upper()}"
        values.update(created_by=actor, created_at=now, updated_at=now)
        fields = ["incident_id","asset_id","plant","unit","severity","status","reported_at","description","symptoms","suspected_cause","confirmed_root_cause","downtime_minutes","cost","corrective_action","created_by","assigned_to","closed_at","created_at","updated_at"]
        values["symptoms"] = json.dumps(values.get("symptoms", []))
        with self._lock, self.connect() as db:
            db.execute(f"INSERT INTO incidents ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})", [values.get(field) for field in fields])
        return self.get_record("incidents", values["incident_id"])

    def create_work_order(self, data, actor):
        now=self.now(); values=data.copy(); values["work_order_id"] = values.get("work_order_id") or f"WO-{datetime.now():%Y%m%d}-{str(uuid4())[:6].upper()}"
        values.update(created_by=actor, created_at=values.get("created_at") or now, updated_at=now)
        fields=["work_order_id","incident_id","asset_id","priority","status","recommended_action","required_parts","required_skills","assigned_to","created_at","approved_at","completed_at","approval_history","completion_notes","created_by","updated_at"]
        for field in ("required_parts","required_skills","approval_history"): values[field]=json.dumps(values.get(field, []))
        with self._lock, self.connect() as db:
            db.execute(f"INSERT INTO work_orders ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})", [values.get(field) for field in fields])
        return self.get_record("work_orders", values["work_order_id"])

    def update_record(self, table, record_id, updates):
        if not updates: return self.get_record(table, record_id)
        key="incident_id" if table=="incidents" else "work_order_id"
        json_fields={"symptoms","required_parts","required_skills","approval_history"}
        values={name:(json.dumps(value) if name in json_fields else value) for name,value in updates.items()}
        values["updated_at"]=self.now()
        with self._lock, self.connect() as db:
            cursor=db.execute(f"UPDATE {table} SET {','.join(f'{name}=?' for name in values)} WHERE {key}=?", (*values.values(), record_id))
            if not cursor.rowcount: return None
        return self.get_record(table, record_id)
