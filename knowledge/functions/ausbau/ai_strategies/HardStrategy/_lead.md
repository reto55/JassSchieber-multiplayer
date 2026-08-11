---
type: Python Method
title: _lead
resource: ausbau/ai_strategies.py#L324-L348
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/ai_strategies/HardStrategy/_lead_legacy
  - functions/ausbau/ai_strategies/HardStrategy/_build_engine_state
  - functions/ausbau/ai_pimc/pimc_choose_lead
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/ai_strategies/HardStrategy/_lead_heuristic
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/pick_card
  - functions/tests/multiplayer/test_ai_pimc/test_lead_uses_pimc_when_enabled
  - functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_to_heuristic_when_pimc_disabled
  - functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_when_pimc_returns_none
---

# Signature

`def _lead(self, play, valid_cards) -> dict:`

# Calls

- [_lead_legacy](../../../../functions/ausbau/ai_strategies/HardStrategy/_lead_legacy.md)
- [_build_engine_state](../../../../functions/ausbau/ai_strategies/HardStrategy/_build_engine_state.md)
- [pimc_choose_lead](../../../../functions/ausbau/ai_pimc/pimc_choose_lead.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)
- [_lead_heuristic](../../../../functions/ausbau/ai_strategies/HardStrategy/_lead_heuristic.md)

# Called by

- [pick_card](../../../../functions/ausbau/ai_strategies/HardStrategy/pick_card.md)
- [test_lead_uses_pimc_when_enabled](../../../../functions/tests/multiplayer/test_ai_pimc/test_lead_uses_pimc_when_enabled.md)
- [test_lead_falls_back_to_heuristic_when_pimc_disabled](../../../../functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_to_heuristic_when_pimc_disabled.md)
- [test_lead_falls_back_when_pimc_returns_none](../../../../functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_when_pimc_returns_none.md)