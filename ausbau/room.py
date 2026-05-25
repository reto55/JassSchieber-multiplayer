import asyncio
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from frontend.auth.guest import Guest
from frontend.auth.models import User

if TYPE_CHECKING:
    from ausbau.game_session import GameSession

logger = logging.getLogger(__name__)


POSITIONS = ('compo', 'compn', 'compe', 'comps')

# Module constants (from spec §2.4)
RECONNECT_GRACE_SECONDS = 60
SEAT_SWAP_REQUEST_TTL_SECONDS = 30
SPECTATOR_CAP_PER_ROOM = 20
REAPER_INTERVAL_SECONDS = 60
ROOM_FINISHED_LINGER_SECONDS = int(os.environ.get("SCHIEBER_ROOM_LINGER_SECONDS", "300"))
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
    ai_difficulty: str = "medium"              # one of: easy / medium / hard
    _strategy: Optional[object] = None         # AIStrategy | None; built on demand

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
    from ausbau.ai_strategies import make_strategy
    code = make_code()
    session = GameSession(
        code=code,
        host_principal_id=principal_id(host),
        variant=variant,
    )
    session.seats[0].principal = host
    session.seats[0].is_ai = False
    # Auto-AI seats 1-3 with default-medium strategy.
    for i in (1, 2, 3):
        seat = session.seats[i]
        seat._strategy = make_strategy(seat.ai_difficulty, seat.position)
    ROOMS[code] = session
    return session


def get_room(code: str):
    return ROOMS.get(code.upper())


def remove_room(code: str) -> None:
    ROOMS.pop(code, None)


async def _close_room(room) -> None:
    """Close all spectator WSs and cancel background tasks before removal.

    Module-private helper used by ``reap_rooms_once``. Best-effort: any
    individual failure (a WS already closed, a task already done) is
    swallowed so a single bad room cannot stall the reaper.
    """
    for spec in list(room.spectators):
        try:
            if spec.websocket is not None:
                await spec.websocket.close(code=1001, reason="room reaped")
        except Exception:
            pass
    # Cancel any outstanding reconnect / swap-TTL tasks.
    for task in list(getattr(room, "_reconnect_tasks", {}).values()):
        if task is not None and not task.done():
            task.cancel()
    for _key, (_expires, task) in list(getattr(room, "_swap_requests", {}).items()):
        if task is not None and not task.done():
            task.cancel()
    game_task = getattr(room, "_game_task", None)
    if game_task is not None and not game_task.done():
        game_task.cancel()


async def reap_rooms_once() -> list[str]:
    """Single reap pass over ``ROOMS``.

    Removes rooms in either of these states (spec §2.3):

      a) ``state == "finished"`` for >``ROOM_FINISHED_LINGER_SECONDS``
         seconds (since ``_finished_at``).
      b) zero connected humans AND zero seated humans for the same
         linger window (since ``_idle_since``).

    Reaped rooms have ``_close_room`` invoked first so spectator WSs and
    background tasks don't dangle. Returns the list of removed codes.

    Best-effort per room: any single-room exception is logged and the
    pass continues with the next code.
    """
    now = time.monotonic()
    removed: list[str] = []
    for code, room in list(ROOMS.items()):
        try:
            should_reap = False
            if room.state == "finished":
                finished_at = getattr(room, "_finished_at", None)
                if (
                    finished_at is not None
                    and (now - finished_at) > ROOM_FINISHED_LINGER_SECONDS
                ):
                    should_reap = True
            if not should_reap:
                idle_since = getattr(room, "_idle_since", None)
                if (
                    idle_since is not None
                    and (now - idle_since) > ROOM_FINISHED_LINGER_SECONDS
                ):
                    should_reap = True
            if not should_reap:
                continue
            await _close_room(room)
            ROOMS.pop(code, None)
            removed.append(code)
        except Exception:
            logger.exception("reaper: failure for room %s", code)
    return removed


async def reaper_loop() -> None:
    """Background task: invoke ``reap_rooms_once`` every interval.

    Runs forever until cancelled. Per-iteration exceptions are logged
    and the loop continues — a single bad iteration must not kill the
    reaper.
    """
    while True:
        await asyncio.sleep(REAPER_INTERVAL_SECONDS)
        try:
            # Look up the function via the module so tests that
            # ``monkeypatch.setattr(room_mod, "reap_rooms_once", ...)``
            # see their stub fire here.
            import ausbau.room as _self
            await _self.reap_rooms_once()
        except Exception:
            logger.exception("reaper iteration failed")


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
