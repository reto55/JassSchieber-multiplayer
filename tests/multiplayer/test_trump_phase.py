import pytest
from ausbau.game_session import GameSession
from ausbau.room import Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket, seat_4_humans


pytestmark = pytest.mark.asyncio


class FakePlay:
    """Bare-minimum stand-in for Cards_refactored.Play in trump_phase tests."""
    def __init__(self, first="compo"):
        self.first = first
        self.operator = None


async def test_trump_phase_human_picks_eicheln():
    g = Guest(guest_id='a' * 32)
    s = GameSession(code="A", host_principal_id=f"guest:{g.guest_id}", variant=Variant())
    wss = seat_4_humans(s)
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
    wss = seat_4_humans(s)
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


async def test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state():
    """Garbage `type` must be rejected with `error` and re-prompt the SAME seat.

    Crucially: after a `schieben` has happened the partner is now `target`.
    A garbage message from the partner must NOT bounce control back to the
    original lead, and must NOT re-allow schieben (single-pass per round).
    """
    g = Guest(guest_id='a' * 32)
    s = GameSession(code="A", host_principal_id=f"guest:{g.guest_id}", variant=Variant())
    wss = seat_4_humans(s)
    play = FakePlay(first="compo")

    # Lead schiebs; partner first sends garbage, then a valid choose_trump.
    s._seat("compo").incoming.put_nowait({"type": "schieben"})
    s._seat("compe").incoming.put_nowait({"type": "garbage", "operator": "Eicheln"})
    s._seat("compe").incoming.put_nowait({"type": "choose_trump", "operator": "Schellen"})

    await s._trump_phase(play)

    # Final outcome: partner chose Schellen.
    assert play.operator == "Schellen"
    chosen = wss["compo"].last_sent_of_type("trump_chosen")
    assert chosen["by_position"] == "compe"
    assert chosen["operator"] == "Schellen"

    # Partner received an error reply for the garbage message.
    errors = wss["compe"].all_sent_of_type("error")
    assert any("invalid action" in e.get("message", "") for e in errors)

    # Partner was re-prompted with schieben_allowed=False (no state regression).
    e_reqs = wss["compe"].all_sent_of_type("trump_request")
    assert len(e_reqs) >= 2  # initial post-schieben prompt + re-prompt after error
    assert all(r.get("schieben_allowed") is False for r in e_reqs)

    # Original lead must NOT have been re-prompted — only the initial one.
    o_reqs = wss["compo"].all_sent_of_type("trump_request")
    assert len(o_reqs) == 1
    assert o_reqs[0].get("schieben_allowed") is True


async def test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state():
    """An operator outside TRUMP_OPTIONS must re-prompt without resetting schieben."""
    g = Guest(guest_id='a' * 32)
    s = GameSession(code="A", host_principal_id=f"guest:{g.guest_id}", variant=Variant())
    wss = seat_4_humans(s)
    play = FakePlay(first="compo")

    s._seat("compo").incoming.put_nowait({"type": "schieben"})
    s._seat("compe").incoming.put_nowait({"type": "choose_trump", "operator": "Bogus"})
    s._seat("compe").incoming.put_nowait({"type": "choose_trump", "operator": "Oben"})

    await s._trump_phase(play)

    assert play.operator == "Oben"
    errors = wss["compe"].all_sent_of_type("error")
    assert any("invalid trump" in e.get("message", "") for e in errors)
    # Partner must NOT regain schieben after an error.
    e_reqs = wss["compe"].all_sent_of_type("trump_request")
    assert all(r.get("schieben_allowed") is False for r in e_reqs)
