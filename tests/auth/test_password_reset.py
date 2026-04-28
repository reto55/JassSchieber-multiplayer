import pytest
import re

pytestmark = pytest.mark.asyncio


async def _signup(client):
    return await client.post("/auth/register", json={
        "email": "bob@example.com", "username": "bob", "password": "longpassword99",
    })


def _reset_token(mail):
    for m in mail.sent:
        if "Reset your" in m.subject:
            return re.search(r"token=(\S+)", m.body).group(1)
    return None


async def test_forgot_unknown_email_202(client):
    r = await client.post("/auth/forgot", json={"email": "nobody@test"})
    assert r.status_code == 202


async def test_forgot_known_email_sends_mail(client, mail):
    await _signup(client)
    mail.sent.clear()
    r = await client.post("/auth/forgot", json={"email": "bob@example.com"})
    assert r.status_code == 202
    assert _reset_token(mail)


async def test_reset_revokes_all_sessions(client, mail):
    await _signup(client)
    await client.post("/auth/login", data={"username": "bob@example.com", "password": "longpassword99"})
    await client.post("/auth/forgot", json={"email": "bob@example.com"})
    token = _reset_token(mail)
    r = await client.post("/auth/reset", json={
        "token": token, "new_password": "newlongpw99!",
    })
    assert r.status_code == 200
    me = await client.get("/auth/me")
    assert me.status_code in (401, 403)
    r2 = await client.post("/auth/login", data={
        "username": "bob@example.com", "password": "newlongpw99!",
    })
    assert r2.status_code == 204


async def test_reset_used_token(client, mail):
    await _signup(client)
    await client.post("/auth/forgot", json={"email": "bob@example.com"})
    token = _reset_token(mail)
    await client.post("/auth/reset", json={"token": token, "new_password": "newlongpw99!"})
    r = await client.post("/auth/reset", json={"token": token, "new_password": "anotherlong!"})
    assert r.status_code == 410
