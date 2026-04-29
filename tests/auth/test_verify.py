import pytest
import re

pytestmark = pytest.mark.asyncio


def _extract_token(mail, kind="verify"):
    for m in mail.sent:
        if kind in m.body:
            match = re.search(r"token=(\S+)", m.body)
            if match:
                return match.group(1)
    return None


async def test_verify_happy(client, mail):
    await client.post("/auth/register", json={
        "email": "bob@test", "username": "bob", "password": "SecurityPass99",
    })
    token = _extract_token(mail, "verify")
    assert token
    r = await client.get(f"/auth/verify?token={token}")
    assert r.status_code == 200


async def test_verify_used_token(client, mail):
    await client.post("/auth/register", json={
        "email": "charlie@test", "username": "charlie", "password": "SecurityPass99",
    })
    token = _extract_token(mail, "verify")
    await client.get(f"/auth/verify?token={token}")
    r = await client.get(f"/auth/verify?token={token}")
    assert r.status_code == 410


async def test_resend_requires_login(client):
    r = await client.post("/auth/resend-verification")
    assert r.status_code in (401, 403)


async def test_resend_after_login_sends_mail(client, mail):
    await client.post("/auth/register", json={
        "email": "dave@test", "username": "dave", "password": "SecurityPass99",
    })
    await client.post("/auth/login", data={
        "username": "dave@test", "password": "SecurityPass99",
    })
    mail.sent.clear()
    r = await client.post("/auth/resend-verification")
    assert r.status_code == 202
    assert any("verify" in m.body for m in mail.sent)
