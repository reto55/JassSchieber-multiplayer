import asyncio
import pytest
import pytest_asyncio

from ausbau.room import ROOMS
from frontend.auth.guest import Guest


@pytest.fixture(autouse=True)
def reset_rooms():
    """Clear the room registry before AND after every test."""
    ROOMS.clear()
    yield
    ROOMS.clear()


class FakeWebSocket:
    """Test double for FastAPI's WebSocket. Same surface as real WS."""

    def __init__(self):
        self.sent: list[dict] = []
        self.incoming: asyncio.Queue = asyncio.Queue()
        self.cookies: dict = {}
        self.closed = False
        self.close_code: int | None = None
        self.close_reason: str = ""

    async def accept(self) -> None:
        pass

    async def send_json(self, msg: dict) -> None:
        self.sent.append(msg)

    async def receive_json(self) -> dict:
        return await self.incoming.get()

    async def close(self, code: int = 1000, reason: str = "") -> None:
        self.closed = True
        self.close_code = code
        self.close_reason = reason

    # ─── Test-side helpers ─────────────────────────────────────────
    def push(self, msg: dict) -> None:
        """Queue an incoming message that the next receive_json() will return."""
        self.incoming.put_nowait(msg)

    def last_sent_of_type(self, t: str) -> dict | None:
        """Return the most recent sent message of a given type, or None."""
        return next((m for m in reversed(self.sent) if m.get("type") == t), None)

    def all_sent_of_type(self, t: str) -> list[dict]:
        return [m for m in self.sent if m.get("type") == t]


@pytest.fixture
def fake_ws():
    return FakeWebSocket()


def seat_4_humans(s) -> dict[str, "FakeWebSocket"]:
    """Seat all four positions of `s` with distinct guest principals + FakeWebSockets.

    Returns a dict mapping position → FakeWebSocket so tests can inspect each
    seat's message stream. Used by trump-phase / weis-phase / play-trick tests
    that need a fully-populated room.
    """
    wss: dict[str, FakeWebSocket] = {}
    for i, seat in enumerate(s.seats):
        seat.principal = Guest(guest_id=str(i) * 32)
        seat.is_ai = False
        seat.websocket = FakeWebSocket()
        wss[seat.position] = seat.websocket
    return wss


@pytest.fixture
def fast_clock(monkeypatch):
    """Patch asyncio.sleep so 60 s timer-based tests run in <1 ms.

    Caveat: any asyncio.sleep(N) inside the test body returns after one
    event-loop tick. Tests that rely on REAL elapsed time should not use
    this fixture.
    """
    real_sleep = asyncio.sleep

    async def fake_sleep(seconds: float) -> None:
        await real_sleep(0)

    monkeypatch.setattr("asyncio.sleep", fake_sleep)
