from __future__ import annotations

import json

import pytest

from sns_recommend import cli


def test_seed_prepares_schema_before_inserting(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[str] = []

    def initialize() -> None:
        calls.append("schema")

    def seed() -> dict[str, int]:
        calls.append("seed")
        return {"users": 3, "posts": 200}

    monkeypatch.setattr("sys.argv", ["sns-recommend", "seed"])
    monkeypatch.setattr(cli, "initialize", initialize)
    monkeypatch.setattr(cli, "seed", seed)
    cli.main()
    assert calls == ["schema", "seed"]
    assert json.loads(capsys.readouterr().out) == {"users": 3, "posts": 200}


def test_failed_schema_preparation_does_not_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    def unavailable() -> None:
        raise ConnectionError("database unavailable")

    def unexpected_seed() -> None:
        pytest.fail("seed must not run after initialization fails")

    monkeypatch.setattr("sys.argv", ["sns-recommend", "seed"])
    monkeypatch.setattr(cli, "initialize", unavailable)
    monkeypatch.setattr(cli, "seed", unexpected_seed)
    with pytest.raises(ConnectionError, match="database unavailable"):
        cli.main()
