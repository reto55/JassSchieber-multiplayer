---
type: Python Function
title: test_both_void_all_trump_hand_leads_trump
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L204-L212
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_drive_both_opponents_void
---

# Signature

`def test_both_void_all_trump_hand_leads_trump(): # Edge: both opponents void AND our whole hand is trump — no non-trump card # to lead, so leading trump is the only legal option.`

# Calls

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)
- [_drive_both_opponents_void](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_drive_both_opponents_void.md)