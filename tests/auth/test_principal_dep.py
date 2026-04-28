import pytest

pytestmark = pytest.mark.asyncio


async def test_principal_dep_via_whoami_authed(client):
    """The whoami endpoint already exercises the User branch — verify by signup+login."""
    await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "SecurePass123!",
    })
    await client.post("/auth/login", data={
        "username": "alice@test", "password": "SecurePass123!",
    })
    r = await client.get("/auth/whoami")
    assert r.status_code == 200
    assert r.json()["kind"] == "user"


async def test_principal_dep_via_whoami_guest(client):
    """No cookies → guest cookie issued."""
    r = await client.get("/auth/whoami")
    assert r.status_code == 200
    assert r.json()["kind"] == "guest"
    assert "schieber_guest" in r.headers.get("set-cookie", "")


async def test_make_current_principal_dep_factory_exists():
    """The factory function is importable and callable."""
    from frontend.auth.deps import make_current_principal_dep
    dep = make_current_principal_dep(
        get_session=lambda: None,
        secret_key="k" * 32,
        secure_cookie=False,
    )
    assert callable(dep)
