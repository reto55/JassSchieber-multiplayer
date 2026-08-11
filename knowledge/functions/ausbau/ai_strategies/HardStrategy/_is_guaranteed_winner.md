---
type: Python Method
title: _is_guaranteed_winner
resource: ausbau/ai_strategies.py#L277-L291
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/ai_strategies/HardStrategy/_strength
  - functions/ausbau/game_session/code_to_card
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/_lead_heuristic
  - functions/ausbau/ai_strategies/HardStrategy/_lead_legacy
---

# Signature

`def _is_guaranteed_winner(self, card_obj, play) -> bool:`

# Calls

- [_strength](../../../../functions/ausbau/ai_strategies/HardStrategy/_strength.md)
- [code_to_card](../../../../functions/ausbau/game_session/code_to_card.md)

# Called by

- [_lead_heuristic](../../../../functions/ausbau/ai_strategies/HardStrategy/_lead_heuristic.md)
- [_lead_legacy](../../../../functions/ausbau/ai_strategies/HardStrategy/_lead_legacy.md)