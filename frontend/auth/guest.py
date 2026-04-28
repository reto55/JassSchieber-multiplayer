import secrets
from dataclasses import dataclass
from itsdangerous import URLSafeSerializer, BadSignature


class GuestCookieError(ValueError):
    pass


@dataclass(frozen=True)
class Guest:
    guest_id: str  # 32 hex chars (16 bytes)

    @property
    def display_name(self) -> str:
        return f"Guest-{self.guest_id[:4]}"


def _serializer(secret: str) -> URLSafeSerializer:
    return URLSafeSerializer(secret, salt="schieber-guest")


def issue_guest_cookie(secret: str) -> tuple[str, Guest]:
    guest = Guest(guest_id=secrets.token_hex(16))
    return _serializer(secret).dumps({"id": guest.guest_id}), guest


def read_guest_cookie(cookie_value: str, secret: str) -> Guest:
    try:
        payload = _serializer(secret).loads(cookie_value)
    except BadSignature as e:
        raise GuestCookieError(str(e))
    if not isinstance(payload, dict) or "id" not in payload:
        raise GuestCookieError("malformed payload")
    gid = payload["id"]
    if not (isinstance(gid, str) and len(gid) == 32):
        raise GuestCookieError("malformed id")
    return Guest(guest_id=gid)
