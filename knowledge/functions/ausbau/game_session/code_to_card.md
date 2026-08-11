---
type: Python Function
title: code_to_card
resource: ausbau/game_session.py#L53-L71
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/Cards_refactored/create_card
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/on_card_played
  - functions/ausbau/ai_strategies/HardStrategy/_is_guaranteed_winner
  - functions/ausbau/ai_strategies/HardStrategy/_build_engine_state
  - functions/ausbau/ai_strategies/HardStrategy/_lead_heuristic
  - functions/ausbau/ai_strategies/HardStrategy/pick_card
  - functions/ausbau/ai_strategies/HardStrategy/_winner_so_far
  - functions/ausbau/game_session/get_valid_cards
  - functions/tests/multiplayer/test_ai_pimc/_remove_from_live_hand
---

# Signature

`def code_to_card(code: str) -> Card:`

# Calls

- [create_card](../../../functions/Cards_refactored/create_card.md)

# Called by

- [on_card_played](../../../functions/ausbau/ai_strategies/HardStrategy/on_card_played.md)
- [_is_guaranteed_winner](../../../functions/ausbau/ai_strategies/HardStrategy/_is_guaranteed_winner.md)
- [_build_engine_state](../../../functions/ausbau/ai_strategies/HardStrategy/_build_engine_state.md)
- [_lead_heuristic](../../../functions/ausbau/ai_strategies/HardStrategy/_lead_heuristic.md)
- [pick_card](../../../functions/ausbau/ai_strategies/HardStrategy/pick_card.md)
- [_winner_so_far](../../../functions/ausbau/ai_strategies/HardStrategy/_winner_so_far.md)
- [get_valid_cards](../../../functions/ausbau/game_session/get_valid_cards.md)
- [_remove_from_live_hand](../../../functions/tests/multiplayer/test_ai_pimc/_remove_from_live_hand.md)