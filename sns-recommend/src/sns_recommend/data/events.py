from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from psycopg.types.json import Jsonb
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from sns_recommend.storage.jobs import enqueue
from sns_recommend.storage.postgres import connection


class PostContent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    body: str = Field(min_length=1, max_length=10_000, strict=True)
    author_id: int = Field(gt=0, le=2**63 - 1, strict=True)
    topic: str = Field(min_length=1, max_length=100, strict=True)


class ProfileContent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    interests: str = Field(min_length=1, max_length=1_000, strict=True)


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: UUID
    kind: Literal[
        "post.updated",
        "post.deleted",
        "impression",
        "click",
        "like",
        "not_interested",
        "profile.updated",
    ]
    occurred_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))
    user_id: int | None = Field(default=None, gt=0, le=2**63 - 1, strict=True)
    post_id: int | None = Field(default=None, gt=0, le=2**63 - 1, strict=True)
    version: int = Field(default=1, ge=1, le=2**63 - 1, strict=True)
    payload: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_fields(self):
        if self.kind.startswith("post."):
            if self.post_id is None:
                raise ValueError("post_id required")
        elif self.user_id is None:
            raise ValueError("user_id required")
        if self.kind in {"impression", "click", "like", "not_interested"} and self.post_id is None:
            raise ValueError("post_id required")
        if self.kind == "post.updated":
            self.payload = PostContent.model_validate(self.payload).model_dump()
        elif self.kind == "profile.updated":
            self.payload = ProfileContent.model_validate(self.payload).model_dump()
        elif self.payload:
            raise ValueError("payload must be empty for this event kind")
        return self


def accept_event(event):
    with connection() as conn:
        if (
            event.user_id
            and not conn.execute("SELECT id FROM users WHERE id=%s", (event.user_id,)).fetchone()
        ):
            raise LookupError("unknown user")
        inserted = conn.execute(
            """INSERT INTO events(event_id,kind,user_id,post_id,
            occurred_at,payload) VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING RETURNING event_id""",
            (
                event.event_id,
                event.kind,
                event.user_id,
                event.post_id,
                event.occurred_at,
                Jsonb(event.model_dump(mode="json")),
            ),
        ).fetchone()
        if not inserted:
            return {"accepted": False, "duplicate": True}
        if event.kind.startswith("post."):
            body = event.payload.get("body", "")
            changed = conn.execute(
                """INSERT INTO posts(id,author_id,body,topic,version,
                created_at,deleted) VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT(id) DO UPDATE SET body=EXCLUDED.body,topic=EXCLUDED.topic,
                author_id=EXCLUDED.author_id,version=EXCLUDED.version,deleted=EXCLUDED.deleted
                WHERE posts.version<EXCLUDED.version RETURNING id""",
                (
                    event.post_id,
                    event.payload.get("author_id", 0),
                    body,
                    event.payload.get("topic", "unknown"),
                    event.version,
                    event.occurred_at,
                    event.kind == "post.deleted",
                ),
            ).fetchone()
            if changed:
                enqueue(conn, "index", post_id=event.post_id, payload={"version": event.version})
        elif event.kind in {"impression", "not_interested"}:
            conn.execute(
                """INSERT INTO exclusions VALUES (%s,%s,%s)
                ON CONFLICT(user_id,post_id) DO UPDATE SET reason=EXCLUDED.reason""",
                (event.user_id, event.post_id, event.kind),
            )
        elif event.kind == "profile.updated":
            conn.execute(
                "UPDATE users SET interests=%s,version=version+1 WHERE id=%s",
                (event.payload["interests"], event.user_id),
            )
            enqueue(conn, "profile", user_id=event.user_id)
        elif event.kind in {"like", "click"}:
            enqueue(conn, "profile", user_id=event.user_id)
        return {"accepted": True, "duplicate": False}


def excluded_ids(conn, user_id):
    rows = conn.execute("SELECT post_id FROM exclusions WHERE user_id=%s", (user_id,)).fetchall()
    deleted = conn.execute("SELECT id FROM posts WHERE deleted").fetchall()
    return {r["post_id"] for r in rows} | {r["id"] for r in deleted}
