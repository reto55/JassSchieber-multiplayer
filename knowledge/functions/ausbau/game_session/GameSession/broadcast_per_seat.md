---
type: Python Method
title: broadcast_per_seat
resource: ausbau/game_session.py#L475-L485
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/send_json
  called_by:
  - functions/ausbau/game_session/GameSession/_run_spiel
  - functions/tests/multiplayer/test_routing_helpers/test_broadcast_per_seat_factory
---

# Signature

`async def broadcast_per_seat(self, msg_factory) -> None:`

# Calls

- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [send_json](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/send_json.md)

# Called by

- [_run_spiel](../../../../functions/ausbau/game_session/GameSession/_run_spiel.md)
- [test_broadcast_per_seat_factory](../../../../functions/tests/multiplayer/test_routing_helpers/test_broadcast_per_seat_factory.md)