import pytest
from ausbau.room import (
    Seat, Spectator, Variant, POSITIONS, principal_id,
    make_code, create_room, get_room, remove_room, ROOMS,
)
from frontend.auth.guest import Guest


def test_positions_layout():
    assert POSITIONS == ('compo', 'compn', 'compe', 'comps')


def test_variant_defaults():
    v = Variant()
    assert v.trumpf_bock is False
    assert v.match_bonus is True
    assert v.stoeck is True


def test_seat_default_is_ai():
    s = Seat(position='compo')
    assert s.is_ai is True
    assert s.principal is None
    assert s.websocket is None


def test_seat_display_name_for_ai():
    s = Seat(position='compn')
    assert s.display_name() == "AI (compn)"


def test_seat_display_name_for_guest():
    g = Guest(guest_id='aabbccdd' * 4)
    s = Seat(position='compe', principal=g, is_ai=False)
    assert s.display_name() == "Guest-aabb"


def test_make_code_format():
    code = make_code()
    assert len(code) == 6
    assert all(c in "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" for c in code)


def test_make_code_unique():
    seen = set()
    for _ in range(20):
        c = make_code()
        assert c not in seen
        seen.add(c)
        ROOMS[c] = None  # type: ignore   # reserve so make_code re-rolls


def test_principal_id_for_guest():
    g = Guest(guest_id='deadbeef' * 4)
    assert principal_id(g) == "guest:" + 'deadbeef' * 4


def test_create_room_assigns_host_to_seat_0():
    g = Guest(guest_id='abcd1234' * 4)
    session = create_room(host=g, variant=Variant())
    assert session.seats[0].principal is g
    assert session.seats[0].is_ai is False
    assert all(s.is_ai for s in session.seats[1:])
    assert session.host_principal_id == principal_id(g)
    assert get_room(session.code) is session


def test_remove_room():
    g = Guest(guest_id='abcd1234' * 4)
    session = create_room(host=g, variant=Variant())
    code = session.code
    remove_room(code)
    assert get_room(code) is None
