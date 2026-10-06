from uuid import uuid4

import pytest
from pydantic import ValidationError

from sns_recommend.data.events import Event


def test_post_event_requires_content_contract():
    with pytest.raises(ValidationError):
        Event(event_id=uuid4(), kind="post.updated", post_id=3)
    with pytest.raises(ValidationError):
        Event(event_id=uuid4(), kind="like", user_id=1)
