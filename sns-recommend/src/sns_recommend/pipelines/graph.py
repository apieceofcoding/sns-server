from __future__ import annotations

from datetime import UTC, datetime, timedelta
from time import perf_counter
from typing import Any, Literal, TypedDict, overload

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from sns_recommend.core.config import settings
from sns_recommend.core.measurement import record_generation
from sns_recommend.core.types import GraphResult, Job, PausedResult, RankingInput, RankingResult
from sns_recommend.pipelines.generation import prepare_inputs
from sns_recommend.providers.rerank import ranking_strategy, rerank_candidates
from sns_recommend.recommenders.ranking import diversify, validate_ranking
from sns_recommend.storage.feeds import publish
from sns_recommend.storage.jobs import claim, enqueue, finish
from sns_recommend.storage.postgres import connection

GRAPH_VERSION = "sns-feed-v1"


class FeedState(TypedDict, total=False):
    user_id: int
    job_id: str
    owner: str
    generation: int
    snapshot_id: str
    created_at: float
    graph_version: str
    inputs: RankingInput
    response: RankingResult
    ordered: list[int]
    valid: bool
    strategy: str
    error: str
    published: bool


def guard(state: FeedState) -> None:
    with connection() as conn:
        row = conn.execute(
            """UPDATE jobs SET lease_until=%s WHERE id=%s AND owner=%s
            AND status='running' AND lease_until>now() RETURNING id""",
            (
                datetime.now(UTC) + timedelta(seconds=settings().lease_seconds),
                state["job_id"],
                state["owner"],
            ),
        ).fetchone()
        if not row:
            raise RuntimeError("job lease lost")


def make_graph(
    checkpointer: BaseCheckpointSaver[Any], pause: bool = False
) -> CompiledStateGraph[FeedState, None, FeedState, FeedState]:
    def retrieve(state: FeedState) -> FeedState:
        guard(state)
        result = prepare_inputs(state["user_id"])
        guard(state)
        return {"inputs": result}

    def rerank(state: FeedState) -> FeedState:
        guard(state)
        try:
            result = rerank_candidates(state["inputs"])
            strategy = ranking_strategy(result["mode"])
            answer: FeedState = {"response": result, "strategy": strategy, "error": ""}
        except Exception as exc:
            answer = {
                "response": {"ordered_ids": [], "mode": settings().model_mode, "usage": {}},
                "error": type(exc).__name__,
            }
        guard(state)
        return answer

    def validate(state: FeedState) -> FeedState:
        guard(state)
        try:
            ids = validate_ranking(
                state["inputs"]["candidates"], state["response"].get("ordered_ids")
            )
            return {"ordered": ids, "valid": not bool(state.get("error"))}
        except ValueError:
            return {"valid": False, "error": "InvalidRanking"}

    def fallback(state: FeedState) -> FeedState:
        guard(state)
        return {
            "ordered": [p["id"] for p in state["inputs"]["candidates"]],
            "strategy": "rules_fallback",
        }

    def diversity(state: FeedState) -> FeedState:
        guard(state)
        return {"ordered": diversify(state["inputs"]["candidates"], state["ordered"])}

    def publish_feed(state: FeedState) -> FeedState:
        guard(state)
        with connection() as conn:
            user = conn.execute(
                "SELECT generation FROM users WHERE id=%s FOR UPDATE", (state["user_id"],)
            ).fetchone()
            job = conn.execute(
                "SELECT * FROM jobs WHERE id=%s FOR UPDATE", (state["job_id"],)
            ).fetchone()
            if (
                user is None
                or job is None
                or user["generation"] != state["generation"]
                or str(job["owner"]) != state["owner"]
                or job["status"] != "running"
                or job["lease_until"] <= datetime.now(UTC)
                or datetime.now(UTC).timestamp() - state["created_at"] > settings().snapshot_ttl
            ):
                return {"published": False}
            # Enqueue takes the same user lock, so it cannot invalidate this generation mid-publish.
            published = publish(
                state["user_id"],
                state["ordered"],
                state["strategy"],
                state["generation"],
                state["snapshot_id"],
                state["created_at"],
            )
        return {"published": published}

    builder = StateGraph(FeedState)
    for name, node in [
        ("retrieve", retrieve),
        ("rerank", rerank),
        ("validate", validate),
        ("fallback", fallback),
        ("diversify", diversity),
        ("publish", publish_feed),
    ]:
        builder.add_node(name, node)
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "rerank")
    builder.add_edge("rerank", "validate")
    builder.add_conditional_edges("validate", lambda s: "diversify" if s["valid"] else "fallback")
    builder.add_edge("fallback", "diversify")
    builder.add_edge("diversify", "publish")
    builder.add_edge("publish", END)
    return builder.compile(checkpointer=checkpointer, interrupt_after=["rerank"] if pause else [])


@overload
def run_graph(job: Job, pause: Literal[False] = False) -> GraphResult: ...


@overload
def run_graph(job: Job, pause: bool) -> GraphResult | PausedResult: ...


def run_graph(job: Job, pause: bool = False) -> GraphResult | PausedResult:
    if job["user_id"] is None:
        raise ValueError("build job requires user_id")
    started = perf_counter()
    # Check ownership before changing the checkpoint's owner or saved state.
    guard({"job_id": str(job["id"]), "owner": str(job["owner"])})
    with PostgresSaver.from_conn_string(settings().database_url) as saver:
        saver.setup()
        graph = make_graph(saver, pause)
        config: RunnableConfig = {"configurable": {"thread_id": str(job["id"])}}
        saved = graph.get_state(config)
        if saved.values:
            if saved.values["graph_version"] != GRAPH_VERSION:
                raise ValueError("unsupported graph version")
            # Lease owner changes after process restart. Persist the new owner before resuming.
            graph.update_state(config, {"owner": str(job["owner"])}, as_node=None)
            result = graph.invoke(None, config)
        else:
            result = graph.invoke(
                {
                    "user_id": job["user_id"],
                    "job_id": str(job["id"]),
                    "owner": str(job["owner"]),
                    "generation": job["generation"],
                    "snapshot_id": str(job["id"]),
                    "created_at": job["created_at"].timestamp(),
                    "graph_version": GRAPH_VERSION,
                },
                config,
            )
        if graph.get_state(config).next:
            with connection() as conn:
                conn.execute(
                    """UPDATE jobs SET lease_until=now() WHERE id=%s AND owner=%s
                    AND status='running'""",
                    (job["id"], job["owner"]),
                )
            return {"paused": True, "job_id": str(job["id"]), "next": "validate"}
    finish(job, "done" if result.get("published") else "superseded")
    record_generation(job["id"], (perf_counter() - started) * 1000, result)
    return {
        "job_id": str(job["id"]),
        "strategy": result["strategy"],
        "post_ids": result["ordered"],
        "published": result.get("published", False),
    }


@overload
def start_graph(user_id: int, pause: Literal[False] = False) -> GraphResult: ...


@overload
def start_graph(user_id: int, pause: bool) -> GraphResult | PausedResult: ...


def start_graph(user_id: int, pause: bool = False) -> GraphResult | PausedResult:
    with connection() as conn:
        job_id = enqueue(conn, "build", user_id=user_id)
    job = claim(("build",), job_id=job_id)
    if job is None:
        raise RuntimeError("job already owned by a worker")
    return run_graph(job, pause)
