from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.feeding import Feeding, FeedingCreate, FeedingUpdate
from app.services import feedings as feeding_service

router = APIRouter(tags=["feedings"])


@router.get("/babies/{baby_id}/feedings", response_model=list[Feeding])
def list_feedings(
    baby_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return feeding_service.list_feedings(session, baby_id, limit=limit, offset=offset)


@router.post("/babies/{baby_id}/feedings", response_model=Feeding, status_code=201)
def create_feeding(
    baby_id: UUID,
    body: FeedingCreate,
    session: Annotated[Session, Depends(get_session)],
):
    data = body.model_dump(exclude_unset=True)
    return feeding_service.create_feeding(
        session,
        baby_id,
        feeding_type=data["feeding_type"],
        side=data.get("side"),
        amount_ml=data.get("amount_ml"),
        duration_seconds=data.get("duration_seconds"),
        left_duration_seconds=data.get("left_duration_seconds"),
        right_duration_seconds=data.get("right_duration_seconds"),
        timestamp=data.get("timestamp"),
        notes=data.get("notes"),
    )


@router.get("/babies/{baby_id}/feedings/{feeding_id}", response_model=Feeding)
def get_feeding(
    baby_id: UUID,
    feeding_id: UUID,
    session: Annotated[Session, Depends(get_session)],
):
    return feeding_service.get_feeding(session, baby_id, feeding_id)


@router.patch("/babies/{baby_id}/feedings/{feeding_id}", response_model=Feeding)
def update_feeding(
    baby_id: UUID,
    feeding_id: UUID,
    body: FeedingUpdate,
    session: Annotated[Session, Depends(get_session)],
):
    return feeding_service.update_feeding(session, baby_id, feeding_id, body)


@router.delete("/babies/{baby_id}/feedings/{feeding_id}", status_code=204)
def delete_feeding(
    baby_id: UUID,
    feeding_id: UUID,
    session: Annotated[Session, Depends(get_session)],
):
    feeding_service.get_feeding(session, baby_id, feeding_id)
    feeding_service.delete_feeding(session, baby_id, feeding_id)
