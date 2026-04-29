"""Tests for the rooms reaper background task (Task 21, spec §2.3).

Scope:

  - ``reap_rooms_once()`` removes rooms in either of these states:
      a) ``state == "finished"`` for >5 min (since ``_finished_at``).
      b) zero connected humans AND zero seated humans for >5 min
         (since ``_idle_since``).
  - Reaped rooms have any orphaned spectator WSs closed (1001).
  - ``GameSession`` exposes ``_idle_since`` / ``_finished_at`` and a
    ``_update_idle_since`` helper that tracks the empty-of-humans
    transitions.
  - ``_disconnect_seat`` (lobby branch) and ``_reclaim_seat`` keep
    ``_idle_since`` in sync.
  - ``start_game`` stamps ``_finished_at`` on transition to "finished".
  - ``reaper_loop`` iterates under fast_clock — verifies the loop
    actually drives ``reap_rooms_once``.
"""

import asyncio
import time

import pytest

from ausbau.game_session import GameSession
from ausbau.room import (
    ROOMS,
    REAPER_INTERVAL_SECONDS,
    ROOM_FINISHED_LINGER_SECONDS,
    Spectator,
    Variant,
    reap_rooms_once,
    reaper_loop,
)
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket, seat_4_humans


pytestmark = pytest.mark.asyncio


def _fresh_session(code: str = "ABCDEF", host_pid: str = "guest:" + "a" * 32) -> GameSession:
    return GameSession(
        code=code,
        host_principal_id=host_pid,
        variant=Variant(),
    )


# ────────────────────────────────────────────────────────────────────
# reap_rooms_once: finished-room linger
# ────────────────────────────────────────────────────────────────────

async def test_reap_finished_room_after_linger():
    s = _fresh_session(code="ROOM01")
    s.state = "finished"
    s._finished_at = time.monotonic() - (ROOM_FINISHED_LINGER_SECONDS + 60)
    ROOMS[s.code] = s

    removed = await reap_rooms_once()

    assert "ROOM01" in removed
    assert "ROOM01" not in ROOMS


async def test_reap_finished_room_inside_linger_kept():
    s = _fresh_session(code="ROOM02")
    s.state = "finished"
    s._finished_at = time.monotonic() - 60  # only 1 min ago
    ROOMS[s.code] = s

    removed = await reap_rooms_once()

    assert "ROOM02" not in removed
    assert "ROOM02" in ROOMS


# ────────────────────────────────────────────────────────────────────
# reap_rooms_once: idle-room linger
# ────────────────────────────────────────────────────────────────────

async def test_reap_idle_room_after_linger():
    s = _fresh_session(code="ROOM03")
    # Lobby with no humans for too long.
    s.state = "lobby"
    s._idle_since = time.monotonic() - (ROOM_FINISHED_LINGER_SECONDS + 60)
    ROOMS[s.code] = s

    removed = await reap_rooms_once()

    assert "ROOM03" in removed
    assert "ROOM03" not in ROOMS


async def test_reap_skip_active_room():
    s = _fresh_session(code="ROOM04")
    # Active room: state=lobby with humans, _idle_since=None.
    seat_4_humans(s)
    s._idle_since = None
    ROOMS[s.code] = s

    removed = await reap_rooms_once()

    assert removed == []
    assert "ROOM04" in ROOMS


async def test_reap_idle_inside_linger_kept():
    s = _fresh_session(code="ROOM05")
    s.state = "lobby"
    s._idle_since = time.monotonic() - 60  # 1 min only
    ROOMS[s.code] = s

    removed = await reap_rooms_once()

    assert "ROOM05" not in removed
    assert "ROOM05" in ROOMS


# ────────────────────────────────────────────────────────────────────
# reap closes orphaned spectator WSs
# ────────────────────────────────────────────────────────────────────

async def test_reaper_closes_spectator_ws_before_remove():
    s = _fresh_session(code="ROOM06")
    s.state = "finished"
    s._finished_at = time.monotonic() - (ROOM_FINISHED_LINGER_SECONDS + 1)
    spec_ws = FakeWebSocket()
    s.spectators.append(Spectator(
        principal=Guest(guest_id="z" * 32),
        websocket=spec_ws,
    ))
    ROOMS[s.code] = s

    removed = await reap_rooms_once()

    assert "ROOM06" in removed
    assert "ROOM06" not in ROOMS
    assert spec_ws.closed is True
    assert spec_ws.close_code == 1001


async def test_reaper_does_not_crash_on_individual_room_exception(monkeypatch):
    """A single bad room must not break the whole reaper pass."""
    s_bad = _fresh_session(code="BADROOM")
    s_bad.state = "finished"
    # Replace _finished_at with a property that raises on access via a
    # __getattribute__ hook on a dummy class. Easiest: set state to a
    # non-string sentinel that the reaper compares against, and ensure
    # finished-branch doesn't crash.
    s_bad._finished_at = time.monotonic() - (ROOM_FINISHED_LINGER_SECONDS + 1)
    ROOMS[s_bad.code] = s_bad

    s_good = _fresh_session(code="GOODROOM")
    s_good.state = "finished"
    s_good._finished_at = time.monotonic() - (ROOM_FINISHED_LINGER_SECONDS + 1)
    ROOMS[s_good.code] = s_good

    # Patch `_close_room` to raise for the BAD room only.
    from ausbau import room as room_mod

    real_close = room_mod._close_room

    async def selective_close(r):
        if r.code == "BADROOM":
            raise RuntimeError("synthetic close failure")
        await real_close(r)

    monkeypatch.setattr(room_mod, "_close_room", selective_close)

    # Should not raise; should still remove the good room.
    removed = await reap_rooms_once()
    assert "GOODROOM" in removed
    assert "GOODROOM" not in ROOMS


# ────────────────────────────────────────────────────────────────────
# _idle_since lifecycle on the GameSession
# ────────────────────────────────────────────────────────────────────

async def test_idle_since_starts_none_in_init():
    s = _fresh_session()
    assert s._idle_since is None
    assert s._finished_at is None


async def test_idle_since_set_when_last_human_leaves_lobby():
    """Lobby with one human + 3 AI: human disconnects → _idle_since set."""
    s = _fresh_session()
    s.state = "lobby"
    # Only seat 0 (compo) is a human; seats 1-3 stay AI.
    g = Guest(guest_id="0" * 32)
    s.seats[0].principal = g
    s.seats[0].is_ai = False
    s.seats[0].websocket = FakeWebSocket()
    s.seats[0].connected_since = 1.0
    assert s._idle_since is None

    await s._disconnect_seat("compo")

    # All humans gone → _idle_since stamped.
    assert s._idle_since is not None
    # Approximately monotonic-now.
    assert abs(time.monotonic() - s._idle_since) < 1.0


async def test_idle_since_cleared_when_human_reclaims():
    """A reclaim with a returning human clears _idle_since."""
    s = _fresh_session()
    s.state = "playing"
    s._idle_since = time.monotonic() - 100  # already idle

    g = Guest(guest_id="1" * 32)
    s.seats[1].principal = g  # principal kept from prior disconnect
    s.seats[1].is_ai = True   # was flipped to AI
    s.seats[1].websocket = None

    new_ws = FakeWebSocket()
    await s._reclaim_seat("compn", new_ws, g)

    assert s._idle_since is None


async def test_idle_since_not_set_when_other_humans_remain():
    """Lobby with two humans: only one disconnects → _idle_since stays None."""
    s = _fresh_session()
    s.state = "lobby"
    g0 = Guest(guest_id="0" * 32)
    s.seats[0].principal = g0
    s.seats[0].is_ai = False
    s.seats[0].websocket = FakeWebSocket()
    s.seats[0].connected_since = 1.0

    g1 = Guest(guest_id="1" * 32)
    s.seats[1].principal = g1
    s.seats[1].is_ai = False
    s.seats[1].websocket = FakeWebSocket()
    s.seats[1].connected_since = 2.0

    await s._disconnect_seat("compo")

    # compn still seated + connected → _idle_since stays None.
    assert s._idle_since is None


# ────────────────────────────────────────────────────────────────────
# _finished_at stamped on game_end
# ────────────────────────────────────────────────────────────────────

async def test_finished_at_set_on_game_end(monkeypatch):
    """``start_game`` with 4 AIs at low end_game stamps _finished_at."""
    real_sleep = asyncio.sleep

    async def fast_sleep(seconds):
        await real_sleep(0)

    monkeypatch.setattr("asyncio.sleep", fast_sleep)

    s = GameSession(
        code="GENDXX",
        host_principal_id="guest:" + "f" * 32,
        variant=Variant(),
        end_game=50,
    )
    for seat in s.seats:
        seat.is_ai = True
        seat.principal = None
        seat.websocket = None

    before = time.monotonic()
    await s.start_game()
    after = time.monotonic()

    assert s.state == "finished"
    assert s._finished_at is not None
    # Stamp lies within the time-window of the run.
    assert before - 0.1 <= s._finished_at <= after + 0.1


# ────────────────────────────────────────────────────────────────────
# reaper_loop integration under fast_clock
# ────────────────────────────────────────────────────────────────────

async def test_reaper_loop_iterates_under_fast_clock(fast_clock):
    """Spawn ``reaper_loop`` as a task; expect one stale room reaped."""
    s = _fresh_session(code="STALE1")
    s.state = "finished"
    s._finished_at = time.monotonic() - (ROOM_FINISHED_LINGER_SECONDS + 60)
    ROOMS[s.code] = s

    task = asyncio.create_task(reaper_loop(), name="test_reaper_loop")
    # Give the loop several ticks to run sleep() + reap_rooms_once().
    for _ in range(5):
        await asyncio.sleep(0)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert "STALE1" not in ROOMS


async def test_reaper_loop_survives_iteration_exception(fast_clock, monkeypatch):
    """A reap iteration that raises must be logged and the loop kept alive."""
    from ausbau import room as room_mod

    calls = {"n": 0}

    async def flaky_reap():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("boom")
        return []

    monkeypatch.setattr(room_mod, "reap_rooms_once", flaky_reap)

    task = asyncio.create_task(reaper_loop(), name="test_reaper_loop_flaky")
    for _ in range(8):
        await asyncio.sleep(0)

    assert not task.done(), "reaper_loop must not crash on inner exception"
    assert calls["n"] >= 2, "loop must call reap_rooms_once again after failure"

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# ────────────────────────────────────────────────────────────────────
# Sanity: reaper does NOT touch healthy/in-progress rooms
# ────────────────────────────────────────────────────────────────────

async def test_reap_skips_finished_room_with_no_finished_at():
    """Defensive: state=finished with _finished_at=None → skip (don't crash)."""
    s = _fresh_session(code="ROOM07")
    s.state = "finished"
    s._finished_at = None
    ROOMS[s.code] = s

    removed = await reap_rooms_once()

    assert "ROOM07" not in removed
    assert "ROOM07" in ROOMS
