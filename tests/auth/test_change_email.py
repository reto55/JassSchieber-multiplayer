import pytest
import re

pytestmark = pytest.mark.asyncio


async def _setup(client):
    await client.post("/auth/register", json={
        "email": "user@test", "username": "testuser", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "user@test", "password": "longpassword99",
    })


def _confirm_token(mail):
    for m in mail.sent:
        if "switch your account email" in m.body:
            return re.search(r"token=(\S+)", m.body).group(1)
    return None


async def test_change_email_two_step(client, mail):
    await _setup(client)
    mail.sent.clear()
    r = await client.post("/auth/change-email", json={
        "new_email": "new@test", "current_password": "longpassword99",
    })
    assert r.status_code == 202
    assert any(m.to == "new@test" for m in mail.sent)
    assert any(m.to == "user@test" for m in mail.sent)
    token = _confirm_token(mail)
    r = await client.get(f"/auth/confirm-email?token={token}")
    assert r.status_code == 200
    me = await client.get("/auth/me")
    assert me.json()["email"] == "new@test"


async def test_change_email_wrong_password_401(client):
    await _setup(client)
    r = await client.post("/auth/change-email", json={
        "new_email": "new@test", "current_password": "wrongpass",
    })
    assert r.status_code == 401


async def test_change_email_collision_409(client, mail):
    await client.post("/auth/register", json={
        "email": "taken@test", "username": "bob", "password": "longpassword99",
    })
    await _setup(client)
    r = await client.post("/auth/change-email", json={
        "new_email": "taken@test", "current_password": "longpassword99",
    })
    assert r.status_code == 409
