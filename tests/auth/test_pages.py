import pytest

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("path,heading", [
    ("/login", "Sign in"),
    ("/signup", "Create account"),
    ("/forgot", "Forgot password"),
    ("/reset", "Reset password"),
    ("/account", "Account"),
    ("/admin", "Admin"),
])
async def test_page_renders(client, path, heading):
    r = await client.get(path)
    assert r.status_code == 200
    assert heading in r.text
