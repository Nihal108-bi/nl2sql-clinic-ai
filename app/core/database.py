"""
app/core/database.py
SQLite connection helper — used by the health check and direct query fallback.
"""

import sqlite3
from contextlib import contextmanager
from app.core.config import settings
from app.core.logger import logger


@contextmanager
def get_connection():
    """Context manager that yields a SQLite connection and auto-closes it."""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    try:
        yield conn
    finally:
        conn.close()


def check_connection() -> bool:
    """Ping the database. Returns True if reachable."""
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def execute_query(sql: str) -> list[dict]:
    """
    Run a SELECT query and return results as a list of dicts.
    Used as a direct fallback when the Vanna agent is unavailable.
    """
    with get_connection() as conn:
        cursor = conn.execute(sql)
        columns = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
