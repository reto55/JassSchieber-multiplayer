---
type: Python Function
title: _queue_seat_plays_first_valid
resource: tests/multiplayer/test_play_trick.py#L49-L89
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/get_valid_cards
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/game_session/GameSession/_seat
  called_by:
  - functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round
  - functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts
  - functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts
  - functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far
  - functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat
  - functions/tests/multiplayer/test_play_trick/test_play_trick_updates_current_seat_turn_per_iteration
---

# Signature

`def _queue_seat_plays_first_valid(s, play, seat_order):`

# Calls

- [get_valid_cards](../../../../functions/ausbau/game_session/get_valid_cards.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)

# Called by

- [test_play_trick_4_humans_one_round](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round.md)
- [test_play_trick_invalid_card_re_prompts](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts.md)
- [test_play_trick_wrong_type_re_prompts](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts.md)
- [test_play_trick_pending_carries_trick_so_far](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far.md)
- [test_play_trick_request_only_to_active_seat](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat.md)
- [test_play_trick_updates_current_seat_turn_per_iteration](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_updates_current_seat_turn_per_iteration.md)