---
type: Python Function
title: test_both_void_never_cashes_guaranteed_trump_winner
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L226-L238
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_drive_both_opponents_void
---

# Signature

`def test_both_void_never_cashes_guaranteed_trump_winner(): # Regression: both opponents void but trumps are still OUTSTANDING — they # can only sit in partner's hand. The trump Under (SEU, top trump, 20 pts) # is a guaranteed winner and outscores the Rosen Ass (11 pts) in the # winners-cash, but leading it would pull partner's trumps. The AI must # cash the non-trump winner instead.`

# Calls

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)
- [_drive_both_opponents_void](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_drive_both_opponents_void.md)