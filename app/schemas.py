from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


TaskStatus = Literal["open", "done"]
TaskFrequency = Literal["once", "daily", "weekly"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    assignee: str = Field(default="כולם", max_length=60)
    due_date: date | None = None
    frequency: TaskFrequency = "once"
    notes: str = Field(default="", max_length=500)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    assignee: str | None = Field(default=None, max_length=60)
    due_date: date | None = None
    frequency: TaskFrequency | None = None
    notes: str | None = Field(default=None, max_length=500)
    status: TaskStatus | None = None


class Task(BaseModel):
    id: int
    title: str
    assignee: str
    due_date: date | None
    frequency: TaskFrequency
    notes: str
    status: TaskStatus
    created_at: str
    completed_at: str | None

