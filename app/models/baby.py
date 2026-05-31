import time
from uuid import UUID, uuid7

from sqlmodel import Field, SQLModel


class Baby(SQLModel, table=True):
    __tablename__ = "babies"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    name: str = Field(max_length=100)
    birth_date: int
    avatar_color: str = Field(default="#FF9AA2", max_length=7)
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))


class BabyCreate(SQLModel):
    name: str = Field(max_length=100)
    birth_date: int
    avatar_color: str = Field(default="#FF9AA2")


class BabyUpdate(SQLModel):
    name: str | None = None
    birth_date: int | None = None
    avatar_color: str | None = None
