---
type: Python Function
title: get_valid_cards
resource: ausbau/game_session.py#L74-L167
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/game_session/code_to_card
  called_by:
  - functions/ausbau/ai_strategies/EasyStrategy/pick_card
  - functions/ausbau/ai_strategies/HardStrategy/pick_card
  - functions/ausbau/game_session/ai_select_card
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid
  - functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick
  - functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners
  - functions/tests/test_game_session/test_valid_cards_leading_all_valid
  - functions/tests/test_game_session/test_valid_cards_must_follow_suit
  - functions/tests/test_game_session/test_valid_cards_cannot_follow_suit
  - functions/tests/test_game_session/test_valid_cards_any_trump_always_playable
  - functions/tests/test_game_session/test_underholdback_trump_led_only_under_any_card
  - functions/tests/test_game_session/test_underholdback_trump_led_under_plus_other_trump_must_follow
  - functions/tests/test_game_session/test_trump_led_no_trump_any_card
  - functions/tests/test_game_session/test_nontrump_led_no_trump_played_may_follow_or_trump
  - functions/tests/test_game_session/test_no_undertrumping_with_nontrump_in_hand
  - functions/tests/test_game_session/test_no_undertrumping_overtrump_allowed
  - functions/tests/test_game_session/test_no_undertrumping_must_beat_highest_of_multiple_trumps
  - functions/tests/test_game_session/test_all_trump_hand_forced_undertrump_allowed
  - functions/tests/test_game_session/test_no_undertrump_discard_nontrump_when_cant_overtrump
  - functions/tests/test_game_session/test_oben_mode_unaffected_must_follow
  - functions/tests/test_game_session/test_unten_mode_cant_follow_any_card
---

# Signature

`def get_valid_cards( hand: dict, lead_suit: Optional[str], operator: str, trick_so_far: Optional[list] = None, ) -> list:`

# Calls

- [card_to_code](../../../functions/ausbau/game_session/card_to_code.md)
- [code_to_card](../../../functions/ausbau/game_session/code_to_card.md)

# Called by

- [pick_card](../../../functions/ausbau/ai_strategies/EasyStrategy/pick_card.md)
- [pick_card](../../../functions/ausbau/ai_strategies/HardStrategy/pick_card.md)
- [ai_select_card](../../../functions/ausbau/game_session/ai_select_card.md)
- [_reclaim_seat](../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [_play_trick](../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [_queue_seat_plays_first_valid](../../../functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid.md)
- [_queue_first_valid_for_trick](../../../functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick.md)
- [test_play_trick_appends_to_spiel_winners](../../../functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners.md)
- [test_valid_cards_leading_all_valid](../../../functions/tests/test_game_session/test_valid_cards_leading_all_valid.md)
- [test_valid_cards_must_follow_suit](../../../functions/tests/test_game_session/test_valid_cards_must_follow_suit.md)
- [test_valid_cards_cannot_follow_suit](../../../functions/tests/test_game_session/test_valid_cards_cannot_follow_suit.md)
- [test_valid_cards_any_trump_always_playable](../../../functions/tests/test_game_session/test_valid_cards_any_trump_always_playable.md)
- [test_underholdback_trump_led_only_under_any_card](../../../functions/tests/test_game_session/test_underholdback_trump_led_only_under_any_card.md)
- [test_underholdback_trump_led_under_plus_other_trump_must_follow](../../../functions/tests/test_game_session/test_underholdback_trump_led_under_plus_other_trump_must_follow.md)
- [test_trump_led_no_trump_any_card](../../../functions/tests/test_game_session/test_trump_led_no_trump_any_card.md)
- [test_nontrump_led_no_trump_played_may_follow_or_trump](../../../functions/tests/test_game_session/test_nontrump_led_no_trump_played_may_follow_or_trump.md)
- [test_no_undertrumping_with_nontrump_in_hand](../../../functions/tests/test_game_session/test_no_undertrumping_with_nontrump_in_hand.md)
- [test_no_undertrumping_overtrump_allowed](../../../functions/tests/test_game_session/test_no_undertrumping_overtrump_allowed.md)
- [test_no_undertrumping_must_beat_highest_of_multiple_trumps](../../../functions/tests/test_game_session/test_no_undertrumping_must_beat_highest_of_multiple_trumps.md)
- [test_all_trump_hand_forced_undertrump_allowed](../../../functions/tests/test_game_session/test_all_trump_hand_forced_undertrump_allowed.md)
- [test_no_undertrump_discard_nontrump_when_cant_overtrump](../../../functions/tests/test_game_session/test_no_undertrump_discard_nontrump_when_cant_overtrump.md)
- [test_oben_mode_unaffected_must_follow](../../../functions/tests/test_game_session/test_oben_mode_unaffected_must_follow.md)
- [test_unten_mode_cant_follow_any_card](../../../functions/tests/test_game_session/test_unten_mode_cant_follow_any_card.md)