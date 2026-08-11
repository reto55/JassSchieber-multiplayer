---
type: Python Function
title: _set_hand
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L36-L42
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/Cards_refactored/create_card
  called_by:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
---

# Signature

`def _set_hand(play, position, suit_to_suffixes):`

# Calls

- [create_card](../../../../functions/Cards_refactored/create_card.md)

# Called by

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)