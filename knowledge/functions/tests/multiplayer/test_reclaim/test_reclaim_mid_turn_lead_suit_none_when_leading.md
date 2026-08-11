---
type: Python Function
title: test_reclaim_mid_turn_lead_suit_none_when_leading
resource: tests/multiplayer/test_reclaim.py#L348-L369
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type
---

# Signature

`async def test_reclaim_mid_turn_lead_suit_none_when_leading():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [all_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type.md)