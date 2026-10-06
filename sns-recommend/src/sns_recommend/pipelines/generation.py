from sns_recommend.core.config import settings
from sns_recommend.providers.rerank import PROMPT_VERSION, rerank_candidates
from sns_recommend.recommenders.ranking import diversify, validate_ranking
from sns_recommend.recommenders.retrieval import retrieve_candidates, update_profile
from sns_recommend.storage.feeds import publish
from sns_recommend.storage.jobs import allocate_generation
from sns_recommend.storage.postgres import connection


def prepare_inputs(user_id):
    update_profile(user_id)
    candidates = retrieve_candidates(user_id)
    with connection() as conn:
        user = conn.execute(
            "SELECT interests,version FROM users WHERE id=%s", (user_id,)
        ).fetchone()
        history = conn.execute(
            """SELECT kind,post_id FROM events WHERE user_id=%s
            AND occurred_at<=now() AND kind IN ('click','like','not_interested')
            ORDER BY occurred_at DESC LIMIT 10""",
            (user_id,),
        ).fetchall()
    return {
        "user_id": user_id,
        "interests": user["interests"],
        "user_version": user["version"],
        "history": history,
        "candidates": candidates,
        "prompt_version": PROMPT_VERSION,
        "model": settings().rerank_model,
        "mode": settings().model_mode,
    }


def generate(user_id, generation=None, snapshot_id=None, created_at=None):
    inputs = prepare_inputs(user_id)
    candidates = inputs["candidates"]
    strategy = "fixture_llm" if settings().model_mode == "fixture" else "llm"
    try:
        response = rerank_candidates(inputs)
        ordered = validate_ranking(candidates, response["ordered_ids"])
    except Exception:
        ordered, strategy = [p["id"] for p in candidates], "rules_fallback"
    ids = diversify(candidates, ordered)
    if generation is None:
        with connection() as conn:
            generation = allocate_generation(conn, user_id)
    published = publish(user_id, ids, strategy, generation, snapshot_id, created_at)
    return {"strategy": strategy, "post_ids": ids, "published": published}
