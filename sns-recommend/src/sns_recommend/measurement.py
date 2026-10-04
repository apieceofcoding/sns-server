from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from .config import settings
from .db import connection


class CallLimitExceeded(RuntimeError):
    pass


def reserve_call(kind, model):
    day = datetime.now(UTC).date()
    call_id = uuid4()
    with connection() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(91731)")
        count = conn.execute(
            "SELECT count(*) AS n FROM model_calls WHERE day=%s", (day,)
        ).fetchone()["n"]
        if count >= settings().daily_call_limit:
            raise CallLimitExceeded("local daily call budget exhausted")
        conn.execute(
            "INSERT INTO model_calls(id,day,kind,model) VALUES (%s,%s,%s,%s)",
            (call_id, day, kind, model),
        )
    return call_id


def complete_call(call_id, duration_ms, usage=None, error=False):
    usage = usage or {}
    cfg = settings()
    input_tokens, output_tokens = usage.get("input_tokens"), usage.get("output_tokens")
    cost = None
    if (
        input_tokens is not None
        and output_tokens is not None
        and cfg.input_usd_per_million is not None
        and cfg.output_usd_per_million is not None
    ):
        cost = (
            input_tokens * cfg.input_usd_per_million + output_tokens * cfg.output_usd_per_million
        ) / 1_000_000
    with connection() as conn:
        conn.execute(
            """UPDATE model_calls SET status=%s,duration_ms=%s,input_tokens=%s,
            output_tokens=%s,estimated_usd=%s WHERE id=%s""",
            (
                "error" if error else "success",
                duration_ms,
                input_tokens,
                output_tokens,
                cost,
                call_id,
            ),
        )


def measured_call(kind, model, fn):
    call_id = reserve_call(kind, model)
    started = perf_counter()
    try:
        result = fn()
    except Exception:
        complete_call(call_id, (perf_counter() - started) * 1000, error=True)
        raise
    complete_call(
        call_id,
        (perf_counter() - started) * 1000,
        result.get("usage", {}) if isinstance(result, dict) else {},
    )
    return result


def record_generation(job_id, duration_ms, result):
    with connection() as conn:
        conn.execute(
            """INSERT INTO generation_runs(job_id,mode,duration_ms,strategy,published)
            VALUES (%s,%s,%s,%s,%s) ON CONFLICT(job_id) DO UPDATE SET
            duration_ms=EXCLUDED.duration_ms,strategy=EXCLUDED.strategy,
            published=EXCLUDED.published,updated_at=now()""",
            (
                job_id,
                settings().model_mode,
                duration_ms,
                result.get("strategy"),
                result.get("published"),
            ),
        )


def metrics():
    with connection() as conn:
        calls = conn.execute("""SELECT kind,status,count(*) AS calls,sum(input_tokens) AS input_tokens,
            sum(output_tokens) AS output_tokens,sum(estimated_usd) AS estimated_usd
            FROM model_calls GROUP BY kind,status""").fetchall()
        runs = conn.execute(
            "SELECT * FROM generation_runs ORDER BY updated_at DESC LIMIT 20"
        ).fetchall()
    return {
        "model_calls": calls,
        "recent_generations": runs,
        "note": "Missing token/cost values are unknown. Fixture and replay do not make live calls.",
    }
