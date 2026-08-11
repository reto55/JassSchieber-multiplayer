---
type: Python Method
title: _build_engine_state
resource: ausbau/ai_strategies.py#L300-L322
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/code_to_card
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/_lead
  - functions/tests/multiplayer/test_ai_pimc/test_build_engine_state_is_consistent
---

# Signature

`def _build_engine_state(self, play):`

# Calls

- [code_to_card](../../../../functions/ausbau/game_session/code_to_card.md)

# Called by

- [_lead](../../../../functions/ausbau/ai_strategies/HardStrategy/_lead.md)
- [test_build_engine_state_is_consistent](../../../../functions/tests/multiplayer/test_ai_pimc/test_build_engine_state_is_consistent.md)