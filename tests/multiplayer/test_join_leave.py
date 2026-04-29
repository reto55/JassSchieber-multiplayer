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


async def test_join_first_ai_seat(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client_other.post(f"/rooms/{code}/join", json={},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 200, r.text
    state = r.json()["room_state"]
    assert state["seats"][1]["is_ai"] is False


async def test_join_specific_seat(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client_other.post(f"/rooms/{code}/join", json={"seat": 2},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 200
    state = r.json()["room_state"]
    assert state["seats"][2]["is_ai"] is False
    assert state["seats"][1]["is_ai"] is True


async def test_join_unknown_room_404(client):
    r = await client.post("/rooms/UNKNOWN/join", json={},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 404


async def test_leave_returns_seat_to_ai(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    await client_other.post(f"/rooms/{code}/join", json={},
                            headers={"X-Requested-With": "schieber"})
    r = await client_other.post(f"/rooms/{code}/leave", json={},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204
    after = await client.get(f"/rooms/{code}")
    assert all(s["is_ai"] for s in after.json()["seats"][1:])


async def test_spectate(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client_other.post(f"/rooms/{code}/spectate",
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 200
    state = r.json()
    assert state["spectator_count"] == 1


async def test_spectate_409_when_seated(client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client.post(f"/rooms/{code}/spectate",
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 409


async def test_leave_spectator(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    await client_other.post(f"/rooms/{code}/spectate",
                            headers={"X-Requested-With": "schieber"})
    r = await client_other.post(f"/rooms/{code}/leave-spectator",
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204
    after = await client.get(f"/rooms/{code}")
    assert after.json()["spectator_count"] == 0
