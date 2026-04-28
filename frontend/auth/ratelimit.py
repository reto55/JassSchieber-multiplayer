from slowapi import Limiter
from slowapi.util import get_remote_address


def make_limiter() -> Limiter:
    return Limiter(key_func=get_remote_address)


# Per spec §6.2; values reused as decorator args
LIMITS = {
    "signup": "5/hour",
    "login": "20/15minute",
    "forgot": "3/minute",
    "forgot_day": "10/day",
    "resend_verification": "5/day",
    "reset": "10/hour",
    "change_password": "10/hour",
    "change_email": "5/day",
    "whoami": "30/minute",
    "admin": "60/minute",
}
