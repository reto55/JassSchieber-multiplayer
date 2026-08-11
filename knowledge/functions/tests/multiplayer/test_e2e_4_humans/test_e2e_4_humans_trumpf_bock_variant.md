---
type: Python Function
title: test_e2e_4_humans_trumpf_bock_variant
resource: tests/multiplayer/test_e2e_4_humans.py#L179-L238
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_e2e_4_humans/_fresh_4_human_session
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/start_game
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
  - functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type
---

# Signature

`async def test_e2e_4_humans_trumpf_bock_variant(fast_clock):`

# Calls

- [_fresh_4_human_session](../../../../functions/tests/multiplayer/test_e2e_4_humans/_fresh_4_human_session.md)
- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [start_game](../../../../functions/ausbau/game_session/GameSession/start_game.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)
- [all_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type.md)