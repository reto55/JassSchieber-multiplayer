---
type: Python Method
title: _lead_legacy
resource: ausbau/ai_strategies.py#L457-L465
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/ai_strategies/HardStrategy/_is_guaranteed_winner
  - functions/ausbau/ai_strategies/HardStrategy/_card_value
  - functions/ausbau/game_session/card_to_code
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/_lead
---

# Signature

`def _lead_legacy(self, play, valid_cards) -> dict:`

# Calls

- [_is_guaranteed_winner](../../../../functions/ausbau/ai_strategies/HardStrategy/_is_guaranteed_winner.md)
- [_card_value](../../../../functions/ausbau/ai_strategies/HardStrategy/_card_value.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)

# Called by

- [_lead](../../../../functions/ausbau/ai_strategies/HardStrategy/_lead.md)