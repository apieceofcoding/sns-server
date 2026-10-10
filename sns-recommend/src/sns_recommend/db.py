from contextlib import contextmanager
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from .config import settings


@contextmanager
def connection():
    with psycopg.connect(settings().database_url, row_factory=dict_row) as conn:
        yield conn


def initialize():
    root = Path(__file__).resolve().parents[2]
    with connection() as conn:
        for path in sorted((root / "sql").glob("*.sql")):
            conn.execute(path.read_text())
