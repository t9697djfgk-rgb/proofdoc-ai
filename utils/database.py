"""
Persistent SQLite storage for ProofDoc AI.
Database file: proofdoc.db (gitignored, lives beside app.py)
"""

import sqlite3
import json
import uuid
from datetime import datetime, date
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / "proofdoc.db"


@contextmanager
def _conn():
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db():
    """Create tables if they don't exist. Call once at app startup."""
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS clients (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                email       TEXT,
                phone       TEXT,
                company     TEXT,
                type        TEXT DEFAULT 'Individual',
                status      TEXT DEFAULT 'Active',
                created_at  TEXT NOT NULL,
                notes       TEXT
            );

            CREATE TABLE IF NOT EXISTS matters (
                id              TEXT PRIMARY KEY,
                ref             TEXT UNIQUE NOT NULL,
                title           TEXT NOT NULL,
                client_id       TEXT REFERENCES clients(id),
                type            TEXT,
                status          TEXT DEFAULT 'Active',
                jurisdiction    TEXT DEFAULT 'UK',
                opened_date     TEXT NOT NULL,
                deadline        TEXT,
                lead_lawyer     TEXT,
                description     TEXT,
                tags            TEXT DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id          TEXT PRIMARY KEY,
                matter_id   TEXT REFERENCES matters(id),
                title       TEXT NOT NULL,
                description TEXT,
                status      TEXT DEFAULT 'Pending',
                priority    TEXT DEFAULT 'Medium',
                due_date    TEXT,
                assigned_to TEXT,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS documents (
                id          TEXT PRIMARY KEY,
                matter_id   TEXT REFERENCES matters(id),
                name        TEXT NOT NULL,
                type        TEXT,
                size_bytes  INTEGER DEFAULT 0,
                uploaded_at TEXT NOT NULL,
                notes       TEXT
            );

            CREATE TABLE IF NOT EXISTS notes (
                id          TEXT PRIMARY KEY,
                matter_id   TEXT REFERENCES matters(id),
                body        TEXT NOT NULL,
                author      TEXT,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS time_entries (
                id          TEXT PRIMARY KEY,
                matter_id   TEXT REFERENCES matters(id),
                date        TEXT NOT NULL,
                hours       REAL NOT NULL,
                rate        REAL DEFAULT 0,
                description TEXT,
                lawyer      TEXT,
                billed      INTEGER DEFAULT 0
            );
        """)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _uid() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _row_to_dict(row) -> dict:
    return dict(row) if row else {}


# ── Clients ──────────────────────────────────────────────────────────────────

def create_client(name: str, email: str = "", phone: str = "", company: str = "",
                  type_: str = "Individual", notes: str = "") -> dict:
    cid = _uid()
    with _conn() as con:
        con.execute(
            "INSERT INTO clients VALUES (?,?,?,?,?,?,?,?,?)",
            (cid, name, email, phone, company, type_, "Active", _now(), notes),
        )
    return get_client(cid)


def get_client(cid: str) -> dict:
    with _conn() as con:
        row = con.execute("SELECT * FROM clients WHERE id=?", (cid,)).fetchone()
    return _row_to_dict(row)


def list_clients(status: str = "") -> list[dict]:
    with _conn() as con:
        if status:
            rows = con.execute("SELECT * FROM clients WHERE status=? ORDER BY name", (status,)).fetchall()
        else:
            rows = con.execute("SELECT * FROM clients ORDER BY name").fetchall()
    return [dict(r) for r in rows]


def update_client(cid: str, **fields) -> dict:
    allowed = {"name", "email", "phone", "company", "type", "status", "notes"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if updates:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        with _conn() as con:
            con.execute(f"UPDATE clients SET {set_clause} WHERE id=?",
                        (*updates.values(), cid))
    return get_client(cid)


def delete_client(cid: str):
    with _conn() as con:
        con.execute("DELETE FROM clients WHERE id=?", (cid,))


# ── Matters ───────────────────────────────────────────────────────────────────

def _next_ref() -> str:
    with _conn() as con:
        count = con.execute("SELECT COUNT(*) FROM matters").fetchone()[0]
    year = datetime.utcnow().year
    return f"MAT-{year}-{count + 1:04d}"


def create_matter(title: str, client_id: str = "", type_: str = "Commercial",
                  jurisdiction: str = "UK", deadline: str = "", lead_lawyer: str = "",
                  description: str = "", tags: list | None = None) -> dict:
    mid = _uid()
    with _conn() as con:
        con.execute(
            "INSERT INTO matters VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (mid, _next_ref(), title, client_id or None, type_, "Active",
             jurisdiction, _now()[:10], deadline or None, lead_lawyer,
             description, json.dumps(tags or [])),
        )
    return get_matter(mid)


def get_matter(mid: str) -> dict:
    with _conn() as con:
        row = con.execute("SELECT * FROM matters WHERE id=?", (mid,)).fetchone()
    if not row:
        return {}
    d = dict(row)
    d["tags"] = json.loads(d.get("tags") or "[]")
    return d


def list_matters(status: str = "", client_id: str = "") -> list[dict]:
    with _conn() as con:
        q = "SELECT * FROM matters WHERE 1=1"
        params: list = []
        if status:
            q += " AND status=?"
            params.append(status)
        if client_id:
            q += " AND client_id=?"
            params.append(client_id)
        q += " ORDER BY opened_date DESC"
        rows = con.execute(q, params).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d.get("tags") or "[]")
        result.append(d)
    return result


def update_matter(mid: str, **fields) -> dict:
    allowed = {"title", "client_id", "type", "status", "jurisdiction",
               "deadline", "lead_lawyer", "description", "tags"}
    updates = {}
    for k, v in fields.items():
        if k not in allowed:
            continue
        updates[k] = json.dumps(v) if k == "tags" else v
    if updates:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        with _conn() as con:
            con.execute(f"UPDATE matters SET {set_clause} WHERE id=?",
                        (*updates.values(), mid))
    return get_matter(mid)


def delete_matter(mid: str):
    with _conn() as con:
        con.execute("DELETE FROM matters WHERE id=?", (mid,))


# ── Tasks ─────────────────────────────────────────────────────────────────────

def create_task(matter_id: str, title: str, description: str = "",
                priority: str = "Medium", due_date: str = "",
                assigned_to: str = "") -> dict:
    tid = _uid()
    with _conn() as con:
        con.execute(
            "INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?)",
            (tid, matter_id or None, title, description, "Pending",
             priority, due_date or None, assigned_to, _now()),
        )
    return get_task(tid)


def get_task(tid: str) -> dict:
    with _conn() as con:
        row = con.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
    return _row_to_dict(row)


def list_tasks(matter_id: str = "", status: str = "") -> list[dict]:
    with _conn() as con:
        q = "SELECT * FROM tasks WHERE 1=1"
        params: list = []
        if matter_id:
            q += " AND matter_id=?"
            params.append(matter_id)
        if status:
            q += " AND status=?"
            params.append(status)
        q += " ORDER BY due_date ASC NULLS LAST, priority DESC"
        rows = con.execute(q, params).fetchall()
    return [dict(r) for r in rows]


def update_task(tid: str, **fields) -> dict:
    allowed = {"title", "description", "status", "priority", "due_date", "assigned_to"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if updates:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        with _conn() as con:
            con.execute(f"UPDATE tasks SET {set_clause} WHERE id=?",
                        (*updates.values(), tid))
    return get_task(tid)


def delete_task(tid: str):
    with _conn() as con:
        con.execute("DELETE FROM tasks WHERE id=?", (tid,))


# ── Notes ─────────────────────────────────────────────────────────────────────

def add_note(matter_id: str, body: str, author: str = "") -> dict:
    nid = _uid()
    with _conn() as con:
        con.execute(
            "INSERT INTO notes VALUES (?,?,?,?,?)",
            (nid, matter_id, body, author, _now()),
        )
    with _conn() as con:
        row = con.execute("SELECT * FROM notes WHERE id=?", (nid,)).fetchone()
    return _row_to_dict(row)


def list_notes(matter_id: str) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM notes WHERE matter_id=? ORDER BY created_at DESC",
            (matter_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Time Entries ──────────────────────────────────────────────────────────────

def add_time_entry(matter_id: str, hours: float, description: str = "",
                   rate: float = 0, lawyer: str = "", entry_date: str = "") -> dict:
    eid = _uid()
    with _conn() as con:
        con.execute(
            "INSERT INTO time_entries VALUES (?,?,?,?,?,?,?,?)",
            (eid, matter_id, entry_date or _now()[:10], hours,
             rate, description, lawyer, 0),
        )
    with _conn() as con:
        row = con.execute("SELECT * FROM time_entries WHERE id=?", (eid,)).fetchone()
    return _row_to_dict(row)


def list_time_entries(matter_id: str = "") -> list[dict]:
    with _conn() as con:
        if matter_id:
            rows = con.execute(
                "SELECT * FROM time_entries WHERE matter_id=? ORDER BY date DESC",
                (matter_id,),
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT * FROM time_entries ORDER BY date DESC"
            ).fetchall()
    return [dict(r) for r in rows]


# ── Stats (for dashboard) ─────────────────────────────────────────────────────

def dashboard_stats() -> dict:
    with _conn() as con:
        active_matters = con.execute(
            "SELECT COUNT(*) FROM matters WHERE status='Active'"
        ).fetchone()[0]
        total_clients = con.execute(
            "SELECT COUNT(*) FROM clients WHERE status='Active'"
        ).fetchone()[0]
        pending_tasks = con.execute(
            "SELECT COUNT(*) FROM tasks WHERE status='Pending'"
        ).fetchone()[0]
        upcoming_deadlines = con.execute(
            "SELECT COUNT(*) FROM matters WHERE deadline IS NOT NULL AND deadline >= date('now') AND deadline <= date('now','+14 days')"
        ).fetchone()[0]
        recent_matters = con.execute(
            "SELECT id, ref, title, status, opened_date FROM matters ORDER BY opened_date DESC LIMIT 5"
        ).fetchall()
        overdue_tasks = con.execute(
            "SELECT id, title, due_date, matter_id FROM tasks WHERE status='Pending' AND due_date < date('now') ORDER BY due_date ASC LIMIT 5"
        ).fetchall()
    return {
        "active_matters": active_matters,
        "total_clients": total_clients,
        "pending_tasks": pending_tasks,
        "upcoming_deadlines": upcoming_deadlines,
        "recent_matters": [dict(r) for r in recent_matters],
        "overdue_tasks": [dict(r) for r in overdue_tasks],
    }
