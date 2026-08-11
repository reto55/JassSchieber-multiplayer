---
type: Python Function
title: test_play_trick_4_humans_one_round
resource: tests/multiplayer/test_play_trick.py#L92-L161
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_play_trick_4_humans_one_round():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_queue_seat_plays_first_valid](../../../../functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid.md)
- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [all_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)