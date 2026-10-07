from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from sns_recommend.core.config import settings
from sns_recommend.core.resources import resource_directory
from sns_recommend.core.types import DatabaseConnection


@contextmanager
def connection() -> Iterator[DatabaseConnection]:
    with psycopg.connect(settings().database_url, row_factory=dict_row) as conn:
        yield conn


def initialize() -> None:
    with connection() as conn:
        for path in sorted(resource_directory("sql").iterdir(), key=lambda entry: entry.name):
            if not path.name.endswith(".sql"):
                continue
            conn.execute(path.read_text())
