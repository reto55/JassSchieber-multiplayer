---
type: Python Method
title: _winner_so_far
resource: ausbau/ai_strategies.py#L555-L571
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/code_to_card
  - functions/ausbau/ai_strategies/HardStrategy/_strength
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/pick_card
---

# Signature

`def _winner_so_far(self, played: list, operator: str) -> Optional[str]:`

# Calls

- [code_to_card](../../../../functions/ausbau/game_session/code_to_card.md)
- [_strength](../../../../functions/ausbau/ai_strategies/HardStrategy/_strength.md)

# Called by

- [pick_card](../../../../functions/ausbau/ai_strategies/HardStrategy/pick_card.md)