"""Tests for ``_disconnect_seat`` + ``_reconnect_timeout`` (Task 14).

Spec (multiplayer plan §6.2 / §6.3):

  - ``_disconnect_seat`` is idempotent for AI / already-disconnected seats.
  - In ``lobby``: drop seat to AI immediately (no grace), broadcast
    ``seat_changed`` with ``reason="disconnect"``. If the disconnecting
    seat was host, transfer host.
  - Mid-game: 60-second grace via ``_reconnect_timeout``, broadcast
    ``seat_paused``, set ``state_event`` to wake any phase awaiter.
  - ``_reconnect_timeout`` flips the seat to AI but KEEPS ``principal``
    so the original human can reclaim. If the timed-out seat was host,
    transfer host.
  - If the seat reclaimed before the timer fires (``websocket`` is back),
    ``_reconnect_timeout`` is a no-op.
"""

import asyncio

import pytest

from ausbau.game_session import GameSession
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
# Lobby disconnects: immediate AI drop, no timer.
# ────────────────────────────────────────────────────────────────────

async def test_disconnect_in_lobby_drops_to_ai_immediately():
    s = _fresh_session()
    wss = seat_4_humans(s)
    # State stays "lobby" by default.
    assert s.state == "lobby"

    target_ws = wss["compn"]
    target_seat = s._seat("compn")
    target_principal = target_seat.principal
    assert target_principal is not None

    await s._disconnect_seat("compn")

    # Seat flipped to AI, principal cleared, ws closed and dropped.
    assert target_seat.is_ai is True
    assert target_seat.principal is None
    assert target_seat.websocket is None
    assert target_seat.reconnect_deadline is None
    assert target_seat.connected_since is None
    assert target_ws.closed is True

    # No reconnect timer registered (lobby has no grace).
    assert "compn" not in s._reconnect_tasks

    # The OTHER seats received a `seat_changed` broadcast with
    # reason="disconnect" and a payload reflecting the new AI state.
    for pos in ("compo", "compe", "comps"):
        evt = wss[pos].last_sent_of_type("seat_changed")
        assert evt is not None, f"{pos} did not receive seat_changed"
        assert evt["reason"] == "disconnect"
        assert evt["seat"]["position"] == "compn"
        assert evt["seat"]["is_ai"] is True
        assert evt["seat"]["principal_id"] is None


async def test_disconnect_in_lobby_host_triggers_transfer():
    """Host (compo) disconnects in lobby → host is transferred to the
    next-oldest connected human (compn here)."""
    host_guest = Guest(guest_id="0" * 32)
    s = GameSession(
        code="ABCDEF",
        host_principal_id=f"guest:{host_guest.guest_id}",
        variant=Variant(),
    )
    # Seat compo as host human, compn as another human, others stay AI.
    s.seats[0].principal = host_guest
    s.seats[0].is_ai = False
    s.seats[0].websocket = FakeWebSocket()
    s.seats[0].connected_since = 1.0  # for _transfer_host candidate sort

    other_guest = Guest(guest_id="1" * 32)
    s.seats[1].principal = other_guest
    s.seats[1].is_ai = False
    s.seats[1].websocket = FakeWebSocket()
    s.seats[1].connected_since = 2.0

    # seats[2] and seats[3] stay default AI.
    assert s.host_principal_id == f"guest:{host_guest.guest_id}"

    await s._disconnect_seat("compo")

    # Host transferred to compn (the only remaining connected human).
    assert s.host_principal_id == f"guest:{other_guest.guest_id}"

    # compn got a host_changed broadcast.
    evt = s.seats[1].websocket.last_sent_of_type("host_changed")
    assert evt is not None
    assert evt["new_host_position"] == "compn"
    # In the lobby branch the seat's principal is cleared BEFORE the
    # host transfer fires, so `_transfer_host` cannot resolve the old
    # host position by principal_id and reports None. (Mid-game keeps
    # the principal during grace, so old_host_position is populated
    # there — see test_disconnect_mid_game_host_triggers_transfer_after_timeout.)
    assert evt["old_host_position"] is None


# ────────────────────────────────────────────────────────────────────
# Mid-game disconnect: 60s grace, seat_paused, timer registered.
# ────────────────────────────────────────────────────────────────────

async def test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused():
    s = _fresh_session()
    wss = seat_4_humans(s)
    s.state = "playing"

    seat = s._seat("compn")
    assert seat.principal is not None

    await s._disconnect_seat("compn")

    # Seat still owns its principal — only ws cleared.
    assert seat.websocket is None
    assert seat.is_ai is False
    assert seat.principal is not None
    assert seat.reconnect_deadline is not None  # set to monotonic + 60

    # Reconnect timer registered.
    assert "compn" in s._reconnect_tasks
    timer = s._reconnect_tasks["compn"]
    assert isinstance(timer, asyncio.Task)
    assert not timer.done()

    # Other seats see seat_paused with the 60s countdown.
    for pos in ("compo", "compe", "comps"):
        evt = wss[pos].last_sent_of_type("seat_paused")
        assert evt is not None, f"{pos} did not receive seat_paused"
        assert evt["position"] == "compn"
        assert evt["reconnect_deadline_secs"] == RECONNECT_GRACE_SECONDS
        assert "display_name" in evt

    # state_event is set so any phase awaiter wakes.
    assert seat.state_event.is_set()

    # Cancel timer to keep the test event loop clean.
    timer.cancel()
    try:
        await timer
    except asyncio.CancelledError:
        pass


async def test_disconnect_idempotent_for_ai_or_already_disconnected():
    s = _fresh_session()
    s.state = "playing"
    # Seat is default AI — disconnect should be a no-op (no broadcast,
    # no timer, no exception).
    await s._disconnect_seat("compn")
    assert "compn" not in s._reconnect_tasks

    # Now make it a human with no ws — same no-op semantics.
    seat = s._seat("compn")
    seat.is_ai = False
    seat.principal = Guest(guest_id="b" * 32)
    seat.websocket = None
    await s._disconnect_seat("compn")
    assert "compn" not in s._reconnect_tasks
    # Still human, still no ws.
    assert seat.is_ai is False
    assert seat.websocket is None


# ────────────────────────────────────────────────────────────────────
# _reconnect_timeout
# ────────────────────────────────────────────────────────────────────

async def test_reconnect_timeout_flips_to_ai(fast_clock):
    """The 60s timeout fires (instantly under fast_clock); seat flips to
    AI, principal is preserved, broadcast `seat_ai_takeover` is sent."""
    s = _fresh_session()
    wss = seat_4_humans(s)
    s.state = "playing"

    seat = s._seat("compn")
    original_principal = seat.principal
    seat.websocket = None  # simulate the prior disconnect

    await s._reconnect_timeout("compn")

    assert seat.is_ai is True
    assert seat.principal is original_principal  # principal kept!
    assert seat.reconnect_deadline is None
    assert "compn" not in s._reconnect_tasks

    for pos in ("compo", "compe", "comps"):
        evt = wss[pos].last_sent_of_type("seat_ai_takeover")
        assert evt is not None, f"{pos} did not receive seat_ai_takeover"
        assert evt["position"] == "compn"

    assert seat.state_event.is_set()


async def test_reconnect_timeout_no_op_if_websocket_returned(fast_clock):
    """If the seat reclaimed before the timer fires (ws is back), the
    timeout is a no-op: seat stays human, no broadcast, principal kept."""
    s = _fresh_session()
    wss = seat_4_humans(s)
    s.state = "playing"

    seat = s._seat("compn")
    # seat is human + connected (seat_4_humans gave it a ws). Run the
    # timer body — it should bail out early once it sees ws is not None.
    assert seat.websocket is not None

    await s._reconnect_timeout("compn")

    assert seat.is_ai is False  # untouched
    assert seat.principal is not None

    # No `seat_ai_takeover` was broadcast.
    for pos in ("compo", "compe", "comps", "compn"):
        assert wss[pos].last_sent_of_type("seat_ai_takeover") is None


async def test_disconnect_mid_game_host_triggers_transfer_after_timeout(fast_clock):
    """Host disconnects mid-game → on timeout flip-to-AI, host transfers
    to the next-oldest connected human (per spec §8.2)."""
    s = _fresh_session()
    wss = seat_4_humans(s)
    s.state = "playing"

    # Make compo the host and assign connected_since to candidates so
    # `_transfer_host` can deterministically pick a successor.
    host_seat = s._seat("compo")
    s.host_principal_id = f"guest:{host_seat.principal.guest_id}"
    host_seat.connected_since = 1.0
    s._seat("compn").connected_since = 2.0
    s._seat("compe").connected_since = 3.0
    s._seat("comps").connected_since = 4.0

    # Disconnect host mid-game → schedules a timer.
    await s._disconnect_seat("compo")
    timer = s._reconnect_tasks["compo"]

    # Drive the timer to completion (fast_clock makes sleep instant).
    await timer

    # Host transferred to compn (next-oldest connected human).
    expected_pid = f"guest:{s._seat('compn').principal.guest_id}"
    assert s.host_principal_id == expected_pid

    # A host_changed event was broadcast to remaining humans.
    evt = wss["compn"].last_sent_of_type("host_changed")
    assert evt is not None
    assert evt["new_host_position"] == "compn"
    assert evt["old_host_position"] == "compo"

    # The disconnected seat ended up AI (timeout flipped it).
    assert s._seat("compo").is_ai is True


async def test_disconnect_state_event_set_wakes_awaiter():
    """A phase awaiter blocked on a disconnected seat (state_event
    cleared) must be released when `_disconnect_seat` runs mid-game."""
    s = _fresh_session()
    wss = seat_4_humans(s)
    s.state = "playing"

    seat = s._seat("compn")

    # Simulate the awaiter: it cleared state_event and is waiting.
    seat.state_event.clear()
    waiter = asyncio.create_task(seat.state_event.wait())
    # Yield once so the waiter actually parks on the event.
    await asyncio.sleep(0)
    assert not waiter.done()

    await s._disconnect_seat("compn")

    # The disconnect path should have set the event → waiter completes.
    await asyncio.wait_for(waiter, timeout=0.1)
    assert waiter.done()

    # Cleanup: cancel the reconnect timer.
    timer = s._reconnect_tasks.pop("compn", None)
    if timer is not None and not timer.done():
        timer.cancel()
        try:
            await timer
        except asyncio.CancelledError:
            pass
