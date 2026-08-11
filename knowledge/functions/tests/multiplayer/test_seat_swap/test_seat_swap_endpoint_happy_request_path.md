---
type: Python Function
title: test_seat_swap_endpoint_happy_request_path
resource: tests/multiplayer/test_seat_swap.py#L315-L343
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_seat_swap_endpoint_happy_request_path(client, client_other):`

# Calls

- [get_room](../../../../functions/ausbau/room/get_room.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)