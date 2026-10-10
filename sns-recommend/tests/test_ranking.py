from __future__ import annotations

import pytest

from sns_recommend.core.types import Candidate
from sns_recommend.recommenders.ranking import diversify, validate_ranking

CANDIDATES: list[Candidate] = [
    {"id": 1, "author_id": 1, "topic": "a", "body": "Python", "created_at": "2026-10-07T00:00:00Z"},
    {"id": 2, "author_id": 1, "topic": "a", "body": "Python", "created_at": "2026-10-07T00:00:00Z"},
    {"id": 3, "author_id": 2, "topic": "b", "body": "Travel", "created_at": "2026-10-07T00:00:00Z"},
]


@pytest.mark.parametrize("ids", [[1, 2], [1, 2, 99], [1, 1, 3], [True, 2, 3]])
def test_rejects_invalid_model_ids(ids: object) -> None:
    with pytest.raises(ValueError):
        validate_ranking(CANDIDATES, ids)


def test_diversity_preserves_candidates_but_separates_authors() -> None:
    assert diversify(CANDIDATES, [1, 2, 3]) == [1, 3, 2]
