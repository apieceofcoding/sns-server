from __future__ import annotations

from typing import Never

import psycopg
import pytest

import sns_recommend.worker.runner as runner


def test_worker_retries_storage_outage_without_logging_credentials(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    attempts = []
    waits = []

    def unavailable() -> Never:
        attempts.append(1)
        raise psycopg.OperationalError("sensitive-database-password")

    def stop_after_retry(seconds: float) -> None:
        waits.append(seconds)
        if len(waits) == 2:
            raise KeyboardInterrupt()

    monkeypatch.setattr("sys.argv", ["sns_recommend.worker"])
    monkeypatch.setattr(runner, "schedule_active", lambda: None)
    monkeypatch.setattr(runner, "run_one", unavailable)
    monkeypatch.setattr(runner.time, "sleep", stop_after_retry)
    with pytest.raises(KeyboardInterrupt):
        runner.main()
    assert len(attempts) == 2
    assert waits == [1, 1]
    assert "OperationalError" in caplog.text
    assert "sensitive-database-password" not in caplog.text
