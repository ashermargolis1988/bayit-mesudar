import base64
import hashlib
import hmac
import secrets


_ALGORITHM = "scrypt"
_VERSION = "v1"
_N = 2**14
_R = 8
_P = 1
_SALT_BYTES = 16
_KEY_BYTES = 32


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.b64decode(value + padding, altchars=b"-_", validate=True)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_SALT_BYTES)
    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_N,
        r=_R,
        p=_P,
        dklen=_KEY_BYTES,
    )
    return f"{_ALGORITHM}${_VERSION}${_N}${_R}${_P}${_encode(salt)}${_encode(derived_key)}"


def verify_password(password: str, password_hash: str) -> bool:
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
