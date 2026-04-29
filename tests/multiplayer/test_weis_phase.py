"""Tests for the multi-seat `_weis_phase` (Task 11).

Per `schieber-protocol` skill §weis_request / weis_resolution:
  - `weis_request` is sent per-seat with ONLY that seat's eligible weis
    (`your_weis`). Seats with no weis still receive the prompt with
    `your_weis: []`.
  - Seats reply with `{"type": "announce_weis", "announce": bool, "weis": ...}`.
  - The server then broadcasts `weis_resolution` containing
    `weis_by_position` (only seats that announced) and `winning_team`.

Per-seat redaction is the load-bearing invariant: a seat's `weis_request`
must NEVER reveal another seat's weis.
"""
from unittest.mock import patch

import pytest

from Cards_refactored import SUITS
from ausbau.game_session import GameSession
from ausbau.room import Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import seat_4_humans


pytestmark = pytest.mark.asyncio


def _empty_hand():
    return {suit: [] for suit in SUITS}


class FakePlay:
    """Minimal stand-in for Cards_refactored.Play in weis_phase tests.

    The real `Play` deals real cards, but tests want determinism — we
    monkeypatch `describe_weis` upstream so eligible-weis are picked
    seat-by-seat. Hands are empty dicts (one per suit) so the real
    `wiis` / `wiis_gleiche` don't crash on missing keys.
    """
    def __init__(self):
        self.comps = _empty_hand()
        self.compn = _empty_hand()
        self.compo = _empty_hand()
        self.compe = _empty_hand()


def _fresh_session():
    g = Guest(guest_id='a' * 32)
    return GameSession(
        code="A",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(),
    )


def _describe_weis_per_position(weis_by_position):
    """Build a `describe_weis` side-effect that returns position-specific lists.

    `_weis_phase` calls `describe_weis(wiis(hand), wiis_gleiche(hand))` four
    times, once per seat in the order `PLAYERS` defines
    (`comps, compo, compn, compe`). We rely on that iteration order to
    map calls back to positions deterministically.
    """
    from ausbau.game_session import PLAYERS

    def factory(play):
        seen = {"calls": 0}

        def _impl(*_args, **_kwargs):
            pos = PLAYERS[seen["calls"]]
            seen["calls"] += 1
            return weis_by_position.get(pos, [])

        return _impl
    return factory


async def test_weis_request_per_seat_only_own_weis():
    """Each seat's `weis_request` carries only that seat's `your_weis`."""
    s = _fresh_session()
    wss = seat_4_humans(s)
    play = FakePlay()

    dreier = {"name": "Dreier", "suit": "Eicheln", "points": 20}
    weis_by_pos = {
        "compo": [dreier],
        "compn": [],
        "compe": [],
        "comps": [],
    }

    # Each seat will reply with announce=False to keep this test focused on
    # the request shape. We pre-load all four queues.
    for pos in ("compo", "compn", "compe", "comps"):
        s._seat(pos).incoming.put_nowait({"type": "announce_weis", "announce": False})

    factory = _describe_weis_per_position(weis_by_pos)
    with patch("ausbau.game_session.describe_weis", side_effect=factory(play)):
        await s._weis_phase(play)

    for pos, expected in weis_by_pos.items():
        req = wss[pos].last_sent_of_type("weis_request")
        assert req is not None, f"{pos} did not receive weis_request"
        assert req["your_weis"] == expected, (
            f"{pos} weis_request leaked or omitted weis: {req}"
        )

    # Per-seat redaction: compo's Dreier must NOT appear in any other seat's request
    for pos in ("compn", "compe", "comps"):
        req = wss[pos].last_sent_of_type("weis_request")
        assert req["your_weis"] == [], (
            f"{pos} received compo's weis (leak): {req}"
        )


async def test_weis_resolution_broadcasts_to_all():
    """`weis_resolution` reaches every seat with full `weis_by_position`."""
    s = _fresh_session()
    wss = seat_4_humans(s)
    play = FakePlay()

    dreier = {"name": "Dreier", "suit": "Eicheln", "points": 20}
    weis_by_pos = {
        "compo": [dreier],
        "compn": [],
        "compe": [],
        "comps": [],
    }

    # compo announces; others auto-decline (no weis to announce anyway)
    s._seat("compo").incoming.put_nowait(
        {"type": "announce_weis", "announce": True, "weis": ["Dreier"]}
    )
    for pos in ("compn", "compe", "comps"):
        s._seat(pos).incoming.put_nowait({"type": "announce_weis", "announce": False})

    factory = _describe_weis_per_position(weis_by_pos)
    with patch("ausbau.game_session.describe_weis", side_effect=factory(play)):
        await s._weis_phase(play)

    for pos in ("compo", "compn", "compe", "comps"):
        res = wss[pos].last_sent_of_type("weis_resolution")
        assert res is not None, f"{pos} did not receive weis_resolution"
        assert res["winning_team"] == "ow", res
        assert res["weis_by_position"] == {"compo": [dreier]}, res

    # compo is OW team — score should reflect the 20-pt Dreier.
    assert s.point_ow == 20
    assert s.point_sn == 0


async def test_weis_decline():
    """A seat replying `announce=False` is excluded from `weis_by_position`."""
    s = _fresh_session()
    wss = seat_4_humans(s)
    play = FakePlay()

    dreier = {"name": "Dreier", "suit": "Eicheln", "points": 20}
    vierter = {"name": "Vierter", "suit": "Rosen", "points": 50}
    weis_by_pos = {
        "compo": [dreier],
        "compn": [vierter],
        "compe": [],
        "comps": [],
    }

    # compo announces, compn declines (despite having weis), others decline.
    s._seat("compo").incoming.put_nowait(
        {"type": "announce_weis", "announce": True, "weis": ["Dreier"]}
    )
    s._seat("compn").incoming.put_nowait({"type": "announce_weis", "announce": False})
    s._seat("compe").incoming.put_nowait({"type": "announce_weis", "announce": False})
    s._seat("comps").incoming.put_nowait({"type": "announce_weis", "announce": False})

    factory = _describe_weis_per_position(weis_by_pos)
    with patch("ausbau.game_session.describe_weis", side_effect=factory(play)):
        await s._weis_phase(play)

    res = wss["compo"].last_sent_of_type("weis_resolution")
    assert "compn" not in res["weis_by_position"], (
        f"compn declined but appears in weis_by_position: {res}"
    )
    assert res["weis_by_position"] == {"compo": [dreier]}
    # Only OW (compo) scored.
    assert s.point_ow == 20
    assert s.point_sn == 0
