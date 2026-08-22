"""
database.py — Step 8 in the workflow: Save to Database.

SQLite layer for two things now:
  1. Users (signup/signin) — id, name, email, hashed password
  2. Each resume analysis, tied to the user who ran it, so dashboard/
     history/reports are personal instead of one shared list.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "resumelens.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    # The SQLite file lives in this folder. Creating it here keeps a new
    # Render deployment from failing if the database directory is not present.
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            resume_filename TEXT NOT NULL,
            match_score REAL NOT NULL,
            skill_match_score REAL,
            matched_skills TEXT,
            missing_skills TEXT,
            suggestions TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------- Users

def create_user(full_name: str, email: str, password_hash: str) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO users (full_name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (full_name, email.lower().strip(), password_hash, datetime.utcnow().isoformat()),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_user_by_email(email: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------------------------------------------- Analyses

def save_analysis(result: dict, user_id: int = None) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO analysis_history
            (user_id, resume_filename, match_score, skill_match_score, matched_skills,
             missing_skills, suggestions, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            result["resume_filename"],
            result["match_score"],
            result.get("skill_match_score"),
            json.dumps(result["matched_skills"]),
            json.dumps(result["missing_skills"]),
            json.dumps(result["suggestions"]),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def _parse_entry(row) -> dict:
    entry = dict(row)
    entry["matched_skills"] = json.loads(entry["matched_skills"] or "[]")
    entry["missing_skills"] = json.loads(entry["missing_skills"] or "[]")
    entry["suggestions"] = json.loads(entry["suggestions"] or "[]")
    return entry


def get_analysis_by_id(analysis_id: int, user_id: int = None):
    """
    Fetch a single analysis by id. If user_id is given, only returns it
    when it actually belongs to that user (so people can't download or
    view each other's reports by guessing an id).
    """
    conn = get_connection()
    if user_id is not None:
        row = conn.execute(
            "SELECT * FROM analysis_history WHERE id = ? AND user_id = ?",
            (analysis_id, user_id),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM analysis_history WHERE id = ?", (analysis_id,)
        ).fetchone()
    conn.close()

    return _parse_entry(row) if row else None


def get_history(user_id: int, limit: int = 20) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM analysis_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [_parse_entry(row) for row in rows]


def get_stats(user_id: int) -> dict:
    """Aggregate stats for one user's analyses, for the dashboard summary cards."""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total_count,
            AVG(match_score) AS avg_score,
            MAX(match_score) AS best_score
        FROM analysis_history
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()
    conn.close()

    total_count = row["total_count"] or 0
    avg_score = round(row["avg_score"], 1) if row["avg_score"] is not None else 0
    best_score = round(row["best_score"], 1) if row["best_score"] is not None else 0

    return {
        "total_count": total_count,
        "avg_score": avg_score,
        "best_score": best_score,
    }


def get_score_trend(user_id: int, limit: int = 8) -> list:
    """
    Return the user's last few scores in oldest-to-newest order, so the
    dashboard chart can show whether their scores are improving over time.
    """
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT match_score, created_at FROM analysis_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    conn.close()

    # rows come back newest-first; reverse so the chart reads left-to-right in time order
    rows = list(reversed(rows))

    return [
        {"date": row["created_at"][:10], "score": row["match_score"]}
        for row in rows
    ]


def get_top_missing_skills(user_id: int, limit: int = 5) -> list:
    """
    Look across every one of the user's past analyses and find which
    missing skills come up most often — a simple "what to learn next" list.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT missing_skills FROM analysis_history WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    conn.close()

    # Count how many times each skill shows up across all analyses
    skill_counts = {}
    for row in rows:
        skills = json.loads(row["missing_skills"] or "[]")
        for skill in skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

    # Sort by how often it appeared, most common first
    sorted_skills = sorted(skill_counts.items(), key=lambda pair: pair[1], reverse=True)
    return [{"skill": skill, "count": count} for skill, count in sorted_skills[:limit]]


def update_user_name(user_id: int, full_name: str):
    conn = get_connection()
    conn.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name, user_id))
    conn.commit()
    conn.close()


def update_user_password(user_id: int, new_password_hash: str):
    conn = get_connection()
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
    conn.commit()
    conn.close()
