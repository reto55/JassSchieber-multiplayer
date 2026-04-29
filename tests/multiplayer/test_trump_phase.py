import pytest
from ausbau.game_session import GameSession
from ausbau.room import Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket


pytestmark = pytest.mark.asyncio


class FakePlay:
    """Bare-minimum stand-in for Cards_refactored.Play in trump_phase tests."""
    def __init__(self, first="compo"):
        self.first = first
        self.operator = None


def _seat_4_humans(s):
    wss = {}
    for i, seat in enumerate(s.seats):
        seat.principal = Guest(guest_id=str(i) * 32)
        seat.is_ai = False
        seat.websocket = FakeWebSocket()
        wss[seat.position] = seat.websocket
    return wss


async def test_trump_phase_human_picks_eicheln():
    g = Guest(guest_id='a' * 32)
    s = GameSession(code="A", host_principal_id=f"guest:{g.guest_id}", variant=Variant())
    wss = _seat_4_humans(s)
    play = FakePlay(first="compo")

    s._seat("compo").incoming.put_nowait({"type": "choose_trump", "operator": "Eicheln"})
    await s._trump_phase(play)

    for ws in wss.values():
        chosen = ws.last_sent_of_type("trump_chosen")
        assert chosen is not None
        assert chosen["operator"] == "Eicheln"
        assert chosen["by_position"] == "compo"

    assert play.operator == "Eicheln"

    # only the lead got trump_request
    assert wss["compo"].last_sent_of_type("trump_request") is not None
    for pos in ("compn", "compe", "comps"):
        assert wss[pos].last_sent_of_type("trump_request") is None
        assert wss[pos].last_sent_of_type("trump_pending") is not None


async def test_trump_phase_schieben_transfers_to_partner():
    g = Guest(guest_id='a' * 32)
    s = GameSession(code="A", host_principal_id=f"guest:{g.guest_id}", variant=Variant())
    wss = _seat_4_humans(s)
    play = FakePlay(first="compo")

    s._seat("compo").incoming.put_nowait({"type": "schieben"})
    s._seat("compe").incoming.put_nowait({"type": "choose_trump", "operator": "Rosen"})

    await s._trump_phase(play)

    assert play.operator == "Rosen"
    chosen = wss["compo"].last_sent_of_type("trump_chosen")
    assert chosen["by_position"] == "compe"
    assert chosen["operator"] == "Rosen"

    # partner got 2nd trump_request with schieben_allowed=false
    e_reqs = wss["compe"].all_sent_of_type("trump_request")
    assert any(r.get("schieben_allowed") is False for r in e_reqs)
