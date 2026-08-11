---
type: Python Function
title: card_to_code
resource: ausbau/game_session.py#L29-L31
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/ai_pimc/_remove_card
  - functions/ausbau/ai_pimc/rollout
  - functions/ausbau/ai_pimc/pimc_choose_lead
  - functions/ausbau/ai_strategies/MediumStrategy/pick_card
  - functions/ausbau/ai_strategies/HardStrategy/_lead
  - functions/ausbau/ai_strategies/HardStrategy/_lead_heuristic
  - functions/ausbau/ai_strategies/HardStrategy/_lead_legacy
  - functions/ausbau/ai_strategies/HardStrategy/pick_card
  - functions/ausbau/game_session/hand_to_codes
  - functions/ausbau/game_session/find_card_in_hand
  - functions/ausbau/game_session/get_valid_cards
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_capacities_and_partitions_unseen
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_under_holdback_only_under_to_voided_player
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_is_deterministic_under_seed
  - functions/tests/multiplayer/test_ai_pimc/test_pimc_prefers_boss_trump_over_ruffable_side_lead
  - functions/tests/multiplayer/test_ai_pimc/test_pimc_is_deterministic_under_seed
  - functions/tests/multiplayer/test_ai_pimc/_remove_from_live_hand
  - functions/tests/multiplayer/test_ai_pimc/test_pick_card_leading_with_pimc_returns_legal_card
  - functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_lead_picks_highest_point
  - functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_follow_picks_lowest_point
  - functions/tests/multiplayer/test_await_seat_action/test_compute_ai_play_uses_ai_select_card
  - functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid
  - functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick
  - functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners
  - functions/tests/test_game_session/test_card_to_code_eicheln_ass
  - functions/tests/test_game_session/test_card_to_code_schellen_koenig
  - functions/tests/test_game_session/test_card_to_code_schilten_under
  - functions/tests/test_game_session/test_card_to_code_rosen_sechs
  - functions/tests/test_game_session/test_ai_leads_plays_highest_value
  - functions/tests/test_game_session/test_ai_follows_plays_lowest_value
---

# Signature

`def card_to_code(card: Card) -> str:`

# Called by

- [_remove_card](../../../functions/ausbau/ai_pimc/_remove_card.md)
- [rollout](../../../functions/ausbau/ai_pimc/rollout.md)
- [pimc_choose_lead](../../../functions/ausbau/ai_pimc/pimc_choose_lead.md)
- [pick_card](../../../functions/ausbau/ai_strategies/MediumStrategy/pick_card.md)
- [_lead](../../../functions/ausbau/ai_strategies/HardStrategy/_lead.md)
- [_lead_heuristic](../../../functions/ausbau/ai_strategies/HardStrategy/_lead_heuristic.md)
- [_lead_legacy](../../../functions/ausbau/ai_strategies/HardStrategy/_lead_legacy.md)
- [pick_card](../../../functions/ausbau/ai_strategies/HardStrategy/pick_card.md)
- [hand_to_codes](../../../functions/ausbau/game_session/hand_to_codes.md)
- [find_card_in_hand](../../../functions/ausbau/game_session/find_card_in_hand.md)
- [get_valid_cards](../../../functions/ausbau/game_session/get_valid_cards.md)
- [_play_trick](../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [test_sampler_respects_capacities_and_partitions_unseen](../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_capacities_and_partitions_unseen.md)
- [test_sampler_under_holdback_only_under_to_voided_player](../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_under_holdback_only_under_to_voided_player.md)
- [test_sampler_is_deterministic_under_seed](../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_is_deterministic_under_seed.md)
- [test_pimc_prefers_boss_trump_over_ruffable_side_lead](../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_prefers_boss_trump_over_ruffable_side_lead.md)
- [test_pimc_is_deterministic_under_seed](../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_is_deterministic_under_seed.md)
- [_remove_from_live_hand](../../../functions/tests/multiplayer/test_ai_pimc/_remove_from_live_hand.md)
- [test_pick_card_leading_with_pimc_returns_legal_card](../../../functions/tests/multiplayer/test_ai_pimc/test_pick_card_leading_with_pimc_returns_legal_card.md)
- [test_medium_pick_card_lead_picks_highest_point](../../../functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_lead_picks_highest_point.md)
- [test_medium_pick_card_follow_picks_lowest_point](../../../functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_follow_picks_lowest_point.md)
- [test_compute_ai_play_uses_ai_select_card](../../../functions/tests/multiplayer/test_await_seat_action/test_compute_ai_play_uses_ai_select_card.md)
- [_queue_seat_plays_first_valid](../../../functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid.md)
- [_queue_first_valid_for_trick](../../../functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick.md)
- [test_play_trick_appends_to_spiel_winners](../../../functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners.md)
- [test_card_to_code_eicheln_ass](../../../functions/tests/test_game_session/test_card_to_code_eicheln_ass.md)
- [test_card_to_code_schellen_koenig](../../../functions/tests/test_game_session/test_card_to_code_schellen_koenig.md)
- [test_card_to_code_schilten_under](../../../functions/tests/test_game_session/test_card_to_code_schilten_under.md)
- [test_card_to_code_rosen_sechs](../../../functions/tests/test_game_session/test_card_to_code_rosen_sechs.md)
- [test_ai_leads_plays_highest_value](../../../functions/tests/test_game_session/test_ai_leads_plays_highest_value.md)
- [test_ai_follows_plays_lowest_value](../../../functions/tests/test_game_session/test_ai_follows_plays_lowest_value.md)