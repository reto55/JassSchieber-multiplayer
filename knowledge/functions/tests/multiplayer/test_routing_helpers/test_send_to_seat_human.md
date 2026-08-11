---
type: Python Function
title: test_send_to_seat_human
resource: tests/multiplayer/test_routing_helpers.py#L11-L18
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_send_to_seat_human(fake_ws):`

# Calls

- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)