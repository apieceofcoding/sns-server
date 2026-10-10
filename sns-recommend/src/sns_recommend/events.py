from datetime import datetime, timezone
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator
from psycopg.types.json import Jsonb
from . import source
from .db import connection
from .jobs import enqueue


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: UUID
    kind: Literal["post.updated", "post.deleted", "impression", "click", "like",
                  "not_interested", "profile.updated"]
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int | None = Field(default=None, gt=0)
    post_id: int | None = Field(default=None, gt=0)
    # Post events carry the ID and version only. The body stays in the SNS database.
    version: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_fields(self):
        if self.kind.startswith("post."):
            if self.post_id is None:
                raise ValueError("post_id required")
        elif self.user_id is None:
            raise ValueError("user_id required")
        if self.kind in {"impression", "click", "like", "not_interested"} and self.post_id is None:
            raise ValueError("post_id required")
        return self


def accept_event(event):
    if event.user_id is not None and not source.user_exists(event.user_id):
        raise LookupError("unknown user")
    with connection() as conn:
        inserted = conn.execute("""INSERT INTO events(event_id,kind,user_id,post_id,
            occurred_at,payload) VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING RETURNING event_id""",
                                (event.event_id, event.kind, event.user_id, event.post_id,
                                 event.occurred_at, Jsonb(event.model_dump(mode="json")))).fetchone()
        if not inserted:
            return {"accepted": False, "duplicate": True}
        if event.kind.startswith("post."):
            newer = conn.execute("""SELECT 1 FROM events WHERE post_id=%s AND kind LIKE 'post.%%'
                AND event_id<>%s AND (payload->>'version')::bigint>=%s LIMIT 1""",
                                 (event.post_id, event.event_id, event.version)).fetchone()
            if not newer:
                # The worker reads the current post from the SNS database, then stores its vector.
                enqueue(conn, "index", post_id=event.post_id, payload={"version": event.version})
        elif event.kind in {"impression", "not_interested"}:
            conn.execute("""INSERT INTO exclusions VALUES (%s,%s,%s)
                ON CONFLICT(user_id,post_id) DO UPDATE SET reason=EXCLUDED.reason""",
                         (event.user_id, event.post_id, event.kind))
        else:
            # like, click and profile.updated refresh the user vector.
            enqueue(conn, "profile", user_id=event.user_id)
        return {"accepted": True, "duplicate": False}


def excluded_ids(conn, user_id):
    rows = conn.execute("SELECT post_id FROM exclusions WHERE user_id=%s", (user_id,)).fetchall()
    return {r["post_id"] for r in rows}
