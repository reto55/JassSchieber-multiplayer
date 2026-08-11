---
type: Python Function
title: test_reclaim_into_room_with_connected_host_does_not_promote
resource: tests/multiplayer/test_host_transfer.py#L127-L153
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/principal_id
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_reclaim_into_room_with_connected_host_does_not_promote():`

# Calls

- [principal_id](../../../../functions/ausbau/room/principal_id.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)