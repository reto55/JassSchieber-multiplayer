from pathlib import Path
from functools import lru_cache


class PasswordError(ValueError):
    pass


_BLOCKLIST_PATH = Path(__file__).parent / "data" / "common-passwords.txt"


@lru_cache(maxsize=1)
def _blocklist() -> frozenset[str]:
    if not _BLOCKLIST_PATH.exists():
        return frozenset()
    with _BLOCKLIST_PATH.open() as f:
        return frozenset(line.strip().lower() for line in f if line.strip())


def validate_password(password: str, *, username: str, email: str) -> None:
    if len(password) < 10:
        raise PasswordError("password must be at least 10 characters")

    pw_lower = password.lower()
    if pw_lower in _blocklist():
        raise PasswordError("password is too common")

    if username and username.lower() in pw_lower:
        raise PasswordError("password must not contain your username")

    local = email.split("@", 1)[0].lower() if email else ""
    if local and local in pw_lower:
        raise PasswordError("password must not contain your email")
