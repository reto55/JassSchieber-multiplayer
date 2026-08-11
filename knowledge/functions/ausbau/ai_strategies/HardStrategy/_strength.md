---
type: Python Method
title: _strength
resource: ausbau/ai_strategies.py#L264-L275
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/_is_guaranteed_winner
  - functions/ausbau/ai_strategies/HardStrategy/pick_card
  - functions/ausbau/ai_strategies/HardStrategy/_winner_so_far
---

# Signature

`def _strength(self, card_obj, operator: str, lead_suit: Optional[str]):`

# Called by

- [_is_guaranteed_winner](../../../../functions/ausbau/ai_strategies/HardStrategy/_is_guaranteed_winner.md)
- [pick_card](../../../../functions/ausbau/ai_strategies/HardStrategy/pick_card.md)
- [_winner_so_far](../../../../functions/ausbau/ai_strategies/HardStrategy/_winner_so_far.md)