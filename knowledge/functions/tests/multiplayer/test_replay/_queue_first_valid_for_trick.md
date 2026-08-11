---
type: Python Function
title: _queue_first_valid_for_trick
resource: tests/multiplayer/test_replay.py#L54-L88
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/get_valid_cards
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/game_session/GameSession/_seat
  called_by:
  - functions/tests/multiplayer/test_replay/test_replay_buffer_appends_one_trick
  - functions/tests/multiplayer/test_replay/test_replay_buffer_caps_at_three
  - functions/tests/multiplayer/test_replay/test_replay_entry_carries_winner_and_points_matching_trick_end
---

# Signature

`def _queue_first_valid_for_trick(s, play):`

# Calls

- [get_valid_cards](../../../../functions/ausbau/game_session/get_valid_cards.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)

# Called by

- [test_replay_buffer_appends_one_trick](../../../../functions/tests/multiplayer/test_replay/test_replay_buffer_appends_one_trick.md)
- [test_replay_buffer_caps_at_three](../../../../functions/tests/multiplayer/test_replay/test_replay_buffer_caps_at_three.md)
- [test_replay_entry_carries_winner_and_points_matching_trick_end](../../../../functions/tests/multiplayer/test_replay/test_replay_entry_carries_winner_and_points_matching_trick_end.md)