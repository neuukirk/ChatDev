"""SQLite-backed daily leaderboard for BEATGRID.

Scores are namespaced by the day number (the same value the daily chart uses),
so each day has its own board. A connection is opened per call, which is fine
for the dev server and keeps things simple.
"""

from __future__ import annotations

import os
import re
import sqlite3
from typing import Dict, List

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "beatgrid.db")


def db_path() -> str:
    return os.environ.get("BEATGRID_DB", DEFAULT_DB)


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day INTEGER NOT NULL,
                date TEXT NOT NULL,
                initials TEXT NOT NULL,
                score INTEGER NOT NULL,
                accuracy INTEGER NOT NULL,
                combo INTEGER NOT NULL,
                grade TEXT NOT NULL,
                created TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_day_score ON scores(day, score DESC)")


def clean_initials(raw: str) -> str:
    letters = re.sub(r"[^A-Za-z]", "", raw or "").upper()
    return (letters[:3] or "AAA")


def add_score(day: int, date: str, initials: str, score: int,
              accuracy: int, combo: int, grade: str) -> Dict:
    initials = clean_initials(initials)
    score = max(0, min(int(score), 9_999_999))
    accuracy = max(0, min(int(accuracy), 100))
    combo = max(0, min(int(combo), 99_999))
    grade = grade if grade in ("S", "A", "B", "C", "D") else "D"
    with _conn() as conn:
        conn.execute(
            "INSERT INTO scores (day, date, initials, score, accuracy, combo, grade)"
            " VALUES (?,?,?,?,?,?,?)",
            (day, date, initials, score, accuracy, combo, grade),
        )
    return {"rank": rank_for(day, score), "players": player_count(day)}


def top_scores(day: int, limit: int = 10) -> List[Dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT initials, score, accuracy, combo, grade FROM scores"
            " WHERE day = ? ORDER BY score DESC, id ASC LIMIT ?",
            (day, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def rank_for(day: int, score: int) -> int:
    with _conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM scores WHERE day = ? AND score > ?",
            (day, score),
        ).fetchone()
    return int(row["c"]) + 1


def player_count(day: int) -> int:
    with _conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM scores WHERE day = ?", (day,)
        ).fetchone()
    return int(row["c"])
