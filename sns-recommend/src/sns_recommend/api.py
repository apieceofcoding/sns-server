import secrets
from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from redis.exceptions import RedisError
from .config import settings
from .feed import read_feed

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
        return read_feed(user_id, limit, cursor)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(410, str(exc)) from exc
    except RedisError as exc:
        raise HTTPException(503, "feed unavailable; SNS should serve latest") from exc
