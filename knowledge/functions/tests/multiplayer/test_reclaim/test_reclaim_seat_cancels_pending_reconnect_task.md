---
type: Python Function
title: test_reclaim_seat_cancels_pending_reconnect_task
resource: tests/multiplayer/test_reclaim.py#L47-L80
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/ausbau/game_session/GameSession/_reclaim_seat
---

# Signature

`async def test_reclaim_seat_cancels_pending_reconnect_task():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)