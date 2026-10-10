"""Reads from the SNS database. Posts and accounts stay there and are never copied."""
from .db import source_connection

# A feed candidate is an original post: not deleted, not a reply and not a repost.
VISIBLE = "deleted_at IS NULL AND parent_id IS NULL AND repost_id IS NULL"


def ordered_post_ids(strategy):
    order = {"latest": "created_at DESC,id DESC", "popular": "like_count DESC,id DESC"}[strategy]
    with source_connection() as conn:
        rows = conn.execute(f"SELECT id FROM posts WHERE {VISIBLE} ORDER BY {order}").fetchall()
    return [row["id"] for row in rows]


def user_exists(user_id):
    with source_connection() as conn:
        return conn.execute("SELECT id FROM users WHERE id=%s AND deleted_at IS NULL",
                            (user_id,)).fetchone() is not None


def alive_ids(post_ids):
    with source_connection() as conn:
        rows = conn.execute("SELECT id FROM posts WHERE id=ANY(%s) AND deleted_at IS NULL",
                            (post_ids,)).fetchall()
    return {row["id"] for row in rows}
