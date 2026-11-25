import base64
import hashlib
import hmac
import os

from argon2 import PasswordHasher, extract_parameters
from argon2.exceptions import InvalidHashError, VerificationError

MIN_PASSWORD_LENGTH = 15
MAX_PASSWORD_LENGTH = 128


def _cost(name: str, default: int, maximum: int) -> int:
    value = int(os.getenv(name, str(default)))
    if not default <= value <= maximum:
        raise ValueError(f"{name} must be between {default} and {maximum}")
    return value


_HASHER = PasswordHasher(
    memory_cost=_cost("BAYIT_ARGON2_MEMORY_KIB", 65536, 262144),
    time_cost=_cost("BAYIT_ARGON2_TIME_COST", 3, 10),
    parallelism=4,
)


_ALGORITHM = "scrypt"
_VERSION = "v1"
_N = 2**14
_R = 8
_P = 1
_SALT_BYTES = 16
_KEY_BYTES = 32


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.b64decode(value + padding, altchars=b"-_", validate=True)


def hash_password(password: str) -> str:
    return _HASHER.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("$argon2id$"):
        try:
            params = extract_parameters(password_hash)
            if params.memory_cost > 262144 or params.time_cost > 10 or params.parallelism != 4:
                return False
            return _HASHER.verify(password_hash, password)
        except (InvalidHashError, VerificationError, ValueError):
            return False
    return _verify_scrypt(password, password_hash)


def password_needs_rehash(password_hash: str) -> bool:
    """Call only after successful verification of the stored hash."""
    return not password_hash.startswith("$argon2id$") or _HASHER.check_needs_rehash(password_hash)


def _verify_scrypt(password: str, password_hash: str) -> bool:
    try:
        algorithm, version, n, r, p, encoded_salt, encoded_key = password_hash.split("$")
        if (algorithm, version) != (_ALGORITHM, _VERSION):
            return False
        if (int(n), int(r), int(p)) != (_N, _R, _P):
            return False

        salt = _decode(encoded_salt)
        expected_key = _decode(encoded_key)
        if len(salt) != _SALT_BYTES or len(expected_key) != _KEY_BYTES:
            return False

        actual_key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=_N,
            r=_R,
            p=_P,
            dklen=_KEY_BYTES,
        )
    except (TypeError, ValueError):
        return False

    return hmac.compare_digest(actual_key, expected_key)
