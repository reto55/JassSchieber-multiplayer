"""Tests for ``POST /rooms/{code}/start`` (Task 18).

Endpoint contract per spec §4.2:

  - host-only (403 otherwise)
  - lobby-only (409 otherwise)
  - 404 for unknown room codes
  - 204 on success — flips ``room.state`` to ``"playing"`` and spawns
    a background game-loop task on the GameSession.

We stub ``GameSession.start_game`` with an async no-op so the test
returns synchronously without actually running spiele. The endpoint
contract is verified independently of the game loop body (which has
its own coverage in ``test_run_spiel.py``).
"""

import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


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


async def _stub_start_game(self):
    """Replacement for GameSession.start_game — yields once and returns."""
    self.state = "playing"
    await asyncio.sleep(0)


async def test_start_happy_path_204(client, monkeypatch):
    """Host calls /rooms/{code}/start; room.state="lobby" → 204."""
    from ausbau.game_session import GameSession
    from ausbau.room import get_room

    monkeypatch.setattr(GameSession, "start_game", _stub_start_game)

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]

    r = await client.post(f"/rooms/{code}/start",
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204, r.text

    room = get_room(code)
    assert room is not None
    # State flipped to "playing" by the endpoint.
    assert room.state == "playing"
    # Background task was spawned.
    assert room._game_task is not None
    # Drain the task so its no-op stub resolves cleanly.
    await room._game_task


async def test_start_not_host_403(client, client_other, monkeypatch):
    """Non-host calling /start gets 403; state unchanged."""
    from ausbau.game_session import GameSession
    from ausbau.room import get_room

    monkeypatch.setattr(GameSession, "start_game", _stub_start_game)

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]

    # Use a different httpx client (independent guest cookie) to call start.
    r = await client_other.post(f"/rooms/{code}/start",
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 403, r.text

    room = get_room(code)
    assert room.state == "lobby"
    assert room._game_task is None


async def test_start_not_lobby_409(client, monkeypatch):
    """Calling /start when room.state != 'lobby' returns 409."""
    from ausbau.game_session import GameSession
    from ausbau.room import get_room

    monkeypatch.setattr(GameSession, "start_game", _stub_start_game)

    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    room = get_room(code)
    room.state = "playing"  # mutate directly to skip the bg task

    r = await client.post(f"/rooms/{code}/start",
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 409, r.text


async def test_start_room_not_found_404(client):
    """Unknown code → 404."""
    r = await client.post("/rooms/UNKNOWN/start",
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 404
