---
type: Python Function
title: rollout
resource: ausbau/ai_pimc.py#L134-L195
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/ai_pimc/_clone_hand
  - functions/ausbau/ai_pimc/_remove_card
  - functions/ausbau/ai_pimc/_order_from
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/game_session/ai_select_card
  - functions/ausbau/game_session/determine_trick_winner
  - functions/ausbau/game_session/trick_points
  - functions/ausbau/game_session/_mode_multiplier
  called_by:
  - functions/ausbau/ai_pimc/pimc_choose_lead
  - functions/tests/multiplayer/test_ai_pimc/test_rollout_is_deterministic
  - functions/tests/multiplayer/test_ai_pimc/test_rollout_points_are_bounded_and_nonnegative
  - functions/tests/multiplayer/test_ai_pimc/test_rollout_raises_descriptive_error_on_empty_hand
---

# Signature

`def rollout(state: EngineState, deal: dict, lead_card) -> int:`

# Calls

- [_clone_hand](../../../functions/ausbau/ai_pimc/_clone_hand.md)
- [_remove_card](../../../functions/ausbau/ai_pimc/_remove_card.md)
- [_order_from](../../../functions/ausbau/ai_pimc/_order_from.md)
- [card_to_code](../../../functions/ausbau/game_session/card_to_code.md)
- [ai_select_card](../../../functions/ausbau/game_session/ai_select_card.md)
- [determine_trick_winner](../../../functions/ausbau/game_session/determine_trick_winner.md)
- [trick_points](../../../functions/ausbau/game_session/trick_points.md)
- [_mode_multiplier](../../../functions/ausbau/game_session/_mode_multiplier.md)

# Called by

- [pimc_choose_lead](../../../functions/ausbau/ai_pimc/pimc_choose_lead.md)
- [test_rollout_is_deterministic](../../../functions/tests/multiplayer/test_ai_pimc/test_rollout_is_deterministic.md)
- [test_rollout_points_are_bounded_and_nonnegative](../../../functions/tests/multiplayer/test_ai_pimc/test_rollout_points_are_bounded_and_nonnegative.md)
- [test_rollout_raises_descriptive_error_on_empty_hand](../../../functions/tests/multiplayer/test_ai_pimc/test_rollout_raises_descriptive_error_on_empty_hand.md)