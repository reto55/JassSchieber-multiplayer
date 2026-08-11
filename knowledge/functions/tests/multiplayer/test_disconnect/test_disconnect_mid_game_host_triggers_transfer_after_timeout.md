---
type: Python Function
title: test_disconnect_mid_game_host_triggers_transfer_after_timeout
resource: tests/multiplayer/test_disconnect.py#L236-L270
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_disconnect_mid_game_host_triggers_transfer_after_timeout(fast_clock):`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)