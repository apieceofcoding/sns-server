from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal, Self
from uuid import UUID

from psycopg.types.json import Jsonb
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from sns_recommend.core.types import DatabaseConnection, EventResult
from sns_recommend.storage import source
from sns_recommend.storage.jobs import enqueue
from sns_recommend.storage.postgres import connection


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
    # Post events carry the ID and version only. The body stays in the SNS database.
    version: int = Field(default=1, ge=1, le=2**63 - 1, strict=True)

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        if self.kind.startswith("post."):
            if self.post_id is None:
                raise ValueError("post_id required")
        elif self.user_id is None:
            raise ValueError("user_id required")
        if self.kind in {"impression", "click", "like", "not_interested"} and self.post_id is None:
            raise ValueError("post_id required")
        return self


def accept_event(event: Event) -> EventResult:
    if event.user_id is not None and not source.user_exists(event.user_id):
        raise LookupError("unknown user")
    with connection() as conn:
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
            # Skip only while work for this or a newer version is alive. A failed job never blocks.
            covered = conn.execute(
                """SELECT 1 FROM jobs WHERE kind='index' AND post_id=%s AND status<>'failed'
                AND (payload->>'version')::bigint>=%s LIMIT 1""",
                (event.post_id, event.version),
            ).fetchone()
            if not covered:
                # The worker reads the current post from the SNS database, then stores its vector.
                enqueue(conn, "index", post_id=event.post_id, payload={"version": event.version})
        elif event.kind in {"impression", "not_interested"}:
            conn.execute(
                """INSERT INTO exclusions VALUES (%s,%s,%s)
                ON CONFLICT(user_id,post_id) DO UPDATE SET reason=EXCLUDED.reason""",
                (event.user_id, event.post_id, event.kind),
            )
        elif event.kind in {"like", "click", "profile.updated"}:
            enqueue(conn, "profile", user_id=event.user_id)  # Refresh the user vector.
        else:
            raise ValueError("unsupported event kind")  # A new kind must be handled explicitly.
        return {"accepted": True, "duplicate": False}


def excluded_ids(conn: DatabaseConnection, user_id: int) -> set[int]:
    rows = conn.execute("SELECT post_id FROM exclusions WHERE user_id=%s", (user_id,)).fetchall()
    return {r["post_id"] for r in rows}
