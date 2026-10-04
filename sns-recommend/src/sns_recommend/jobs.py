import time
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from psycopg.types.json import Jsonb

from .config import settings
from .db import connection


def allocate_generation(conn, user_id):
    row = conn.execute(
        """UPDATE users SET generation=GREATEST(generation+1,%s)
        WHERE id=%s RETURNING generation""",
        (int(time.time() * 1000000), user_id),
    ).fetchone()
    if not row:
        raise LookupError("unknown user")
    return row["generation"]


def enqueue(conn, kind, user_id=None, post_id=None, payload=None, throttle=False):
    if kind == "build":
        # Serialize enqueue and publish against the same user row.
        conn.execute("SELECT id FROM users WHERE id=%s FOR UPDATE", (user_id,)).fetchone()
        existing = conn.execute(
            """SELECT * FROM jobs WHERE kind='build'
            AND user_id=%s AND status='pending'""",
            (user_id,),
        ).fetchone()
        if existing:
            return str(existing["id"])
        if throttle:
            recent = conn.execute(
                """SELECT id FROM jobs WHERE user_id=%s AND kind='build'
                AND created_at>now()-make_interval(secs=>%s) LIMIT 1""",
                (user_id, settings().minimum_refresh_seconds),
            ).fetchone()
            if recent:
                return None
        generation = allocate_generation(conn, user_id)
    else:
        generation = 0
    job_id = uuid4()
    conn.execute(
        """INSERT INTO jobs(id,kind,user_id,post_id,generation,payload)
        VALUES (%s,%s,%s,%s,%s,%s)""",
        (job_id, kind, user_id, post_id, generation, Jsonb(payload or {})),
    )
    return str(job_id)


def claim(kinds=("index", "profile", "build"), job_id=None):
    owner = uuid4()
    with connection() as conn:
        row = conn.execute(
            """SELECT * FROM jobs WHERE kind=ANY(%s) AND (%s::uuid IS NULL OR id=%s::uuid) AND
            ((status='pending' AND available_at<=now()) OR
             (status='running' AND lease_until<now()))
            ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1""",
            (list(kinds), job_id, job_id),
        ).fetchone()
        if not row:
            return None
        conn.execute(
            """UPDATE jobs SET status='running', owner=%s,
            attempts=attempts+1, lease_until=%s WHERE id=%s""",
            (owner, datetime.now(UTC) + timedelta(seconds=settings().lease_seconds), row["id"]),
        )
        row["owner"] = owner
        row["attempts"] += 1
        return row


def finish(job, status="done", error=None):
    with connection() as conn:
        conn.execute(
            """UPDATE jobs SET status=%s,error=%s,lease_until=NULL
            WHERE id=%s AND owner=%s AND status='running'""",
            (status, error, job["id"], job["owner"]),
        )


def retry(job, error):
    status = "failed" if job["attempts"] >= 3 else "running"
    with connection() as conn:
        conn.execute(
            """UPDATE jobs SET status=%s,error=%s,lease_until=now()+interval '10 seconds'
            WHERE id=%s AND owner=%s AND status='running'""",
            (status, error, job["id"], job["owner"]),
        )
