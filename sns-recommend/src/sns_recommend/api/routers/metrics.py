from __future__ import annotations

from fastapi import APIRouter

from sns_recommend.core.measurement import metrics
from sns_recommend.core.types import MetricsReport

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
def measurements() -> MetricsReport:
    return metrics()
