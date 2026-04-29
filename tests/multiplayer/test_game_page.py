"""Smoke tests for the multiplayer game page (Task 23, spec §11.5).

These verify that the static game HTML, JS, and CSS are reachable and that
the JS speaks the multi-WS protocol. We do not exercise DOM behaviour here
(per spec §11.5 — manual browser smoke is the integration check).
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


async def test_game_page_serves_html(client):
    r = await client.get("/")
    assert r.status_code == 200, r.text
    body = r.text
    assert "Schieber" in body
    # The JS bootstraps the page; make sure it's referenced.
    assert "schieber.js" in body


async def test_game_js_speaks_multi_ws_protocol(client):
    """The schieber.js file must address /ws/{code} and the multi-seat message
    types defined by the schieber-protocol skill."""
    r = await client.get("/static/js/schieber.js")
    assert r.status_code == 200
    body = r.text

    # URL pattern: /ws/{code} — code is read from ?code= query param.
    assert "/ws/" in body
    assert "ROOM_CODE" in body or "code" in body

    # Server → client message types we handle.
    for mtype in (
        "game_start",
        "room_resume",
        "trump_request",
        "trump_pending",
        "trump_chosen",
        "weis_request",
        "weis_resolution",
        "play_request",
        "play_pending",
        "card_played",
        "trick_end",
        "spiel_end",
        "game_end",
        "seat_paused",
        "seat_reclaimed",
        "seat_ai_takeover",
        "host_changed",
    ):
        assert mtype in body, f"missing handler for {mtype} in schieber.js"

    # Client → server message types we send.
    for mtype in ("choose_trump", "schieben", "announce_weis", "play_card"):
        assert mtype in body, f"missing sender for {mtype} in schieber.js"

    # The legacy single-WS path must NOT be present.
    assert "declare_weis" not in body, (
        "schieber.js still references legacy 'declare_weis' — "
        "multi-seat path uses 'announce_weis'."
    )


async def test_game_css_paused_class(client):
    """The CSS adds a `.paused` style for pause overlays (Task 23)."""
    r = await client.get("/static/css/game.css")
    assert r.status_code == 200
    body = r.text
    assert ".paused" in body
