---
type: Python Function
title: test_reclaim_into_hostless_room_promotes_reconnecting_human
resource: tests/multiplayer/test_host_transfer.py#L69-L124
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/principal_id
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_reclaim_into_hostless_room_promotes_reconnecting_human(fast_clock):`

# Calls

- [principal_id](../../../../functions/ausbau/room/principal_id.md)
- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)