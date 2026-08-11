---
type: Python Function
title: _endgame_state
resource: tests/multiplayer/test_ai_pimc.py#L175-L196
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_pimc/_hand
  - functions/tests/multiplayer/test_ai_pimc/_basic_state
  - functions/Cards_refactored/create_card
  called_by:
  - functions/tests/multiplayer/test_ai_pimc/test_pimc_prefers_boss_trump_over_ruffable_side_lead
  - functions/tests/multiplayer/test_ai_pimc/test_pimc_returns_none_when_below_min_samples
  - functions/tests/multiplayer/test_ai_pimc/test_pimc_is_deterministic_under_seed
---

# Signature

`def _endgame_state():`

# Calls

- [_hand](../../../../functions/tests/multiplayer/test_ai_pimc/_hand.md)
- [_basic_state](../../../../functions/tests/multiplayer/test_ai_pimc/_basic_state.md)
- [create_card](../../../../functions/Cards_refactored/create_card.md)

# Called by

- [test_pimc_prefers_boss_trump_over_ruffable_side_lead](../../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_prefers_boss_trump_over_ruffable_side_lead.md)
- [test_pimc_returns_none_when_below_min_samples](../../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_returns_none_when_below_min_samples.md)
- [test_pimc_is_deterministic_under_seed](../../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_is_deterministic_under_seed.md)