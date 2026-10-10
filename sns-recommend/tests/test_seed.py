from __future__ import annotations

from sns_recommend.data.seed import TOPICS


def test_course_topics_have_content() -> None:
    assert len(TOPICS) == 5
    assert all(len(v) > 10 for v in TOPICS.values())


def test_post_examples_are_distinct_and_deterministic() -> None:
    from sns_recommend.post_examples import post_body

    bodies = [post_body(topic, n) for topic in TOPICS for n in range(40)]
    assert len(set(bodies)) == 200
    assert bodies == [post_body(topic, n) for topic in TOPICS for n in range(40)]
    assert all("오늘의 기록" not in body for body in bodies)
