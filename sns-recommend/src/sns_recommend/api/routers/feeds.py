import psycopg
from fastapi import APIRouter, HTTPException, Query
from redis.exceptions import RedisError

from sns_recommend.data.events import excluded_ids
from sns_recommend.storage.feeds import read_feed
from sns_recommend.storage.jobs import enqueue
from sns_recommend.storage.postgres import connection

router = APIRouter(prefix="/feeds", tags=["feeds"])


@router.get("/{user_id}")
def feed(user_id: int, limit: int = Query(20, ge=1, le=50), cursor: str | None = None):
    try:
        with connection() as conn:
            excluded = excluded_ids(conn, user_id)
        result = read_feed(user_id, limit, cursor, excluded)
        with connection() as conn:
            user = conn.execute(
                "UPDATE users SET active_at=now() WHERE id=%s RETURNING id", (user_id,)
            ).fetchone()
            if not user:
                raise HTTPException(404, "unknown user")
            if not result["ready"] or result.get("stale") or not result["next_cursor"]:
                result["refresh_job"] = enqueue(conn, "build", user_id=user_id, throttle=True)
        return result
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(410, str(exc)) from exc
    except (RedisError, psycopg.Error) as exc:
        raise HTTPException(503, "feed unavailable; SNS should serve latest") from exc
