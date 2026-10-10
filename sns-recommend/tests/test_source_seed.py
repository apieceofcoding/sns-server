"""Run with COURSE_DB_TESTS=1 after both course databases have started."""

import os

import pytest

from sns_recommend.db import connection, initialize, source_connection
from sns_recommend.seed import seed


@pytest.mark.integration
@pytest.mark.skipif(os.getenv("COURSE_DB_TESTS") != "1", reason="requires course databases")
def test_seed_uses_app_schema_and_keeps_originals_out_of_vector_db():
    initialize()
    seed()
    with source_connection() as conn:
        users = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        posts = conn.execute("SELECT * FROM posts ORDER BY id").fetchall()
        interests = conn.execute("SELECT * FROM user_interests ORDER BY user_id").fetchall()
        assert len(users) == 3
        assert len(posts) == 200
        assert len(interests) == 3
        assert len({post["content"] for post in posts}) == 200
        assert {post["user_id"] for post in posts} == {user["id"] for user in users}
        for table in ("users", "posts"):
            sequence = conn.execute(
                "SELECT pg_get_serial_sequence(%s, 'id') AS name", (table,)
            ).fetchone()["name"]
            from psycopg import sql

            value = conn.execute(
                sql.SQL("SELECT last_value FROM {}").format(sql.Identifier(*sequence.split(".")))
            ).fetchone()["last_value"]
            assert value >= max(row["id"] for row in (users if table == "users" else posts))
    seed()
    with source_connection() as conn:
        assert conn.execute("SELECT * FROM users ORDER BY id").fetchall() == users
        assert conn.execute("SELECT * FROM posts ORDER BY id").fetchall() == posts
        assert conn.execute("SELECT * FROM user_interests ORDER BY user_id").fetchall() == interests
    with connection() as conn:
        assert conn.execute("SELECT to_regclass('public.users') AS name").fetchone()["name"] is None
        assert conn.execute("SELECT to_regclass('public.posts') AS name").fetchone()["name"] is None
        assert (
            conn.execute("SELECT extname FROM pg_extension WHERE extname='vector'").fetchone()
            is not None
        )
