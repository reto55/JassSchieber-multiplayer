import pytest

pytestmark = pytest.mark.asyncio


async def test_signup_rate_limit(client):
    for i in range(5):
        r = await client.post("/auth/register", json={
            "email": f"a{i}@test", "username": f"alice{i:03d}",
            "password": "SecurePass123!",
        })
        assert r.status_code == 201, r.text
    r = await client.post("/auth/register", json={
        "email": "a99@test", "username": "alice999",
        "password": "SecurePass123!",
    })
    assert r.status_code == 429
    assert "Retry-After" in r.headers


async def test_forgot_rate_limit(client):
    for _ in range(3):
        await client.post("/auth/forgot", json={"email": "x@test"})
    r = await client.post("/auth/forgot", json={"email": "x@test"})
    assert r.status_code == 429
