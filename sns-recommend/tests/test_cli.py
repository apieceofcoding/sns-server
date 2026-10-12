import json
import sys

import psycopg
import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from sns_recommend import cli


@pytest.mark.parametrize(("error", "hint"), [
    (psycopg.OperationalError("private connection details"), "up -d --wait postgres"),
    (psycopg.errors.UndefinedTable("posts"), "uv run sns-recommend seed"),
    (RedisConnectionError("private connection details"), "docker compose up -d --wait"),
    (RedisTimeoutError("timed out"), "REDIS_URL"),
])
def test_baseline_dependency_failure_has_recovery_hint(monkeypatch, capsys, error, hint):
    monkeypatch.setattr(sys, "argv", ["sns-recommend", "baseline", "--user", "7"])

    def fail(*args):
        raise error

    monkeypatch.setattr(cli, "baseline", fail)
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert hint in output.err
    assert "private connection details" not in output.err
    assert "Traceback" not in output.err


def test_baseline_success_keeps_json_output(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "sns-recommend", "baseline", "--user", "7", "--strategy", "latest",
    ])
    monkeypatch.setattr(cli, "baseline", lambda user, strategy: {
        "user_id": user, "strategy": strategy, "count": 240,
    })
    cli.main()
    assert json.loads(capsys.readouterr().out) == {
        "user_id": 7, "strategy": "latest", "count": 240,
    }
