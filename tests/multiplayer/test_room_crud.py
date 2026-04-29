import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def client():
    """An httpx client against the live ausbau.server app."""
    from ausbau.server import app as srv_app
    async with AsyncClient(transport=ASGITransport(app=srv_app),
                           base_url="http://test") as c:
        yield c


async def test_create_room_returns_code_and_state(client):
    r = await client.post("/rooms", json={
        "variant": {"trumpf_bock": False, "match_bonus": True, "stoeck": True},
    }, headers={"X-Requested-With": "schieber"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert "code" in body and len(body["code"]) == 6
    assert body["state"] == "lobby"
    assert len(body["seats"]) == 4
    assert body["seats"][0]["is_ai"] is False  # host
    assert all(s["is_ai"] for s in body["seats"][1:])
    assert body["seats"][0]["is_host"] is True


async def test_get_room_404_for_unknown(client):
    r = await client.get("/rooms/UNKNOWN")
    assert r.status_code == 404


async def test_get_room_returns_state(client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client.get(f"/rooms/{code}")
    assert r.status_code == 200
    assert r.json()["code"] == code


async def test_rooms_mine_includes_created(client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client.get("/rooms/mine")
    assert r.status_code == 200
    rooms = r.json()
    assert any(rm["code"] == code and rm["role"] == "seat" for rm in rooms)
