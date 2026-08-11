---
type: Python Function
title: test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state
resource: tests/multiplayer/test_trump_phase.py#L63-L100
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_trump_phase
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
  - functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type
---

# Signature

`async def test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_trump_phase](../../../../functions/ausbau/game_session/GameSession/_trump_phase.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)
- [all_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type.md)