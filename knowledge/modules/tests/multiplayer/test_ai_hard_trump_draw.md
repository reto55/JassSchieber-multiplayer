---
type: Python Module
title: test_ai_hard_trump_draw
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L1-L361
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/pytest
  - external/cards-refactored
  - external/ausbau-ai-strategies
  - external/ausbau-game-session
  - external/sys
---

# Contains

- [_set_hand](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_set_hand.md)
- [_make](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)
- [_drive_both_opponents_void](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_drive_both_opponents_void.md)
- [_play_out_trumps](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_play_out_trumps.md)
- [test_leads_highest_trump_fresh_spiel](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_leads_highest_trump_fresh_spiel.md)
- [test_drawing_takes_priority_over_guaranteed_side_winner](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_drawing_takes_priority_over_guaranteed_side_winner.md)
- [test_keeps_drawing_while_one_opponent_may_hold_trump](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_keeps_drawing_while_one_opponent_may_hold_trump.md)
- [test_one_trump_out_lacks_boss_does_not_lead_trump](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_one_trump_out_lacks_boss_does_not_lead_trump.md)
- [test_one_trump_out_lacks_boss_no_trump_in_hand_unaffected](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_one_trump_out_lacks_boss_no_trump_in_hand_unaffected.md)
- [test_one_trump_out_holds_boss_still_leads_trump](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_one_trump_out_holds_boss_still_leads_trump.md)
- [test_two_trumps_out_lacks_boss_still_draws](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_two_trumps_out_lacks_boss_still_draws.md)
- [test_stops_trump_and_leads_guaranteed_winner](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_stops_trump_and_leads_guaranteed_winner.md)
- [test_stops_trump_and_leads_opponent_shown_side_suit](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_stops_trump_and_leads_opponent_shown_side_suit.md)
- [test_both_void_unshown_suit_never_leads_trump](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_both_void_unshown_suit_never_leads_trump.md)
- [test_both_void_all_trump_hand_leads_trump](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_both_void_all_trump_hand_leads_trump.md)
- [test_does_not_lead_trump_when_both_void](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_does_not_lead_trump_when_both_void.md)
- [test_both_void_never_cashes_guaranteed_trump_winner](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_both_void_never_cashes_guaranteed_trump_winner.md)
- [test_stops_trump_when_all_outstanding_trumps_played](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_stops_trump_when_all_outstanding_trumps_played.md)
- [test_no_trump_outstanding_cashes_trump_winner](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_no_trump_outstanding_cashes_trump_winner.md)
- [test_no_trump_in_hand_leads_guaranteed_winner](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_no_trump_in_hand_leads_guaranteed_winner.md)
- [test_only_discarding_opponent_flagged_void](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_only_discarding_opponent_flagged_void.md)
- [test_partner_discard_does_not_flag_opponent](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_partner_discard_does_not_flag_opponent.md)
- [test_non_trump_lead_does_not_flag_void](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_non_trump_lead_does_not_flag_void.md)
- [test_trick_resets_after_four_cards](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_trick_resets_after_four_cards.md)
- [test_shown_suits_tracked_for_opponents_not_self](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_shown_suits_tracked_for_opponents_not_self.md)
- [test_on_spiel_start_resets_trump_draw_state](../../../functions/tests/multiplayer/test_ai_hard_trump_draw/test_on_spiel_start_resets_trump_draw_state.md)

# Imports

- `pytest`
- `Cards_refactored`
- `ausbau.ai_strategies`
- `ausbau.game_session`
- `sys`