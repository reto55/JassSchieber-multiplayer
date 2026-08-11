---
type: Python Function
title: _hand
resource: tests/multiplayer/test_ai_pimc.py#L12-L18
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/Cards_refactored/create_card
  called_by:
  - functions/tests/multiplayer/test_ai_pimc/test_engine_state_holds_fields
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_capacities_and_partitions_unseen
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_voids
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_under_holdback_only_under_to_voided_player
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_is_deterministic_under_seed
  - functions/tests/multiplayer/test_ai_pimc/test_rollout_is_deterministic
  - functions/tests/multiplayer/test_ai_pimc/test_rollout_points_are_bounded_and_nonnegative
  - functions/tests/multiplayer/test_ai_pimc/_endgame_state
  - functions/tests/multiplayer/test_ai_pimc/test_rollout_raises_descriptive_error_on_empty_hand
---

# Signature

`def _hand(suit_to_suffixes):`

# Calls

- [create_card](../../../../functions/Cards_refactored/create_card.md)

# Called by

- [test_engine_state_holds_fields](../../../../functions/tests/multiplayer/test_ai_pimc/test_engine_state_holds_fields.md)
- [test_sampler_respects_capacities_and_partitions_unseen](../../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_capacities_and_partitions_unseen.md)
- [test_sampler_respects_voids](../../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_voids.md)
- [test_sampler_under_holdback_only_under_to_voided_player](../../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_under_holdback_only_under_to_voided_player.md)
- [test_sampler_is_deterministic_under_seed](../../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_is_deterministic_under_seed.md)
- [test_rollout_is_deterministic](../../../../functions/tests/multiplayer/test_ai_pimc/test_rollout_is_deterministic.md)
- [test_rollout_points_are_bounded_and_nonnegative](../../../../functions/tests/multiplayer/test_ai_pimc/test_rollout_points_are_bounded_and_nonnegative.md)
- [_endgame_state](../../../../functions/tests/multiplayer/test_ai_pimc/_endgame_state.md)
- [test_rollout_raises_descriptive_error_on_empty_hand](../../../../functions/tests/multiplayer/test_ai_pimc/test_rollout_raises_descriptive_error_on_empty_hand.md)