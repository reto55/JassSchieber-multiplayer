---
type: Python Module
title: test_ai_pimc
resource: tests/multiplayer/test_ai_pimc.py#L1-L391
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/random
  - external/pytest
  - external/cards-refactored
  - external/ausbau-game-session
  - external/ausbau
  - external/ausbau-ai-strategies
---

# Contains

- [_hand](../../../functions/tests/multiplayer/test_ai_pimc/_hand.md)
- [test_engine_state_holds_fields](../../../functions/tests/multiplayer/test_ai_pimc/test_engine_state_holds_fields.md)
- [_basic_state](../../../functions/tests/multiplayer/test_ai_pimc/_basic_state.md)
- [test_sampler_respects_capacities_and_partitions_unseen](../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_capacities_and_partitions_unseen.md)
- [test_sampler_respects_voids](../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_voids.md)
- [test_sampler_under_holdback_only_under_to_voided_player](../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_under_holdback_only_under_to_voided_player.md)
- [test_sampler_is_deterministic_under_seed](../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_is_deterministic_under_seed.md)
- [test_rollout_is_deterministic](../../../functions/tests/multiplayer/test_ai_pimc/test_rollout_is_deterministic.md)
- [test_rollout_points_are_bounded_and_nonnegative](../../../functions/tests/multiplayer/test_ai_pimc/test_rollout_points_are_bounded_and_nonnegative.md)
- [_endgame_state](../../../functions/tests/multiplayer/test_ai_pimc/_endgame_state.md)
- [test_pimc_prefers_boss_trump_over_ruffable_side_lead](../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_prefers_boss_trump_over_ruffable_side_lead.md)
- [test_pimc_returns_none_when_below_min_samples](../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_returns_none_when_below_min_samples.md)
- [test_pimc_is_deterministic_under_seed](../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_is_deterministic_under_seed.md)
- [_make_strat](../../../functions/tests/multiplayer/test_ai_pimc/_make_strat.md)
- [test_tracking_initializes_sizes_and_voids](../../../functions/tests/multiplayer/test_ai_pimc/test_tracking_initializes_sizes_and_voids.md)
- [test_tracking_decrements_sizes_for_all_others](../../../functions/tests/multiplayer/test_ai_pimc/test_tracking_decrements_sizes_for_all_others.md)
- [test_tracking_marks_hard_void_on_nontrump_lead_discard](../../../functions/tests/multiplayer/test_ai_pimc/test_tracking_marks_hard_void_on_nontrump_lead_discard.md)
- [test_tracking_marks_under_holdback_on_trump_lead_discard](../../../functions/tests/multiplayer/test_ai_pimc/test_tracking_marks_under_holdback_on_trump_lead_discard.md)
- [_remove_from_live_hand](../../../functions/tests/multiplayer/test_ai_pimc/_remove_from_live_hand.md)
- [test_build_engine_state_is_consistent](../../../functions/tests/multiplayer/test_ai_pimc/test_build_engine_state_is_consistent.md)
- [test_rollout_raises_descriptive_error_on_empty_hand](../../../functions/tests/multiplayer/test_ai_pimc/test_rollout_raises_descriptive_error_on_empty_hand.md)
- [test_lead_uses_pimc_when_enabled](../../../functions/tests/multiplayer/test_ai_pimc/test_lead_uses_pimc_when_enabled.md)
- [fake_choose](../../../functions/tests/multiplayer/test_ai_pimc/fake_choose.md)
- [test_lead_falls_back_to_heuristic_when_pimc_disabled](../../../functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_to_heuristic_when_pimc_disabled.md)
- [test_lead_falls_back_when_pimc_returns_none](../../../functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_when_pimc_returns_none.md)
- [test_pick_card_leading_with_pimc_returns_legal_card](../../../functions/tests/multiplayer/test_ai_pimc/test_pick_card_leading_with_pimc_returns_legal_card.md)

# Imports

- `random`
- `pytest`
- `Cards_refactored`
- `ausbau.game_session`
- `ausbau`
- `ausbau.ai_strategies`