from typing import Any

from ..database import connection, row_to_dict


def create_user(values: dict[str, Any]) -> dict[str, Any]:
    with connection() as db:
        cursor = db.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (values["name"], values["email"], values["password_hash"]),
        )
        row = db.execute(
            "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return row_to_dict(row)


def get_user(user_id: int) -> dict[str, Any] | None:
    with connection() as db:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return row_to_dict(row) if row is not None else None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with connection() as db:
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return row_to_dict(row) if row is not None else None


def list_active_users() -> list[dict[str, Any]]:
    with connection() as db:
        rows = db.execute(
            """
            SELECT * FROM users
            WHERE disabled_at IS NULL
            ORDER BY name COLLATE NOCASE, id
            """
        ).fetchall()
        return [row_to_dict(row) for row in rows]
