import secrets
from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from redis.exceptions import RedisError

from .config import settings
from .db import connection
from .events import Event, accept_event, excluded_ids
from .feed import read_feed
from .jobs import enqueue
from .measurement import metrics

app = FastAPI(title="SNS Recommend", version="0.1.0")


def authenticate(x_internal_token: Annotated[str, Header()] = ""):
    if not secrets.compare_digest(x_internal_token, settings().internal_token):
        raise HTTPException(401, "invalid internal token")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/internal/feeds/{user_id}", dependencies=[Depends(authenticate)])
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


@app.post("/internal/events", dependencies=[Depends(authenticate)])
def events(event: Event):
    try:
        return accept_event(event)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/internal/metrics", dependencies=[Depends(authenticate)])
def measurements():
    return metrics()
