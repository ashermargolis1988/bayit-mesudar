import base64
import hashlib

import pytest

from app.security import hash_password, password_needs_rehash, verify_password


@pytest.fixture(scope="module")
def password_hash() -> str:
    return hash_password("סיסמה חזקה 123!")


def test_hash_password_does_not_store_plaintext(password_hash: str) -> None:
    assert "סיסמה חזקה 123!" not in password_hash
    assert password_hash.startswith("$argon2id$")
    assert not password_needs_rehash(password_hash)


def test_verify_password_accepts_correct_password(password_hash: str) -> None:
    assert verify_password("סיסמה חזקה 123!", password_hash) is True


def test_legacy_scrypt_hash_can_be_verified_and_upgraded() -> None:
    password = "סיסמה ישנה"
    salt = b"0123456789abcdef"
    key = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
    encoded_salt, encoded_key = [
        base64.urlsafe_b64encode(value).decode().rstrip("=") for value in (salt, key)
    ]
    legacy = f"scrypt$v1$16384$8$1${encoded_salt}${encoded_key}"
    assert verify_password(password, legacy)
    assert not verify_password("wrong", legacy)
    assert password_needs_rehash(legacy)


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
        "$argon2id$malformed",
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
