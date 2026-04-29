"""Tests for ``POST /rooms/{code}/seat`` mid-game seat swap (Task 19).

Spec §4.3 + §5.2.6: a seated, connected human can request to swap seats
with another seated, connected human mid-game. The flow is:

  1. Requester calls ``POST /rooms/{code}/seat`` with ``{to: <idx>}``.
     Server records the pending request (TTL = 30 s) and pushes
     ``seat_swap_request`` to the target seat.
  2. Target accepts via the same endpoint with
     ``{to: <requester-idx>, accept: true}``. Server marks the swap as
     pending — the actual seat swap (principal, websocket, hand) takes
     effect at the next trick boundary inside ``_play_trick``.
  3. Once committed, server broadcasts ``seat_swap_committed`` with
     ``swaps`` listing both directions.
  4. If the TTL expires before acceptance, the target receives
     ``seat_swap_expired`` and the request is dropped.

Restrictions:
  - Both seats must be human (no human↔AI swap).
  - Both must currently be connected (no swap with a paused seat).
  - Concurrent swaps from the same ``from_position`` overwrite earlier.

Scores stay attached to teams (NS/EW); they are not swapped.
"""

import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from Cards_refactored import Play
from ausbau.game_session import GameSession
from ausbau.room import SEAT_SWAP_REQUEST_TTL_SECONDS, Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket, seat_4_humans


pytestmark = pytest.mark.asyncio


def _fresh_session():
    g = Guest(guest_id='a' * 32)
    s = GameSession(
        code="A",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(),
    )
    s.state = "playing"
    return s


# -----------------------------------------------------------------------
# Direct-helper tests (session-level; no HTTP)
# -----------------------------------------------------------------------


async def test_seat_swap_request_records_and_pushes():
    """A request from compo→compn records pending entry and pushes
    seat_swap_request to compn's WS only."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    await s._record_seat_swap_request("compo", "compn", "alice")

    # Pending entry tracked.
    assert ("compo", "compn") in s._swap_requests

    # compn got seat_swap_request; compo / compe / comps did NOT.
    req = wss["compn"].last_sent_of_type("seat_swap_request")
    assert req is not None
    assert req["from_position"] == "compo"
    assert req["from_display_name"] == "alice"
    for other in ("compo", "compe", "comps"):
        assert wss[other].last_sent_of_type("seat_swap_request") is None


async def test_seat_swap_request_overwrites_prior_from_same_seat():
    """A second request from compo (now to compe) cancels the prior
    (compo→compn) request — only one outstanding request per from_position."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    await s._record_seat_swap_request("compo", "compn", "alice")
    first_task = s._swap_requests[("compo", "compn")][1]

    await s._record_seat_swap_request("compo", "compe", "alice")

    # Old request gone, prior task cancelled. Yield once so the
    # cancellation request actually propagates to a finished state.
    assert ("compo", "compn") not in s._swap_requests
    try:
        await first_task
    except asyncio.CancelledError:
        pass
    assert first_task.cancelled() or first_task.done()

    # New request live.
    assert ("compo", "compe") in s._swap_requests

    req = wss["compe"].last_sent_of_type("seat_swap_request")
    assert req is not None
    assert req["from_position"] == "compo"


async def test_seat_swap_accept_sets_pending_swap():
    """Accept clears the pending request entry and arms the swap for
    the next trick boundary."""
    s = _fresh_session()
    seat_4_humans(s)

    await s._record_seat_swap_request("compo", "compn", "alice")
    await s._accept_seat_swap("compn", "compo")

    assert s._pending_swap == ("compo", "compn")
    assert ("compo", "compn") not in s._swap_requests


async def test_commit_pending_swap_swaps_principals_and_hands():
    """``_commit_pending_swap`` atomically swaps principal, websocket and
    the per-Play hand attribute, then broadcasts seat_swap_committed."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    play = Play(spiel=1)
    s.current_play = play

    seat_o = s._seat("compo")
    seat_n = s._seat("compn")
    p_o, p_n = seat_o.principal, seat_n.principal
    ws_o, ws_n = seat_o.websocket, seat_n.websocket
    hand_o = play.compo
    hand_n = play.compn

    s._pending_swap = ("compo", "compn")
    await s._commit_pending_swap()

    # Principals + websockets swapped.
    assert seat_o.principal is p_n
    assert seat_n.principal is p_o
    assert seat_o.websocket is ws_n
    assert seat_n.websocket is ws_o

    # Hands swapped on Play.
    assert play.compo is hand_n
    assert play.compn is hand_o

    # _pending_swap consumed.
    assert s._pending_swap is None

    # seat_swap_committed broadcast to all four seats.
    expected = {"type": "seat_swap_committed",
                "swaps": [["compo", "compn"], ["compn", "compo"]]}
    for pos in ("compo", "compn", "compe", "comps"):
        msg = wss[pos].last_sent_of_type("seat_swap_committed")
        assert msg is not None
        assert msg["swaps"] == [["compo", "compn"], ["compn", "compo"]]


async def test_commit_pending_swap_noop_when_no_pending():
    """``_commit_pending_swap`` is a no-op when no swap is pending."""
    s = _fresh_session()
    wss = seat_4_humans(s)
    s._pending_swap = None

    await s._commit_pending_swap()

    for pos in ("compo", "compn", "compe", "comps"):
        assert wss[pos].last_sent_of_type("seat_swap_committed") is None


async def test_commit_aborts_if_either_seat_disconnected_post_accept():
    """If a side disconnects between accept and the trick boundary, the
    swap aborts and ``seat_swap_expired`` fires to whoever is still
    connected. Principals/hands stay put.
    """
    s = _fresh_session()
    wss = seat_4_humans(s)

    play = Play(spiel=1)
    s.current_play = play

    seat_o = s._seat("compo")
    seat_n = s._seat("compn")
    p_o, p_n = seat_o.principal, seat_n.principal
    hand_o = play.compo
    hand_n = play.compn

    # Simulate compn dropping after accept but before the trick boundary.
    surviving_ws = wss["compo"]
    seat_n.websocket = None

    s._pending_swap = ("compo", "compn")
    await s._commit_pending_swap()

    # No commit broadcast.
    for pos in ("compo", "compn", "compe", "comps"):
        assert wss[pos].last_sent_of_type("seat_swap_committed") is None

    # Principals & hands untouched.
    assert seat_o.principal is p_o
    assert seat_n.principal is p_n
    assert play.compo is hand_o
    assert play.compn is hand_n

    # _pending_swap consumed (one-shot).
    assert s._pending_swap is None

    # The still-connected side received seat_swap_expired.
    expired = surviving_ws.last_sent_of_type("seat_swap_expired")
    assert expired is not None
    assert expired["from_position"] == "compo"


async def test_seat_swap_ttl_fires_seat_swap_expired(fast_clock):
    """If the target never accepts, the timeout coro fires and pushes
    seat_swap_expired to the target."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    await s._record_seat_swap_request("compo", "compn", "alice")
    _expires, task = s._swap_requests[("compo", "compn")]

    # Drive the timer — fast_clock collapses sleeps to 0 ticks.
    await task

    expired = wss["compn"].last_sent_of_type("seat_swap_expired")
    assert expired is not None
    assert expired["from_position"] == "compo"
    assert ("compo", "compn") not in s._swap_requests


# -----------------------------------------------------------------------
# Endpoint tests (HTTP layer)
# -----------------------------------------------------------------------


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


async def test_seat_swap_endpoint_409_if_state_lobby(client):
    """Mid-game swap is rejected when state is lobby."""
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client.post(f"/rooms/{code}/seat", json={"to": 1},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 409, r.text


async def test_seat_swap_endpoint_403_if_caller_not_seated(client, client_other):
    """Caller who is not seated → 403."""
    from ausbau.room import get_room

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    room = get_room(code)
    room.state = "playing"

    # client_other has no seat in this room.
    r = await client_other.post(f"/rooms/{code}/seat", json={"to": 1},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 403, r.text


async def test_seat_swap_endpoint_400_if_target_ai(client):
    """Target seat is AI → 400."""
    from ausbau.room import get_room

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    room = get_room(code)
    room.state = "playing"
    # Caller (host) is at seat 0 = compo; we need an attached websocket so
    # the "connected human" check passes.
    room.seats[0].websocket = FakeWebSocket()
    # Seat 1 (compn) is AI by default.

    r = await client.post(f"/rooms/{code}/seat", json={"to": 1},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 400, r.text


async def test_seat_swap_endpoint_400_if_self(client):
    """Cannot swap with own seat → 400."""
    from ausbau.room import get_room

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    room = get_room(code)
    room.state = "playing"
    room.seats[0].websocket = FakeWebSocket()

    r = await client.post(f"/rooms/{code}/seat", json={"to": 0},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 400, r.text


async def test_seat_swap_endpoint_happy_request_path(client, client_other):
    """Two connected humans, state=playing → 200; pending entry created;
    target's WS got seat_swap_request."""
    from ausbau.room import get_room

    # client = host @ compo; client_other = compn after /join.
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    join = await client_other.post(f"/rooms/{code}/join", json={"seat": 1},
                                   headers={"X-Requested-With": "schieber"})
    assert join.status_code == 200

    room = get_room(code)
    room.state = "playing"
    # Both seats need a websocket attached for the connected-human check.
    ws_o = FakeWebSocket()
    ws_n = FakeWebSocket()
    room.seats[0].websocket = ws_o
    room.seats[1].websocket = ws_n

    r = await client.post(f"/rooms/{code}/seat", json={"to": 1},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 200, r.text

    assert ("compo", "compn") in room._swap_requests
    req = ws_n.last_sent_of_type("seat_swap_request")
    assert req is not None
    assert req["from_position"] == "compo"


async def test_seat_swap_endpoint_happy_accept_path(client, client_other):
    """Prior request pending; accepter calls with accept:true → 200;
    _pending_swap set on the room."""
    from ausbau.room import get_room

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    join = await client_other.post(f"/rooms/{code}/join", json={"seat": 1},
                                   headers={"X-Requested-With": "schieber"})
    assert join.status_code == 200

    room = get_room(code)
    room.state = "playing"
    ws_o = FakeWebSocket()
    ws_n = FakeWebSocket()
    room.seats[0].websocket = ws_o
    room.seats[1].websocket = ws_n

    # Step 1: requester (host @ compo) asks compn.
    r1 = await client.post(f"/rooms/{code}/seat", json={"to": 1},
                           headers={"X-Requested-With": "schieber"})
    assert r1.status_code == 200, r1.text

    # Step 2: target (client_other @ compn) accepts (to=0 = compo).
    r2 = await client_other.post(
        f"/rooms/{code}/seat",
        json={"to": 0, "accept": True},
        headers={"X-Requested-With": "schieber"},
    )
    assert r2.status_code == 200, r2.text

    assert room._pending_swap == ("compo", "compn")
    assert ("compo", "compn") not in room._swap_requests


async def test_seat_swap_409_when_target_already_has_pending_request(client, client_other):
    """A second requester aiming at a seat that already has a pending
    request gets 409. Spec is silent; reviewer guidance picks "fail
    fast" so two requesters can't race for one acceptor click.
    """
    from ausbau.room import get_room

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    join = await client_other.post(f"/rooms/{code}/join", json={"seat": 1},
                                   headers={"X-Requested-With": "schieber"})
    assert join.status_code == 200

    room = get_room(code)
    room.state = "playing"
    # All four seats need to be connected humans for the swap checks.
    room.seats[0].websocket = FakeWebSocket()
    room.seats[1].websocket = FakeWebSocket()
    # Attach client_other's principal to seat 2 (compe) too, so it's a
    # connected human that can also issue a request.
    from frontend.auth.guest import Guest
    room.seats[2].principal = Guest(guest_id='c' * 32)
    room.seats[2].is_ai = False
    room.seats[2].websocket = FakeWebSocket()

    # Simulate compe→compn already pending (a different requester already
    # has the same target). We bypass the endpoint to plant it cleanly.
    await room._record_seat_swap_request("compe", "compn", "carol")
    assert ("compe", "compn") in room._swap_requests

    # Now host (compo) tries compo→compn. Different from-pos, same to-pos.
    r = await client.post(f"/rooms/{code}/seat", json={"to": 1},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 409, r.text
    # Original request still standing.
    assert ("compe", "compn") in room._swap_requests
    # No new request was recorded for compo.
    assert ("compo", "compn") not in room._swap_requests


async def test_seat_swap_endpoint_403_if_caller_disconnected(client):
    """Caller's seat exists but ``websocket=None`` (mid-grace) → 403.
    The existing ``websocket is None`` branch covers this case.
    """
    from ausbau.room import get_room

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    room = get_room(code)
    room.state = "playing"
    # Caller is host @ compo: principal is set by /rooms POST, but no WS
    # ever attached (or it dropped, mid-grace).
    assert room.seats[0].principal is not None
    assert room.seats[0].websocket is None
    assert room.seats[0].is_ai is False

    r = await client.post(f"/rooms/{code}/seat", json={"to": 1},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 403, r.text
