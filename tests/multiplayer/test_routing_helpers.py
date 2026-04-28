import pytest
from ausbau.game_session import GameSession
from ausbau.room import Variant, Spectator
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket


pytestmark = pytest.mark.asyncio


async def test_send_to_seat_human(fake_ws):
    g = Guest(guest_id='h' * 32)
    s = GameSession(code="A", host_principal_id=f"guest:{g.guest_id}", variant=Variant())
    s.seats[1].principal = g
    s.seats[1].is_ai = False
    s.seats[1].websocket = fake_ws
    await s.send_to_seat("compn", {"type": "hi"})
    assert fake_ws.last_sent_of_type("hi") == {"type": "hi"}


async def test_send_to_seat_ai_is_noop(fake_ws):
    s = GameSession(code="A", host_principal_id="guest:x", variant=Variant())
    # seat 1 is AI by default; websocket=None
    await s.send_to_seat("compn", {"type": "hi"})
    assert fake_ws.sent == []


async def test_broadcast_to_all_seats():
    s = GameSession(code="A", host_principal_id="guest:x", variant=Variant())
    wss = []
    for i, seat in enumerate(s.seats):
        seat.principal = Guest(guest_id=f"{i}" * 32)
        seat.is_ai = False
        seat.websocket = FakeWebSocket()
        wss.append(seat.websocket)
    await s.broadcast({"type": "card_played", "card": "EA"})
    for ws in wss:
        assert ws.last_sent_of_type("card_played") is not None


async def test_broadcast_except_seat():
    s = GameSession(code="A", host_principal_id="guest:x", variant=Variant())
    wss = {}
    for i, seat in enumerate(s.seats):
        seat.principal = Guest(guest_id=f"{i}" * 32)
        seat.is_ai = False
        seat.websocket = FakeWebSocket()
        wss[seat.position] = seat.websocket
    await s.broadcast({"type": "x"}, except_seat="compn")
    assert wss["compn"].last_sent_of_type("x") is None
    assert wss["compo"].last_sent_of_type("x") is not None


async def test_broadcast_to_spectators():
    s = GameSession(code="A", host_principal_id="guest:x", variant=Variant())
    spec_ws = FakeWebSocket()
    s.spectators.append(Spectator(principal=Guest(guest_id='s' * 32), websocket=spec_ws))
    await s.broadcast({"type": "y"})
    assert spec_ws.last_sent_of_type("y") is not None


async def test_broadcast_per_seat_factory():
    s = GameSession(code="A", host_principal_id="guest:x", variant=Variant())
    wss = {}
    for i, seat in enumerate(s.seats):
        seat.principal = Guest(guest_id=f"{i}" * 32)
        seat.is_ai = False
        seat.websocket = FakeWebSocket()
        wss[seat.position] = seat.websocket

    def factory(seat):
        return {"type": "x", "for_position": seat.position if seat else None}

    await s.broadcast_per_seat(factory)
    for pos, ws in wss.items():
        sent = ws.last_sent_of_type("x")
        assert sent["for_position"] == pos
