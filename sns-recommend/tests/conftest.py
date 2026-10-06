import os
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from sns_recommend.core.config import settings
from sns_recommend.data.seed import seed
from sns_recommend.storage.feeds import redis_client
from sns_recommend.storage.postgres import initialize


@pytest.fixture
def infra(monkeypatch):
    if os.environ.get("RUN_INTEGRATION") != "1":
        pytest.skip("set RUN_INTEGRATION=1 for isolated local database tests")
    original = settings()
    options = conninfo_to_dict(original.database_url)
    name = "rec_test_" + uuid4().hex
    admin = make_conninfo(**{**options, "dbname": "postgres"})
    with psycopg.connect(admin, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    monkeypatch.setenv("DATABASE_URL", make_conninfo(**{**options, "dbname": name}))
    monkeypatch.setenv("REDIS_URL", original.redis_url.rsplit("/", 1)[0] + "/15")
    monkeypatch.setenv("MODEL_MODE", "fixture")
    settings.cache_clear()
    r = redis_client()
    try:
        initialize()
        keys = list(r.scan_iter("recommend:*"))
        if keys:
            r.delete(*keys)
        seed()
        yield
    finally:
        try:
            keys = list(r.scan_iter("recommend:*"))
            if keys:
                r.delete(*keys)
        finally:
            settings.cache_clear()
            with psycopg.connect(admin, autocommit=True) as conn:
                conn.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))
