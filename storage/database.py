"""
database.py
تخزين محلي بسيط بـ SQLite لنتائج الـ CBC.
"""
import sqlite3
from contextlib import contextmanager

DB_PATH = "storage/cbc_results.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id TEXT,
                wbc REAL, rbc REAL, hgb REAL, hct REAL,
                mcv REAL, mch REAL, mchc REAL, plt REAL, rdw REAL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_result(result):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO results
               (sample_id, wbc, rbc, hgb, hct, mcv, mch, mchc, plt, rdw)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result.sample_id, result.wbc, result.rbc, result.hgb,
                result.hct, result.mcv, result.mch, result.mchc,
                result.plt, result.rdw,
            ),
        )
