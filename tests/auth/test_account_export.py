import pytest

pytestmark = pytest.mark.asyncio


async def test_export_returns_self_data(client):
    await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "SecurePass123!",
    })
    await client.post("/auth/login", data={
        "username": "alice@test", "password": "SecurePass123!",
    })
    r = await client.get("/auth/export")
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["email"] == "alice@test"
    assert "access_tokens" in body
    assert "email_tokens" in body
