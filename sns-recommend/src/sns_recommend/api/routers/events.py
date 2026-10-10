from __future__ import annotations

from fastapi import APIRouter, HTTPException

from sns_recommend.core.types import EventResult
from sns_recommend.data.events import Event, accept_event

router = APIRouter(prefix="/events", tags=["events"])


@router.post("")
def events(event: Event) -> EventResult:
    try:
        return accept_event(event)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
