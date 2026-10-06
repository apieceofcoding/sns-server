import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from sns_recommend.api.dependencies import authenticate
from sns_recommend.core.config import Settings


@pytest.mark.parametrize(
    "values",
    [
        {"internal_token": ""},
        {"internal_token": " "},
        {"internal_token": "비밀"},
        {"dimensions": 4},
        {"snapshot_ttl": 0},
        {"lease_seconds": -1},
        {"daily_call_limit": -1},
        {"input_usd_per_million": float("inf")},
    ],
)
def test_invalid_settings_are_rejected(values):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **values)


def test_config_hides_internal_token():
    cfg = Settings(_env_file=None, internal_token="private-test-token")
    assert "private-test-token" not in repr(cfg)


def test_non_ascii_authentication_returns_unauthorized():
    with pytest.raises(HTTPException) as error:
        authenticate("잘못된 토큰")
    assert error.value.status_code == 401
