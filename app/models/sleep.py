import time
from uuid import UUID, uuid7

from sqlmodel import Field, SQLModel


class Sleep(SQLModel, table=True):
    __tablename__ = "sleeps"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    baby_id: UUID = Field(foreign_key="babies.id", index=True)
    start_time: int = Field(default_factory=lambda: int(time.time()))
    end_time: int | None = None
    duration_seconds: int | None = None
    notes: str | None = None
    created_at: int = Field(default_factory=lambda: int(time.time()))

    @property
    def is_active(self) -> bool:
        return self.end_time is None


class SleepCreate(SQLModel):
    start_time: int | None = None
    notes: str | None = None


class SleepUpdate(SQLModel):
    start_time: int | None = None
    end_time: int | None = None
    notes: str | None = None


class SleepEnd(SQLModel):
    end_time: int | None = None
