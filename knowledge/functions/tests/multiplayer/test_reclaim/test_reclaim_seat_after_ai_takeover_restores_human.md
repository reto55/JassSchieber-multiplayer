---
type: Python Function
title: test_reclaim_seat_after_ai_takeover_restores_human
resource: tests/multiplayer/test_reclaim.py#L83-L104
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_reclaim_seat
---

# Signature

`async def test_reclaim_seat_after_ai_takeover_restores_human():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)