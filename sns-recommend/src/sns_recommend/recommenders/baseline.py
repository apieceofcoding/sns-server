from __future__ import annotations

from sns_recommend.storage.feeds import publish
from sns_recommend.storage.jobs import allocate_generation
from sns_recommend.storage.postgres import connection


def baseline(user_id: int, strategy: str = "latest") -> dict[str, str | int]:
    if strategy not in {"latest", "popular"}:
        raise ValueError("unsupported baseline")
    order = "created_at DESC, id DESC" if strategy == "latest" else "likes DESC, id DESC"
    with connection() as conn:
        posts = conn.execute(f"SELECT id FROM posts WHERE NOT deleted ORDER BY {order}").fetchall()
        generation = allocate_generation(conn, user_id)
        publish(user_id, [p["id"] for p in posts], strategy, generation)
    return {"user_id": user_id, "strategy": strategy, "count": len(posts)}
