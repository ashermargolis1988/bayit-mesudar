import sqlite3

from ..repositories import users as user_repository
from ..schemas import User, UserCreateInternal


class DuplicateEmailError(ValueError):
    pass


def create_user(payload: UserCreateInternal) -> User:
    values = payload.model_dump(mode="json")
    values["name"] = payload.name.strip()
    values["email"] = str(payload.email).strip().lower()
    try:
        row = user_repository.create_user(values)
    except sqlite3.IntegrityError as error:
        if "users.email" in str(error):
            raise DuplicateEmailError("כתובת הדוא״ל כבר רשומה") from error
        raise
    return User.model_validate(row)


def get_user(user_id: int) -> User | None:
    row = user_repository.get_user(user_id)
    return User.model_validate(row) if row is not None else None


def list_active_users() -> list[User]:
    return [User.model_validate(row) for row in user_repository.list_active_users()]
