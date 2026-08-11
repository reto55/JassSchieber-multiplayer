---
type: Python Function
title: test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target
resource: tests/multiplayer/test_host_transfer.py#L241-L289
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target( client, client_other, ):`

# Calls

- [get_room](../../../../functions/ausbau/room/get_room.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)