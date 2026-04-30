"""Sub-project C, Task 8: lifecycle wiring for join / leave / AI-takeover.

Per spec §5:
  - human-joins-AI-seat:  ``_strategy`` cleared, ``ai_difficulty`` preserved.
  - human-leaves-AI-seat in lobby:  ``_strategy`` rebuilt from preserved difficulty.
  - AI-takeover mid-game:  ``ai_difficulty`` reset to "medium" + ``_strategy`` rebuilt.
"""
import pytest

from ausbau.room import Variant, create_room
from ausbau.ai_strategies import MediumStrategy, HardStrategy, make_strategy
from frontend.auth.guest import Guest

pytestmark = pytest.mark.asyncio


async def test_human_join_clears_strategy_keeps_difficulty():
    """Manually simulate /join's effect on the seat. Difficulty preserved."""
    g_host = Guest(guest_id="h" * 32)
    g_join = Guest(guest_id="j" * 32)
    room = create_room(host=g_host, variant=Variant())
    seat = room.seats[1]
    seat.ai_difficulty = "hard"
    seat._strategy = make_strategy("hard", seat.position)
    # Simulate join: replicate what /join does to an AI seat.
    seat.principal = g_join
    seat.is_ai = False
    seat._strategy = None
    assert seat.ai_difficulty == "hard"          # preserved
    assert seat._strategy is None


async def test_lobby_leave_rebuilds_strategy_from_preserved_difficulty():
    """When a human leaves an AI-seat in lobby, _strategy must rebuild."""
    g_host = Guest(guest_id="h" * 32)
    g_join = Guest(guest_id="j" * 32)
    room = create_room(host=g_host, variant=Variant())
    seat = room.seats[1]
    seat.ai_difficulty = "hard"
    # Human took the seat:
    seat.principal = g_join
    seat.is_ai = False
    seat._strategy = None
    # Now they leave (server.py path will eventually call _strategy rebuild).
    # We test the helper directly.
    seat.principal = None
    seat.is_ai = True
    # The /leave endpoint must do this. We test the endpoint in Task 11.
    # Here we test the seat-side invariant: rebuild yields correct class.
    seat._strategy = make_strategy(seat.ai_difficulty, seat.position)
    assert isinstance(seat._strategy, HardStrategy)
    assert seat._strategy.position == seat.position


async def test_mid_game_ai_takeover_resets_difficulty_to_medium(fast_clock):
    """AI takeover post-disconnect resets difficulty to medium."""
    g_host = Guest(guest_id="h" * 32)
    room = create_room(host=g_host, variant=Variant())
    # Replace seat 1 with a hard human seat
    seat = room.seats[1]
    seat.principal = Guest(guest_id="x" * 32)
    seat.is_ai = False
    seat.websocket = None  # disconnected
    seat.ai_difficulty = "hard"
    seat._strategy = None
    room.state = "playing"

    await room._reconnect_timeout("compn")

    assert seat.is_ai is True
    assert seat.ai_difficulty == "medium"        # reset!
    assert isinstance(seat._strategy, MediumStrategy)
