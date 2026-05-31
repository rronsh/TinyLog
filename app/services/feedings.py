import time
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.feeding import BreastSide, Feeding, FeedingType, FeedingUpdate
from app.services import babies as baby_service


def list_feedings(
    session: Session,
    baby_id: UUID,
    limit: int = 50,
    offset: int = 0,
) -> list[Feeding]:
    return list(
        session.exec(
            select(Feeding)
            .where(Feeding.baby_id == baby_id)
            .order_by(Feeding.timestamp.desc())  # type: ignore
            .offset(offset)
            .limit(limit)
        ).all()
    )


def get_recent_feedings(
    session: Session,
    baby_id: UUID,
    limit: int = 5,
) -> list[Feeding]:
    return list_feedings(session, baby_id, limit=limit)


def create_feeding(
    session: Session,
    baby_id: UUID,
    *,
    feeding_type: FeedingType,
    side: BreastSide | None = None,
    amount_ml: float | None = None,
    duration_seconds: int | None = None,
    left_duration_seconds: int | None = None,
    right_duration_seconds: int | None = None,
    timestamp: int | None = None,
    notes: str | None = None,
) -> Feeding:
    baby_service.get_baby(session, baby_id)
    feeding = Feeding(
        baby_id=baby_id,
        feeding_type=feeding_type,
        side=side,
        amount_ml=amount_ml,
        duration_seconds=duration_seconds,
        left_duration_seconds=left_duration_seconds,
        right_duration_seconds=right_duration_seconds,
        timestamp=timestamp if timestamp is not None else int(time.time()),
        notes=notes,
    )
    session.add(feeding)
    session.commit()
    session.refresh(feeding)
    return feeding


def get_feeding(
    session: Session,
    baby_id: UUID,
    feeding_id: UUID,
) -> Feeding:
    feeding = session.get(Feeding, feeding_id)
    if not feeding or feeding.baby_id != baby_id:
        raise HTTPException(404, "Feeding not found")
    return feeding


def update_feeding(
    session: Session,
    baby_id: UUID,
    feeding_id: UUID,
    data: FeedingUpdate,
) -> Feeding:
    feeding = get_feeding(session, baby_id, feeding_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(feeding, field, value)
    session.add(feeding)
    session.commit()
    session.refresh(feeding)
    return feeding


def delete_feeding(
    session: Session,
    baby_id: UUID,
    feeding_id: UUID,
) -> None:
    feeding = session.get(Feeding, feeding_id)
    if feeding and feeding.baby_id == baby_id:
        session.delete(feeding)
        session.commit()
