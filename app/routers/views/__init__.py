from fastapi import APIRouter

from app.routers.views import baby, feedings, forms, home, sleeps

views_router = APIRouter()
views_router.include_router(forms.router)
views_router.include_router(home.router)
views_router.include_router(baby.router)
views_router.include_router(feedings.router)
views_router.include_router(sleeps.router)
