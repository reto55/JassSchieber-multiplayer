---
type: Python Function
title: create_card
resource: Cards_refactored.py#L124-L139
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/Cards_refactored/Deck/__init__
  - functions/ausbau/game_session/code_to_card
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_set_hand
  - functions/tests/multiplayer/test_ai_pimc/_hand
  - functions/tests/multiplayer/test_ai_pimc/test_engine_state_holds_fields
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_capacities_and_partitions_unseen
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_voids
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_under_holdback_only_under_to_voided_player
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_is_deterministic_under_seed
  - functions/tests/multiplayer/test_ai_pimc/test_rollout_is_deterministic
  - functions/tests/multiplayer/test_ai_pimc/test_rollout_points_are_bounded_and_nonnegative
  - functions/tests/multiplayer/test_ai_pimc/_endgame_state
  - functions/tests/multiplayer/test_ai_pimc/_make_strat
  - functions/tests/multiplayer/test_ai_pimc/test_rollout_raises_descriptive_error_on_empty_hand
  - functions/tests/multiplayer/test_ai_pimc/test_lead_uses_pimc_when_enabled
  - functions/tests/multiplayer/test_ai_strategies/_hand_with_suits
---

# Signature

`def create_card(rank, suit):`

# Called by

- [__init__](../../functions/Cards_refactored/Deck/__init__.md)
- [code_to_card](../../functions/ausbau/game_session/code_to_card.md)
- [_set_hand](../../functions/tests/multiplayer/test_ai_hard_trump_draw/_set_hand.md)
- [_hand](../../functions/tests/multiplayer/test_ai_pimc/_hand.md)
- [test_engine_state_holds_fields](../../functions/tests/multiplayer/test_ai_pimc/test_engine_state_holds_fields.md)
- [test_sampler_respects_capacities_and_partitions_unseen](../../functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_capacities_and_partitions_unseen.md)
- [test_sampler_respects_voids](../../functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_voids.md)
- [test_sampler_under_holdback_only_under_to_voided_player](../../functions/tests/multiplayer/test_ai_pimc/test_sampler_under_holdback_only_under_to_voided_player.md)
- [test_sampler_is_deterministic_under_seed](../../functions/tests/multiplayer/test_ai_pimc/test_sampler_is_deterministic_under_seed.md)
- [test_rollout_is_deterministic](../../functions/tests/multiplayer/test_ai_pimc/test_rollout_is_deterministic.md)
- [test_rollout_points_are_bounded_and_nonnegative](../../functions/tests/multiplayer/test_ai_pimc/test_rollout_points_are_bounded_and_nonnegative.md)
- [_endgame_state](../../functions/tests/multiplayer/test_ai_pimc/_endgame_state.md)
- [_make_strat](../../functions/tests/multiplayer/test_ai_pimc/_make_strat.md)
- [test_rollout_raises_descriptive_error_on_empty_hand](../../functions/tests/multiplayer/test_ai_pimc/test_rollout_raises_descriptive_error_on_empty_hand.md)
- [test_lead_uses_pimc_when_enabled](../../functions/tests/multiplayer/test_ai_pimc/test_lead_uses_pimc_when_enabled.md)
- [_hand_with_suits](../../functions/tests/multiplayer/test_ai_strategies/_hand_with_suits.md)