import time
from uuid import UUID, uuid7

from sqlmodel import Field, SQLModel


class ActiveBreastFeeding(SQLModel, table=True):
    __tablename__ = "active_breast_feedings"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    baby_id: UUID = Field(foreign_key="babies.id", index=True, unique=True)
    started_at: int = Field(default_factory=lambda: int(time.time()))
    current_side: str = "left"
    last_switch_at: int = Field(default_factory=lambda: int(time.time()))
    left_accumulated: int = 0
    right_accumulated: int = 0
    notes: str | None = None
