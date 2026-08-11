---
type: Python Module
title: test_game_session
resource: tests/test_game_session.py#L1-L357
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/sys
  - external/os
  - external/cards-refactored
  - external/ausbau-game-session
---

# Contains

- [test_card_to_code_eicheln_ass](../../functions/tests/test_game_session/test_card_to_code_eicheln_ass.md)
- [test_card_to_code_schellen_koenig](../../functions/tests/test_game_session/test_card_to_code_schellen_koenig.md)
- [test_card_to_code_schilten_under](../../functions/tests/test_game_session/test_card_to_code_schilten_under.md)
- [test_card_to_code_rosen_sechs](../../functions/tests/test_game_session/test_card_to_code_rosen_sechs.md)
- [test_hand_to_codes_returns_all](../../functions/tests/test_game_session/test_hand_to_codes_returns_all.md)
- [test_find_card_in_hand_found](../../functions/tests/test_game_session/test_find_card_in_hand_found.md)
- [test_find_card_in_hand_not_found](../../functions/tests/test_game_session/test_find_card_in_hand_not_found.md)
- [test_valid_cards_leading_all_valid](../../functions/tests/test_game_session/test_valid_cards_leading_all_valid.md)
- [test_valid_cards_must_follow_suit](../../functions/tests/test_game_session/test_valid_cards_must_follow_suit.md)
- [test_valid_cards_cannot_follow_suit](../../functions/tests/test_game_session/test_valid_cards_cannot_follow_suit.md)
- [test_valid_cards_any_trump_always_playable](../../functions/tests/test_game_session/test_valid_cards_any_trump_always_playable.md)
- [test_underholdback_trump_led_only_under_any_card](../../functions/tests/test_game_session/test_underholdback_trump_led_only_under_any_card.md)
- [test_underholdback_trump_led_under_plus_other_trump_must_follow](../../functions/tests/test_game_session/test_underholdback_trump_led_under_plus_other_trump_must_follow.md)
- [test_trump_led_no_trump_any_card](../../functions/tests/test_game_session/test_trump_led_no_trump_any_card.md)
- [test_nontrump_led_no_trump_played_may_follow_or_trump](../../functions/tests/test_game_session/test_nontrump_led_no_trump_played_may_follow_or_trump.md)
- [test_no_undertrumping_with_nontrump_in_hand](../../functions/tests/test_game_session/test_no_undertrumping_with_nontrump_in_hand.md)
- [test_no_undertrumping_overtrump_allowed](../../functions/tests/test_game_session/test_no_undertrumping_overtrump_allowed.md)
- [test_no_undertrumping_must_beat_highest_of_multiple_trumps](../../functions/tests/test_game_session/test_no_undertrumping_must_beat_highest_of_multiple_trumps.md)
- [test_all_trump_hand_forced_undertrump_allowed](../../functions/tests/test_game_session/test_all_trump_hand_forced_undertrump_allowed.md)
- [test_no_undertrump_discard_nontrump_when_cant_overtrump](../../functions/tests/test_game_session/test_no_undertrump_discard_nontrump_when_cant_overtrump.md)
- [test_oben_mode_unaffected_must_follow](../../functions/tests/test_game_session/test_oben_mode_unaffected_must_follow.md)
- [test_unten_mode_cant_follow_any_card](../../functions/tests/test_game_session/test_unten_mode_cant_follow_any_card.md)
- [test_trick_winner_trump_beats_lead](../../functions/tests/test_game_session/test_trick_winner_trump_beats_lead.md)
- [test_trick_winner_highest_lead_suit_wins](../../functions/tests/test_game_session/test_trick_winner_highest_lead_suit_wins.md)
- [test_trick_points_oben_mode](../../functions/tests/test_game_session/test_trick_points_oben_mode.md)
- [test_trick_points_trumpf_mode](../../functions/tests/test_game_session/test_trick_points_trumpf_mode.md)
- [test_ai_leads_plays_highest_value](../../functions/tests/test_game_session/test_ai_leads_plays_highest_value.md)
- [test_ai_follows_plays_lowest_value](../../functions/tests/test_game_session/test_ai_follows_plays_lowest_value.md)
- [test_describe_weis_dreier](../../functions/tests/test_game_session/test_describe_weis_dreier.md)
- [test_describe_weis_vierter](../../functions/tests/test_game_session/test_describe_weis_vierter.md)
- [test_describe_weis_fuenfer](../../functions/tests/test_game_session/test_describe_weis_fuenfer.md)
- [test_describe_weis_viererle](../../functions/tests/test_game_session/test_describe_weis_viererle.md)
- [test_detect_stock_true](../../functions/tests/test_game_session/test_detect_stock_true.md)
- [test_detect_stock_false_wrong_suit](../../functions/tests/test_game_session/test_detect_stock_false_wrong_suit.md)
- [test_detect_stock_false_missing_ober](../../functions/tests/test_game_session/test_detect_stock_false_missing_ober.md)
- [test_initial_state_structure](../../functions/tests/test_game_session/test_initial_state_structure.md)
- [test_initial_state_scores_accumulate](../../functions/tests/test_game_session/test_initial_state_scores_accumulate.md)

# Imports

- `sys`
- `os`
- `Cards_refactored`
- `ausbau.game_session`