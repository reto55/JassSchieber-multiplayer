import pytest

pytestmark = pytest.mark.asyncio


async def test_logout_clears_cookie_and_revokes(client):
    await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "alice@test", "password": "longpassword99",
    })
    r = await client.post("/auth/logout")
    assert r.status_code == 204
    assert 'schieber_session=""' in r.headers.get("set-cookie", "") \
        or "Max-Age=0" in r.headers.get("set-cookie", "")
    # subsequent /auth/me returns 401
    r2 = await client.get("/auth/me")
    assert r2.status_code in (401, 403)
