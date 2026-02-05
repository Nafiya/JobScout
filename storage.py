import sqlite3
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DB_PATH = "jobs.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            url TEXT,
            score REAL,
            notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def is_seen(conn: sqlite3.Connection, job_id: str) -> bool:
    cursor = conn.execute("SELECT 1 FROM seen_jobs WHERE job_id = ?", (job_id,))
    return cursor.fetchone() is not None


def mark_seen(conn: sqlite3.Connection, job_id: str, title: str, company: str, url: str, score: float):
    conn.execute(
        "INSERT OR IGNORE INTO seen_jobs (job_id, title, company, url, score) VALUES (?, ?, ?, ?, ?)",
        (job_id, title, company, url, score),
    )
    conn.commit()
    logger.info(f"Stored job: {title} at {company} (score: {score:.1f}%)")


def cleanup_old(conn: sqlite3.Connection, days: int = 30):
    cutoff = datetime.now() - timedelta(days=days)
    conn.execute("DELETE FROM seen_jobs WHERE notified_at < ?", (cutoff,))
    conn.commit()
    logger.debug(f"Cleaned up jobs older than {days} days")
