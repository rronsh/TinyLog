import time
from enum import StrEnum
from uuid import UUID, uuid7

from sqlmodel import Field, SQLModel


class FeedingType(StrEnum):
    BREAST = "breast"
    BOTTLE = "bottle"


class BreastSide(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


class Feeding(SQLModel, table=True):
    __tablename__ = "feedings"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    baby_id: UUID = Field(foreign_key="babies.id", index=True)
    feeding_type: FeedingType
    side: BreastSide | None = None
    amount_ml: float | None = None
    duration_seconds: int | None = None
    left_duration_seconds: int | None = None
    right_duration_seconds: int | None = None
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    notes: str | None = None
    created_at: int = Field(default_factory=lambda: int(time.time()))


class FeedingCreate(SQLModel):
    feeding_type: FeedingType
    side: BreastSide | None = None
    amount_ml: float | None = None
    duration_seconds: int | None = None
    left_duration_seconds: int | None = None
    right_duration_seconds: int | None = None
    timestamp: int | None = None
    notes: str | None = None


class FeedingUpdate(SQLModel):
    feeding_type: FeedingType | None = None
    side: BreastSide | None = None
    amount_ml: float | None = None
    duration_seconds: int | None = None
    left_duration_seconds: int | None = None
    right_duration_seconds: int | None = None
    timestamp: int | None = None
    notes: str | None = None
