---
type: Python Function
title: test_both_void_unshown_suit_never_leads_trump
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L190-L201
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_drive_both_opponents_void
---

# Signature

`def test_both_void_unshown_suit_never_leads_trump(): # Regression: both opponents void, no guaranteed winner, and our only # non-trump card is in a suit NO opponent has shown (so the shown-suit # dump filter finds nothing). The fallback must still pick the non-trump # card, never re-open with trump. compo shows Rosen, compe shows Eicheln # while driving voids; our side suit is Schilten (unshown).`

# Calls

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)
- [_drive_both_opponents_void](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_drive_both_opponents_void.md)