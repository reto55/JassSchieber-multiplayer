---
type: Python Function
title: test_trump_phase_human_picks_eicheln
resource: tests/multiplayer/test_trump_phase.py#L18-L39
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_trump_phase
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_trump_phase_human_picks_eicheln():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_trump_phase](../../../../functions/ausbau/game_session/GameSession/_trump_phase.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)