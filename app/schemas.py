"""Request and response models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200, examples=["Buy milk"])
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime


class TaskPage(BaseModel):
    """One page of tasks. `total` is the filtered count before limit and offset."""

    items: list[TaskRead]
    total: int
    limit: int
    offset: int
