import asyncio
import secrets
import time
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from frontend.auth.guest import Guest
from frontend.auth.models import User

if TYPE_CHECKING:
    from ausbau.game_session import GameSession


POSITIONS = ('compo', 'compn', 'compe', 'comps')

# Module constants (from spec §2.4)
RECONNECT_GRACE_SECONDS = 60
SEAT_SWAP_REQUEST_TTL_SECONDS = 30
SPECTATOR_CAP_PER_ROOM = 20
REAPER_INTERVAL_SECONDS = 60
ROOM_FINISHED_LINGER_SECONDS = 300
REPLAY_BUFFER_TRICK_COUNT = 3

_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 0/O/1/I excluded


def principal_id(p) -> str:
    if isinstance(p, User):
        return str(p.id)
    if isinstance(p, Guest):
        return f"guest:{p.guest_id}"
    raise TypeError(f"unknown principal type: {type(p)}")


@dataclass(frozen=True)
class Variant:
    trumpf_bock: bool = False
    match_bonus: bool = True
    stoeck: bool = True


@dataclass
class Seat:
    position: str
    principal: Optional[object] = None         # User | Guest | None
    websocket: Optional[object] = None         # WebSocket | None
    is_ai: bool = True
    reconnect_deadline: Optional[float] = None
    connected_since: Optional[float] = None
    incoming: asyncio.Queue = field(default_factory=asyncio.Queue)
    state_event: asyncio.Event = field(default_factory=asyncio.Event)

    def display_name(self) -> str:
        if self.is_ai or self.principal is None:
            return f"AI ({self.position})"
        if isinstance(self.principal, User):
            return self.principal.username
        if isinstance(self.principal, Guest):
            return self.principal.display_name
        return self.position


@dataclass
class Spectator:
    principal: object         # User | Guest
    websocket: object         # WebSocket | None


# Global room registry (from spec §2.2)
ROOMS: dict[str, "GameSession"] = {}


def make_code() -> str:
    while True:
        code = ''.join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
        if code not in ROOMS:
            return code


def create_room(*, host, variant: Variant):
    """Create a room and register it. Host claims seat 0; seats 1-3 default to AI."""
    from ausbau.game_session import GameSession
    code = make_code()
    session = GameSession(
        code=code,
        host_principal_id=principal_id(host),
        variant=variant,
    )
    session.seats[0].principal = host
    session.seats[0].is_ai = False
    ROOMS[code] = session
    return session


def get_room(code: str):
    return ROOMS.get(code.upper())


def remove_room(code: str) -> None:
    ROOMS.pop(code, None)


def find_rooms_for_principal(p) -> list[dict]:
    pid = principal_id(p)
    out = []
    for room in ROOMS.values():
        for seat in room.seats:
            if seat.principal is not None and principal_id(seat.principal) == pid:
                out.append({
                    "code": room.code, "role": "seat",
                    "position": seat.position, "state": room.state,
                })
                break
        else:
            for spec in room.spectators:
                if principal_id(spec.principal) == pid:
                    out.append({
                        "code": room.code, "role": "spectator",
                        "state": room.state,
                    })
                    break
    return out
