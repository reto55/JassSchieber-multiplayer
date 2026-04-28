import pytest
from httpx import AsyncClient, ASGITransport

pytestmark = pytest.mark.asyncio


async def test_bootstrap_email_auto_promotes(client):
    # admin_bootstrap_email is "admin@test" per the conftest settings fixture
    await client.post("/auth/register", json={
        "email": "admin@test", "username": "admin", "password": "SecurePass123!",
    })
    await client.post("/auth/login", data={
        "username": "admin@test", "password": "SecurePass123!",
    })
    r = await client.get("/auth/me")
    assert r.json()["is_superuser"] is True


async def test_ban_revokes_sessions(client, app):
    # admin signup + login (this client = admin)
    await client.post("/auth/register", json={
        "email": "admin@test", "username": "admin", "password": "SecurePass123!",
    })
    await client.post("/auth/login", data={
        "username": "admin@test", "password": "SecurePass123!",
    })
    # spawn a 2nd client for the victim
    target_client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    try:
        await target_client.post("/auth/register", json={
            "email": "victim@test", "username": "victim", "password": "SecurePass123!",
        })
        await target_client.post("/auth/login", data={
            "username": "victim@test", "password": "SecurePass123!",
        })
        # admin: list users, find victim
        r = await client.get("/admin/users?q=victim")
        assert r.status_code == 200, r.text
        users = r.json()
        vid = next(u["id"] for u in users if u["username"] == "victim")
        ban = await client.post(f"/admin/users/{vid}/ban", json={"reason": "test"})
        assert ban.status_code == 200, ban.text
        # victim's /auth/me should now be 401
        me = await target_client.get("/auth/me")
        assert me.status_code in (401, 403)
    finally:
        await target_client.aclose()


async def test_demote_self_blocked(client):
    await client.post("/auth/register", json={
        "email": "admin@test", "username": "admin", "password": "SecurePass123!",
    })
    await client.post("/auth/login", data={
        "username": "admin@test", "password": "SecurePass123!",
    })
    me = (await client.get("/auth/me")).json()
    r = await client.post(f"/admin/users/{me['id']}/demote")
    assert r.status_code == 409
