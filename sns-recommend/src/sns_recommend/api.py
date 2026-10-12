from fastapi import FastAPI, HTTPException, Query
from redis.exceptions import RedisError

from .feed import read_feed

app = FastAPI(title="SNS Recommend", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/internal/feeds/{user_id}")
def feed(user_id: int, limit: int = Query(20, ge=1, le=50), cursor: str | None = None):
    try:
        return read_feed(user_id, limit, cursor)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(410, str(exc)) from exc
    except RedisError as exc:
        raise HTTPException(503, "feed unavailable; SNS should serve latest") from exc
