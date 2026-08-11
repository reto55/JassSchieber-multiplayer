---
type: Python Function
title: test_weis_phase_rejects_wrong_type_then_re_prompts
resource: tests/multiplayer/test_weis_phase.py#L229-L280
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_seat
  - functions/tests/multiplayer/test_weis_phase/_describe_weis_per_position
  - functions/ausbau/game_session/GameSession/_weis_phase
  - functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_weis_phase_rejects_wrong_type_then_re_prompts():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_describe_weis_per_position](../../../../functions/tests/multiplayer/test_weis_phase/_describe_weis_per_position.md)
- [_weis_phase](../../../../functions/ausbau/game_session/GameSession/_weis_phase.md)
- [all_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)