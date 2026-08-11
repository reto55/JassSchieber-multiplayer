---
type: Python Function
title: _hand_with_suits
resource: tests/multiplayer/test_ai_strategies.py#L166-L176
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/Cards_refactored/create_card
  called_by:
  - functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_commits_when_long_with_under
  - functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_schiebens_when_weak_and_allowed
  - functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_falls_back_to_max_score_post_schieben
  - functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_long_no_under_no_neun_schiebens
  - functions/tests/multiplayer/test_ai_strategies/test_hard_pick_card_lead_plays_guaranteed_winner_ass
  - functions/tests/multiplayer/test_ai_strategies/test_hard_pick_card_lead_no_winner_plays_lowest
  - functions/tests/multiplayer/test_ai_strategies/test_hard_follow_partner_winning_dumps_low
  - functions/tests/multiplayer/test_ai_strategies/test_hard_follow_opponent_winning_beats_cheaply
  - functions/tests/multiplayer/test_ai_strategies/test_hard_follow_no_lead_suit_dumps_low_when_cant_beat
  - functions/tests/multiplayer/test_ai_strategies/test_hard_trump_steal_when_trick_high_value
---

# Signature

`def _hand_with_suits(play, position, suit_to_codes):`

# Calls

- [create_card](../../../../functions/Cards_refactored/create_card.md)

# Called by

- [test_hard_pick_trump_commits_when_long_with_under](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_commits_when_long_with_under.md)
- [test_hard_pick_trump_schiebens_when_weak_and_allowed](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_schiebens_when_weak_and_allowed.md)
- [test_hard_pick_trump_falls_back_to_max_score_post_schieben](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_falls_back_to_max_score_post_schieben.md)
- [test_hard_pick_trump_long_no_under_no_neun_schiebens](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_trump_long_no_under_no_neun_schiebens.md)
- [test_hard_pick_card_lead_plays_guaranteed_winner_ass](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_card_lead_plays_guaranteed_winner_ass.md)
- [test_hard_pick_card_lead_no_winner_plays_lowest](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_pick_card_lead_no_winner_plays_lowest.md)
- [test_hard_follow_partner_winning_dumps_low](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_follow_partner_winning_dumps_low.md)
- [test_hard_follow_opponent_winning_beats_cheaply](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_follow_opponent_winning_beats_cheaply.md)
- [test_hard_follow_no_lead_suit_dumps_low_when_cant_beat](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_follow_no_lead_suit_dumps_low_when_cant_beat.md)
- [test_hard_trump_steal_when_trick_high_value](../../../../functions/tests/multiplayer/test_ai_strategies/test_hard_trump_steal_when_trick_high_value.md)