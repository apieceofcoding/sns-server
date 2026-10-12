from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from .config import settings


@contextmanager
def source_connection():
    with psycopg.connect(settings().source_database_url, row_factory=dict_row,
                         options="-c timezone=UTC", connect_timeout=5) as conn:
        yield conn


def initialize():
    root = Path(__file__).resolve().parents[2]
    with source_connection() as conn:
        app_ddl = root.parent / "sns-app/src/main/resources/ddl.sql"
        if app_ddl.is_file():
            ddl = app_ddl.read_text()
            ddl = ddl.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ")
            ddl = ddl.replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ")
            conn.execute(ddl)
        conn.execute("""CREATE TABLE IF NOT EXISTS user_interests (
            user_id bigint PRIMARY KEY REFERENCES users(id),
            interests text NOT NULL
        )""")
