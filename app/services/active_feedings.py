import time
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.active_breast_feeding import ActiveBreastFeeding
from app.models.feeding import BreastSide, Feeding, FeedingType
from app.services import babies as baby_service


def get_active(session: Session, baby_id: UUID) -> ActiveBreastFeeding | None:
    return session.exec(select(ActiveBreastFeeding).where(ActiveBreastFeeding.baby_id == baby_id)).first()


def start(session: Session, baby_id: UUID, side: str = "left") -> ActiveBreastFeeding:
    baby_service.get_baby(session, baby_id)

    existing = get_active(session, baby_id)
    if existing:
        session.delete(existing)
        session.commit()

    now = int(time.time())
    active = ActiveBreastFeeding(
        baby_id=baby_id,
        started_at=now,
        current_side=side,
        last_switch_at=now,
        left_accumulated=0,
        right_accumulated=0,
    )
    session.add(active)
    session.commit()
    session.refresh(active)
    return active


def switch_side(session: Session, baby_id: UUID, new_side: str) -> ActiveBreastFeeding:
    active = get_active(session, baby_id)
    if not active:
        raise HTTPException(404, "No active feeding session")

    if new_side == active.current_side:
        return active

    elapsed = int(time.time()) - active.last_switch_at
    if active.current_side == "left":
        active.left_accumulated += elapsed
    else:
        active.right_accumulated += elapsed

    active.current_side = new_side
    active.last_switch_at = int(time.time())
    session.add(active)
    session.commit()
    session.refresh(active)
    return active


def stop_and_log(
    session: Session,
    baby_id: UUID,
    notes: str | None = None,
    timestamp: int | None = None,
) -> Feeding:
    active = get_active(session, baby_id)
    if not active:
        raise HTTPException(404, "No active feeding session")

    elapsed = int(time.time()) - active.last_switch_at
    left = active.left_accumulated + (elapsed if active.current_side == "left" else 0)
    right = active.right_accumulated + (elapsed if active.current_side == "right" else 0)
    total = left + right

    if left > 0 and right > 0:
        side = BreastSide.BOTH
    elif right > 0:
        side = BreastSide.RIGHT
    else:
        side = BreastSide.LEFT

    feeding = Feeding(
        baby_id=baby_id,
        feeding_type=FeedingType.BREAST,
        side=side,
        duration_seconds=total if total > 0 else None,
        left_duration_seconds=left if left > 0 else None,
        right_duration_seconds=right if right > 0 else None,
        timestamp=timestamp if timestamp is not None else active.started_at,
        notes=notes or None,
    )
    session.add(feeding)
    session.delete(active)
    session.commit()
    session.refresh(feeding)
    return feeding
