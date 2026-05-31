from collections.abc import Generator

from sqlalchemy import create_engine
from sqlmodel import Session

from app.config import settings

engine = create_engine(settings.database_url, echo=False)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
