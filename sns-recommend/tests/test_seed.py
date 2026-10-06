from sns_recommend.data.seed import TOPICS


def test_course_topics_have_content():
    assert len(TOPICS) == 5
    assert all(len(v) > 10 for v in TOPICS.values())
