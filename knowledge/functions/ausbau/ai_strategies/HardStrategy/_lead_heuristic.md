---
type: Python Method
title: _lead_heuristic
resource: ausbau/ai_strategies.py#L350-L455
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/ai_strategies/HardStrategy/_both_opponents_void_trump
  - functions/ausbau/game_session/code_to_card
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/ai_strategies/HardStrategy/_is_guaranteed_winner
  - functions/ausbau/ai_strategies/HardStrategy/_card_value
  - functions/ausbau/ai_strategies/HardStrategy/_opponents
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/_lead
---

# Signature

`def _lead_heuristic(self, play, valid_cards) -> dict:`

# Calls

- [_both_opponents_void_trump](../../../../functions/ausbau/ai_strategies/HardStrategy/_both_opponents_void_trump.md)
- [code_to_card](../../../../functions/ausbau/game_session/code_to_card.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)
- [_is_guaranteed_winner](../../../../functions/ausbau/ai_strategies/HardStrategy/_is_guaranteed_winner.md)
- [_card_value](../../../../functions/ausbau/ai_strategies/HardStrategy/_card_value.md)
- [_opponents](../../../../functions/ausbau/ai_strategies/HardStrategy/_opponents.md)

# Called by

- [_lead](../../../../functions/ausbau/ai_strategies/HardStrategy/_lead.md)