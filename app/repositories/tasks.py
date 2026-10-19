from typing import Any

from ..database import connection, row_to_dict


def list_tasks(status_filter: str | None = None) -> list[dict[str, Any]]:
    query = "SELECT * FROM tasks"
    params: tuple[str, ...] = ()
    if status_filter in {"open", "done"}:
        query += " WHERE status = ?"
        params = (status_filter,)
    query += " ORDER BY status, due_date IS NULL, due_date, id DESC"
    with connection() as db:
        return [row_to_dict(row) for row in db.execute(query, params).fetchall()]


def create_task(values: dict[str, Any]) -> dict[str, Any]:
    with connection() as db:
        cursor = db.execute(
            """
            INSERT INTO tasks (title, assignee, due_date, frequency, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                values["title"],
                values["assignee"],
                values["due_date"],
                values["frequency"],
                values["notes"],
            ),
        )
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return row_to_dict(row)


def update_task(task_id: int, values: dict[str, Any]) -> dict[str, Any] | None:
    assignments: list[str] = []
    params: list[Any] = []
    for key, value in values.items():
        if key == "completed_at" and value == "CURRENT_TIMESTAMP":
            assignments.append("completed_at = CURRENT_TIMESTAMP")
        else:
            assignments.append(f"{key} = ?")
            params.append(value)
    params.append(task_id)

    with connection() as db:
        cursor = db.execute(
            f"UPDATE tasks SET {', '.join(assignments)} WHERE id = ?", params
        )
        if cursor.rowcount == 0:
            return None
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return row_to_dict(row)


def delete_task(task_id: int) -> bool:
    with connection() as db:
        cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0

