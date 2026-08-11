---
type: Python Function
title: test_broadcast_except_seat
resource: tests/multiplayer/test_routing_helpers.py#L41-L51
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_broadcast_except_seat():`

# Calls

- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)