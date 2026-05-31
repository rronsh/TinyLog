import time
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.sleep import Sleep, SleepUpdate
from app.services import babies as baby_service


def list_sleeps(
    session: Session,
    baby_id: UUID,
    limit: int = 50,
    offset: int = 0,
    active: bool | None = None,
) -> list[Sleep]:
    q = select(Sleep).where(Sleep.baby_id == baby_id)
    if active is True:
        q = q.where(Sleep.end_time == None)  # noqa: E711
    elif active is False:
        q = q.where(Sleep.end_time != None)  # noqa: E711
    return list(session.exec(q.order_by(Sleep.start_time.desc()).offset(offset).limit(limit)).all())  # type: ignore


def get_recent_sleeps(
    session: Session,
    baby_id: UUID,
    limit: int = 5,
) -> list[Sleep]:
    return list_sleeps(session, baby_id, limit=limit)


def get_active_sleep(session: Session, baby_id: UUID) -> Sleep | None:
    return session.exec(
        select(Sleep)
        .where(Sleep.baby_id == baby_id, Sleep.end_time == None)  # noqa: E711
        .limit(1)
    ).first()


def start_sleep(
    session: Session,
    baby_id: UUID,
    *,
    start_time: int | None = None,
    notes: str | None = None,
) -> Sleep:
    baby_service.get_baby(session, baby_id)
    sleep = Sleep(
        baby_id=baby_id,
        start_time=start_time if start_time is not None else int(time.time()),
        notes=notes,
    )
    session.add(sleep)
    session.commit()
    session.refresh(sleep)
    return sleep


def get_sleep(
    session: Session,
    baby_id: UUID,
    sleep_id: UUID,
) -> Sleep:
    sleep = session.get(Sleep, sleep_id)
    if not sleep or sleep.baby_id != baby_id:
        raise HTTPException(404, "Sleep not found")
    return sleep


def update_sleep(
    session: Session,
    baby_id: UUID,
    sleep_id: UUID,
    data: SleepUpdate,
) -> Sleep:
    sleep = get_sleep(session, baby_id, sleep_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sleep, field, value)
    if sleep.end_time and sleep.start_time:
        sleep.duration_seconds = sleep.end_time - sleep.start_time
    session.add(sleep)
    session.commit()
    session.refresh(sleep)
    return sleep


def end_sleep(
    session: Session,
    baby_id: UUID,
    sleep_id: UUID,
    end_time: int | None = None,
) -> Sleep:
    sleep = get_sleep(session, baby_id, sleep_id)
    if sleep.end_time is not None:
        raise HTTPException(400, "Sleep already ended")
    t = end_time if end_time is not None else int(time.time())
    sleep.end_time = t
    sleep.duration_seconds = t - sleep.start_time
    session.add(sleep)
    session.commit()
    session.refresh(sleep)
    return sleep


def delete_sleep(
    session: Session,
    baby_id: UUID,
    sleep_id: UUID,
) -> None:
    sleep = session.get(Sleep, sleep_id)
    if sleep and sleep.baby_id == baby_id:
        session.delete(sleep)
        session.commit()
