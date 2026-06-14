from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.ringcentral import router as ringcentral_router
from app.api.v1.sheets import router as sheets_router
from app.api.v1.summaries import router as summaries_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(ringcentral_router)
api_router.include_router(summaries_router)
api_router.include_router(sheets_router)
api_router.include_router(jobs_router)
api_router.include_router(health_router)

__all__ = ["api_router"]
