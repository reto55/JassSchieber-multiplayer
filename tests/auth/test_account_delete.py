import pytest

pytestmark = pytest.mark.asyncio


async def _setup(client, email="alice@test", username="alice", password="SecurePass123!"):
    await client.post("/auth/register", json={
        "email": email, "username": username, "password": password,
    })
    await client.post("/auth/login", data={
        "username": email, "password": password,
    })


async def test_delete_account(client):
    password = "SecurePass123!"
    await _setup(client, password=password)
    r = await client.request("DELETE", "/auth/account",
                             json={"current_password": password})
    assert r.status_code == 200
    me = await client.get("/auth/me")
    assert me.status_code in (401, 403)


async def test_signup_blocked_by_tombstone(client):
    password = "SecurePass123!"
    await _setup(client, password=password)
    await client.request("DELETE", "/auth/account",
                        json={"current_password": password})
    # try same email/username again — within 30d should fail
    r = await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": password,
    })
    assert r.status_code in (400, 409)
