from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.models.baby import BabyCreate
from app.services import babies as baby_service
from app.templates_config import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request, session: Annotated[Session, Depends(get_session)]):
    babies = baby_service.list_babies(session)
    return templates.TemplateResponse(request, "home.html", {"babies": babies})


@router.post("/babies", response_class=HTMLResponse)
def create_baby_view(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    name: str = Form(...),
    birth_date: str = Form(...),
    avatar_color: str = Form("#FF9AA2"),
):
    bd = datetime.fromisoformat(birth_date).replace(tzinfo=UTC)
    body = BabyCreate(name=name, birth_date=int(bd.timestamp()), avatar_color=avatar_color)
    baby = baby_service.create_baby(session, body)

    if request.headers.get("HX-Request"):
        babies = baby_service.list_babies(session)
        return templates.TemplateResponse(
            request,
            "partials/baby_list.html",
            {"babies": babies},
            headers={"HX-Trigger": "closeSheet"},
        )
    return RedirectResponse(f"/babies/{baby.id}", status_code=303)


@router.delete("/babies/{baby_id}", response_class=HTMLResponse)
def delete_baby_view(
    baby_id: str,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    baby_service.delete_baby(session, UUID(baby_id))

    if request.headers.get("HX-Request"):
        babies = baby_service.list_babies(session)
        return templates.TemplateResponse(request, "partials/baby_list.html", {"babies": babies})
    return RedirectResponse("/", status_code=303)
