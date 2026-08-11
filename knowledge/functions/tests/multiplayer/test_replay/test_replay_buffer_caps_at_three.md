---
type: Python Function
title: test_replay_buffer_caps_at_three
resource: tests/multiplayer/test_replay.py#L120-L140
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick
  - functions/ausbau/game_session/GameSession/_play_trick
---

# Signature

`async def test_replay_buffer_caps_at_three():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_queue_first_valid_for_trick](../../../../functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick.md)
- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)