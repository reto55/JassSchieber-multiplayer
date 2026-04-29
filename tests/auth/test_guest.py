import pytest

pytestmark = pytest.mark.asyncio


async def test_whoami_issues_guest_cookie(client):
    r = await client.get("/auth/whoami")
    assert r.status_code == 200
    assert r.json()["kind"] == "guest"
    assert r.json()["display_name"].startswith("Guest-")
    assert "schieber_guest" in r.headers.get("set-cookie", "")


async def test_whoami_authed(client):
    await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "SecurePass123!",
    })
    await client.post("/auth/login", data={
        "username": "alice@test", "password": "SecurePass123!",
    })
    r = await client.get("/auth/whoami")
    assert r.json() == {
        "kind": "user", "display_name": "alice",
        "is_verified": False, "is_superuser": False,
    }


async def test_signup_clears_guest_cookie(client):
    await client.get("/auth/whoami")  # gets guest cookie
    r = await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "SecurePass123!",
    })
    cookie_header = r.headers.get("set-cookie", "")
    assert "schieber_guest=" in cookie_header
    assert "Max-Age=0" in cookie_header or 'schieber_guest=""' in cookie_header


async def test_tampered_guest_cookie_replaced(client):
    client.cookies.set("schieber_guest", "tampered.cookie.value")
    r = await client.get("/auth/whoami")
    assert r.json()["kind"] == "guest"
    # new cookie issued
    assert "schieber_guest" in r.headers.get("set-cookie", "")
