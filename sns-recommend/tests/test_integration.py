from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from sns_recommend.api import app
from sns_recommend.db import connection
from sns_recommend.events import Event, accept_event
from sns_recommend.feed import publish, read_feed
from sns_recommend.graph import run_graph, start_graph
from sns_recommend.indexing import index_posts
from sns_recommend.jobs import claim, enqueue
from sns_recommend.measurement import CallLimitExceeded, measured_call
from sns_recommend.retrieval import retrieve_candidates, update_profile

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
    from sns_recommend.source_demo import change_post

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
    import sns_recommend.graph as graph_module

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
        "sns_recommend.graph.rerank_candidates",
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

    monkeypatch.setattr("sns_recommend.graph.rerank_candidates", forbidden)
    result = TestClient(app).get(
        "/internal/feeds/1", headers={"X-Internal-Token": "course-local-token"}
    )
    assert result.status_code == 200
    assert result.json()["post_ids"] == [1, 2, 3]


def test_budget_is_enforced_before_provider_call(infra, monkeypatch):
    monkeypatch.setenv("DAILY_CALL_LIMIT", "1")
    from sns_recommend.config import settings

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
