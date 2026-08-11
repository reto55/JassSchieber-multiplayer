---
type: Python Function
title: _make_strat
resource: tests/multiplayer/test_ai_pimc.py#L233-L243
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/Cards_refactored/create_card
  called_by:
  - functions/tests/multiplayer/test_ai_pimc/test_tracking_initializes_sizes_and_voids
  - functions/tests/multiplayer/test_ai_pimc/test_tracking_decrements_sizes_for_all_others
  - functions/tests/multiplayer/test_ai_pimc/test_tracking_marks_hard_void_on_nontrump_lead_discard
  - functions/tests/multiplayer/test_ai_pimc/test_tracking_marks_under_holdback_on_trump_lead_discard
  - functions/tests/multiplayer/test_ai_pimc/test_build_engine_state_is_consistent
  - functions/tests/multiplayer/test_ai_pimc/test_lead_uses_pimc_when_enabled
  - functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_to_heuristic_when_pimc_disabled
  - functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_when_pimc_returns_none
  - functions/tests/multiplayer/test_ai_pimc/test_pick_card_leading_with_pimc_returns_legal_card
---

# Signature

`def _make_strat(position, operator, my_suit_to_suffixes):`

# Calls

- [create_card](../../../../functions/Cards_refactored/create_card.md)

# Called by

- [test_tracking_initializes_sizes_and_voids](../../../../functions/tests/multiplayer/test_ai_pimc/test_tracking_initializes_sizes_and_voids.md)
- [test_tracking_decrements_sizes_for_all_others](../../../../functions/tests/multiplayer/test_ai_pimc/test_tracking_decrements_sizes_for_all_others.md)
- [test_tracking_marks_hard_void_on_nontrump_lead_discard](../../../../functions/tests/multiplayer/test_ai_pimc/test_tracking_marks_hard_void_on_nontrump_lead_discard.md)
- [test_tracking_marks_under_holdback_on_trump_lead_discard](../../../../functions/tests/multiplayer/test_ai_pimc/test_tracking_marks_under_holdback_on_trump_lead_discard.md)
- [test_build_engine_state_is_consistent](../../../../functions/tests/multiplayer/test_ai_pimc/test_build_engine_state_is_consistent.md)
- [test_lead_uses_pimc_when_enabled](../../../../functions/tests/multiplayer/test_ai_pimc/test_lead_uses_pimc_when_enabled.md)
- [test_lead_falls_back_to_heuristic_when_pimc_disabled](../../../../functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_to_heuristic_when_pimc_disabled.md)
- [test_lead_falls_back_when_pimc_returns_none](../../../../functions/tests/multiplayer/test_ai_pimc/test_lead_falls_back_when_pimc_returns_none.md)
- [test_pick_card_leading_with_pimc_returns_legal_card](../../../../functions/tests/multiplayer/test_ai_pimc/test_pick_card_leading_with_pimc_returns_legal_card.md)