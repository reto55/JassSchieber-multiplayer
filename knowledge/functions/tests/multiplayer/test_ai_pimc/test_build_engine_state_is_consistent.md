---
type: Python Function
title: test_build_engine_state_is_consistent
resource: tests/multiplayer/test_ai_pimc.py#L293-L315
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_pimc/_make_strat
  - functions/tests/multiplayer/test_ai_pimc/_remove_from_live_hand
  - functions/ausbau/ai_strategies/HardStrategy/_build_engine_state
---

# Signature

`def test_build_engine_state_is_consistent(): # A balanced, real 9-card hand (the invariant only holds for consistent # deals, exactly as in live play). One full trump-led trick is simulated # in lockstep with our own hand shrinking, so the unseen set tracks the # three hidden hands exactly.`

# Calls

- [_make_strat](../../../../functions/tests/multiplayer/test_ai_pimc/_make_strat.md)
- [_remove_from_live_hand](../../../../functions/tests/multiplayer/test_ai_pimc/_remove_from_live_hand.md)
- [_build_engine_state](../../../../functions/ausbau/ai_strategies/HardStrategy/_build_engine_state.md)