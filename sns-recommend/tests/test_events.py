from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from sns_recommend.api import app
from sns_recommend.data.events import Event


def test_post_event_requires_content_contract():
    with pytest.raises(ValidationError):
        Event(event_id=uuid4(), kind="post.updated", post_id=3)
    with pytest.raises(ValidationError):
        Event(event_id=uuid4(), kind="like", user_id=1)


@pytest.mark.parametrize(
    "changes",
    [
        {"post_id": True},
        {"post_id": 2**63},
        {"version": 2**63},
        {"occurred_at": "2026-10-06T12:00:00"},
        {"payload": {"body": "Python", "author_id": "10", "topic": "backend"}},
        {"payload": {"body": {"text": "Python"}, "author_id": 10, "topic": "backend"}},
        {"payload": {"body": "x" * 10_001, "author_id": 10, "topic": "backend"}},
        {"payload": {"body": "Python", "author_id": 10, "topic": "backend", "extra": 1}},
    ],
)
def test_invalid_events_are_rejected(changes):
    event = {
        "event_id": uuid4(),
        "kind": "post.updated",
        "post_id": 3,
        "payload": {"body": "Python", "author_id": 10, "topic": "backend"},
    }
    with pytest.raises(ValidationError):
        Event.model_validate({**event, **changes})


def test_invalid_profile_payload_never_reaches_database(monkeypatch):
    def forbidden(*args):
        raise AssertionError("invalid request reached database")

    monkeypatch.setattr("sns_recommend.api.routers.events.accept_event", forbidden)
    response = TestClient(app).post(
        "/internal/events",
        headers={"X-Internal-Token": "course-local-token"},
        json={
            "event_id": str(uuid4()),
            "kind": "profile.updated",
            "user_id": 1,
            "payload": {"interests": ["Python"]},
        },
    )
    assert response.status_code == 422
