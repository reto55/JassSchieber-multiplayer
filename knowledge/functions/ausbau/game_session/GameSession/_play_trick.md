---
type: Python Method
title: _play_trick
resource: ausbau/game_session.py#L1150-L1334
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/get_valid_cards
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/game_session/GameSession/_await_seat_action
  - functions/ausbau/game_session/find_card_in_hand
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/game_session/determine_trick_winner
  - functions/ausbau/game_session/trick_points
  - functions/ausbau/game_session/GameSession/_commit_pending_swap
  called_by:
  - functions/ausbau/game_session/GameSession/_run_spiel
  - functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round
  - functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts
  - functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts
  - functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far
  - functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat
  - functions/tests/multiplayer/test_play_trick/test_play_trick_updates_current_seat_turn_per_iteration
  - functions/tests/multiplayer/test_replay/test_replay_buffer_appends_one_trick
  - functions/tests/multiplayer/test_replay/test_replay_buffer_caps_at_three
  - functions/tests/multiplayer/test_replay/test_replay_entry_carries_winner_and_points_matching_trick_end
  - functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners
---

# Signature

`async def _play_trick(self, play: Play) -> tuple:`

# Calls

- [get_valid_cards](../../../../functions/ausbau/game_session/get_valid_cards.md)
- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [_await_seat_action](../../../../functions/ausbau/game_session/GameSession/_await_seat_action.md)
- [find_card_in_hand](../../../../functions/ausbau/game_session/find_card_in_hand.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)
- [determine_trick_winner](../../../../functions/ausbau/game_session/determine_trick_winner.md)
- [trick_points](../../../../functions/ausbau/game_session/trick_points.md)
- [_commit_pending_swap](../../../../functions/ausbau/game_session/GameSession/_commit_pending_swap.md)

# Called by

- [_run_spiel](../../../../functions/ausbau/game_session/GameSession/_run_spiel.md)
- [test_play_trick_4_humans_one_round](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round.md)
- [test_play_trick_invalid_card_re_prompts](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts.md)
- [test_play_trick_wrong_type_re_prompts](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts.md)
- [test_play_trick_pending_carries_trick_so_far](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far.md)
- [test_play_trick_request_only_to_active_seat](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat.md)
- [test_play_trick_updates_current_seat_turn_per_iteration](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_updates_current_seat_turn_per_iteration.md)
- [test_replay_buffer_appends_one_trick](../../../../functions/tests/multiplayer/test_replay/test_replay_buffer_appends_one_trick.md)
- [test_replay_buffer_caps_at_three](../../../../functions/tests/multiplayer/test_replay/test_replay_buffer_caps_at_three.md)
- [test_replay_entry_carries_winner_and_points_matching_trick_end](../../../../functions/tests/multiplayer/test_replay/test_replay_entry_carries_winner_and_points_matching_trick_end.md)
- [test_play_trick_appends_to_spiel_winners](../../../../functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners.md)