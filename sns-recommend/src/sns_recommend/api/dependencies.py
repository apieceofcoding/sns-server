from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Header, HTTPException

from sns_recommend.core.config import settings


def authenticate(x_internal_token: Annotated[str, Header()] = "") -> None:
    expected = settings().internal_token.get_secret_value().encode()
    if not secrets.compare_digest(x_internal_token.encode(), expected):
        raise HTTPException(401, "invalid internal token")
