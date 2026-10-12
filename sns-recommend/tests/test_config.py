from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from sns_recommend.core.config import Settings


@pytest.mark.parametrize(
    "values",
    [
        {"cursor_secret": ""},
        {"cursor_secret": " "},
        {"cursor_secret": "비밀"},
        {"dimensions": 4},
        {"snapshot_ttl": 0},
        {"lease_seconds": -1},
        {"daily_call_limit": -1},
        {"input_usd_per_million": float("inf")},
    ],
)
def test_invalid_settings_are_rejected(values: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        Settings(**{"_env_file": None, **values})


def test_config_hides_cursor_secret() -> None:
    values: dict[str, Any] = {
        "_env_file": None,
        "cursor_secret": "private-test-token",
    }
    cfg = Settings(**values)
    assert "private-test-token" not in repr(cfg)

