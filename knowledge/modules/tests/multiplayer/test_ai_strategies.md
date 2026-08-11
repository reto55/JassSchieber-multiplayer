---
type: Python Module
title: test_ai_strategies
resource: tests/multiplayer/test_ai_strategies.py#L1-L361
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/pytest
  - external/random
  - external/cards-refactored
  - external/ausbau-ai-strategies
  - external/ausbau-game-session
  - external/utils-card-utils
---

# Contains

- [test_make_strategy_easy](../../../functions/tests/multiplayer/test_ai_strategies/test_make_strategy_easy.md)
- [test_make_strategy_medium](../../../functions/tests/multiplayer/test_ai_strategies/test_make_strategy_medium.md)
- [test_make_strategy_hard](../../../functions/tests/multiplayer/test_ai_strategies/test_make_strategy_hard.md)
- [test_make_strategy_unknown](../../../functions/tests/multiplayer/test_ai_strategies/test_make_strategy_unknown.md)
- [test_easy_pick_trump_returns_one_of_six_modes](../../../functions/tests/multiplayer/test_ai_strategies/test_easy_pick_trump_returns_one_of_six_modes.md)
- [test_easy_pick_trump_never_schiebens](../../../functions/tests/multiplayer/test_ai_strategies/test_easy_pick_trump_never_schiebens.md)
- [test_easy_pick_card_returns_valid_card](../../../functions/tests/multiplayer/test_ai_strategies/test_easy_pick_card_returns_valid_card.md)
- [test_medium_pick_trump_uses_farbe_lang](../../../functions/tests/multiplayer/test_ai_strategies/test_medium_pick_trump_uses_farbe_lang.md)
- [test_medium_pick_trump_never_schiebens](../../../functions/tests/multiplayer/test_ai_strategies/test_medium_pick_trump_never_schiebens.md)
- [test_medium_pick_card_lead_picks_highest_point](../../../functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_lead_picks_highest_point.md)
- [test_medium_pick_card_follow_picks_lowest_point](../../../functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_follow_picks_lowest_point.md)
- [test_hard_on_spiel_start_populates_remaining](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_on_spiel_start_populates_remaining.md)
- [test_hard_on_spiel_start_excludes_own_hand](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_on_spiel_start_excludes_own_hand.md)
- [test_hard_on_card_played_removes_known_card](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_on_card_played_removes_known_card.md)
- [test_hard_on_card_played_skips_own_position](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_on_card_played_skips_own_position.md)
- [test_hard_on_card_played_unknown_card_is_noop](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_on_card_played_unknown_card_is_noop.md)
- [_hand_with_suits](../../../functions/tests/multiplayer/test_ai_strategies/_hand_with_suits.md)
- [test_hard_pick_trump_commits_when_long_with_under](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_commits_when_long_with_under.md)
- [test_hard_pick_trump_schiebens_when_weak_and_allowed](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_schiebens_when_weak_and_allowed.md)
- [test_hard_pick_trump_falls_back_to_max_score_post_schieben](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_falls_back_to_max_score_post_schieben.md)
- [test_hard_pick_trump_long_no_under_no_neun_schiebens](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_long_no_under_no_neun_schiebens.md)
- [test_hard_pick_card_lead_plays_guaranteed_winner_ass](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_card_lead_plays_guaranteed_winner_ass.md)
- [test_hard_pick_card_lead_no_winner_plays_lowest](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_card_lead_no_winner_plays_lowest.md)
- [test_hard_follow_partner_winning_dumps_low](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_follow_partner_winning_dumps_low.md)
- [test_hard_follow_opponent_winning_beats_cheaply](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_follow_opponent_winning_beats_cheaply.md)
- [test_hard_follow_no_lead_suit_dumps_low_when_cant_beat](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_follow_no_lead_suit_dumps_low_when_cant_beat.md)
- [test_hard_trump_steal_when_trick_high_value](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_trump_steal_when_trick_high_value.md)

# Imports

- `pytest`
- `random`
- `Cards_refactored`
- `ausbau.ai_strategies`
- `ausbau.game_session`
- `utils.card_utils`