import pytest
from ausbau.room import create_room, Variant
from frontend.auth.guest import Guest


pytestmark = pytest.mark.asyncio


async def test_seat_for_principal_for_seat_owner():
    """When a principal owns a seat, _seat_for_principal finds them."""
    g = Guest(guest_id='a' * 32)
    room = create_room(host=g, variant=Variant())
    seat = room._seat_for_principal(g)
    assert seat is not None
    assert seat.position == "compo"


async def test_ws_endpoint_registered():
    """The /ws/{code} endpoint is registered in the FastAPI app."""
    from ausbau.server import app
    paths = [r.path for r in app.routes if hasattr(r, 'path')]
    assert "/ws/{code}" in paths
