from .db import source_connection

VISIBLE = "deleted_at IS NULL AND parent_id IS NULL AND repost_id IS NULL"


def ordered_post_ids(strategy):
    order = {"latest": "created_at DESC,id DESC", "popular": "like_count DESC,id DESC"}[strategy]
    with source_connection() as conn:
        rows = conn.execute(f"SELECT id FROM posts WHERE {VISIBLE} ORDER BY {order}").fetchall()
    return [row["id"] for row in rows]
