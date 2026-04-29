import pytest

pytestmark = pytest.mark.asyncio


async def test_me_authed(client):
    await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "alice@test", "password": "longpassword99",
    })
    r = await client.get("/auth/me")
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "alice@test"
    assert body["username"] == "alice"


async def test_me_unauthed(client):
    r = await client.get("/auth/me")
    assert r.status_code in (401, 403)
