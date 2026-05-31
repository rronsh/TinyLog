from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.sleep import Sleep, SleepCreate, SleepEnd, SleepUpdate
from app.services import sleeps as sleep_service

router = APIRouter(tags=["sleeps"])


@router.get("/babies/{baby_id}/sleeps", response_model=list[Sleep])
def list_sleeps(
    baby_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    active: bool | None = Query(None),
):
    return sleep_service.list_sleeps(session, baby_id, limit=limit, offset=offset, active=active)


@router.post("/babies/{baby_id}/sleeps", response_model=Sleep, status_code=201)
def start_sleep(
    baby_id: UUID,
    body: SleepCreate,
    session: Annotated[Session, Depends(get_session)],
):
    data = body.model_dump(exclude_unset=True)
    return sleep_service.start_sleep(
        session,
        baby_id,
        start_time=data.get("start_time"),
        notes=data.get("notes"),
    )


@router.get("/babies/{baby_id}/sleeps/{sleep_id}", response_model=Sleep)
def get_sleep(
    baby_id: UUID,
    sleep_id: UUID,
    session: Annotated[Session, Depends(get_session)],
):
    return sleep_service.get_sleep(session, baby_id, sleep_id)


@router.patch("/babies/{baby_id}/sleeps/{sleep_id}", response_model=Sleep)
def update_sleep(
    baby_id: UUID,
    sleep_id: UUID,
    body: SleepUpdate,
    session: Annotated[Session, Depends(get_session)],
):
    return sleep_service.update_sleep(session, baby_id, sleep_id, body)


@router.post("/babies/{baby_id}/sleeps/{sleep_id}/end", response_model=Sleep)
def end_sleep(
    baby_id: UUID,
    sleep_id: UUID,
    body: SleepEnd,
    session: Annotated[Session, Depends(get_session)],
):
    return sleep_service.end_sleep(session, baby_id, sleep_id, end_time=body.end_time)


@router.delete("/babies/{baby_id}/sleeps/{sleep_id}", status_code=204)
def delete_sleep(
    baby_id: UUID,
    sleep_id: UUID,
    session: Annotated[Session, Depends(get_session)],
):
    sleep_service.get_sleep(session, baby_id, sleep_id)
    sleep_service.delete_sleep(session, baby_id, sleep_id)
