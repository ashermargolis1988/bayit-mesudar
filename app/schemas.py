from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


TaskStatus = Literal["open", "done"]
TaskFrequency = Literal["once", "daily", "weekly"]


class UserCreateInternal(BaseModel):
    name: str
    email: EmailStr
    password_hash: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("שם המשתמש לא יכול להיות ריק")
        if len(normalized) > 80:
            raise ValueError("שם המשתמש יכול להכיל עד 80 תווים")
        return normalized


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: str
    disabled_at: str | None


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

