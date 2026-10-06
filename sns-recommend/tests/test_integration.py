import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.postgres import PostgresSaver

from sns_recommend.api import app
from sns_recommend.core.config import settings
from sns_recommend.core.measurement import CallLimitExceeded, measured_call
from sns_recommend.data.events import Event, accept_event
from sns_recommend.data.indexing import index_posts
from sns_recommend.pipelines.graph import make_graph, run_graph, start_graph
from sns_recommend.providers.embeddings import (
    CachedEmbeddings,
    FixtureEmbeddings,
    normalize,
    space,
    vector_sql,
)
from sns_recommend.recommenders.retrieval import retrieve_candidates, update_profile
from sns_recommend.storage.feeds import publish, read_feed
from sns_recommend.storage.jobs import claim, enqueue, finish, retry
from sns_recommend.storage.postgres import connection

pytestmark = pytest.mark.integration


def prepare():
    index_posts()
    update_profile(1)


def test_event_duplicate_and_old_version_are_not_reapplied(infra):
    event = Event(
        event_id=uuid4(),
        kind="post.updated",
        post_id=1,
        version=3,
        payload={"body": "Python updated", "author_id": 10, "topic": "backend"},
    )
    assert accept_event(event)["accepted"]
    assert accept_event(event)["duplicate"]
    accept_event(event.model_copy(update={"event_id": uuid4(), "version": 2}))
    with connection() as conn:
        assert conn.execute("SELECT version FROM posts WHERE id=1").fetchone()["version"] == 3
        assert conn.execute("SELECT count(*) AS n FROM jobs").fetchone()["n"] == 1


def test_source_outbox_commits_with_post(infra):
    from sns_recommend.data.source_demo import change_post

    change_post(1001, "Python")
    with connection() as conn:
        assert conn.execute("SELECT count(*) AS n FROM source_demo.posts").fetchone()["n"] == 1
        assert conn.execute("SELECT count(*) AS n FROM source_demo.outbox").fetchone()["n"] == 1


def test_exclusions_delete_and_stale_vectors(infra):
    prepare()
    accept_event(Event(event_id=uuid4(), kind="impression", user_id=1, post_id=200))
    accept_event(Event(event_id=uuid4(), kind="post.deleted", post_id=195, version=2))
    with connection() as conn:
        conn.execute("UPDATE posts SET version=2 WHERE id=190")
    ids = [p["id"] for p in retrieve_candidates(1)]
    assert 200 not in ids and 195 not in ids
    stale = next((p for p in retrieve_candidates(1) if p["id"] == 190), None)
    assert stale is None or stale["similarity"] is None


def test_old_snapshot_stays_stable_and_publish_is_idempotent(infra):
    assert publish(1, [1, 2, 3, 4], "test", 1, "old", 123.0)
    page = read_feed(1, 2)
    assert publish(1, [4, 3, 2, 1], "test", 2, "new", 124.0)
    assert read_feed(1, 2, page["next_cursor"])["post_ids"] == [3, 4]
    assert publish(1, [4, 3, 2, 1], "test", 2, "new", 124.0)
    assert not publish(1, [1], "test", 1, "stale", 125.0)
    with pytest.raises(ValueError):
        publish(1, [99], "test", 2, "new", 124.0)


def test_graph_resumes_without_repeating_saved_rerank(infra, monkeypatch):
    prepare()
    import sns_recommend.pipelines.graph as graph_module

    calls = []
    original = graph_module.rerank_candidates

    def count(inputs):
        calls.append(1)
        return original(inputs)

    monkeypatch.setattr(graph_module, "rerank_candidates", count)
    paused = start_graph(1, pause=True)
    assert paused["next"] == "validate"
    job = claim(("build",), job_id=paused["job_id"])
    result = run_graph(job)
    assert result["published"]
    assert len(calls) == 1
    assert read_feed(1)["snapshot_id"] == paused["job_id"]


def test_invalid_rank_uses_rule_branch(infra, monkeypatch):
    prepare()
    monkeypatch.setattr(
        "sns_recommend.pipelines.graph.rerank_candidates",
        lambda inputs: {"ordered_ids": [99999], "mode": "fixture"},
    )
    result = start_graph(1)
    assert result["strategy"] == "rules_fallback"
    assert result["published"]
    assert 99999 not in result["post_ids"]


def test_new_generation_fences_old_graph(infra):
    prepare()
    old = start_graph(1, pause=True)
    with connection() as conn:
        enqueue(conn, "build", user_id=1)
    resumed = claim(("build",), job_id=old["job_id"])
    assert not run_graph(resumed)["published"]
    assert not read_feed(1)["ready"]


def test_read_api_does_not_call_model(infra, monkeypatch):
    publish(1, [1, 2, 3], "latest", 1)

    def forbidden(*args):
        raise AssertionError("read path called model")

    monkeypatch.setattr("sns_recommend.pipelines.graph.rerank_candidates", forbidden)
    result = TestClient(app).get(
        "/internal/feeds/1", headers={"X-Internal-Token": "course-local-token"}
    )
    assert result.status_code == 200
    assert result.json()["post_ids"] == [1, 2, 3]


def test_budget_is_enforced_before_provider_call(infra, monkeypatch):
    monkeypatch.setenv("DAILY_CALL_LIMIT", "1")
    from sns_recommend.core.config import settings

    settings.cache_clear()
    calls = []
    measured_call("rerank", "fake", lambda: calls.append(1))
    with pytest.raises(CallLimitExceeded):
        measured_call("rerank", "fake", lambda: calls.append(1))
    assert len(calls) == 1


def test_lease_ownership_blocks_late_worker(infra):
    prepare()
    with connection() as conn:
        job_id = enqueue(conn, "build", user_id=1)
    old = claim(("build",), job_id=job_id)
    with connection() as conn:
        conn.execute("UPDATE jobs SET owner=%s WHERE id=%s", (uuid4(), job_id))
    with pytest.raises(RuntimeError, match="lease lost"):
        run_graph(old)


def test_lost_owner_cannot_change_saved_checkpoint(infra):
    prepare()
    with connection() as conn:
        job_id = enqueue(conn, "build", user_id=1)
    old = claim(("build",), job_id=job_id)
    assert run_graph(old, pause=True)["paused"]
    current = claim(("build",), job_id=job_id)
    config = {"configurable": {"thread_id": job_id}}
    with PostgresSaver.from_conn_string(settings().database_url) as saver:
        graph = make_graph(saver)
        before = graph.get_state(config)
        with pytest.raises(RuntimeError, match="lease lost"):
            run_graph(old)
        after = graph.get_state(config)
        assert before.config == after.config
        assert before.values == after.values
    assert run_graph(current)["published"]


def test_crashed_jobs_stop_after_retry_limit(infra):
    with connection() as conn:
        job_id = enqueue(conn, "index", post_id=1)
    for attempt in range(1, 4):
        assert claim(("index",), job_id=job_id)["attempts"] == attempt
        with connection() as conn:
            conn.execute(
                "UPDATE jobs SET lease_until=now()-interval '1 second' WHERE id=%s", (job_id,)
            )
    assert claim(("index",), job_id=job_id) is None
    with connection() as conn:
        row = conn.execute("SELECT status,attempts FROM jobs WHERE id=%s", (job_id,)).fetchone()
    assert row == {"status": "failed", "attempts": 3}


def test_retry_does_not_reopen_finished_job(infra):
    with connection() as conn:
        job_id = enqueue(conn, "index", post_id=1)
    job = claim(("index",), job_id=job_id)
    finish(job)
    retry(job, "metrics unavailable")
    with connection() as conn:
        assert (
            conn.execute("SELECT status FROM jobs WHERE id=%s", (job_id,)).fetchone()["status"]
            == "done"
        )


def test_embedding_record_replays_full_request_from_cold_cache(infra, monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_MODE", "record")
    monkeypatch.setenv("RECORDINGS_DIR", str(tmp_path))
    settings.cache_clear()
    calls = []

    def simulated_provider(self, texts):
        calls.append(texts)
        return FixtureEmbeddings().embed_documents(texts)

    # Synthetic provider data only. This test does not call or record Gemini.
    monkeypatch.setattr(CachedEmbeddings, "_embed_missing", simulated_provider)
    embedding = CachedEmbeddings()
    embedding.embed_documents(["Python"])
    texts = ["Python", "제주 여행", "제주 여행"]
    recorded = embedding.embed_documents(texts)
    assert calls == [["Python"], ["제주 여행"]]
    with connection() as conn:
        conn.execute("DELETE FROM embedding_cache")
    monkeypatch.setenv("MODEL_MODE", "replay")
    settings.cache_clear()
    replayed = embedding.embed_documents(texts)
    for actual, expected in zip(replayed, recorded, strict=True):
        assert actual == pytest.approx(expected)
    assert len(calls) == 2
    # A warm cache must not conceal a missing recording.
    for path in tmp_path.iterdir():
        path.unlink()
    with pytest.raises(FileNotFoundError):
        embedding.embed_documents(texts)


def test_profile_uses_recent_actions_instead_of_largest_post_ids(infra):
    now = datetime.now(UTC)
    recent = [1.0] + [0.0] * 767
    old = [0.0, 1.0] + [0.0] * 766
    with connection() as conn:
        for i in range(7):
            conn.execute(
                """UPDATE posts SET embedding=%s::vector,embedding_space=%s,embedding_version=version
                WHERE id=%s""",
                (vector_sql(recent if i < 5 else old), space(), i + 1),
            )
            accept_event(
                Event(
                    event_id=uuid4(),
                    kind="like",
                    user_id=1,
                    post_id=i + 1,
                    occurred_at=now - timedelta(minutes=i + 1),
                )
            )
    update_profile(1)
    with connection() as conn:
        row = conn.execute("SELECT interests,embedding::text FROM users WHERE id=1").fetchone()
    base = FixtureEmbeddings().embed_query(row["interests"])
    expected = normalize([0.7 * x + 0.3 * y for x, y in zip(base, recent, strict=True)])
    assert json.loads(row["embedding"]) == pytest.approx(expected, abs=1e-7)


def test_stale_user_vector_is_not_used_for_similarity(infra):
    prepare()
    with connection() as conn:
        conn.execute("UPDATE users SET version=version+1 WHERE id=1")
    candidates = retrieve_candidates(1)
    assert candidates
    assert all(p["similarity"] is None and "embedding" not in p["sources"] for p in candidates)


def test_candidate_merge_keeps_fresh_and_popular_posts(infra):
    prepare()
    with connection() as conn:
        for post_id, likes in [(1001, 0), (1002, 1_000_000)]:
            conn.execute(
                """INSERT INTO posts(id,author_id,body,topic,created_at,likes)
                VALUES (%s,10,'unindexed','new',now(),%s)""",
                (post_id, likes),
            )
    candidates = retrieve_candidates(1)
    assert len(candidates) == 30
    by_id = {p["id"]: p for p in candidates}
    assert "latest" in by_id[1001]["sources"]
    assert "popular" in by_id[1002]["sources"]


def test_function_generation_rejects_superseded_result_and_labels_replay(infra, monkeypatch):
    from sns_recommend.pipelines.generation import generate

    candidate = {"id": 1, "author_id": 10, "topic": "backend"}
    monkeypatch.setattr(
        "sns_recommend.pipelines.generation.prepare_inputs",
        lambda user_id: {"candidates": [candidate]},
    )

    def supersede(inputs):
        with connection() as conn:
            enqueue(conn, "build", user_id=1)
        return {"ordered_ids": [1], "mode": "replay"}

    monkeypatch.setattr("sns_recommend.pipelines.generation.rerank_candidates", supersede)
    result = generate(1)
    assert result["strategy"] == "replay_llm"
    assert not result["published"]
    assert not read_feed(1)["ready"]
