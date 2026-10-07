"""Transactional Outbox demo. Real SNS uses its own database and authentication."""

from __future__ import annotations

from uuid import uuid4

import httpx
from psycopg.types.json import Jsonb

from sns_recommend.core.config import settings
from sns_recommend.data.events import Event
from sns_recommend.storage.postgres import connection


def change_post(post_id: int, body: str) -> dict[str, str | int]:
    with connection() as conn:
        row = conn.execute(
            """INSERT INTO source_demo.posts VALUES (%s,%s,1)
            ON CONFLICT(id) DO UPDATE SET body=EXCLUDED.body,
            version=source_demo.posts.version+1 RETURNING version""",
            (post_id, body),
        ).fetchone()
        assert row is not None  # INSERT/UPDATE RETURNING always returns a row.
        event = Event(
            event_id=uuid4(),
            kind="post.updated",
            post_id=post_id,
            version=row["version"],
            payload={"body": body, "topic": "backend", "author_id": 10},
        )
        conn.execute(
            "INSERT INTO source_demo.outbox(id,event) VALUES (%s,%s)",
            (event.event_id, Jsonb(event.model_dump(mode="json"))),
        )
    return {"event_id": str(event.event_id), "version": row["version"]}


def relay(url: str = "http://localhost:8001") -> dict[str, int]:
    count = 0
    with connection() as conn:
        rows = conn.execute(
            "SELECT * FROM source_demo.outbox WHERE delivered_at IS NULL"
        ).fetchall()
    for row in rows:
        response = httpx.post(
            url + "/internal/events",
            json=row["event"],
            timeout=5,
            headers={"X-Internal-Token": settings().internal_token.get_secret_value()},
        )
        response.raise_for_status()
        with connection() as conn:
            conn.execute(
                "UPDATE source_demo.outbox SET delivered_at=now() WHERE id=%s", (row["id"],)
            )
        count += 1
    return {"delivered": count}
