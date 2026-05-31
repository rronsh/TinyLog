from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.baby import Baby, BabyCreate, BabyUpdate
from app.services import babies as baby_service

router = APIRouter(prefix="/babies", tags=["babies"])


@router.get("", response_model=list[Baby])
def list_babies(session: Annotated[Session, Depends(get_session)]):
    return baby_service.list_babies(session)


@router.post("", response_model=Baby, status_code=201)
def create_baby(body: BabyCreate, session: Annotated[Session, Depends(get_session)]):
    return baby_service.create_baby(session, body)


@router.get("/{baby_id}", response_model=Baby)
def get_baby(baby_id: UUID, session: Annotated[Session, Depends(get_session)]):
    return baby_service.get_baby(session, baby_id)


@router.patch("/{baby_id}", response_model=Baby)
def update_baby(
    baby_id: UUID,
    body: BabyUpdate,
    session: Annotated[Session, Depends(get_session)],
):
    return baby_service.update_baby(session, baby_id, body)


@router.delete("/{baby_id}", status_code=204)
def delete_baby(baby_id: UUID, session: Annotated[Session, Depends(get_session)]):
    baby_service.get_baby(session, baby_id)
    baby_service.delete_baby(session, baby_id)
