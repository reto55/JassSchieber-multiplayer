import asyncio
import pytest
from ausbau.game_session import GameSession
from ausbau.room import Variant
from ausbau.ai_strategies import make_strategy
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket, seat_4_humans

pytestmark = pytest.mark.asyncio


async def _human_responder(seat, ws, log):
    """Same pattern as test_e2e_4_humans.py."""
    last_seen = 0
    while True:
        if len(ws.sent) > last_seen:
            new_msgs = ws.sent[last_seen:]
            last_seen = len(ws.sent)
            for msg in new_msgs:
                t = msg.get("type")
                log.append(t)
                if t == "trump_request":
                    seat.incoming.put_nowait({
                        "type": "choose_trump",
                        "operator": "Eicheln",
                    })
                elif t == "weis_request":
                    seat.incoming.put_nowait({"type": "announce_weis", "announce": False})
                elif t == "play_request":
                    valid = msg.get("valid_cards") or []
                    if valid:
                        seat.incoming.put_nowait({"type": "play_card", "card": valid[0]})
                elif t == "game_end":
                    return
        await asyncio.sleep(0)


async def test_e2e_mixed_difficulty_3_ai(fast_clock):
    """1 human (compo) + 3 AIs at easy/medium/hard. Verify game completes."""
    g = Guest(guest_id="h" * 32)
    s = GameSession(
        code="MIXAI",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(),
        end_game=200,
    )
    # Seat 0 = human (compo); seats 1-3 = AI with mixed levels.
    s.seats[0].principal = g
    s.seats[0].is_ai = False
    s.seats[0].websocket = FakeWebSocket()
    s.seats[1].ai_difficulty = "easy"
    s.seats[1]._strategy = make_strategy("easy", s.seats[1].position)
    s.seats[2].ai_difficulty = "medium"
    s.seats[2]._strategy = make_strategy("medium", s.seats[2].position)
    s.seats[3].ai_difficulty = "hard"
    s.seats[3]._strategy = make_strategy("hard", s.seats[3].position)

    log = []
    responder = asyncio.create_task(
        _human_responder(s.seats[0], s.seats[0].websocket, log)
    )
    game = asyncio.create_task(s.start_game())

    try:
        await asyncio.wait_for(game, timeout=10.0)
    except asyncio.TimeoutError:
        pytest.fail(f"game didn't finish in 10s; log: {log}")
    finally:
        responder.cancel()

    assert s.state == "finished"
    assert s.seats[0].websocket.last_sent_of_type("game_end") is not None
    # All 3 AI strategies must have been consulted at least once.
    # We can't directly assert that here, but on_spiel_start populated
    # HardStrategy memory:
    assert s.seats[3]._strategy._remaining_by_suit  # non-empty after spiel start
