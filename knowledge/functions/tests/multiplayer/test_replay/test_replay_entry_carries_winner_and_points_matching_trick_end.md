---
type: Python Function
title: test_replay_entry_carries_winner_and_points_matching_trick_end
resource: tests/multiplayer/test_replay.py#L143-L160
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_replay_entry_carries_winner_and_points_matching_trick_end():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_queue_first_valid_for_trick](../../../../functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick.md)
- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)