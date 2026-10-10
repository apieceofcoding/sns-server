from __future__ import annotations

from sns_recommend.core.config import settings
from sns_recommend.storage.jobs import enqueue
from sns_recommend.storage.postgres import connection


def schedule_active() -> dict[str, int]:
    with connection() as conn:
        users = conn.execute(
            """SELECT u.user_id AS id FROM profiles u
            WHERE active_at>now()-interval '30 minutes'
            AND NOT EXISTS (SELECT 1 FROM jobs j WHERE j.user_id=u.user_id AND j.kind='build'
            AND j.created_at>now()-make_interval(secs=>%s))""",
            (settings().refresh_seconds,),
        ).fetchall()
        ids = [enqueue(conn, "build", user_id=u["id"], throttle=True) for u in users]
    return {"scheduled": len([i for i in ids if i])}
