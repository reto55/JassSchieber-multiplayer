import pytest

pytestmark = pytest.mark.asyncio


async def _signup(client, email="alice@test", username="alice"):
    r = await client.post("/auth/register", json={
        "email": email, "username": username, "password": "longpassword99",
    })
    assert r.status_code == 201, r.text


async def test_login_sets_cookie(client):
    await _signup(client)
    r = await client.post("/auth/login", data={
        "username": "alice@test", "password": "longpassword99",
    })
    assert r.status_code == 204
    assert "schieber_session" in r.headers.get("set-cookie", "")


async def test_login_wrong_password_401(client):
    await _signup(client)
    r = await client.post("/auth/login", data={
        "username": "alice@test", "password": "wrong-password!!",
    })
    assert r.status_code in (400, 401)


async def test_login_locks_out_after_5_failures(client):
    await _signup(client)
    for _ in range(5):
        await client.post("/auth/login", data={
            "username": "alice@test", "password": "wrong-password!!",
        })
    r = await client.post("/auth/login", data={
        "username": "alice@test", "password": "wrong-password!!",
    })
    assert r.status_code == 429
