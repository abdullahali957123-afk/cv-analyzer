"""Local SQLite storage. Data stays in instance/app.db on this computer."""
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

PROFILE_FIELDS = ("name", "email", "phone", "skills", "education", "experience", "projects", "certifications")


def _path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.environ.get("CV_DB_PATH") or os.path.join(base, "instance", "app.db")


def _conn():
    p = _path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    return conn


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def init_db():
    with closing(_conn()) as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY CHECK (id = 1), data TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, score INTEGER, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS saved_jobs (job_id TEXT PRIMARY KEY, saved_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        c.commit()


def save_profile(data):
    clean = {k: str(data.get(k) or "")[:5000] for k in PROFILE_FIELDS}
    with closing(_conn()) as c:
        c.execute("INSERT OR REPLACE INTO profile (id, data, updated_at) VALUES (1, ?, ?)", (json.dumps(clean), _now()))
        c.commit()


def get_profile():
    with closing(_conn()) as c:
        row = c.execute("SELECT data, updated_at FROM profile WHERE id = 1").fetchone()
    if row is None:
        return None
    return {"data": json.loads(row["data"]), "updated_at": row["updated_at"]}


def add_history(kind, score):
    with closing(_conn()) as c:
        c.execute("INSERT INTO history (kind, score, created_at) VALUES (?, ?, ?)", (kind, score, _now()))
        c.commit()


def list_history(limit=20):
    with closing(_conn()) as c:
        rows = c.execute("SELECT kind, score, created_at FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def save_job(job_id):
    with closing(_conn()) as c:
        c.execute("INSERT OR REPLACE INTO saved_jobs (job_id, saved_at) VALUES (?, ?)", (job_id, _now()))
        c.commit()


def remove_job(job_id):
    with closing(_conn()) as c:
        c.execute("DELETE FROM saved_jobs WHERE job_id = ?", (job_id,))
        c.commit()


def list_saved_jobs():
    with closing(_conn()) as c:
        rows = c.execute("SELECT job_id, saved_at FROM saved_jobs ORDER BY saved_at DESC").fetchall()
    return [dict(r) for r in rows]


def get_setting(key, default="0"):
    with closing(_conn()) as c:
        row = c.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(key, value):
    with closing(_conn()) as c:
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        c.commit()


def delete_all():
    with closing(_conn()) as c:
        for t in ("profile", "history", "saved_jobs", "settings"):
            c.execute("DELETE FROM %s" % t)
        c.commit()
