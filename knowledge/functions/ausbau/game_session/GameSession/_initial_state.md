---
type: Python Method
title: _initial_state
resource: ausbau/game_session.py#L852-L868
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/hand_to_codes
  called_by:
  - functions/tests/test_game_session/test_initial_state_structure
  - functions/tests/test_game_session/test_initial_state_scores_accumulate
---

# Signature

`def _initial_state(self, play: Play) -> dict:`

# Calls

- [hand_to_codes](../../../../functions/ausbau/game_session/hand_to_codes.md)

# Called by

- [test_initial_state_structure](../../../../functions/tests/test_game_session/test_initial_state_structure.md)
- [test_initial_state_scores_accumulate](../../../../functions/tests/test_game_session/test_initial_state_scores_accumulate.md)