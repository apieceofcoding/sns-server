from sns_recommend.seed import TOPICS


def test_course_topics_have_content():
    assert len(TOPICS) == 6
    assert all(len(v) > 10 for v in TOPICS.values())
