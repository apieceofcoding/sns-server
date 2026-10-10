from datetime import datetime, timezone, timedelta
from uuid import uuid4
import time
from psycopg.types.json import Jsonb
from .config import settings
from .db import connection


def allocate_generation(conn, user_id):
    row = conn.execute("""INSERT INTO profiles(user_id,generation) VALUES (%s,%s)
        ON CONFLICT(user_id) DO UPDATE SET
        generation=GREATEST(profiles.generation+1,EXCLUDED.generation) RETURNING generation""",
                       (user_id, int(time.time()*1000000))).fetchone()
    return row["generation"]


def current_generation(conn, user_id):
    # The row lock serializes enqueue and publish for the same user.
    conn.execute("INSERT INTO profiles(user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
    return conn.execute("SELECT generation FROM profiles WHERE user_id=%s FOR UPDATE",
                        (user_id,)).fetchone()["generation"]


def enqueue(conn, kind, user_id=None, post_id=None, payload=None):
    if kind == "build":
        current_generation(conn, user_id)
        existing = conn.execute("""SELECT * FROM jobs WHERE kind='build'
            AND user_id=%s AND status='pending'""", (user_id,)).fetchone()
        if existing:
            return str(existing["id"])
        generation = allocate_generation(conn, user_id)
    else:
        generation = 0
    job_id = uuid4()
    conn.execute("""INSERT INTO jobs(id,kind,user_id,post_id,generation,payload)
        VALUES (%s,%s,%s,%s,%s,%s)""",
                 (job_id, kind, user_id, post_id, generation, Jsonb(payload or {})))
    return str(job_id)


def claim(kinds=("index", "profile", "build")):
    owner = uuid4()
    with connection() as conn:
        row = conn.execute("""SELECT * FROM jobs WHERE kind=ANY(%s) AND
            ((status='pending' AND available_at<=now()) OR
             (status='running' AND lease_until<now()))
            ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1""", (list(kinds),)).fetchone()
        if not row:
            return None
        conn.execute("""UPDATE jobs SET status='running', owner=%s,
            attempts=attempts+1, lease_until=%s WHERE id=%s""",
                     (owner, datetime.now(timezone.utc)+timedelta(seconds=settings().lease_seconds),
                      row["id"]))
        row["owner"] = owner
        row["attempts"] += 1
        return row


def finish(job, status="done", error=None):
    with connection() as conn:
        conn.execute("""UPDATE jobs SET status=%s,error=%s,lease_until=NULL
            WHERE id=%s AND owner=%s AND status='running'""",
                     (status, error, job["id"], job["owner"]))
