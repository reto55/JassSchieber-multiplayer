import pytest

pytestmark = pytest.mark.asyncio


async def _setup(client):
    await client.post("/auth/register", json={
        "email": "user@test", "username": "testuser", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "user@test", "password": "longpassword99",
    })


async def test_change_password_happy(client):
    await _setup(client)
    r = await client.post("/auth/change-password", json={
        "current_password": "longpassword99",
        "new_password": "differentpw77!",
    })
    assert r.status_code == 200


async def test_change_password_wrong_current_401(client):
    await _setup(client)
    r = await client.post("/auth/change-password", json={
        "current_password": "wrong-password!!",
        "new_password": "differentpw77!",
    })
    assert r.status_code == 401


async def test_change_password_keeps_current_session(client):
    await _setup(client)
    r = await client.post("/auth/change-password", json={
        "current_password": "longpassword99",
        "new_password": "differentpw77!",
    })
    assert r.status_code == 200
    me = await client.get("/auth/me")
    assert me.status_code == 200
