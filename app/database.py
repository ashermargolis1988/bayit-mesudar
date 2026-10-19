import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "bayit_mesudar.db"


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    finally:
        db.close()


def init_db() -> None:
    with connection() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                assignee TEXT NOT NULL DEFAULT 'כולם',
                due_date TEXT,
                frequency TEXT NOT NULL DEFAULT 'once'
                    CHECK (frequency IN ('once', 'daily', 'weekly')),
                notes TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'done')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            )
            """
        )
        count = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            db.executemany(
                """
                INSERT INTO tasks (title, assignee, due_date, frequency, notes)
                VALUES (?, ?, date('now'), ?, ?)
                """,
                [
                    ("לסדר את המטבח", "כולם", "daily", "איפוס השיש והכיור"),
                    ("להפעיל מכונת כביסה", "אשר", "weekly", "כביסה צבעונית"),
                    ("לעבור על רשימת הקניות", "כולם", "once", "לפני היציאה לסופר"),
                ],
            )


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)

