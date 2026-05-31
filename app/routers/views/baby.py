from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from app.database import get_session
from app.services import babies as baby_service
from app.services import feedings as feeding_service
from app.services import sleeps as sleep_service
from app.templates_config import templates

router = APIRouter()


@router.get("/babies/{baby_id}", response_class=HTMLResponse)
def baby_dashboard(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    baby = baby_service.get_baby(session, baby_id)
    recent_feedings = feeding_service.get_recent_feedings(session, baby_id)
    sleep = sleep_service.get_active_sleep(session, baby_id)
    recent_sleeps = sleep_service.get_recent_sleeps(session, baby_id)

    return templates.TemplateResponse(
        request,
        "baby_dashboard.html",
        {
            "baby": baby,
            "current_baby": baby,
            "current_section": "dashboard",
            "recent_feedings": recent_feedings,
            "sleep": sleep,
            "recent_sleeps": recent_sleeps,
        },
    )
