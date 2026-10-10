from __future__ import annotations

from sns_recommend.data.seed import TOPICS


def test_course_topics_have_content() -> None:
    assert len(TOPICS) == 5
    assert all(len(v) > 10 for v in TOPICS.values())
