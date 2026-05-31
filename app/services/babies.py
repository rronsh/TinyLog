import time
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.baby import Baby, BabyCreate, BabyUpdate


def list_babies(session: Session) -> list[Baby]:
    return list(session.exec(select(Baby).order_by(Baby.created_at)).all())  # type: ignore


def create_baby(session: Session, data: BabyCreate) -> Baby:
    baby = Baby.model_validate(data)
    session.add(baby)
    session.commit()
    session.refresh(baby)
    return baby


def get_baby(session: Session, baby_id: UUID) -> Baby:
    baby = session.get(Baby, baby_id)
    if not baby:
        raise HTTPException(404, "Baby not found")
    return baby


def update_baby(session: Session, baby_id: UUID, data: BabyUpdate) -> Baby:
    baby = get_baby(session, baby_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(baby, field, value)
    baby.updated_at = int(time.time())
    session.add(baby)
    session.commit()
    session.refresh(baby)
    return baby


def delete_baby(session: Session, baby_id: UUID) -> None:
    baby = session.get(Baby, baby_id)
    if baby:
        session.delete(baby)
        session.commit()
