---
type: Python Function
title: test_rollout_raises_descriptive_error_on_empty_hand
resource: tests/multiplayer/test_ai_pimc.py#L319-L337
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

`def test_rollout_raises_descriptive_error_on_empty_hand(): # Unbalanced: a non-self seat has an empty hand while cards remain # elsewhere, so a seat is eventually asked to play from nothing.`

# Calls

- [_hand](../../../../functions/tests/multiplayer/test_ai_pimc/_hand.md)
- [_basic_state](../../../../functions/tests/multiplayer/test_ai_pimc/_basic_state.md)
- [create_card](../../../../functions/Cards_refactored/create_card.md)
- [rollout](../../../../functions/ausbau/ai_pimc/rollout.md)