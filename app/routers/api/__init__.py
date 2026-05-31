from fastapi import APIRouter

from app.routers.api import babies, feedings, sleeps

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(babies.router)
api_router.include_router(feedings.router)
api_router.include_router(sleeps.router)
