---
type: Python Function
title: _remove_card
resource: ausbau/ai_pimc.py#L113-L121
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/card_to_code
  called_by:
  - functions/ausbau/ai_pimc/rollout
---

# Signature

`def _remove_card(hand: dict, card) -> None:`

# Calls

- [card_to_code](../../../functions/ausbau/game_session/card_to_code.md)

# Called by

- [rollout](../../../functions/ausbau/ai_pimc/rollout.md)