from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from app.database import get_session
from app.models.baby import Baby
from app.services import active_feedings as active_feeding_service
from app.templates_config import templates

router = APIRouter()


@router.get("/babies/new-form", response_class=HTMLResponse)
def baby_form(request: Request):
    return templates.TemplateResponse(request, "partials/baby_form.html")


@router.get("/babies/{baby_id}/feedings/form", response_class=HTMLResponse)
def feeding_form(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    baby = session.get(Baby, baby_id)
    active = active_feeding_service.get_active(session, baby_id)
    return templates.TemplateResponse(
        request,
        "partials/feeding_form.html",
        {"baby": baby, "active": active},
    )
