from sns_recommend.core.config import settings
from sns_recommend.storage.jobs import enqueue
from sns_recommend.storage.postgres import connection


def schedule_active():
    with connection() as conn:
        users = conn.execute(
            """SELECT u.id FROM users u WHERE active_at>now()-interval '30 minutes'
            AND NOT EXISTS (SELECT 1 FROM jobs j WHERE j.user_id=u.id AND j.kind='build'
            AND j.created_at>now()-make_interval(secs=>%s))""",
            (settings().refresh_seconds,),
        ).fetchall()
        ids = [enqueue(conn, "build", user_id=u["id"], throttle=True) for u in users]
    return {"scheduled": len([i for i in ids if i])}
