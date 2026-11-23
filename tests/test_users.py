import sqlite3

import pytest
from pydantic import ValidationError

from app import database
from app.repositories import users as user_repository
from app.schemas import UserCreateInternal
from app.services import users as user_service


@pytest.fixture(autouse=True)
def initialized_database() -> None:
    database.init_db()


def make_user(
    *,
    name: str = "משתמשת לדוגמה",
    email: str = "user@example.com",
    password_hash: str = "not-a-real-hash-yet",
) -> UserCreateInternal:
    return UserCreateInternal(name=name, email=email, password_hash=password_hash)


def test_create_user_normalizes_name_and_email_without_exposing_hash() -> None:
    user = user_service.create_user(
        make_user(name="  ישראלה ישראלי  ", email="  USER@Example.COM  ")
    )

    assert user.name == "ישראלה ישראלי"
    assert str(user.email) == "user@example.com"
    assert "password_hash" not in user.model_dump()

    stored = user_repository.get_user(user.id)
    assert stored is not None
    assert stored["password_hash"] == "not-a-real-hash-yet"


def test_email_lookup_is_case_insensitive() -> None:
    created = user_service.create_user(make_user(email="user@example.com"))

    found = user_repository.get_user_by_email("USER@EXAMPLE.COM")

    assert found is not None
    assert found["id"] == created.id


def test_duplicate_email_is_rejected_case_insensitively() -> None:
    user_service.create_user(make_user(email="user@example.com"))

    with pytest.raises(user_service.DuplicateEmailError, match="כבר רשומה"):
        user_service.create_user(make_user(email="USER@example.com"))


@pytest.mark.parametrize(
    ("name", "email"),
    [
        ("   ", "valid@example.com"),
        ("א" * 81, "valid@example.com"),
        ("שם תקין", "not-an-email"),
    ],
)
def test_invalid_user_data_is_rejected(name: str, email: str) -> None:
    with pytest.raises(ValidationError):
        make_user(name=name, email=email)


def test_list_active_users_excludes_disabled_users() -> None:
    active = user_service.create_user(make_user(name="פעיל", email="active@example.com"))
    disabled = user_service.create_user(
        make_user(name="מושבת", email="disabled@example.com")
    )
    with database.connection() as db:
        db.execute(
            "UPDATE users SET disabled_at = CURRENT_TIMESTAMP WHERE id = ?",
            (disabled.id,),
        )

    users = user_service.list_active_users()

    assert [user.id for user in users] == [active.id]


def test_database_rejects_blank_names_and_password_hashes() -> None:
    with pytest.raises(sqlite3.IntegrityError):
        user_repository.create_user(
            {"name": "   ", "email": "blank@example.com", "password_hash": "hash"}
        )
    with pytest.raises(sqlite3.IntegrityError):
        user_repository.create_user(
            {"name": "Valid", "email": "hash@example.com", "password_hash": ""}
        )
