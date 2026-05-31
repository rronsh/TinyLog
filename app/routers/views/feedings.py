import time
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.models.feeding import BreastSide, FeedingType
from app.services import active_feedings as active_feeding_service
from app.services import babies as baby_service
from app.services import feedings as feeding_service
from app.templates_config import templates

router = APIRouter()


@router.get("/babies/{baby_id}/feedings", response_class=HTMLResponse)
def feedings_page(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    baby = baby_service.get_baby(session, baby_id)
    feedings = feeding_service.list_feedings(session, baby_id)
    return templates.TemplateResponse(
        request,
        "feedings.html",
        {
            "baby": baby,
            "current_baby": baby,
            "current_section": "feedings",
            "feedings": feedings,
        },
    )


@router.get("/babies/{baby_id}/feedings/dashboard", response_class=HTMLResponse)
def feedings_dashboard_partial(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    baby = baby_service.get_baby(session, baby_id)
    recent_feedings = feeding_service.get_recent_feedings(session, baby_id)
    return templates.TemplateResponse(
        request,
        "partials/dashboard_feeding_body.html",
        {"baby": baby, "recent_feedings": recent_feedings},
    )


@router.get("/babies/{baby_id}/feedings/list", response_class=HTMLResponse)
def feedings_list_partial(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    baby = baby_service.get_baby(session, baby_id)
    feedings = feeding_service.list_feedings(session, baby_id)
    return templates.TemplateResponse(
        request,
        "partials/feeding_list.html",
        {"baby": baby, "feedings": feedings},
    )


@router.post("/babies/{baby_id}/feedings", response_class=HTMLResponse)
def log_feeding_view(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    feeding_type: str = Form(...),
    side: str = Form(None),
    amount_ml: float = Form(None),
    duration_minutes: int = Form(None),
    timestamp: str = Form(None),
    notes: str = Form(None),
):
    baby = baby_service.get_baby(session, baby_id)

    if timestamp:
        dt = datetime.fromisoformat(timestamp)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        ts = int(dt.timestamp())
    else:
        ts = int(time.time())

    ft = FeedingType(feeding_type)
    feeding_service.create_feeding(
        session,
        baby_id,
        feeding_type=ft,
        side=BreastSide(side) if ft == FeedingType.BREAST and side else None,
        amount_ml=amount_ml,
        duration_seconds=duration_minutes * 60 if duration_minutes else None,
        timestamp=ts,
        notes=notes or None,
    )

    if request.headers.get("HX-Request"):
        feedings = feeding_service.list_feedings(session, baby_id)
        return templates.TemplateResponse(
            request,
            "partials/feeding_list.html",
            {"baby": baby, "feedings": feedings},
            headers={"HX-Trigger": '{"closeSheet": true, "feedingLogged": true}'},
        )
    return RedirectResponse(f"/babies/{baby_id}/feedings", status_code=303)


@router.delete("/babies/{baby_id}/feedings/{feeding_id}", response_class=HTMLResponse)
def delete_feeding_view(
    baby_id: UUID,
    feeding_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    feeding_service.delete_feeding(session, baby_id, feeding_id)

    if request.headers.get("HX-Request"):
        return HTMLResponse("")
    return RedirectResponse(f"/babies/{baby_id}/feedings", status_code=303)


@router.post("/babies/{baby_id}/feedings/start", response_class=HTMLResponse)
def start_feeding_timer(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    side: str = Form("left"),
):
    baby = baby_service.get_baby(session, baby_id)
    active = active_feeding_service.start(session, baby_id, side=side)
    return templates.TemplateResponse(
        request,
        "partials/feeding_form.html",
        {"baby": baby, "active": active},
        headers={"HX-Trigger": '{"feedingTimerStarted": true}'},
    )


@router.post("/babies/{baby_id}/feedings/active/switch", response_class=HTMLResponse)
def switch_feeding_side(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    side: str = Form(...),
):
    baby = baby_service.get_baby(session, baby_id)
    active = active_feeding_service.switch_side(session, baby_id, new_side=side)
    return templates.TemplateResponse(
        request,
        "partials/feeding_timer_section.html",
        {"baby": baby, "active": active},
    )


@router.post("/babies/{baby_id}/feedings/active/stop", response_class=HTMLResponse)
def stop_feeding_timer(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    notes: str = Form(None),
):
    active_feeding_service.stop_and_log(session, baby_id, notes=notes)
    return HTMLResponse(
        "",
        headers={"HX-Trigger": '{"closeSheet": true, "feedingLogged": true, "feedingTimerStopped": true}'},
    )


@router.get("/babies/{baby_id}/feedings/active-badge", response_class=HTMLResponse)
def active_feeding_badge(
    baby_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    active = active_feeding_service.get_active(session, baby_id)
    return templates.TemplateResponse(
        request,
        "partials/feeding_active_badge.html",
        {"baby_id": str(baby_id), "active": active},
    )
