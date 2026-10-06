from fastapi import APIRouter

from sns_recommend.core.measurement import metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
def measurements():
    return metrics()
