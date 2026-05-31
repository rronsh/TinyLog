from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.services import babies as baby_service
from app.services import sleeps as sleep_service
from app.templates_config import templates

router = APIRouter()


@router.get("/babies/{baby_id}/sleeps", response_class=HTMLResponse)
def sleeps_page(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    baby = baby_service.get_baby(session, baby_id)
    sleep = sleep_service.get_active_sleep(session, baby_id)
    sleeps = sleep_service.list_sleeps(session, baby_id)
    return templates.TemplateResponse(
        request,
        "sleeps.html",
        {
            "baby": baby,
            "current_baby": baby,
            "current_section": "sleeps",
            "sleep": sleep,
            "sleeps": sleeps,
        },
    )


@router.post("/babies/{baby_id}/sleeps/start", response_class=HTMLResponse)
def start_sleep_view(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    notes: str = Form(None),
):
    baby = baby_service.get_baby(session, baby_id)
    sleep = sleep_service.start_sleep(session, baby_id, notes=notes or None)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "partials/sleep_timer.html",
            {"baby": baby, "sleep": sleep},
        )
    return RedirectResponse(f"/babies/{baby_id}/sleeps", status_code=303)


@router.post("/babies/{baby_id}/sleeps/{sleep_id}/end", response_class=HTMLResponse)
def end_sleep_view(
    baby_id: UUID,
    sleep_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    sleep_service.end_sleep(session, baby_id, sleep_id)
    baby = baby_service.get_baby(session, baby_id)

    if request.headers.get("HX-Request"):
        current_url = request.headers.get("HX-Current-URL", "")
        is_dashboard = current_url.endswith(f"/babies/{baby_id}") or f"/babies/{baby_id}?" in current_url

        if is_dashboard:
            recent_sleeps = sleep_service.get_recent_sleeps(session, baby_id)
            return templates.TemplateResponse(
                request,
                "partials/dashboard_sleep_body.html",
                {"baby": baby, "sleep": None, "recent_sleeps": recent_sleeps},
            )

        sleeps = sleep_service.list_sleeps(session, baby_id)
        return templates.TemplateResponse(
            request,
            "partials/sleep_list.html",
            {"baby": baby, "sleep": None, "sleeps": sleeps},
        )
    return RedirectResponse(f"/babies/{baby_id}/sleeps", status_code=303)


@router.delete("/babies/{baby_id}/sleeps/{sleep_id}", response_class=HTMLResponse)
def delete_sleep_view(
    baby_id: UUID,
    sleep_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    sleep_service.delete_sleep(session, baby_id, sleep_id)

    if request.headers.get("HX-Request"):
        return HTMLResponse("")
    return RedirectResponse(f"/babies/{baby_id}/sleeps", status_code=303)
