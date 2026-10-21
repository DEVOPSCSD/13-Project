"""SQLite connection handling, schema creation and demo data."""
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    TEXT    NOT NULL UNIQUE,
    full_name     TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    course        TEXT    NOT NULL,
    year_of_study INTEGER NOT NULL CHECK (year_of_study BETWEEN 1 AND 6),
    phone         TEXT,
    created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

DEMO_STUDENTS = [
    ("CS2024001", "Aarav Sharma", "aarav.sharma@example.com", "Computer Science", 2, "9876543210"),
    ("CS2024002", "Priya Reddy", "priya.reddy@example.com", "Computer Science", 3, "9123456780"),
    ("EC2024001", "Rohan Verma", "rohan.verma@example.com", "Electronics", 1, "9988776655"),
    ("ME2024001", "Sneha Iyer", "sneha.iyer@example.com", "Mechanical Engineering", 4, ""),
    ("IT2024001", "Kiran Patel", "kiran.patel@example.com", "Information Technology", 2, "9012345678"),
]


def get_db():
    """Return one SQLite connection per request (stored in flask.g)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the database folder and table, and seed demo data if empty."""
    Path(current_app.config["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()
    if current_app.config.get("SEED_DEMO_DATA"):
        if db.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO students (student_id, full_name, email, course, year_of_study, phone) "
                "VALUES (?, ?, ?, ?, ?, ?)", DEMO_STUDENTS)
            db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
