"""Smoke tests for the lobby page (Task 22, spec §4.6).

These verify that the static lobby HTML, JS, and CSS are reachable through
the FastAPI server and that the HTML wires up the JS asset. We do not
exercise DOM behaviour (deferred per spec §11.5 — manual browser smoke).
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def client():
    from ausbau.server import app as srv_app
    async with AsyncClient(transport=ASGITransport(app=srv_app),
                           base_url="http://test") as c:
        yield c


async def test_lobby_page_serves_html(client):
    r = await client.get("/lobby?code=ABCDEF")
    assert r.status_code == 200, r.text
    body = r.text
    assert "Schieber Room" in body
    # The JS bootstraps the page; make sure it's referenced.
    assert "lobby.js" in body


async def test_lobby_page_lists_action_buttons(client):
    r = await client.get("/lobby?code=ABCDEF")
    assert r.status_code == 200
    body = r.text
    # Sanity-check the action buttons exist by id.
    for btn_id in ("btn-join", "btn-leave", "btn-spectate", "btn-start"):
        assert f'id="{btn_id}"' in body, f"missing #{btn_id} in lobby.html"


async def test_lobby_static_assets_served(client):
    """The JS+CSS the lobby page loads must be reachable through /static."""
    r_js = await client.get("/static/js/lobby.js")
    assert r_js.status_code == 200
    # Sanity: it is the lobby JS (not e.g. game.js).
    assert "lobby" in r_js.text.lower()
    # Verify it talks to the right endpoints.
    body = r_js.text
    assert f"/rooms/" in body
    assert "/ws/" in body
    assert "X-Requested-With" in body

    r_css = await client.get("/static/css/lobby.css")
    assert r_css.status_code == 200
