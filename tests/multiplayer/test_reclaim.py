"""Tests for ``_reclaim_seat`` + ``_room_resume_message_for`` (Task 15).

Spec (multiplayer plan §6.4 / §5.2.8):

  - ``_reclaim_seat`` cancels any pending reconnect timer, restores the
    seat to a connected human (``is_ai=False``, ``websocket=ws``,
    principal kept/refreshed), sends a tailored ``room_resume`` to the
    reclaiming WS, broadcasts ``seat_reclaimed`` to every OTHER seat +
    spectator, and finally sets the seat's ``state_event`` so any phase
    awaiter wakes.
  - ``_room_resume_message_for(None)`` → spectator (TV) shape:
    ``your_position=None``, ``your_hand=None``, ``your_turn=None``.
  - ``_room_resume_message_for(position)`` → seat reclaim shape: includes
    the seat's own hand as a list of card codes, plus ``your_turn``
    derived from ``self._current_seat_turn``.
  - Common fields: phase, scores, operator (if a Spiel is in flight),
    variant block, ``trick_so_far`` snapshot, ``missed_tricks`` (last 3
    completed tricks), ``current_seat_turn``.
"""

import asyncio

import pytest

from Cards_refactored import Play
from ausbau.game_session import GameSession, hand_to_codes
from ausbau.room import RECONNECT_GRACE_SECONDS, Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket, seat_4_humans


pytestmark = pytest.mark.asyncio


def _fresh_session(host_pid: str = "guest:" + "a" * 32) -> GameSession:
    return GameSession(
        code="ABCDEF",
        host_principal_id=host_pid,
        variant=Variant(),
    )


# ────────────────────────────────────────────────────────────────────
# _reclaim_seat
# ────────────────────────────────────────────────────────────────────

async def test_reclaim_seat_cancels_pending_reconnect_task():
    """Disconnecting compn mid-game registers a reconnect timer.
    Reclaiming compn (with a fresh ws + same principal) must cancel and
    pop that timer."""
    s = _fresh_session()
    seat_4_humans(s)
    s.state = "playing"

    seat = s._seat("compn")
    original_principal = seat.principal

    await s._disconnect_seat("compn")
    assert "compn" in s._reconnect_tasks
    timer = s._reconnect_tasks["compn"]
    assert not timer.done()

    new_ws = FakeWebSocket()
    await s._reclaim_seat("compn", new_ws, original_principal)

    # Timer cancelled and removed from registry.
    assert "compn" not in s._reconnect_tasks
    # Wait for the cancelled timer to actually finish so the test loop is clean.
    try:
        await timer
    except asyncio.CancelledError:
        pass
    assert timer.cancelled() or timer.done()

    # Seat restored.
    assert seat.is_ai is False
    assert seat.websocket is new_ws
    assert seat.principal is original_principal
    assert seat.reconnect_deadline is None
    assert seat.connected_since is not None


async def test_reclaim_seat_after_ai_takeover_restores_human():
    """Simulate the FULL takeover path: 60 s timer fired → seat is AI,
    websocket=None, principal preserved. Reclaim must flip back to human
    and reattach the new ws without changing the principal."""
    s = _fresh_session()
    seat_4_humans(s)
    s.state = "playing"

    seat = s._seat("compn")
    original_principal = seat.principal
    # Mimic the post-timeout state.
    seat.is_ai = True
    seat.websocket = None
    seat.reconnect_deadline = None
    seat.connected_since = None

    new_ws = FakeWebSocket()
    await s._reclaim_seat("compn", new_ws, original_principal)

    assert seat.is_ai is False
    assert seat.websocket is new_ws
    assert seat.principal is original_principal


async def test_reclaim_sends_room_resume():
    """The reclaiming WS must receive exactly one `room_resume` whose
    shape matches the multi-seat protocol contract."""
    s = _fresh_session()
    seat_4_humans(s)
    s.state = "playing"
    s.point_sn = 80
    s.point_ow = 60

    seat = s._seat("compn")
    original_principal = seat.principal

    new_ws = FakeWebSocket()
    await s._reclaim_seat("compn", new_ws, original_principal)

    resumes = new_ws.all_sent_of_type("room_resume")
    assert len(resumes) == 1, f"expected 1 room_resume, got {len(resumes)}"
    msg = resumes[0]
    assert msg["your_position"] == "compn"
    # No Play in flight here → empty list (current_play is None).
    assert isinstance(msg["your_hand"], list)
    assert msg["scores"] == {"sn": 80, "ow": 60}
    assert msg["variant"] == {
        "trumpf_bock": False,
        "match_bonus": True,
        "stoeck": True,
    }
    assert msg["phase"] == "playing"
    assert msg["trick_so_far"] == []
    assert msg["missed_tricks"] == []
    # No turn currently tracked → your_turn=False, current_seat_turn=None.
    assert msg["your_turn"] is False
    assert msg["current_seat_turn"] is None


async def test_reclaim_broadcasts_seat_reclaimed_to_others():
    """Every OTHER seat + spectator gets `seat_reclaimed`; the reclaimer
    itself MUST NOT (it already received `room_resume`)."""
    s = _fresh_session()
    wss = seat_4_humans(s)
    s.state = "playing"

    seat = s._seat("compn")
    original_principal = seat.principal

    new_ws = FakeWebSocket()
    await s._reclaim_seat("compn", new_ws, original_principal)

    for pos in ("compo", "compe", "comps"):
        # The seat's old ws stays in the seat for the OTHER seats.
        evt = wss[pos].last_sent_of_type("seat_reclaimed")
        assert evt is not None, f"{pos} did not receive seat_reclaimed"
        assert evt["position"] == "compn"
        assert "display_name" in evt

    # The reclaiming WS receives the room_resume but NOT the
    # `seat_reclaimed` self-broadcast (except_seat="compn" filters it).
    assert new_ws.last_sent_of_type("seat_reclaimed") is None


async def test_reclaim_state_event_set():
    """A phase awaiter blocked on the disconnected seat (state_event
    cleared) must be released by `_reclaim_seat`."""
    s = _fresh_session()
    seat_4_humans(s)
    s.state = "playing"

    seat = s._seat("compn")
    original_principal = seat.principal

    seat.state_event.clear()
    waiter = asyncio.create_task(seat.state_event.wait())
    await asyncio.sleep(0)
    assert not waiter.done()

    new_ws = FakeWebSocket()
    await s._reclaim_seat("compn", new_ws, original_principal)

    await asyncio.wait_for(waiter, timeout=0.1)
    assert waiter.done()
    assert seat.state_event.is_set()


# ────────────────────────────────────────────────────────────────────
# _room_resume_message_for — spectator vs seat shape.
# ────────────────────────────────────────────────────────────────────

async def test_room_resume_for_spectator_has_null_your_position():
    """`_room_resume_message_for(None)` is the TV-mode payload: no
    position, no hand, no turn. Variant + scores + phase still present."""
    s = _fresh_session()
    s.state = "playing"
    s.current_play = Play(spiel=1)

    msg = s._room_resume_message_for(None)

    assert msg["type"] == "room_resume"
    assert msg["your_position"] is None
    assert msg["your_hand"] is None
    assert msg["your_turn"] is None
    assert msg["phase"] == "playing"
    assert msg["scores"] == {"sn": 0, "ow": 0}
    assert msg["variant"] == {
        "trumpf_bock": False,
        "match_bonus": True,
        "stoeck": True,
    }
    # Operator from current_play (Play(spiel=1) sets one via determine_trumpf).
    assert msg["operator"] == s.current_play.operator
    assert msg["trick_so_far"] == []
    assert msg["missed_tricks"] == []
    assert msg["current_seat_turn"] is None


async def test_room_resume_for_seat_includes_hand():
    """For a real seat with a live `Play`, `your_hand` is a non-empty
    list of card codes drawn from that seat's actual hand."""
    s = _fresh_session()
    s.state = "playing"
    play = Play(spiel=1)
    s.current_play = play

    msg = s._room_resume_message_for("comps")

    assert msg["your_position"] == "comps"
    assert isinstance(msg["your_hand"], list)
    assert len(msg["your_hand"]) > 0
    # All codes match what hand_to_codes would produce for that seat's
    # private hand — i.e. seats see only their own cards.
    assert msg["your_hand"] == hand_to_codes(play.comps)
    # No turn currently tracked.
    assert msg["your_turn"] is False


async def test_room_resume_includes_replay_buffer():
    """`missed_tricks` is the LAST 3 entries of `_completed_tricks`."""
    s = _fresh_session()
    s.state = "playing"
    s.current_play = Play(spiel=1)

    fake_tricks = [
        {
            "by": [f"compo:trick{i}", "compn:R6", "compe:RA", "comps:E9"],
            "winner_position": "compe",
            "points": i,
        }
        for i in range(5)
    ]
    s._completed_tricks.extend(fake_tricks)

    msg = s._room_resume_message_for("comps")

    assert len(msg["missed_tricks"]) == 3
    # Should be the LAST three (indices 2, 3, 4).
    assert msg["missed_tricks"] == fake_tricks[-3:]


async def test_room_resume_your_turn_true_when_seat_matches_current_turn():
    """`your_turn` is True iff `_current_seat_turn` matches the position
    we're building the message for."""
    s = _fresh_session()
    s.state = "playing"
    s.current_play = Play(spiel=1)
    s._current_seat_turn = "comps"

    msg_for_comps = s._room_resume_message_for("comps")
    assert msg_for_comps["your_turn"] is True
    assert msg_for_comps["current_seat_turn"] == "comps"

    msg_for_compn = s._room_resume_message_for("compn")
    assert msg_for_compn["your_turn"] is False
    assert msg_for_compn["current_seat_turn"] == "comps"

    msg_for_spec = s._room_resume_message_for(None)
    assert msg_for_spec["your_turn"] is None
    assert msg_for_spec["current_seat_turn"] == "comps"
