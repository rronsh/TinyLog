import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from app.database import get_session
from app.main import app

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(name="engine", scope="function")
def engine_fixture():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(name="session", scope="function")
def session_fixture(engine):
    factory = sessionmaker(engine, class_=Session, expire_on_commit=False)
    with factory() as session:
        yield session


@pytest.fixture(name="client", scope="function")
async def client_fixture(session):
    def override():
        yield session

    app.dependency_overrides[get_session] = override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
