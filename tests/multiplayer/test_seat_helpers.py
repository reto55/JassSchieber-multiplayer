import pytest
from ausbau.game_session import GameSession
from ausbau.room import Variant
from frontend.auth.guest import Guest


def test_seat_by_position():
    g = Guest(guest_id='a' * 32)
    s = GameSession(code="ABCDEF", host_principal_id=f"guest:{g.guest_id}", variant=Variant())
    s.seats[0].principal = g
    s.seats[0].is_ai = False
    seat = s._seat("compo")
    assert seat is s.seats[0]


def test_seat_by_position_invalid():
    s = GameSession(code="ABCDEF", host_principal_id="guest:x", variant=Variant())
    with pytest.raises(KeyError):
        s._seat("nope")


def test_seat_for_principal_finds_existing():
    g = Guest(guest_id='b' * 32)
    s = GameSession(code="ABCDEF", host_principal_id=f"guest:{g.guest_id}", variant=Variant())
    s.seats[2].principal = g
    s.seats[2].is_ai = False
    seat = s._seat_for_principal(g)
    assert seat is s.seats[2]


def test_seat_for_principal_none_when_absent():
    g = Guest(guest_id='c' * 32)
    s = GameSession(code="ABCDEF", host_principal_id="guest:other", variant=Variant())
    assert s._seat_for_principal(g) is None
