import sqlite3
from pathlib import Path


DB_PATH = Path("jobs.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    try:
        # ----------------------------------------------------------
        # Jobs
        # ----------------------------------------------------------

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                experience_years REAL,
                salary TEXT,
                source TEXT NOT NULL,
                match_score INTEGER,
                application_status TEXT NOT NULL
            )
            """
        )

        # ----------------------------------------------------------
        # Application attempts / state history
        # ----------------------------------------------------------

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS application_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # ----------------------------------------------------------
        # Helpful index for application history lookups
        # ----------------------------------------------------------

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_application_attempts_job_url
            ON application_attempts(job_url)
            """
        )

        connection.commit()

    finally:
        connection.close()
