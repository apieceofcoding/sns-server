from __future__ import annotations

from pathlib import Path

import pytest

from sns_recommend.providers.embeddings import FixtureEmbeddings, checked_vectors, normalize
from sns_recommend.providers.recordings import write_recording


def test_synthetic_vectors_preserve_topic_and_shape() -> None:
    embedding = FixtureEmbeddings()
    a, b, c = embedding.embed_documents(["Python 백엔드", "PostgreSQL FastAPI", "제주 여행"])

    def dot(x: list[float], y: list[float]) -> float:
        return sum(i * j for i, j in zip(x, y, strict=True))

    assert len(a) == 768
    assert dot(a, b) > dot(a, c)
    assert abs(sum(i * i for i in normalize(a)) - 1) < 1e-6


@pytest.mark.parametrize("vectors", [[], [[1.0]], [[float("nan")] * 768], [[0.0] * 768]])
def test_invalid_provider_vectors_are_rejected(vectors: object) -> None:
    with pytest.raises(ValueError):
        checked_vectors(vectors, 1)


def test_recordings_are_private_and_failed_write_preserves_previous_file(tmp_path: Path) -> None:
    path = tmp_path / "response.json"
    write_recording(path, {"result": "ok"})
    assert path.stat().st_mode & 0o777 == 0o600
    original = path.read_text()
    with pytest.raises(ValueError):
        write_recording(path, {"result": float("nan")})
    assert path.read_text() == original
    assert list(tmp_path.iterdir()) == [path]
