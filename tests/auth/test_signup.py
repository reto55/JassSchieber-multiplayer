import pytest

pytestmark = pytest.mark.asyncio


async def test_signup_happy_path(client, mail):
    r = await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "longpassword99",
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "alice@test"
    assert body["username"] == "alice"
    assert body["is_verified"] is False
    # verification mail sent
    assert any("verify" in m.body for m in mail.sent)


async def test_signup_duplicate_email_409(client):
    payload = {"email": "x@test", "username": "alice", "password": "longpassword99"}
    r = await client.post("/auth/register", json=payload)
    assert r.status_code == 201
    payload2 = {**payload, "username": "alice2"}
    r = await client.post("/auth/register", json=payload2)
    assert r.status_code in (400, 409)


async def test_signup_duplicate_username_409(client):
    await client.post("/auth/register", json={
        "email": "a1@test", "username": "alice", "password": "longpassword99",
    })
    r = await client.post("/auth/register", json={
        "email": "a2@test", "username": "alice", "password": "longpassword99",
    })
    assert r.status_code in (400, 409)


async def test_signup_short_password_422(client):
    r = await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "short",
    })
    assert r.status_code in (400, 422)


async def test_signup_invalid_username_422(client):
    r = await client.post("/auth/register", json={
        "email": "a@test", "username": "ab", "password": "longpassword99",
    })
    assert r.status_code == 422
