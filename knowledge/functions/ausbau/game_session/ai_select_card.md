---
type: Python Function
title: ai_select_card
resource: ausbau/game_session.py#L238-L261
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/get_valid_cards
  - functions/ausbau/game_session/find_card_in_hand
  called_by:
  - functions/ausbau/ai_pimc/rollout
  - functions/ausbau/ai_strategies/MediumStrategy/pick_card
  - functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_lead_picks_highest_point
  - functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_follow_picks_lowest_point
  - functions/tests/test_game_session/test_ai_leads_plays_highest_value
  - functions/tests/test_game_session/test_ai_follows_plays_lowest_value
---

# Signature

`def ai_select_card( hand: dict, lead_suit: Optional[str], operator: str, trick_so_far: Optional[list] = None, ) -> Card:`

# Calls

- [get_valid_cards](../../../functions/ausbau/game_session/get_valid_cards.md)
- [find_card_in_hand](../../../functions/ausbau/game_session/find_card_in_hand.md)

# Called by

- [rollout](../../../functions/ausbau/ai_pimc/rollout.md)
- [pick_card](../../../functions/ausbau/ai_strategies/MediumStrategy/pick_card.md)
- [test_medium_pick_card_lead_picks_highest_point](../../../functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_lead_picks_highest_point.md)
- [test_medium_pick_card_follow_picks_lowest_point](../../../functions/tests/multiplayer/test_ai_strategies/test_medium_pick_card_follow_picks_lowest_point.md)
- [test_ai_leads_plays_highest_value](../../../functions/tests/test_game_session/test_ai_leads_plays_highest_value.md)
- [test_ai_follows_plays_lowest_value](../../../functions/tests/test_game_session/test_ai_follows_plays_lowest_value.md)