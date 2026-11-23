import pytest

from app.security import hash_password, verify_password


@pytest.fixture(scope="module")
def password_hash() -> str:
    return hash_password("סיסמה חזקה 123!")


def test_hash_password_does_not_store_plaintext(password_hash: str) -> None:
    assert "סיסמה חזקה 123!" not in password_hash
    assert password_hash.startswith("scrypt$v1$")


def test_verify_password_accepts_correct_password(password_hash: str) -> None:
    assert verify_password("סיסמה חזקה 123!", password_hash) is True


def test_verify_password_rejects_wrong_password(password_hash: str) -> None:
    assert verify_password("סיסמה אחרת", password_hash) is False


def test_same_password_gets_a_different_salt() -> None:
    first = hash_password("same password")
    second = hash_password("same password")

    assert first != second
    assert verify_password("same password", first) is True
    assert verify_password("same password", second) is True


@pytest.mark.parametrize(
    "invalid_hash",
    [
        "",
        "not-a-password-hash",
        "bcrypt$v1$16384$8$1$c2FsdA$a2V5",
        "scrypt$v2$16384$8$1$c2FsdA$a2V5",
        "scrypt$v1$999999999$8$1$c2FsdA$a2V5",
        "scrypt$v1$16384$8$1$%%%$%%%",
    ],
)
def test_verify_password_rejects_malformed_or_unsupported_hashes(
    invalid_hash: str,
) -> None:
    assert verify_password("password", invalid_hash) is False
