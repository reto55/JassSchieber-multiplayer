---
type: Python Function
title: _remove_from_live_hand
resource: tests/multiplayer/test_ai_pimc.py#L283-L290
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/code_to_card
  - functions/ausbau/game_session/card_to_code
  called_by:
  - functions/tests/multiplayer/test_ai_pimc/test_build_engine_state_is_consistent
---

# Signature

`def _remove_from_live_hand(play, position, code):`

# Calls

- [code_to_card](../../../../functions/ausbau/game_session/code_to_card.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)

# Called by

- [test_build_engine_state_is_consistent](../../../../functions/tests/multiplayer/test_ai_pimc/test_build_engine_state_is_consistent.md)