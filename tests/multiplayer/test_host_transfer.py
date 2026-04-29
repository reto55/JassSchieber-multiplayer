"""Tests for Task 20: host transfer + kick refinements.

Spec (multiplayer §8):

- §8.1–8.3 Host privileges + transfer
  - Host disconnect in lobby → immediate transfer (Task 14, regression covered).
  - Host disconnect mid-game → 60s grace; transfer fires when AI-takeover does
    (Task 14, regression covered).
  - Host /leave → immediate transfer before leave completes (Task 6 wires
    `_transfer_host` for the lobby self-leave path; verified here via HTTP).
  - "Oldest-connected human becomes host." Selection done by `_transfer_host`,
    tie-break alphabetical principal_id.
  - No connected humans → host transfer deferred. The host_principal_id
    remains pointing at the disconnected former host; lobby /start fails 403
    until somebody reconnects (or a different human joins and reclaims host).

- §8.4 Kick (POST /rooms/{code}/leave with `target_position`):
  - Caller must be host, else 403.
  - Room must be lobby state, else 400.
  - Target seat → AI; broadcasts `seat_kicked`.
  - Target's WS closed with code 1008 reason "kicked from room".
  - Mid-game kicks not allowed.
  - Host kicks themselves (target_position == host's seat) → treated as
    ordinary leave (host transfer + AI fill).

- §8.6 Edge cases:
  - All humans disconnect → no host; first reconnect becomes host. Implemented
    in `_reclaim_seat` via post-attach check: if `host_principal_id` does NOT
    match any currently-connected seat, trigger `_transfer_host()`.
"""

import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from ausbau.game_session import GameSession
from ausbau.room import Variant, principal_id
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
# Unit-level: deferred host on no connected humans + reconnect promote
# ────────────────────────────────────────────────────────────────────

async def test_transfer_host_no_op_when_no_connected_humans():
    """When called with all seats AI/disconnected, _transfer_host returns
    silently (no candidates). host_principal_id stays untouched."""
    s = _fresh_session(host_pid="guest:" + "0" * 32)
    # All seats default AI.
    before = s.host_principal_id
    await s._transfer_host()
    assert s.host_principal_id == before


async def test_reclaim_into_hostless_room_promotes_reconnecting_human(fast_clock):
    """Lone host disconnects mid-game → after 60s timeout the seat is AI but
    `_transfer_host()` finds no candidates, so host_principal_id is unchanged
    (still pointing at the now-disconnected host). When that very seat is
    reclaimed (the original host returns), the new `_reclaim_seat` post-check
    re-fires `_transfer_host` so the reconnecting human becomes (or remains)
    host.

    Concretely: another human reclaims a seat in a hostless room → they
    become host.
    """
    s = _fresh_session()
    s.state = "playing"

    # Host (compo) human + one other human (compn). compe/comps stay AI.
    host_g = Guest(guest_id="0" * 32)
    other_g = Guest(guest_id="1" * 32)
    s.seats[0].principal = host_g
    s.seats[0].is_ai = False
    s.seats[0].websocket = FakeWebSocket()
    s.seats[0].connected_since = 1.0
    s.host_principal_id = principal_id(host_g)

    s.seats[1].principal = other_g
    s.seats[1].is_ai = False
    s.seats[1].websocket = FakeWebSocket()
    s.seats[1].connected_since = 2.0

    # Disconnect both humans mid-game (no AI takeover yet — sim a network
    # hiccup that loses both at once).
    await s._disconnect_seat("compo")
    await s._disconnect_seat("compn")

    # Drive both reconnect timers to AI takeover.
    for pos in ("compo", "compn"):
        timer = s._reconnect_tasks.get(pos)
        if timer is not None:
            await timer

    # Both seats are AI now; host_principal_id still points at host_g
    # (because _transfer_host found no candidates at takeover time).
    assert s.seats[0].is_ai is True
    assert s.seats[1].is_ai is True
    assert s.host_principal_id == principal_id(host_g)

    # The OTHER human (other_g) reclaims their seat (compn). Since the room
    # has no connected host at that moment, _reclaim_seat must promote them.
    new_ws = FakeWebSocket()
    await s._reclaim_seat("compn", new_ws, other_g)

    # other_g is now host — they are the only connected human.
    assert s.host_principal_id == principal_id(other_g)
    # host_changed broadcast fired.
    evt = new_ws.last_sent_of_type("host_changed")
    assert evt is not None
    assert evt["new_host_position"] == "compn"


async def test_reclaim_into_room_with_connected_host_does_not_promote():
    """When a connected host already holds office, reclaiming a non-host
    seat must NOT trigger host transfer."""
    s = _fresh_session()
    s.state = "playing"

    host_g = Guest(guest_id="0" * 32)
    other_g = Guest(guest_id="1" * 32)
    s.seats[0].principal = host_g
    s.seats[0].is_ai = False
    s.seats[0].websocket = FakeWebSocket()
    s.seats[0].connected_since = 1.0
    s.host_principal_id = principal_id(host_g)

    # compn was held by other_g, currently disconnected (mid-game grace).
    s.seats[1].principal = other_g
    s.seats[1].is_ai = False
    s.seats[1].websocket = None  # disconnected
    s.seats[1].connected_since = None

    new_ws = FakeWebSocket()
    await s._reclaim_seat("compn", new_ws, other_g)

    # Host stayed.
    assert s.host_principal_id == principal_id(host_g)
    # No host_changed event went to compn either.
    assert new_ws.last_sent_of_type("host_changed") is None


# ────────────────────────────────────────────────────────────────────
# HTTP-level: host /leave triggers immediate host transfer
# ────────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    from ausbau.server import app as srv_app
    async with AsyncClient(transport=ASGITransport(app=srv_app),
                           base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def client_other():
    from ausbau.server import app as srv_app
    async with AsyncClient(transport=ASGITransport(app=srv_app),
                           base_url="http://test") as c:
        yield c


async def test_host_leave_in_lobby_transfers_host(client, client_other):
    """Host calls /leave (no target) → another connected human becomes host."""
    from ausbau.room import get_room

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    # Other human joins, takes seat 1 (compn).
    join = await client_other.post(f"/rooms/{code}/join", json={"seat": 1},
                                   headers={"X-Requested-With": "schieber"})
    assert join.status_code == 200

    room = get_room(code)
    # Wire a FakeWebSocket on the joiner so _transfer_host has a connected
    # candidate (the HTTP join endpoint doesn't open a WS).
    import time
    other_ws = FakeWebSocket()
    room.seats[1].websocket = other_ws
    room.seats[1].connected_since = time.monotonic()

    # Sanity: host is currently seat 0.
    host_pid_before = room.host_principal_id
    assert room.seats[0].principal is not None
    assert principal_id(room.seats[0].principal) == host_pid_before

    # Host leaves.
    r = await client.post(f"/rooms/{code}/leave", json={},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204

    # Host transferred to compn.
    assert room.host_principal_id != host_pid_before
    assert room.seats[1].principal is not None
    assert room.host_principal_id == principal_id(room.seats[1].principal)
    # compn got a host_changed broadcast.
    evt = other_ws.last_sent_of_type("host_changed")
    assert evt is not None
    assert evt["new_host_position"] == "compn"


async def test_host_leave_in_lobby_no_other_humans_no_transfer(client):
    """Host leaves an empty (host-only) lobby → host_principal_id is unchanged
    (no candidate to transfer to). The seat drops to AI."""
    from ausbau.room import get_room

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    room = get_room(code)
    host_pid_before = room.host_principal_id

    r = await client.post(f"/rooms/{code}/leave", json={},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204

    # No transfer (no candidates).
    assert room.host_principal_id == host_pid_before
    # Seat 0 is AI.
    assert room.seats[0].is_ai is True


# ────────────────────────────────────────────────────────────────────
# HTTP-level: kick path
# ────────────────────────────────────────────────────────────────────

async def test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target(
    client, client_other,
):
    """Host kicks a human from lobby:

    - Target seat drops to AI (principal cleared, websocket cleared).
    - Target's WS receives close(1008, "kicked from room").
    - All other connected seats receive `seat_kicked` broadcast.
    """
    from ausbau.room import get_room
    import time

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    join = await client_other.post(f"/rooms/{code}/join", json={"seat": 2},
                                   headers={"X-Requested-With": "schieber"})
    assert join.status_code == 200

    room = get_room(code)
    # Manually attach FakeWebSockets so close + broadcast are observable.
    host_ws = FakeWebSocket()
    target_ws = FakeWebSocket()
    room.seats[0].websocket = host_ws
    room.seats[0].connected_since = time.monotonic()
    room.seats[2].websocket = target_ws
    room.seats[2].connected_since = time.monotonic()

    # Host kicks compe (seat index 2).
    r = await client.post(f"/rooms/{code}/leave",
                          json={"target_position": "compe"},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204

    # Target seat is AI.
    assert room.seats[2].is_ai is True
    assert room.seats[2].principal is None
    assert room.seats[2].websocket is None

    # Target's WS was closed with 1008 + "kicked from room".
    assert target_ws.closed is True
    assert target_ws.close_code == 1008
    assert target_ws.close_reason == "kicked from room"

    # Host received `seat_kicked` broadcast.
    evt = host_ws.last_sent_of_type("seat_kicked")
    assert evt is not None
    assert evt["position"] == "compe"
    assert evt["by_host"] is True


async def test_kick_not_host_returns_403(client, client_other):
    """Non-host calls /leave with target_position → 403."""
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    # client_other joins seat 1.
    j1 = await client_other.post(f"/rooms/{code}/join", json={"seat": 1},
                                 headers={"X-Requested-With": "schieber"})
    assert j1.status_code == 200

    # client_other (NOT host) tries to kick seat 0 (host).
    r = await client_other.post(f"/rooms/{code}/leave",
                                json={"target_position": "compo"},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 403


async def test_kick_mid_game_returns_400(client, client_other):
    """Kick attempt while state != lobby returns 400."""
    from ausbau.room import get_room

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    await client_other.post(f"/rooms/{code}/join", json={"seat": 1},
                            headers={"X-Requested-With": "schieber"})
    room = get_room(code)
    room.state = "playing"  # simulate mid-game

    r = await client.post(f"/rooms/{code}/leave",
                          json={"target_position": "compn"},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 400


async def test_kick_self_treated_as_leave_transfers_host(client, client_other):
    """Host kicks themselves (target_position == own seat) →
    behaves as a normal leave: seat → AI, host transfers to next-oldest
    connected human."""
    from ausbau.room import get_room
    import time

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    j1 = await client_other.post(f"/rooms/{code}/join", json={"seat": 1},
                                 headers={"X-Requested-With": "schieber"})
    assert j1.status_code == 200

    room = get_room(code)
    other_ws = FakeWebSocket()
    room.seats[1].websocket = other_ws
    room.seats[1].connected_since = time.monotonic()

    host_pid_before = room.host_principal_id

    r = await client.post(f"/rooms/{code}/leave",
                          json={"target_position": "compo"},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204

    # Host's old seat is AI.
    assert room.seats[0].is_ai is True
    assert room.seats[0].principal is None
    # Host transferred to compn.
    assert room.host_principal_id != host_pid_before
    assert room.host_principal_id == principal_id(room.seats[1].principal)
    evt = other_ws.last_sent_of_type("host_changed")
    assert evt is not None
    assert evt["new_host_position"] == "compn"


async def test_kick_invalid_target_position_returns_422(client):
    """Bogus target_position string → 422."""
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client.post(f"/rooms/{code}/leave",
                          json={"target_position": "bogus"},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 422


async def test_kick_target_already_ai_is_idempotent(client):
    """Kicking an AI seat is a no-op success (204)."""
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client.post(f"/rooms/{code}/leave",
                          json={"target_position": "compn"},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204
