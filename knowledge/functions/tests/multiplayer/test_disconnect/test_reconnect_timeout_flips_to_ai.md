---
type: Python Function
title: test_reconnect_timeout_flips_to_ai
resource: tests/multiplayer/test_disconnect.py#L188-L211
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_reconnect_timeout
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_reconnect_timeout_flips_to_ai(fast_clock):`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_reconnect_timeout](../../../../functions/ausbau/game_session/GameSession/_reconnect_timeout.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)