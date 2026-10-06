from fastapi import Depends, FastAPI

from sns_recommend.api.dependencies import authenticate
from sns_recommend.api.routers import events, feeds, health, metrics


def create_app():
    app = FastAPI(title="SNS Recommend", version="0.1.0")
    app.include_router(health.router)
    for router in (feeds.router, events.router, metrics.router):
        app.include_router(router, prefix="/internal", dependencies=[Depends(authenticate)])
    return app


app = create_app()
