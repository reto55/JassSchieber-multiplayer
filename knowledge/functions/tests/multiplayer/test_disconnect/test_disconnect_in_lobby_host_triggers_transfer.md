---
type: Python Function
title: test_disconnect_in_lobby_host_triggers_transfer
resource: tests/multiplayer/test_disconnect.py#L78-L116
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_disconnect_in_lobby_host_triggers_transfer():`

# Calls

- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)