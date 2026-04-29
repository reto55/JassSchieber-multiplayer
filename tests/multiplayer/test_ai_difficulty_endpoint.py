"""Sub-project C, Task 11: ``POST /rooms/{code}/ai_difficulty`` endpoint.

Auth follows the repo's standard test pattern: top-level ``tests/conftest.py``
already monkeypatches ``ausbau.server._auth_settings`` and ``_auth_factory``,
and ``_get_principal`` auto-issues a fresh guest cookie on the first request
of any ``httpx.AsyncClient``. So the *first* client to hit ``/rooms`` is the
host; a *second* client gets its own (non-host) guest principal — same
pattern as ``tests/multiplayer/test_join_leave.py``.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from ausbau.room import ROOMS


pytestmark = pytest.mark.asyncio


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


async def _make_lobby(client) -> str:
    r = await client.post("/rooms", json={},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 201, r.text
    return r.json()["code"]


async def test_set_ai_difficulty_happy(client):
    from ausbau.ai_strategies import HardStrategy
    code = await _make_lobby(client)
    r = await client.post(
        f"/rooms/{code}/ai_difficulty",
        json={"position": "compn", "level": "hard"},
        headers={"X-Requested-With": "schieber"},
    )
    assert r.status_code == 200, r.text
    seat = next(s for s in ROOMS[code].seats if s.position == "compn")
    assert seat.ai_difficulty == "hard"
    assert isinstance(seat._strategy, HardStrategy)
    # Returned payload is the full room state with the updated field.
    body = r.json()
    n_seat = next(s for s in body["seats"] if s["position"] == "compn")
    assert n_seat["ai_difficulty"] == "hard"


async def test_set_ai_difficulty_invalid_level(client):
    code = await _make_lobby(client)
    r = await client.post(
        f"/rooms/{code}/ai_difficulty",
        json={"position": "compn", "level": "expert"},
        headers={"X-Requested-With": "schieber"},
    )
    assert r.status_code == 400


async def test_set_ai_difficulty_invalid_position(client):
    code = await _make_lobby(client)
    r = await client.post(
        f"/rooms/{code}/ai_difficulty",
        json={"position": "compZ", "level": "hard"},
        headers={"X-Requested-With": "schieber"},
    )
    assert r.status_code == 400


async def test_set_ai_difficulty_human_seat(client):
    """Seat 0 (compo) is the human host. Cannot set difficulty on a human."""
    code = await _make_lobby(client)
    r = await client.post(
        f"/rooms/{code}/ai_difficulty",
        json={"position": "compo", "level": "hard"},
        headers={"X-Requested-With": "schieber"},
    )
    assert r.status_code == 400


async def test_set_ai_difficulty_not_host(client, client_other):
    code = await _make_lobby(client)
    # client_other is a different guest principal → not the host.
    r = await client_other.post(
        f"/rooms/{code}/ai_difficulty",
        json={"position": "compn", "level": "hard"},
        headers={"X-Requested-With": "schieber"},
    )
    assert r.status_code == 403


async def test_set_ai_difficulty_mid_game_409(client):
    code = await _make_lobby(client)
    ROOMS[code].state = "playing"
    r = await client.post(
        f"/rooms/{code}/ai_difficulty",
        json={"position": "compn", "level": "hard"},
        headers={"X-Requested-With": "schieber"},
    )
    assert r.status_code == 409


async def test_set_ai_difficulty_room_not_found_404(client):
    r = await client.post(
        "/rooms/NOSUCH/ai_difficulty",
        json={"position": "compn", "level": "hard"},
        headers={"X-Requested-With": "schieber"},
    )
    assert r.status_code == 404
