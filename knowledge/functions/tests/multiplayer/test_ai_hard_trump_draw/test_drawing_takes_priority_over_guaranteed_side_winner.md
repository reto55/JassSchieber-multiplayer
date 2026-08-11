---
type: Python Function
title: test_drawing_takes_priority_over_guaranteed_side_winner
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L85-L91
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
---

# Signature

`def test_drawing_takes_priority_over_guaranteed_side_winner(): # Holds the trump Under (top trump, SEU) AND an off-suit Ass (RA) that # would also win. While drawing, the trump lead wins out.`

# Calls

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)