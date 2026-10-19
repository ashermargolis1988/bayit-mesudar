from typing import Any

from ..repositories import tasks as task_repository
from ..schemas import TaskCreate, TaskUpdate


class EmptyUpdateError(ValueError):
    pass


def list_tasks(status_filter: str | None = None) -> list[dict[str, Any]]:
    return task_repository.list_tasks(status_filter)


def create_task(payload: TaskCreate) -> dict[str, Any]:
    values = payload.model_dump(mode="json")
    values["title"] = payload.title.strip()
    values["assignee"] = payload.assignee.strip() or "כולם"
    values["notes"] = payload.notes.strip()
    return task_repository.create_task(values)


def update_task(task_id: int, payload: TaskUpdate) -> dict[str, Any] | None:
    values = payload.model_dump(exclude_unset=True, mode="json")
    if not values:
        raise EmptyUpdateError("לא נשלחו שדות לעדכון")
    if values.get("title") is not None:
        values["title"] = values["title"].strip()
    if values.get("assignee") is not None:
        values["assignee"] = values["assignee"].strip() or "כולם"
    if values.get("notes") is not None:
        values["notes"] = values["notes"].strip()
    if values.get("status") == "done":
        values["completed_at"] = "CURRENT_TIMESTAMP"
    elif values.get("status") == "open":
        values["completed_at"] = None
    return task_repository.update_task(task_id, values)


def delete_task(task_id: int) -> bool:
    return task_repository.delete_task(task_id)

