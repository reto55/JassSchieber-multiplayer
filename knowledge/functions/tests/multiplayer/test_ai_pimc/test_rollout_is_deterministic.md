---
type: Python Function
title: test_rollout_is_deterministic
resource: tests/multiplayer/test_ai_pimc.py#L134-L153
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_pimc/_hand
  - functions/tests/multiplayer/test_ai_pimc/_basic_state
  - functions/Cards_refactored/create_card
  - functions/ausbau/ai_pimc/rollout
---

# Signature

`def test_rollout_is_deterministic(): # 2-card endgame: I lead, everyone has 2 cards. Schellen trump.`

# Calls

- [_hand](../../../../functions/tests/multiplayer/test_ai_pimc/_hand.md)
- [_basic_state](../../../../functions/tests/multiplayer/test_ai_pimc/_basic_state.md)
- [create_card](../../../../functions/Cards_refactored/create_card.md)
- [rollout](../../../../functions/ausbau/ai_pimc/rollout.md)