---
type: Python Method
title: pick_card
resource: ausbau/ai_strategies.py#L467-L553
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/get_valid_cards
  - functions/ausbau/game_session/find_card_in_hand
  - functions/ausbau/ai_strategies/HardStrategy/_lead
  - functions/ausbau/ai_strategies/HardStrategy/_winner_so_far
  - functions/ausbau/ai_strategies/HardStrategy/_card_value
  - functions/ausbau/game_session/code_to_card
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/ai_strategies/HardStrategy/_strength
---

# Signature

`def pick_card(self, play, lead_suit: Optional[str], trick_so_far: list) -> dict:`

# Calls

- [get_valid_cards](../../../../functions/ausbau/game_session/get_valid_cards.md)
- [find_card_in_hand](../../../../functions/ausbau/game_session/find_card_in_hand.md)
- [_lead](../../../../functions/ausbau/ai_strategies/HardStrategy/_lead.md)
- [_winner_so_far](../../../../functions/ausbau/ai_strategies/HardStrategy/_winner_so_far.md)
- [_card_value](../../../../functions/ausbau/ai_strategies/HardStrategy/_card_value.md)
- [code_to_card](../../../../functions/ausbau/game_session/code_to_card.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)
- [_strength](../../../../functions/ausbau/ai_strategies/HardStrategy/_strength.md)