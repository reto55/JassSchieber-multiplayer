import pytest
import asyncio


pytestmark = pytest.mark.asyncio


async def test_fake_ws_send_recv(fake_ws):
    await fake_ws.send_json({"type": "hello"})
    fake_ws.push({"type": "hi"})
    msg = await fake_ws.receive_json()
    assert msg == {"type": "hi"}
    assert fake_ws.sent == [{"type": "hello"}]
    assert fake_ws.last_sent_of_type("hello") == {"type": "hello"}


async def test_fake_ws_close(fake_ws):
    await fake_ws.close(code=1008, reason="bye")
    assert fake_ws.closed is True
    assert fake_ws.close_code == 1008
    assert fake_ws.close_reason == "bye"


async def test_fast_clock(fast_clock):
    import time
    t0 = time.monotonic()
    await asyncio.sleep(60.0)  # would normally take 60 s
    t1 = time.monotonic()
    assert (t1 - t0) < 1.0  # actually returns instantly


def test_rooms_isolated_per_test():
    from ausbau.room import ROOMS, create_room, Variant
    from frontend.auth.guest import Guest
    g = Guest(guest_id='a' * 32)
    create_room(host=g, variant=Variant())
    assert len(ROOMS) == 1


def test_rooms_isolated_per_test_round2():
    from ausbau.room import ROOMS
    # autouse fixture should have cleared ROOMS between tests
    assert len(ROOMS) == 0
