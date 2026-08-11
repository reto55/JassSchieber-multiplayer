---
type: Python Function
title: test_play_trick_updates_current_seat_turn_per_iteration
resource: tests/multiplayer/test_play_trick.py#L319-L368
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid
  - functions/ausbau/game_session/GameSession/_play_trick
---

# Signature

`async def test_play_trick_updates_current_seat_turn_per_iteration():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_queue_seat_plays_first_valid](../../../../functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid.md)
- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)